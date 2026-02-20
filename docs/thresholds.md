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
例: Turbine Power — ≥2000kW 正常，<500kW 停机

### 模式 C: 上限阈值（越低越好）
```
  🟢 绿              🟡 黄           🔴 红
◄──────────────────┤──────────────┤──────────►
                 yellow_above    red_above
```
例: Pellet Moisture — <10% 正常，>11% 严重

---

## 2. 全部 16 个参数的默认值和 UI

### #1 Press Load Amps [模式 A] — 单位: A
适用: `Press [1/2/3] - Load Amps` | 来源: Events_Log "amps at 470"
```
│ 🔴 Red Low:      Below  [  50 ] (停机)      │
│ 🟡 Yellow Low:   From   [  50 ]  To  [ 400 ]│ ← 启动过渡/异常低载
│ 🟢 Green Range:  Min    [ 400 ]  Max [ 460 ]│
│ 🟡 Yellow High:  From   [ 460 ]  To  [ 480 ]│
│ 🔴 Red High:     Above  [ 480 ]             │
```
> 注: 50-400A 是磨机启动过渡态或异常低负载，实际运行中几乎不会长时间停留。

### #2 Pellet Mill Moisture [模式 A] — 单位: %
适用: `Pellet Mill Moistures %` | 来源: Events_Log "10.5% steady"
```
│ 🔴 Red Low:      Below  [  9.0 ]            │
│ 🟡 Yellow Low:   From   [  9.0 ]  To [ 10.0]│
│ 🟢 Green Range:  Min    [ 10.0 ]  Max[ 11.5]│
│ 🟡 Yellow High:  From   [ 11.5 ]  To [ 12.5]│
│ 🔴 Red High:     Above  [ 12.5 ]            │
```

### #3 Dryer Outlet Moisture Actual [模式 A] — 单位: %
适用: `Moisture % Actual Value at Dryer Outlet` | 来源: GreCon "dry material"
```
│ 🔴 Red Low:      Below  [  6.0 ] ⚠️火灾风险  │
│ 🟡 Yellow Low:   From   [  6.0 ]  To [  7.0]│
│ 🟢 Green Range:  Min    [  7.0 ]  Max[ 10.0]│
│ 🟡 Yellow High:  From   [ 10.0 ]  To [ 12.0]│
│ 🔴 Red High:     Above  [ 12.0 ]            │
```

### #4 Dry Silo Level [模式 A] — 单位: %
适用: `Dry Silo 1 Level %` / `Dry Silo 2 Level %` | 来源: "clear belt silos 82%"
```
│ 🔴 Red Low:      Below  [ 20 ] (断料)       │
│ 🟡 Yellow Low:   From   [ 20 ]  To  [ 30 ] │
│ 🟢 Green Range:  Min    [ 30 ]  Max [ 80 ] │
│ 🟡 Yellow High:  From   [ 80 ]  To  [ 90 ] │
│ 🔴 Red High:     Above  [ 90 ] (满仓停机)   │
```

### #5 Durability [模式 B — 越高越好] — 单位: %
适用: `Durability %` | 来源: 白板 >97.5%
```
│ 🔴 Red:          Below  [ 97.0 ]            │
│ 🟡 Yellow:       From   [ 97.0 ]  To [ 97.5]│
│ 🟢 Green:        Above  [ 97.5 ]            │
```

### #6 Pellet Moisture 成品 [模式 C — 越低越好] — 单位: %
适用: `Pellet Moisture %` | 来源: 白板 <10%
```
│ 🟢 Green:        Below  [ 10.0 ]            │
│ 🟡 Yellow:       From   [ 10.0 ]  To [ 11.0]│
│ 🔴 Red:          Above  [ 11.0 ]            │
```

### #7 Avg Pellet Length [模式 C — 越短越好] — 单位: mm
适用: `Average Pellet Length(mm)` | 来源: 白板 <40mm
```
│ 🟢 Green:        Below  [ 40 ]              │
│ 🟡 Yellow:       From   [ 40 ]  To  [ 45 ] │
│ 🔴 Red:          Above  [ 45 ]              │
```

### #8 Bulk Density [模式 B — 越高越好] — 单位: g/l
适用: `Bulk Density g/l` | 来源: 白板 630 g/l
```
│ 🔴 Red:          Below  [ 600 ]             │
│ 🟡 Yellow:       From   [ 600 ]  To [ 630 ]│
│ 🟢 Green:        Above  [ 630 ]             │
```

### #9 Main Filter kP [模式 B — 越高越好] — 单位: kPa
适用: `Main Filter kP` | 来源: "Filter blocked KP @ 0.01"
```
│ 🔴 Red:          Below  [ 0.2 ]             │
│ 🟡 Yellow:       From   [ 0.2 ]  To [ 0.5 ]│
│ 🟢 Green:        Above  [ 0.5 ]             │
```

### #10 Furnace Temp [模式 A] — 单位: °C
适用: `Furnace Temp` | 来源: "Furnace temp dropping to 877"
```
│ 🔴 Red Low:      Below  [ 877 ]             │
│ 🟡 Yellow Low:   From   [ 877 ]  To [ 920 ]│
│ 🟢 Green Range:  Min    [ 920 ]  Max[ 960 ]│
│ 🔴 Red High:     Above  [ 960 ]             │
```
> 注: >960°C 直接红色（无 Yellow High），因现有数据中没有高温异常案例。用户可自行调整添加。

### #11 Thermal Oil OUT [模式 B — 越高越好] — 单位: °C
适用: `Thermal Oil OUT` | 来源: "temperatures reached 300"
```
│ 🔴 Red:          Below  [ 300 ]              │
│ 🟡 Yellow:       From   [ 300 ]  To [ 305 ] │
│ 🟢 Green:        Above  [ 305 ]              │
```

### #12 Turbine Power [模式 B — 越高越好] — 单位: kW
适用: `Turbine Generated Power kW` | CSV 正常: 2200–2370
```
│ 🔴 Red:          Below  [  500 ] (跳闸)     │
│ 🟡 Yellow:       From   [  500 ]  To [ 2000]│
│ 🟢 Green:        Above  [ 2000 ]            │
```

### #13 Dryer Out Feed [模式 B — 越高越好] — 单位: t/h
适用: `Dryer out feed t/h` (Col 8) | CSV: avg=12.3
```
│ 🔴 Red:          Below  [  9.0 ]            │
│ 🟡 Yellow:       From   [  9.0 ]  To [ 11.0]│
│ 🟢 Green:        Above  [ 11.0 ]            │
```

### #14 Belt Weigher Hourly [模式 B — 越高越好] — 单位: t/h
适用: `Total tons passed belt weigher (hour)` (Col 51) | 目标: 20–24 t/h
```
│ 🔴 Red:          Below  [ 10.0 ]            │
│ 🟡 Yellow:       From   [ 10.0 ]  To [ 14.0]│
│ 🟢 Green:        Above  [ 14.0 ]            │
```

### #15 Valve Position [模式 A] — 单位: %
适用: `Valve position open at %` | 来源: P1.505 "stuck closed"
```
│ 🔴 Red Low:      Below  [ 15 ]              │
│ 🟡 Yellow Low:   From   [ 15 ]  To  [ 25 ] │
│ 🟢 Green Range:  Min    [ 25 ]  Max [ 40 ] │
│ 🟡 Yellow High:  From   [ 40 ]  To  [ 60 ] │
│ 🔴 Red High:     Above  [ 60 ]              │
```

### #16 Feeder % [模式 B — 越高越好] — 单位: %
适用: `Press [1/2/3] - Feeder %` | CSV: 58–69%
```
│ 🔴 Red:          Below  [ 40 ] (喂料不足)   │
│ 🟡 Yellow:       From   [ 40 ]  To  [ 55 ] │
│ 🟢 Green:        Above  [ 55 ]              │
```

---

## 3. 设置面板 UI 设计

### 入口
顶栏右侧 ⚙️ → 弹出 Modal

### 面板结构
- 16 个参数按分组折叠: Mill (1,2,16) / Dryer (3,4,13) / Quality (5,6,7,8) / CHP (10,11,12) / Throughput (14) / Other (9,15)
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
