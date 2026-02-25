# src/data.py
"""Data access layer — all SQL queries against land_energy.db."""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "land_energy.db"


def _open():
    return sqlite3.connect(DB_PATH)


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
            df = pd.read_sql_query(
                """SELECT * FROM shift_protocol
                   WHERE "Date Time" >= ? AND "Date Time" <= ?
                   ORDER BY "Date Time" """,
                conn,
                params=[start, end],
            )
        df["Date Time"] = pd.to_datetime(df["Date Time"], errors="coerce")
        return df
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
