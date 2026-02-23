# Layout Specification & Acceptance Criteria

## Page 1 — KPI Overview (`/`)

> 首页：大字体 KPI 卡片 + Quality 网格，一眼总览工厂状态。
> 导航按钮: **Overview** · Detail · AI

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] Land Energy — Dashboard                                    │
│        Date: [01-01] → [02-01] [Apply]   🌐[EN|中|FR] ⚙️          │
│        [Overview] · [Detail] · [AI]                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ── PRODUCTION ─────────────────────────────────────────────────  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Daily Out │  │  Rate    │  │  Mills   │  │Cumulative│        │
│  │  324 t   │  │ 13.8t/h🟡│  │  3/3  🟢 │  │ 807,680t │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  ── ENERGY ─────────────────────────────────────────────────────  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Turbine  │  │ Furnace  │  │Thermal   │  │HRU Bypass│        │
│  │ 1950 kW  │  │  940 °C  │  │Oil 285°C │  │  42 %    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  ── DRYER ──────────────────────────────────────────────────────  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Dryer Feed│  │Outlet    │  │Dry Silo 1│  │Dry Silo 2│        │
│  │ 12.8t/h🟢│  │Moist 8.2%│  │  67 %    │  │  38 %    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  ── PELLET QUALITY ─────────────────────────────────────────────  │
│  ┌────────────────┬────────────────┬────────────────┐            │
│  │  Durability    │  Bulk Density  │ Pellet Moisture│            │
│  │    98.5 %    🟢│    641 g/l   🟢│     7.5 %    🟢│            │
│  ├────────────────┼────────────────┼────────────────┤            │
│  │  Pellet Temp   │  Avg Length    │                │            │
│  │    28 °C     🟢│    22 mm     🟢│                │            │
│  └────────────────┴────────────────┴────────────────┘            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### P1 KPI 卡片定义

**Production (4 张)**:
| 卡片 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Daily Output | Col 45 累计差值（当日） | t | 无颜色 |
| Hourly Rate | Col 51 `Total tons passed belt weigher (hour)` | t/h | Belt Weigher 阈值 |
| Mills Running | 3 台 Amps > 50A 计数 | x/3 | 3=🟢 1-2=🟡 0=🔴 |
| Period Total | Col 45 累计差值（选定日期范围） | t | 无颜色 |

**Energy (4 张)**:
| 卡片 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Turbine Power | Col 48 `Turbine Generated Power kW` | kW | Turbine 阈值 |
| Furnace Temp | Col 45 `Furnace Temp` | °C | Furnace 阈值 |
| Thermal Oil OUT | Col 47 `Thermal Oil OUT` | °C | 无颜色 |
| HRU Bypass | Col 51 `HRU Bypass Damper` | % | 无颜色 |

**Dryer (4 张)**:
| 卡片 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Dryer Feed | Col 7 `Dryer out feed t/h` | t/h | Dryer Feed 阈值 |
| Outlet Moisture | Col 5 `Moisture % Actual Value at Dryer Outlet` | % | Dryer Moisture 阈值 |
| Dry Silo 1 | Col 8 `Dry Silo 1 Level %` | % | 无颜色 |
| Dry Silo 2 | Col 9 `Dry Silo 2 Level %` | % | 无颜色 |

**Quality 网格 (2×3, 5 个指标 + 1 空格)**:
| 指标 | 数据来源 | 单位 | 颜色 |
|------|----------|------|------|
| Durability | Col 34 `Durability %` | % | Durability 阈值 |
| Bulk Density | Col 33 `Bulk Density g/l` | g/l | Bulk Density 阈值 |
| Pellet Moisture | Col 32 `Pellet Moisture %` | % | Pellet Moisture 阈值 |
| Pellet Temp | Col 35 `Temp of Pellets at cooler` | °C | 无颜色 |
| Avg Length | Col 36 `Average Pellet Length(mm)` | mm | Avg Length 阈值 |

> 注: Pellet Fines % 在 CSV 中不存在，已去掉。

---

## Page 2 — Detailed Operations (`/ops`)

> 详细运营监控页：KPI 卡片行 + 6 面板 + 全数据表。
> 导航按钮: Overview · **Detail** · AI

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] Land Energy — Dashboard                                    │
│        Date: [01-01] → [02-01] [Apply]      🌐[EN|中|FR] ⚙️       │
├──────────────────────────────────────────────────────────────────┤
│ OEE    │ Daily    │ Rate    │ Mills   │ Dryer   │ Events        │
│ — %    │ Out (t)  │ (t/h)   │ Status  │ Feed    │ (24h)         │
│ ░ N/A  │ 324.5    │ 13.7 🟡  │ 2/3 🟢  │ 12.3 🟢  │ 5 ⚠️          │
├──────────────────────────────────────────────────────────────────┤
│ [Tab: Production] [Mill Health] [Dryer] [Quality] [CHP] [Down]  │
├──────────────────────────────────────────────────────────────────┤
│ ┌─ Production & Throughput ──────────────────────────────────┐   │
│ │ [Line: Belt Weigher t/h (Col 51) + 20 t/h target]         │   │
│ │ [Line: Dryer Out Feed t/h (Col 8)]                         │   │
│ │ [Big Number: Shift/Daily Total]                            │   │
│ │ [Bar: Pellet Silo 1/2/3 (tonnes)]                         │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Mill Health & Load ───────────────────────────────────────┐   │
│ │ [●]M1:Running [●]M2:Running [●]M3:Stopped                 │   │
│ │ [Gauge×3: Amps] [Line: Amps trend] [Bar: kWh/t]           │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Dryer & Feed ─────────────────────────────────────────────┐   │
│ │ [Tank: Silo1 67%] [Tank: Silo2 38%]                       │   │
│ │ [Line: Outlet Moisture Actual vs Displayed]                │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Quality Control ──────────────────────────────────────────┐   │
│ │ [Cards: Durability/Moisture/Density/Length]                 │   │
│ │ [Line: Quality trends]                                     │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ CHP & Energy ─────────────────────────────────────────────┐   │
│ │ [Gauge: Turbine kW] [Line: Furnace Temp + Thermal Oil]     │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Downtime & Events ────────────────────────────────────────┐   │
│ │ [Table: Recent 10] [Pareto: Fault Cat] [Bar: Area]         │   │
│ └────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────┤
│ Full Data Table (52 cols, scrollable, sortable)                  │
└──────────────────────────────────────────────────────────────────┘
```

### P2 KPI 卡片定义

| 卡片 | 数据来源 | 颜色逻辑 |
|------|----------|----------|
| OEE | 无 | 固定灰色，显示 "— %" |
| Daily Output | Col 45 (当日最新值 - 当日起始值) | 无颜色 |
| Rate (t/h) | Col 51 最新记录 | 按 Belt Weigher 阈值着色 |
| Mills Status | 3 台磨机 Amps >50 判定 | 全部运行=🟢, 部分=🟡, 全停=🔴 |
| Dryer Feed | Col 8 最新值 | 按 Dryer Out Feed 阈值着色 |
| Events (24h) | Events_Log 过去 24h 计数 | >10=🔴, 5-10=🟡, <5=🟢 |

---

## Page 3 — AI Analytics Placeholder (`/ai`)

> AI 占位页：伪数据面板 + 灰色 overlay。
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
│ ⚠️ Requires more historical data. Expected: Q3 2026              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 设计原则
1. 深色主题 SCADA 风格 (Grafana/MachineMetrics)
2. 关键数字 2 米外可读（KPI 值 ≥ 48px, 总览页 52px）
3. 🟢🟡🔴 全局统一语义
4. Gauge 用于有明确上下限的参数
5. Tank Level 用于 Silo 液位
6. Pareto 用于停机分析
7. 上游/下游产量双线对比

---

## 页面路由

| 页面 | 路径 | 导航按钮 | 内容 |
|------|------|---------|------|
| P1 KPI 总览 | `/` | Overview | 12 KPI 卡片 + Quality 2×3 网格 |
| P2 详细运营 | `/ops` | Detail | KPI 行 + 6 面板 + 全数据表 |
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
- [ ] Production 组: 4 张大字 KPI 卡片
- [ ] Energy 组: 4 张大字 KPI 卡片
- [ ] Dryer 组: 4 张大字 KPI 卡片
- [ ] Quality 网格: 2×3 布局，5 个指标有数据（无 Fines）
- [ ] KPI 值字体 ≥ 52px，醒目可读
- [ ] 阈值颜色正确 (Rate/Mills/Turbine/Furnace/Dryer/Moisture/Quality)
- [ ] DateRange 联动刷新所有卡片

### P2 详细运营 (数据)
- [ ] OEE 灰色占位，不计算
- [ ] KPI 卡片数值匹配 CSV（可抽查）
- [ ] 磨机状态灯正确 (Amps>50=Running)
- [ ] Dry Silo = Tank Level (%)
- [ ] Pellet Silo = 柱状图 (吨)
- [ ] 所有 🔴 参数有颜色指示
- [ ] 底部 52 列全数据表
- [ ] Events_Log 正确显示

### P2 Production 精确性
- [ ] Col 51 (Belt Weigher) 趋势图标题明确
- [ ] Col 8 (Dryer Feed) 趋势图标题明确
- [ ] 两条线不混淆

### 阈值面板
- [ ] ⚙️ 可打开设置面板
- [ ] 16 个参数可调
- [ ] 调整即时生效
- [ ] Reset 恢复默认
- [ ] 持久化到 thresholds.json

### 三语
- [ ] EN/中/FR 切换正常
- [ ] 所有标题/按钮/Tooltip 已翻译
- [ ] 无错位截断
- [ ] 默认 English

### P3 AI Placeholder
- [ ] 4 个 Placeholder + "Coming Soon"
- [ ] 面板标题三语
