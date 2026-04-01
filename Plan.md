# Plan.md — Land Energy Dashboard 开发计划

> ⚠️ **每次启动必读此文件，每轮任务结束后必须更新。**

## 📅 最后更新: 2026-03-31
## 🏁 当前阶段: Phase 8 🔄 — Live Data Integration

---

## 已完成阶段（摘要）

| Phase | 内容 | 完成日期 |
|-------|------|----------|
| 0 | 规划 — 数据分析 + 64 列映射 + 文档拆分 | 2026-02-17 |
| 1 | 数据层 — config.py + translations.py + init_db.py (CSV→SQLite, 745行/52列) | 2026-02-18 |
| 2 | Dashboard 骨架 — Dash app + 深色主题 + 3页路由 + 三语 + KPI卡片 | 2026-02-18 |
| 3 | Page 1 面板 — data.py + charts.py (15图) + 6面板全接入 + DateRange联动 | 2026-02-18 |
| 3.5 | KPI 总览页 — 12张大卡片 + Quality网格 + 字体放大 + 3页导航 | 2026-02-23 |
| 4 | 阈值设置 — Settings Modal (16参数/44输入) + JSON持久化 + 全局颜色刷新 | 2026-02-23 |
| 5 | AI Placeholder — 4个伪数据 Plotly 图表 + overlay + Coming Soon | 2026-02-24 |
| 6 | 打磨交付 — Logo + README + 30+验收项 PASS + Render.com 部署配置 | 2026-02-24 |
| 7 | Grafana 时间控制 — 快速范围按钮(1m/30m/1h/6h/24h) + 自动刷新(Off/5s/30s/1min) | 2026-02-25 |

> 各阶段详细记录和 bugfix 历史见 git log。

---

## Phase 8: Live Data Integration 🔄

> **决策 (2026-03-31)**: 完全替换旧 Demo 数据，只用 BG 实时数据管道。不做双模式切换。
> **核心决策**: SQLite 默认 | 全部写入 DB、显示时过滤 | Fuel_Level 上限 5000 吨
> **技术文档**: `docs/phase8-live-data.md`（架构、数据流、清洗规则、页面布局、部署方案）
> **列映射注册表**: `src/column_map.py`（BG value_id → Dashboard 列名，单一真相源）

### Phase 8a — 基础层 + 文档
- [x] 创建 `src/column_map.py`：25 个 value_id 完整映射 + 清洗规则
- [x] 更新 `column_map.py`：Fuel_Level max→5000, Mill Amps→800, Roller→250, Feeder→120, 加 SILO_MAX_CAPACITY + tons_to_pct()
- [x] 更新 `docs/phase8-live-data.md`：SQLite 默认 + 显示时过滤 + 页面布局重组方案（§9）
- [x] 更新 `CLAUDE.md` + `Plan.md`：反映 Phase 8 决策和进度
- [x] 修改 `src/config.py`：加 `DATABASE_URL` / `BG_EXPORT_DIR` 环境变量 + `pellet_silo_level` 阈值
- [ ] 修改 `src/data.py`：查询 `live_data` 表 + 显示时过滤 + SQLite/PostgreSQL 双支持 + `get_date_range()`（已完成 live_data优先 + 显示时过滤 + get_date_range；PostgreSQL 原生驱动待补）
- [ ] 在 SQLite 中创建 `live_data` 表（由 ingest.py 首次运行自动建表）

### Phase 8b — 采集引擎
- [x] 创建 `src/ingest.py`：CSV 尾部增量读取 → 基本校验 → 30s 重采样 → pivot 宽表 → UPSERT（不做范围清洗）
- [x] 创建 `ingest_state.json` 状态管理（字节偏移追踪 + 崩溃恢复）
- [x] 用 `BaumgartnerData/*.csv` 样本数据测试，验证宽表列名正确

### Phase 8c — Dashboard 对接 + 页面重组
- [ ] 修改 `src/app.py`：默认时间范围自动适配 + 页面布局重组（见 §9）**（默认时间范围自动适配已完成；布局已完成首版，待联调）**
- [x] Overview 页: 移除 Energy/Dryer/Quality section, 新增 Mill Status + Pellet Silo 液位罐 + Dispatch
- [x] Detail 页: 移除 Dryer/Quality/CHP/Downtime panel, 新增 Pellet Silo + Dispatch panel
- [x] 修改 `src/charts.py`：fig_pellet_silos() 改百分比液位罐 + 新增 fig_silo_level_trend/fig_dispatch_trend + 缺失列保护
- [x] 修改 `src/translations.py`：加 Pellet Silo + Dispatch + "No data" 翻译 key
- [ ] 端到端测试：ingest 导入样本 → 启动 Dashboard → 确认图表正常

### Phase 8d — 生产部署
- [ ] Windows VM + SQLite (默认) + 本地 BG CSV 目录
- [ ] 部署流程: GitHub → VM git pull → 运行
- [ ] 部署细节见 `docs/phase8-live-data.md` §8

---

## 已知风险

| # | 问题 | 状态 |
|---|------|------|
| 1 | BG 只覆盖 17/52 列，Dryer/Quality/CHP 面板无数据 | 已知: 显示空，待 BG 增加数据点 |
| 2 | BG 样本数据含异常（Silo 归零、负值、天文数字） | 已分析: 清洗规则定义在 column_map.py |
| 3 | BG 样本时间范围是 2022-2024 历史数据 | 需处理: app.py 默认时间自动适配 |
| 4 | OEE 不计算 | 已决: 灰色占位 |

---

## Session Log

| 日期 | Phase | 完成内容 |
|------|-------|----------|
| 2026-02-17 | 0 | 规划完成, 文档拆分 |
| 2026-02-18 | 1-3 | 数据层 + Dashboard 骨架 + 15 图表面板，全部接入真实数据 |
| 2026-02-23 | 3.5-4 | KPI 总览页 + 阈值设置面板 + gauge 硬编码修复 |
| 2026-02-24 | 5-6 | AI 占位页 + 打磨交付 + 阈值颜色修复 + Dry Silo 液位罐 + Render 部署 |
| 2026-02-25 | 7 | Grafana 风格时间控制 + 自动刷新 |
| 2026-03-31 | 8 | Live Data Integration 启动 — 决策: 弃用旧 Demo 数据; column_map.py 已建; 技术文档已写; 待完成: config→data→ingest→app |
| 2026-04-01 | 8a | column_map.py 清洗规则更新 + Silo 容量 3500t; phase8-live-data.md 完善(§9 页面布局); **全部 docs/ 更新**: scope-and-design(面板6→4), layout-spec(重写布局+验收), thresholds(16→4有效+示例修正), i18n(移除无用key+新增13), column-map+data-analysis(归档), background+deployment(小改); CLAUDE.md+README.md 同步; **全量一致性 doublecheck 完成**; 移除 Avg Amps (14→13 KPI); timestamp_utc 说明; 部署修正: Ubuntu→Windows VM, live-data-solution 弃用 |
| 2026-04-01 | 8c | 回退 `/dashboard` 试验页改动；新增 `data.get_date_range()` 并接入 `app.py` DatePicker，默认时间范围随数据库真实最小/最大时间自动适配（覆盖 BG 样本历史时间风险） |
| 2026-04-01 | 8c | 首版页面重组落地：Overview 切为 Production/Mill/Pellet Silo/Dispatch；Detail 切为 4 面板；新增 silo 百分比趋势和 dispatch 趋势图；三语 key 补充完成，待 ingest 联调与端到端验收 |
| 2026-04-01 | 8a | config/data 首轮落地：新增 DATABASE_URL/BG_EXPORT_DIR 与 pellet_silo_level 阈值；data 层改为 live_data 优先、shift_protocol 回退，并在显示时应用 column_map 清洗规则 |
| 2026-04-01 | 8b | 新增 `src/ingest.py`（增量偏移 + 30s重采样 + 宽表UPSERT）；生成 `src/ingest_state.json`；完成 BaumgartnerData 样本导入验证，`live_data` 成功写入 86,698 行 |
