Project Report: Land Energy OEE Dashboard Pilot (Project 4)
Date: October/November 2023 (Estimated from context) Client: Land Energy Consultant: DCIC / University Team Focus: Digitalization of the Pellet Production Line (Milling Process)
1. Executive Summary
The objective of this project ("Project 4") is to transition Land Energy from a manual, paper-based monitoring system to an automated digital dashboard. The pilot focuses on calculating Overall Equipment Effectiveness (OEE) for the Bulk Pellet Line.
The investigation reveals that while the necessary data exists within the plant’s systems, it is currently "trapped" inside proprietary software managed by an external Austrian vendor, Baumgartner Automation. The critical next step is not technical installation, but administrative negotiation: formally requesting Baumgartner to automate data exports (CSV files) to feed the new dashboard.
--------------------------------------------------------------------------------
2. Current Operational State ("As-Is" Analysis)
2.1 The "Siloed" Control Room
The control room setup is fragmented. As described in the audio and supported by the photos, there are approximately six different computer screens sitting side-by-side, but they do not talk to each other.
• Baumgartner (SCADA): Controls the pellet mills and critical machinery.
• Siemens WinCC: Displays status information.
• Thermo Scientific: Independent scale terminals displaying tonnage.
Audio Insight: The staff emphasized, "Don't let the number of keyboards fool you... they are all running in isolation".
2.2 Manual Data Recording
Currently, the plant relies on human operators to notice faults and manually write them down.
• The Process: When a machine stops, the operator looks at the alarm on the screen, then turns around and writes the fault code, time, and reason onto a whiteboard or Excel sheet.
• The Risk: Data entry is delayed. In one audio clip, a dryer tripped due to a conveyor fault (15-minute disruption). The operator noted that if he is busy fixing the jam, he might not record the data until 30 minutes later, leading to inaccurate "guesstimates" of downtime.
• Visual Context: Photos 140, 141, and 142 confirm this practice. They show whiteboards titled "Action Follow Up" and "Last 24 Hours" with handwritten notes like "Dry Grinder Vibration" and "Pellet Tonnage 282."
--------------------------------------------------------------------------------
3. Technical Architecture & Constraints
3.1 The "Black Box" Problem (Baumgartner)
The core of the production line is controlled by Baumgartner Automation (referred to phonetically as "Boomgardner" in the audio).
• Vendor Lock-in: Baumgartner manages the PLCs remotely via TeamViewer. Land Energy staff have "operational" access (buttons to run machines) but no "admin" access to the backend code or data logs.
• Data Availability: The system currently only stores local data for about one week.
• Connectivity: The plant is hardwired (Ethernet) which is the "gold standard" for these machines. However, "Project 6" is simultaneously installing Wi-Fi to cover blind spots.
3.2 Key Hardware Identified
• PLCs: Siemens Simatic Panels are used for local machine control. Photo 137 shows a dirty, well-used Siemens touch panel.
• Scales: Production output is measured by Thermo Scientific scales. Photo 139 clearly shows a reading of "11.02 t/h" (tons per hour), which matches the audio discussion about verifying live tonnage.
• Sensors: The machines monitor Amps (current), vibration, and temperature, but this data is currently only used for automatic tripping (safety stops) and is not being logged for analysis.
--------------------------------------------------------------------------------
4. Project Strategy: The OEE Dashboard
4.1 The Goal
The dashboard aims to visualize Weight over Time (Production Rate) correlated with Energy Usage and Downtime.
• Business Case: Land Energy aims to increase throughput from ~16 tons/hour to 20–24 tons/hour. To do this, they must identify exactly why and when the mills stop (micro-stoppages).
4.2 The Data Extraction Plan
The team decided against installing new sensors or "hacking" the PLCs, which would be risky and expensive. Instead, the strategy is Vendor Integration.
1. The "Ask": Land Energy will send a formal letter to Baumgartner.
2. The Requirement: Request a scheduled "Data Dump" (likely a CSV text file generated every hour) containing key tags: Status (On/Off), Fault Codes, Amps, and Tonnage.
3. Storage: This data will be moved from the local server to a cloud environment (or local Land Energy server) for the dashboard to read.
4.3 Future Vision (AI & Predictive Maintenance)
The audio frequently mentions that this dashboard is just "Step 1."
• Step 2: The long-term goal is Predictive Maintenance.
• Example: Using historical vibration and amp data to predict when a bearing is about to jam before it actually fails, preventing the 15-minute stops described earlier.


基于提供的录音和文档，以下是关于 Land Energy 项目 4 (Project 4)：整体设备效率 (OEE) 试点项目 的详细总结：

1. 项目背景与目标
该项目被称为“项目 4 (Project 4)”，是一个与 西苏格兰大学 (UWS) 合作的运营改进计划，旨在 Land Energy 的 Girvan 工厂实施 。


核心目标： 建立一个 OEE（整体设备效率）仪表板，以提高对停机时间、生产绩效和设备行为的可见性 。


商业目的： 通过识别流程瓶颈，支持工厂增加颗粒生产线吞吐量的长期野心（目标是产能翻倍/增加吨位）。
+1


资金情况： 项目已获得批准，总资金包含约 2.4 万英镑的赠款和 Land Energy 出资的 1.6 万英镑 。

2. 当前面临的挑战

数据孤岛与手动记录： 工厂拥有大量数据，但分散且未被利用 。目前，操作员需要手动查看多个独立的屏幕，并在 Excel 表格中手动记录停机原因和故障代码，这种方式效率低下且容易出错 。
+3


系统封闭性： 关键设备（特别是颗粒磨机）由供应商 Baumgartner (BG) 的 SCADA/PLC 系统控制。Land Energy 内部缺乏访问这些底层数据的权限或技能，依赖供应商进行远程控制 。
+2


缺乏预测性维护： 目前主要依赖故障后维修。项目的愿景是利用数据转向基于状态的维护（如振动、电流分析），最终实现 AI 辅助的预测性维护 。
+1

3. 实施方案与技术细节

试点范围： 初始试点将专注于 制粒/研磨工艺 (Milling Process)，特别是 3 台颗粒磨机 (Mills) 。
+1


数据获取策略： 团队决定不直接物理接入或修改 PLC，而是通过向供应商 Baumgartner 发出正式请求，要求其从 WinCC SCADA 系统中定期导出 CSV 格式 的数据文件 。
+2

所需关键数据点：


产量数据： 输送机秤测量的吨/小时 (T/h) 和累计吨数 。


状态数据： 3 台磨机的启动/停止指示器、时间戳及故障信息 。


能耗数据： 每台磨机的千瓦/吨 (kw/t) 和安培/吨 (Amps/ton) 。


筒仓数据： 各个筒仓的吨数和流量 。
