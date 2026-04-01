# Layout Specification & Acceptance Criteria

> **Phase 8 更新 (2026-04)**: 数据源切换为 BG 实时 CSV (17 列)。
> Energy/Dryer/Quality/Events 面板已移除（BG 未覆盖）。

## Page 1 — KPI Overview (`/`)

> 首页：大字体 KPI 卡片 + 液位罐，一眼总览工厂状态。
> 导航按钮: **Overview** · Detail · AI

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] Land Energy — Dashboard                                    │
│        Date: [auto]     🌐[EN|中|FR] ⚙️                            │
│        [1m][30m][1h][6h][24h]  Auto-refresh:[Off|5s|30s|1m]      │
│        [Overview] · [Detail] · [AI]                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ── PRODUCTION ─────────────────────────────────────────────────  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Daily Out │  │  Rate    │  │  Mills   │  │Cumulative│        │
│  │  324 t   │  │ 13.8t/h🟡│  │  3/3  🟢 │  │ 2,450 t  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  ── MILL STATUS ────────────────────────────────────────────────  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │ Mill 1   │  │ Mill 2   │  │ Mill 3   │                       │
│  │  285 A 🟢│  │  291 A 🟢│  │  278 A 🟡│                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
│                                                                  │
│  ── PELLET SILO ────────────────────────────────────────────────  │
│  ┌───────┐     ┌───────┐     ┌───────┐                          │
│  │▓▓▓▓▓▓│     │▓▓▓▓  │     │▓▓    │                            │
│  │▓▓▓▓▓▓│     │▓▓▓▓  │     │      │                            │
│  │ 78 %  │     │ 52 %  │     │ 23 % │                            │
│  │Silo 1 │     │Silo 2 │     │Silo 3│                            │
│  └───────┘     └───────┘     └───────┘                           │
│                                                                  │
│  ── DISPATCH ───────────────────────────────────────────────────  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │ Bagging  │  │ Truck    │  │  Total   │                       │
│  │ Today    │  │ Today    │  │ Dispatch │                       │
│  │  45 t    │  │  80 t    │  │  125 t   │                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### P1 KPI 卡片定义

**Production (4 张 `_ov_card`)**:
| 卡片 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Daily Output | Totaliser 累计差值（当日） | t | 无颜色 |
| Hourly Rate | `Total tons passed belt weigher (hour)` 最新值 | t/h | `belt_weigher_hourly` 阈值 |
| Mills Running | 3 台 Amps > 50A 计数 | x/3 | 3=🟢 1-2=🟡 0=🔴 |
| Period Total | Totaliser 累计差值（选定时间范围） | t | 无颜色 |

**Mill Status (3 张 `_ov_card`)**:
| 卡片 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Mill 1 Amps | `Press 1 - Load Amps` 最新值 | A | `press_load_amps` 阈值 |
| Mill 2 Amps | `Press 2 - Load Amps` 最新值 | A | `press_load_amps` 阈值 |
| Mill 3 Amps | `Press 3 - Load Amps` 最新值 | A | `press_load_amps` 阈值 |

**Pellet Silo (3 个 `_ov_tank` 液位罐)**:
| 卡片 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Pellet Silo 1 | `Pellet Silo Level 1 Readout` → `tons_to_pct()` | % | `pellet_silo_level` 阈值 |
| Pellet Silo 2 | `Pellet Silo Level 2 Readout` → `tons_to_pct()` | % | `pellet_silo_level` 阈值 |
| Pellet Silo 3 | `Pellet Silo Level 3 Readout` → `tons_to_pct()` | % | `pellet_silo_level` 阈值 |

**Dispatch (3 张 `_ov_card`)**:
| 卡片 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Bagging Today | `_bagging_totaliser` 当日差值 | t | 无颜色 |
| Truck Today | `_truck_totaliser` 当日差值 | t | 无颜色 |
| Total Dispatch | Bagging + Truck 合计 | t | 无颜色 |

---

## Page 2 — Detailed Operations (`/ops`)

> 详细运营监控页：KPI 卡片行 + 4 面板 + 全数据表。
> 导航按钮: Overview · **Detail** · AI

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] Land Energy — Dashboard                                    │
│        Date: [auto]     🌐[EN|中|FR] ⚙️                            │
│        [1m][30m][1h][6h][24h]  Auto-refresh:[Off|5s|30s|1m]      │
├──────────────────────────────────────────────────────────────────┤
│ OEE    │ Daily    │ Rate    │ Mills                              │
│ — %    │ Out (t)  │ (t/h)   │ Status                             │
│ ░ N/A  │ 324.5    │ 13.7 🟡  │ 3/3 🟢                             │
├──────────────────────────────────────────────────────────────────┤
│ [Tab: Production] [Mill Health] [Pellet Silo] [Dispatch]         │
├──────────────────────────────────────────────────────────────────┤
│ ┌─ Production & Throughput ──────────────────────────────────┐   │
│ │ [Line: Belt Weigher t/h + 20 t/h target]  │ Period Output │   │
│ │                                             │   2,450 t    │   │
│ │                                             │──────────────│   │
│ │                                             │ [Tank×3:     │   │
│ │                                             │  Silo % ]    │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Mill Health & Load ───────────────────────────────────────┐   │
│ │ [●]M1:Running [●]M2:Running [●]M3:Running                 │   │
│ │ [Gauge×3: Amps]                                            │   │
│ │ [Line: Amps trend]        │ [Line: Feeder % trend]         │   │
│ │ [Line: Roller Temp Diff]  │ [Line: Mill Energy kWh]        │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Pellet Silo ──────────────────────────────────────────────┐   │
│ │ [Line: Silo 1/2/3 % trend + threshold bands]              │   │
│ │ [Line: Infeed Totaliser trend ×3]                          │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Dispatch ─────────────────────────────────────────────────┐   │
│ │ [Line: Bagging + Truck Totaliser trend]                    │   │
│ └────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────┤
│ Full Data Table (live_data columns, scrollable, sortable)        │
└──────────────────────────────────────────────────────────────────┘
```

### P2 KPI 卡片定义

| 卡片 | 数据来源 | 颜色逻辑 |
|------|----------|----------|
| OEE | 无 | 固定灰色，显示 "— %" |
| Daily Output | Totaliser 当日差值 | 无颜色 |
| Rate (t/h) | `Total tons passed belt weigher (hour)` 最新值 | `belt_weigher_hourly` 阈值 |
| Mills Status | 3 台 Amps > 50A | 全部=🟢, 部分=🟡, 全停=🔴 |

### P2 图表清单

| 面板 | 图表 | 类型 | 数据列 |
|------|------|------|--------|
| Production | `fig_production_lines` | 折线图 | Belt Weigher t/h |
| Production | `fig_pellet_silos` | 液位罐 (tank overlay) | Silo 1/2/3 → % |
| Mill | `fig_mill_gauges` | 半圆仪表盘 ×3 | Mill 1/2/3 Amps |
| Mill | `fig_mill_amps_trend` | 折线图 (×3 线) | Mill 1/2/3 Amps |
| Mill | `fig_mill_feeder` | 折线图 (×3 线) | Mill 1/2/3 Feeder % |
| Mill | `fig_roller_temp_diff` | 折线图 (×3 线) | Mill 1/2/3 |Left-Right| Temp |
| Mill | `fig_mill_energy` | 折线图 (×3 线) | Mill 1/2/3 累计 kWh |
| Pellet Silo | `fig_silo_level_trend` | 折线图 + 阈值色带 | Silo 1/2/3 % |
| Pellet Silo | `fig_silo_infeed_trend` | 折线图 (×3 线) | Silo 1/2/3 Infeed |
| Dispatch | `fig_dispatch_trend` | 折线图 (2 线) | Bagging + Truck |

---

## Page 3 — AI Analytics Placeholder (`/ai`)

> AI 占位页：伪数据面板 + 灰色 overlay。不变。
> 导航按钮: Overview · Detail · **AI**

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] AI Predictive Analytics — Coming Soon     🌐[EN|中|FR]    │
├───────────────────────┬──────────────────────────────────────────┤
│ Production Forecast   │ Fault Prediction                         │
│ [Fake trend+band]     │ Mill 2 Blockage ETA:14h Conf:72%        │
│ ░░ PLACEHOLDER ░░     │ ░░ PLACEHOLDER ░░                        │
├───────────────────────┼──────────────────────────────────────────┤
│ Anomaly Detection     │ Root Cause Analysis                      │
│ [Fake timeline]       │ [Fake Sankey]                            │
│ ░░ PLACEHOLDER ░░     │ ░░ PLACEHOLDER ░░                        │
├──────────────────────────────────────────────────────────────────┤
│ Requires more historical data. Expected: Q3 2026                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 设计原则

1. 深色主题 SCADA 风格 (Grafana/MachineMetrics)
2. 关键数字 2 米外可读（KPI 值 >= 48px, 总览页 52px）
3. 红黄绿全局统一语义
4. Gauge 用于有明确上下限的参数 (Mill Amps)
5. Tank Level 用于 Silo 液位 (Pellet Silo 百分比)
6. 折线图用于时间序列趋势 (所有趋势图表)
7. 多线叠加用于同类对比 (3 台 Mill 在同一图上)

---

## 页面路由

| 页面 | 路径 | 导航按钮 | 内容 |
|------|------|---------|------|
| P1 KPI 总览 | `/` | Overview | 13 KPI (4 card + 3 card + 3 tank + 3 card) |
| P2 详细运营 | `/ops` | Detail | KPI 行 + 4 面板 + 10 图表 + 全数据表 |
| P3 AI 占位 | `/ai` | AI | 4 伪面板 + overlay + Coming Soon |

---

## 完整验收标准

### 基础
- [ ] `python src/app.py` 启动无报错
- [ ] localhost:8050 显示 Dashboard
- [ ] 顶部有 Land Energy Logo + 工厂名

### 导航
- [ ] 3 页导航: Overview · Detail · AI
- [ ] 默认首页为 P1 KPI 总览 (`/`)
- [ ] P2 详细运营 (`/ops`) 可访问
- [ ] P3 AI 占位 (`/ai`) 可访问

### P1 KPI 总览
- [ ] Production 组: 4 张大字 KPI 卡片 (Daily Output, Rate, Mills, Cumulative)
- [ ] Mill Status 组: 3 张 KPI 卡片 (Mill 1/2/3 Amps)
- [ ] Pellet Silo 组: 3 个百分比液位罐 (tank visual, 非吨数条形图)
- [ ] Dispatch 组: 3 张 KPI 卡片 (Bagging, Truck, Total)
- [ ] KPI 值字体 >= 52px，醒目可读
- [ ] 阈值颜色正确 (Rate/Mills/Amps/Silo Level)
- [ ] 时间范围联动刷新所有卡片
- [ ] 无 Energy/Dryer/Quality section（已移除）

### P2 详细运营 (数据)
- [ ] OEE 灰色占位，不计算
- [ ] KPI 卡片数值匹配数据库（可抽查）
- [ ] 面板导航只有 4 个按钮: Production / Mill Health / Pellet Silo / Dispatch
- [ ] 磨机状态灯正确 (Amps>50=Running)
- [ ] Pellet Silo = 液位罐 (百分比，非吨数)
- [ ] Mill Energy 趋势 = 累计 kWh (非 kWh/t)
- [ ] Silo Level 趋势有阈值色带
- [ ] 底部数据表显示 live_data 所有列
- [ ] 无 Dryer/Quality/CHP/Downtime 面板（已移除）

### P2 图表精确性
- [ ] Production 趋势只有 Belt Weigher 一条线（无 Dryer Out Feed）
- [ ] Mill 图表 3 台 Mill 颜色区分清晰
- [ ] Dispatch 趋势 Bagging + Truck 两条线

### 阈值面板
- [ ] 可打开设置面板
- [ ] 4 个有效阈值可调: press_load_amps, belt_weigher_hourly, feeder_pct, pellet_silo_level
- [ ] 调整即时生效
- [ ] Reset 恢复默认
- [ ] 持久化到 thresholds.json

### 三语
- [ ] EN/中/FR 切换正常
- [ ] 所有标题/按钮已翻译（含新增 Mill Status/Pellet Silo/Dispatch）
- [ ] 无错位截断
- [ ] 默认 English

### P3 AI Placeholder
- [ ] 4 个 Placeholder + "Coming Soon"
- [ ] 面板标题三语
