# src/translations.py
"""
Trilingual UI strings: English / Chinese / French.
Usage:
    from translations import t
    label = t("panel_production", lang)   # lang: "en" | "zh" | "fr"
"""

DEFAULT_LANG = "en"

TRANSLATIONS = {
    "en": {
        # ── Page titles ──────────────────────────────────────────────────
        "page1_title":          "Operational Overview",
        "page2_title":          "AI Analytics",
        # ── Navigation ───────────────────────────────────────────────────
        "page1_nav":            "Page 1",
        "page2_nav":            "Page 2",
        # ── Panel headers ────────────────────────────────────────────────
        "panel_production":     "Production & Throughput",
        "panel_mill":           "Mill Health & Load",
        "panel_dryer":          "Dryer & Feed",
        "panel_quality":        "Quality Control",
        "panel_chp":            "CHP & Energy",
        "panel_downtime":       "Downtime & Events",
        # ── KPI card labels ──────────────────────────────────────────────
        "kpi_daily_output":     "Daily Output",
        "kpi_rate":             "Rate (t/h)",
        "kpi_mills":            "Mills Status",
        "kpi_dryer_feed":       "Dryer Feed",
        "kpi_events":           "Events (24h)",
        "kpi_oee":              "OEE",
        # ── Status labels ────────────────────────────────────────────────
        "state_running":        "Running",
        "state_stopped":        "Stopped",
        "state_insufficient":   "Insufficient Data",
        # ── Buttons ──────────────────────────────────────────────────────
        "btn_apply":            "Apply",
        "btn_save_apply":       "Save & Apply",
        "btn_reset":            "Reset to Default",
        "btn_reset_all":        "Reset All to Default",
        # ── Settings panel ───────────────────────────────────────────────
        "settings_title":       "Threshold Settings",
        # ── Threshold group names ────────────────────────────────────────
        "group_mill":           "Mill",
        "group_dryer":          "Dryer",
        "group_quality":        "Quality",
        "group_chp":            "CHP",
        "group_throughput":     "Throughput",
        "group_other":          "Other",
        # ── Page 2 placeholders ──────────────────────────────────────────
        "p2_coming_soon":       "Coming Soon",
        "p2_production_fc":     "Production Forecast",
        "p2_fault_pred":        "Fault Prediction",
        "p2_anomaly":           "Anomaly Detection",
        "p2_root_cause":        "Root Cause Analysis",
        "p2_overlay":           "Requires additional historical data",
        "p2_availability":      "Expected availability: Q3 2026",
        # ── Chart / axis labels ──────────────────────────────────────────
        "chart_target_line":    "Target (20 t/h)",
        "chart_belt_weigher":   "Belt Weigher [Col 51] (t/h)",
        "chart_dryer_feed":     "Dryer Out Feed [Col 8] (t/h)",
        "chart_cumulative":     "Cumulative Output (t)",
        "chart_downtime_min":   "Downtime (min)",
        "chart_events_table":   "Recent Events",
        # ── Date picker ──────────────────────────────────────────────────
        "date_range":           "Date Range",
    },
    "zh": {
        "page1_title":          "\u8fd0\u8425\u76d1\u63a7",
        "page2_title":          "AI \u5206\u6790",
        "page1_nav":            "\u7b2c1\u9875",
        "page2_nav":            "\u7b2c2\u9875",
        "panel_production":     "\u4ea7\u91cf\u4e0e\u751f\u4ea7\u7387",
        "panel_mill":           "\u78e8\u673a\u5065\u5eb7\u4e0e\u8d1f\u8f7d",
        "panel_dryer":          "\u70d8\u5e72\u4e0e\u4f9b\u6599",
        "panel_quality":        "\u8d28\u91cf\u63a7\u5236",
        "panel_chp":            "\u70ed\u7535\u8054\u4ea7\u4e0e\u80fd\u6548",
        "panel_downtime":       "\u505c\u673a\u4e0e\u4e8b\u4ef6",
        "kpi_daily_output":     "\u65e5\u4ea7\u91cf",
        "kpi_rate":             "\u5b9e\u65f6\u4ea7\u91cf (t/h)",
        "kpi_mills":            "\u78e8\u673a\u72b6\u6001",
        "kpi_dryer_feed":       "\u70d8\u5e72\u51fa\u6599",
        "kpi_events":           "\u4e8b\u4ef6 (24h)",
        "kpi_oee":              "OEE",
        "state_running":        "\u8fd0\u884c\u4e2d",
        "state_stopped":        "\u505c\u673a",
        "state_insufficient":   "\u6570\u636e\u4e0d\u8db3",
        "btn_apply":            "\u5e94\u7528",
        "btn_save_apply":       "\u4fdd\u5b58\u5e76\u5e94\u7528",
        "btn_reset":            "\u6062\u590d\u9ed8\u8ba4",
        "btn_reset_all":        "\u5168\u90e8\u6062\u590d\u9ed8\u8ba4",
        "settings_title":       "\u9608\u5024\u8bbe\u7f6e",
        "group_mill":           "\u78e8\u673a",
        "group_dryer":          "\u70d8\u5e72",
        "group_quality":        "\u8d28\u91cf",
        "group_chp":            "\u70ed\u7535\u8054\u4ea7",
        "group_throughput":     "\u4ea7\u91cf",
        "group_other":          "\u5176\u4ed6",
        "p2_coming_soon":       "\u5373\u5c06\u63a8\u51fa",
        "p2_production_fc":     "\u4ea7\u91cf\u9884\u6d4b",
        "p2_fault_pred":        "\u6545\u969c\u9884\u6d4b",
        "p2_anomaly":           "\u5f02\u5e38\u68c0\u6d4b",
        "p2_root_cause":        "\u6839\u56e0\u5206\u6790",
        "p2_overlay":           "\u9700\u8981\u66f4\u591a\u5386\u53f2\u6570\u636e\u6765\u8bad\u7ec3\u6a21\u578b",
        "p2_availability":      "\u9884\u8ba1\u53ef\u7528\u65f6\u95f4\uff1a2026\u5e74\u7b2c\u4e09\u5b63\u5ea6",
        "chart_target_line":    "\u76ee\u6807 (20 t/h)",
        "chart_belt_weigher":   "\u76ae\u5e26\u79e4 [Col 51] (t/h)",
        "chart_dryer_feed":     "\u70d8\u5e72\u51fa\u6599 [Col 8] (t/h)",
        "chart_cumulative":     "\u7d2f\u8ba1\u4ea7\u91cf (t)",
        "chart_downtime_min":   "\u505c\u673a\u65f6\u957f (min)",
        "chart_events_table":   "\u8fd1\u671f\u4e8b\u4ef6",
        "date_range":           "\u65f6\u95f4\u8303\u56f4",
    },
    "fr": {
        "page1_title":          "Vue op\u00e9rationnelle",
        "page2_title":          "Analytique IA",
        "page1_nav":            "Page 1",
        "page2_nav":            "Page 2",
        "panel_production":     "Production et d\u00e9bit",
        "panel_mill":           "Sant\u00e9 et charge des broyeurs",
        "panel_dryer":          "S\u00e9choir et alimentation",
        "panel_quality":        "Contr\u00f4le qualit\u00e9",
        "panel_chp":            "Cog\u00e9n\u00e9ration et \u00e9nergie",
        "panel_downtime":       "Arr\u00eats et \u00e9v\u00e9nements",
        "kpi_daily_output":     "Production journali\u00e8re",
        "kpi_rate":             "D\u00e9bit (t/h)",
        "kpi_mills":            "\u00c9tat des broyeurs",
        "kpi_dryer_feed":       "D\u00e9bit s\u00e9choir",
        "kpi_events":           "\u00c9v\u00e9nements (24h)",
        "kpi_oee":              "OEE",
        "state_running":        "En marche",
        "state_stopped":        "Arr\u00eat\u00e9",
        "state_insufficient":   "Donn\u00e9es insuffisantes",
        "btn_apply":            "Appliquer",
        "btn_save_apply":       "Enregistrer et appliquer",
        "btn_reset":            "R\u00e9initialiser",
        "btn_reset_all":        "Tout r\u00e9initialiser",
        "settings_title":       "Param\u00e8tres de seuil",
        "group_mill":           "Broyeurs",
        "group_dryer":          "S\u00e9choir",
        "group_quality":        "Qualit\u00e9",
        "group_chp":            "Cog\u00e9n\u00e9ration",
        "group_throughput":     "D\u00e9bit",
        "group_other":          "Autre",
        "p2_coming_soon":       "Bient\u00f4t disponible",
        "p2_production_fc":     "Pr\u00e9vision de production",
        "p2_fault_pred":        "Pr\u00e9diction de pannes",
        "p2_anomaly":           "D\u00e9tection d\u2019anomalies",
        "p2_root_cause":        "Analyse des causes profondes",
        "p2_overlay":           "N\u00e9cessite des donn\u00e9es historiques suppl\u00e9mentaires",
        "p2_availability":      "Disponibilit\u00e9 pr\u00e9vue\u00a0: T3 2026",
        "chart_target_line":    "Objectif (20 t/h)",
        "chart_belt_weigher":   "Peseur \u00e0 bande [Col 51] (t/h)",
        "chart_dryer_feed":     "D\u00e9bit s\u00e9choir [Col 8] (t/h)",
        "chart_cumulative":     "Production cumul\u00e9e (t)",
        "chart_downtime_min":   "Arr\u00eat (min)",
        "chart_events_table":   "\u00c9v\u00e9nements r\u00e9cents",
        "date_range":           "P\u00e9riode",
    },
}


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    """Return the translated string for *key* in *lang*.
    Falls back to English if the key is missing in the requested language.
    Falls back to *key* itself if not found in English either.
    """
    return (
        TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG])
        .get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))
    )
