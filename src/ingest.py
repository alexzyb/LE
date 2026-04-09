#!/usr/bin/env python3
# src/ingest.py
"""
BG CSV Ingestion Engine (Phase 8)

Usage:
  python src/ingest.py --source BaumgartnerData/ --once   # one-shot import
  python src/ingest.py --source BaumgartnerData/           # watch loop (every 5s)
  python src/ingest.py --source D:\\BG_Export\\            # production Windows VM
"""

import argparse
import io
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from column_map import BY_VALUE_ID, LIVE_COLUMNS

DB_PATH    = SRC / "land_energy.db"
STATE_FILE = SRC / "ingest_state.json"


# ─── Database setup ───────────────────────────────────────────────────────────

def ensure_table(conn):
    """Create live_data table and index if they don't exist."""
    cols_ddl = ",\n    ".join(f'"{c}" REAL' for c in LIVE_COLUMNS)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS live_data (
            "Date Time" TEXT NOT NULL PRIMARY KEY,
            {cols_ddl}
        )
    """)
    conn.execute(
        'CREATE INDEX IF NOT EXISTS idx_dt ON live_data ("Date Time")'
    )
    conn.commit()


# ─── State persistence ────────────────────────────────────────────────────────

def read_state() -> dict:
    """Load byte-offset state from disk (file → offset mapping)."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def write_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ─── CSV reading (chunked) ───────────────────────────────────────────────────

CHUNK_SIZE = 50 * 1024 * 1024  # 50 MB per chunk — safe for large CSV files


def _get_header(csv_path: Path):
    """Read the first line (header) and return (header_str, header_end_offset)."""
    with open(csv_path, "rb") as f:
        header_bytes = f.readline()
        return header_bytes.decode("utf-8", errors="replace").strip(), f.tell()


def read_chunk(csv_path: Path, offset: int, header_line: str):
    """
    Read up to CHUNK_SIZE bytes of complete lines from csv_path at offset.
    Returns (DataFrame, new_offset, done).
    'done' is True when there is no more data to read.
    """
    try:
        file_size = csv_path.stat().st_size
    except OSError:
        return pd.DataFrame(), offset, True

    if offset >= file_size:
        return pd.DataFrame(), offset, True

    with open(csv_path, "rb") as f:
        f.seek(offset)
        raw = f.read(CHUNK_SIZE)

    if not raw:
        return pd.DataFrame(), offset, True

    # Trim to last complete line (avoid half-written line at chunk boundary)
    last_nl = raw.rfind(b"\n")
    if last_nl < 0:
        return pd.DataFrame(), offset, True

    complete   = raw[: last_nl + 1].decode("utf-8", errors="replace")
    new_offset = offset + last_nl + 1
    done       = new_offset >= file_size

    try:
        df = pd.read_csv(io.StringIO(header_line + "\n" + complete))
    except Exception as e:
        print(f"  [ingest] parse error {csv_path.name} "
              f"at byte {offset:,}: {type(e).__name__}: {e}")
        return pd.DataFrame(), new_offset, done

    return df, new_offset, done


# ─── Processing (long → wide, 30s resample) ──────────────────────────────────

def process_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert BG long-format rows → wide 30s-bucketed DataFrame.

    Input columns: value_id, value_name, timestamp_utc, real_value,
                   sync_id, sync_timestamp_utc
    Output: "Date Time" (ISO string) + one column per dashboard_col.

    - Uses timestamp_utc (actual WinCC time), ignores sync_timestamp_utc.
    - Groups by 30s floor bucket; takes last value per (bucket, column).
    """
    if raw_df.empty or "value_id" not in raw_df.columns:
        return pd.DataFrame()

    known = set(BY_VALUE_ID.keys())
    df = raw_df[raw_df["value_id"].isin(known)].copy()
    if df.empty:
        return pd.DataFrame()

    df["dashboard_col"] = df["value_id"].map(
        lambda vid: BY_VALUE_ID[vid]["dashboard_col"]
    )

    # Parse measurement timestamp (UTC-aware).
    # BG format: "2024-03-22T08:27:00.1910000+00:00" (ISO 8601 with sub-second + offset).
    # utc=True normalises all tz-aware strings to UTC; errors="coerce" drops truly bad rows.
    df["ts"] = pd.to_datetime(df["timestamp_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["ts"])
    if df.empty:
        return pd.DataFrame()

    df["val"] = pd.to_numeric(df["real_value"], errors="coerce")

    # 30-second floor bucket, timezone-naive for SQLite storage
    df["bucket"] = df["ts"].dt.floor("30s").dt.tz_localize(None)

    # Last value per (bucket, col) — preserves most recent reading in window
    df = (
        df.groupby(["bucket", "dashboard_col"])["val"]
        .last()
        .reset_index()
    )

    # Pivot to wide format
    wide = df.pivot(index="bucket", columns="dashboard_col", values="val")
    wide.index.name = "Date Time"
    wide = wide.reset_index()
    wide["Date Time"] = wide["Date Time"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    return wide


# ─── UPSERT ───────────────────────────────────────────────────────────────────

def upsert_df(conn, wide_df: pd.DataFrame) -> int:
    """
    UPSERT wide_df rows into live_data.
    On conflict, keep existing non-null values (COALESCE strategy).
    This handles the case where different CSV files arrive at different times
    and gradually fill in columns for the same 30s bucket.
    """
    if wide_df.empty:
        return 0

    present_cols = ["Date Time"] + [c for c in LIVE_COLUMNS if c in wide_df.columns]
    df = wide_df[present_cols].copy()

    cols_q        = ", ".join(f'"{c}"' for c in df.columns)
    placeholders  = ", ".join("?" for _ in df.columns)
    update_parts  = ", ".join(
        f'"{c}" = COALESCE(excluded."{c}", live_data."{c}")'
        for c in df.columns if c != "Date Time"
    )

    sql = (
        f'INSERT INTO live_data ({cols_q}) VALUES ({placeholders})'
        f' ON CONFLICT("Date Time") DO UPDATE SET {update_parts}'
    )

    rows = [
        tuple(None if pd.isna(v) else v for v in row)
        for row in df.itertuples(index=False, name=None)
    ]

    conn.executemany(sql, rows)
    conn.commit()
    return len(rows)


# ─── Main ingest pass ─────────────────────────────────────────────────────────

def ingest_once(source_dir: str, verbose=True) -> int:
    """
    One full pass over all *.csv files in source_dir.
    Reads in 50 MB chunks to keep memory usage low even for multi-GB files.
    Returns number of time-buckets upserted.
    """
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"[ingest] Source directory not found: {source_path}")
        return 0

    state = read_state()

    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        ensure_table(conn)

        total = 0
        for csv_file in sorted(source_path.glob("*.csv")):
            key    = csv_file.name
            header_line, header_end = _get_header(csv_file)
            offset = max(state.get(key, 0), header_end)

            file_raw_rows = 0
            file_buckets  = 0
            chunk_num     = 0

            while True:
                chunk_num += 1
                raw_df, new_offset, done = read_chunk(
                    csv_file, offset, header_line
                )
                offset = new_offset

                if not raw_df.empty:
                    wide_df = process_df(raw_df)
                    if not wide_df.empty:
                        n = upsert_df(conn, wide_df)
                        file_raw_rows += len(raw_df)
                        file_buckets  += n

                if done:
                    break

            state[key] = offset
            total += file_buckets

            if verbose and file_buckets > 0:
                print(f"  {key}: {file_raw_rows:,} raw rows → "
                      f"{file_buckets:,} 30s buckets")

    write_state(state)
    if verbose:
        print(f"[ingest] Done. Total upserted: {total:,} time-buckets")
    return total


# ─── Watch loop ───────────────────────────────────────────────────────────────

def watch_loop(source_dir: str, interval_sec: int = 5):
    """Continuously poll source_dir every interval_sec seconds."""
    print(f"[ingest] Watching '{source_dir}' every {interval_sec}s  (Ctrl+C to stop)")
    while True:
        try:
            n = ingest_once(source_dir, verbose=False)
            if n:
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"[ingest] {ts}  +{n} buckets")
        except KeyboardInterrupt:
            print("\n[ingest] Stopped.")
            break
        except Exception as e:
            print(f"[ingest] Error: {e}")
        time.sleep(interval_sec)


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BG CSV Ingest Engine (Phase 8)")
    parser.add_argument(
        "--source", required=True,
        help="Directory containing BG CSV files (e.g. BaumgartnerData/ or D:\\BG_Export\\)"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single pass then exit (omit for continuous watch loop)"
    )
    parser.add_argument(
        "--interval", type=int, default=5,
        help="Watch-loop poll interval in seconds (default: 5)"
    )
    args = parser.parse_args()

    if args.once:
        ingest_once(args.source)
    else:
        ingest_once(args.source)          # initial full pass
        watch_loop(args.source, args.interval)


if __name__ == "__main__":
    main()
