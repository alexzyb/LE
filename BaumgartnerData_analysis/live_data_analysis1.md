# L Energy 数据对话总结（重点：CSV / Totalizer / 异常值 / Dashboard）

## 1. 文档目的
这份文档用于总结本轮关于 **L Energy / Land Energy live CSV 数据** 的全部关键讨论，重点覆盖：

- 数据公司给出的原始说明与其含义
- CSV 数据结构与两个时间戳的解释
- 各文件的 `value_id / value_name / frequency`
- Totalizer / Infeed Totalizer / Fuel Level 的业务理解
- 对 `Complete Plant Totaliser`、`Silo Infeed Totaliser`、`Bagging Totaliser`、`Truck Totaliser` 的关系分析
- 已发现的异常值与系统性异常
- 对实时 Dashboard / ETL / 数据清洗的建议

---

## 2. 你之前发来的“数据公司回复”原文（完整列出）

### 2.1 关于 CSV 格式与 CDC 的回复（原文）
> We chose a format that is suitable for both batch export + continuous change data capture of time series raw data: one record per row. For performance reasons, incoming records are appended at the ends of the files.
>
> The assumption was to write raw data into CSV files which could then (after export) be postprocessed by you and transformed into frontend-ready data through SQL queries, e. g. using DuckDB.

### 2.2 关于 WinCC / 连接方式 / 凭据处理的回复（原文）
> Thank you for the update.
>
> Our understanding is that our program is running on the same machine as WinCC and writes the CSV files to a network drive. This setup implicates that credentials are not actively handled by our program code.
>
> The connection string is credential-less: (example) Server=BGA-SOFT-VMS\WINCC;Integrated Security=True;Encrypt=False;TrustServerCertificate=True;Command Timeout=120;
>
> and the destination directory access for writing the CSV files should be a standard Windows path.
>
> Please confirm or describe your differing situation in detail.

---

## 3. 这些回复的核心含义

### 3.1 “one record per row” 的真正含义
数据公司明确说明：
- 他们输出的是 **长表（long-table）格式**
- 一行只表示 **某一个 tag / value_id 在某一个时间点的一个数值**
- 而不是“每个时间点一整行、多个变量分别占不同列”的宽表

也就是说，它的本质是：

| value_id | value_name | timestamp_utc | real_value |
|---:|---|---|---:|
| 62 | Actual_Speed_Dosing_Screw | 2024-03-22 08:27:00 | ... |
| 62 | Actual_Speed_Dosing_Screw | 2024-03-22 08:27:01 | ... |
| 66 | Actual_Current | 2024-03-22 08:27:00 | ... |

这种结构**适合原始时序数据落地与追加写入**，但**不适合直接做最终 Dashboard 展示**。

### 3.2 “incoming records are appended at the ends of the files”
这表示：
- 新数据会不断 **append 到文件末尾**
- 不会回写到文件中间
- 这对写入性能有利

但副作用是：
- 文件会持续增大
- 如果前端直接读取 CSV，会越来越慢
- 更适合后续做 ETL / SQL / DuckDB / 时序数据库再加工

### 3.3 “postprocessed by you … transformed into frontend-ready data”
这句话很关键。它实际上说明：
- 数据公司**并不打算直接给你一个前端可用的成品表**
- 他们给的是 **raw export**
- 他们默认你这边会再做：
  - 清洗
  - 排序
  - 透视（pivot）
  - 对齐时间轴
  - 生成 Dashboard 可用结构

所以，CSV 本来就不是最终报表层，而是 **原始层 / raw layer**。

---

## 4. 当前已分析的 CSV 文件
本轮已分析的文件包括：

- `Pellet_Mill_1.csv`
- `Pellet_Mill_2.csv`
- `Pellet_Mill_3.csv`
- `Pellet_Silo_1.csv`
- `Pellet_Silo_2.csv`
- `Pellet_Silo_3.csv`
- `Complete_Plant.csv`
- `Bagging_Station.csv`
- `Truck_Loading_Station.csv`

---

## 5. CSV 字段结构解释

所有文件结构一致，字段如下：

- `value_id`：变量 / 测点 ID
- `value_name`：变量名称
- `timestamp_utc`：原始测量时间
- `real_value`：测量值
- `sync_id`：同步批次 ID
- `sync_timestamp_utc`：该条数据被同步 / 导出到 CSV 的时间

### 5.1 两个时间戳的解释
#### `timestamp_utc`
表示：
- 这条数据原本什么时候被机器 / historian / SCADA 记录下来

#### `sync_timestamp_utc`
表示：
- 这条历史数据是什么时候被同步 / 导出到 CSV 的

### 5.2 对两个时间戳的业务理解
从实际数据看，存在大量情况：

- `timestamp_utc` 很旧（例如 2021 / 2022 / 2024）
- `sync_timestamp_utc` 很新（例如 2026-03-26）

因此可以推断：
- 这不是纯实时当前值
- 而更像是一个导出程序在 **分批把历史数据扫出来，写入 CSV**

### 5.3 `sync_id`
从数据规律看，`sync_id` 基本等于 `sync_timestamp_utc` 的 Unix 毫秒时间戳，因此它更像：
- “这批导出的唯一批次编号”
- 实际上由同步时间直接生成

---

## 6. 各文件 frequency（频率）总结

### 6.1 `Pellet_Mill_1.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 62 | Actual_Speed_Dosing_Screw | 8000 | 1 秒 |
| 66 | Actual_Current | 8000 | 1 秒 |
| 67 | Left_Roller_Temperature | 8000 | 1 秒 |
| 68 | Right_Roller_Temperature | 8000 | 1 秒 |
| 171 | Energy | 8000 | 5 秒 |

结论：
- 主体信号：1 秒
- Energy：5 秒

---

### 6.2 `Pellet_Mill_2.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 64 | Actual_Speed_Dosing_Screw | 8000 | 1 秒 |
| 69 | Actual_Current | 8000 | 1 秒 |
| 70 | Left_Roller_Temperature | 8000 | 1 秒 |
| 71 | Right_Roller_Temperature | 8000 | 1 秒 |
| 173 | Energy | 7000 | 5 秒 |

结论：
- 主体信号：1 秒
- Energy：5 秒

---

### 6.3 `Pellet_Mill_3.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 114 | Actual_Speed_Dosing_Screw | 8000 | 1 秒 |
| 117 | Actual_Current | 8000 | 1 秒 |
| 118 | Left_Roller_Temperature | 8000 | 1 秒 |
| 119 | Right_Roller_Temperature | 8000 | 1 秒 |
| 172 | Energy | 8000 | 5 秒 |

结论：
- 主体信号：1 秒
- Energy：5 秒

---

### 6.4 `Complete_Plant.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 74 | Totaliser | 8000 | 30 秒 |
| 75 | Production | 8000 | 30 秒 |

结论：
- 两个变量都为 30 秒

---

### 6.5 `Pellet_Silo_1.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 150 | Fuel_Level | 8000 | 1 小时 |
| 157 | Infeed_Totaliser | 8000 | 1 小时 |

### 6.6 `Pellet_Silo_2.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 149 | Fuel_Level | 8000 | 1 小时 |
| 156 | Infeed_Totaliser | 8000 | 1 小时 |

### 6.7 `Pellet_Silo_3.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 148 | Fuel_Level | 8000 | 1 小时 |
| 155 | Infeed_Totaliser | 8000 | 1 小时 |

### 6.8 `Bagging_Station.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 152 | Totaliser | 8000 | 1 小时 |

### 6.9 `Truck_Loading_Station.csv`
| value_id | value_name | count | frequency |
|---:|---|---:|---|
| 159 | Totaliser | 8000 | 1 小时 |

---

## 7. value_id / value_name 总览

### 7.1 Pellet Mills（3 个文件）
总共有 15 个 `value_id`，但变量类型实际上只有 5 类：

- Actual_Speed_Dosing_Screw
- Actual_Current
- Left_Roller_Temperature
- Right_Roller_Temperature
- Energy

按文件分布：

#### Pellet_Mill_1
- 62 → Actual_Speed_Dosing_Screw
- 66 → Actual_Current
- 67 → Left_Roller_Temperature
- 68 → Right_Roller_Temperature
- 171 → Energy

#### Pellet_Mill_2
- 64 → Actual_Speed_Dosing_Screw
- 69 → Actual_Current
- 70 → Left_Roller_Temperature
- 71 → Right_Roller_Temperature
- 173 → Energy

#### Pellet_Mill_3
- 114 → Actual_Speed_Dosing_Screw
- 117 → Actual_Current
- 118 → Left_Roller_Temperature
- 119 → Right_Roller_Temperature
- 172 → Energy

### 7.2 Pellet Silos（3 个文件）
总共有 6 个 `value_id`，变量类型实际上只有 2 类：

- Fuel_Level
- Infeed_Totaliser

#### Pellet_Silo_1
- 150 → Fuel_Level
- 157 → Infeed_Totaliser

#### Pellet_Silo_2
- 149 → Fuel_Level
- 156 → Infeed_Totaliser

#### Pellet_Silo_3
- 148 → Fuel_Level
- 155 → Infeed_Totaliser

### 7.3 Complete Plant
- 74 → Totaliser
- 75 → Production

### 7.4 Bagging Station
- 152 → Totaliser

### 7.5 Truck Loading Station
- 159 → Totaliser

### 7.6 总计
本轮数据中总共有 **25 个不同的 value_id**。

---

## 8. 关于 Dashboard：当前 raw CSV 是否适合直接做实时 Dashboard

结论：
- **适合作为 raw 数据落地格式**
- **不适合作为最终直接供 Dashboard 展示的结构**

### 8.1 原因 1：它是长表，不是宽表
当前结构是一行一个点位一个时刻一个数值。  
而 Dashboard 往往更适合：

| timestamp_utc | tag_A | tag_B | tag_C |
|---|---:|---:|---:|

因此需要先做：
- pivot / reshape
- 按 timestamp 对齐

### 8.2 原因 2：混合频率
例如 Pellet Mill 同时存在：
- 1 秒数据
- 5 秒数据

如果直接透视成列，会出现空值，需要后续处理：
- 保留空值
- forward fill
- resample 到统一周期（例如 5 秒或 10 秒）

### 8.3 原因 3：全文件不一定全局按时间排序
对单个 `value_id` 来说，时间基本有序；  
但整个文件不是“所有点位按统一时间戳交错排好”的结构，因此如果直接做图，会不方便。

### 8.4 更合理的两层结构
#### Raw Layer
继续保留现在的 CSV 长表结构。

#### Dashboard Layer
按设备分别生成宽表，例如：

- `pellet_mill_1_live`
- `pellet_mill_2_live`
- `pellet_mill_3_live`
- `complete_plant_live`
- `pellet_silo_1_live`
- `pellet_silo_2_live`
- `pellet_silo_3_live`
- `dispatch_live`

这样后续无论接：
- Plotly Dash
- Power BI
- Grafana
- Streamlit

都会容易很多。

---

## 9. 关于 Totalizer / Totaliser / Infeed Totaliser 的业务逻辑讨论总结

### 9.1 三类关键 Totaliser
本轮讨论中，重点关注的 Totaliser 包括：

1. **Complete Plant Totaliser**  
   - 表示总厂生产累计
   - 位置上更像总出口 / 总皮带秤
   - 更接近“总产量”

2. **Pellet Silo 1/2/3 Infeed Totaliser**  
   - 表示进入各个料仓的累计量
   - 更接近“入仓量 / 内部分流量”

3. **Bagging / Truck Loading Totaliser**  
   - 表示最终出厂 / 发货累计
   - 更接近“销售 / 发运量”

### 9.2 关于“Complete Plant = Silo 1 + 2 + 3” 的疑问
讨论中曾提出一种直觉：
- `Complete Plant Totaliser` 是否等于 `Silo 1 + Silo 2 + Silo 3`

更谨慎、公正的结论是：

**不能直接这样写成一个简单恒等式。**

原因有两类：

#### 业务逻辑层面
真实工厂中可能存在：
- 直接旁路到 Truck
- 直接旁路到 Bagging
- 粉尘 / 筛分损耗
- 中间缓冲 / 存货变化

因此概念上就已经不一定严格满足：
- `Complete Plant = Silo1 + Silo2 + Silo3`

#### 数据质量层面
更重要的是，当前上传的 Silo / Bagging / Truck 原始数据本身存在明显异常（后文详述），因此在数据未清洗前，根本不适合拿来做物料守恒公式验证。

### 9.3 关于“Truck + Bagging = 总发货量”
概念上，这句话是合理的：
- Truck 表示散装发货
- Bagging 表示包装发货
- 两者合起来更接近总 dispatch

但在当前 raw 数据里：
- Bagging 有异常暴涨
- Truck 有归零与恢复
因此**原始值未经清洗前不能直接拿来做精确业务报表**。

### 9.4 本轮最稳妥的业务建议
如果当前目的是找一个相对可信的“生产基准”指标，那么：
- **Complete_Plant.csv 中的 `Totaliser`**
- **Complete_Plant.csv 中的 `Production`**

在这批样本里看起来最干净、最稳定。

---

## 10. 异常值扫描总结（重点）

本轮重新基于你实际上传的 CSV 扫描后，结论非常明确：

> **异常值确实存在，而且不是零星个例，而是明显的系统性异常。**

受影响最大的包括：
- `Pellet_Silo_1/2/3.csv` 里的 `Infeed_Totaliser`
- `Pellet_Silo_1/2/3.csv` 里的 `Fuel_Level`
- `Bagging_Station.csv` 里的 `Totaliser`
- `Truck_Loading_Station.csv` 里的 `Totaliser`

相对稳定的是：
- `Complete_Plant.csv` 里的 `Totaliser`
- `Complete_Plant.csv` 里的 `Production`

---

## 11. 最强异常证据：5 个累计器在同一时间一起归零

以下 5 个累计器：
- Bagging Totaliser
- Truck Totaliser
- Silo 1 Infeed Totaliser
- Silo 2 Infeed Totaliser
- Silo 3 Infeed Totaliser

在以下时间戳**同时等于 0**：

- `2022-03-24 22:00:00.270000+00:00`
- `2022-03-24 23:00:00.270000+00:00`
- `2022-03-25 00:00:00.270000+00:00`
- `2022-09-27 00:00:00.136000+00:00`
- `2022-09-27 01:00:00.311000+00:00`
- `2022-10-02 00:00:00.130000+00:00`

这非常不像真实生产行为，更像：
- historian / export / CDC 问题
- 系统重置
- 标定 / 单位切换
- 质量码缺失
- 导出逻辑异常

---

## 12. Silo Infeed Totaliser 的异常（已核实）

### 12.1 Silo 1 Infeed Totaliser（ID 157）
#### 早期较正常量级
- `2022-03-25 01:00:00.310000+00:00`
- `real_value = 69561.0625`

#### 异常高值
- `2022-09-26 23:00:00.067000+00:00`
- `real_value = 1573233.5`

#### 紧接着被重置为 0
- `2022-09-27 00:00:00.136000+00:00`
- `real_value = 0.0`

#### 又恢复到百万级
- `2022-09-27 02:00:00.311000+00:00`
- `real_value = 1573233.5`

#### 更高峰值
- `2022-10-08 03:00:00.099000+00:00`
- `real_value = 1979640.5`

---

### 12.2 Silo 2 Infeed Totaliser（ID 156）
#### 较早值
- `2022-03-25 01:00:00.310000+00:00`
- `real_value = 275838.1875`

#### 异常高值
- `2022-09-26 23:00:00.067000+00:00`
- `real_value = 1446273.75`

#### 重置为 0
- `2022-09-27 00:00:00.136000+00:00`
- `real_value = 0.0`

#### 再恢复
- `2022-09-27 02:00:00.311000+00:00`
- `real_value = 1446282.25`

#### 更高峰值
- `2022-10-08 18:00:00.099000+00:00`
- `real_value = 1446384.25`

---

### 12.3 Silo 3 Infeed Totaliser（ID 155）
#### 较早值
- `2022-03-25 01:00:00.310000+00:00`
- `real_value = 99283.3125`

#### 异常高值
- `2022-09-26 23:00:00.067000+00:00`
- `real_value = 1721889.75`

#### 归零
- `2022-09-27 00:00:00.136000+00:00`
- `real_value = 0.0`

#### 再恢复
- `2022-09-27 02:00:00.311000+00:00`
- `real_value = 1721889.75`

#### 更高峰值
- `2022-10-11 11:00:00.099000+00:00`
- `real_value = 2130433.25`

---

## 13. Fuel_Level 的异常（已核实）

### 13.1 Silo 1 Fuel_Level（ID 150）
#### 异常高值
- `2022-09-27 02:00:00.311000+00:00`
- `real_value = 406270.5`

#### 异常负值
- `2022-10-03 10:00:00.476000+00:00`
- `real_value = -406642.0`

---

### 13.2 Silo 2 Fuel_Level（ID 149）
#### 异常高值
- `2022-07-22 07:00:00.417000+00:00`
- `real_value = 1169041.5`

#### 巨大跳变点
- `2022-07-17 18:00:00.417000+00:00`
- `real_value = 779027.25`

#### 负值
- `2022-02-22 09:00:00.329000+00:00`
- `real_value = -467.375`

---

### 13.3 Silo 3 Fuel_Level（ID 148）
#### 异常高值
- `2022-10-02 11:00:00.150000+00:00`
- `real_value = 407694.5`

#### 异常负值
- `2022-08-27 14:00:00.259000+00:00`
- `real_value = -396322.75`

---

## 14. Bagging / Truck Totaliser 也存在异常

### 14.1 Bagging Totaliser（ID 152）
#### 2022-09-30 07:00 → 08:00
- `2022-09-30 07:00:00.007000+00:00` → `33369.324219`
- `2022-09-30 08:00:00.007000+00:00` → `440029.84375`

即：
- **1 小时内暴涨约 40.7 万**

#### 2022-10-02 00:00 → 02:00
- `2022-10-02 00:00:00.130000+00:00` → `0.0`
- `2022-10-02 02:00:00.150000+00:00` → `440081.8125`

---

### 14.2 Truck Totaliser（ID 159）
#### 2022-09-26 23:00 → 2022-09-27 02:00
- `2022-09-26 23:00:00.067000+00:00` → `282822.75`
- `2022-09-27 00:00:00.136000+00:00` → `0.0`
- `2022-09-27 02:00:00.311000+00:00` → `282822.75`

#### 2022-03-24 / 25 的同步归零
- `2022-03-24 22:00 / 23:00 / 00:00` → `0.0`
- `2022-03-25 01:00:00.310000+00:00` → `253989.09375`

---

## 15. Complete Plant 这份数据在当前样本里相对稳定

### 15.1 Totaliser（ID 74）
- 最小值：`639150.125`
- 最大值：`639889.5`
- 最大单步增量（30 秒间隔）：`0.25`
- 未见归零
- 未见大幅异常跳变
- 未见负向暴跌

### 15.2 Production（ID 75）
- 范围约：`2.208` 到 `13.248`
- 波动平稳
- 未见异常的极端尖峰或断崖式归零

### 15.3 当前最稳妥的结论
如果当前只是为了找到一个相对可信的生产基准指标，那么：
- `Complete Plant Totaliser`
- `Complete Plant Production`

在本轮上传样本里最可信。

---

## 16. 对业务建模的直接影响

### 16.1 不能在数据未清洗前直接验证
- `Complete Plant = Silo 1 + Silo 2 + Silo 3`
- `Truck + Bagging = Total Dispatch`

不是因为这些逻辑概念一定错，而是因为：
- 当前原始数据里存在大量异常重置 / 跳变 / 绝对值失真

因此：
> **在数据未清洗前，不能拿当前 raw totalizer 直接做严肃业务公式验证。**

### 16.2 先后顺序应该是
1. 先做异常检测
2. 再做清洗策略
3. 再做业务公式验证
4. 最后再做 Dashboard KPI

---

## 17. 针对数据公司 / 供应商最值得追问的问题

最值得发邮件追问的，不是单一的一个大值，而是这个更强的问题：

> 为什么 Bagging、Truck、Silo1 Infeed、Silo2 Infeed、Silo3 Infeed 会在完全相同的时间戳同时变成 0？

这个问题更能直接指向：
- 导出程序逻辑
- CDC 问题
- historian 重置
- 标定 / 单位切换
- 质量码 / status tag 缺失
- 传感器重新初始化
- PLC / WinCC 层的数据处理规则

---

## 18. 当前最稳妥的数据工程建议

### 18.1 先不要直接用原始累计值做 KPI
尤其不要直接拿以下 raw 数据算正式报表：
- Silo Infeed Totaliser
- Fuel_Level
- Bagging Totaliser
- Truck Totaliser

### 18.2 可以先优先用 `Complete_Plant.csv`
短期内更适合先用于：
- OEE / 生产趋势
- 基础产能图
- Totaliser hourly delta / daily delta

### 18.3 后续应建立的 ETL 流程
建议至少包含：

1. **按 `value_id + timestamp_utc` 去重**
2. **异常跳变识别**
   - 相邻差值阈值
   - 负值检查
   - 不可能上限检查
   - 同步归零模式识别
3. **质量标记**
   - 正常
   - 重置
   - 传感器异常
   - 疑似标定错误
4. **生成 Dashboard 宽表**
5. **将清洗前 / 清洗后分层保存**

### 18.4 适合 Dashboard 的表层建议
例如：

#### `complete_plant_live`
| timestamp_utc | totaliser | production |

#### `pellet_silo_1_live`
| timestamp_utc | fuel_level | infeed_totaliser | quality_flag |

#### `dispatch_live`
| timestamp_utc | truck_totaliser | bagging_totaliser | quality_flag |

---

## 19. 本轮最终结论（简明版）

1. 数据公司给的是 **raw CSV 长表**，不是前端成品表  
2. `timestamp_utc` 是原始测量时间；`sync_timestamp_utc` 是导出时间  
3. 当前数据明显包含 **历史回灌 / 同步导出** 行为  
4. frequency 结构已经识别清楚：  
   - Pellet Mills：1 秒 + 5 秒  
   - Complete Plant：30 秒  
   - Silos / Bagging / Truck：1 小时  
5. 当前 raw 数据里存在大量异常值，尤其是：
   - Silo Infeed Totaliser
   - Fuel_Level
   - Bagging Totaliser
   - Truck Totaliser
6. 最大的异常证据是：  
   - 5 个累计器在多个相同时间点**同时归零**
7. 在当前阶段，最可信的生产基准是：
   - `Complete Plant Totaliser`
   - `Complete Plant Production`
8. 在数据未清洗前，**不要直接用 raw totalizer 做严肃的物料守恒公式验证**
9. 最应向数据公司追问的问题是：
   - 为什么多个 Totalizer 会在完全相同的时间戳一起归零？

---

## 20. 后续最值得继续做的事
如果继续推进，最有价值的下一步通常是：

1. 做一张 **异常时间戳清单**
2. 给供应商写一封 **英文邮件**，把这些异常行和时间戳发过去
3. 设计一版 **数据清洗规则**
4. 再生成一版 **Dashboard-ready 宽表**
