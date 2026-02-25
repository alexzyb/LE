# Plan.md — Land Energy Dashboard 开发计划

> ⚠️ **每次启动必读此文件，每轮任务结束后必须更新。**
> 📝 **Bugfix 记录规范**: 每次临时修复 bug，需在对应 Phase 下追加 `🐛 fix:` 条目，注明问题原因和修复内容。

## 📅 最后更新: 2026-02-25
## 🏁 当前阶段: Phase 7 ✅ — Grafana 风格时间控制

---

## Phase 0: 规划 ✅
- [x] 数据分析 + 64 列映射
- [x] 阈值提取 + 来源引用
- [x] 文档拆分: CLAUDE.md + docs/

## Phase 1: 数据层 ✅
- [x] `src/config.py` — DEFAULT_THRESHOLDS (16 参数) + COLOR_SCHEME + COLUMN_MAP + THRESHOLD_GROUPS
- [x] `src/translations.py` — 三语字典 (EN/ZH/FR) + t() 辅助函数
- [x] `src/init_db.py` — CSV 清洗 + SQLite
  - Date Time: DD/MM/YYYY HH:MM:SS → ISO ✓
  - 空白列 (1,14,18,24,30,36,38,44,55) 已丢弃 ✓
  - #REF!/#VALUE!/空值 → NULL ✓
  - Col 51: |值|>50 → NULL (7个NULL: 6噪点+首行#VALUE!) ✓
  - Col 52-54: 已丢弃 ✓
  - Events_Log Duration H:MM:SS → Duration_min (分钟) ✓ 编码兼容utf-8-sig/cp1252/latin-1 ✓
  - Meter_Readings: 导入完成 ✓
- [x] 测试: `python src/init_db.py` 无报错 — 745行/52列/244KB ✓
- [x] `src/requirements.txt` 创建完成

## Phase 2: Dashboard 骨架 ✅
- [x] `src/assets/style.css` — SCADA 深色主题 CSS
- [x] `src/app.py` — Dash 4.0, 2页路由, 深色主题
- [x] 顶栏: ⚡Logo + 标题 + DatePicker + 🌐语言(EN|中|FR) + ⚙️阈值 + P1|P2导航
- [x] KPI 卡片行 — 真实 DB 数据 (OEE灰占位, Daily/Rate/Mills/Dryer/Events实时)
  - 最新数据: 2026-02-01, Rate=13.8 t/h🟡, Dryer=12.8 t/h🟢, Mills=3/3🟢
- [x] 6 面板空壳 (标题+占位符，Phase 3 填充图表)
- [x] Page 2: 4 个 AI 占位面板 + 灰色 overlay + Coming Soon + Q3 2026 横幅
- [x] 4 个 Callback: 语言切换/TopBar文本/页面路由/Settings弹窗
- [x] 测试: `python src/app.py` 启动 http://localhost:8050 无报错 ✓

## Phase 3: Page 1 面板 ✅
- [x] `src/data.py` — get_shift_df() + get_events_df() SQLite 查询
- [x] `src/charts.py` — 15 个 Plotly 图表函数 (6 面板全覆盖)
  - Panel 1: fig_production_lines (Col51+Col8+20t/h目标) + fig_pellet_silos
  - Panel 2: fig_mill_gauges (3×Gauge) + fig_mill_amps_trend + fig_mill_feeder + fig_roller_temp_diff + fig_mill_kwht
  - Panel 3: fig_dry_silos (tank overlay) + fig_dryer_moisture (Displayed vs Actual)
  - Panel 4: fig_quality_trends (2×2 subplot + 参考线)
  - Panel 5: fig_turbine_gauge + fig_chp_trend (双Y轴) + fig_hru_damper
  - Panel 6: fig_downtime_pareto (Pareto+80%线) + fig_area_downtime
- [x] `src/app.py` 重写 — 659行，6面板+KPI+全数据表+DateRange联动
- [x] 测试: 15/15 图表 OK, page1_layout/page2_layout OK, 数据: 745行/322事件 ✓

## Phase 3.5: KPI 总览页 + 字体放大 ✅
- [x] 全局字体放大: KPI值 38→48px, 标签 10→13px, 面板标题 11→14px, DataTable 10→13px 等
- [x] 新增 P1 KPI 总览页 (`/`) — 大字体商务绩效看板
  - Production: 4 张 KPI 卡片 (日产量/小时速率/磨机状态/期间总量)
  - Energy: 4 张 KPI 卡片 (涡轮功率/炉温/热油出口/HRU旁通)
  - Dryer: 4 张 KPI 卡片 (烘干出料/出口水分/干燥仓1/干燥仓2)
  - Quality: 2×3 网格 (Durability/Density/Moisture/Pellet Temp/Avg Length, 无Fines)
- [x] 页面路由调整: `/`=总览, `/ops`=详细运营, `/ai`=AI占位
- [x] 导航切换: Overview · Detail · AI (三语)
- [x] `translations.py` 新增 ~25 个翻译键 (EN/ZH/FR)
- [x] `style.css` 新增 `.overview-card`, `.quality-grid` 等 CSS 类
- [x] Google Fonts 镜像修复 (fonts.googleapis.com → fonts.loli.net)
- [x] 测试: 3页布局全部 OK, 15图表 OK, 三语 OK ✓

## Phase 4: 阈值设置面板 ✅
- [x] `config.py` — get_thresholds() / save_thresholds() / reset_thresholds() 持久化函数
- [x] Modal UI: dbc.Accordion 6 组 (Mill/Dryer/Quality/CHP/Throughput/Other), 16 参数 44 个输入框
- [x] build_settings_body(lang) — 动态构建手风琴面板，dict ID 模式匹配
- [x] populate_modal 回调 — 打开时填充当前阈值，语言切换重建
- [x] save_or_reset_thresholds 回调 — pattern-matching ALL 收集输入，Save→JSON / Reset→删 JSON
- [x] store-thresh-ver 版本号机制 — 阈值变更触发全页面颜色刷新
- [x] 按钮文字 (Save & Apply / Reset All) 跟随三语切换
- [x] style.css — Accordion 暗色主题 + Modal 输入框样式
- [x] translations.py — 8 个边界标签 + 6 个分组名三语翻译
- [x] 测试: 3 页 HTTP 200, save/reset 流程正常, 6 回调注册成功 ✓
- [x] 🐛 fix: charts.py gauge 色带硬编码阈值 — 问题: fig_mill_gauges 和 fig_turbine_gauge 的色带边界是硬编码数字，Settings 面板修改阈值后 gauge 不会更新。修复: 改为从 get_thresholds() 动态读取边界值

## Phase 5: Page 3 (AI) Placeholder 打磨 ✅
- [x] 4 占位面板伪数据优化 — charts.py 新增 4 个伪数据 Plotly 图表函数 (Production Forecast 趋势+置信带, Fault Prediction 概率条形图, Anomaly Detection 时间线+标记, Root Cause Sankey)
- [x] overlay 样式微调 — 透明度 0.82→0.68，blur 3→2px，min-height 改 auto 适配图表高度
- [x] 三语 — 已在 Phase 2 完成，无需新增翻译 key
- [x] 测试: 3 页 HTTP 200, 4 个 AI 图表渲染正常, overlay 覆盖正常 ✓

## Phase 6: 打磨交付 ✅
- [x] Logo 获取 — S3 CDN 下载 PNG (60×60 RGBA)，html.Img 替换 ⚡ emoji，CSS height:32px
- [x] CSS 微调 — .brand-logo 从 font-size 改为 height/width auto，与文字对齐正常
- [x] 三语全面测试 — 77 个 key，EN/ZH/FR 完全一致，无遗漏
- [x] README.md — 项目简介 + 快速启动 + 项目结构 + 技术栈 + 功能列表
- [x] 对照 `docs/layout-spec.md` 验收清单逐项检查 — 30+ 项全部 PASS
- [x] 🐛 fix: Overview 页阈值颜色缺失 — 问题: Dry Silo 1/2 永远灰色（未调用 threshold_color）、Outlet Moisture 用了不存在的 key `dryer_moisture_actual`（应为 `dryer_outlet_moisture`）、Thermal Oil 未接入阈值颜色。修复: app.py 补全 4 个 KPI 卡片的 threshold_color 调用
- [x] 🐛 fix: Detail 页 Dry Silo 图表颜色硬编码 — 问题: charts.py fig_dry_silos() 色带边界写死 (20/30/80/90)，Settings 面板修改阈值后不生效。修复: 改为从 get_thresholds() 动态读取 dry_silo_level 边界值
- [x] Overview Dry Silo 液位罐视觉组件 — 新增 `_ov_tank()` 纯 CSS+HTML tank level 组件，替代原数字卡片，底部半透明填充色块高度=百分比，颜色跟随阈值
- [x] Render.com 部署配置 — gunicorn + render.yaml + PORT 环境变量 + docs/deployment.md

## Phase 7: Grafana 风格时间范围 + 自动刷新 ✅
- [x] `src/data.py` — get_shift_df() / get_events_df() 支持 datetime 精度过滤（YYYY-MM-DDTHH:MM:SS），向后兼容原 YYYY-MM-DD 格式
- [x] `src/app.py` layout — 新增 dcc.Store(store-time-mode) + dcc.Interval(auto-refresh-interval) + 5 个快速范围按钮(1m/30m/1h/6h/24h) + dbc.Select 刷新间隔下拉(Off/5s/30s/1min) + 刷新指示灯(refresh-dot)
- [x] `src/app.py` callbacks — 新增 3 个 callback:
  - update_refresh_interval: 控制 Interval 启停 + 指示灯显隐
  - update_time_mode: 根据触发源切换 quick/custom 模式（存入 store-time-mode）
  - highlight_active_qr: 快速按钮高亮（outline=True/False 切换填充色）
- [x] `src/app.py` render_page() 改造 — 新增 Input: store-time-mode + auto-refresh-interval.n_intervals; quick 模式用 datetime.now()-timedelta 计算滚动窗口
- [x] `src/translations.py` — 新增 tr_auto_refresh / tr_refresh_off 翻译 key (EN/ZH/FR)
- [x] `src/assets/style.css` — 新增 .time-range-toolbar / 按钮高亮(.btn-secondary) / .auto-refresh-select / .refresh-indicator + pulse 动画
- [x] 测试: 3 页 HTTP 200, layout JSON 包含所有新组件 ID ✓

---

## 已知风险
| # | 问题 | 状态 |
|---|------|------|
| 1 | Logo 获取 (可能需联网) | 已解决: S3 CDN 下载 PNG |
| 2 | Col 52-54 损坏 | 已决: 从 Col 45 差值计算 |
| 3 | Col 51 噪点 (6行) | 已决: 过滤 |
| 4 | OEE 不计算 | 已决: 灰色占位 |
| 5 | 法语翻译准确性 | 低风险 |
| 6 | 阈值面板 UI 复杂度 (60+ 输入框) | 已解决: 44 输入框，pattern-matching ALL |

---

## Session Log
| 日期 | Phase | 完成内容 |
|------|-------|----------|
| 2026-02-17 | 0 | 规划完成, 文档拆分 |
| 2026-02-18 | 1 | config.py / translations.py / init_db.py / requirements.txt — 全部完成，测试通过 |
| 2026-02-18 | 2 | app.py + assets/style.css — Dashboard骨架完成，KPI实时数据，三语切换，服务器启动正常 |
| 2026-02-18 | 3 | data.py + charts.py(15图) + app.py重写 — 6面板全部接入真实数据，DateRange联动，测试全通过 |
| 2026-02-23 | 3.5 | 新增P1 KPI总览页(12卡片+Quality网格) + 全局字体放大 + 3页路由(Overview/Detail/AI) + Google Fonts镜像修复 |
| 2026-02-23 | 4 | 阈值设置面板完成 — config.py持久化 + Modal手风琴UI(16参数44输入) + save/reset回调 + store-thresh-ver全局刷新 + 三语 |
| 2026-02-23 | 4-fix | charts.py gauge 硬编码阈值修复 (fig_mill_gauges + fig_turbine_gauge → get_thresholds()) |
| 2026-02-24 | 5 | AI占位页打磨 — 4个伪数据Plotly图表(Forecast+FaultPred+Anomaly+Sankey) + overlay透明度微调 |
| 2026-02-24 | 6 | 打磨交付 — Logo集成(S3 PNG→html.Img) + CSS微调 + 三语77key一致 + README.md + 30+项验收全PASS |
| 2026-02-24 | 6-fix | 阈值颜色修复 — Overview: Dry Silo 1/2 + Outlet Moisture(错误key) + Thermal Oil 补全threshold_color; Detail: fig_dry_silos硬编码→get_thresholds()动态读取 |
| 2026-02-24 | 6+ | Overview Dry Silo 液位罐组件(_ov_tank CSS+HTML) + Render部署配置(gunicorn/render.yaml/deployment.md) |
| 2026-02-25 | 7 | Grafana风格时间控制 — 快速范围按钮(1m/30m/1h/6h/24h) + 自动刷新(Off/5s/30s/1min) + data.py datetime精度过滤 + 3个新callback + 刷新指示灯 |
