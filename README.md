# Land Energy — Girvan Pellet Plant Dashboard

Real-time SCADA-style monitoring dashboard for the Land Energy wood pellet production facility in Girvan, Scotland. Built with Dash & Plotly, featuring a dark industrial theme, trilingual UI (English / Chinese / French), and configurable alert thresholds.

![Dashboard Screenshot](docs/screenshot-placeholder.png)

## Quick Start

```bash
# 1. Install dependencies
pip install -r src/requirements.txt

# 2. Initialize the database (imports CSV data into SQLite)
python src/init_db.py

# 3. Launch the dashboard
python src/app.py
```

Open **http://localhost:8050** in your browser.

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Overview | `/` | 12 large-font KPI cards + Quality 2x3 grid — at-a-glance plant status |
| Detail | `/ops` | KPI strip + 6 operational panels (Production, Mill, Dryer, Quality, CHP, Downtime) + full data table |
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
│   ├── init_db.py         # CSV → SQLite ETL pipeline
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

- **Dark SCADA Theme** — Grafana-inspired dark UI, key numbers readable from 2 metres
- **Trilingual** — English, Chinese, French; switch via top bar
- **Configurable Thresholds** — 16 parameters across 6 groups, persisted to JSON
- **Real-time Colour Coding** — Green/Yellow/Red indicators on KPIs and charts
- **6 Operational Panels** — Production & Throughput, Mill Health, Dryer & Feed, Quality Control, CHP & Energy, Downtime & Events
- **Full Data Table** — 52-column scrollable table with sorting

## License

Proprietary — Land Energy Ltd.
