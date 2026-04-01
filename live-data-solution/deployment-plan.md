# Live Data 本地部署实施方案

**日期**: 2026-03-05
**目标**: 在 LE 工厂服务器上部署 VM，接入 BG 实时 CSV 数据，运行 Dashboard

---

## Context

Land Energy (LE) 的 SCADA 供应商 Baumgartner (BG) 通过 CDC 服务将传感器数据导出为 CSV 文件，存放在工厂本地服务器上。CDC 每 10 秒扫描一次 WinCC 数据库，将新记录批量追加到对应 CSV 文件（传感器实际采样频率约 2-3 秒）。

当前 Dashboard 是 Python Dash + SQLite 架构，基于一次性导入的历史 CSV 运行。本方案在 LE 服务器上部署 Ubuntu VM，通过 PostgreSQL 接收实时数据，实现 Dashboard 内网实时访问。

**关键邮件确认（dataexport.txt & details.txt）**:
- BG 支持 CSV / TSV / JSONL 格式
- BG 支持「每变量一个文件」或「所有变量合并为一个文件」
- 我们选择：按大类合并（如 Pellet_Mill_1 下所有传感器合为一个 CSV），每天一个文件
- BG 需要 LE 提供：① 最终数据点清单 ② CSV 存放路径

---

## 一、VM 配置

在 LE 工厂服务器（Windows Server）上使用 Hyper-V 创建虚拟机。

### 硬件配置

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| **OS** | Ubuntu Server 22.04 LTS | 轻量稳定，Python/PostgreSQL 原生支持 |
| **CPU** | 2 vCPU | ingest.py + PostgreSQL + Dash app 三个服务，2 核足够 |
| **RAM** | 4 GB | PostgreSQL 缓存 ~1GB + Python 进程 ~512MB + 系统 ~1GB，留有余量 |
| **磁盘** | 80 GB SSD | 系统 ~5GB + PostgreSQL 数据一年 ~3GB + 日志/备份，充足 |
| **网络** | External Virtual Switch | VM 获得与宿主机同网段的内网 IP，工厂任何电脑可直接访问 |

### 数据量估算

- 传感器采样频率 ~3 秒，约 40 个传感器
- 每天约 115 万行（合并为宽表后约 28,800 行 × 40 列）
- 每天数据量约 5-15 MB
- 一年约 2-5 GB
- PostgreSQL 轻松处理，80 GB 磁盘绰绰有余

### Hyper-V 创建步骤

```
1. 宿主机 → 服务器管理器 → 添加角色 → 启用 Hyper-V（如尚未启用）
2. 下载 Ubuntu Server 22.04 LTS ISO（~2GB）
3. Hyper-V 管理器 → 新建 → 虚拟机：
   - 名称: LE-Dashboard
   - 代数: 第 2 代（Generation 2）
   - 内存: 4096 MB（取消动态内存）
   - 网络: 选择 External Virtual Switch
   - 硬盘: 80 GB（动态扩展）
   - 安装: 挂载 Ubuntu ISO
4. 设置 → 安全 → 取消勾选"启用安全启动"（Ubuntu 需要）
5. 启动 VM → 按提示安装 Ubuntu Server（~20 分钟）
6. 安装完成 → 记录 VM 内网 IP（如 192.168.1.100）
```

---

## 二、VM 访问宿主机 CSV 文件夹

BG 的 CSV 导出在宿主机（或同网络机器）的某个文件夹中（如 `D:\BG_Export\`）。VM 通过 SMB 网络共享只读挂载。

### 宿主机操作（Windows）

```
1. 右键 D:\BG_Export → 属性 → 共享 → 高级共享
2. 勾选"共享此文件夹"，共享名: BG_Export
3. 权限 → 添加用户（如 dashboard_reader）→ 只读权限
```

### VM 操作（Ubuntu）

```bash
# 安装 SMB 客户端
sudo apt install cifs-utils -y

# 创建挂载点
sudo mkdir -p /mnt/bg_export

# 创建凭据文件
sudo bash -c 'cat > /etc/samba/bg_creds << EOF
username=dashboard_reader
password=<密码>
domain=WORKGROUP
EOF'
sudo chmod 600 /etc/samba/bg_creds

# 测试挂载
sudo mount -t cifs //宿主机IP/BG_Export /mnt/bg_export \
    -o credentials=/etc/samba/bg_creds,ro,iocharset=utf8

# 验证
ls /mnt/bg_export/Pellet_Mill_1/

# 写入 fstab 开机自动挂载
echo '//宿主机IP/BG_Export /mnt/bg_export cifs credentials=/etc/samba/bg_creds,ro,iocharset=utf8,_netdev 0 0' \
    | sudo tee -a /etc/fstab
```

> `ro` = 只读挂载，VM 只读不写，保护 BG 原始文件安全。

### 文件夹结构（按大类合并方案）

```
/mnt/bg_export/
├── Pellet_Mill_1/
│   ├── 2026-03-05.csv    ← 每天一个文件，包含 timestamp + 所有 Mill 1 传感器列
│   ├── 2026-03-06.csv
│   └── ...
├── Pellet_Mill_2/
├── Pellet_Mill_3/
├── Dryer/
├── Throughput/
└── CHP/
```

每个 CSV 内部结构示例（`Pellet_Mill_1/2026-03-05.csv`）：
```
timestamp,act_Current,act_Speed,Roller_temp_left,Roller_temp_right,kWh_T,Feeder_pct
2026-03-05T08:00:00,285.3,1550,62.1,63.4,18.2,75.0
2026-03-05T08:00:03,286.1,1550,62.2,63.5,18.3,75.0
2026-03-05T08:00:06,284.8,1549,62.1,63.4,18.1,75.0
...
```

---

## 三、PostgreSQL 安装与配置

### 安装

```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl enable postgresql
```

### 建库建用户

```bash
sudo -u postgres psql <<EOF
CREATE USER dashboard WITH PASSWORD '<密码>';
CREATE DATABASE landenergy OWNER dashboard;
\c landenergy
-- 授权
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dashboard;
EOF
```

### 建表

```sql
-- 实时数据主表：所有大类传感器合并到一张宽表（和现有 shift_protocol 结构对齐）
CREATE TABLE live_data (
    datetime    TIMESTAMP PRIMARY KEY,
    -- Pellet Mill 1
    pm1_current         REAL,
    pm1_speed           REAL,
    pm1_roller_temp_l   REAL,
    pm1_roller_temp_r   REAL,
    pm1_kwh_t           REAL,
    pm1_feeder_pct      REAL,
    -- Pellet Mill 2
    pm2_current         REAL,
    pm2_speed           REAL,
    pm2_roller_temp_l   REAL,
    pm2_roller_temp_r   REAL,
    pm2_kwh_t           REAL,
    pm2_feeder_pct      REAL,
    -- Pellet Mill 3（同上结构）
    pm3_current         REAL,
    pm3_speed           REAL,
    pm3_roller_temp_l   REAL,
    pm3_roller_temp_r   REAL,
    pm3_kwh_t           REAL,
    pm3_feeder_pct      REAL,
    -- Dryer
    dryer_tonnage       REAL,
    dryer_moisture_out  REAL,
    dryer_outfeed       REAL,
    dry_silo_1_pct      REAL,
    dry_silo_2_pct      REAL,
    -- Throughput
    belt_weigher_th     REAL,
    belt_weigher_cum    REAL,
    pellet_silo_1       REAL,
    pellet_silo_2       REAL,
    pellet_silo_3       REAL,
    -- CHP
    furnace_temp        REAL,
    thermal_oil_out     REAL,
    turbine_power_kw    REAL
    -- ... 根据最终确认的数据点清单扩展
);

CREATE INDEX idx_live_datetime ON live_data (datetime DESC);
```

---

## 四、ingest.py — 数据采集脚本

### 核心逻辑

```
循环（每 5 秒）:
    for 每个大类文件夹 (Pellet_Mill_1, Dryer, ...):
        打开今天的 CSV 文件
        从上次读取的字节位置继续读
        解析新增行（跳过不完整行）
        按 timestamp 合并各大类数据
        INSERT INTO live_data（ON CONFLICT 忽略重复）
```

### 关键设计

1. **文件偏移量追踪**: 用字典记录每个 CSV 读到的字节位置，只读新增行，不重复处理
2. **不完整行处理**: BG 说 "between writes, unfinished CSV may be read"。如果一行列数不够，跳过，下次再读
3. **多文件按 timestamp 合并**: 各大类 CSV 独立文件，ingest.py 读取后按 timestamp 合并到同一行写入数据库
4. **ON CONFLICT DO UPDATE**: 如果同一时间戳的数据分多次写入（不同大类先后到达），用 UPSERT 合并

### 自动恢复机制

```python
# 最外层 while True + try/except，任何异常都不会导致进程退出
def main():
    while True:
        try:
            run_ingest_loop()
        except Exception as e:
            logging.error(f"异常: {e}")
            time.sleep(10)  # 等 10 秒自动重试
```

加上 systemd 的 `Restart=always`，双重保障：
- Python 内部异常 → try/except 捕获，继续运行
- 进程彻底崩溃（如内存溢出）→ systemd 10 秒后自动重启进程

---

## 五、Dashboard 代码改动

### `src/data.py` — 改动最小化

```python
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def _open():
    if DATABASE_URL:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    else:
        import sqlite3
        return sqlite3.connect(DB_PATH)
```

- 有 DATABASE_URL 环境变量 → 用 PostgreSQL（生产环境）
- 没有 → 用 SQLite（本地开发 / Demo 演示）
- SQL 查询语句基本不变（PostgreSQL 兼容 SQLite 的基础 SQL）

### `src/app.py` — 微调

- 默认时间范围从固定的 `2026-01-01 ~ 2026-02-01` 改为 `datetime.now()` 的当天
- auto-refresh 已有（Phase 7 实现的 5s/30s/1min），无需改动
- 可选：加一个数据源切换（Demo Data / Live Data）

### 新增 `src/ingest.py`

- 完整的数据采集脚本（见第四节设计）
- 约 150-200 行代码

### 新增依赖

```
psycopg2-binary   # PostgreSQL Python 驱动
```

---

## 六、systemd 服务注册

### ingest 服务

```ini
# /etc/systemd/system/le-ingest.service
[Unit]
Description=LE Live Data Ingestion
After=network.target postgresql.service mnt-bg_export.mount

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/le-dashboard
Environment=DATABASE_URL=postgresql://dashboard:<密码>@localhost:5432/landenergy
Environment=BG_EXPORT_DIR=/mnt/bg_export
ExecStart=/opt/le-dashboard/venv/bin/python src/ingest.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Dashboard 服务

```ini
# /etc/systemd/system/le-dashboard.service
[Unit]
Description=LE Dashboard Web App
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/le-dashboard
Environment=DATABASE_URL=postgresql://dashboard:<密码>@localhost:5432/landenergy
ExecStart=/opt/le-dashboard/venv/bin/gunicorn src.app:server -b 0.0.0.0:8050 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 启动

```bash
sudo systemctl daemon-reload
sudo systemctl enable le-ingest le-dashboard
sudo systemctl start le-ingest le-dashboard

# 查看状态
sudo systemctl status le-ingest
sudo systemctl status le-dashboard

# 查看日志
journalctl -u le-ingest -f
journalctl -u le-dashboard -f
```

---

## 七、内网访问

部署完成后，工厂内网任何电脑浏览器打开：

```
http://<VM_IP>:8050
```

例如：`http://192.168.1.100:8050`

可选优化：
- 让 LE 的 IT 在内网 DNS 加一条记录 → `http://le-dashboard:8050`
- 装 Nginx 反向代理 → 用 80 端口访问（不用输 :8050）

---

## 八、开发工作流（Laptop 开发 → VM 部署）

### 流程

```
Laptop（开发机，有 Claude Code）
    │
    ├── VPN 连入 LE 内网
    ├── 映射网络驱动器访问 BG CSV（如 Z:\BG_Export\）
    ├── 本地 PostgreSQL 或 SQLite 做测试
    ├── Claude Code 协助开发 ingest.py、改 data.py
    ├── 本地测试通过
    └── git push 到 GitHub
         │
         ▼
VM（生产机，无 Claude Code）
    │
    ├── git pull 拉取最新代码
    ├── sudo systemctl restart le-ingest le-dashboard
    └── 完成部署（30 秒）
```

### Laptop 上的环境变量

```bash
# Windows（Laptop）
set BG_EXPORT_DIR=Z:\BG_Export
set DATABASE_URL=postgresql://user:pass@localhost:5432/landenergy
# 或者不设 DATABASE_URL，默认用 SQLite 测试
```

### VM 上的环境变量

```bash
# Ubuntu（VM）— 通过 systemd 或 .env 文件设置
BG_EXPORT_DIR=/mnt/bg_export
DATABASE_URL=postgresql://dashboard:<密码>@localhost:5432/landenergy
```

### 代码中用环境变量适配两种环境

```python
import os
BG_EXPORT_DIR = os.environ.get("BG_EXPORT_DIR", r"Z:\BG_Export")  # Laptop 默认值
DATABASE_URL = os.environ.get("DATABASE_URL")  # None → 用 SQLite
```

### 更新部署步骤

```bash
# Laptop 上改好代码后
git add . && git commit -m "fix xxx" && git push

# SSH 到 VM
ssh ubuntu@192.168.1.100
cd /opt/le-dashboard
git pull
sudo systemctl restart le-ingest le-dashboard
```

---

## 九、需要修改的文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/ingest.py` | **新建** | 数据采集脚本（~200 行） |
| `src/data.py` | **微调** | `_open()` 函数支持 PostgreSQL 连接 |
| `src/app.py` | **微调** | 默认时间范围改为当天 |
| `requirements.txt` | **新增一行** | `psycopg2-binary` |

现有的 `charts.py`、`config.py`、`translations.py`、`style.css` **均不需要改动**。

---

## 十、验证步骤

1. **VM 网络**: 从工厂内网电脑 ping VM 的 IP
2. **文件夹挂载**: VM 内 `ls /mnt/bg_export/Pellet_Mill_1/` 能看到 CSV 文件
3. **PostgreSQL**: `psql -U dashboard -d landenergy -c "SELECT 1"`
4. **ingest.py**: 启动后检查 `SELECT count(*) FROM live_data` 是否持续增长
5. **Dashboard**: 浏览器打开 `http://VM_IP:8050`，确认数据显示且 auto-refresh 正常
6. **崩溃恢复**: `sudo systemctl kill le-ingest`，等待 10 秒，确认自动重启
7. **重启恢复**: 重启 VM，确认两个服务自动启动 + 文件夹自动挂载

---

## 十一、去 LE 需要确认的事项

1. LE 服务器是否已启用 Hyper-V（或者用什么虚拟化方案）
2. BG 导出 CSV 的具体文件夹路径
3. LE 服务器能否分配 2 vCPU + 4GB RAM + 80GB 给 VM
4. 是否需要 IT 配合设置网络共享和防火墙（开放 8050 端口）
5. 是否可以给你开 VPN + SSH 访问 VM 的权限（方便远程开发和维护）
6. BG 提供的完整传感器数据点清单（Pellet_Mill_1 只是示例之一）
