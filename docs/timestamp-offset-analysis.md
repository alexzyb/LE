# 时间戳偏移问题分析与修复指南

**记录日期**: 2026-05-21  
**问题状态**: 部分修复（Dashboard 侧已修，BG 侧待 Christian 修复）  
**涉及文件**: `src/data.py`, `src/ingest.py`, `land_energy.db`

---

## 背景

Dashboard 上线后发现图表时间比用户本地时间慢 **2 小时**。经排查，问题由两个独立原因叠加造成。

---

## 问题分解

### 原因 1：Dashboard 代码未做时区转换（已修复）

`data.py` 的 `get_live_df()` 函数从数据库读取 UTC 时间戳后直接返回，不做任何时区转换。Dashboard 拿到后直接画图，显示的是 UTC 时间。

英国夏令时（BST = UTC+1），用户本地时钟比 UTC 快 1 小时，因此图表比本地时钟慢 1 小时。

**修复**：`data.py` 加入 UTC → Europe/London 转换，自动处理 BST/GMT 切换：

```python
from zoneinfo import ZoneInfo
_TZ_LONDON = ZoneInfo("Europe/London")

# 在 get_live_df() 解析 Date Time 列之后：
df["Date Time"] = (
    df["Date Time"].dt.tz_localize("UTC")
    .dt.tz_convert(_TZ_LONDON)
    .dt.tz_localize(None)
)
```

- 夏天（BST）：自动 +1 小时
- 冬天（GMT）：自动 +0 小时
- **不需要手动随季节改代码**

### 原因 2：BG WinCC 测量时钟未应用夏令时（待 Christian 修复）

CSV 文件中有两个时间戳字段：

| 字段 | 含义 | 状态 |
|---|---|---|
| `timestamp_utc` | WinCC 实际采集数据的时间 | ❌ 比真实 UTC 慢 1 小时 |
| `sync_timestamp_utc` | 数据写入 CSV 的时间 | ✅ 正确，与真实 UTC 一致 |

实测对比（检查时真实 UTC ≈ 13:35）：
```
sync_timestamp_utc: 2026-05-21T13:35:42+00:00  ✓ 正确
timestamp_utc:      2026-05-21T12:35:24+00:00  ✗ 慢 1 小时
```

**结论**：数据本身是实时的（sync 时间正确），但 WinCC 采集时钟没有跟上 BST，导致测量时间戳系统性偏移 1 小时。`ingest.py` 使用 `timestamp_utc`，因此数据库里存的测量时间戳也慢 1 小时。

---

## 当前状态（修复后）

| 来源 | 差距 | 状态 |
|---|---|---|
| Dashboard 不转换时区 | 1 小时 | ✅ 已修复 |
| BG WinCC 时钟未应用 BST | 1 小时 | ⏳ 待 Christian 修复 |
| **合计** | **0 小时（修复后）** | |

修复 Dashboard 代码后，当前差距从 2 小时缩小到 1 小时。等 Christian 修好 BG 后归零。

---

## 常见问题解答

### Q: Dashboard 显示的时间慢，会影响数据库里的数据吗？

**不影响。** Dashboard 的显示是查询时的最后一步处理，不会反写数据库。数据库永远存原始值。

### Q: 对数据分析和机器学习有影响吗？

**基本没有影响。** 所有历史数据的时间标签系统性地偏移了相同的量，数据之间的相对时间关系完全正确。分析变量之间的关联性、趋势、周期性规律均不受影响。

唯一有影响的场景：需要将本系统数据与**外部数据源**（非 BG 系统）按时间对齐时，需注意 1 小时偏移。

### Q: 冬令时来了会自动正常吗？

**新数据会自动正常，历史数据不会自动修正。**

- 冬天（GMT = UTC+0）：BG 时钟本来就不应用 DST，冬天 GMT = UTC，自然对齐
- 我们的代码冬天自动 +0 小时（ZoneInfo 自动处理）
- 结果：新数据 0 小时延迟 ✓
- 但已存入数据库的夏季历史数据时间标签仍然偏移 1 小时，不会自动修正

### Q: Christian 修好后图表会出现什么现象？

修复前后的数据时间戳会有 **1 小时跳跃**（值连续，但标签不连续）：

```
修复前（慢1小时）    修复后（正确）
...13:29 → 13:30 ··· [跳1小时] ··· 14:31 → 14:32...
```

图表上看起来像中断了 1 小时，实际数据是连续的。

---

## 如何定位跳空时间点并修复历史数据

### 第一步：定位精确跳空时间点

已知 Christian 大概修复日期，在数据库中寻找连续两行之间时间差超过 50 分钟的位置（正常间隔是 30 秒）：

```python
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("src/land_energy.db")

conn = sqlite3.connect(str(DB_PATH))

# 替换为 Christian 告知的大概修复日期
approx_date = "2026-XX-XX"

df = pd.read_sql_query(
    f'SELECT "Date Time" FROM live_data '
    f'WHERE "Date Time" >= "{approx_date}" '
    f'ORDER BY "Date Time"',
    conn
)
conn.close()

df["Date Time"] = pd.to_datetime(df["Date Time"])
df["gap_minutes"] = df["Date Time"].diff().dt.total_seconds() / 60

# 找出间隔超过 50 分钟的行（正常是 0.5 分钟）
jumps = df[df["gap_minutes"] > 50]
print(jumps[["Date Time", "gap_minutes"]])
```

输出示例：
```
         Date Time        gap_minutes
1234  2026-10-25 10:31:00    61.5
```

`2026-10-25 10:31:00` 即为跳空点，之前所有数据需要 +1 小时修正。

### 第二步：修复历史数据（SQL）

确认跳空时间点后，对该时间点之前的所有记录加 1 小时：

```sql
-- 先备份（可选但推荐）
CREATE TABLE live_data_backup AS SELECT * FROM live_data;

-- 修正历史时间戳（将 CUTOVER_TIMESTAMP 替换为第一步找到的跳空时间点）
UPDATE live_data
SET "Date Time" = datetime("Date Time", '+1 hour')
WHERE "Date Time" < 'CUTOVER_TIMESTAMP';

-- 验证：检查修正前后的连续性
SELECT "Date Time" FROM live_data
WHERE "Date Time" BETWEEN 'CUTOVER_TIMESTAMP - 5min' AND 'CUTOVER_TIMESTAMP + 5min'
ORDER BY "Date Time";
```

### 第三步：验证

```python
# 重新查询跳空附近的数据，确认时间戳连续
df_check = pd.read_sql_query(
    'SELECT "Date Time" FROM live_data '
    'WHERE "Date Time" >= "CUTOVER_MINUS_10MIN" '
    'AND "Date Time" <= "CUTOVER_PLUS_10MIN" '
    'ORDER BY "Date Time"',
    conn
)
df_check["gap"] = pd.to_datetime(df_check["Date Time"]).diff().dt.total_seconds()
print(df_check)  # 所有 gap 应约为 30 秒
```

---

## 注意事项

1. **修正 DB 前务必备份** `land_energy.db`
2. **记录 Christian 告知的修复时间**，越精确越好（精确到分钟），作为跳空定位的参考
3. 修正 DB 后，`data.py` 中的 UTC→BST 转换代码**保持不变**（历史数据修正后变成正确 UTC，+1h 转换依然正确）
4. 如果不做 DB 修正，对日常实时监控无影响；只在做跨时段精确数据分析时才需要修正

---

## 文件变更记录

| 文件 | 改动 | 日期 |
|---|---|---|
| `src/data.py` | 新增 `from zoneinfo import ZoneInfo` + `_TZ_LONDON`；`get_live_df()` 加 UTC→London 转换 | 2026-05-21 |
| `docs/timestamp-offset-analysis.md` | 本文件，记录问题分析与修复方案 | 2026-05-21 |
