# src/app.py
"""
Land Energy — Girvan Pellet Plant Dashboard
Run:  python src/app.py   →   http://localhost:8050
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from config import (COLOR_SCHEME, DEFAULT_THRESHOLDS, THRESHOLD_GROUPS,
                    get_thresholds, save_thresholds, reset_thresholds)
from translations import t, DEFAULT_LANG
import data as _data
import charts as _charts

# ─── Paths ────────────────────────────────────────────────────────────────────
DB_PATH         = SRC_DIR / "land_energy.db"
THRESHOLDS_JSON = SRC_DIR / "thresholds.json"
CS = COLOR_SCHEME

# ─── App ──────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
    ],
    suppress_callback_exceptions=True,
    title="Land Energy | Girvan Pellet Plant",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _query(sql, params=None):
    if not DB_PATH.exists():
        return pd.DataFrame()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(sql, conn, params=params)
    except Exception:
        return pd.DataFrame()


def _latest_val(df, col):
    if df.empty or col not in df.columns:
        return None
    vals = df[col].dropna()
    return float(vals.iloc[-1]) if len(vals) > 0 else None


def threshold_color(key, value):
    if value is None:
        return "grey"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "grey"
    if pd.isna(v):
        return "grey"
    p = get_thresholds().get(key, {})
    mode = p.get("mode", "")
    if mode == "dual":
        if v < p["red_low"] or v > p["red_high"]:   return "red"
        if v < p["green_min"] or v > p["green_max"]: return "yellow"
        return "green"
    if mode == "lower":
        if v < p["red_below"]:   return "red"
        if v < p["green_above"]: return "yellow"
        return "green"
    if mode == "upper":
        if v > p["red_above"]:   return "red"
        if v > p["green_below"]: return "yellow"
        return "green"
    return "grey"


_HEX = {"green": CS["green"], "yellow": CS["yellow"],
        "red": CS["red"], "grey": CS["subtext"]}

def color_style(c):
    return {"color": _HEX.get(c, CS["subtext"])}

# ─── UI primitives ────────────────────────────────────────────────────────────

def kpi_card(label, value, unit="", color="grey", note=""):
    return dbc.Card(
        dbc.CardBody([
            html.P(label, className="kpi-label"),
            html.Div([
                html.Span(value, className="kpi-value", style=color_style(color)),
                html.Span(f"\u00a0{unit}", className="kpi-unit") if unit else None,
            ]),
            html.P(note, className="kpi-subtitle") if note else None,
        ]),
        className="kpi-card",
    )


def section_panel(title, body, section_id):
    return html.Div(
        id=section_id,
        children=html.Div([
            html.Div(html.H5(title, className="panel-title"), className="panel-header"),
            html.Div(body, className="panel-body"),
        ], className="dashboard-panel"),
    )


def G(fig, height=None):
    """Shorthand for dcc.Graph with dark config."""
    style = {"height": f"{height}px"} if height else {}
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False, "responsive": True},
        style=style,
    )

# ─── KPI row ──────────────────────────────────────────────────────────────────

def _get_latest_row():
    df = _query(
        'SELECT * FROM shift_protocol'
        ' WHERE "Date Time" IS NOT NULL ORDER BY "Date Time" DESC LIMIT 1'
    )
    return df.iloc[0].to_dict() if not df.empty else None


def _daily_output(date_prefix):
    df = _query(
        'SELECT "Total Pellets passed belt weigher (cumlative)" AS c'
        ' FROM shift_protocol WHERE "Date Time" LIKE ? ORDER BY "Date Time"',
        params=[f"{date_prefix}%"],
    )
    if df.empty:
        return None
    vals = df["c"].dropna()
    return round(float(vals.iloc[-1]) - float(vals.iloc[0]), 1) if len(vals) >= 2 else None


def _event_count(date_str):
    df = _query("SELECT COUNT(*) AS n FROM events_log WHERE Date = ?",
                params=[date_str])
    return int(df.iloc[0]["n"]) if not df.empty else 0


def build_kpi_row(lang):
    row = _get_latest_row()
    latest_date = str(row.get("Date Time", ""))[:10] if row else ""

    daily = _daily_output(latest_date) if latest_date else None
    daily_str = f"{daily:.0f}" if daily is not None else "\u2014"

    rate_val = row.get("Total tons passed belt weigher (hour)") if row else None
    try:
        rate_f   = float(rate_val)
        rate_str = f"{rate_f:.1f}"
    except (TypeError, ValueError):
        rate_f   = None
        rate_str = "\u2014"
    rate_color = threshold_color("belt_weigher_hourly", rate_f)

    mills_ok = 0
    if row:
        for c in ["Press 1 - Load Amps", "Press 2 - Load Amps", "Press 3 - Load Amps"]:
            try:
                if float(row.get(c, 0) or 0) > 50:
                    mills_ok += 1
            except (TypeError, ValueError):
                pass
    mills_str   = f"{mills_ok}/3"
    mills_note  = (t("state_running", lang) if mills_ok == 3 else
                   t("state_stopped", lang) if mills_ok == 0 else
                   f"{mills_ok} {t('state_running', lang)}")
    mills_color = "green" if mills_ok == 3 else ("yellow" if mills_ok > 0 else "red")

    dryer_val = row.get("Dryer out feed t/h") if row else None
    try:
        dryer_f   = float(dryer_val)
        dryer_str = f"{dryer_f:.1f}"
    except (TypeError, ValueError):
        dryer_f   = None
        dryer_str = "\u2014"
    dryer_color = threshold_color("dryer_out_feed", dryer_f)

    ev_n     = _event_count(latest_date) if latest_date else 0
    ev_str   = str(ev_n)
    ev_color = "red" if ev_n > 10 else ("yellow" if ev_n >= 5 else "green")

    return dbc.Row([
        dbc.Col(kpi_card("OEE", "\u2014", "%", "grey", t("state_insufficient", lang)), md=2, xs=6),
        dbc.Col(kpi_card(t("kpi_daily_output", lang), daily_str,  "t",   "grey"),        md=2, xs=6),
        dbc.Col(kpi_card(t("kpi_rate",         lang), rate_str,   "t/h", rate_color),    md=2, xs=6),
        dbc.Col(kpi_card(t("kpi_mills",        lang), mills_str,  "",    mills_color, mills_note), md=2, xs=6),
        dbc.Col(kpi_card(t("kpi_dryer_feed",   lang), dryer_str,  "t/h", dryer_color),   md=2, xs=6),
        dbc.Col(kpi_card(t("kpi_events",       lang), ev_str,     "",    ev_color),       md=2, xs=6),
    ], className="kpi-row g-2 mb-3")

# ─── Panel component builders ─────────────────────────────────────────────────

def _mill_status(df, lang):
    """3 coloured status lights (HTML, not Plotly)."""
    items = []
    for i, col in enumerate(
        ["Press 1 - Load Amps", "Press 2 - Load Amps", "Press 3 - Load Amps"], 1
    ):
        val = _latest_val(df, col)
        running = val is not None and val > 50
        clr     = CS["green"] if running else CS["subtext"]
        status  = t("state_running", lang) if running else t("state_stopped", lang)
        amp_str = f"{val:.0f}\u202fA" if val is not None else "\u2014"
        items.append(html.Div([
            html.Span("\u25cf", style={"color": clr, "fontSize": "18px"}),
            html.Span(
                f"\u2002Mill\u202f{i}\u2002{status}\u2002|\u2002{amp_str}",
                style={"color": clr, "fontFamily": "Roboto Mono, monospace",
                       "fontSize": "15px", "marginLeft": "4px"},
            ),
        ], style={"marginBottom": "6px"}))
    return html.Div(items, style={"marginBottom": "10px"})


def _quality_cards(df, lang):
    """4 quality metric tiles with threshold border colours."""
    _thresh = get_thresholds()
    def qclr(key, val):
        if val is None:
            return CS["subtext"]
        p = _thresh.get(key, {})
        m = p.get("mode", "")
        v = float(val)
        if m == "lower":
            return CS["green"]  if v >= p["green_above"] else \
                   CS["yellow"] if v >= p["red_below"]   else CS["red"]
        if m == "upper":
            return CS["green"]  if v <= p["green_below"] else \
                   CS["yellow"] if v <= p["red_above"]   else CS["red"]
        return CS["subtext"]

    def tile(label, val, unit, key):
        clr     = qclr(key, val)
        val_str = f"{val:.1f}" if val is not None else "\u2014"
        return dbc.Col(
            html.Div([
                html.P(label, style={"fontSize": "12px", "color": CS["subtext"],
                                     "textTransform": "uppercase",
                                     "letterSpacing": "0.8px", "margin": "0 0 4px 0"}),
                html.Span(val_str, style={"fontSize": "36px", "fontWeight": "700",
                                          "fontFamily": "Roboto Mono, monospace",
                                          "color": clr}),
                html.Span(f"\u202f{unit}", style={"fontSize": "16px",
                                                   "color": CS["subtext"]}),
            ], style={
                "textAlign": "center", "padding": "12px 8px",
                "background": CS["bg"], "borderRadius": "4px",
                "border": f"1px solid {clr}",
            }),
            md=3, xs=6,
        )

    dur  = _latest_val(df, "Durability %")
    mois = _latest_val(df, "Pellet Moisture %")
    dens = _latest_val(df, "Bulk  Density g/l")
    leng = _latest_val(df, "Average Pellet Length(mm)")

    return dbc.Row([
        tile("Durability",      dur,  "%",   "durability"),
        tile("Pellet Moisture", mois, "%",   "pellet_moisture_finished"),
        tile("Bulk Density",    dens, "g/l", "bulk_density"),
        tile("Avg Length",      leng, "mm",  "avg_pellet_length"),
    ], className="g-2 mb-3")


def _events_table(events_df):
    """Dash DataTable: 10 most recent events."""
    if events_df.empty:
        return html.P("No events in selected date range.", className="placeholder-text")

    show = (events_df
            .sort_values(["Date", "Time"], ascending=False)
            .head(10))
    keep = ["Date", "Time", "Area", "Fault Category", "Event Description", "Duration_min"]
    show = show[[c for c in keep if c in show.columns]].copy()
    if "Duration_min" in show.columns:
        show["Duration_min"] = show["Duration_min"].apply(
            lambda x: f"{x:.0f} min" if pd.notna(x) else "\u2014"
        )

    return dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in show.columns],
        data=show.to_dict("records"),
        style_table={"overflowX": "auto", "fontSize": "13px"},
        style_header={"backgroundColor": "#0f3460", "color": CS["text"],
                      "fontWeight": "bold", "border": f"1px solid {CS['border']}"},
        style_data={"backgroundColor": CS["card"], "color": CS["text"],
                    "border": f"1px solid {CS['border']}"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": CS["bg"]},
        ],
        style_cell={"padding": "6px 10px", "textAlign": "left",
                    "whiteSpace": "normal", "minWidth": "80px"},
        page_size=10,
    )


def _full_data_table(df):
    """Scrollable DataTable with all shift_protocol columns."""
    if df.empty:
        return html.P("No data in selected range.", className="placeholder-text")

    display = df.copy()
    if "Date Time" in display.columns:
        display["Date Time"] = display["Date Time"].dt.strftime("%Y-%m-%d %H:%M")
    for col in display.select_dtypes(include="number").columns:
        display[col] = display[col].round(2)

    return dash_table.DataTable(
        columns=[{"name": c, "id": c} for c in display.columns],
        data=display.to_dict("records"),
        page_size=20,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto", "fontSize": "13px", "minWidth": "100%"},
        style_header={"backgroundColor": "#0f3460", "color": CS["text"],
                      "fontWeight": "bold", "border": f"1px solid {CS['border']}",
                      "whiteSpace": "nowrap"},
        style_data={"backgroundColor": CS["card"], "color": CS["text"],
                    "border": f"1px solid {CS['border']}"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": CS["bg"]},
        ],
        style_cell={"padding": "4px 8px", "textAlign": "left",
                    "minWidth": "80px", "whiteSpace": "nowrap"},
        fixed_rows={"headers": True},
    )

# ─── Overview page (new P1) ───────────────────────────────────────────────────

def _ov_card(label, value, unit, color="grey"):
    """Large KPI card for the overview page."""
    return dbc.Col(
        html.Div([
            html.P(label, className="overview-card-label"),
            html.Div([
                html.Span(value, className="overview-card-value",
                          style={"color": _HEX.get(color, CS["text"])}),
                html.Span(f"\u202f{unit}", className="overview-card-unit") if unit else None,
            ]),
        ], className="overview-card",
           style={"borderLeft": f"4px solid {_HEX.get(color, CS['border'])}"}),
        md=3, sm=6, xs=6, className="mb-3",
    )


def _ov_tank(label, value_num, value_str, color="grey"):
    """Tank level card for the overview page (Dry Silo)."""
    clr = _HEX.get(color, CS["text"])
    pct = max(0, min(100, value_num or 0))
    return dbc.Col(
        html.Div([
            html.Div(style={
                "backgroundColor": clr,
                "height": f"{pct}%",
            }, className="overview-tank-fill"),
            html.P(label, className="overview-tank-label"),
            html.Div([
                html.Span(value_str, className="overview-tank-value",
                          style={"color": clr}),
                html.Span("\u202f%", className="overview-tank-unit"),
            ]),
        ], className="overview-tank",
           style={"borderLeft": f"4px solid {clr}"}),
        md=3, sm=6, xs=6, className="mb-3",
    )


def _ov_quality_cell(label, value, unit, color="grey"):
    """Single cell in the quality grid."""
    clr = _HEX.get(color, CS["subtext"])
    return html.Div([
        html.P(label, className="quality-grid-label"),
        html.Div([
            html.Span(value, className="quality-grid-value",
                      style={"color": clr}),
            html.Span(f"\u202f{unit}", className="quality-grid-unit"),
        ]),
    ], className="quality-grid-cell",
       style={"border": f"1px solid {clr}"})


def overview_layout(lang, start_date, end_date):
    """P1: High-level KPI cards + Quality grid."""
    df = _data.get_shift_df(start_date, end_date)

    # ── helpers ───────────────────────────────────────────────────────────────
    def _fmt(val, decimals=1):
        if val is None:
            return "\u2014"
        return f"{val:,.{decimals}f}"

    def _latest(col):
        return _latest_val(df, col)

    # ── PRODUCTION ────────────────────────────────────────────────────────────
    # Daily output (cumulative delta for latest day)
    cum_col = "Total Pellets passed belt weigher (cumlative)"
    daily_out = None
    if not df.empty and cum_col in df.columns and "Date Time" in df.columns:
        df_dt = df.copy()
        df_dt["Date Time"] = pd.to_datetime(df_dt["Date Time"], errors="coerce")
        last_day = df_dt["Date Time"].dropna().max()
        if last_day is not None:
            day_df = df_dt[df_dt["Date Time"].dt.date == last_day.date()]
            vals = day_df[cum_col].dropna()
            if len(vals) >= 2:
                daily_out = round(float(vals.iloc[-1]) - float(vals.iloc[0]), 1)

    # Period cumulative
    period_out = None
    if not df.empty and cum_col in df.columns:
        vals = df[cum_col].dropna()
        if len(vals) >= 2:
            period_out = round(float(vals.iloc[-1]) - float(vals.iloc[0]), 0)

    rate = _latest("Total tons passed belt weigher (hour)")
    rate_clr = threshold_color("belt_weigher_hourly", rate)

    mills_ok = 0
    for c in ["Press 1 - Load Amps", "Press 2 - Load Amps", "Press 3 - Load Amps"]:
        v = _latest(c)
        if v is not None and v > 50:
            mills_ok += 1
    mills_clr = "green" if mills_ok == 3 else ("yellow" if mills_ok > 0 else "red")

    prod_section = html.Div([
        html.H6(t("cat_production", lang), className="overview-section-title"),
        dbc.Row([
            _ov_card(t("ov_daily_output", lang), _fmt(daily_out, 0), "t"),
            _ov_card(t("ov_rate", lang),         _fmt(rate),         "t/h", rate_clr),
            _ov_card(t("ov_mills", lang),         f"{mills_ok}/3",   "",    mills_clr),
            _ov_card(t("ov_cumulative", lang),   _fmt(period_out, 0), "t"),
        ]),
    ], className="mb-2")

    # ── ENERGY ────────────────────────────────────────────────────────────────
    turbine  = _latest("Turbine Generated Power kW")
    turb_clr = threshold_color("turbine_power", turbine)
    furnace  = _latest("Furnace Temp")
    furn_clr = threshold_color("furnace_temp", furnace)
    thermal  = _latest("Thermal Oil OUT")
    therm_clr = threshold_color("thermal_oil_out", thermal)
    hru      = _latest("HRU Bypass Damper")

    energy_section = html.Div([
        html.H6(t("cat_energy", lang), className="overview-section-title"),
        dbc.Row([
            _ov_card(t("ov_turbine", lang),      _fmt(turbine, 0), "kW",  turb_clr),
            _ov_card(t("ov_furnace_temp", lang), _fmt(furnace, 0), "\u00b0C", furn_clr),
            _ov_card(t("ov_thermal_oil", lang),  _fmt(thermal, 0), "\u00b0C", therm_clr),
            _ov_card(t("ov_hru_bypass", lang),   _fmt(hru, 0),     "%"),
        ]),
    ], className="mb-2")

    # ── DRYER ─────────────────────────────────────────────────────────────────
    dryer_feed = _latest("Dryer out feed t/h")
    dryer_clr  = threshold_color("dryer_out_feed", dryer_feed)
    moisture   = _latest("Moisture %  Actual Value at Dryer Outlet")
    moist_clr  = threshold_color("dryer_outlet_moisture", moisture)
    silo1      = _latest("Dry Silo 1 Level %")
    silo1_clr  = threshold_color("dry_silo_level", silo1)
    silo2      = _latest("Dry Silo 2 Level %")
    silo2_clr  = threshold_color("dry_silo_level", silo2)

    dryer_section = html.Div([
        html.H6(t("cat_dryer", lang), className="overview-section-title"),
        dbc.Row([
            _ov_card(t("ov_dryer_feed", lang),      _fmt(dryer_feed), "t/h", dryer_clr),
            _ov_card(t("ov_outlet_moisture", lang), _fmt(moisture),   "%",   moist_clr),
            _ov_tank(t("ov_dry_silo_1", lang), silo1, _fmt(silo1, 0), silo1_clr),
            _ov_tank(t("ov_dry_silo_2", lang), silo2, _fmt(silo2, 0), silo2_clr),
        ]),
    ], className="mb-2")

    # ── QUALITY (2×3 grid) ────────────────────────────────────────────────────
    dur  = _latest("Durability %")
    dens = _latest("Bulk  Density g/l")
    pmoi = _latest("Pellet Moisture %")
    ptmp = _latest("Temp of Pellets at cooler")
    plen = _latest("Average Pellet Length(mm)")

    dur_clr  = threshold_color("durability", dur)
    dens_clr = threshold_color("bulk_density", dens)
    pmoi_clr = threshold_color("pellet_moisture_finished", pmoi)
    plen_clr = threshold_color("avg_pellet_length", plen)

    quality_section = html.Div([
        html.H6(t("cat_quality", lang), className="overview-section-title"),
        html.Div([
            _ov_quality_cell(t("ov_durability", lang),       _fmt(dur),  "%",   dur_clr),
            _ov_quality_cell(t("ov_density", lang),          _fmt(dens, 0), "g/l", dens_clr),
            _ov_quality_cell(t("ov_pellet_moisture", lang),  _fmt(pmoi), "%",   pmoi_clr),
            _ov_quality_cell(t("ov_pellet_temp", lang),      _fmt(ptmp, 0), "\u00b0C"),
            _ov_quality_cell(t("ov_pellet_length", lang),    _fmt(plen, 0), "mm",  plen_clr),
        ], className="quality-grid"),
    ], className="mb-2")

    return html.Div([
        prod_section,
        energy_section,
        dryer_section,
        quality_section,
    ])


# ─── Detailed ops page (P2) ──────────────────────────────────────────────────

def page1_layout(lang, start_date, end_date):
    df        = _data.get_shift_df(start_date, end_date)
    events_df = _data.get_events_df(start_date, end_date)

    # Period cumulative output (Col 45 diff)
    cum_col = "Total Pellets passed belt weigher (cumlative)"
    period_out = None
    if not df.empty and cum_col in df.columns:
        vals = df[cum_col].dropna()
        if len(vals) >= 2:
            period_out = round(float(vals.iloc[-1]) - float(vals.iloc[0]), 1)
    period_str = f"{period_out:.0f}" if period_out is not None else "\u2014"

    panel_items = [
        (t("panel_production", lang), "sec-production"),
        (t("panel_mill",       lang), "sec-mill"),
        (t("panel_dryer",      lang), "sec-dryer"),
        (t("panel_quality",    lang), "sec-quality"),
        (t("panel_chp",        lang), "sec-chp"),
        (t("panel_downtime",   lang), "sec-downtime"),
    ]
    panel_nav = html.Div(
        [html.A(title, href=f"#{pid}", className="panel-nav-btn")
         for title, pid in panel_items],
        className="panel-nav",
    )

    # ── Panel 1: Production ───────────────────────────────────────────────────
    prod_panel = section_panel(t("panel_production", lang), [
        dbc.Row([
            dbc.Col([
                G(_charts.fig_production_lines(df), height=260),
            ], md=8),
            dbc.Col([
                # Big number: period cumulative output
                html.Div([
                    html.P("Period Output [Col\u202f45\u202f\u0394]",
                           style={"fontSize": "12px", "color": CS["subtext"],
                                  "textTransform": "uppercase", "letterSpacing": "0.8px",
                                  "margin": "0 0 4px 0"}),
                    html.Div([
                        html.Span(period_str,
                                  style={"fontSize": "48px", "fontWeight": "700",
                                         "fontFamily": "Roboto Mono, monospace",
                                         "color": CS["text"]}),
                        html.Span("\u202ft", style={"fontSize": "18px",
                                                    "color": CS["subtext"]}),
                    ]),
                ], style={"textAlign": "center", "padding": "16px 8px",
                          "background": CS["bg"], "borderRadius": "4px",
                          "marginBottom": "8px", "border": f"1px solid {CS['border']}"}),
                G(_charts.fig_pellet_silos(df), height=180),
            ], md=4),
        ], className="g-2"),
    ], "sec-production")

    # ── Panel 2: Mill Health ──────────────────────────────────────────────────
    mill_panel = section_panel(t("panel_mill", lang), [
        _mill_status(df, lang),
        G(_charts.fig_mill_gauges(df), height=190),
        dbc.Row([
            dbc.Col(G(_charts.fig_mill_amps_trend(df), height=220), md=6),
            dbc.Col(G(_charts.fig_mill_feeder(df),     height=220), md=6),
        ], className="g-2 mt-2"),
        dbc.Row([
            dbc.Col(G(_charts.fig_roller_temp_diff(df), height=200), md=6),
            dbc.Col(G(_charts.fig_mill_kwht(df),        height=200), md=6),
        ], className="g-2 mt-2"),
    ], "sec-mill")

    # ── Panel 3: Dryer ────────────────────────────────────────────────────────
    dryer_panel = section_panel(t("panel_dryer", lang), [
        dbc.Row([
            dbc.Col(G(_charts.fig_dry_silos(df),      height=240), md=4),
            dbc.Col(G(_charts.fig_dryer_moisture(df), height=240), md=8),
        ], className="g-2"),
    ], "sec-dryer")

    # ── Panel 4: Quality ──────────────────────────────────────────────────────
    quality_panel = section_panel(t("panel_quality", lang), [
        _quality_cards(df, lang),
        G(_charts.fig_quality_trends(df), height=380),
    ], "sec-quality")

    # ── Panel 5: CHP ─────────────────────────────────────────────────────────
    chp_panel = section_panel(t("panel_chp", lang), [
        dbc.Row([
            dbc.Col(G(_charts.fig_turbine_gauge(df), height=200), md=4),
            dbc.Col(G(_charts.fig_chp_trend(df),     height=200), md=8),
        ], className="g-2"),
        G(_charts.fig_hru_damper(df), height=160),
    ], "sec-chp")

    # ── Panel 6: Downtime ─────────────────────────────────────────────────────
    downtime_panel = section_panel(t("panel_downtime", lang), [
        html.Div(_events_table(events_df), style={"marginBottom": "12px"}),
        dbc.Row([
            dbc.Col(G(_charts.fig_downtime_pareto(events_df), height=280), md=6),
            dbc.Col(G(_charts.fig_area_downtime(events_df),   height=280), md=6),
        ], className="g-2"),
    ], "sec-downtime")

    # ── Full data table ───────────────────────────────────────────────────────
    data_table_panel = html.Div(html.Div([
        html.Div(
            html.H5("Full Data Table (all columns)", className="panel-title"),
            className="panel-header",
        ),
        html.Div(_full_data_table(df), className="panel-body"),
    ], className="dashboard-panel"))

    return html.Div([
        panel_nav,
        build_kpi_row(lang),
        prod_panel,
        mill_panel,
        dryer_panel,
        quality_panel,
        chp_panel,
        downtime_panel,
        data_table_panel,
    ])


# ─── Page 3 / AI Placeholder layout ───────────────────────────────────────────

def page2_layout(lang):
    def ai_panel(title, figure):
        return dbc.Col(
            html.Div([
                html.Div(html.H5(title, className="panel-title"),
                         className="panel-header"),
                html.Div([
                    dcc.Graph(figure=figure, config={"displayModeBar": False,
                                                     "responsive": True}),
                    html.Div(
                        html.Div([
                            html.Div("\U0001f512",
                                     style={"fontSize": "32px", "lineHeight": "1"}),
                            html.P(t("p2_overlay", lang), className="overlay-text"),
                        ], className="overlay-inner"),
                        className="coming-soon-overlay",
                    ),
                ], className="panel-body placeholder-panel-body"),
            ], className="dashboard-panel"),
            md=6,
        )

    return html.Div([
        html.H4([
            "AI Predictive Analytics \u2014 ",
            html.Span(t("p2_coming_soon", lang), style={"color": CS["yellow"]}),
        ], className="p2-title mb-3"),
        dbc.Row([
            ai_panel(t("p2_production_fc", lang),
                     _charts.fig_ai_production_forecast()),
            ai_panel(t("p2_fault_pred", lang),
                     _charts.fig_ai_fault_prediction()),
        ], className="g-2 mb-2"),
        dbc.Row([
            ai_panel(t("p2_anomaly",    lang),
                     _charts.fig_ai_anomaly_detection()),
            ai_panel(t("p2_root_cause", lang),
                     _charts.fig_ai_root_cause()),
        ], className="g-2 mb-3"),
        html.Div(["\u26a0\ufe0f\u2002", t("p2_availability", lang)],
                 className="p2-banner"),
    ])


# ─── Static app layout ────────────────────────────────────────────────────────

app.layout = html.Div([

    dcc.Store(id="store-lang", data=DEFAULT_LANG, storage_type="session"),
    dcc.Store(id="store-thresh-ver", data=0),
    dcc.Location(id="url", refresh=False),

    # Top Bar
    html.Div([
        html.Div([
            html.Img(src="/assets/logo.png", className="brand-logo"),
            html.Div([
                html.Span("Land Energy",        className="brand-name"),
                html.Span("Dashboard", className="brand-sub"),
            ]),
        ], className="topbar-left"),

        html.Div([
            html.Span(id="label-date-range", children="Date Range:",
                      className="topbar-label"),
            dcc.DatePickerRange(
                id="date-picker",
                min_date_allowed="2026-01-01",
                max_date_allowed="2026-02-01",
                start_date="2026-01-01",
                end_date="2026-02-01",
                display_format="DD/MM/YYYY",
                className="dash-date-picker mx-1",
            ),
            dbc.Button("Apply", id="btn-apply", n_clicks=0,
                       color="primary", size="sm"),
        ], className="topbar-center"),

        html.Div([
            html.Div([
                dbc.Button("EN", id="btn-lang-en", color="link", size="sm",
                           className="lang-btn", n_clicks=0),
                html.Span("|", className="lang-sep"),
                dbc.Button("\u4e2d", id="btn-lang-zh", color="link", size="sm",
                           className="lang-btn", n_clicks=0),
                html.Span("|", className="lang-sep"),
                dbc.Button("FR", id="btn-lang-fr", color="link", size="sm",
                           className="lang-btn", n_clicks=0),
            ], className="lang-group"),
            dbc.Button("\u2699\ufe0f", id="btn-settings", color="link",
                       title="Threshold Settings",
                       className="settings-btn ms-2", n_clicks=0),
            html.Div([
                dcc.Link(id="nav-overview", children="Overview", href="/",
                         className="page-link-btn"),
                html.Span("\u00b7",
                          style={"color": CS["border"], "padding": "0 2px"}),
                dcc.Link(id="nav-detail", children="Detail", href="/ops",
                         className="page-link-btn"),
                html.Span("\u00b7",
                          style={"color": CS["border"], "padding": "0 2px"}),
                dcc.Link(id="nav-ai", children="AI", href="/ai",
                         className="page-link-btn"),
            ], className="page-switcher ms-2"),
        ], className="topbar-right"),
    ], className="top-bar"),

    # Main content
    dbc.Container(html.Div(id="page-content"), fluid=True,
                  className="main-content"),

    # Settings modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="modal-title",
                                       children="Threshold Settings")),
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter([
            dbc.Button(id="btn-reset-all", color="danger", outline=True,
                       size="sm", children="Reset All", n_clicks=0,
                       className="me-auto"),
            dbc.Button(id="btn-save-thresh", color="success", size="sm",
                       children="Save & Apply", n_clicks=0),
            dbc.Button("Close", id="btn-modal-close", color="secondary",
                       size="sm", n_clicks=0),
        ]),
    ], id="modal-settings", size="xl", is_open=False, scrollable=True),

], style={"backgroundColor": CS["bg"], "minHeight": "100vh",
          "color": CS["text"]})


# ─── Callbacks ────────────────────────────────────────────────────────────────

@app.callback(
    Output("store-lang", "data"),
    [Input("btn-lang-en", "n_clicks"),
     Input("btn-lang-zh", "n_clicks"),
     Input("btn-lang-fr", "n_clicks")],
    prevent_initial_call=True,
)
def update_language(_a, _b, _c):
    btn = callback_context.triggered[0]["prop_id"].split(".")[0]
    return {"btn-lang-en": "en", "btn-lang-zh": "zh",
            "btn-lang-fr": "fr"}.get(btn, DEFAULT_LANG)


@app.callback(
    [Output("label-date-range", "children"),
     Output("btn-apply",        "children"),
     Output("modal-title",      "children"),
     Output("btn-modal-close",  "children"),
     Output("nav-overview",     "children"),
     Output("nav-detail",       "children"),
     Output("nav-ai",           "children"),
     Output("btn-save-thresh",  "children"),
     Output("btn-reset-all",    "children")],
    Input("store-lang", "data"),
)
def update_topbar_labels(lang):
    lang = lang or DEFAULT_LANG
    return (
        t("date_range",     lang) + ":",
        t("btn_apply",      lang),
        t("settings_title", lang),
        "\u00d7\u2002Close",
        t("nav_overview",   lang),
        t("nav_detail",     lang),
        t("nav_ai",         lang),
        t("btn_save_apply", lang),
        t("btn_reset_all",  lang),
    )


@app.callback(
    Output("page-content", "children"),
    [Input("url",              "pathname"),
     Input("store-lang",       "data"),
     Input("btn-apply",        "n_clicks"),
     Input("store-thresh-ver", "data")],
    [State("date-picker", "start_date"),
     State("date-picker", "end_date")],
)
def render_page(pathname, lang, _n, _tv, start_date, end_date):
    lang       = lang       or DEFAULT_LANG
    start_date = start_date or "2026-01-01"
    end_date   = end_date   or "2026-02-01"
    if pathname == "/ops":
        return page1_layout(lang, start_date, end_date)
    if pathname == "/ai":
        return page2_layout(lang)
    return overview_layout(lang, start_date, end_date)


@app.callback(
    Output("modal-settings", "is_open"),
    [Input("btn-settings",    "n_clicks"),
     Input("btn-modal-close", "n_clicks"),
     Input("btn-save-thresh", "n_clicks"),
     Input("btn-reset-all",   "n_clicks")],
    State("modal-settings", "is_open"),
    prevent_initial_call=True,
)
def toggle_settings(_a, _b, _c, _d, is_open):
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]
    if trigger == "btn-settings":
        return not is_open
    return False


# ─── Settings Modal Builder ──────────────────────────────────────────────────

_GROUP_I18N = {
    "Mill": "group_mill", "Dryer": "group_dryer", "Quality": "group_quality",
    "CHP": "group_chp", "Throughput": "group_throughput", "Other": "group_other",
}

_MODE_BOUNDS = {
    "dual":  ["red_low", "green_min", "green_max", "red_high"],
    "lower": ["red_below", "green_above"],
    "upper": ["green_below", "red_above"],
}

_BOUND_LABELS = {
    "red_low": "thresh_red_low", "green_min": "thresh_green_min",
    "green_max": "thresh_green_max", "red_high": "thresh_red_high",
    "red_below": "thresh_red_below", "green_above": "thresh_green_above",
    "green_below": "thresh_green_below", "red_above": "thresh_red_above",
}


def build_settings_body(lang):
    """Build Accordion with 6 groups, each containing threshold input rows."""
    thresh = get_thresholds()
    items = []
    for group, keys in THRESHOLD_GROUPS.items():
        group_label = t(_GROUP_I18N[group], lang)
        rows = []
        for key in keys:
            p = thresh.get(key, {})
            mode = p.get("mode", "dual")
            bounds = _MODE_BOUNDS.get(mode, [])
            inputs = []
            for b in bounds:
                inputs.append(dbc.Col([
                    dbc.Label(t(_BOUND_LABELS[b], lang), className="form-label"),
                    dbc.Input(
                        id={"type": "thresh-input", "key": key, "bound": b},
                        type="number",
                        value=p.get(b, 0),
                        step="any",
                        className="form-control",
                    ),
                ], md=3, sm=6, xs=6))
            rows.append(html.Div([
                html.P(
                    "{} ({})".format(p.get("label", key), p.get("unit", "")),
                    style={"fontSize": "13px", "fontWeight": "600",
                           "color": CS["text"], "margin": "8px 0 4px 0"},
                ),
                dbc.Row(inputs, className="g-2 mb-2"),
            ]))
        items.append(dbc.AccordionItem(html.Div(rows), title=group_label))
    return dbc.Accordion(items, start_collapsed=True)


@app.callback(
    Output("modal-body", "children"),
    [Input("modal-settings", "is_open"),
     Input("store-lang",     "data")],
)
def populate_modal(is_open, lang):
    lang = lang or DEFAULT_LANG
    if not is_open:
        return dash.no_update
    return build_settings_body(lang)


@app.callback(
    Output("store-thresh-ver", "data"),
    [Input("btn-save-thresh", "n_clicks"),
     Input("btn-reset-all",   "n_clicks")],
    [State({"type": "thresh-input", "key": ALL, "bound": ALL}, "value"),
     State({"type": "thresh-input", "key": ALL, "bound": ALL}, "id"),
     State("store-thresh-ver", "data")],
    prevent_initial_call=True,
)
def save_or_reset_thresholds(n_save, n_reset, values, ids, ver):
    trigger = callback_context.triggered[0]["prop_id"].split(".")[0]
    if trigger == "btn-save-thresh" and n_save:
        overrides = {}
        for val, id_dict in zip(values, ids):
            key = id_dict["key"]
            bound = id_dict["bound"]
            if key not in overrides:
                overrides[key] = {}
            try:
                overrides[key][bound] = float(val)
            except (TypeError, ValueError):
                pass
        save_thresholds(overrides)
    elif trigger == "btn-reset-all" and n_reset:
        reset_thresholds()
    return (ver or 0) + 1


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db_ok = "OK" if DB_PATH.exists() else "NOT FOUND \u2014 run init_db.py first"
    print(f"Database : {DB_PATH}  [{db_ok}]")
    import os
    port = int(os.environ.get("PORT", 8050))
    print(f"Starting : http://localhost:{port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)
