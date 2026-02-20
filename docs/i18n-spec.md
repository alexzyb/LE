# i18n Specification — EN / 中文 / Français

## 翻译对照表

| 类别 | English | 中文 | Français |
|------|---------|------|----------|
| 页面标题 | Operational Overview | 运营监控 | Vue opérationnelle |
| 面板 | Production & Throughput | 产量与生产率 | Production et débit |
| 面板 | Mill Health & Load | 磨机健康与负载 | Santé et charge des broyeurs |
| 面板 | Dryer & Feed | 烘干与供料 | Séchoir et alimentation |
| 面板 | Quality Control | 质量控制 | Contrôle qualité |
| 面板 | CHP & Energy | 热电联产与能效 | Cogénération et énergie |
| 面板 | Downtime & Events | 停机与事件 | Arrêts et événements |
| KPI | Daily Output | 日产量 | Production journalière |
| KPI | Rate (t/h) | 实时产量 (t/h) | Débit (t/h) |
| KPI | Mills Status | 磨机状态 | État des broyeurs |
| KPI | Dryer Feed | 烘干出料 | Débit séchoir |
| KPI | Events (24h) | 事件 (24h) | Événements (24h) |
| 状态 | Running | 运行中 | En marche |
| 状态 | Stopped | 停机 | Arrêté |
| 状态 | Insufficient Data | 数据不足 | Données insuffisantes |
| 按钮 | Apply | 应用 | Appliquer |
| 按钮 | Save & Apply | 保存并应用 | Enregistrer et appliquer |
| 按钮 | Reset to Default | 恢复默认 | Réinitialiser |
| 设置 | Threshold Settings | 阈值设置 | Paramètres de seuil |
| P2 | Coming Soon | 即将推出 | Bientôt disponible |
| P2 | Production Forecast | 产量预测 | Prévision de production |
| P2 | Fault Prediction | 故障预测 | Prédiction de pannes |
| P2 | Anomaly Detection | 异常检测 | Détection d'anomalies |
| P2 | Root Cause Analysis | 根因分析 | Analyse des causes profondes |
| P2 overlay | Requires additional historical data | 需要更多历史数据来训练模型 | Nécessite des données historiques supplémentaires |
| P2 横幅 | Expected availability: Q3 2026 | 预计可用时间：2026年第三季度 | Disponibilité prévue : T3 2026 |
| 按钮 | Reset All to Default | 全部恢复默认 | Tout réinitialiser |
| 导航 | Page 1 | 第1页 | Page 1 |
| 导航 | Page 2 | 第2页 | Page 2 |

## 不翻译的内容
- CSV 原始列名（全数据表保持英文原名）
- 技术单位: kWh/t, kPa, t/h, °C, A, %
- Events_Log 操作员原始描述
- 数值和单位符号

## 实现方式
- `translations.py` 中定义 `TRANSLATIONS = {"en": {...}, "zh": {...}, "fr": {...}}`
- `t(key, lang)` 辅助函数
- 语言切换器: `dcc.Store` 或 URL `?lang=zh`
- 默认语言: English
