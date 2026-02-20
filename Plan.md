# Plan.md — Land Energy Dashboard 开发计划

> ⚠️ **每次启动必读此文件，每轮任务结束后必须更新。**

## 📅 最后更新: 2026-02-18
## 🏁 当前阶段: Phase 3 ✅ → Phase 4 待开始

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

## Phase 4: 阈值设置面板 ⬜
- [ ] Modal UI (16 参数输入表单)
- [ ] Save → thresholds.json + 全局颜色刷新
- [ ] Reset → 删 json + 恢复默认
- [ ] 面板三语

## Phase 5: Page 2 Placeholder ⬜
- [ ] 4 占位面板 + 灰色 overlay
- [ ] 伪数据 + "Coming Soon"
- [ ] 三语

## Phase 6: 打磨交付 ⬜
- [ ] Logo 获取
- [ ] CSS 微调
- [ ] 三语全面测试
- [ ] README.md
- [ ] 对照 `docs/layout-spec.md` 验收清单逐项检查

---

## 已知风险
| # | 问题 | 状态 |
|---|------|------|
| 1 | Logo 获取 (可能需联网) | 待定 |
| 2 | Col 52-54 损坏 | 已决: 从 Col 45 差值计算 |
| 3 | Col 51 噪点 (6行) | 已决: 过滤 |
| 4 | OEE 不计算 | 已决: 灰色占位 |
| 5 | 法语翻译准确性 | 低风险 |
| 6 | 阈值面板 UI 复杂度 (60+ 输入框) | 中风险 |

---

## Session Log
| 日期 | Phase | 完成内容 |
|------|-------|----------|
| 2026-02-17 | 0 | 规划完成, 文档拆分 |
| 2026-02-18 | 1 | config.py / translations.py / init_db.py / requirements.txt — 全部完成，测试通过 |
| 2026-02-18 | 2 | app.py + assets/style.css — Dashboard骨架完成，KPI实时数据，三语切换，服务器启动正常 |
| 2026-02-18 | 3 | data.py + charts.py(15图) + app.py重写 — 6面板全部接入真实数据，DateRange联动，测试全通过 |
