# Land Energy Pellet Line Dashboard

## 铁律 (Hard Rules)
- **每次启动必须先读 `Plan.md`**，了解当前进度和下一步任务
- **每轮任务结束后必须更新 `Plan.md`**（勾选已完成项、记录问题、更新 Session Log）
- 写代码前先读相关的 `docs/` 参考文档（见下方索引）
- 所有图表数据必须能追溯到 `src/column_map.py` 中的列映射，不可凭记忆编造

## 项目概要
- **客户**: Land Energy（苏格兰 Girvan 木质颗粒工厂），目标: 16 t/h → 20-24 t/h
- **交付物**: 工厂运营实时监控 Dashboard（Python + Dash + SQLite/PostgreSQL）
- **数据源 (Phase 8+)**: Baumgartner (BG) CDC 实时 CSV（长表格式，9 文件，25 个 value_id，每 ~10 秒追加）
  - 列映射注册表: `src/column_map.py`（BG value_id → Dashboard 列名的单一真相源）
  - 采集引擎: `src/ingest.py`（读 CSV 增量 → 清洗 → 30s 重采样 → UPSERT 到数据库）
  - 技术细节: `docs/phase8-live-data.md`
- **旧数据 (Phase 0-7, 已弃用)**: `data/Shift_Protocol_date_time_merged.csv`（64 列宽表，745 行 Demo 快照）
  - `init_db.py` 和 `data/` 目录保留但不再使用
- **BG 当前覆盖**: 17/52 列（Mill + Production + Pellet Silo），Dryer/Quality/CHP 待 BG 后续增加
- **P1 KPI 总览** (`/`): Production 4 卡片 + Mill Status 3 卡片 + Pellet Silo 3 液位罐 + Dispatch 4 卡片 (差值+原始值各2)
- **P2 详细运营** (`/ops`): 4个分区面板 (Production/Mill/Pellet Silo/Dispatch)。~~KPI卡片行~~ LEGACY（Phase 8 移除，代码保留注释）
- **P3 AI Placeholder** (`/ai`): 4 个伪数据占位面板 + "Coming Soon"
- **三语**: EN / 中文 / Français 顶栏切换器（见 `docs/i18n-spec.md`）
- **阈值可调**: 4 个有效参数 (Amps/Belt Weigher/Feeder/Pellet Silo) 🟢🟡🔴 颜色边界，⚙️ Settings UI 调整（见 `docs/thresholds.md`）
- **不计算 OEE**: OEE 卡片灰色占位
- **Light/Dark 主题切换**: 顶栏 ☀️/🌙 按钮切换，CSS 变量驱动，偏好保存 localStorage
- **深色 SCADA 风格**: Roboto Mono 数字字体，关键数字 2 米外可读
- **Grafana 风格时间控制**: 快速范围按钮 + 自动刷新 (Off/5s/30s/1min)

## 关键约束
- **技术栈**: Python 3.10+, Dash (Plotly), SQLite(本地)/PostgreSQL(生产), localhost:8050
- **深色主题**: 背景 `#1a1a2e` / 卡片 `#16213e` / 绿 `#0f9b58` / 黄 `#f4b400` / 红 `#db4437`
- **列名映射**: BG value_id → Dashboard 列名，定义在 `src/column_map.py`
- **Logo**: 从 https://www.land-energy.com/ 获取

## docs/ 参考文档索引

| 文档 | 何时读 | 内容 |
|------|--------|------|
| `docs/phase8-live-data.md` | **写数据层/采集/部署时** | BG 实时数据架构、列映射表、清洗规则、数据流全景图、部署方案 |
| `docs/scope-and-design.md` | 写任何新功能前 | 完整 Scope (In/Out)、面板图表规格、设计原则 |
| `docs/column-map.md` | 需要旧 64 列参考时 | 旧 Shift Protocol 64 列映射（已被 `src/column_map.py` 取代） |
| `docs/thresholds.md` | 写颜色逻辑/设置面板时 | 4 个有效参数的 🟢🟡🔴 默认值、Settings Panel 规格 |
| `docs/i18n-spec.md` | 写 UI 文本/translations.py 时 | 三语翻译对照表 |
| `docs/layout-spec.md` | 写页面布局时 | ASCII 线框图、KPI 卡片定义、验收标准 |
| `docs/background.md` | 需要业务背景时 | 项目背景、工厂架构、商业目标 |
| `docs/data-analysis.md` | 需要参数含义时 | 前期数据分析（参数详解、阈值来源推导） |
| `docs/deployment.md` | Render.com 云端部署时 | Render.com 部署步骤 |
| `docs/timestamp-offset-analysis.md` | 处理时间戳/时区问题时 | BG 时间戳偏移问题分析、BST/GMT 修复方案、历史数据 SQL 修正方法 |

## 参考资料目录（只读，不主动使用）

| 目录 | 说明 |
|------|------|
| `BaumgartnerData/` | BG 导出的 9 个原始 CSV 样本（~100万行，用于本地测试） |
| `BaumgartnerData_analysis/` | BG 数据的分析笔记（异常值、频率、业务含义） |
| `live-data-solution/` | 早期部署规划草稿（已弃用，不作参考） |
| `data/` | 旧 Demo CSV 数据（Phase 0-7，已弃用） |

## ❌ Out of Scope（不做的功能）
- 不做 OEE 计算、不做真实 AI/ML、不做用户认证、不做移动端适配
- 完整清单见 `docs/scope-and-design.md` §2

## 目录结构
```
C:/LE/
├── CLAUDE.md                ← 项目全貌（你正在读的文件）
├── Plan.md                  ← 进度追踪
├── README.md                ← 项目说明
├── requirements.txt         ← 根目录依赖
├── render.yaml              ← Render.com 部署配置
├── docs/                    ← 参考文档（按需读取）
│   ├── phase8-live-data.md  ← 实时数据技术设计（核心）
│   ├── scope-and-design.md
│   ├── column-map.md        ← 旧 64 列映射（参考）
│   └── ...
├── BaumgartnerData/         ← BG 原始 CSV 样本（测试用）
├── data/                    ← 旧 Demo CSV（已弃用）
└── src/                     ← 代码
    ├── app.py               ← Dash 主应用
    ├── ingest.py            ← BG CSV 采集引擎（Phase 8）
    ├── column_map.py        ← BG→Dashboard 列映射注册表（Phase 8）
    ├── data.py              ← 数据库查询层
    ├── charts.py            ← 15 个 Plotly 图表函数
    ├── config.py            ← 阈值/颜色/环境变量配置
    ├── translations.py      ← 三语翻译字典
    ├── init_db.py           ← 旧 CSV→SQLite 导入（已弃用）
    ├── requirements.txt
    ├── assets/
    │   ├── style.css
    │   └── logo.png
    ├── thresholds.json      ← 运行时生成（用户阈值覆盖）
    ├── ingest_state.json    ← 运行时生成（CSV 字节偏移追踪）
    └── land_energy.db       ← 运行时生成（ingest.py 写入）
```

## 验收清单 (快速版)
- [ ] `python src/ingest.py --once --source BaumgartnerData/` 导入无报错
- [ ] `python src/app.py` 启动无报错，Dashboard 显示 BG 实时数据
- [ ] Production KPI = Complete_Plant.Production 最新值
- [ ] Mill Load Amps 图表 = Pellet_Mill_X.Actual_Current 趋势
- [ ] Pellet Silo 柱状图 = Fuel_Level 值
- [ ] BG 未覆盖的面板（Dryer/Quality/CHP）优雅处理，不崩溃
- [ ] 时间范围选择器联动所有图表
- [ ] 阈值设置面板可调、持久化到 thresholds.json
- [ ] 三语切换正常
- [ ] 自动刷新 (5s/30s/1min) 可启停
- [ ] 导航: Overview · Detail · AI 三页切换

完整验收标准见 `docs/layout-spec.md` 底部。
