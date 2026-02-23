# src/charts.py
"""
Plotly figure builders for every dashboard panel.
All figures use the SCADA dark theme.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from config import get_thresholds

# ─── Dark SCADA colours ───────────────────────────────────────────────────────
BG      = "#1a1a2e"
CARD_BG = "#16213e"
GRID    = "#2a2a4a"
TEXT    = "#e0e0e0"
SUBTEXT = "#9e9e9e"
GREEN   = "#0f9b58"
YELLOW  = "#f4b400"
RED     = "#db4437"

# Distinct colours for the 3 mills
MILL_CLR = ["#4dd0e1", "#f06292", "#aed581"]   # cyan / pink / lime

# ─── Shared layout base ───────────────────────────────────────────────────────
_BASE = dict(
    paper_bgcolor=CARD_BG,
    plot_bgcolor=BG,
    font=dict(color=TEXT, family="Roboto Mono, Courier New, monospace", size=11),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID, font=dict(size=10)),
    hovermode="x unified",
    margin=dict(l=52, r=22, t=38, b=48),
    xaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(size=10), zeroline=False),
    yaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(size=10), zeroline=False),
)


def _fig(**extra) -> go.Figure:
    layout = {**_BASE, **extra}
    return go.Figure(layout=go.Layout(**layout))


def _empty(msg="No data in selected range") -> go.Figure:
    fig = _fig()
    fig.add_annotation(
        text=msg, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=SUBTEXT, size=13),
    )
    return fig


def _latest(df: pd.DataFrame, col: str):
    """Latest non-null value of a column, or None."""
    if df.empty or col not in df.columns:
        return None
    vals = df[col].dropna()
    return float(vals.iloc[-1]) if len(vals) > 0 else None


def _cfg():
    """Common dcc.Graph config (hides toolbar, enables responsiveness)."""
    return {"displayModeBar": False, "responsive": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 1 — Production & Throughput
# ═══════════════════════════════════════════════════════════════════════════════

def fig_production_lines(df: pd.DataFrame) -> go.Figure:
    """
    Dual line: Belt Weigher [Col 51] and Dryer Out Feed [Col 8].
    20 t/h dashed target line for Belt Weigher.
    """
    if df.empty:
        return _empty()

    dt   = df["Date Time"]
    belt = "Total tons passed belt weigher (hour)"
    dry  = "Dryer out feed t/h"

    fig = _fig(title=dict(text="Production Throughput (t/h)", font=dict(size=13)))

    if belt in df.columns:
        fig.add_trace(go.Scatter(
            x=dt, y=df[belt],
            name="Belt Weigher [Col\u202f51] (t/h)",
            line=dict(color=GREEN, width=1.8), mode="lines", connectgaps=False,
        ))
        fig.add_hline(
            y=20, line_dash="dash", line_color=YELLOW, line_width=1.5,
            annotation_text="Target 20\u202ft/h",
            annotation_position="top right",
            annotation_font=dict(color=YELLOW, size=10),
        )

    if dry in df.columns:
        fig.add_trace(go.Scatter(
            x=dt, y=df[dry],
            name="Dryer Out Feed [Col\u202f8] (t/h)",
            line=dict(color=MILL_CLR[0], width=1.8), mode="lines", connectgaps=False,
        ))

    fig.update_layout(
        yaxis=dict(title="t/h", range=[0, 26]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_pellet_silos(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: latest Pellet Silo 1/2/3 levels (tonnes)."""
    if df.empty:
        return _empty()

    silo_map = [
        ("Pellet Silo Level 1 Readout", "Silo 1", MILL_CLR[0]),
        ("Pellet Silo Level 2 Readout", "Silo 2", MILL_CLR[1]),
        ("Pellet Silo Level 3 Readout", "Silo 3", MILL_CLR[2]),
    ]

    names, vals, colors = [], [], []
    for col, label, color in silo_map:
        v = _latest(df, col)
        names.append(label)
        vals.append(v if v is not None else 0)
        colors.append(color)

    fig = _fig(title=dict(text="Pellet Silo Levels (t)", font=dict(size=13)))
    fig.add_trace(go.Bar(
        y=names, x=vals, orientation="h",
        marker_color=colors,
        text=[f"{v:.0f}\u202ft" for v in vals],
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
    ))
    fig.update_layout(
        xaxis=dict(title="tonnes"),
        margin=dict(l=58, r=80, t=38, b=40),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 2 — Mill Health & Load
# ═══════════════════════════════════════════════════════════════════════════════

def fig_mill_gauges(df: pd.DataFrame) -> go.Figure:
    """3 semi-circular Amps gauges (latest value) for Press 1/2/3."""
    amp_cols = [
        ("Press 1 - Load Amps", "Mill\u202f1"),
        ("Press 2 - Load Amps", "Mill\u202f2"),
        ("Press 3 - Load Amps", "Mill\u202f3"),
    ]
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[n for _, n in amp_cols],
        specs=[[{"type": "indicator"}] * 3],
    )

    th = get_thresholds().get("press_load_amps", {})
    rl = th.get("red_low", 50)
    gn = th.get("green_min", 400)
    gx = th.get("green_max", 460)
    rh = th.get("red_high", 480)

    for i, (col, name) in enumerate(amp_cols, 1):
        v = _latest(df, col) or 0
        bar_clr = (
            GREEN  if gn <= v <= gx else
            YELLOW if (rl <= v < gn or gx < v <= rh) else
            RED
        )
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=v,
            number={"suffix": " A", "font": {"size": 18, "color": TEXT}},
            gauge={
                "axis": {"range": [0, 550], "tickfont": {"size": 9, "color": SUBTEXT}},
                "bar": {"color": bar_clr},
                "bgcolor": GRID,
                "steps": [
                    {"range": [0, rl],       "color": "#3d1a1a"},
                    {"range": [rl, gn],      "color": "#3d3312"},
                    {"range": [gn, gx],      "color": "#0f3d27"},
                    {"range": [gx, rh],      "color": "#3d3312"},
                    {"range": [rh, 550],     "color": "#3d1a1a"},
                ],
            },
        ), row=1, col=i)

    fig.update_layout(
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT, size=11),
        margin=dict(l=10, r=10, t=50, b=10),
        height=190,
    )
    for ann in fig.layout.annotations:
        ann.font.color = SUBTEXT
        ann.font.size  = 11
    return fig


def fig_mill_amps_trend(df: pd.DataFrame) -> go.Figure:
    """Overlaid time-series: Press 1/2/3 Load Amps."""
    if df.empty:
        return _empty()
    fig = _fig(title=dict(text="Mill Load Amps — Trend", font=dict(size=13)))
    for col, name, clr in [
        ("Press 1 - Load Amps", "Mill\u202f1", MILL_CLR[0]),
        ("Press 2 - Load Amps", "Mill\u202f2", MILL_CLR[1]),
        ("Press 3 - Load Amps", "Mill\u202f3", MILL_CLR[2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.add_hline(y=400, line_dash="dot", line_color=GREEN,  line_width=1,
                  annotation_text="400A", annotation_font=dict(size=9, color=GREEN))
    fig.add_hline(y=460, line_dash="dot", line_color=YELLOW, line_width=1,
                  annotation_text="460A", annotation_font=dict(size=9, color=YELLOW))
    fig.update_layout(
        yaxis=dict(title="Amps", range=[0, 550]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_mill_feeder(df: pd.DataFrame) -> go.Figure:
    """Time-series: Press 1/2/3 Feeder %."""
    if df.empty:
        return _empty()
    fig = _fig(title=dict(text="Feeder Speed (%)", font=dict(size=13)))
    for col, name, clr in [
        ("Press 1 - Feeder %", "Mill\u202f1", MILL_CLR[0]),
        ("Press 2 - Feeder %", "Mill\u202f2", MILL_CLR[1]),
        ("Press 3 - Feeder %", "Mill\u202f3", MILL_CLR[2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.add_hline(y=55, line_dash="dot", line_color=GREEN, line_width=1,
                  annotation_text="55%", annotation_font=dict(size=9, color=GREEN))
    fig.update_layout(
        yaxis=dict(title="%", range=[0, 100]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_roller_temp_diff(df: pd.DataFrame) -> go.Figure:
    """Absolute L–R roller temperature difference per mill over time."""
    if df.empty:
        return _empty()
    fig = _fig(title=dict(text="Roller Temp L\u2013R Difference (\u00b0C)", font=dict(size=13)))
    for l_col, r_col, name, clr in [
        ("Press 1 - Left Roller Temperature", "Press 1 - Right Roller Temperature", "Mill\u202f1", MILL_CLR[0]),
        ("Press 2 - Left Roller Temperature", "Press 2 - Right Roller Temperature", "Mill\u202f2", MILL_CLR[1]),
        ("Press 3 - Left Roller Temperature", "Press 3 - Right Roller Temperature", "Mill\u202f3", MILL_CLR[2]),
    ]:
        if l_col in df.columns and r_col in df.columns:
            diff = (df[l_col] - df[r_col]).abs()
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=diff,
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.update_layout(
        yaxis=dict(title="|\u0394T| \u00b0C"),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_mill_kwht(df: pd.DataFrame) -> go.Figure:
    """Time-series: Press 1/2/3 energy consumption (kWh/t)."""
    if df.empty:
        return _empty()
    fig = _fig(title=dict(text="Mill Energy (kWh/t)", font=dict(size=13)))
    for col, name, clr in [
        ("Press 1 kWh/t", "Mill\u202f1", MILL_CLR[0]),
        ("Press 2 kWh/t", "Mill\u202f2", MILL_CLR[1]),
        ("Press 3 kWh/t", "Mill\u202f3", MILL_CLR[2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.update_layout(
        yaxis=dict(title="kWh/t"),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 3 — Dryer & Feed
# ═══════════════════════════════════════════════════════════════════════════════

def fig_dry_silos(df: pd.DataFrame) -> go.Figure:
    """
    'Tank level' bar chart for Dry Silo 1 (Col 9) and Silo 2 (Col 10).
    Background bar = 100 %; fill bar = current %.
    """
    if df.empty:
        return _empty()

    s1 = _latest(df, "Dry Silo 1 Level %") or 0
    s2 = _latest(df, "Dry Silo 2 Level %") or 0

    def bar_color(v):
        if v < 20 or v > 90: return RED
        if v < 30 or v > 80: return YELLOW
        return GREEN

    fig = go.Figure()
    for label, val in [("Dry Silo\u202f1", s1), ("Dry Silo\u202f2", s2)]:
        clr = bar_color(val)
        # empty tank background
        fig.add_trace(go.Bar(
            x=[label], y=[100], marker_color=GRID, showlegend=False,
            hoverinfo="skip", width=0.55,
        ))
        # fill level
        fig.add_trace(go.Bar(
            x=[label], y=[val], marker_color=clr, showlegend=False,
            width=0.55, name=label,
            text=f"<b>{val:.0f}%</b>",
            textposition="outside",
            textfont=dict(color=clr, size=18),
            hovertemplate=f"{label}: {val:.1f}%<extra></extra>",
        ))

    fig.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=BG,
        barmode="overlay",
        font=dict(color=TEXT, size=11),
        yaxis=dict(range=[0, 115], ticksuffix="%", gridcolor=GRID,
                   title="Level (%)", tickfont=dict(size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        margin=dict(l=50, r=20, t=30, b=20),
        height=230,
        showlegend=False,
    )
    return fig


def fig_dryer_moisture(df: pd.DataFrame) -> go.Figure:
    """Dual line: Dryer Outlet Moisture Displayed (Col 5) vs Actual (Col 6)."""
    if df.empty:
        return _empty()

    col_d = "Moisture %  Displayed Value at Dryer Outlet"
    col_a = "Moisture %  Actual Value at Dryer Outlet"

    fig = _fig(title=dict(text="Dryer Outlet Moisture (%)", font=dict(size=13)))
    if col_d in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date Time"], y=df[col_d],
            name="Displayed [Col\u202f5]",
            line=dict(color=YELLOW, width=1.6, dash="dot"), mode="lines",
        ))
    if col_a in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date Time"], y=df[col_a],
            name="Actual [Col\u202f6]",
            line=dict(color=GREEN, width=1.6), mode="lines",
        ))
    fig.add_hline(y=7,  line_dash="dash", line_color=GREEN,  line_width=1,
                  annotation_text="7%",  annotation_font=dict(size=9, color=GREEN))
    fig.add_hline(y=10, line_dash="dash", line_color=YELLOW, line_width=1,
                  annotation_text="10%", annotation_font=dict(size=9, color=YELLOW))
    fig.update_layout(
        yaxis=dict(title="%"),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 4 — Quality Control
# ═══════════════════════════════════════════════════════════════════════════════

def fig_quality_trends(df: pd.DataFrame) -> go.Figure:
    """
    2×2 subplot grid: Durability / Pellet Moisture / Bulk Density / Avg Length.
    Reference lines from thresholds.
    """
    if df.empty:
        return _empty()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Durability (%)",
            "Pellet Moisture (%)",
            "Bulk Density (g/l)",
            "Avg Pellet Length (mm)",
        ],
        vertical_spacing=0.18,
        horizontal_spacing=0.12,
    )

    dt = df["Date Time"]

    def add(col, row, col_i, clr, g_ref=None, r_ref=None):
        if col not in df.columns:
            return
        fig.add_trace(
            go.Scatter(x=dt, y=df[col], mode="lines+markers",
                       line=dict(color=clr, width=1.2),
                       marker=dict(size=4, color=clr),
                       showlegend=False),
            row=row, col=col_i,
        )
        if g_ref is not None:
            fig.add_hline(y=g_ref, line_dash="dot", line_color=GREEN, line_width=1,
                          row=row, col=col_i)
        if r_ref is not None:
            fig.add_hline(y=r_ref, line_dash="dot", line_color=RED,   line_width=1,
                          row=row, col=col_i)

    add("Durability %",              1, 1, GREEN,       g_ref=97.5, r_ref=97.0)
    add("Pellet Moisture %",         1, 2, YELLOW,      g_ref=10.0, r_ref=11.0)
    add("Bulk  Density g/l",         2, 1, MILL_CLR[0], g_ref=630,  r_ref=600)
    add("Average Pellet Length(mm)", 2, 2, MILL_CLR[1], g_ref=40,   r_ref=45)

    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT, size=11),
        margin=dict(l=52, r=22, t=55, b=40),
        height=380,
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(size=9))
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(size=9))
    for ann in fig.layout.annotations:
        ann.font.color = SUBTEXT
        ann.font.size  = 11
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 5 — CHP & Energy
# ═══════════════════════════════════════════════════════════════════════════════

def fig_turbine_gauge(df: pd.DataFrame) -> go.Figure:
    """Semi-circular gauge: Turbine Generated Power kW (Col 60)."""
    th = get_thresholds().get("turbine_power", {})
    rb = th.get("red_below", 500)
    ga = th.get("green_above", 2000)

    val = _latest(df, "Turbine Generated Power kW") or 0
    bar_clr = GREEN if val >= ga else (YELLOW if val >= rb else RED)

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=val,
        delta={"reference": ga, "relative": False,
               "font": {"size": 12, "color": SUBTEXT}},
        number={"suffix": "\u202fkW", "font": {"size": 20, "color": TEXT}},
        title={"text": "Turbine Power [Col\u202f60]",
               "font": {"size": 11, "color": SUBTEXT}},
        gauge={
            "axis": {
                "range": [0, 2800],
                "tickfont": {"size": 9, "color": SUBTEXT},
                "tickmode": "array",
                "tickvals": [0, 500, 1000, 1500, 2000, 2500, 2800],
            },
            "bar": {"color": bar_clr},
            "bgcolor": GRID,
            "steps": [
                {"range": [0, rb],     "color": "#3d1a1a"},
                {"range": [rb, ga],    "color": "#3d3312"},
                {"range": [ga, 2800],  "color": "#0f3d27"},
            ],
            "threshold": {
                "line": {"color": GREEN, "width": 2},
                "thickness": 0.75, "value": ga,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT),
        margin=dict(l=20, r=20, t=30, b=10),
        height=200,
    )
    return fig


def fig_chp_trend(df: pd.DataFrame) -> go.Figure:
    """
    Dual-axis line: Furnace Temp [Col 57] (left Y) + Thermal Oil OUT [Col 59] (right Y).
    """
    if df.empty:
        return _empty()

    fig = _fig(title=dict(text="CHP Temperature Trends", font=dict(size=13)))

    if "Furnace Temp" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date Time"], y=df["Furnace Temp"],
            name="Furnace Temp [Col\u202f57] (\u00b0C)",
            line=dict(color=RED, width=1.6), mode="lines", yaxis="y",
        ))
    if "Thermal Oil OUT" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date Time"], y=df["Thermal Oil OUT"],
            name="Thermal Oil OUT [Col\u202f59] (\u00b0C)",
            line=dict(color=YELLOW, width=1.6), mode="lines", yaxis="y2",
        ))

    fig.update_layout(
        yaxis=dict(title="Furnace Temp (\u00b0C)", gridcolor=GRID, linecolor=GRID,
                   tickfont=dict(size=10)),
        yaxis2=dict(
            title="Thermal Oil (\u00b0C)",
            overlaying="y", side="right",
            gridcolor="rgba(0,0,0,0)", linecolor=GRID,
            tickfont=dict(size=10),
        ),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_hru_damper(df: pd.DataFrame) -> go.Figure:
    """Line chart: HRU Bypass Damper position (Col 63)."""
    if df.empty:
        return _empty()
    fig = _fig(
        title=dict(text="HRU Bypass Damper [Col\u202f63]", font=dict(size=13)),
        margin=dict(l=52, r=22, t=38, b=40),
    )
    col = "HRU Bypass Damper"
    if col in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date Time"], y=df[col],
            name="HRU Bypass Damper",
            line=dict(color=MILL_CLR[0], width=1.4), mode="lines",
            showlegend=False,
        ))
    fig.update_layout(yaxis=dict(title="Position"))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 6 — Downtime & Events
# ═══════════════════════════════════════════════════════════════════════════════

def fig_downtime_pareto(events_df: pd.DataFrame) -> go.Figure:
    """
    Pareto: Fault Category sorted by total Duration_min.
    Bar on left Y + cumulative % line on right Y + 80% reference line.
    """
    if events_df.empty or "Fault Category" not in events_df.columns:
        return _empty("No downtime events in selected range")

    grp = (
        events_df.groupby("Fault Category", as_index=False)["Duration_min"]
        .sum()
        .sort_values("Duration_min", ascending=False)
        .reset_index(drop=True)
    )
    if grp.empty:
        return _empty("No downtime data")

    total = grp["Duration_min"].sum()
    grp["cum_pct"] = grp["Duration_min"].cumsum() / total * 100

    cats = list(grp["Fault Category"])

    fig = _fig(title=dict(text="Downtime Pareto \u2014 Fault Category", font=dict(size=13)))

    fig.add_trace(go.Bar(
        x=cats, y=grp["Duration_min"],
        name="Downtime (min)", marker_color=RED, yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=cats, y=grp["cum_pct"],
        name="Cumulative %",
        line=dict(color=YELLOW, width=2), mode="lines+markers",
        marker=dict(size=6), yaxis="y2",
    ))
    # 80 % reference line on y2 axis
    fig.add_trace(go.Scatter(
        x=cats, y=[80] * len(cats),
        mode="lines",
        line=dict(color=GREEN, width=1.5, dash="dash"),
        yaxis="y2", showlegend=False, hoverinfo="skip",
    ))

    fig.update_layout(
        yaxis=dict(title="Downtime (min)", gridcolor=GRID, linecolor=GRID,
                   tickfont=dict(size=10)),
        yaxis2=dict(
            title="Cumulative %", overlaying="y", side="right",
            range=[0, 105], gridcolor="rgba(0,0,0,0)", linecolor=GRID,
            ticksuffix="%", tickfont=dict(size=10),
        ),
        legend=dict(orientation="h", y=-0.25),
        xaxis=dict(tickangle=-30, tickfont=dict(size=10)),
    )
    return fig


def fig_area_downtime(events_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: total downtime (min) per Area."""
    if events_df.empty or "Area" not in events_df.columns:
        return _empty("No downtime events in selected range")

    grp = (
        events_df.groupby("Area", as_index=False)["Duration_min"]
        .sum()
        .sort_values("Duration_min", ascending=True)
    )
    if grp.empty:
        return _empty("No downtime data")

    fig = _fig(title=dict(text="Downtime by Area (min)", font=dict(size=13)))
    fig.add_trace(go.Bar(
        x=grp["Duration_min"], y=grp["Area"],
        orientation="h",
        marker_color=YELLOW,
        text=[f"{v:.0f}" for v in grp["Duration_min"]],
        textposition="outside",
        textfont=dict(color=TEXT, size=10),
    ))
    fig.update_layout(
        xaxis=dict(title="minutes"),
        margin=dict(l=140, r=60, t=38, b=40),
    )
    return fig
