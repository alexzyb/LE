# src/data.py
"""Data access layer — all SQL queries against land_energy.db."""

import sqlite3
from typing import Optional
from pathlib import Path

import pandas as pd

from column_map import BY_DASHBOARD_COL, clean_value
from config import DATABASE_URL

DB_PATH = Path(__file__).resolve().parent / "land_energy.db"


def _open():
    if DATABASE_URL:
        # Keep sqlite path fallback in this phase; PostgreSQL driver wiring can be
        # introduced later without changing call sites.
        if DATABASE_URL.startswith("sqlite:///"):
            return sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
    return sqlite3.connect(DB_PATH)


def _table_exists(conn, table_name: str) -> bool:
    try:
        df = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            conn,
            params=[table_name],
        )
        return not df.empty
    except Exception:
        return False


def _active_shift_table(conn) -> Optional[str]:
    """Prefer live_data, fallback to shift_protocol."""
    if _table_exists(conn, "live_data"):
        return "live_data"
    if _table_exists(conn, "shift_protocol"):
        return "shift_protocol"
    return None


def _apply_display_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    cleaned = df.copy()
    for col in cleaned.columns:
        meta = BY_DASHBOARD_COL.get(col)
        if not meta:
            continue
        rule = meta.get("clean")
        if not rule:
            continue
        cleaned[col] = cleaned[col].apply(lambda v: clean_value(v, rule))
    return cleaned


def get_shift_df(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Query shift_protocol for rows in [start_date, end_date].
    Accepts YYYY-MM-DD (expanded to full day) or YYYY-MM-DDTHH:MM:SS (precise).
    Returns a DataFrame with 'Date Time' parsed as datetime, sorted ascending.
    """
    if not DB_PATH.exists():
        return pd.DataFrame()
    start = f"{start_date}T00:00:00" if len(start_date) <= 10 else start_date
    end   = f"{end_date}T23:59:59"   if len(end_date)   <= 10 else end_date
    try:
        with _open() as conn:
            table = _active_shift_table(conn)
            if not table:
                return pd.DataFrame()
            df = pd.read_sql_query(
                f"""SELECT * FROM {table}
                   WHERE "Date Time" >= ? AND "Date Time" <= ?
                   ORDER BY "Date Time" """,
                conn,
                params=[start, end],
            )
        df["Date Time"] = pd.to_datetime(df["Date Time"], errors="coerce")
        return _apply_display_cleaning(df)
    except Exception as e:
        print(f"[data.get_shift_df] {e}")
        return pd.DataFrame()


def get_events_df(start_date: str, end_date: str) -> pd.DataFrame:
    """Query events_log for rows in [start_date, end_date].
    Accepts date or datetime strings (only the date portion is used)."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    try:
        with _open() as conn:
            return pd.read_sql_query(
                """SELECT * FROM events_log
                   WHERE Date >= ? AND Date <= ?
                   ORDER BY Date, Time """,
                conn,
                params=[start_date[:10], end_date[:10]],
            )
    except Exception as e:
        print(f"[data.get_events_df] {e}")
        return pd.DataFrame()


def get_date_range() -> tuple[str | None, str | None]:
    """Return min/max timestamp strings from available data tables.
    Priority: live_data.Date Time -> shift_protocol.Date Time.
    """
    if not DB_PATH.exists():
        return None, None

    try:
        with _open() as conn:
            for table in ("live_data", "shift_protocol"):
                if not _table_exists(conn, table):
                    continue
                try:
                    row = pd.read_sql_query(
                        f'SELECT MIN("Date Time") AS min_dt, MAX("Date Time") AS max_dt FROM {table}',
                        conn,
                    ).iloc[0]
                except Exception:
                    continue
                min_dt = row.get("min_dt")
                max_dt = row.get("max_dt")
                if pd.notna(min_dt) and pd.notna(max_dt):
                    return str(min_dt), str(max_dt)
    except Exception as e:
        print(f"[data.get_date_range] {e}")

    return None, None
