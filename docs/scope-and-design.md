# Scope, Constraints & Design Principles

> 本文档定义项目边界（做什么/不做什么）、每个面板的具体内容、技术约束和设计原则。
> 写任何新功能或面板前，先对照此文档确认是否在 scope 内。

---

## 1. In Scope — 完整功能清单

### 1.1 基础设施
- **本地 SQLite 数据库** (`land_energy.db`): 导入 3 个 CSV，支持时间范围筛选查询
- **三语支持 (i18n)**: EN / 中文 / Français，顶栏切换器，所有 UI 文本均翻译（详见 `docs/i18n-spec.md`）
- **阈值设置面板**: 16 个参数的 🟢🟡🔴 颜色边界可通过 UI 实时调整（详见 `docs/thresholds.md`）
- **Logo**: 从 https://www.land-energy.com/ 获取，放置在 Dashboard 左上角

### 1.2 Page 1 — KPI 总览 (`/`)

> 首页 Landing Page，大字体 KPI 卡片，一眼总览工厂状态。

**4 大类 KPI 卡片 (共 12 张)**:

| 分类 | 卡片 1 | 卡片 2 | 卡片 3 | 卡片 4 |
|------|--------|--------|--------|--------|
| Production | Daily Output (t) | Hourly Rate (t/h) | Mills Running (x/3) | Period Total (t) |
| Energy | Turbine Power (kW) | Furnace Temp (°C) | Thermal Oil OUT (°C) | HRU Bypass (%) |
| Dryer | Dryer Feed (t/h) | Outlet Moisture (%) | Dry Silo 1 (%) | Dry Silo 2 (%) |

**Quality 2×3 网格** (5 个指标):
- Row 1: Durability % | Bulk Density g/l | Pellet Moisture %
- Row 2: Pellet Temp °C | Avg Length mm | (空)
- 注: Pellet Fines % 在 CSV 中无此列，已去掉

**设计要求**:
- KPI 数值字体 ≥ 52px，2 米外可读
- 左侧彩色边框表示阈值状态 (🟢🟡🔴)
- Quality 网格每格带颜色边框
- DateRange 联动刷新全部卡片

### 1.3 Page 2 — Detailed Operations (`/ops`)

**顶栏**:
- Land Energy Logo + 工厂名 "Girvan Pellet Plant"
- Date Range Picker（默认 2026-01-01 ~ 2026-02-01）
- 🌐 语言切换器 (EN | 中 | FR)
- ⚙️ 阈值设置按钮（打开 Modal/Sidebar）

**KPI 卡片行** (6 张卡片):
| 卡片 | 数据来源 | 颜色 |
|------|----------|------|
| OEE % | **无计算** — 灰色占位，显示 "— %"，底注 "Insufficient Data" | 固定灰色 |
| Daily Output (t) | Col 45 累计值差值（当日最新 - 当日起始） | 无颜色 |
| Rate (t/h) | Col 51 `Total tons passed belt weigher (hour)` 最新记录 | 按 Belt Weigher 阈值 |
| Mills Status | 3 台磨机 Amps > 50A = Running → 显示 "2/3 Running" | 全运行🟢 部分🟡 全停🔴 |
| Dryer Feed (t/h) | Col 8 `Dryer out feed t/h` 最新值 | 按 Dryer Feed 阈值 |
| Events (24h) | Events_Log 过去 24h 事件计数 | >10🔴 5-10🟡 <5🟢 |

**分区面板** (6 个面板，可折叠或 Tab 切换):

#### Panel 1: Production & Throughput（产量与生产率）
- **趋势线 1**: `Total tons passed belt weigher (hour)` (Col 51) — 含 20 t/h 水平目标参考线
- **趋势线 2**: `Dryer out feed t/h` (Col 8) — 与趋势线 1 同图或上下排列
- ⚠️ 两条线的图表标题必须标注精确数据来源列名，不可混淆
- **累计产量大数卡**: 从 Col 45 差值计算的班次/日产量
- **Pellet Silo 1/2/3 库存柱状图**: Col 48/49/50，单位=吨，柱状图

#### Panel 2: Mill Health & Load（磨机健康与负载）
- **3 台磨机状态指示灯**: Running (绿●) / Stopped (灰●)，基于 Load Amps > 50A
- **Load Amps Gauge ×3**: 每台磨机一个仪表盘，颜色来自阈值（可通过 Settings 调整）
- **Amps 趋势叠加图**: 3 台磨机的 Load Amps 在同一张图上，不同颜色区分
- **Feeder % 对比**: 3 台磨机的 Feeder % 柱状/趋势对比
- **Roller Temperature 左右差值监控**: 关注左右压辊温差异常
- **kWh/t 能耗对比柱状图**: 3 台磨机的单吨能耗对比

#### Panel 3: Dryer & Feed（烘干与供料）
- **Dry Silo 1/2 Tank Level 可视化**: Col 9/10，单位=百分比 %，用"水箱填充"图形
- **出口水分趋势 (双线)**: Col 5 Displayed vs Col 6 Actual 同图对比

#### Panel 4: Quality Control（质量控制）
- **4 个指标卡片** (带颜色状态):
  - Durability % (含 97.5% 参考线)
  - Pellet Moisture % (含 10% 参考线)
  - Bulk Density g/l
  - Average Pellet Length mm
- **Quality 趋势图**: 以上 4 指标的时间序列

#### Panel 5: CHP & Energy（热电联产与能效）
- **Turbine Power Gauge**: Col 60，仪表盘，颜色来自阈值
- **Furnace Temp 趋势**: Col 57
- **Thermal Oil OUT 趋势**: Col 59
- **HRU Bypass Damper 状态**: Col 63

#### Panel 6: Downtime & Events（停机与事件）
- **最近事件表格**: Events_Log 最近 10 条，含日期/时间/区域/描述/时长
- **Pareto 图**: 按 Fault Category 降序排列，显示 80/20 分界线
- **停机时间按 Area 柱状图**: 汇总各区域停机分钟数

**底部全数据表**:
- Shift_Protocol 全部 52 列（去除空白和损坏列后），可滚动、可排序、可筛选
- 列名保持 CSV 英文原名（不翻译）

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

## 2. Out of Scope ❌

**以下功能明确不做，Claude Code 不应自行添加：**

- 生产环境部署 / 云端托管
- 真实 SCADA / PLC 数据接入
- 真实 AI/ML 模型训练与推理（Page 3 / AI 仅占位）
- **OEE 综合指标计算**（不做 Availability × Performance × Quality）
- 用户认证 / 多角色权限
- 移动端响应式适配（Desktop 优先即可）
- Meter_Readings.csv 的深度能源分析（仅作为 CHP 面板的补充参考）
- 额外的数据导出功能（Excel/PDF 报表生成）
- 实时数据推送 / WebSocket

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
| 时间范围筛选 | < 1 秒刷新 |
| 语言切换 | < 0.5 秒（纯字符串替换，不重新查询数据） |
| 阈值调整 | < 1 秒全图表颜色刷新 |

### 不能改的东西
- CSV 原始列名（代码中做映射即可）
- 数据时间范围 2026-01-01 ~ 2026-02-01

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
| 有明确上下限的瞬时值 | **Gauge/仪表盘** | Load Amps, Turbine Power |
| 液位/库存百分比 | **Tank Level（水箱填充图）** | Dry Silo 1/2 |
| 库存吨数 | **柱状图** | Pellet Silo 1/2/3 |
| 时间序列趋势 | **Line Chart** | 产量 t/h, 温度, 水分 |
| 停机原因排序 | **Pareto 图** | Fault Category（含 80/20 线） |
| 运行/停机时间线 | **Gantt / 颜色条** | Running(绿) / Down(红) / Idle(黄) |
| 单值+状态色 | **KPI 卡片** | OEE, 产量, 事件数 |
| 上下游对比 | **双线同图** | Dryer Feed (Col 8) vs Belt Weigher (Col 51) |

### 颜色纪律
- 🟢🟡🔴 全局统一语义 — **永远不能让红色代表"好"**
- 状态灯: Running = 绿, Stopped = 灰
- 阈值色带: 所有参数统一使用 thresholds.md 定义的颜色边界
