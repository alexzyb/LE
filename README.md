# Land Energy — Girvan Pellet Plant Dashboard

Real-time SCADA-style monitoring dashboard for the Land Energy wood pellet production facility in Girvan, Scotland. Built with Dash & Plotly, featuring a dark industrial theme, trilingual UI (English / Chinese / French), and configurable alert thresholds.

![Dashboard Screenshot](docs/screenshot-placeholder.png)

## Quick Start

```bash
# 1. Install dependencies
pip install -r src/requirements.txt

# 2. Import BG CSV data into SQLite
python src/ingest.py --once --source BaumgartnerData/

# 3. Launch the dashboard
python src/app.py
```

Open **http://localhost:8050** in your browser.

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Overview | `/` | 14 large-font KPI cards + Pellet Silo tank visuals — at-a-glance plant status |
| Detail | `/ops` | 4 operational panels (Production, Mill Health, Pellet Silo, Dispatch) + 11 charts _(P2 KPI strip is LEGACY — removed in Phase 8)_ |
| AI Analytics | `/ai` | Placeholder panels for future ML features (Production Forecast, Fault Prediction, Anomaly Detection, Root Cause Analysis) |

## Project Structure

```
LE/
├── docs/                  # Specifications & design documents
│   ├── layout-spec.md     # Wireframes & acceptance criteria
│   ├── thresholds.md      # Threshold definitions & sources
│   ├── column-map.md      # CSV column mapping (64 → 52 columns)
│   ├── i18n-spec.md       # Internationalisation spec
│   └── scope-and-design.md
├── src/
│   ├── app.py             # Main Dash application (layout + callbacks)
│   ├── charts.py          # 15+ Plotly chart builder functions
│   ├── config.py          # Thresholds, colour scheme, column map
│   ├── data.py            # SQLite query helpers
│   ├── ingest.py          # BG CSV → SQLite incremental ingestion
│   ├── column_map.py      # BG value_id → Dashboard column mapping
│   ├── init_db.py         # Legacy CSV importer (deprecated)
│   ├── translations.py    # EN/ZH/FR UI string dictionaries
│   ├── requirements.txt   # Python dependencies
│   ├── land_energy.db     # SQLite database (generated)
│   ├── thresholds.json    # User-customised thresholds (generated)
│   └── assets/
│       ├── style.css      # SCADA dark theme stylesheet
│       └── logo.png       # Land Energy logo
├── CLAUDE.md              # AI assistant project context
├── Plan.md                # Development plan & progress tracker
└── README.md              # This file
```

## Tech Stack

- **Dash 2.14+** — Python web framework for analytical dashboards
- **Plotly 5.18+** — Interactive charts (line, bar, gauge, Sankey, tank level)
- **Dash Bootstrap Components** — Darkly theme, modals, accordions, grid layout
- **Pandas** — Data manipulation and aggregation
- **SQLite** — Lightweight embedded database

## Features

- **Light/Dark Theme Toggle** — Switch between dark SCADA and light theme via top bar button; preference saved to localStorage
- **Dark SCADA Theme** — Grafana-inspired dark UI, key numbers readable from 2 metres
- **Trilingual** — English, Chinese, French; switch via top bar
- **Configurable Thresholds** — 4 active parameters (Press Amps, Belt Weigher, Feeder %, Pellet Silo Level), persisted to JSON
- **Real-time Colour Coding** — Green/Yellow/Red indicators on KPIs and charts
- **4 Operational Panels** — Production & Throughput, Mill Health & Load, Pellet Silo, Dispatch
- **Grafana-Style Time Control** — Quick range buttons (1m / 30m / 6h / 24h / 7d / 1M / 6M) + auto-refresh (Off / 5s / 30s / 1min) with pulsing indicator
- **Pellet Silo Tank Level** — CSS liquid-fill visual for silo percentage on Overview page
- **BG Live Data Pipeline** — Incremental CSV ingestion with 30s resampling and UPSERT

## License

Proprietary — Land Energy Ltd.
