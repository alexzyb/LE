"""
BG Live Data ingest pipeline (Phase 8).

Reads long-table CSV exports incrementally, applies basic validation,
resamples to 30s buckets, pivots to wide format, and UPSERTs into SQLite.

Usage:
  python src/ingest.py --once --source BaumgartnerData
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import pandas as pd

from column_map import BY_VALUE_ID, BG_FILES
from config import BG_EXPORT_DIR

SRC_DIR = Path(__file__).resolve().parent
DB_PATH = SRC_DIR / "land_energy.db"
STATE_PATH = SRC_DIR / "ingest_state.json"


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"files": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"files": {}}


def _save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _read_delta_csv(path: Path, offset: int) -> tuple[pd.DataFrame, int]:
    if not path.exists():
        return pd.DataFrame(), offset
    size = path.stat().st_size
    if size <= offset:
        return pd.DataFrame(), size

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        if offset > 0:
            f.seek(offset)
            # Skip partial line if starting mid-file.
            f.readline()
            text = f.read()
            if not text.strip():
                return pd.DataFrame(), size
            csv_text = "value_id,value_name,timestamp_utc,real_value,sync_id,sync_timestamp_utc\n" + text
            df = pd.read_csv(pd.io.common.StringIO(csv_text))
        else:
            df = pd.read_csv(f)
    return df, size


def _collect_long_rows(source_dir: Path, state: dict) -> tuple[pd.DataFrame, dict]:
    rows = []
    file_state = state.setdefault("files", {})

    for base in BG_FILES:
        path = source_dir / f"{base}.csv"
        prev = int(file_state.get(path.name, 0))
        df, new_offset = _read_delta_csv(path, prev)
        file_state[path.name] = new_offset
        if df.empty:
            continue
        rows.append(df)

    if not rows:
        return pd.DataFrame(), state
    all_df = pd.concat(rows, ignore_index=True)
    return all_df, state


def _transform_long_to_wide(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    required = {"value_id", "timestamp_utc", "real_value"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    df = df.copy()
    df["value_id"] = pd.to_numeric(df["value_id"], errors="coerce").astype("Int64")
    df["real_value"] = pd.to_numeric(df["real_value"], errors="coerce")
    df["Date Time"] = pd.to_datetime(df["timestamp_utc"], errors="coerce", utc=True)
    df = df.dropna(subset=["value_id", "real_value", "Date Time"])

    # Keep only mapped BG points.
    df = df[df["value_id"].isin(BY_VALUE_ID.keys())].copy()
    if df.empty:
        return df

    df["dashboard_col"] = df["value_id"].astype(int).map(
        lambda vid: BY_VALUE_ID[vid]["dashboard_col"]
    )
    df["Date Time"] = df["Date Time"].dt.floor("30s").dt.strftime("%Y-%m-%dT%H:%M:%S")

    grouped = (
        df.sort_values("Date Time")
        .groupby(["Date Time", "dashboard_col"], as_index=False)["real_value"]
        .last()
    )
    wide = grouped.pivot(index="Date Time", columns="dashboard_col", values="real_value").reset_index()
    wide.columns.name = None
    return wide


def _ensure_live_data_table(conn: sqlite3.Connection, wide_df: pd.DataFrame) -> None:
    cols = [c for c in wide_df.columns if c != "Date Time"]
    if not cols:
        cols = [e["dashboard_col"] for e in BY_VALUE_ID.values()]

    col_defs = ',\n'.join([f'"{c}" REAL' for c in sorted(set(cols))])
    sql = f'''
    CREATE TABLE IF NOT EXISTS live_data (
      "Date Time" TEXT PRIMARY KEY,
      {col_defs}
    )
    '''
    conn.execute(sql)

    # Add missing columns for evolving schema.
    existing = pd.read_sql_query("PRAGMA table_info(live_data)", conn)["name"].tolist()
    for c in cols:
        if c not in existing:
            conn.execute(f'ALTER TABLE live_data ADD COLUMN "{c}" REAL')


def _upsert_live_data(conn: sqlite3.Connection, wide_df: pd.DataFrame) -> int:
    if wide_df.empty:
        return 0
    cols = list(wide_df.columns)
    quoted = [f'"{c}"' for c in cols]
    placeholders = ", ".join(["?"] * len(cols))
    update_set = ", ".join(
        [f'{q}=excluded.{q}' for q in quoted if q != '"Date Time"']
    )
    sql = f'''
    INSERT INTO live_data ({", ".join(quoted)})
    VALUES ({placeholders})
    ON CONFLICT("Date Time") DO UPDATE SET
    {update_set}
    '''
    conn.executemany(sql, wide_df[cols].itertuples(index=False, name=None))
    return len(wide_df)


def run_once(source: Path) -> int:
    state = _load_state()
    long_df, state = _collect_long_rows(source, state)
    wide_df = _transform_long_to_wide(long_df)

    with sqlite3.connect(DB_PATH) as conn:
        _ensure_live_data_table(conn, wide_df)
        n = _upsert_live_data(conn, wide_df)
        conn.commit()

    _save_state(state)
    print(f"[ingest] rows_upserted={n} source={source}")
    return n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single ingest cycle")
    parser.add_argument("--source", default=BG_EXPORT_DIR or "BaumgartnerData")
    args = parser.parse_args()

    source = Path(args.source)
    if args.once:
        run_once(source)
        return

    # Default behavior: single pass for now (safe for non-daemon environments).
    run_once(source)


if __name__ == "__main__":
    main()
