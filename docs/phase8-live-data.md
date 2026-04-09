# Phase 8: Live Data Integration — 技术设计文档

> **日期**: 2026-04-01（最后更新）
> **核心决策**:
> - 完全替换旧 Demo 数据，只用 BG 实时数据管道
> - **数据库: SQLite**（本地和工厂部署均使用，代码预留 PostgreSQL 接口）
> - **清洗策略: 全部写入 DB，显示时过滤**（不在入库时丢弃数据，保留原始值）

---

## 1. 数据生命周期全景图

```
┌─ 工厂现场 ─────────────────────────────────────────────────────────┐
│                                                                     │
│  SCADA/WinCC (传感器每 2-3 秒采样)                                   │
│       │                                                             │
│       ▼                                                             │
│  BG CDC 程序 (每 ~10 秒扫描 WinCC，追加新行到 CSV 文件末尾)           │
│       │                                                             │
│       ▼                                                             │
│  9 个 CSV 文件 (长表格式，持续增长，永不截断)                          │
│  /mnt/bg_export/ (生产) 或 BaumgartnerData/ (本地样本)               │
│                                                                     │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              │  ingest.py 每 5 秒读取一次
                              │
┌─ ingest.py 处理流程 ────────▼───────────────────────────────────────┐
│                                                                     │
│  第1步: 读增量                                                       │
│  ├─ 打开每个 CSV 文件                                                │
│  ├─ seek 到上次读取的字节位置 (记录在 ingest_state.json)              │
│  ├─ 读取从该位置到文件末尾的所有新字节                                │
│  ├─ 如果最后一行不完整 → 丢弃，下次再读                              │
│  └─ 更新 ingest_state.json 中的字节位置                              │
│                                                                     │
│  第2步: 解析 + 映射                                                  │
│  ├─ 每行: value_id=66, real_value=285.3                             │
│  ├─ 查 column_map.BY_VALUE_ID[66] → "Press 1 - Load Amps"          │
│  ├─ ⚠ 时间键: 使用 `timestamp_utc`（数据实际产生时间）                │
│  │   忽略 `sync_timestamp_utc`（CDC 扫描/导出时间，仅为元数据）       │
│  └─ 结果: {timestamp_utc → {"Press 1 - Load Amps": 285.3, ...}}    │
│                                                                     │
│  第3步: 基本校验（不做范围清洗）                                      │
│  ├─ 非数字值 → NULL（解析失败的行）                                   │
│  ├─ 所有合法数值原封不动保留（包括可能的异常值）                       │
│  └─ 范围过滤在 Dashboard 显示层做，不在入库时做                       │
│                                                                     │
│  第4步: 重采样 (30 秒桶)                                             │
│  ├─ 1s/5s Mill 数据 → 取每 30s 窗口最后一个值                        │
│  ├─ 30s Complete_Plant → 自然对齐                                    │
│  └─ 1h Silo/Dispatch → forward-fill 到 30s 粒度                     │
│                                                                     │
│  第5步: 写入数据库 (UPSERT)                                          │
│  ├─ SQLite (默认): INSERT OR REPLACE INTO live_data ...             │
│  └─ PostgreSQL (可选，通过 DATABASE_URL 环境变量切换):               │
│     INSERT ... ON CONFLICT("Date Time") DO UPDATE ...               │
│                                                                     │
│  为什么用 UPSERT？                                                   │
│  因为不同 CSV 文件的数据可能在不同时刻到达:                            │
│  - 第一次写入: Mill 数据填了 "Press 1 - Load Amps" 列                │
│  - 几秒后:    Silo 数据到达，UPSERT 补上 "Pellet Silo Level 1" 列   │
│  - 同一个 30s 时间桶的行会被逐步补全                                  │
│                                                                     │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─ 数据库 ───────────────────────────────────────────────────────────┐
│                                                                     │
│  表: live_data (宽表，列名与旧 shift_protocol 完全一致)               │
│                                                                     │
│  "Date Time"  │ "Press 1 - Load Amps" │ ... │ "Pellet Silo Level 1" │
│  ─────────────┼───────────────────────┼─────┼──────────────────────│
│  2024-03-22T08:27:00 │ 285.3          │ ... │ 501.2               │
│  2024-03-22T08:27:30 │ 286.1          │ ... │ 501.2               │
│  2024-03-22T08:28:00 │ 284.8          │ ... │ 501.2               │
│                                                                     │
│  主键: "Date Time" (30秒间隔的 ISO 时间戳)                           │
│  增长速度: ~2,880 行/天, ~200 KB/天, ~70 MB/年                       │
│  存储: 全部原始值（含可能的异常值），不在入库时丢弃                    │
│                                                                     │
│  默认: SQLite (land_energy.db) — 本地开发和工厂部署均可              │
│  可选: PostgreSQL (设 DATABASE_URL 环境变量即可切换)                  │
│                                                                     │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              │  Dashboard 每次刷新时查询
                              │
┌─ Dashboard 显示层 ──────────▼───────────────────────────────────────┐
│                                                                     │
│  data.py: get_live_df(start, end)                                   │
│  → SELECT * FROM live_data WHERE "Date Time" BETWEEN ? AND ?        │
│  → 返回 pandas DataFrame (宽表)                                     │
│  → **在此处按 column_map.py 的规则过滤异常值**                       │
│     例: Fuel_Level 负值→0, >5000→NULL                               │
│     规则可随时修改，不需要重新导入数据                                │
│  → **大范围自动降采样** (保证前端流畅):                               │
│     ≤24h:   原始 30s 粒度 (最多 ~2,880 行)                          │
│     ≤14d:   5 min 重采样 (~2,016 行)                                 │
│     ≤60d:   30 min 重采样 (~1,440 行)                                │
│     ≤1Y:    2h 重采样 (~4,380 行)                                    │
│     >1Y:    6h 重采样 (≤~7,300 行)                                   │
│     策略: 瞬时列取窗口均值, 累计列取末值; 每次返回 ≤~3,000 行       │
│                                                                     │
│  app.py: 自动刷新 (5s/30s/1m) → 触发重新查询 → 拿到干净数据          │
│  charts.py: 用 DataFrame 列名画图                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 关键场景

### 场景 A: 首次运行（空数据库）

```bash
# 用 BaumgartnerData/ 样本做初始导入
python src/ingest.py --once --source BaumgartnerData/

# 处理流程:
# 1. 发现 ingest_state.json 不存在 → 从每个 CSV 的第 0 字节开始
# 2. 读取全部 ~100 万行，解析 + 基本校验 + 重采样
# 3. 写入 live_data 表（约几分钟）
# 4. 保存各文件的最终字节位置到 ingest_state.json
```

### 场景 B: 持续运行（生产环境）

```bash
# 在 Windows VM 上持续运行（可注册为 Windows 服务或用 Task Scheduler）
python src/ingest.py --source D:\BG_Export\

# 每 5 秒循环:
# 1. 读 ingest_state.json → 知道上次读到了哪个字节
# 2. 打开 9 个 CSV → seek 到上次位置 → 读新增行（通常几十到几百行）
# 3. 解析 + 基本校验 + 重采样 → UPSERT 到 live_data（原始值全部保留）
# 4. 更新 ingest_state.json
# 5. sleep 5 秒，重复
```

### 场景 C: 崩溃恢复

```
ingest.py 重启时:
├─ ingest_state.json 存在 → 从记录的字节位置继续读
├─ ingest_state.json 丢失 → 查询 DB: SELECT MAX("Date Time") FROM live_data
│   └─ 扫描 CSV 找到对应位置，从那里继续
│       （可能重复处理少量行，UPSERT 保证幂等，不会产生重复数据）
└─ 数据库也空 → 等同于场景 A，全量导入
```

### 场景 D: BG 新增数据点（将来）

```
假设 BG 将来增加了 Dryer 温度数据:
1. 他们在 CSV 中追加新的 value_id (比如 200 = Dryer_Outlet_Moisture)
2. 我们在 column_map.py 添加一条映射:
   {"bg_value_id": 200, "dashboard_col": "Moisture %  Displayed Value at Dryer Outlet", ...}
3. ingest.py 自动识别新 value_id → 写入 live_data 表的新列
4. Dashboard 的 Dryer 面板自动有数据了
不需要改 app.py / charts.py / data.py
```

---

## 3. 列映射注册表 (`src/column_map.py`)

### A. 可直接映射到 Dashboard 现有面板（17 列）

| BG 文件 | BG value_name | value_id | Dashboard 列名 | 频率 |
|---|---|---|---|---|
| Pellet_Mill_1 | Actual_Current | 66 | `Press 1 - Load Amps` | 1s |
| Pellet_Mill_2 | Actual_Current | 69 | `Press 2 - Load Amps` | 1s |
| Pellet_Mill_3 | Actual_Current | 117 | `Press 3 - Load Amps` | 1s |
| Pellet_Mill_1 | Actual_Speed_Dosing_Screw | 62 | `Press 1 - Feeder %` | 1s |
| Pellet_Mill_2 | Actual_Speed_Dosing_Screw | 64 | `Press 2 - Feeder %` | 1s |
| Pellet_Mill_3 | Actual_Speed_Dosing_Screw | 114 | `Press 3 - Feeder %` | 1s |
| Pellet_Mill_1 | Left_Roller_Temperature | 67 | `Press 1 - Left Roller Temperature` | 1s |
| Pellet_Mill_1 | Right_Roller_Temperature | 68 | `Press 1 - Right Roller Temperature` | 1s |
| Pellet_Mill_2 | Left_Roller_Temperature | 70 | `Press 2 - Left Roller Temperature` | 1s |
| Pellet_Mill_2 | Right_Roller_Temperature | 71 | `Press 2 - Right Roller Temperature` | 1s |
| Pellet_Mill_3 | Left_Roller_Temperature | 118 | `Press 3 - Left Roller Temperature` | 1s |
| Pellet_Mill_3 | Right_Roller_Temperature | 119 | `Press 3 - Right Roller Temperature` | 1s |
| Complete_Plant | Production | 75 | `Total tons passed belt weigher (hour)` | 30s |
| Complete_Plant | Totaliser | 74 | `Total Pellets passed belt weigher (cumlative)` | 30s |
| Pellet_Silo_1 | Fuel_Level | 150 | `Pellet Silo Level 1 Readout` | 1h |
| Pellet_Silo_2 | Fuel_Level | 149 | `Pellet Silo Level 2 Readout` | 1h |
| Pellet_Silo_3 | Fuel_Level | 148 | `Pellet Silo Level 3 Readout` | 1h |

### B. BG 新增数据（暂存为 `_` 前缀列，Phase 9 再建面板）

| BG value_name | value_id | 内部列名 | 说明 |
|---|---|---|---|
| Energy (Mill 1/2/3) | 171/173/172 | `_pm1/2/3_energy_cumulative` | 累计 kWh |
| Infeed_Totaliser (Silo 1/2/3) | 157/156/155 | `_silo1/2/3_infeed_totaliser` | 各仓累计进料 |
| Bagging Totaliser | 152 | `_bagging_totaliser` | 包装线累计 |
| Truck Totaliser | 159 | `_truck_totaliser` | 卡车累计 |

### C. Dashboard 现有但 BG 未覆盖（Live 模式下为空）

Dryer 全部 12 列、Quality 全部、CHP 全部、Mill kWh/t 等。
将来 BG 增加数据点 → 在 `column_map.py` 加一行映射即可，不需要改其他代码。

---

## 4. 数据清洗策略

### 核心原则: 全部写入 DB，显示时过滤

- **ingest.py 不做范围清洗** — 只丢弃解析失败的行（非数字值→NULL），所有合法数值原封不动写入 DB
- **data.py 查询后过滤** — 按 `column_map.py` 中定义的规则过滤异常值
- **规则可随时调整** — 改 `column_map.py` 里的数字即可，不需要重新导入数据
- **BG 原始 CSV 始终保留** — 如果需要完全重新导入，跑 `ingest.py --once` 即可

### 显示层过滤规则（在 data.py 中执行）

| 数据 | 规则 | 备注 |
|---|---|---|
| Fuel_Level Silo 1 (450t) | [0, 520] 吨→有效, 超出→NULL | 容量 450t + 15% 容差 |
| Fuel_Level Silo 2/3 (3500t) | [0, 4000] 吨→有效, 超出→NULL | 容量 3500t + 15% 容差 |
| Infeed_Totaliser | 非负 | 累计值不应为负 |
| Bagging/Truck Totaliser | 非负 | 累计值不应为负 |
| Complete_Plant Production | [0, 50] t/h→有效, 超出→NULL | 正常 11-12 t/h，BG 偶现 30000+ 错值 |
| Complete_Plant Totaliser | 非负 | 最可靠数据源 |
| Mill Actual_Current | [0, 800] A | 放宽（堵机可瞬间飙高） |
| Mill Roller Temp | [0, 250] °C | 放宽 |
| Mill Feeder (Dosing Screw) | [0, 120] % | 可能短时超 100% |
| Mill Energy | 非负 | 累计值 |

规则定义在 `column_map.py` 的每条映射的 `clean` 字段中。

---

## 5. ingest.py 核心状态管理

### ingest_state.json（字节偏移追踪文件）

```json
{
  "file_offsets": {
    "Pellet_Mill_1.csv": 4521760,
    "Pellet_Mill_2.csv": 4518400,
    "Complete_Plant.csv": 1890432,
    ...
  },
  "last_update": "2026-03-31T14:22:05"
}
```

**为什么要追踪字节位置？**
- BG 的 CSV 文件会持续增长（几十万行以上）
- 每次循环只需要读新增的几十行，而不是重新解析整个文件
- seek 到字节位置 → 读到文件末尾 → 毫秒级完成

**完整行保护:**
- BG 文档说明："between writes, unfinished CSV may be read"
- 如果读到的最后一行列数不足 → 丢弃 → 字节位置回退到该行起始
- 下次循环会重新读这行（此时 BG 已写完）

---

## 6. 混合频率重采样

BG 数据有 4 种频率：1s / 5s / 30s / 1h。统一重采样为 **30 秒**。

| 原始频率 | 处理方式 | 示例 |
|---|---|---|
| 1s (Mill 电流/速度/温度) | 取 30s 窗口最后一个值 | 08:27:00~08:27:29 的 30 个值 → 取 08:27:29 的 |
| 5s (Mill Energy) | 取 30s 窗口最后一个值 | 6 个值 → 取最后一个 |
| 30s (Complete Plant) | 自然对齐 | 不需要重采样 |
| 1h (Silo/Dispatch) | forward-fill | 08:00 的值填充到 08:00:00~08:59:30 所有桶 |

---

## 7. 文件变更清单

| 文件 | 操作 | 说明 |
|---|---|---|
| `src/column_map.py` | **已更新** | 清洗规则(显示时过滤), Fuel_Level 上限 5000, Silo 容量(1=450t, 2/3=3500t), `tons_to_pct()` |
| `src/ingest.py` | **待创建** | 采集引擎: CSV tail → 基本校验 → 30s 重采样 → UPSERT（不做范围清洗） |
| `src/data.py` | **待修改** | 查询 live_data 表 + 查询后按 column_map 规则过滤 + SQLite/PostgreSQL 双支持 |
| `src/config.py` | **待修改** | 加 `DATABASE_URL` / `BG_EXPORT_DIR` 环境变量 + `pellet_silo_level_1` / `pellet_silo_level_23` 阈值（Silo 1 与 Silo 2/3 分开设置） |
| `src/app.py` | **待修改** | 动态时间范围 + Pellet Silo 百分比液位罐 + 页面布局重组（移除无数据面板） |
| `src/charts.py` | **待修改** | `fig_pellet_silos()` 改为百分比液位罐 + 各图表缺失列保护 |
| `src/translations.py` | **待修改** | 加 Pellet Silo 翻译 key + "No data" 翻译 |
| `src/init_db.py` | 不改 | 保留文件但不再使用 |
| `requirements.txt` | 待加 | `psycopg2-binary`（预留 PostgreSQL 支持） |

---

## 8. 生产部署

部署环境: **Windows VM**（LE 工厂服务器）

- BG CSV 目录在 VM 本地磁盘，直接访问（无需 SMB 挂载）
- **SQLite 为默认数据库**（land_energy.db，与应用同目录）
  - SQLite WAL 模式支持一写多读（ingest 写 + Dashboard 读）
  - 预计 ~70 MB/年，完全够用
  - 如需 PostgreSQL（例如多节点部署），设 `DATABASE_URL` 环境变量即可切换
- 部署流程: 本地开发 → 推送 GitHub → VM 上 `git pull` → `python src/app.py`
- 未来可考虑云部署（Render 等），当前不需要

### Windows VM 部署步骤

```bash
# 1. 环境准备（首次）
git clone <repo-url> C:\LE
cd C:\LE
python -m pip install -r src/requirements.txt

# 2. 首次导入（3GB CSV 预计 3-10 分钟）
python src/ingest.py --once --source D:\BG_Export\

# 3. 启动 Dashboard
python src/app.py
# 浏览器访问 http://localhost:8050

# 4. 持续采集（每 10s 轮询 CSV 新增行）
python src/ingest.py --source D:\BG_Export\ --interval 10
```

**生产环境推荐**: 用 Windows 任务计划程序创建两个任务:
- **le-ingest**: 触发器=系统启动时, 操作=`pythonw.exe src/ingest.py --source D:\BG_Export\ --interval 10`
- **le-dashboard**: 触发器=系统启动时, 操作=`pythonw.exe src/app.py`

**日常更新**:
```bash
cd C:\LE && git pull && python -m pip install -r src/requirements.txt
# 重启 le-ingest + le-dashboard 任务
```

---

## 9. 页面布局重组

BG 目前只覆盖 17/52 列。Energy/CHP、Dryer、Quality、Events/Downtime 完全没有数据。
需要重组页面，移除空面板，用有数据的指标填满屏幕。

### 可用数据清单

| 类别 | 列 | 来源 | 用途 |
|------|-----|------|------|
| **Production** | Production (t/h) | Complete_Plant | 实时产能速率 |
| | Totaliser (t) | Complete_Plant | 累计产量（算日/段差值） |
| **Mill 1/2/3** (×3) | Load Amps (A) | Pellet_Mill_X | 负载电流 |
| | Feeder % | Pellet_Mill_X | 进料螺杆速度 |
| | Left Roller Temp (°C) | Pellet_Mill_X | 左辊温度 |
| | Right Roller Temp (°C) | Pellet_Mill_X | 右辊温度 |
| **Pellet Silo 1/2/3** (×3) | Fuel Level (t→%) | Pellet_Silo_X | 仓位百分比 |
| **BG-only** | Energy (kWh) ×3 | Pellet_Mill_X | 累计电耗（待建面板） |
| | Infeed Totaliser (t) ×3 | Pellet_Silo_X | 各仓累计进料 |
| | Bagging Totaliser (t) | Bagging_Station | 包装线累计 |
| | Truck Totaliser (t) | Truck_Loading | 卡车装载累计 |

### 不再可用的面板（Phase 8 移除）

- Energy/CHP: Turbine Power, Furnace Temp, Thermal Oil, HRU Bypass
- Dryer: Dry Silo Levels, Dryer Moisture, Dryer Feed
- Quality: Pellet Durability, Fines %, Pellet Moisture, Pellet Temp, Pellet Length
- Downtime/Events: 事件日志、停机 Pareto 图

---

### Page 1/2/3 — 布局规格

> **详细线框图、KPI 定义表、图表清单、验收标准** → 见 [`docs/layout-spec.md`](layout-spec.md)（UI 布局唯一参考）。
>
> 本文档只记录 **Phase 8 相对旧版的变更摘要**，不重复线框图。

#### Phase 8 布局变更摘要

| 页面 | 变更 |
|------|------|
| **P1 Overview** | Production 4 卡片保留; **新增 Mill Status** 3 卡片 (Amps+阈值色); **Pellet Silo** 吨数柱状→百分比液位罐 `_ov_tank()`; **新增 Dispatch** 3 卡片 (Bagging/Truck/Total); **移除** Energy/CHP/Dryer/Quality sections |
| **P2 Detail** | 面板 6→4: 保留 Production + Mill Health; **新增** Pellet Silo (level trend + infeed trend) + Dispatch (cumul trend); **移除** Dryer/Quality/CHP/Downtime; Mill kWh/t→cumul kWh; Roller Temp diff→L/R 两图; **移除底部全数据表** (25 列均有图表覆盖) |
| **P3 AI** | 不变，4 个伪数据占位面板 + "Coming Soon" |

**P2 图表清单** (11 个): `fig_production_lines`, `fig_pellet_silos`, `fig_mill_gauges`, `fig_mill_amps_trend`, `fig_mill_feeder`, `fig_roller_temp_left`, `fig_roller_temp_right`, `fig_mill_energy`, `fig_silo_level_trend`, `fig_silo_infeed_trend`, `fig_dispatch_trend`

---

## 10. 验证方法

```bash
# 1. 首次导入样本数据
python src/ingest.py --once --source BaumgartnerData/

# 2. 检查数据库
sqlite3 src/land_energy.db "SELECT COUNT(*) FROM live_data"
sqlite3 src/land_energy.db "SELECT * FROM live_data LIMIT 5"

# 3. 启动 Dashboard
python src/app.py
# → 浏览器打开 http://localhost:8050

# 4. 验证点:
# - Overview 页 Production KPI = Complete_Plant.Production 最新值
# - Mill Load Amps 图表 = Pellet_Mill_X.Actual_Current 趋势
# - Pellet Silo 百分比液位罐 = Fuel_Level → tons_to_pct() (Silo1=450t, Silo2/3=3500t)
# - 无 Dryer/Quality/CHP/Downtime 面板（已移除）
# - 自动刷新 (5s) 开启后，若 ingest.py 在后台运行，Dashboard 自动更新
```
