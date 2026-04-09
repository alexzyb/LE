# src/config.py
"""
Static configuration: colour palette, column map, default thresholds.
All values here serve as factory defaults; runtime overrides live in
thresholds.json (written by the Settings panel).
"""

import json
import os
from copy import deepcopy
from pathlib import Path as _Path

# ─── Environment Variables ────────────────────────────────────────────────────
DATABASE_URL   = os.environ.get("DATABASE_URL", "")        # e.g. postgresql://...
BG_EXPORT_DIR  = os.environ.get("BG_EXPORT_DIR", "")       # live CSV directory on VM

# ─── Colour Palette (dark / light SCADA themes) ─────────────────────────────
COLOR_SCHEMES = {
    "dark": {
        "bg":      "#1a1a2e",
        "card":    "#16213e",
        "accent":  "#0f3460",
        "green":   "#0f9b58",
        "yellow":  "#f4b400",
        "red":     "#e05545",   # improved contrast (4.0:1 vs old 3.2:1)
        "text":    "#e0e0e0",
        "subtext": "#b0b0b0",   # improved contrast (4.8:1 vs old 3.5:1)
        "border":  "#2a2a4a",
        "mill":    ["#4dd0e1", "#f06292", "#aed581"],
        "overlay": "rgba(26,26,46,0.68)",
        "green_alpha": "rgba(15,155,88,0.25)",
        "gauge_red": "#3d1a1a", "gauge_yellow": "#3d3312", "gauge_green": "#0f3d27",
    },
    "light": {
        "bg":      "#f0f2f5",
        "card":    "#ffffff",
        "accent":  "#e3e8ef",
        "green":   "#0d8a4e",   # 4.6:1 on white
        "yellow":  "#b8860b",   # 4.5:1 on white
        "red":     "#c62828",   # 5.6:1 on white
        "text":    "#1a1a2e",
        "subtext": "#5a5a6e",   # 5.3:1 on #f0f2f5
        "border":  "#d0d4da",
        "mill":    ["#00838f", "#c2185b", "#558b2f"],
        "overlay": "rgba(240,242,245,0.68)",
        "green_alpha": "rgba(13,138,78,0.25)",
        "gauge_red": "#fde0e0", "gauge_yellow": "#fdf3d0", "gauge_green": "#d0f0dd",
    },
}
COLOR_SCHEME = COLOR_SCHEMES["dark"]   # backward compat


def get_color_scheme(theme="dark"):
    """Return colour palette for the given theme."""
    return COLOR_SCHEMES.get(theme, COLOR_SCHEMES["dark"])

# ─── Blank Separator & Damaged Columns (0-indexed in the raw CSV) ─────────────
SKIP_COLS    = {1, 14, 18, 24, 30, 36, 38, 44, 55}   # empty separator cols
DAMAGED_COLS = {52, 53, 54}                            # #REF!/#VALUE! cols

# ─── Column Map ───────────────────────────────────────────────────────────────
# Key   = 0-indexed position in the original CSV (used for documentation only).
# name  = exact column name as it appears in the CSV header row (row 1).
# These names are what pandas / SQLite use after init_db.py loads the file.
COLUMN_MAP = {
    0:  {"name": "Date Time",                                          "unit": "",       "group": "Time"},
    # ── Dryer ──────────────────────────────────────────────────────────────
    2:  {"name": "Dryer Tonnage",                                      "unit": "t/h",    "group": "Dryer"},
    3:  {"name": "Moisture %  Displayed Value at Dryer Inlet",         "unit": "%",      "group": "Dryer"},
    4:  {"name": "Dryer bed Temp\u00b0 C",                             "unit": "\u00b0C","group": "Dryer"},
    5:  {"name": "Moisture %  Displayed Value at Dryer Outlet",        "unit": "%",      "group": "Dryer"},
    6:  {"name": "Moisture %  Actual Value at Dryer Outlet",           "unit": "%",      "group": "Dryer"},
    7:  {"name": "Dryer belt speed %",                                 "unit": "%",      "group": "Dryer"},
    8:  {"name": "Dryer out feed t/h",                                 "unit": "t/h",    "group": "Dryer"},
    9:  {"name": "Dry Silo 1 Level %",                                 "unit": "%",      "group": "Dryer"},
    10: {"name": "Dry Silo 2 Level %",                                 "unit": "%",      "group": "Dryer"},
    11: {"name": "Dryer 1/2 fan speed",                                "unit": "",       "group": "Dryer"},
    12: {"name": "Fresh Air Temp\u00b0 C",                             "unit": "\u00b0C","group": "Dryer"},
    13: {"name": "Water Addition at Dryer",                            "unit": "",       "group": "Dryer"},
    # ── Process ────────────────────────────────────────────────────────────
    15: {"name": "Valve position open at %",                           "unit": "%",      "group": "Process"},
    16: {"name": "Pellet Mill Moistures %",                            "unit": "%",      "group": "Process"},
    17: {"name": "Press Hopper Temperature",                           "unit": "\u00b0C","group": "Process"},
    # ── Mill 1 ─────────────────────────────────────────────────────────────
    19: {"name": "Press 1 - Left Roller Temperature",                  "unit": "\u00b0C","group": "Mill1"},
    20: {"name": "Press 1 - Right Roller Temperature",                 "unit": "\u00b0C","group": "Mill1"},
    21: {"name": "Press 1 - Load Amps",                                "unit": "A",      "group": "Mill1"},
    22: {"name": "Press 1 - Feeder %",                                 "unit": "%",      "group": "Mill1"},
    23: {"name": "Press 1 kWh/t",                                      "unit": "kWh/t",  "group": "Mill1"},
    # ── Mill 2 ─────────────────────────────────────────────────────────────
    25: {"name": "Press 2 - Left Roller Temperature",                  "unit": "\u00b0C","group": "Mill2"},
    26: {"name": "Press 2 - Right Roller Temperature",                 "unit": "\u00b0C","group": "Mill2"},
    27: {"name": "Press 2 - Load Amps",                                "unit": "A",      "group": "Mill2"},
    28: {"name": "Press 2 - Feeder %",                                 "unit": "%",      "group": "Mill2"},
    29: {"name": "Press 2 kWh/t",                                      "unit": "kWh/t",  "group": "Mill2"},
    # ── Mill 3 ─────────────────────────────────────────────────────────────
    31: {"name": "Press 3 - Left Roller Temperature",                  "unit": "\u00b0C","group": "Mill3"},
    32: {"name": "Press 3 - Right Roller Temperature",                 "unit": "\u00b0C","group": "Mill3"},
    33: {"name": "Press 3 - Load Amps",                                "unit": "A",      "group": "Mill3"},
    34: {"name": "Press 3 - Feeder %",                                 "unit": "%",      "group": "Mill3"},
    35: {"name": "Press 3 kWh/t",                                      "unit": "kWh/t",  "group": "Mill3"},
    # ── Filter ─────────────────────────────────────────────────────────────
    37: {"name": "Main Filter kP",                                     "unit": "kPa",    "group": "Filter"},
    # ── Quality ────────────────────────────────────────────────────────────
    39: {"name": "Pellet Moisture %",                                  "unit": "%",      "group": "Quality"},
    40: {"name": "Bulk  Density g/l",                                  "unit": "g/l",    "group": "Quality"},
    41: {"name": "Durability %",                                       "unit": "%",      "group": "Quality"},
    42: {"name": "Temp of Pellets at cooler",                          "unit": "\u00b0C","group": "Quality"},
    43: {"name": "Average Pellet Length(mm)",                          "unit": "mm",     "group": "Quality"},
    # ── Throughput ─────────────────────────────────────────────────────────
    45: {"name": "Total Pellets passed belt weigher (cumlative)",      "unit": "t",      "group": "Throughput"},
    46: {"name": "Total pellet to totes hopper (cumulative)",          "unit": "t",      "group": "Throughput"},
    47: {"name": "Silo  strain gauge level (tonnes)",                  "unit": "t",      "group": "Throughput"},
    48: {"name": "Pellet Silo Level 1 Readout",                        "unit": "t",      "group": "Throughput"},
    49: {"name": "Pellet Silo Level 2 Readout",                        "unit": "t",      "group": "Throughput"},
    50: {"name": "Pellet Silo Level 3 Readout",                        "unit": "t",      "group": "Throughput"},
    51: {"name": "Total tons passed belt weigher (hour)",              "unit": "t/h",    "group": "Throughput"},
    # 52-54 damaged — omitted from DB (init_db drops them)
    # ── CHP ────────────────────────────────────────────────────────────────
    56: {"name": "Furnace O2%",                                        "unit": "%",      "group": "CHP"},
    57: {"name": "Furnace Temp",                                       "unit": "\u00b0C","group": "CHP"},
    58: {"name": "Furnace Pressure",                                   "unit": "Pa",     "group": "CHP"},
    59: {"name": "Thermal Oil OUT",                                    "unit": "\u00b0C","group": "CHP"},
    60: {"name": "Turbine Generated Power kW",                         "unit": "kW",     "group": "CHP"},
    61: {"name": "Flue Gas Fan",                                       "unit": "%",      "group": "CHP"},
    62: {"name": "Primary Air Fan",                                    "unit": "%",      "group": "CHP"},
    63: {"name": "HRU Bypass Damper",                                  "unit": "",       "group": "CHP"},
}

# ─── Default Thresholds ───────────────────────────────────────────────────────
# mode "dual"  → red_low, green_min, green_max, red_high
#   < red_low            → RED
#   red_low..green_min   → YELLOW
#   green_min..green_max → GREEN
#   green_max..red_high  → YELLOW
#   > red_high           → RED
#
# mode "lower" → red_below, green_above   (higher is better)
#   < red_below              → RED
#   red_below..green_above   → YELLOW
#   > green_above            → GREEN
#
# mode "upper" → green_below, red_above   (lower is better)
#   < green_below            → GREEN
#   green_below..red_above   → YELLOW
#   > red_above              → RED
#
# cols = list of CSV column indices this threshold applies to
DEFAULT_THRESHOLDS = {
    "press_load_amps": {
        "label": "Press Load Amps",
        "mode": "dual",
        "red_low": 50, "green_min": 400, "green_max": 460, "red_high": 480,
        "unit": "A",
        "cols": ["Press 1 - Load Amps", "Press 2 - Load Amps", "Press 3 - Load Amps"],
    },
    "pellet_mill_moisture": {
        "label": "Pellet Mill Moisture",
        "mode": "dual",
        "red_low": 9.0, "green_min": 10.0, "green_max": 11.5, "red_high": 12.5,
        "unit": "%",
        "cols": [16],
    },
    "dryer_outlet_moisture": {
        "label": "Dryer Outlet Moisture (Actual)",
        "mode": "dual",
        "red_low": 6.0, "green_min": 7.0, "green_max": 10.0, "red_high": 12.0,
        "unit": "%",
        "cols": [6],
    },
    "dry_silo_level": {
        "label": "Dry Silo Level",
        "mode": "dual",
        "red_low": 20, "green_min": 30, "green_max": 80, "red_high": 90,
        "unit": "%",
        "cols": [9, 10],
    },
    "durability": {
        "label": "Durability",
        "mode": "lower",
        "red_below": 97.0, "green_above": 97.5,
        "unit": "%",
        "cols": [41],
    },
    "pellet_moisture_finished": {
        "label": "Pellet Moisture (Finished)",
        "mode": "upper",
        "green_below": 10.0, "red_above": 11.0,
        "unit": "%",
        "cols": [39],
    },
    "avg_pellet_length": {
        "label": "Avg Pellet Length",
        "mode": "upper",
        "green_below": 40, "red_above": 45,
        "unit": "mm",
        "cols": [43],
    },
    "bulk_density": {
        "label": "Bulk Density",
        "mode": "lower",
        "red_below": 600, "green_above": 630,
        "unit": "g/l",
        "cols": [40],
    },
    "main_filter_kp": {
        "label": "Main Filter kP",
        "mode": "lower",
        "red_below": 0.2, "green_above": 0.5,
        "unit": "kPa",
        "cols": [37],
    },
    "furnace_temp": {
        "label": "Furnace Temp",
        "mode": "dual",
        "red_low": 877, "green_min": 920, "green_max": 960, "red_high": 960,
        "unit": "\u00b0C",
        "cols": [57],
    },
    "thermal_oil_out": {
        "label": "Thermal Oil OUT",
        "mode": "lower",
        "red_below": 300, "green_above": 305,
        "unit": "\u00b0C",
        "cols": [59],
    },
    "turbine_power": {
        "label": "Turbine Power",
        "mode": "lower",
        "red_below": 500, "green_above": 2000,
        "unit": "kW",
        "cols": [60],
    },
    "dryer_out_feed": {
        "label": "Dryer Out Feed",
        "mode": "lower",
        "red_below": 9.0, "green_above": 11.0,
        "unit": "t/h",
        "cols": [8],
    },
    "belt_weigher_hourly": {
        "label": "Belt Weigher (Hourly)",
        "mode": "lower",
        "red_below": 10.0, "green_above": 14.0,
        "unit": "t/h",
        "cols": ["Total tons passed belt weigher (hour)"],
    },
    "valve_position": {
        "label": "Valve Position",
        "mode": "dual",
        "red_low": 15, "green_min": 25, "green_max": 40, "red_high": 60,
        "unit": "%",
        "cols": [15],
    },
    "feeder_pct": {
        "label": "Feeder %",
        "mode": "lower",
        "red_below": 40, "green_above": 55,
        "unit": "%",
        "cols": ["Press 1 - Feeder %", "Press 2 - Feeder %", "Press 3 - Feeder %"],
    },
    # ── Pellet Silo Level % (Phase 8, split by capacity) ───────────────────────
    "pellet_silo_level_1": {
        "label": "Pellet Silo 1 (450t)",
        "mode": "dual",
        "red_low": 15, "green_min": 25, "green_max": 85, "red_high": 95,
        "unit": "%",
        "cols": ["Pellet Silo Level 1 Readout"],
    },
    "pellet_silo_level_23": {
        "label": "Pellet Silo 2/3 (3500t)",
        "mode": "dual",
        "red_low": 10, "green_min": 20, "green_max": 80, "red_high": 90,
        "unit": "%",
        "cols": ["Pellet Silo Level 2 Readout", "Pellet Silo Level 3 Readout"],
    },
}

# ─── Settings Panel Grouping (Phase 8: 5 active BG-backed thresholds) ─────────
THRESHOLD_GROUPS = {
    "Mill":       ["press_load_amps", "feeder_pct"],
    "Throughput": ["belt_weigher_hourly"],
    "Silo":       ["pellet_silo_level_1", "pellet_silo_level_23"],
}

# ─── Threshold Persistence ────────────────────────────────────────────────────

_THRESHOLDS_JSON = _Path(__file__).resolve().parent / "thresholds.json"

_BOUNDARY_KEYS = {"red_low", "green_min", "green_max", "red_high",
                  "red_below", "green_above", "green_below", "red_above"}


def get_thresholds():
    """Return merged thresholds: DEFAULT_THRESHOLDS overlaid with thresholds.json."""
    merged = deepcopy(DEFAULT_THRESHOLDS)
    if _THRESHOLDS_JSON.exists():
        try:
            with open(_THRESHOLDS_JSON, "r", encoding="utf-8") as f:
                overrides = json.load(f)
            for key, vals in overrides.items():
                if key in merged and isinstance(vals, dict):
                    merged[key].update(vals)
        except (json.JSONDecodeError, OSError):
            pass
    return merged


def save_thresholds(overrides_dict):
    """Write user overrides to thresholds.json. Only boundary fields are stored."""
    clean = {}
    for key, vals in overrides_dict.items():
        if key in DEFAULT_THRESHOLDS:
            clean[key] = {k: v for k, v in vals.items() if k in _BOUNDARY_KEYS}
    with open(_THRESHOLDS_JSON, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)


def reset_thresholds():
    """Delete thresholds.json, restoring factory defaults."""
    if _THRESHOLDS_JSON.exists():
        _THRESHOLDS_JSON.unlink()
