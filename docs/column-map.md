# Column Map — Shift_Protocol_date_time_merged.csv

> **LEGACY 文档** — 此文件描述的是旧 Shift Protocol 64 列映射。
> Phase 8 起，列映射已迁移到 `src/column_map.py`（BG 实时数据 25 列）。
> 此文件仅作历史参考，不再更新。

> 64 列完整映射。构建任何图表/查询前请核对此文档。

## ⏱ 全局时间戳 — Col 0
| Col | 列名 | 单位 | 说明 |
|-----|-------|------|------|
| 0 | Date Time | DD/MM/YYYY HH:MM:SS | **全局主键**。所有图表 X 轴、所有查询时间筛选均基于此列。 |

**空白分隔列 (跳过)**: Col 1, 14, 18, 24, 30, 36, 38, 44, 55

---

## A. Dryer（烘干机） — Col 2–13
| Col | 列名 | 中文 | 单位 | 优先级 |
|-----|-------|------|------|--------|
| 2 | Dryer Tonnage | 湿料进料速率 | t/h | 🟡 |
| 3 | Moisture % Displayed Value at Dryer Inlet | 进口水分(显示) | % | ⚪ |
| 4 | Dryer bed Temp° C | 烘干床温度 | °C | 🟡 |
| 5 | Moisture % Displayed Value at Dryer Outlet | 出口水分(显示) | % | 🔴 |
| 6 | Moisture % Actual Value at Dryer Outlet | 出口水分(实际) | % | 🔴 |
| 7 | Dryer belt speed % | 网带速度 | % | ⚪ |
| 8 | Dryer out feed t/h | 烘干出料流速 | t/h | 🔴 |
| 9 | Dry Silo 1 Level % | 干料仓1液位 | % | 🔴 |
| 10 | Dry Silo 2 Level % | 干料仓2液位 | % | 🔴 |
| 11 | Dryer 1/2 fan speed | 风机速度 | — | ⚪ |
| 12 | Fresh Air Temp° C | 环境气温 | °C | ⚪ |
| 13 | Water Addition at Dryer | 烘干机补水 | — | 🟡 |

## B. 未分类关键工艺参数 — Col 15–17
| Col | 列名 | 中文 | 单位 | 优先级 |
|-----|-------|------|------|--------|
| 15 | Valve position open at % | 水阀开度 | % | 🔴 |
| 16 | Pellet Mill Moistures % | 入磨水分 | % | 🔴 |
| 17 | Press Hopper Temperature | 料斗温度 | °C | 🟡 |

## C. Pellet Mill 1/2/3（制粒机）— Col 19–35
**Mill 1**: Col 19–23 | **Mill 2**: Col 25–29 | **Mill 3**: Col 31–35

| 列名模式 | 中文 | 单位 | 优先级 |
|-----------|------|------|--------|
| Press [x] - Left Roller Temperature | 左压辊温度 | °C | 🟡 |
| Press [x] - Right Roller Temperature | 右压辊温度 | °C | 🟡 |
| Press [x] - Load Amps | 主电机电流 | A | 🔴 |
| Press [x] - Feeder % | 喂料速度 | % | 🔴 |
| Press [x] kWh/t | 单吨能耗 | kWh/t | 🟡 |

**状态判定**: `IF Load Amps > 50 THEN "Running" ELSE "Stopped"`

## D. Main Filter — Col 37
| Col | 列名 | 中文 | 单位 | 优先级 |
|-----|-------|------|------|--------|
| 37 | Main Filter kP | 过滤器压差 | kPa | 🟡 |

## E. Quality（质量）— Col 39–43
| Col | 列名 | 中文 | 单位 | 优先级 |
|-----|-------|------|------|--------|
| 39 | Pellet Moisture % | 成品水分 | % | 🔴 |
| 40 | Bulk Density g/l | 堆积密度 | g/l | 🟡 |
| 41 | Durability % | 耐久度 | % | 🔴 |
| 42 | Temp of Pellets at cooler | 冷却温度 | °C | 🟡 |
| 43 | Average Pellet Length(mm) | 平均长度 | mm | 🟡 |

## F. Throughput（产量）— Col 45–54
| Col | 列名 | 中文 | 单位 | 优先级 |
|-----|-------|------|------|--------|
| 45 | Total Pellets passed belt weigher (cumlative) | 累计总产量 | t (累计) | 🔴 |
| 46 | Total pellet to totes hopper (cumulative) | 吨袋累计量 | t (累计) | ⚪ |
| 47 | Silo strain gauge level (tonnes) | 缓冲仓称重 | t | 🟡 |
| 48 | Pellet Silo Level 1 Readout | 成品仓1库存 | t | 🟡 |
| 49 | Pellet Silo Level 2 Readout | 成品仓2库存 | t | 🟡 |
| 50 | Pellet Silo Level 3 Readout | 成品仓3库存 | t | 🟡 |
| 51 | Total tons passed belt weigher (hour) | 成品实时产量 | t/h | 🔴 |
| 52 | Total tons per shift | ❌ 损坏 | — | ⚪ |
| 53 | Total tons per day to silo | ❌ 损坏 | — | ⚪ |
| 54 | Total tonnes to tote hopper (shift) | ❌ 损坏 | — | ⚪ |

⚠️ Col 52–54: `#REF!`/`#VALUE!` 错误，从 Col 45 累计值自行计算
⚠️ Col 51: 6 行异常值 (|值|>50)，过滤为 NULL

## G. CHP（热电联产）— Col 56–63
| Col | 列名 | 中文 | 单位 | 优先级 |
|-----|-------|------|------|--------|
| 56 | Furnace O2% | 炉膛含氧量 | % | 🟡 |
| 57 | Furnace Temp | 炉膛温度 | °C | 🔴 |
| 58 | Furnace Pressure | 炉膛负压 | Pa | ⚪ |
| 59 | Thermal Oil OUT | 导热油出口温度 | °C | 🔴 |
| 60 | Turbine Generated Power kW | 涡轮发电功率 | kW | 🔴 |
| 61 | Flue Gas Fan | 烟气风机 | % | ⚪ |
| 62 | Primary Air Fan | 一次风机 | % | ⚪ |
| 63 | HRU Bypass Damper | 热回收旁路挡板 | — | 🟡 |

---

## ⚠️ 易混淆的两条产量线
| # | 参数 | CSV 列 | 含义 | 数据特征 |
|---|------|--------|------|----------|
| 上游 | Dryer Out Feed | Col 8 `Dryer out feed t/h` | 烘干机出料速度 | avg=12.3, range 9.4–14.7 |
| 下游 | Belt Weigher | Col 51 `Total tons passed belt weigher (hour)` | 最终成品产量 | avg=11.4, range 0–17.0 |

**Dashboard 中必须分别展示，图表标题必须标注数据来源列名。**

---

## 辅助数据文件列结构

### Events_Log.csv（~200+ 行）
| 列名 | 中文 | 说明 |
|------|------|------|
| Date | 日期 | DD/MM/YYYY |
| Time | 时间 | H:MM:SS 或 HH:MM:SS (格式不统一，需兼容) |
| Duration | 停机时长 | H:MM:SS 格式，init_db 需转换为分钟数 |
| Area | 区域 | Dryer / Pellet Mill / CHP / Cooler 等 |
| Fault Category | 故障类别 | Mechanical / Electrical / Process / Operator 等 |
| Asset ID | 资产编号 | P1.505 / Mill 2 等 |
| Event Description | 事件描述 | 操作员手写英文描述（不翻译） |

> 用途: Downtime 面板 (Pareto 用 Fault Category, 柱状图用 Area, 表格显示全部列)
> KPI "Events (24h)" = 按 Date 过滤后的行数

### Meter_Readings.csv（~32 行）
| 列名 | 说明 |
|------|------|
| Date | 日期 |
| 其他列 | 电力/热力/水等能源表日读数 |

> 本期 Demo **不深度使用**此文件。导入 SQLite 备用，无面板直接引用。
