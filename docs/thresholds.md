# Thresholds & Color System

> 所有数值为**默认初始值**。Dashboard 必须提供 UI 让用户实时调整。

---

## 1. 阈值逻辑说明

每个参数有**自己独立的数值范围**，彼此完全不同。颜色逻辑分三种模式：

### 模式 A: 双边阈值（中间好、两头差）
```
  🔴 红     🟡 黄      🟢 绿       🟡 黄      🔴 红
◄────────┤────────┤──────────────┤────────┤────────►
       low_red  low_yellow    high_yellow  high_red
```
例: Press Load Amps — 400–460A 正常，太高过载，太低停机

### 模式 B: 下限阈值（越高越好）
```
  🔴 红         🟡 黄           🟢 绿
◄──────────┤──────────────┤──────────────────►
         red_below      yellow_below
```
例: Belt Weigher Hourly — ≥14 t/h 正常，<10 t/h 产能不足

### 模式 C: 上限阈值（越低越好）
```
  🟢 绿              🟡 黄           🔴 红
◄──────────────────┤──────────────┤──────────►
                 yellow_above    red_above
```
例: Roller Temperature — <200°C 正常，>250°C 过热（注: 当前无阈值面板，仅作说明）

---

## 2. 有效阈值参数

> **Phase 8 更新**: BG 只覆盖 17 列。原 16 个阈值中只有 3 个有对应 BG 数据，新增 1 个。
> Legacy 阈值保留在 `config.py` 中但不激活，待 BG 增加数据点后可恢复。

### 有效阈值 (4 个，有 BG 数据)

#### #1 Press Load Amps [模式 A] — 单位: A
适用: `Press [1/2/3] - Load Amps` | BG: Pellet_Mill_X.Actual_Current
```
│ 🔴 Red Low:      Below  [  50 ] (停机)      │
│ 🟡 Yellow Low:   From   [  50 ]  To  [ 400 ]│
│ 🟢 Green Range:  Min    [ 400 ]  Max [ 460 ]│
│ 🟡 Yellow High:  From   [ 460 ]  To  [ 480 ]│
│ 🔴 Red High:     Above  [ 480 ]             │
```

#### #2 Belt Weigher Hourly [模式 B — 越高越好] — 单位: t/h
适用: `Total tons passed belt weigher (hour)` | BG: Complete_Plant.Production
```
│ 🔴 Red:          Below  [ 10.0 ]            │
│ 🟡 Yellow:       From   [ 10.0 ]  To [ 14.0]│
│ 🟢 Green:        Above  [ 14.0 ]            │
```

#### #3 Feeder % [模式 B — 越高越好] — 单位: %
适用: `Press [1/2/3] - Feeder %` | BG: Pellet_Mill_X.Actual_Speed_Dosing_Screw
```
│ 🔴 Red:          Below  [ 40 ] (喂料不足)   │
│ 🟡 Yellow:       From   [ 40 ]  To  [ 55 ] │
│ 🟢 Green:        Above  [ 55 ]              │
```

#### #4 Pellet Silo Level [模式 A] — 单位: % (新增)
适用: `Pellet Silo Level 1/2/3 Readout` → 百分比 | BG: Pellet_Silo_X.Fuel_Level
```
│ 🔴 Red Low:      Below  [ 20 ] (接近空仓)   │
│ 🟡 Yellow Low:   From   [ 20 ]  To  [ 30 ] │
│ 🟢 Green Range:  Min    [ 30 ]  Max [ 80 ] │
│ 🟡 Yellow High:  From   [ 80 ]  To  [ 90 ] │
│ 🔴 Red High:     Above  [ 90 ] (接近满仓)   │
```

### Legacy 阈值 (12 个，BG 未覆盖，暂不激活)

以下阈值在 `config.py` 中保留定义，但因 BG 未提供对应数据，Dashboard 不会使用。
待 BG 增加数据点后，在 `column_map.py` 加映射即可自动恢复。

| # | Key | 说明 | 原因 |
|---|-----|------|------|
| 2 | `pellet_mill_moisture` | Mill 水分 % | BG 未覆盖 |
| 3 | `dryer_outlet_moisture` | Dryer 出口水分 | BG 无 Dryer 数据 |
| 4 | `dry_silo_level` | Dry Silo 液位 | BG 无 Dry Silo 数据 |
| 5 | `durability` | 耐久性 % | BG 无 Quality 数据 |
| 6 | `pellet_moisture_finished` | 成品水分 | BG 无 Quality 数据 |
| 7 | `avg_pellet_length` | 平均长度 | BG 无 Quality 数据 |
| 8 | `bulk_density` | 堆密度 | BG 无 Quality 数据 |
| 9 | `main_filter_kp` | 主过滤器 kP | BG 未覆盖 |
| 10 | `furnace_temp` | 炉温 | BG 无 CHP 数据 |
| 11 | `thermal_oil_out` | 热油出口 | BG 无 CHP 数据 |
| 12 | `turbine_power` | 涡轮功率 | BG 无 CHP 数据 |
| 13 | `dryer_out_feed` | 烘干出料 | BG 无 Dryer 数据 |
| 15 | `valve_position` | 阀门位置 | BG 未覆盖 |

---

## 3. 设置面板 UI 设计

### 入口
顶栏右侧 ⚙️ → 弹出 Modal

### 面板结构
- 4 个有效参数按分组: Mill (Amps, Feeder %) / Production (Belt Weigher) / Silo (Pellet Silo Level)
- 模式 A 参数显示 4-5 个输入框
- 模式 B/C 参数显示 2 个输入框
- 每个参数有单独 [Reset to Default]
- 底部: [Reset All to Default] + [Save & Apply]

### 持久化
- 默认值: `config.py` → `DEFAULT_THRESHOLDS`
- 用户覆盖: `thresholds.json`（启动时优先加载）
- Save → 写 json + 全局 Callback 刷新颜色
- Reset All → 删 json + 恢复默认
- 面板文字三语

### config.py 数据结构

```python
# 字段含义: 定义边界点，颜色区间自动推导
# 模式 A (dual): 4 个边界点 → 5 个颜色区间
#   < red_low = 🔴 | red_low ~ green_min = 🟡 | green_min ~ green_max = 🟢 
#   | green_max ~ red_high = 🟡 | > red_high = 🔴
#
# 模式 B (lower): 2 个边界点 → 3 个颜色区间
#   < red_below = 🔴 | red_below ~ green_above = 🟡 | > green_above = 🟢
#
# 模式 C (upper): 2 个边界点 → 3 个颜色区间
#   < green_below = 🟢 | green_below ~ red_above = 🟡 | > red_above = 🔴

DEFAULT_THRESHOLDS = {
    "press_load_amps": {
        "mode": "dual",
        "red_low": 50, "green_min": 400,
        "green_max": 460, "red_high": 480,
        "unit": "A"
    },
    "furnace_temp": {
        "mode": "dual",
        "red_low": 877, "green_min": 920,
        "green_max": 960, "red_high": 960,
        "unit": "°C"
    },
    "turbine_power": {
        "mode": "lower",
        "red_below": 500, "green_above": 2000,
        "unit": "kW"
    },
    "pellet_moisture_finished": {
        "mode": "upper",
        "green_below": 10.0, "red_above": 11.0,
        "unit": "%"
    },
    # ... 其余 12 个参数同理，完整清单见本文档 §2
}
```
