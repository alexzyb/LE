# i18n Specification — EN / 中文 / Fran\u00e7ais

> **Phase 8 更新 (2026-04)**: 移除无 BG 数据的翻译 key，新增 Mill Status/Pellet Silo/Dispatch key。

## 翻译对照表

| 类别 | English | 中文 | Fran\u00e7ais |
|------|---------|------|----------|
| **导航** | | | |
| 导航 | Overview | 总览 | Synth\u00e8se |
| 导航 | Detail | 详细 | D\u00e9tail |
| 导航 | AI | AI | IA |
| **P1 Overview 分类** | | | |
| P1 分类 | Production | 产量 | Production |
| P1 分类 | Mill Status | 磨机状态 | \u00c9tat des broyeurs |
| P1 分类 | Pellet Silo | 颗粒料仓 | Silo \u00e0 granul\u00e9s |
| P1 分类 | Dispatch | 出货 | Exp\u00e9dition |
| **P1 Production 卡片** | | | |
| P1 卡片 | Daily Output | 日产量 | Production du jour |
| P1 卡片 | Hourly Rate | 小时产率 | D\u00e9bit horaire |
| P1 卡片 | Mills Running | 磨机运行 | Broyeurs actifs |
| P1 卡片 | YTD Output | 本年产量 | Production YTD |
| **P1 Mill Status 卡片** | | | |
| P1 卡片 | Mill 1 Amps | 压机1电流 | Courant presse 1 |
| P1 卡片 | Mill 2 Amps | 压机2电流 | Courant presse 2 |
| P1 卡片 | Mill 3 Amps | 压机3电流 | Courant presse 3 |
| **P1 Pellet Silo 液位罐** | | | |
| P1 液位罐 | Pellet Silo 1 | 颗粒仓 1 | Silo 1 |
| P1 液位罐 | Pellet Silo 2 | 颗粒仓 2 | Silo 2 |
| P1 液位罐 | Pellet Silo 3 | 颗粒仓 3 | Silo 3 |
| **P1 Dispatch 卡片** | | | |
| P1 卡片 | Daily Bagging | 包装日产 | Ensachage du jour |
| P1 卡片 | Daily Truck | 装车日产 | Camion du jour |
| P1 卡片 | YTD Bagging | 本年包装 | Ensachage YTD |
| P1 卡片 | YTD Truck | 本年装车 | Camion YTD |
| **P2 Detail 面板** | | | |
| 控件 | Silo & Dispatch Range | 料仓与出货范围 | Plage Silo & Expédition |
| 控件 | Year | 年份 | Année |
| 面板 | Production & Throughput | 产量与生产率 | Production et d\u00e9bit |
| 面板 | Mill Health & Load | 磨机健康与负载 | Sant\u00e9 et charge des broyeurs |
| 面板 | Pellet Silo | 颗粒料仓 | Silo \u00e0 granul\u00e9s |
| 面板 | Dispatch | 出货 | Exp\u00e9dition |
| **KPI / 状态** | | | |
| KPI | Daily Output | 日产量 | Production journali\u00e8re |
| KPI | Rate (t/h) | 实时产量 (t/h) | D\u00e9bit (t/h) |
| KPI | Mills Status | 磨机状态 | \u00c9tat des broyeurs |
| 状态 | Running | 运行中 | En marche |
| 状态 | Stopped | 停机 | Arr\u00eat\u00e9 |
| 状态 | Insufficient Data | 数据不足 | Donn\u00e9es insuffisantes |
| 状态 | No data | 无数据 | Pas de donn\u00e9es |
| **主题** | | | |
| 主题 | Toggle Theme | 切换主题 | Basculer le thème |
| **按钮 / 设置** | | | |
| 按钮 | Apply | 应用 | Appliquer |
| 按钮 | Save & Apply | 保存并应用 | Enregistrer et appliquer |
| 按钮 | Reset to Default | 恢复默认 | R\u00e9initialiser |
| 按钮 | Reset All to Default | 全部恢复默认 | Tout r\u00e9initialiser |
| 设置 | Threshold Settings | 阈值设置 | Param\u00e8tres de seuil |
| **P3 AI Placeholder** | | | |
| P3 | Coming Soon | 即将推出 | Bient\u00f4t disponible |
| P3 | Production Forecast | 产量预测 | Pr\u00e9vision de production |
| P3 | Fault Prediction | 故障预测 | Pr\u00e9diction de pannes |
| P3 | Anomaly Detection | 异常检测 | D\u00e9tection d'anomalies |
| P3 | Root Cause Analysis | 根因分析 | Analyse des causes profondes |
| P3 overlay | Requires additional historical data | 需要更多历史数据来训练模型 | N\u00e9cessite des donn\u00e9es historiques suppl\u00e9mentaires |
| P3 横幅 | Expected availability: Q3 2026 | 预计可用时间：2026年第三季度 | Disponibilit\u00e9 pr\u00e9vue : T3 2026 |

## 已移除的翻译 key (Phase 8, BG 无数据)

以下 key 在旧版本中存在，Phase 8 因无 BG 数据已移除:
- 面板: Dryer & Feed, Quality Control, CHP & Energy, Downtime & Events
- P1 分类: Energy, Dryer, Pellet Quality
- P1 卡片: Turbine Power, Furnace Temp, Thermal Oil OUT, HRU Bypass, Dryer Feed, Outlet Moisture, Dry Silo 1/2
- P1 质量: Durability, Bulk Density, Pellet Moisture, Pellet Temp, Avg Length
- KPI: Dryer Feed, Events (24h)

待 BG 增加数据点后可恢复。

## 不翻译的内容
- 数据库列名（全数据表保持英文原名）
- 技术单位: kWh, t/h, \u00b0C, A, %
- 数值和单位符号

## 实现方式
- `translations.py` 中定义 `TRANSLATIONS = {"en": {...}, "zh": {...}, "fr": {...}}`
- `t(key, lang)` 辅助函数
- 语言切换器: `dcc.Store`
- 默认语言: English
