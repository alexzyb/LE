# Plan.md — Land Energy Dashboard 开发计划

> ⚠️ **每次启动必读此文件，每轮任务结束后必须更新。**

## 📅 最后更新: 2026-04-10
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
> **核心决策**: SQLite 默认 | 全部写入 DB、显示时过滤 | Silo 清洗范围按容量+15%容差 (Silo1: 0-520t, Silo2/3: 0-4000t)
> **技术文档**: `docs/phase8-live-data.md`（架构、数据流、清洗规则、页面布局、部署方案）
> **列映射注册表**: `src/column_map.py`（BG value_id → Dashboard 列名，单一真相源）

### Phase 8a — 基础层 + 文档
- [x] 创建 `src/column_map.py`：25 个 value_id 完整映射 + 清洗规则
- [x] 更新 `column_map.py`：Fuel_Level max→5000, Mill Amps→800, Roller→250, Feeder→120, 加 SILO_MAX_CAPACITY + tons_to_pct()
- [x] 更新 `docs/phase8-live-data.md`：SQLite 默认 + 显示时过滤 + 页面布局重组方案（§9）
- [x] 更新 `CLAUDE.md` + `Plan.md`：反映 Phase 8 决策和进度
- [x] 修改 `src/config.py`：加 `DATABASE_URL` / `BG_EXPORT_DIR` 环境变量 + `pellet_silo_level` 阈值
- [x] 修改 `src/data.py`：查询 `live_data` 表 + 显示时过滤 + SQLite/PostgreSQL 双支持 + `get_db_time_range()`
- [x] 在 SQLite 中创建 `live_data` 表（由 ingest.py 首次运行自动建表）

### Phase 8b — 采集引擎
- [x] 创建 `src/ingest.py`：CSV 尾部增量读取 → 基本校验 → 30s 重采样 → pivot 宽表 → UPSERT（不做范围清洗）
- [x] 创建 `ingest_state.json` 状态管理（字节偏移追踪 + 崩溃恢复）
- [x] 用 `BaumgartnerData/*.csv` 样本数据测试，验证宽表列名正确（250K+ 时间桶导入成功）

### Phase 8c — Dashboard 对接 + 页面重组
- [x] 修改 `src/app.py`：默认时间范围自动适配 + 页面布局重组（见 §9）
- [x] Overview 页: 移除 Energy/Dryer/Quality section, 新增 Mill Status + Pellet Silo 液位罐 + Dispatch
- [x] Detail 页: 移除 Dryer/Quality/CHP/Downtime panel, 新增 Pellet Silo + Dispatch panel
- [x] 修改 `src/charts.py`：fig_pellet_silos() 改百分比液位罐 + 新增 fig_silo_level_trend/fig_dispatch_trend + 缺失列保护
- [x] 修改 `src/translations.py`：加 Pellet Silo + Dispatch + "No data" 翻译 key
- [x] 端到端测试：ingest 导入样本 → 启动 Dashboard → HTTP 200 通过

### Phase 8e — Bug 修复 + 完善 ✅ (2026-04-07 完成)
- [x] 修复 `clean_value` NaN Bug — `v != v` 检查，Period Output 从 0 恢复为 3383t
- [x] 修复降采样逻辑 — 累计列用 `.last()`，瞬时列用 `.mean()`；增加 >1Y: 6h 档；阈值 3000→2000
- [x] 移除 Silo 面板重复 tank 图 + 移除 Full Data Table（25 列均有图表覆盖）
- [x] Silo 阈值拆分: `pellet_silo_level_1` (15/25/85/95%) + `pellet_silo_level_23` (10/20/80/90%)
- [x] Silo 清洗范围按容量拆分: Silo1 0-520t, Silo2/3 0-4000t（原统一 0-5000 太宽）
- [x] Roller Temp diff → `fig_roller_temp_left` + `fig_roller_temp_right` (Mill Health 3×2 网格 + Energy 全宽)
- [x] 文档精简: phase8-live-data.md §9 去重（布局线框图只保留在 layout-spec.md）
- [x] 文档同步: phase8-live-data(降采样表+清洗范围+标题) + layout-spec + scope-and-design + thresholds + i18n-spec + README
- [x] Daily Output Bug — 用 Totaliser 列自身最后日期而非 df 全局最后日期（修复全量范围时显示"—"）
- [x] 快速范围锚点 Bug — 从 DB max 改为 `datetime.now()`（选"过去1分钟"应查真实当前时间，非数据最后时间）

### Phase 8f — 混合频率图表修复 ✅ (2026-04-08 完成)
- [x] **NaN 交叉断线 Bug**: Silo/Infeed/Dispatch 图表在 Mill 30s 数据出现后线条断裂（原因: 小时级数据点被 30s NaN 行隔开，Plotly 默认断线）
  - 修复: 新增 `_sparse_series()` 辅助函数 — 先过滤 NaN 行，再用自适应阈值(3×中位间隔)在真实数据缺口处插入 NaN 断点
  - 影响: Silo Level Trend / Silo Infeed Totaliser / Dispatch Totaliser 三图均已修复
- [x] **tons_to_pct 100% 钳位 Bug**: 超容量读数(如 Silo1=518t/450t=115%)被 `min(100%)` 钳位为 100%
  - 修复: 移除上限钳位，允许显示真实百分比; Y 轴扩展到 120%; 阈值红色带扩展到 120%
- [x] **Bar 图 null 值显示 0%**: 无效数据(如 Silo1=961t 超出 520t 清洗范围)在柱状图显示 0%，易误解为空罐
  - 修复: null 值显示 "N/A"（柱状图 + 概览页罐体卡片）
- [x] **Hover 提示格式 Bug**: `hovermode="x unified"` + 不同 x 轴数据导致 Silo 1 hover 显示 `(Jan 1, 2024, 84.5)` 元组格式
  - 修复: 添加 `hovertemplate` 格式化（Level: `%.1f%%`, Infeed/Dispatch: `%,.0f t`）

### Phase 8g — Totaliser 实线 + Light/Dark 主题切换 + 文档同步 ✅ (2026-04-08 完成)
- [x] **Totaliser 线型**: P2 Production 双轴图青色虚线(`dash="dot"`) → 实线
- [x] **Light/Dark 主题切换**:
  - `config.py`: 新增 `COLOR_SCHEMES` (dark+light) + `get_color_scheme(theme)` + gauge 背景色
  - `style.css`: 80+ 硬编码 hex → CSS 变量 (`var(--le-*)`) + `[data-theme="light"]` 浅色覆盖
  - `app.py`: `dcc.Store("store-theme")` + ☀️/🌙 切换按钮 + clientside callback + theme 参数传递到所有页面/组件
  - `charts.py`: 模块级颜色常量 → `_tc(theme)` 函数 + 所有 23+ `fig_*` 函数添加 `theme` 参数
  - `translations.py`: 新增 `theme_toggle` key
- [x] **对比度改善 (WCAG AA)**:
  - Dark: subtext `#9e9e9e`→`#b0b0b0` (3.5:1→4.8:1), red `#db4437`→`#e05545` (3.2:1→4.0:1 大字体)
  - Light: 全新配色，text/green/yellow/red 均通过 AA (4.5:1+)
- [x] **文档全量同步**: scope-and-design(KPI 14+LEGACY+主题), layout-spec(实线+主题按钮), i18n(theme_toggle), README(KPI 14+LEGACY+主题), CLAUDE.md(LEGACY+主题)

### Phase 8h — VM 部署 + Ingest 引擎修复 ✅ (2026-04-09 完成)
- [x] **VM 部署**: LE 文件夹复制到 Windows VM，BG 实时 CSV 路径 `D:\CSVData\BaumgartnerData`
- [x] **大文件 parse error 修复**: `read_new_rows()` 一次性 `f.read()` 整个 2GB+ 文件导致 Pellet_Mill_2.csv 每次 parse error
  - 根本原因: 将 2GB 字节流解码为单一字符串再传 `pd.read_csv(io.StringIO(...))` 会撑爆 pandas 解析器
  - 修复: 重写为 **分块读取**（`CHUNK_SIZE = 50MB`）— 新增 `read_chunk()` + `_get_header()`; `ingest_once()` 对每个文件循环分块直到 `done=True`
  - 效果: 9 个 CSV 全部成功，总计 ~489 万时间桶导入，内存峰值从 2GB+ 降至 ~500MB
- [x] **错误信息改善**: 原来只打印文件名，现在打印 `type(e).__name__: message + 字节偏移`，便于定位坏行位置
- [x] **时间戳两列说明**: BG CSV 有 `timestamp_utc`（WinCC 实际采集时间，每行递增）和 `sync_timestamp_utc`（CDC 导出批次时间，同批全部相同）；`ingest.py` 使用 `timestamp_utc`，用 `sync_timestamp_utc` 会把所有数据堆在同一点上
- [x] **timestamp format 说明**: BG 格式 `2024-03-22T08:27:00.1910000+00:00`（含纳秒+时区偏移），无法用固定 format 字符串；让 pandas 自动推断是正确做法，UserWarning 无害
- [x] **持续监控模式**: `python ingest.py --source "D:\CSVData\BaumgartnerData"` 默认每 5 秒轮询新增字节（`--interval N` 可调）

### Phase 8k — 日期选择器 Bug 修复 ✅ (2026-04-10 完成)
- [x] **DatePicker max_date_allowed Bug**: 日期选择器上限锁死在 app 启动时的 DB 最大日期，持续注入新数据后仍无法选择今天
  - 根本原因: `_db_max = get_db_time_range()` 是模块级代码，只在 `python app.py` 启动时执行一次，之后不更新
  - 修复: `_picker_max` 改为 `datetime.now() + 1 day`（始终允许选到今天），顶部新增 `from datetime import datetime, timedelta`
  - 影响文件: `src/app.py`（仅此一个文件）

### Phase 8l — 时间戳时区修复 ✅ (2026-05-21 完成)
- [x] **问题**: Dashboard 图表显示 UTC 时间，UK 用户看到的时间比本地时间慢 2 小时
  - 1 小时：BG WinCC 测量时钟未应用夏令时（BST），记录的 `timestamp_utc` 比真实 UTC 慢 1 小时（待 Christian 修复 BG 服务器时区）
  - 1 小时：Dashboard 直接显示 UTC，UK 夏令时（BST = UTC+1）导致固有 1 小时差
- [x] **诊断**: 对比 CSV 的 `sync_timestamp_utc`（正确实时）与 `timestamp_utc`（慢 1 小时），确认数据本身是实时的，仅时间戳偏移
- [x] **修复**: `src/data.py` — `get_live_df()` 返回前将 UTC 时间戳转换为 Europe/London 本地时间（`zoneinfo.ZoneInfo`，自动处理 BST/GMT 切换）
  - 顶部新增 `from zoneinfo import ZoneInfo` + `_TZ_LONDON = ZoneInfo("Europe/London")`
  - 解析 `Date Time` 列后：`dt.tz_localize("UTC").dt.tz_convert(_TZ_LONDON).dt.tz_localize(None)`
  - 效果：图表时间 +1h（UTC→BST），差距从 2 小时缩小到 1 小时；等 Christian 修好 BG 时钟后差距归零
- [x] **仅改 `src/data.py` 一个文件**，无需重新导入数据，重启 `app.py` 即生效
- [ ] 待办：发邮件给 Christian，请他修复 BG WinCC 服务器时区（夏令时未应用）

### Phase 8m — Year-to-Date Totalisers + Silo/Dispatch 独立时间范围 ✅ (2026-05-21 完成)
- [x] **需求 (Land Energy 反馈)**: ①Totaliser 显示全部历史累计无意义→改为 YTD 本年累计 ②Silo/Dispatch 趋势想看更长周期，独立于 Mill 的全局范围
- [x] **新数据函数** (`src/data.py`): `get_year_total(col, year)`（年末值−年初值，两条 LIMIT-1 SQL，当前年用 now() 当前年末用 12-31）+ `get_available_years()`
- [x] **Overview YTD** (`overview_layout`): Production `ov_cumulative` + Dispatch `ov_bagging_total`/`ov_truck_total` 三卡改用 `get_year_total(col, 今年)`；Daily 卡片不变
- [x] **Detail YTD + 年份选择器** (`page1_layout`): "Data Totaliser" 静态框→`t("ov_cumulative")` + `get_year_total(col, 选定年)`；新增 `dcc.Dropdown(id="ytd-year-select")`（默认当前年，历史年份=整年总量）
- [x] **Silo/Dispatch 独立范围**: `page1_layout` 新增第二个 df_sd（`_range_to_dates(sd_range)`，新增 1Y 档）；`fig_silo_level_trend`/`fig_silo_infeed_trend`/`fig_dispatch_trend` 改用 df_sd；面板前插入 `sd-range-bar` + `dbc.Select(id="sd-range-select")`（默认6M，选项24h/7d/1M/6M/1Y）；Tank 液位罐仍用全局 df
- [x] **性能修复 (关键)**: 初版 df_sd 用 `get_live_df()` → 对长范围(6M/1Y) `SELECT *` 把所有 30s Mill 行也拖进来，VM 上极慢（点 1m 也慢，因 df_sd 照跑 6M）。新增 `data.get_sparse_df(cols, start, end)`：只查 Silo/Dispatch 那 8 列 + 只取非空行（数据本是每小时一条），1Y ≈ 几千行无需降采样。`page1_layout` 改用 `get_sparse_df`。本地 1Y 渲染 0.2-0.4s
- [x] **首屏默认范围改 24h**: `store-time-mode` 默认从 `{custom, None}`（=全量 DB 范围，VM 上几年数据极慢）改为 `{quick, "24h"}`，首屏只查最近 24 小时，秒开；24h 按钮自动高亮；picker 上下限不变
- [x] **YTD 计算修正 (关键)**: 累计计数器的年产量 = **当年最后值 − 前一年最后值**（不是当年内 last−first）。当前年(2026) = 最新值 − 2025年末值（即 1月1日→今天）。`get_year_total` 重写：end=年内最后值, baseline=年初之前最后值（前一年末），最早年份无 baseline 时回退年内 first；新增 `_clean_sql()` 按 column_map 清洗规则过滤异常（non_negative→`>=0`）；**计数器跨年重置保护**：跨年 delta<0 时回退年内 delta，仍<0 则返回 None（样本数据 bagging 2021→2022 计数器从 9588 跌到 6886 即重置案例）
- [x] **YTD 框紧凑化**: 字号 48→30px、padding 16→6px、年份下拉移到标签同行(inline 78px)，腾出空间让下方 Pellet Silo 液位罐(180→200px)完整显示
- [x] **年份下拉只列有数据的年份**: VM 上 belt weigher 产量只有 2024-2026，旧版下拉列全部年份(2021-2026)，选 2021/22/23 显示"—"像 bug。改为 `page1_layout` 预计算各年 `get_year_total`，下拉只列非 None 年份；store 年份不在列表时回退到最新有效年。**验证**: 修正后 VM 年产量 2024=67k/2025=92.5k/2026=35k(YTD)，比旧公式 83万 合理约 5 倍(符合 16-24t/h 工厂年产)
- [x] **Stores + 回调**: 新增 `store-ytd-year` / `store-sd-range`；render_page 加 2 Input 并传给 page1_layout；新增 `update_ytd_year` / `update_sd_range` 回调；模块级 `_range_to_dates` 助手
- [x] **翻译**: `ov_cumulative`→YTD Output/本年产量/Production YTD；`ov_bagging_total`→YTD Bagging/本年包装/Ensachage YTD；`ov_truck_total`→YTD Truck/本年装车/Camion YTD；新增 `sd_range_label` + `ytd_year`（三语）
- [x] **CSS**: `.sd-range-bar` / `.sd-range-label` / `.sd-range-select` / `.ytd-year-select`
- [x] **文档同步**: layout-spec(P1/P2 wireframe+KPI表+图表清单+验收) / scope-and-design(KPI表+面板描述+YTD口径说明) / i18n-spec / user-guide(§3/§4/§6) / README / CLAUDE.md
- [x] `src/charts.py` 无需改（趋势图接收哪个 df 画哪个）

### Phase 8d — 生产部署
- [x] Windows VM + SQLite (默认) + 本地 BG CSV 目录（见 Phase 8h）
- [ ] 验证 Dashboard 在 VM 上显示所有 Mill/Amps/Energy 数据
- [ ] 持续监控模式长期稳定运行确认

---

## 已知风险

| # | 问题 | 状态 |
|---|------|------|
| 1 | BG 只覆盖 17/52 列，Dryer/Quality/CHP 面板无数据 | 已知: 显示空，待 BG 增加数据点 |
| 2 | BG 样本数据含异常（Silo 归零、负值、天文数字） | 已解决: 清洗规则定义在 column_map.py，按容量+15%容差 |
| 3 | 样本 CSV 各列时间范围差异大 | 已知: Mill仅1天(2024-03-22), Silo有5年; VM完整数据无此问题 |
| 4 | OEE 不计算 | 已决: 灰色占位 |
| 5 | 大范围查询性能 (>1M/6M/全量) 在 3GB+ 数据时可能慢 (10-60s) | 已知: 日常监控 (≤24h) 无影响; 需要时可优化 SQL 层降采样 |
| 6 | 大 CSV 文件 (2GB+) 一次性 read() 导致 parse error | **已修复 (Phase 8h)**: 改为 50MB 分块读取，9 个文件全部正常 |
| 7 | Production Rate 偶现 30000+ t/h 天文数字错值 | **已修复 (Phase 8j)**: column_map.py 清洗规则 non_negative→range [0,50]，>50 t/h 过滤为 NULL |
| 8 | 日期选择器无法选今天（max_date_allowed 锁死在启动时） | **已修复 (Phase 8k)**: _picker_max 改为 now()+1day，不再依赖 DB 最大日期 |
| 9 | BG WinCC 测量时钟未应用 BST，timestamp_utc 比真实 UTC 慢 1 小时 | **部分修复 (Phase 8l)**: data.py 加 UTC→Europe/London 转换抵消 Dashboard 侧 1 小时；BG 侧待 Christian 修复。Christian 修复后需记录精确时间点，用 `docs/timestamp-offset-analysis.md` 中的 SQL 脚本修正历史数据 |

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
| 2026-04-01 | 8b-c | config.py + data.py + ingest.py + app.py + charts.py + translations.py 全部实现; ingest 导入 250K+ 时间桶; Dashboard 启动 HTTP 200 |
| 2026-04-02 | 8e(分析) | 发现并定位 3 个 Bug: clean_value NaN→0, 降采样 .mean() 不适合累计列, Silo 图表重复; 完成文档修改: roller temp diff→L/R, Mill Health 3×2, silo 阈值拆分, KPI 14→13, 移除 Full Data Table; VM 部署步骤; thresholds 4→5 |
| 2026-04-07 | 8e(执行) | **全部代码修复完成**: ①NaN bug→Period Output=3383t ②降采样: 累计列.last()+>1Y:6h档+阈值2000 ③移除重复silo tank+data table ④silo阈值拆分_1(15/25/85/95)+_23(10/20/80/90) ⑤silo清洗按容量: 1→520/2,3→4000 ⑥roller temp L/R两图+Mill Health 3×2+Energy全宽 ⑦文档: phase8§9去重+降采样表+i18n dispatch标签 ⑧Daily Output bug: 用Totaliser自身最后日期(修复全量范围显示"—"); **样本数据说明**: Mill CSV 219K行但只覆盖1天(1s采样×5 ID=44K行/ID), Silo/Dispatch覆盖5年(1h采样), 这是BG导出特征非代码问题; **验证**: 删库重导250K桶→三页200→5年6506行 |
| 2026-04-08 | 8f | **混合频率图表修复**: ①NaN交叉断线: 新增`_sparse_series()`自适应过滤 ②tons_to_pct移除100%钳位 ③Bar图null→"N/A" ④Hover hovertemplate; **布局调整**: ⑤Production "Period Total"→"Totaliser"原始值(白色) ⑥Detail页同步 ⑦Dispatch 4卡片2行(Daily+Totaliser,全白色) ⑧Daily Output/Bagging/Truck统一白色; **Production图表双轴**: ⑨`fig_production_lines`新增右轴Totaliser(青色虚线)，左轴Rate t/h不变; ⑩P2 Detail顶部KPI栏标注LEGACY; 全部MD同步(layout-spec线框+定义表+图表清单, i18n, scope-and-design, CLAUDE.md, Plan.md) |
| 2026-04-08 | 8g | **Totaliser实线+Light/Dark主题+文档同步**: ①Totaliser青色虚线→实线 ②config.py: COLOR_SCHEMES dark/light + get_color_scheme() ③style.css: 80+硬编码hex→CSS变量+浅色覆盖 ④app.py: store-theme+☀️/🌙按钮+clientside callback+theme传递 ⑤charts.py: _tc(theme)+23个fig_*添加theme参数 ⑥translations.py: theme_toggle key ⑦对比度WCAG AA: dark subtext #9e9e9e→#b0b0b0, red #db4437→#e05545; light全新配色 ⑧文档同步: scope-and-design(KPI14+LEGACY+主题), layout-spec(实线+主题按钮), i18n(theme_toggle), README(KPI14+LEGACY+主题), CLAUDE.md(LEGACY+主题) |
| 2026-04-09 | 8h | **VM 部署 + Ingest 引擎修复**: ①VM 部署: LE 复制到 Windows VM, BG 路径 D:\CSVData\BaumgartnerData ②大文件 parse error 根本原因: 一次性 f.read() 整 2GB 文件撑爆 pandas StringIO 解析器 ③修复: 重写为 50MB 分块读取 — read_chunk()+_get_header(); ingest_once()循环分块; 9个CSV全部成功导入489万桶 ④错误信息改善: 打印 type(e).__name__+字节偏移 ⑤澄清: timestamp_utc(实际采集,每行递增) vs sync_timestamp_utc(CDC批次时间,同批相同); 时间格式含纳秒+时区偏移,pandas自动推断正确,UserWarning无害 ⑥30s bucket对不同频率数据: 1s→取last无损; 30s→1:1; 1h→稀疏(119个null桶+1个有值) |
| 2026-04-09 | 8i | **Daily Output/Bagging/Truck 降采样偏差修复 + 虚线移除**: ①**根本原因**: Daily delta 从降采样后的df计算，2h桶的vals.iloc[0]含2小时产出，导致不同时间范围显示77→67→44递减偏差 ②**修复**: data.py新增get_daily_delta(col)——直接查原始30s数据，不降采样，取最近一天的last-first差值；app.py中Daily Output/Bagging/Truck全部改用此函数 ③**移除参考虚线**: charts.py删除fig_mill_amps的400A/460A虚线 + fig_mill_feeder的55%虚线 |
| 2026-04-09 | 8j | **Production Rate 异常值过滤**: column_map.py Production 清洗规则 non_negative→range[0,50] t/h（正常11-12 t/h，BG偶现30000+错值→NULL）; 文档同步: phase8-live-data.md §4清洗表 + thresholds.md Belt Weigher + Plan.md 已知风险#7 |
| 2026-04-10 | 8k | **日期选择器Bug修复**: DatePicker max_date_allowed 锁死在启动时DB最大日期→改为 now()+1day; 顶部新增 datetime/timedelta 导入; 仅改 app.py 一个文件 |
| 2026-05-21 | 8l | **时间戳时区修复**: Dashboard 显示 UTC 时间，UK 用户看到比本地慢 2 小时（1h=BG时钟未应用BST，1h=UTC vs BST显示差）; 诊断: sync_timestamp_utc 正确实时，timestamp_utc 慢1h，确认BG侧问题; 修复: data.py get_live_df() 加 UTC→Europe/London 转换（zoneinfo 自动DST），差距缩至1h; 待Christian修复BG时钟后归零; 仅改 data.py |
| 2026-05-21 | 8m | **YTD Totalisers + Silo/Dispatch 独立时间范围**: ①data.py 新增 get_year_total()/get_available_years() ②Overview Production/Bagging/Truck 三卡改 YTD 本年累计 ③Detail YTD 框 + 年份下拉(历史整年总量) ④Silo/Dispatch 三趋势图改用独立 df_sd + sd-range-select(默认6M/选项24h-1Y) ⑤新增 store-ytd-year/store-sd-range + 2回调 + _range_to_dates 助手 ⑥翻译 3 key 改 YTD + 新增 sd_range_label/ytd_year ⑦CSS ⑧全量文档同步(layout-spec/scope/i18n/user-guide/README/CLAUDE) |
