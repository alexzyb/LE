# Land Energy Pellet Line Dashboard (Demo)

## 铁律 (Hard Rules)
- **每次启动必须先读 `Plan.md`**，了解当前进度和下一步任务
- **每轮任务结束后必须更新 `Plan.md`**（勾选已完成项、记录问题、更新 Session Log）
- 写代码前先读相关的 `docs/` 参考文档（见下方索引）
- 所有图表数据必须能追溯到 CSV 原始列名，不可凭记忆编造

## 项目概要
- **客户**: Land Energy（苏格兰 Girvan 木质颗粒工厂），目标: 16 t/h → 20-24 t/h
- **交付物**: 可本地运行的工厂运营监控 Dashboard（Python + Dash + SQLite）
- **数据**: `data/Shift_Protocol_date_time_merged.csv`（64 列，745 行，2026-01-01~02-01 每小时）
- **辅助数据**: `data/Events_Log.csv`（停机事件）、`data/Meter_Readings.csv`（日能源表）
- **P1 KPI 总览** (`/`): 大字体KPI卡片(Production/Energy/Dryer各4张) + Quality 2×3网格，一眼总览工厂状态
- **P2 详细运营** (`/ops`): KPI卡片行(6张) → 6个分区面板(Production/Mill/Dryer/Quality/CHP/Downtime) → 底部52列全数据表
- **P3 AI Placeholder** (`/ai`): 4 个伪数据占位面板 + 灰色 overlay + "Coming Soon"
- **三语**: EN / 中文 / Français 顶栏切换器（见 `docs/i18n-spec.md`）
- **阈值可调**: 16 个参数的 🟢🟡🔴 颜色边界可通过 ⚙️ Settings UI 调整（见 `docs/thresholds.md`）
- **不计算 OEE**: OEE 卡片灰色占位 "— %"，不做 A×P×Q
- **深色 SCADA 风格**: Roboto Mono 数字字体，关键数字 2 米外可读
- **Grafana 风格时间控制**: 快速范围按钮 (1m/30m/1h/6h/24h) + 自动刷新 (Off/5s/30s/1min)
- **Render.com 部署**: gunicorn + render.yaml，可云端 Demo（见 `docs/deployment.md`）

## 关键约束
- **技术栈**: Python 3.10+, Dash (Plotly), SQLite, 本地运行 localhost:8050
- **深色主题**: 背景 `#1a1a2e` / 卡片 `#16213e` / 绿 `#0f9b58` / 黄 `#f4b400` / 红 `#db4437`
- **CSV 列名不可改**: 代码中做映射
- **Col 52-54 损坏**: 忽略，从 Col 45 累计值自行计算产量
- **Col 51 有 6 行噪点** (|值|>50): init_db.py 过滤为 NULL
- **Logo**: 从 https://www.land-energy.com/ 获取

## docs/ 参考文档索引
读相关文档的时机：

| 文档 | 何时读 | 内容 |
|------|--------|------|
| `docs/scope-and-design.md` | **写任何新功能前** | 完整 Scope (In/Out)、每个面板具体包含什么图表、性能要求、设计原则、图表类型选择指南 |
| `docs/column-map.md` | 写数据层/图表时 | 64 列完整映射、大类分组、优先级、状态判定逻辑 |
| `docs/thresholds.md` | 写颜色逻辑/设置面板时 | 16 个参数的 🟢🟡🔴 默认值、引用来源、Settings Panel 设计规格 |
| `docs/i18n-spec.md` | 写 UI 文本/translations.py 时 | 三语翻译对照表、翻译覆盖范围、不翻译的内容 |
| `docs/layout-spec.md` | 写页面布局时 | ASCII 线框图 (P1总览/P2详细/P3 AI)、KPI 卡片定义、完整验收标准 |
| `docs/background.md` | 需要业务背景时 | 项目背景、工厂架构、商业目标 |
| `docs/data-analysis.md` | 需要参数含义时 | 前期数据分析对话（参数详解、阈值来源推导） |
| `docs/deployment.md` | 部署到云端时 | Render.com 部署步骤、Azure 未来规划 |

## ❌ Out of Scope（不做的功能）
- 不做 OEE 计算、不做真实 AI/ML、不做用户认证、不做移动端适配
- 完整清单见 `docs/scope-and-design.md` §2

## 目录结构目标
```
C:/LE/
├── CLAUDE.md              ← 你正在读的文件
├── Plan.md                ← 进度追踪
├── README.md              ← 项目说明
├── requirements.txt       ← 根目录依赖 (Render 部署用)
├── render.yaml            ← Render.com 部署配置
├── docs/                  ← 参考文档（按需读取）
│   └── deployment.md      ← 部署指南
├── data/                  ← CSV 数据文件
└── src/                   ← 代码输出
    ├── app.py
    ├── init_db.py
    ├── data.py
    ├── charts.py
    ├── config.py
    ├── translations.py
    ├── requirements.txt
    ├── assets/
    │   ├── style.css
    │   └── logo.png
    ├── thresholds.json    ← 运行时生成 (用户阈值覆盖)
    └── land_energy.db     ← 运行时生成 (init_db.py)
```

## 验收清单 (快速版)
- [ ] `python src/app.py` 启动无报错
- [ ] OEE 卡片灰色占位，不计算
- [ ] 时间范围选择器联动所有图表
- [ ] 阈值设置面板可调、持久化到 thresholds.json
- [ ] 三语切换正常、无错位
- [ ] Production 面板: Col 51 (Belt Weigher) 和 Col 8 (Dryer Feed) 分别显示、不混淆
- [ ] Dry Silo 用 Tank Level (%), Pellet Silo 用柱状图 (吨)
- [ ] 底部全数据表 52 列可滚动
- [ ] P1 总览页: 12张KPI大卡片 + Quality 2×3网格，字体醒目
- [ ] P3 有 4 个 AI Placeholder 面板
- [ ] 导航: Overview · Detail · AI 三页切换
- [ ] 快速时间范围按钮 (1m/30m/1h/6h/24h) 可切换并高亮
- [ ] 自动刷新下拉 (Off/5s/30s/1min) 可启停，指示灯闪烁
- [ ] Overview Dry Silo 1/2 显示液位罐视觉组件

完整验收标准见 `docs/layout-spec.md` 底部。
