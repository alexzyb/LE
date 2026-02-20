# Layout Specification & Acceptance Criteria

## Page 1 — Operational Overview

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] Land Energy — Girvan Pellet Plant Dashboard               │
│        Date: [01-01] → [02-01] [Apply]      🌐[EN|中|FR] ⚙️     │
├──────────────────────────────────────────────────────────────────┤
│ OEE    │ Daily    │ Rate    │ Mills   │ Dryer   │ Events        │
│ — %    │ Out (t)  │ (t/h)   │ Status  │ Feed    │ (24h)         │
│ ░ N/A  │ 324.5    │ 13.7 🟡  │ 2/3 🟢  │ 12.3 🟢  │ 5 ⚠️          │
├──────────────────────────────────────────────────────────────────┤
│ [Tab: Production] [Mill Health] [Dryer] [Quality] [CHP] [Down]  │
├──────────────────────────────────────────────────────────────────┤
│ ┌─ Production & Throughput ──────────────────────────────────┐   │
│ │ [Line: Belt Weigher t/h (Col 51) + 20 t/h target]         │   │
│ │ [Line: Dryer Out Feed t/h (Col 8)]                         │   │
│ │ [Big Number: Shift/Daily Total]                            │   │
│ │ [Bar: Pellet Silo 1/2/3 (tonnes)]                         │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Mill Health & Load ───────────────────────────────────────┐   │
│ │ [●]M1:Running [●]M2:Running [●]M3:Stopped                 │   │
│ │ [Gauge×3: Amps] [Line: Amps trend] [Bar: kWh/t]           │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Dryer & Feed ─────────────────────────────────────────────┐   │
│ │ [Tank: Silo1 67%] [Tank: Silo2 38%]                       │   │
│ │ [Line: Outlet Moisture Actual vs Displayed]                │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Quality Control ──────────────────────────────────────────┐   │
│ │ [Cards: Durability/Moisture/Density/Length]                 │   │
│ │ [Line: Quality trends]                                     │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ CHP & Energy ─────────────────────────────────────────────┐   │
│ │ [Gauge: Turbine kW] [Line: Furnace Temp + Thermal Oil]     │   │
│ └────────────────────────────────────────────────────────────┘   │
│ ┌─ Downtime & Events ────────────────────────────────────────┐   │
│ │ [Table: Recent 10] [Pareto: Fault Cat] [Bar: Area]         │   │
│ └────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────┤
│ Full Data Table (64 cols, scrollable, sortable)                  │
└──────────────────────────────────────────────────────────────────┘
```

## Page 2 — AI Analytics Placeholder

```
┌──────────────────────────────────────────────────────────────────┐
│ [Logo] AI Predictive Analytics — Coming Soon     🌐[EN|中|FR]    │
├───────────────────────┬──────────────────────────────────────────┤
│ Production Forecast   │ Fault Prediction                         │
│ [Fake trend+band]     │ Mill 2 Blockage ETA:14h Conf:72%        │
│ ░░ PLACEHOLDER ░░     │ ░░ PLACEHOLDER ░░                        │
├───────────────────────┼──────────────────────────────────────────┤
│ Anomaly Detection     │ Root Cause Analysis                      │
│ [Fake timeline]       │ [Fake Sankey]                            │
│ ░░ PLACEHOLDER ░░     │ ░░ PLACEHOLDER ░░                        │
├──────────────────────────────────────────────────────────────────┤
│ ⚠️ Requires more historical data. Expected: Q3 2026              │
└──────────────────────────────────────────────────────────────────┘
```

## KPI 卡片定义

| 卡片 | 数据来源 | 颜色逻辑 |
|------|----------|----------|
| OEE | 无 | 固定灰色，显示 "— %" |
| Daily Output | Col 45 (当日最新值 - 当日起始值) | 无颜色 |
| Rate (t/h) | Col 51 最新记录 | 按 Belt Weigher 阈值着色 |
| Mills Status | 3 台磨机 Amps >50 判定 | 全部运行=🟢, 部分=🟡, 全停=🔴 |
| Dryer Feed | Col 8 最新值 | 按 Dryer Out Feed 阈值着色 |
| Events (24h) | Events_Log 过去 24h 计数 | >10=🔴, 5-10=🟡, <5=🟢 |

## 设计原则
1. 深色主题 SCADA 风格 (Grafana/MachineMetrics)
2. 关键数字 2 米外可读
3. 🟢🟡🔴 全局统一语义
4. Gauge 用于有明确上下限的参数
5. Tank Level 用于 Silo 液位
6. Pareto 用于停机分析
7. 上游/下游产量双线对比

## 完整验收标准

### 基础
- [ ] `python src/app.py` 启动无报错
- [ ] localhost:8050 显示 Dashboard
- [ ] 顶部有 Land Energy Logo + 工厂名

### 数据
- [ ] OEE 灰色占位，不计算
- [ ] KPI 卡片数值匹配 CSV（可抽查）
- [ ] 磨机状态灯正确 (Amps>50=Running)
- [ ] Dry Silo = Tank Level (%)
- [ ] Pellet Silo = 柱状图 (吨)
- [ ] 所有 🔴 参数有颜色指示
- [ ] 底部 64 列全数据表
- [ ] Events_Log 正确显示

### Production 精确性
- [ ] Col 51 (Belt Weigher) 趋势图标题明确
- [ ] Col 8 (Dryer Feed) 趋势图标题明确
- [ ] 两条线不混淆

### 阈值面板
- [ ] ⚙️ 可打开设置面板
- [ ] 16 个参数可调
- [ ] 调整即时生效
- [ ] Reset 恢复默认
- [ ] 持久化到 thresholds.json

### 三语
- [ ] EN/中/FR 切换正常
- [ ] 所有标题/按钮/Tooltip 已翻译
- [ ] 无错位截断
- [ ] 默认 English

### Page 2
- [ ] 4 个 Placeholder + "Coming Soon"
- [ ] 面板标题三语
