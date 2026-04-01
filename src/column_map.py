# src/column_map.py
"""
Centralized mapping: Baumgartner (BG) live CSV value_ids → Dashboard column names.

This is the SINGLE SOURCE OF TRUTH for the BG → Dashboard translation.
The dashboard column names MUST match exactly what app.py / charts.py use.

BG CSV format (long table):
  value_id, value_name, timestamp_utc, real_value, sync_id, sync_timestamp_utc

Time key: use `timestamp_utc` (actual measurement time from WinCC).
Ignore `sync_timestamp_utc` (CDC export time, metadata only).

Dashboard expects: wide table with "Date Time" + named columns.
"""

# ---------------------------------------------------------------------------
# A. Direct mappings: BG value_id → existing Dashboard column name
# ---------------------------------------------------------------------------
LIVE_COLUMN_MAP = [
    # -- Pellet Mill 1 --
    {
        "bg_file": "Pellet_Mill_1",
        "bg_value_name": "Actual_Current",
        "bg_value_id": 66,
        "dashboard_col": "Press 1 - Load Amps",
        "unit": "A",
        "group": "Mill1",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 800},
    },
    {
        "bg_file": "Pellet_Mill_1",
        "bg_value_name": "Actual_Speed_Dosing_Screw",
        "bg_value_id": 62,
        "dashboard_col": "Press 1 - Feeder %",
        "unit": "%",
        "group": "Mill1",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 120},
    },
    {
        "bg_file": "Pellet_Mill_1",
        "bg_value_name": "Left_Roller_Temperature",
        "bg_value_id": 67,
        "dashboard_col": "Press 1 - Left Roller Temperature",
        "unit": "°C",
        "group": "Mill1",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 250},
    },
    {
        "bg_file": "Pellet_Mill_1",
        "bg_value_name": "Right_Roller_Temperature",
        "bg_value_id": 68,
        "dashboard_col": "Press 1 - Right Roller Temperature",
        "unit": "°C",
        "group": "Mill1",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 250},
    },
    {
        "bg_file": "Pellet_Mill_1",
        "bg_value_name": "Energy",
        "bg_value_id": 171,
        "dashboard_col": "_pm1_energy_cumulative",
        "unit": "kWh",
        "group": "Mill1",
        "freq_sec": 5,
        "clean": {"type": "non_negative"},
    },
    # -- Pellet Mill 2 --
    {
        "bg_file": "Pellet_Mill_2",
        "bg_value_name": "Actual_Current",
        "bg_value_id": 69,
        "dashboard_col": "Press 2 - Load Amps",
        "unit": "A",
        "group": "Mill2",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 800},
    },
    {
        "bg_file": "Pellet_Mill_2",
        "bg_value_name": "Actual_Speed_Dosing_Screw",
        "bg_value_id": 64,
        "dashboard_col": "Press 2 - Feeder %",
        "unit": "%",
        "group": "Mill2",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 120},
    },
    {
        "bg_file": "Pellet_Mill_2",
        "bg_value_name": "Left_Roller_Temperature",
        "bg_value_id": 70,
        "dashboard_col": "Press 2 - Left Roller Temperature",
        "unit": "°C",
        "group": "Mill2",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 250},
    },
    {
        "bg_file": "Pellet_Mill_2",
        "bg_value_name": "Right_Roller_Temperature",
        "bg_value_id": 71,
        "dashboard_col": "Press 2 - Right Roller Temperature",
        "unit": "°C",
        "group": "Mill2",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 250},
    },
    {
        "bg_file": "Pellet_Mill_2",
        "bg_value_name": "Energy",
        "bg_value_id": 173,
        "dashboard_col": "_pm2_energy_cumulative",
        "unit": "kWh",
        "group": "Mill2",
        "freq_sec": 5,
        "clean": {"type": "non_negative"},
    },
    # -- Pellet Mill 3 --
    {
        "bg_file": "Pellet_Mill_3",
        "bg_value_name": "Actual_Current",
        "bg_value_id": 117,
        "dashboard_col": "Press 3 - Load Amps",
        "unit": "A",
        "group": "Mill3",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 800},
    },
    {
        "bg_file": "Pellet_Mill_3",
        "bg_value_name": "Actual_Speed_Dosing_Screw",
        "bg_value_id": 114,
        "dashboard_col": "Press 3 - Feeder %",
        "unit": "%",
        "group": "Mill3",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 120},
    },
    {
        "bg_file": "Pellet_Mill_3",
        "bg_value_name": "Left_Roller_Temperature",
        "bg_value_id": 118,
        "dashboard_col": "Press 3 - Left Roller Temperature",
        "unit": "°C",
        "group": "Mill3",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 250},
    },
    {
        "bg_file": "Pellet_Mill_3",
        "bg_value_name": "Right_Roller_Temperature",
        "bg_value_id": 119,
        "dashboard_col": "Press 3 - Right Roller Temperature",
        "unit": "°C",
        "group": "Mill3",
        "freq_sec": 1,
        "clean": {"type": "range", "min": 0, "max": 250},
    },
    {
        "bg_file": "Pellet_Mill_3",
        "bg_value_name": "Energy",
        "bg_value_id": 172,
        "dashboard_col": "_pm3_energy_cumulative",
        "unit": "kWh",
        "group": "Mill3",
        "freq_sec": 5,
        "clean": {"type": "non_negative"},
    },
    # -- Complete Plant --
    {
        "bg_file": "Complete_Plant",
        "bg_value_name": "Production",
        "bg_value_id": 75,
        "dashboard_col": "Total tons passed belt weigher (hour)",
        "unit": "t/h",
        "group": "Throughput",
        "freq_sec": 30,
        "clean": {"type": "non_negative"},
    },
    {
        "bg_file": "Complete_Plant",
        "bg_value_name": "Totaliser",
        "bg_value_id": 74,
        "dashboard_col": "Total Pellets passed belt weigher (cumlative)",
        "unit": "t",
        "group": "Throughput",
        "freq_sec": 30,
        "clean": {"type": "non_negative"},
    },
    # -- Pellet Silos --
    {
        "bg_file": "Pellet_Silo_1",
        "bg_value_name": "Fuel_Level",
        "bg_value_id": 150,
        "dashboard_col": "Pellet Silo Level 1 Readout",
        "unit": "t",
        "group": "Throughput",
        "freq_sec": 3600,
        "clean": {"type": "range", "min": 0, "max": 5000},
    },
    {
        "bg_file": "Pellet_Silo_2",
        "bg_value_name": "Fuel_Level",
        "bg_value_id": 149,
        "dashboard_col": "Pellet Silo Level 2 Readout",
        "unit": "t",
        "group": "Throughput",
        "freq_sec": 3600,
        "clean": {"type": "range", "min": 0, "max": 5000},
    },
    {
        "bg_file": "Pellet_Silo_3",
        "bg_value_name": "Fuel_Level",
        "bg_value_id": 148,
        "dashboard_col": "Pellet Silo Level 3 Readout",
        "unit": "t",
        "group": "Throughput",
        "freq_sec": 3600,
        "clean": {"type": "range", "min": 0, "max": 5000},
    },
    {
        "bg_file": "Pellet_Silo_1",
        "bg_value_name": "Infeed_Totaliser",
        "bg_value_id": 157,
        "dashboard_col": "_silo1_infeed_totaliser",
        "unit": "t",
        "group": "Throughput",
        "freq_sec": 3600,
        "clean": {"type": "non_negative"},
    },
    {
        "bg_file": "Pellet_Silo_2",
        "bg_value_name": "Infeed_Totaliser",
        "bg_value_id": 156,
        "dashboard_col": "_silo2_infeed_totaliser",
        "unit": "t",
        "group": "Throughput",
        "freq_sec": 3600,
        "clean": {"type": "non_negative"},
    },
    {
        "bg_file": "Pellet_Silo_3",
        "bg_value_name": "Infeed_Totaliser",
        "bg_value_id": 155,
        "dashboard_col": "_silo3_infeed_totaliser",
        "unit": "t",
        "group": "Throughput",
        "freq_sec": 3600,
        "clean": {"type": "non_negative"},
    },
    # -- Dispatch --
    {
        "bg_file": "Bagging_Station",
        "bg_value_name": "Totaliser",
        "bg_value_id": 152,
        "dashboard_col": "_bagging_totaliser",
        "unit": "t",
        "group": "Dispatch",
        "freq_sec": 3600,
        "clean": {"type": "non_negative"},
    },
    {
        "bg_file": "Truck_Loading_Station",
        "bg_value_name": "Totaliser",
        "bg_value_id": 159,
        "dashboard_col": "_truck_totaliser",
        "unit": "t",
        "group": "Dispatch",
        "freq_sec": 3600,
        "clean": {"type": "non_negative"},
    },
]

# ---------------------------------------------------------------------------
# Derived lookup indices
# ---------------------------------------------------------------------------
BY_VALUE_ID = {e["bg_value_id"]: e for e in LIVE_COLUMN_MAP}
BY_DASHBOARD_COL = {e["dashboard_col"]: e for e in LIVE_COLUMN_MAP}

BY_BG_FILE: dict[str, list[dict]] = {}
for _e in LIVE_COLUMN_MAP:
    BY_BG_FILE.setdefault(_e["bg_file"], []).append(_e)

# All dashboard column names that have a live BG source
LIVE_COLUMNS = [e["dashboard_col"] for e in LIVE_COLUMN_MAP]

# Columns starting with "_" are BG-only (no existing dashboard panel yet)
DASHBOARD_MAPPED_COLUMNS = [c for c in LIVE_COLUMNS if not c.startswith("_")]
BG_ONLY_COLUMNS = [c for c in LIVE_COLUMNS if c.startswith("_")]

# BG CSV files we expect to find
BG_FILES = list(BY_BG_FILE.keys())

# ---------------------------------------------------------------------------
# Pellet Silo capacity (tonnes) — for percentage calculation
# Set to 3500 t for all silos (pending factory confirmation).
# Adjust per factory confirmation once exact capacity is known.
# ---------------------------------------------------------------------------
SILO_MAX_CAPACITY = {
    "Pellet Silo Level 1 Readout": 3500,
    "Pellet Silo Level 2 Readout": 3500,
    "Pellet Silo Level 3 Readout": 3500,
}


def tons_to_pct(value, col):
    """Convert Fuel_Level tonnes to percentage (0-100) using SILO_MAX_CAPACITY."""
    if value is None:
        return None
    cap = SILO_MAX_CAPACITY.get(col)
    if not cap:
        return None
    pct = (float(value) / cap) * 100
    return max(0.0, min(100.0, pct))


# ---------------------------------------------------------------------------
# Cleaning helpers (applied at display time, NOT at ingest time)
# ---------------------------------------------------------------------------

def clean_value(value, rule):
    """Apply a cleaning rule to a single value. Returns None for rejected values."""
    if value is None or rule is None:
        return value
    try:
        v = float(value)
    except (ValueError, TypeError):
        return None

    rule_type = rule.get("type")

    if rule_type == "range":
        if v < rule["min"] or v > rule["max"]:
            return None
        return v

    if rule_type == "non_negative":
        return max(0.0, v)

    return v
