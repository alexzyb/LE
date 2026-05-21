# Scope, Constraints & Design Principles

> 本文档定义项目边界（做什么/不做什么）、每个面板的具体内容、技术约束和设计原则。
> 写任何新功能或面板前，先对照此文档确认是否在 scope 内。

---

## 1. In Scope — 完整功能清单

### 1.1 基础设施
- **本地 SQLite 数据库** (`land_energy.db`): BG 实时 CSV 由 `ingest.py` 增量写入 `live_data` 表，支持时间范围筛选查询
- **三语支持 (i18n)**: EN / 中文 / Français，顶栏切换器，所有 UI 文本均翻译（详见 `docs/i18n-spec.md`）
- **阈值设置面板**: 4 个有效参数的 🟢🟡🔴 颜色边界可通过 UI 实时调整（详见 `docs/thresholds.md`）
- **Light/Dark 主题切换**: 顶栏 ☀️/🌙 按钮，CSS 变量驱动，偏好保存到 localStorage
- **Logo**: 从 https://www.land-energy.com/ 获取，放置在 Dashboard 左上角

### 1.2 Page 1 — KPI 总览 (`/`)

> 首页 Landing Page，大字体 KPI 卡片，一眼总览工厂状态。
> **Phase 8 更新**: 数据源切换为 BG 实时 CSV。Energy/Dryer/Quality 无 BG 数据，已移除。

**4 大类 KPI (共 14 个)**:

| 分类 | 卡片 1 | 卡片 2 | 卡片 3 | 卡片 4 |
|------|--------|--------|--------|--------|
| Production | Daily Output (t) | Hourly Rate (t/h) | Mills Running (x/3) | YTD Output (t) |
| Mill Status | Mill 1 Amps (A) | Mill 2 Amps (A) | Mill 3 Amps (A) | — |
| Pellet Silo | Silo 1 (% 液位罐) | Silo 2 (% 液位罐) | Silo 3 (% 液位罐) | — |
| Dispatch (行1) | Daily Bagging (t) | Daily Truck (t) | — | — |
| Dispatch (行2) | YTD Bagging (t) | YTD Truck (t) | — | — |

> **YTD（本年累计）**: Production / Bagging / Truck 的第二行卡片显示**当前日历年**的累计产量,而非历史全部累计。因数据是累计计数器,年产量 = **当年最后一个值 − 前一年最后一个值** (`get_year_total`);当前年 = 最新值 − 上一年末值(即 1月1日→今天)。到 2027 年自动显示 2027 的 YTD。计数器跨年重置时回退年内 last−first,仍为负则显示"—"。Overview 页固定显示当前年（无年份选择）。

**Pellet Silo 显示**: 使用 `_ov_tank()` 液位罐组件（与 Dry Silo 相同风格），Fuel_Level 吨数 → 百分比换算。

**设计要求**:
- KPI 数值字体 ≥ 52px，2 米外可读
- 左侧彩色边框表示阈值状态 (🟢🟡🔴)
- Pellet Silo 液位罐带阈值颜色填充
- DateRange 联动刷新全部卡片

### 1.3 Page 2 — Detailed Operations (`/ops`)

> **Phase 8 更新**: 面板从 6 个改为 4 个，移除无 BG 数据的 Dryer/Quality/CHP/Downtime。

**顶栏**:
- Land Energy Logo + 工厂名 "Girvan Pellet Plant"
- Date Range Picker（首屏默认显示**最近 24 小时**以加快加载；picker 上下限仍按数据库实际范围；可手动选任意区间）
- 🌐 语言切换器 (EN | 中 | FR)
- ⚙️ 阈值设置按钮（打开 Modal/Sidebar）
- Grafana 风格时间控制: 快速范围 (1m/30m/6h/24h/7d/1M/6M) + 自动刷新 (Off/5s/30s/1min)

**KPI 卡片行** (4 张卡片) — **⚠️ LEGACY: 已在 Phase 8 中移除（BG 数据不覆盖 OEE）。代码中保留 `# LEGACY` 注释，不排除未来恢复。**

| 卡片 | 数据来源 | 颜色 |
|------|----------|------|
| OEE % | **无计算** — 灰色占位，显示 "— %"，底注 "Insufficient Data" | 固定灰色 |
| Daily Output (t) | Totaliser 累计差值（当日最新 - 当日起始） | 无颜色 |
| Rate (t/h) | `Total tons passed belt weigher (hour)` 最新记录 | 按 Belt Weigher 阈值 |
| Mills Status | 3 台磨机 Amps > 50A = Running → 显示 "2/3 Running" | 全运行🟢 部分🟡 全停🔴 |

**分区面板** (4 个面板):

#### Panel 1: Production & Throughput（产量与生产率）
- **趋势线**: `Total tons passed belt weigher (hour)` — 含 20 t/h 水平目标参考线
- **YTD Output 大数卡 + 年份下拉**: 显示选定年份的累计产量 (`get_year_total` = 当年末 − 前一年末)，默认当前年；下拉**只列有产量数据的年份**，历史年份查看整年总量
- **Pellet Silo 液位罐 (×3)**: 百分比 tank overlay（仿 Dry Silo 风格），带阈值颜色（全局范围）

#### Panel 2: Mill Health & Load（磨机健康与负载）
- **3 台磨机状态指示灯**: Running (绿) / Stopped (灰)，基于 Load Amps > 50A
- **Load Amps Gauge ×3**: 每台磨机一个半圆仪表盘，颜色来自阈值
- **Amps 趋势叠加图**: 3 台磨机的 Load Amps 折线图，不同颜色区分
- **Feeder % 趋势图**: 3 台磨机的进料速度趋势
- **Roller Temperature L/R**: 左/右各一图 (各 3 线)，操作员可对比 L vs R 差异
- **Mill Energy 趋势**: 3 台磨机的累计 kWh 折线图（替换旧的 kWh/t，BG 提供累计值非比率）

> **独立时间范围**: Pellet Silo 和 Dispatch 三个趋势图共用一个独立的时间范围下拉选择器（`sd-range-select`，默认 **6M**，选项 24h/7d/1M/6M/1Y），与顶栏全局时间范围（控制 Production/Mill）分离。运营方希望 Mill 看短周期（如 24h），而料仓/出货看更长周期趋势。

#### Panel 3: Pellet Silo（颗粒料仓）— 新增
- **Silo Level 时间趋势**: Silo 1/2/3 百分比折线图 + 背景阈值色带 (红/黄/绿/黄/红)（独立范围）
- **Infeed Totaliser 趋势**: 各仓累计进料吨数折线图 (×3)（独立范围）

#### Panel 4: Dispatch（出货）— 新增
- **累计趋势图**: Bagging + Truck Totaliser 折线图，2 条线（独立范围）

**~~Panel 3-6 已移除~~**: Dryer/Quality/CHP/Downtime（BG 未覆盖，待 BG 增加数据点后恢复）

### 1.4 Page 3 — AI Analytics Placeholder (`/ai`)

标题: "AI Predictive Analytics — Coming Soon"

| 占位面板 | 伪造内容 |
|----------|----------|
| **Production Forecast** | 未来 24h 产量预测的伪造趋势线 + ±15% 置信区间阴影带 |
| **Fault Prediction** | 伪造卡片: "Next: Mill 2 Blockage, ETA: ~14h, Confidence: 72%" |
| **Anomaly Detection** | 伪造时间线，上面标记 3-4 个异常点 |
| **Root Cause Analysis** | 伪造 Sankey 图或树形图 |

- 每个面板带**灰色半透明 overlay**
- Overlay 上显示: "需要更多历史数据来训练模型 / Requires additional historical data"
- 底部横幅: "⚠️ Expected availability: Q3 2026"
- 面板标题支持三语

---

## 2. Out of Scope

**以下功能明确不做：**

- **OEE 综合指标计算**（不做 Availability x Performance x Quality）
- 真实 AI/ML 模型训练与推理（Page 3 / AI 仅占位）
- 用户认证 / 多角色权限
- 移动端响应式适配（Desktop 优先即可）
- 额外的数据导出功能（Excel/PDF 报表生成）
- **Dryer/Quality/CHP/Events 面板** — BG 未覆盖，待 BG 增加数据点后恢复（在 `column_map.py` 加一行映射即可）

---

## 3. 技术约束

### 技术栈（锁定）
- **Python + Dash (Plotly)** — 理由: 工业 Dashboard 生态成熟、Gauge/Tank/Pareto 图表类型丰富、Callback 机制天然支持阈值联动和语言切换
- **SQLite** — 本地文件 `land_energy.db`
- **i18n**: `translations.py` 字典 + Dash Callback + `dcc.Store`（或 URL `?lang=zh`）
- **运行**: `python src/app.py` → `http://localhost:8050`

### 性能要求
| 操作 | 要求 |
|------|------|
| 首次加载 | < 3 秒 |
| 时间范围筛选 (1m/30m/6h/24h) | < 1 秒刷新（原始 30s 粒度） |
| 时间范围筛选 (7d/1M/6M) | < 2 秒刷新（自动降采样，≤3,000 行） |
| 语言切换 | < 0.5 秒（纯字符串替换，不重新查询数据） |
| 阈值调整 | < 1 秒全图表颜色刷新 |

### 不能改的东西
- BG CSV 原始列名 / value_id（映射在 `src/column_map.py`）
- 数据时间范围由数据库实际数据决定（不再硬编码）

---

## 4. 设计原则

### 视觉风格
- **深色主题 (Dark Theme)**: 工业 SCADA 标准，参考 Grafana / MachineMetrics
- **主色调**: 深灰背景 `#1a1a2e` / 卡片 `#16213e` / 绿 `#0f9b58` / 黄 `#f4b400` / 红 `#db4437`
- **字体**: **Roboto Mono**（等宽，数字显示）+ 无衬线体（标题），大数字用粗体
- **图表**: Plotly + 自定义暗色模板（plotly_dark 基础上微调）

### 布局原则
1. **"Scoreboard" 顶部**: 关键 KPI 数字居中大字体，操作员**站在 2 米外**能看清
2. **信息密度高但不拥挤**: 控制室显示器一屏尽量多看，但留足呼吸空间
3. **i18n 布局**: 中文较短、法语较长，所有容器需留足弹性空间，切换后不错位不截断

### 图表类型选择指南
| 场景 | 推荐图表 | 示例 |
|------|----------|------|
| 有明确上下限的瞬时值 | **Gauge/仪表盘** | Load Amps (Mill 1/2/3) |
| 液位/库存百分比 | **Tank Level（水箱填充图）** | Pellet Silo 1/2/3 (%) |
| 时间序列趋势 | **Line Chart** | 产量 t/h, Roller Temp, Amps, Energy |
| 单值+状态色 | **KPI 卡片** | Daily Output, Rate, Mills Status |
| 多线对比 | **多色折线同图** | 3 台 Mill Amps 叠加 |

### 颜色纪律
- 🟢🟡🔴 全局统一语义 — **永远不能让红色代表"好"**
- 状态灯: Running = 绿, Stopped = 灰
- 阈值色带: 所有参数统一使用 thresholds.md 定义的颜色边界
