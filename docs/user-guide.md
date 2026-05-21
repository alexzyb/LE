# Land Energy Pellet Line Dashboard — User Guide

**Site:** Girvan, Scotland  |  **Version:** Phase 8 (Live Data)  |  **For:** Plant Operations Team

---

## 1. System Overview

```
  BG SCADA (CSV files)  ──►  ingest.py  ──►  SQLite DB  ──►  Dashboard
       on VM disk            every 5 s       land_energy.db    localhost:8050
```

The BG system writes sensor readings to CSV files. The ingest engine reads new data every 5 seconds, compresses it into 30-second intervals, and stores it in a local database. The dashboard queries this database and displays live charts and KPI cards in your browser.

---

## 2. Data Sources

| CSV File | Sensors | Frequency | Status |
|---|---|---|---|
| Pellet_Mill_1 / 2 / 3 | Amps, Feeder %, Roller Temp, Energy | ~1 s | **Historical** (Mar–May 2024) |
| Complete_Plant | Production Rate, Totaliser | ~30 s | **Live** |
| Pellet_Silo_1 / 2 / 3 | Fuel Level, Infeed Totaliser | ~1 h | **Live** |
| Bagging_Station | Totaliser | ~1 h | **Live** |
| Truck_Loading_Station | Totaliser | ~1 h | **Live** |

> **Mill 1/2/3 Note:** These files currently contain ~7 GB of **historical data (March–May 2024)**. The system is still processing this backlog, so Mill charts (Amps, Feeder, Temperature, Energy) display 2024 values — not current readings. It is not yet confirmed whether this is due to the large data volume still being ingested, or whether the BG system has not begun writing current Mill data. **All other sources are live.**

---

## 3. Page 1 — Overview

> **[Screenshot — Overview page]**

### Production

| Card | Shows | Unit |
|---|---|---|
| **Daily Output** | Today's production (not affected by time range selection) | t |
| **Production Rate** | Latest belt weigher reading | t/h |
| **Mills Active** | How many mills are running (e.g. "2/3") | — |
| **YTD Output** | This year's accumulated production (Jan 1 → now) | t |

**Mills Active colour:**

| Display | Colour |
|---|---|
| 3/3 | 🟢 Green — all running |
| 2/3 or 1/3 | 🟡 Yellow — partial |
| 0/3 | 🔴 Red — all stopped |

### Mill Status

Three cards showing latest Load Amps per mill. Colour follows threshold settings (see [Section 7](#7-threshold-settings)).

### Pellet Silos

Three tank gauges showing fill level as a percentage. Silo 1 capacity = 450 t; Silo 2 & 3 = 3,500 t each. The displayed percentage is calculated from the raw tonnes reading. Updated ~once per hour.

> **[Screenshot — Silo gauges]**

### Dispatch

| Card | Shows |
|---|---|
| **Daily Bagging** | Today's bagging output (t) — not affected by time range |
| **Daily Truck** | Today's truck loading (t) — not affected by time range |
| **YTD Bagging** | This year's accumulated bagging (Jan 1 → now) (t) |
| **YTD Truck** | This year's accumulated truck loading (Jan 1 → now) (t) |

---

## 4. Page 2 — Detail Charts

The Production and Mill panels respond to the **global** time range controls (top bar). Four panels:

> **[Screenshot — Detail page]**

**Production** — Dual-axis chart: rate (t/h) on the left, cumulative totaliser (t) on the right. The **YTD Output** box shows the selected year's production; use the **year dropdown** next to it to view past years (only years with production data are listed; each past year shows its full Jan–Dec total).

**Mill Health** — Load Amps, Feeder Speed, Left/Right Roller Temperature, Energy for Mills 1/2/3. *(Currently shows March–May 2024 historical data.)*

**Pellet Silo** — Level trend (%) and Infeed Totalisers.

**Dispatch** — Cumulative bagging and truck loading totalisers over time.

> **Independent range for Silo & Dispatch:** The Pellet Silo and Dispatch panels have their **own** range selector ("Silo & Dispatch Range", default **6 months**, options 24h / 7d / 1M / 6M / 1Y). This lets you watch a longer trend for silos and dispatch while keeping the Mill panels on a short window (e.g. 24h). It does not affect the Production or Mill panels.

---

## 5. Page 3 — AI (Future)

Placeholder for future AI/ML features. Displays illustrative data only — no real plant data. Reserved for a future deployment phase.

---

## 6. Time Range & Controls

> **[Screenshot — control bar]**

### Quick Range Buttons

```
  [ 1m ]  [ 30m ]  [ 6h ]  [ 24h ]  [ 7d ]  [ 1M ]  [ 6M ]
```

Selects a window relative to the current time. Longer ranges are automatically downsampled to keep charts fast (e.g. 7d = 1 point per 5 min; 6M = 1 point per 2 h).

> These global controls drive the **Production** and **Mill** panels. The **Pellet Silo** and **Dispatch** panels on the Detail page have their own separate range selector — see [Section 4](#4-page-2--detail-charts).

### Custom Date Range

Use the **date picker** to select specific start and end dates. For example, to view Mill historical data, set the range to **2024-03-01 → 2024-05-31**.

> **[Screenshot — date picker example]**

### Auto-Refresh

| Setting | Behaviour |
|---|---|
| Off | Manual only |
| 5 s | Refresh every 5 seconds |
| 30 s | Refresh every 30 seconds |
| 1 min | Refresh every minute |

### Other

- **Theme:** ☀️ / 🌙 toggles light / dark mode (saved in browser)
- **Language:** EN / 中文 / FR switcher in the top bar

---

## 7. Threshold Settings

Click **⚙️ Settings** in the top bar. Thresholds control the colour of KPI cards and gauges.

> **[Screenshot — Settings panel]**

### Mode A — Target Range

Used for: **Mill Load Amps**, **Pellet Silo 1**, **Pellet Silo 2/3**

Value should stay in a middle range. Too high or too low triggers a warning.

```
  🔴 Red    🟡 Yellow    🟢 Green    🟡 Yellow    🔴 Red
◄─────────┤───────────┤────────────┤───────────┤─────────►
       Red Low     Green Min     Green Max     Red High
```

| Parameter | 🔴 Red Low | 🟢 Green Min | 🟢 Green Max | 🔴 Red High |
|---|---|---|---|---|
| Mill Load Amps | 50 A | 400 A | 460 A | 480 A |
| Pellet Silo 1 | 15% | 25% | 85% | 95% |
| Pellet Silo 2/3 | 10% | 20% | 80% | 90% |

### Mode B — Higher is Better

Used for: **Belt Weigher (Production Rate)**, **Feeder %**

Above the threshold is good; below is a warning.

```
  🔴 Red            🟡 Yellow              🟢 Green
◄────────────────┤───────────────────┤──────────────────►
              Red Below            Green Above
```

| Parameter | 🔴 Red Below | 🟢 Green Above |
|---|---|---|
| Belt Weigher | 10.0 t/h | 14.0 t/h |
| Feeder % | 40% | 55% |

### How to Adjust

1. Click **⚙️** → Settings panel opens
2. Edit the boundary values
3. Click **Save & Apply** — takes effect immediately
4. **Reset to Default** / **Reset All** to revert
5. Settings persist across restarts

> **Note:** All threshold values shown above are **examples only** and do not represent actual operational targets. The thresholds can be freely adjusted at any time through the Settings panel. Land Energy's engineers will have the best knowledge of what the correct boundaries should be for each parameter.

---

## 8. System Maintenance

### Starting the System

Open **two terminals** on the VM:

**Terminal 1 — Data Ingest** (keep running):
```
cd D:\LE\src
python ingest.py --source "D:\CSVData\BaumgartnerData"
```

**Terminal 2 — Dashboard** (keep running):
```
cd D:\LE\src
python app.py
```

Open browser: **http://localhost:8050**

### If the System Crashes

Close the terminal(s) and rerun the two commands above. No data is lost.

### Verifying Data Flow

When new data arrives, the terminal prints:
```
[ingest] 10:45:21  +27 buckets
```
If no messages appear for several minutes, check that the BG CSV files are being updated by the SCADA system.

---

*End of User Guide*

*For any questions — including threshold settings, data interpretation, or any other issues encountered while using the dashboard — please feel free to contact the developer:*

**Yingbo Zhu**
- University email: yingbo.zhu@uws.ac.uk
- Personal email: pagea75@gmail.com
