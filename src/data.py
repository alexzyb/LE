# src/data.py
"""Data access layer — queries against live_data (BG Phase 8)."""

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

_TZ_LONDON = ZoneInfo("Europe/London")

from column_map import BY_DASHBOARD_COL, clean_value

DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_PATH = Path(__file__).resolve().parent / "land_energy.db"


def _open():
    if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(str(DB_PATH))


def _table_exists(conn, name):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    )
    return cur.fetchone() is not None


# ─── DB metadata ──────────────────────────────────────────────────────────────

def get_db_time_range():
    """Return (min_dt, max_dt) as datetime objects, or (None, None) if no data."""
    if not DB_PATH.exists():
        return None, None
    try:
        with _open() as conn:
            if not _table_exists(conn, "live_data"):
                return None, None
            row = conn.execute(
                'SELECT MIN("Date Time"), MAX("Date Time") FROM live_data'
            ).fetchone()
        if row and row[0] and row[1]:
            mn = datetime.fromisoformat(row[0][:19])
            mx = datetime.fromisoformat(row[1][:19])
            return mn, mx
    except Exception as e:
        print(f"[data.get_db_time_range] {e}")
    return None, None


# ─── Downsampling helper ──────────────────────────────────────────────────────

def _resample_freq(start_dt, end_dt):
    """Return pandas resample freq string, or None to keep raw 30s data."""
    delta = end_dt - start_dt
    if delta <= timedelta(hours=24):
        return None        # raw 30s, ≤2,880 rows
    if delta <= timedelta(days=14):
        return "5min"      # ~2,016 rows
    if delta <= timedelta(days=60):
        return "30min"     # ~1,440 rows
    if delta <= timedelta(days=365):
        return "2h"        # ~4,380 rows (1 year)
    return "6h"            # ≤~7,300 rows (multi-year)


# Cumulative columns — use .last() instead of .mean() when downsampling
_CUMULATIVE_COLS = {
    "Total Pellets passed belt weigher (cumlative)",
    "_pm1_energy_cumulative", "_pm2_energy_cumulative", "_pm3_energy_cumulative",
    "_silo1_infeed_totaliser", "_silo2_infeed_totaliser", "_silo3_infeed_totaliser",
    "_bagging_totaliser", "_truck_totaliser",
}


# ─── Cleaning ─────────────────────────────────────────────────────────────────

def _apply_cleaning(df):
    """Apply column_map cleaning rules to a wide DataFrame in-place."""
    for col, entry in BY_DASHBOARD_COL.items():
        if col not in df.columns:
            continue
        rule = entry.get("clean")
        if not rule:
            continue
        df[col] = df[col].apply(lambda v: clean_value(v, rule))
    return df


# ─── Main query ───────────────────────────────────────────────────────────────

def get_live_df(start_date, end_date) -> pd.DataFrame:
    """
    Query live_data for [start_date, end_date].
    - Applies column_map cleaning rules (display-time filtering)
    - Auto-downsamples large ranges so Plotly never gets > ~3 000 rows
    Returns wide DataFrame with 'Date Time' as datetime column, sorted ascending.
    """
    if not DB_PATH.exists():
        return pd.DataFrame()

    # Normalise to full ISO strings
    s = str(start_date)
    e = str(end_date)
    start_str = (s + "T00:00:00") if len(s) <= 10 else s[:19]
    end_str   = (e + "T23:59:59") if len(e) <= 10 else e[:19]

    try:
        with _open() as conn:
            if not _table_exists(conn, "live_data"):
                return pd.DataFrame()
            df = pd.read_sql_query(
                'SELECT * FROM live_data'
                ' WHERE "Date Time" >= ? AND "Date Time" <= ?'
                ' ORDER BY "Date Time"',
                conn,
                params=[start_str, end_str],
            )
    except Exception as e:
        print(f"[data.get_live_df] {e}")
        return pd.DataFrame()

    if df.empty:
        return df

    df["Date Time"] = pd.to_datetime(df["Date Time"], errors="coerce")
    df = df.dropna(subset=["Date Time"]).sort_values("Date Time").reset_index(drop=True)
    # Convert UTC → Europe/London (BST in summer, GMT in winter — auto DST)
    df["Date Time"] = (
        df["Date Time"].dt.tz_localize("UTC")
        .dt.tz_convert(_TZ_LONDON)
        .dt.tz_localize(None)
    )

    # Apply display-time cleaning
    _apply_cleaning(df)

    # Auto-downsample for large ranges
    start_dt = pd.to_datetime(start_str)
    end_dt   = pd.to_datetime(end_str)
    freq = _resample_freq(start_dt, end_dt)

    if freq and len(df) > 2000:
        df = df.set_index("Date Time")
        num_cols = df.select_dtypes(include="number").columns.tolist()
        instant = [c for c in num_cols if c not in _CUMULATIVE_COLS]
        cumul = [c for c in num_cols if c in _CUMULATIVE_COLS]
        parts = []
        if instant:
            parts.append(df[instant].resample(freq).mean())
        if cumul:
            parts.append(df[cumul].resample(freq).last())
        df = pd.concat(parts, axis=1).reset_index() if parts else df.reset_index()

    return df


# ─── Daily delta (no resampling) ──────────────────────────────────────────────

def get_daily_delta(col: str) -> float | None:
    """
    Return today's delta for a cumulative column: last_value - first_value
    for the most recent day that has data, using raw 30s data (no resampling).

    This avoids the coarse-bucket bias where wider resample windows inflate
    vals.iloc[0] and cause the delta to shrink (e.g. 77→67→44 across ranges).
    """
    if not DB_PATH.exists():
        return None
    try:
        with _open() as conn:
            if not _table_exists(conn, "live_data"):
                return None
            row = conn.execute(
                f'SELECT MAX(substr("Date Time", 1, 10)) FROM live_data'
                f' WHERE "{col}" IS NOT NULL'
            ).fetchone()
            if not row or not row[0]:
                return None
            last_date = row[0]

            df = pd.read_sql_query(
                f'SELECT "{col}" FROM live_data'
                f' WHERE "Date Time" >= ? AND "Date Time" <= ?'
                f' ORDER BY "Date Time"',
                conn,
                params=[f"{last_date}T00:00:00", f"{last_date}T23:59:59"],
            )
    except Exception as e:
        print(f"[data.get_daily_delta] {e}")
        return None

    vals = df[col].dropna()
    if len(vals) < 2:
        return None
    return round(float(vals.iloc[-1]) - float(vals.iloc[0]), 1)


# ─── Year-to-date / annual total (no resampling) ──────────────────────────────

def _clean_sql(col: str) -> str:
    """Build a SQL predicate from the column's column_map clean rule, so raw
    queries skip the same anomalies get_live_df filters at display time."""
    rule = (BY_DASHBOARD_COL.get(col, {}) or {}).get("clean") or {}
    t = rule.get("type")
    if t == "non_negative":
        return f' AND "{col}" >= 0'
    if t == "range":
        return f' AND "{col}" >= {rule["min"]} AND "{col}" <= {rule["max"]}'
    return ""


def get_year_total(col: str, year: int) -> float | None:
    """
    Production during one calendar year for a cumulative counter:
        value at end of year  −  value at end of previous year

    - Current year → latest reading − last reading of previous year (YTD)
    - Past year    → last reading of that year − last reading of previous year
    - Earliest year with data (no prior-year baseline) → last − first within year

    Cumulative counters are monotonic, so the year's production is the delta of
    the counter across the year boundary. Uses LIMIT-1 index seeks (no full
    load) and applies the column's clean rule to skip anomalous values.
    """
    if not DB_PATH.exists():
        return None

    year_start = f"{year}-01-01T00:00:00"
    if year >= datetime.now().year:
        end_bound = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    else:
        end_bound = f"{year}-12-31T23:59:59"

    cln = _clean_sql(col)

    def _one(conn, sql, params):
        r = conn.execute(sql, params).fetchone()
        return float(r[0]) if r and r[0] is not None else None

    try:
        with _open() as conn:
            if not _table_exists(conn, "live_data"):
                return None
            # Last reading within year N
            end_val = _one(conn,
                f'SELECT "{col}" FROM live_data'
                f' WHERE "Date Time" >= ? AND "Date Time" <= ?'
                f' AND "{col}" IS NOT NULL{cln}'
                f' ORDER BY "Date Time" DESC LIMIT 1',
                (year_start, end_bound))
            if end_val is None:
                return None  # no data in this year

            # First reading within year N (fallback baseline)
            first_val = _one(conn,
                f'SELECT "{col}" FROM live_data'
                f' WHERE "Date Time" >= ? AND "Date Time" <= ?'
                f' AND "{col}" IS NOT NULL{cln}'
                f' ORDER BY "Date Time" ASC LIMIT 1',
                (year_start, end_bound))

            # Baseline = last reading BEFORE year N (carry-in from prior years)
            base_val = _one(conn,
                f'SELECT "{col}" FROM live_data'
                f' WHERE "Date Time" < ? AND "{col}" IS NOT NULL{cln}'
                f' ORDER BY "Date Time" DESC LIMIT 1',
                (year_start,))
    except Exception as e:
        print(f"[data.get_year_total] {e}")
        return None

    # Standard cumulative delta: end of year N − end of year N-1.
    if base_val is not None:
        delta = end_val - base_val
        # Counter reset/rollover across the year boundary → cross-year delta is
        # negative and meaningless; fall back to the within-year delta.
        if delta < 0 and first_val is not None:
            delta = end_val - first_val
    elif first_val is not None:
        # Earliest year with data — no prior-year baseline.
        delta = end_val - first_val
    else:
        return None

    return round(delta, 1) if delta >= 0 else None


def get_available_years() -> list[int]:
    """Years covered by the data, ascending. Falls back to [current year]."""
    current = datetime.now().year
    mn, mx = get_db_time_range()
    if mn is None:
        return [current]
    last = max(mx.year if mx else current, current)
    return list(range(mn.year, last + 1))


# ─── Sparse multi-column query (for hourly Silo/Dispatch panels) ──────────────

def get_sparse_df(cols: list[str], start_date, end_date) -> pd.DataFrame:
    """
    Query only `cols` (+ Date Time) and only rows where at least one of them
    is non-null. Silo/Dispatch sources are hourly, so even a 1-year range
    returns a few thousand rows — far cheaper than get_live_df's SELECT * which
    drags in every 30s Mill row. No resampling needed (already sparse).

    Applies the same UTC→London conversion and column cleaning as get_live_df.
    """
    if not DB_PATH.exists():
        return pd.DataFrame()

    s = str(start_date)
    e = str(end_date)
    start_str = (s + "T00:00:00") if len(s) <= 10 else s[:19]
    end_str   = (e + "T23:59:59") if len(e) <= 10 else e[:19]

    quoted   = ", ".join(f'"{c}"' for c in cols)
    not_null = " OR ".join(f'"{c}" IS NOT NULL' for c in cols)

    try:
        with _open() as conn:
            if not _table_exists(conn, "live_data"):
                return pd.DataFrame()
            df = pd.read_sql_query(
                f'SELECT "Date Time", {quoted} FROM live_data'
                f' WHERE "Date Time" >= ? AND "Date Time" <= ?'
                f' AND ({not_null})'
                f' ORDER BY "Date Time"',
                conn,
                params=[start_str, end_str],
            )
    except Exception as ex:
        print(f"[data.get_sparse_df] {ex}")
        return pd.DataFrame()

    if df.empty:
        return df

    df["Date Time"] = pd.to_datetime(df["Date Time"], errors="coerce")
    df = df.dropna(subset=["Date Time"]).sort_values("Date Time").reset_index(drop=True)
    df["Date Time"] = (
        df["Date Time"].dt.tz_localize("UTC")
        .dt.tz_convert(_TZ_LONDON)
        .dt.tz_localize(None)
    )
    _apply_cleaning(df)
    return df
