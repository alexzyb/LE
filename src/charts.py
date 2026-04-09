# src/charts.py
"""
Plotly figure builders for every dashboard panel.
Supports dark / light themes via config.get_color_scheme().
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from config import get_thresholds, get_color_scheme
from column_map import tons_to_pct, SILO_MAX_CAPACITY


# ─── Theme-aware colour helpers ──────────────────────────────────────────────

def _tc(theme="dark"):
    """Return colour dict for the given theme."""
    cs = get_color_scheme(theme)
    return {
        "bg": cs["bg"], "card": cs["card"], "grid": cs["border"],
        "text": cs["text"], "sub": cs["subtext"],
        "green": cs["green"], "yellow": cs["yellow"], "red": cs["red"],
        "mill": cs.get("mill", ["#4dd0e1", "#f06292", "#aed581"]),
        "g_red": cs.get("gauge_red", "#3d1a1a"),
        "g_yel": cs.get("gauge_yellow", "#3d3312"),
        "g_grn": cs.get("gauge_green", "#0f3d27"),
    }


def _base(theme="dark"):
    c = _tc(theme)
    return dict(
        paper_bgcolor=c["card"],
        plot_bgcolor=c["bg"],
        font=dict(color=c["text"], family="Roboto Mono, Courier New, monospace", size=11),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=c["grid"], font=dict(size=10)),
        hovermode="x unified",
        margin=dict(l=52, r=22, t=38, b=48),
        xaxis=dict(gridcolor=c["grid"], linecolor=c["grid"], tickfont=dict(size=10), zeroline=False),
        yaxis=dict(gridcolor=c["grid"], linecolor=c["grid"], tickfont=dict(size=10), zeroline=False),
    )


def _fig(theme="dark", **extra) -> go.Figure:
    layout = {**_base(theme), **extra}
    return go.Figure(layout=go.Layout(**layout))


def _sparse_series(df, col):
    """Extract non-null rows for a sparse column (e.g. hourly silo data in a 30s table).

    Removes NaN rows so Plotly draws continuous lines between adjacent data points,
    but inserts a single NaN row where the gap between consecutive valid points
    is significantly larger than the typical spacing (3x median interval),
    so real data gaps appear as visible line breaks.

    Returns (x_series, y_series) ready for go.Scatter.
    """
    mask = df[col].notna()
    vdf = df.loc[mask, ["Date Time", col]].copy()
    if len(vdf) < 2:
        return vdf["Date Time"], vdf[col]

    diffs = vdf["Date Time"].diff().dropna()
    median_diff = diffs.median()
    gap_threshold = median_diff * 3

    gaps = vdf["Date Time"].diff() > gap_threshold
    if gaps.any():
        gap_rows = []
        for idx in vdf.index[gaps]:
            loc = vdf.index.get_loc(idx)
            prev_idx = vdf.index[loc - 1]
            mid_time = vdf.loc[prev_idx, "Date Time"] + \
                (vdf.loc[idx, "Date Time"] - vdf.loc[prev_idx, "Date Time"]) / 2
            gap_rows.append({"Date Time": mid_time, col: np.nan})
        if gap_rows:
            vdf = pd.concat([vdf, pd.DataFrame(gap_rows)], ignore_index=True)
            vdf = vdf.sort_values("Date Time").reset_index(drop=True)

    return vdf["Date Time"], vdf[col]


def _empty(theme="dark", msg="No data in selected range") -> go.Figure:
    c = _tc(theme)
    fig = _fig(theme)
    fig.add_annotation(
        text=msg, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=c["sub"], size=13),
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

def fig_production_lines(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Belt Weigher production rate (t/h) + Totaliser (t) dual-axis trend."""
    if df.empty:
        return _empty(theme)

    c = _tc(theme)
    belt = "Total tons passed belt weigher (hour)"
    tot  = "Total Pellets passed belt weigher (cumlative)"
    fig  = _fig(theme, title=dict(text="Production Rate & Totaliser", font=dict(size=13)))

    # Left axis — Production Rate (t/h)
    if belt in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date Time"], y=df[belt],
            name="Rate (t/h)",
            line=dict(color=c["green"], width=1.8), mode="lines", connectgaps=False,
            hovertemplate="%{y:.1f} t/h<extra>Rate</extra>",
        ))
        fig.add_hline(
            y=20, line_dash="dash", line_color=c["yellow"], line_width=1.5,
            annotation_text="Target 20\u202ft/h",
            annotation_position="top right",
            annotation_font=dict(color=c["yellow"], size=10),
        )

    # Right axis — Totaliser (t, cumulative, solid line)
    if tot in df.columns:
        x, y = _sparse_series(df, tot)
        fig.add_trace(go.Scatter(
            x=x, y=y,
            name="Totaliser (t)",
            line=dict(color=c["mill"][0], width=1.4), mode="lines",
            yaxis="y2",
            hovertemplate="%{y:,.0f} t<extra>Totaliser</extra>",
        ))

    fig.update_layout(
        yaxis=dict(title="t/h", range=[0, 26]),
        yaxis2=dict(title=dict(text="Totaliser (t)", font=dict(color=c["mill"][0], size=11)),
                    overlaying="y", side="right",
                    showgrid=False, tickfont=dict(size=10, color=c["mill"][0])),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_pellet_silos(df: pd.DataFrame, theme="dark") -> go.Figure:
    """
    Vertical tank-level visual for Pellet Silo 1/2/3.
    Converts Fuel_Level tonnes -> percentage using SILO_MAX_CAPACITY.
    Colour follows pellet_silo_level threshold.
    """
    c = _tc(theme)
    silo_map = [
        ("Pellet Silo Level 1 Readout", "Silo\u202f1", "pellet_silo_level_1"),
        ("Pellet Silo Level 2 Readout", "Silo\u202f2", "pellet_silo_level_23"),
        ("Pellet Silo Level 3 Readout", "Silo\u202f3", "pellet_silo_level_23"),
    ]

    def silo_color(pct, th_key):
        if pct is None:
            return c["sub"]
        th = get_thresholds().get(th_key, {})
        rl   = th.get("red_low",    15)
        gmin = th.get("green_min",  25)
        gmax = th.get("green_max",  85)
        rh   = th.get("red_high",   95)
        if pct < rl or pct > rh:
            return c["red"]
        if pct < gmin or pct > gmax:
            return c["yellow"]
        return c["green"]

    fig = go.Figure()
    for col, label, th_key in silo_map:
        raw_val = _latest(df, col) if not df.empty else None
        pct = tons_to_pct(raw_val, col)
        is_null = pct is None
        pct_display = pct if not is_null else 0
        clr = silo_color(pct, th_key)

        if is_null:
            text_str = "<b>N/A</b>"
            hover_str = f"{label}: N/A (no valid data)<extra></extra>"
        else:
            tonnes_str = f"{raw_val:.0f}\u202ft" if raw_val is not None else "\u2014"
            text_str = f"<b>{pct_display:.0f}%</b><br><span style='font-size:10px'>{tonnes_str}</span>"
            hover_str = f"{label}: {pct_display:.1f}% ({tonnes_str})<extra></extra>"

        # Background (empty tank)
        fig.add_trace(go.Bar(
            x=[label], y=[100],
            marker_color=c["grid"],
            showlegend=False, hoverinfo="skip", width=0.5,
        ))
        # Fill level
        fig.add_trace(go.Bar(
            x=[label], y=[pct_display],
            marker_color=clr,
            showlegend=False, width=0.5,
            name=label,
            text=text_str,
            textposition="outside",
            textfont=dict(color=clr, size=14),
            hovertemplate=hover_str,
        ))

    fig.update_layout(
        paper_bgcolor=c["card"], plot_bgcolor=c["bg"],
        barmode="overlay",
        font=dict(color=c["text"], size=11),
        yaxis=dict(range=[0, 125], ticksuffix="%", gridcolor=c["grid"],
                   title="Level (%)", tickfont=dict(size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        margin=dict(l=50, r=20, t=30, b=20),
        height=230,
        showlegend=False,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 2 — Mill Health & Load
# ═══════════════════════════════════════════════════════════════════════════════

def fig_mill_gauges(df: pd.DataFrame, theme="dark") -> go.Figure:
    """3 semi-circular Amps gauges (latest value) for Press 1/2/3."""
    c = _tc(theme)
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
            c["green"]  if gn <= v <= gx else
            c["yellow"] if (rl <= v < gn or gx < v <= rh) else
            c["red"]
        )
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=v,
            number={"suffix": " A", "font": {"size": 18, "color": c["text"]}},
            gauge={
                "axis": {"range": [0, 550], "tickfont": {"size": 9, "color": c["sub"]}},
                "bar": {"color": bar_clr},
                "bgcolor": c["grid"],
                "steps": [
                    {"range": [0, rl],       "color": c["g_red"]},
                    {"range": [rl, gn],      "color": c["g_yel"]},
                    {"range": [gn, gx],      "color": c["g_grn"]},
                    {"range": [gx, rh],      "color": c["g_yel"]},
                    {"range": [rh, 550],     "color": c["g_red"]},
                ],
            },
        ), row=1, col=i)

    fig.update_layout(
        paper_bgcolor=c["card"],
        font=dict(color=c["text"], size=11),
        margin=dict(l=10, r=10, t=50, b=10),
        height=190,
    )
    for ann in fig.layout.annotations:
        ann.font.color = c["sub"]
        ann.font.size  = 11
    return fig


def fig_mill_amps_trend(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Overlaid time-series: Press 1/2/3 Load Amps."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="Mill Load Amps \u2014 Trend", font=dict(size=13)))
    for col, name, clr in [
        ("Press 1 - Load Amps", "Mill\u202f1", c["mill"][0]),
        ("Press 2 - Load Amps", "Mill\u202f2", c["mill"][1]),
        ("Press 3 - Load Amps", "Mill\u202f3", c["mill"][2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.update_layout(
        yaxis=dict(title="Amps", range=[0, 550]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_mill_feeder(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Time-series: Press 1/2/3 Feeder %."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="Feeder Speed (%)", font=dict(size=13)))
    for col, name, clr in [
        ("Press 1 - Feeder %", "Mill\u202f1", c["mill"][0]),
        ("Press 2 - Feeder %", "Mill\u202f2", c["mill"][1]),
        ("Press 3 - Feeder %", "Mill\u202f3", c["mill"][2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.update_layout(
        yaxis=dict(title="%", range=[0, 100]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_roller_temp_left(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Left roller temperature trend for Mill 1/2/3."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="Left Roller Temperature (\u00b0C)", font=dict(size=13)))
    for col, name, clr in [
        ("Press 1 - Left Roller Temperature", "Mill\u202f1", c["mill"][0]),
        ("Press 2 - Left Roller Temperature", "Mill\u202f2", c["mill"][1]),
        ("Press 3 - Left Roller Temperature", "Mill\u202f3", c["mill"][2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.update_layout(
        yaxis=dict(title="\u00b0C", range=[0, 250]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_roller_temp_right(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Right roller temperature trend for Mill 1/2/3."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="Right Roller Temperature (\u00b0C)", font=dict(size=13)))
    for col, name, clr in [
        ("Press 1 - Right Roller Temperature", "Mill\u202f1", c["mill"][0]),
        ("Press 2 - Right Roller Temperature", "Mill\u202f2", c["mill"][1]),
        ("Press 3 - Right Roller Temperature", "Mill\u202f3", c["mill"][2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.update_layout(
        yaxis=dict(title="\u00b0C", range=[0, 250]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_mill_energy(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Cumulative energy (kWh) trend for Mill 1/2/3."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="Mill Cumulative Energy (kWh)", font=dict(size=13)))
    for col, name, clr in [
        ("_pm1_energy_cumulative", "Mill\u202f1", c["mill"][0]),
        ("_pm2_energy_cumulative", "Mill\u202f2", c["mill"][1]),
        ("_pm3_energy_cumulative", "Mill\u202f3", c["mill"][2]),
    ]:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["Date Time"], y=df[col],
                name=name, line=dict(color=clr, width=1.4), mode="lines",
            ))
    fig.update_layout(
        yaxis=dict(title="kWh"),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 3 — Dryer & Feed  (LEGACY — not called by current BG data flow)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_dry_silos(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Tank-level bar chart for Dry Silo 1/2. LEGACY."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    s1 = _latest(df, "Dry Silo 1 Level %") or 0
    s2 = _latest(df, "Dry Silo 2 Level %") or 0

    def bar_color(v):
        th = get_thresholds().get("dry_silo_level", {})
        rl = th.get("red_low", 20); gmin = th.get("green_min", 30)
        gmax = th.get("green_max", 80); rh = th.get("red_high", 90)
        if v < rl or v > rh: return c["red"]
        if v < gmin or v > gmax: return c["yellow"]
        return c["green"]

    fig = go.Figure()
    for label, val in [("Dry Silo\u202f1", s1), ("Dry Silo\u202f2", s2)]:
        clr = bar_color(val)
        fig.add_trace(go.Bar(x=[label], y=[100], marker_color=c["grid"],
                             showlegend=False, hoverinfo="skip", width=0.55))
        fig.add_trace(go.Bar(x=[label], y=[val], marker_color=clr, showlegend=False,
                             width=0.55, name=label, text=f"<b>{val:.0f}%</b>",
                             textposition="outside", textfont=dict(color=clr, size=18),
                             hovertemplate=f"{label}: {val:.1f}%<extra></extra>"))
    fig.update_layout(
        paper_bgcolor=c["card"], plot_bgcolor=c["bg"], barmode="overlay",
        font=dict(color=c["text"], size=11),
        yaxis=dict(range=[0, 115], ticksuffix="%", gridcolor=c["grid"],
                   title="Level (%)", tickfont=dict(size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        margin=dict(l=50, r=20, t=30, b=20), height=230, showlegend=False,
    )
    return fig


def fig_dryer_moisture(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Dryer Outlet Moisture. LEGACY."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    col_d = "Moisture %  Displayed Value at Dryer Outlet"
    col_a = "Moisture %  Actual Value at Dryer Outlet"
    fig = _fig(theme, title=dict(text="Dryer Outlet Moisture (%)", font=dict(size=13)))
    if col_d in df.columns:
        fig.add_trace(go.Scatter(x=df["Date Time"], y=df[col_d], name="Displayed",
                                 line=dict(color=c["yellow"], width=1.6, dash="dot"), mode="lines"))
    if col_a in df.columns:
        fig.add_trace(go.Scatter(x=df["Date Time"], y=df[col_a], name="Actual",
                                 line=dict(color=c["green"], width=1.6), mode="lines"))
    fig.add_hline(y=7,  line_dash="dash", line_color=c["green"],  line_width=1,
                  annotation_text="7%",  annotation_font=dict(size=9, color=c["green"]))
    fig.add_hline(y=10, line_dash="dash", line_color=c["yellow"], line_width=1,
                  annotation_text="10%", annotation_font=dict(size=9, color=c["yellow"]))
    fig.update_layout(yaxis=dict(title="%"), legend=dict(orientation="h", y=-0.22))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 4 — Quality Control  (LEGACY)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_quality_trends(df: pd.DataFrame, theme="dark") -> go.Figure:
    """2x2 subplot: Durability / Pellet Moisture / Bulk Density / Avg Length. LEGACY."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = make_subplots(rows=2, cols=2,
        subplot_titles=["Durability (%)", "Pellet Moisture (%)",
                        "Bulk Density (g/l)", "Avg Pellet Length (mm)"],
        vertical_spacing=0.18, horizontal_spacing=0.12)
    dt = df["Date Time"]
    def add(col, row, col_i, clr, g_ref=None, r_ref=None):
        if col not in df.columns: return
        fig.add_trace(go.Scatter(x=dt, y=df[col], mode="lines+markers",
                                 line=dict(color=clr, width=1.2),
                                 marker=dict(size=4, color=clr), showlegend=False), row=row, col=col_i)
        if g_ref is not None:
            fig.add_hline(y=g_ref, line_dash="dot", line_color=c["green"], line_width=1, row=row, col=col_i)
        if r_ref is not None:
            fig.add_hline(y=r_ref, line_dash="dot", line_color=c["red"], line_width=1, row=row, col=col_i)
    add("Durability %", 1, 1, c["green"], g_ref=97.5, r_ref=97.0)
    add("Pellet Moisture %", 1, 2, c["yellow"], g_ref=10.0, r_ref=11.0)
    add("Bulk  Density g/l", 2, 1, c["mill"][0], g_ref=630, r_ref=600)
    add("Average Pellet Length(mm)", 2, 2, c["mill"][1], g_ref=40, r_ref=45)
    fig.update_layout(paper_bgcolor=c["card"], plot_bgcolor=c["bg"],
                      font=dict(color=c["text"], size=11),
                      margin=dict(l=52, r=22, t=55, b=40), height=380)
    fig.update_xaxes(gridcolor=c["grid"], linecolor=c["grid"], tickfont=dict(size=9))
    fig.update_yaxes(gridcolor=c["grid"], linecolor=c["grid"], tickfont=dict(size=9))
    for ann in fig.layout.annotations:
        ann.font.color = c["sub"]; ann.font.size = 11
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 5 — CHP & Energy  (LEGACY)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_turbine_gauge(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Turbine Power gauge. LEGACY."""
    c = _tc(theme)
    th = get_thresholds().get("turbine_power", {})
    rb = th.get("red_below", 500); ga = th.get("green_above", 2000)
    val = _latest(df, "Turbine Generated Power kW") or 0
    bar_clr = c["green"] if val >= ga else (c["yellow"] if val >= rb else c["red"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=val,
        delta={"reference": ga, "relative": False, "font": {"size": 12, "color": c["sub"]}},
        number={"suffix": "\u202fkW", "font": {"size": 20, "color": c["text"]}},
        title={"text": "Turbine Power", "font": {"size": 11, "color": c["sub"]}},
        gauge={"axis": {"range": [0, 2800], "tickfont": {"size": 9, "color": c["sub"]},
                        "tickmode": "array", "tickvals": [0, 500, 1000, 1500, 2000, 2500, 2800]},
               "bar": {"color": bar_clr}, "bgcolor": c["grid"],
               "steps": [{"range": [0, rb], "color": c["g_red"]},
                         {"range": [rb, ga], "color": c["g_yel"]},
                         {"range": [ga, 2800], "color": c["g_grn"]}],
               "threshold": {"line": {"color": c["green"], "width": 2}, "thickness": 0.75, "value": ga}},
    ))
    fig.update_layout(paper_bgcolor=c["card"], font=dict(color=c["text"]),
                      margin=dict(l=20, r=20, t=30, b=10), height=200)
    return fig


def fig_chp_trend(df: pd.DataFrame, theme="dark") -> go.Figure:
    """CHP Temperature Trends. LEGACY."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="CHP Temperature Trends", font=dict(size=13)))
    if "Furnace Temp" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date Time"], y=df["Furnace Temp"],
                                 name="Furnace Temp (\u00b0C)",
                                 line=dict(color=c["red"], width=1.6), mode="lines"))
    if "Thermal Oil OUT" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date Time"], y=df["Thermal Oil OUT"],
                                 name="Thermal Oil OUT (\u00b0C)",
                                 line=dict(color=c["yellow"], width=1.6), mode="lines", yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Furnace Temp (\u00b0C)", gridcolor=c["grid"], linecolor=c["grid"], tickfont=dict(size=10)),
        yaxis2=dict(title="Thermal Oil (\u00b0C)", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)", linecolor=c["grid"], tickfont=dict(size=10)),
        legend=dict(orientation="h", y=-0.22))
    return fig


def fig_hru_damper(df: pd.DataFrame, theme="dark") -> go.Figure:
    """HRU Bypass Damper. LEGACY."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="HRU Bypass Damper", font=dict(size=13)),
               margin=dict(l=52, r=22, t=38, b=40))
    col = "HRU Bypass Damper"
    if col in df.columns:
        fig.add_trace(go.Scatter(x=df["Date Time"], y=df[col], name="HRU Bypass Damper",
                                 line=dict(color=c["mill"][0], width=1.4), mode="lines", showlegend=False))
    fig.update_layout(yaxis=dict(title="Position"))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 6 — Downtime & Events  (LEGACY)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_downtime_pareto(events_df: pd.DataFrame, theme="dark") -> go.Figure:
    """Downtime Pareto. LEGACY."""
    c = _tc(theme)
    if events_df.empty or "Fault Category" not in events_df.columns:
        return _empty(theme, "No downtime events in selected range")
    grp = (events_df.groupby("Fault Category", as_index=False)["Duration_min"]
           .sum().sort_values("Duration_min", ascending=False).reset_index(drop=True))
    if grp.empty:
        return _empty(theme, "No downtime data")
    total = grp["Duration_min"].sum()
    grp["cum_pct"] = grp["Duration_min"].cumsum() / total * 100
    cats = list(grp["Fault Category"])
    fig = _fig(theme, title=dict(text="Downtime Pareto \u2014 Fault Category", font=dict(size=13)))
    fig.add_trace(go.Bar(x=cats, y=grp["Duration_min"], name="Downtime (min)", marker_color=c["red"], yaxis="y"))
    fig.add_trace(go.Scatter(x=cats, y=grp["cum_pct"], name="Cumulative %",
                             line=dict(color=c["yellow"], width=2), mode="lines+markers",
                             marker=dict(size=6), yaxis="y2"))
    fig.add_trace(go.Scatter(x=cats, y=[80]*len(cats), mode="lines",
                             line=dict(color=c["green"], width=1.5, dash="dash"),
                             yaxis="y2", showlegend=False, hoverinfo="skip"))
    fig.update_layout(
        yaxis=dict(title="Downtime (min)", gridcolor=c["grid"], linecolor=c["grid"], tickfont=dict(size=10)),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105],
                    gridcolor="rgba(0,0,0,0)", linecolor=c["grid"], ticksuffix="%", tickfont=dict(size=10)),
        legend=dict(orientation="h", y=-0.25), xaxis=dict(tickangle=-30, tickfont=dict(size=10)))
    return fig


def fig_area_downtime(events_df: pd.DataFrame, theme="dark") -> go.Figure:
    """Downtime by Area. LEGACY."""
    c = _tc(theme)
    if events_df.empty or "Area" not in events_df.columns:
        return _empty(theme, "No downtime events in selected range")
    grp = (events_df.groupby("Area", as_index=False)["Duration_min"]
           .sum().sort_values("Duration_min", ascending=True))
    if grp.empty:
        return _empty(theme, "No downtime data")
    fig = _fig(theme, title=dict(text="Downtime by Area (min)", font=dict(size=13)))
    fig.add_trace(go.Bar(x=grp["Duration_min"], y=grp["Area"], orientation="h",
                         marker_color=c["yellow"], text=[f"{v:.0f}" for v in grp["Duration_min"]],
                         textposition="outside", textfont=dict(color=c["text"], size=10)))
    fig.update_layout(xaxis=dict(title="minutes"), margin=dict(l=140, r=60, t=38, b=40))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 3 — Pellet Silo (Phase 8)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_silo_level_trend(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Time-series: Pellet Silo 1/2/3 fill level (%) with threshold colour bands."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)

    th   = get_thresholds().get("pellet_silo_level_23", {})
    rl   = th.get("red_low",   10)
    gmin = th.get("green_min", 20)
    gmax = th.get("green_max", 80)
    rh   = th.get("red_high",  90)

    fig = _fig(theme, title=dict(text="Pellet Silo Level Trend (%)", font=dict(size=13)))

    # Threshold colour bands (background) — use semantic colours with alpha
    r_a = "rgba(219,68,55,0.08)" if theme == "dark" else "rgba(198,40,40,0.10)"
    y_a = "rgba(244,180,0,0.08)" if theme == "dark" else "rgba(184,134,11,0.10)"
    g_a = "rgba(15,155,88,0.08)" if theme == "dark" else "rgba(13,138,78,0.10)"
    for lo, hi, clr in [
        (0, rl, r_a), (rl, gmin, y_a), (gmin, gmax, g_a), (gmax, rh, y_a), (rh, 120, r_a),
    ]:
        fig.add_hrect(y0=lo, y1=hi, fillcolor=clr, line_width=0)

    silo_cols = [
        ("Pellet Silo Level 1 Readout", "Silo\u202f1", c["mill"][0]),
        ("Pellet Silo Level 2 Readout", "Silo\u202f2", c["mill"][1]),
        ("Pellet Silo Level 3 Readout", "Silo\u202f3", c["mill"][2]),
    ]
    for col, name, clr in silo_cols:
        if col not in df.columns:
            continue
        x, y_raw = _sparse_series(df, col)
        pct_y = y_raw.apply(lambda v: tons_to_pct(v, col))
        fig.add_trace(go.Scatter(
            x=x, y=pct_y,
            name=name, line=dict(color=clr, width=1.6), mode="lines",
            hovertemplate="%{y:.1f}%<extra>" + name + "</extra>",
        ))

    fig.update_layout(
        yaxis=dict(title="%", range=[0, 120]),
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


def fig_silo_infeed_trend(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Cumulative infeed totaliser trend for Silo 1/2/3."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="Silo Infeed Totaliser (t)", font=dict(size=13)))
    for col, name, clr in [
        ("_silo1_infeed_totaliser", "Silo\u202f1", c["mill"][0]),
        ("_silo2_infeed_totaliser", "Silo\u202f2", c["mill"][1]),
        ("_silo3_infeed_totaliser", "Silo\u202f3", c["mill"][2]),
    ]:
        if col in df.columns:
            x, y = _sparse_series(df, col)
            fig.add_trace(go.Scatter(
                x=x, y=y,
                name=name, line=dict(color=clr, width=1.4), mode="lines",
                hovertemplate="%{y:,.0f} t<extra>" + name + "</extra>",
            ))
    fig.update_layout(yaxis=dict(title="t"), legend=dict(orientation="h", y=-0.22))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Panel 4 — Dispatch (Phase 8)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_dispatch_trend(df: pd.DataFrame, theme="dark") -> go.Figure:
    """Cumulative dispatch: Bagging and Truck totalisers over time."""
    if df.empty:
        return _empty(theme)
    c = _tc(theme)
    fig = _fig(theme, title=dict(text="Dispatch Totaliser (t)", font=dict(size=13)))
    for col, name, clr in [
        ("_bagging_totaliser", "Bagging",  c["green"]),
        ("_truck_totaliser",   "Truck",    c["mill"][0]),
    ]:
        if col in df.columns:
            x, y = _sparse_series(df, col)
            fig.add_trace(go.Scatter(
                x=x, y=y,
                name=name, line=dict(color=clr, width=1.6), mode="lines",
                hovertemplate="%{y:,.0f} t<extra>" + name + "</extra>",
            ))
    fig.update_layout(yaxis=dict(title="t"), legend=dict(orientation="h", y=-0.22))
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# AI Placeholder — Fake-data charts (Phase 5)
# ═══════════════════════════════════════════════════════════════════════════════

def fig_ai_production_forecast(theme="dark") -> go.Figure:
    """Fake 24h production forecast with +/-15% confidence band."""
    c = _tc(theme)
    np.random.seed(42)
    hours = pd.date_range("2026-02-02 00:00", periods=24, freq="h")
    base = 16 + np.cumsum(np.random.randn(24) * 0.3)
    upper = base * 1.15
    lower = base * 0.85

    fig = _fig(theme, title=dict(text="24h Production Forecast (t/h)", font=dict(size=12)),
               height=220, margin=dict(l=42, r=16, t=34, b=36))
    fig.add_trace(go.Scatter(
        x=list(hours) + list(hours[::-1]),
        y=list(upper) + list(lower[::-1]),
        fill="toself", fillcolor="rgba(15,155,88,0.15)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=hours, y=base, mode="lines",
        line=dict(color=c["green"], width=2), name="Forecast", showlegend=False,
    ))
    now_x = str(hours[6])
    fig.add_shape(type="line", x0=now_x, x1=now_x, y0=0, y1=1,
                  yref="paper", line=dict(color=c["yellow"], width=1, dash="dash"))
    fig.add_annotation(x=now_x, y=1, yref="paper", text="Now",
                       showarrow=False, font=dict(size=9, color=c["yellow"]), yshift=8)
    fig.update_layout(yaxis=dict(title="t/h", range=[10, 22]), xaxis=dict(tickformat="%H:%M"))
    return fig


def fig_ai_fault_prediction(theme="dark") -> go.Figure:
    """Fake fault prediction: horizontal bar showing risk levels."""
    c = _tc(theme)
    components = ["Mill 2 Blockage", "Dryer Overheat", "Bearing Wear", "Belt Slip"]
    probs = [72, 35, 18, 8]
    colors = [c["red"], c["yellow"], c["green"], c["green"]]

    fig = _fig(theme, title=dict(text="Fault Probability \u2014 Next 24h", font=dict(size=12)),
               height=220, margin=dict(l=120, r=40, t=34, b=36))
    fig.add_trace(go.Bar(
        y=components, x=probs, orientation="h", marker_color=colors,
        text=[f"{p}%" for p in probs], textposition="outside",
        textfont=dict(color=c["text"], size=11), showlegend=False,
    ))
    fig.update_layout(xaxis=dict(title="Probability %", range=[0, 100]),
                      yaxis=dict(autorange="reversed"))
    fig.add_annotation(x=72, y="Mill 2 Blockage", text="ETA ~14h",
                       showarrow=True, arrowhead=2, arrowcolor=c["red"],
                       font=dict(color=c["red"], size=10), ax=40, ay=-20)
    return fig


def fig_ai_anomaly_detection(theme="dark") -> go.Figure:
    """Fake timeline with 4 anomaly markers."""
    c = _tc(theme)
    np.random.seed(7)
    hours = pd.date_range("2026-01-28", periods=96, freq="h")
    signal = 14 + np.sin(np.arange(96) * 0.15) * 2 + np.random.randn(96) * 0.4
    anomaly_idx = [18, 45, 72, 88]
    for i in anomaly_idx:
        signal[i] += np.random.choice([-4, 4])

    fig = _fig(theme, title=dict(text="Anomaly Detection \u2014 Throughput", font=dict(size=12)),
               height=220, margin=dict(l=42, r=16, t=34, b=36))
    fig.add_trace(go.Scatter(x=hours, y=signal, mode="lines",
                             line=dict(color=c["mill"][0], width=1.4), showlegend=False))
    fig.add_trace(go.Scatter(x=hours[anomaly_idx], y=signal[anomaly_idx], mode="markers",
                             marker=dict(symbol="triangle-up", size=12, color=c["red"],
                                         line=dict(width=1, color="#ff8a80")),
                             name="Anomaly", showlegend=False,
                             hovertemplate="Anomaly<br>%{x}<br>%{y:.1f} t/h<extra></extra>"))
    fig.update_layout(yaxis=dict(title="t/h"), xaxis=dict(tickformat="%d %b %H:%M"))
    return fig


def fig_ai_root_cause(theme="dark") -> go.Figure:
    """Fake Sankey: Feed Rate -> Moisture -> Blockage causal chain."""
    c = _tc(theme)
    labels = ["Feed Rate \u2191", "Moisture \u2191", "Die Pressure \u2191",
              "Blockage", "Bearing Temp \u2191", "Normal"]
    fig = go.Figure(go.Sankey(
        node=dict(pad=15, thickness=18, line=dict(color=c["grid"], width=0.5),
                  label=labels,
                  color=[c["yellow"], c["yellow"], c["red"], c["red"], c["yellow"], c["green"]]),
        link=dict(source=[0, 0, 1, 1, 2, 2], target=[1, 5, 2, 4, 3, 5],
                  value=[60, 40, 45, 15, 35, 10],
                  color=["rgba(244,180,0,0.25)", "rgba(15,155,88,0.2)",
                         "rgba(219,68,55,0.25)", "rgba(244,180,0,0.2)",
                         "rgba(219,68,55,0.3)", "rgba(15,155,88,0.15)"]),
    ))
    fig.update_layout(
        title=dict(text="Root Cause Analysis", font=dict(size=12, color=c["text"])),
        paper_bgcolor=c["card"],
        font=dict(color=c["text"], family="Roboto Mono, Courier New, monospace", size=10),
        margin=dict(l=16, r=16, t=34, b=16), height=220,
    )
    return fig
