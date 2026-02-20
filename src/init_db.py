# src/init_db.py
"""
Reads the three CSVs from data/ and writes a clean SQLite database at
src/land_energy.db.

Run once (or whenever the source CSV files change):
    python src/init_db.py

Cleaning rules applied to Shift_Protocol_date_time_merged.csv:
  - Header is on row 1 (row 0 = group labels, skipped automatically)
  - Blank separator columns (1,14,18,24,30,36,38,44,55) are dropped
  - Damaged columns 52-54 (#REF!/#VALUE!) are dropped
  - All remaining #REF! / #VALUE! strings and bare empty cells → NULL
  - Date Time: DD/MM/YYYY HH:MM:SS → ISO 8601 (YYYY-MM-DDTHH:MM:SS)
  - Col 51 (belt weigher hourly): |value| > 50 → NULL  (6 known noise rows)

Events_Log.csv:
  - Header is on row 2 (rows 0-1 are title/instructions)
  - Duration (H:MM:SS or HH:MM:SS) converted to minutes → Duration_min
  - Date normalised to ISO (YYYY-MM-DD)

Meter_Readings.csv:
  - Loaded as-is; reserved for future use (no dashboard panel in Phase 1)
"""

import re
import sqlite3
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent   # C:/LE/
DATA_DIR   = BASE_DIR / "data"
DB_PATH    = Path(__file__).resolve().parent / "land_energy.db"   # src/land_energy.db

CSV_SHIFT  = DATA_DIR / "Shift_Protocol_date_time_merged.csv"
CSV_EVENTS = DATA_DIR / "Events_Log.csv"
CSV_METER  = DATA_DIR / "Meter_Readings.csv"

# Column indices (0-based) to drop from the Shift Protocol CSV
SKIP_COLS    = {1, 14, 18, 24, 30, 36, 38, 44, 55}   # blank separators
DAMAGED_COLS = {52, 53, 54}                            # #REF!/#VALUE! cols
BELT_WEIGHER = "Total tons passed belt weigher (hour)" # Col 51 noise filter

# Strings that represent missing / error values in the raw CSVs
ERROR_STRINGS = {"#REF!", "#VALUE!", "#N/A", "N/A", ""}


def _parse_hms(value) -> Optional[float]:
    """Convert H:MM:SS or HH:MM:SS to decimal minutes.  Returns None on failure."""
    if not isinstance(value, str):
        return None
    s = value.strip()
    m = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})", s)
    if m:
        h, mi, sec = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return round(h * 60 + mi + sec / 60, 2)
    return None


def _read_csv_robust(path: Path, **kwargs) -> pd.DataFrame:
    """Try UTF-8-sig first, fall back to cp1252 (common for Excel exports)."""
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode {path} with any of: utf-8-sig, cp1252, latin-1")


# ─── Shift Protocol ───────────────────────────────────────────────────────────

def load_shift_csv() -> pd.DataFrame:
    """Load, clean and return the main shift-protocol data as a DataFrame."""
    # Row 0 = group labels (Dryer, Dryer, …), Row 1 = column names, Row 2+ = data
    df = _read_csv_robust(CSV_SHIFT, header=1, dtype=str)

    # ── Drop blank separator and damaged columns by position ─────────────────
    drop_positions = SKIP_COLS | DAMAGED_COLS
    cols_to_drop = [
        df.columns[i] for i in sorted(drop_positions)
        if i < len(df.columns)
    ]
    df = df.drop(columns=cols_to_drop, errors="ignore")

    # ── Normalise Date Time column ────────────────────────────────────────────
    if "Date Time" in df.columns:
        df["Date Time"] = (
            pd.to_datetime(df["Date Time"], dayfirst=True, errors="coerce")
            .dt.strftime("%Y-%m-%dT%H:%M:%S")
        )

    # ── Replace error strings → NaN, then coerce to numeric ──────────────────
    for col in df.columns:
        if col == "Date Time":
            continue
        df[col] = df[col].str.strip()
        df[col] = df[col].replace(list(ERROR_STRINGS), np.nan)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Col 51: filter belt-weigher noise (|value| > 50 → NaN) ───────────────
    if BELT_WEIGHER in df.columns:
        df.loc[df[BELT_WEIGHER].abs() > 50, BELT_WEIGHER] = np.nan

    return df


# ─── Events Log ───────────────────────────────────────────────────────────────

def load_events_csv() -> pd.DataFrame:
    """Load Events_Log.csv and convert Duration to minutes."""
    # Row 0 = title, Row 1 = instructions text, Row 2 = actual column headers
    df = _read_csv_robust(CSV_EVENTS, header=2, dtype=str)

    # Rename to canonical dashboard names
    rename_map = {
        "Event Time":     "Time",
        "Total Downtime": "Duration",
        "Event":          "Event Description",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Normalise Date
    if "Date" in df.columns:
        df["Date"] = (
            pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
            .dt.strftime("%Y-%m-%d")
        )

    # Convert Duration string → decimal minutes
    if "Duration" in df.columns:
        df["Duration_min"] = df["Duration"].apply(_parse_hms)
        df = df.drop(columns=["Duration"])

    # Drop rows that have no usable date (header bleed-through, etc.)
    if "Date" in df.columns:
        df = df[df["Date"].notna()].reset_index(drop=True)

    return df


# ─── Meter Readings ───────────────────────────────────────────────────────────

def load_meter_csv() -> pd.DataFrame:
    """Load Meter_Readings.csv as-is (reserved for future panels)."""
    return _read_csv_robust(CSV_METER, dtype=str)


# ─── Write to SQLite ──────────────────────────────────────────────────────────

def write_db(
    conn: sqlite3.Connection,
    shift: pd.DataFrame,
    events: pd.DataFrame,
    meter: pd.DataFrame,
) -> None:
    shift.to_sql("shift_protocol",  conn, if_exists="replace", index=False)
    events.to_sql("events_log",     conn, if_exists="replace", index=False)
    meter.to_sql("meter_readings",  conn, if_exists="replace", index=False)


# ─── Column-name verification helper ─────────────────────────────────────────

def _verify_key_columns(df: pd.DataFrame) -> None:
    """Warn if any dashboard-critical column is missing from the loaded data."""
    key_cols = [
        "Date Time",
        "Dryer out feed t/h",
        "Dry Silo 1 Level %",
        "Dry Silo 2 Level %",
        "Moisture %  Actual Value at Dryer Outlet",
        "Moisture %  Displayed Value at Dryer Outlet",
        "Press 1 - Load Amps",
        "Press 2 - Load Amps",
        "Press 3 - Load Amps",
        "Press 1 - Feeder %",
        "Press 2 - Feeder %",
        "Press 3 - Feeder %",
        "Main Filter kP",
        "Pellet Moisture %",
        "Bulk  Density g/l",
        "Durability %",
        "Average Pellet Length(mm)",
        "Total Pellets passed belt weigher (cumlative)",
        "Total tons passed belt weigher (hour)",
        "Pellet Silo Level 1 Readout",
        "Pellet Silo Level 2 Readout",
        "Pellet Silo Level 3 Readout",
        "Furnace Temp",
        "Thermal Oil OUT",
        "Turbine Generated Power kW",
        "HRU Bypass Damper",
    ]
    missing = [c for c in key_cols if c not in df.columns]
    if missing:
        print(f"  WARNING — {len(missing)} expected column(s) not found:")
        for c in missing:
            print(f"    - {c!r}")
    else:
        print("  All key columns present. OK.")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Source directory : {DATA_DIR}")
    print(f"Target database  : {DB_PATH}")
    print()

    print("[1/3] Loading Shift Protocol CSV …")
    shift = load_shift_csv()
    print(f"  Rows: {len(shift)}   Columns: {len(shift.columns)}")
    _verify_key_columns(shift)

    print("[2/3] Loading Events Log CSV …")
    events = load_events_csv()
    print(f"  Rows: {len(events)}   Columns: {len(events.columns)}")

    print("[3/3] Loading Meter Readings CSV …")
    meter = load_meter_csv()
    print(f"  Rows: {len(meter)}   Columns: {len(meter.columns)}")

    print()
    print(f"Writing SQLite database …")
    DB_PATH.unlink(missing_ok=True)          # start fresh every run
    with sqlite3.connect(DB_PATH) as conn:
        write_db(conn, shift, events, meter)

    size_kb = DB_PATH.stat().st_size / 1024
    print(f"Done.  {DB_PATH.name}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
