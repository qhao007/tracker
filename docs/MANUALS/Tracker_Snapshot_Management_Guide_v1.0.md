# Tracker 快照运维管理指南 v1.0

> 本指南面向系统管理员和运维人员，说明如何管理和维护 Tracker 项目的快照功能。

---

## 目录

1. [概述](#概述)
2. [快照功能说明](#快照功能说明)
3. [手动创建快照](#手动创建快照)
4. [设置定期自动快照](#设置定期自动快照)
5. [查看和管理快照](#查看和管理快照)
6. [导出快照数据](#导出快照数据)
7. [删除快照](#删除快照)
8. [常见问题](#常见问题)

---

## 概述

### 什么是快照

快照（Snapshot）是项目在特定时间点的进度状态记录，包含：
- 快照日期
- 实际覆盖率（CP 覆盖率）
- TC 统计（总数、PASS 数量）
- 各 Priority 覆盖率（P0/P1/P2/P3）

### 快照的作用

| 用途 | 说明 |
|------|------|
| 进度追踪 | 记录项目在各时间点的验证进度 |
| 趋势分析 | 对比计划曲线与实际曲线，分析偏差 |
| 数据导出 | 导出历史数据用于离线分析 |
| 汇报材料 | 生成进度报告的原始数据 |

---

## 快照功能说明

### 快照存储位置

| 项目 | 路径 |
|------|------|
| 数据库 | `/projects/management/tracker/shared/data/{project_name}.db` |
| 表名 | `project_progress` |
| 备份目录 | `/projects/management/tracker/shared/data/backups/` |

### 快照数据结构

```sql
CREATE TABLE project_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    actual_coverage REAL,
    tc_total INTEGER,
    tc_pass_count INTEGER,
    p0_coverage REAL,
    p1_coverage REAL,
    p2_coverage REAL,
    p3_coverage REAL,
    progress_data TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, snapshot_date)
);
```

---

## 手动创建快照

### 通过 UI 创建（推荐）

适用于：临时需要记录当前进度、手动刷新等场景。

**操作步骤**：

1. **访问 Tracker**
   ```
   http://localhost:8080
   ```

2. **选择项目**
   - 从顶部下拉菜单选择要创建快照的项目

3. **进入进度图表页面**
   - 点击「Progress Charts」标签

4. **创建快照**
   - 点击「刷新快照」按钮
   - 系统自动采集当前项目状态

5. **确认结果**
   - 页面会显示新快照的覆盖率数据

### 通过 API 创建

适用于：自动化脚本、批量操作等场景。

**API 接口**：
```
POST /api/progress/{project_id}/snapshot
```

**请求示例**：
```bash
curl -X POST "http://localhost:8080/api/progress/1/snapshot" \
  -H "Content-Type: application/json" \
  -b "session=<your_session_cookie>"
```

**响应示例**：
```json
{
  "success": true,
  "message": "快照创建成功",
  "snapshot": {
    "id": 123,
    "snapshot_date": "2026-03-24",
    "actual_coverage": 36.6,
    "tc_total": 52,
    "tc_pass_count": 21
  }
}
```

---

## 设置定期自动快照

Tracker 本身不提供内置的定时快照功能，但可以通过以下方式实现：

### 方式一：通过 OpenClaw Cron Job（推荐）

适用于：已部署 OpenClaw 的环境。

**创建 Cron Job 步骤**：

1. **配置 CRON_API_TOKEN**

   在 systemd service 文件中配置环境变量 (`/etc/systemd/system/tracker.service`)：
   ```ini
   [Service]
   Environment="CRON_API_TOKEN=your-secure-token-here"
   ```

   生成安全 Token：
   ```bash
   openssl rand -hex 32
   ```

2. **验证 Token 配置**

   ```bash
   curl -X POST "http://localhost:8080/api/cron/progress-snapshot" \
     -H "X-API-Token: your-secure-token-here"
   ```

   成功响应：
   ```json
   {
     "success": true,
     "created_count": 3,
     "skipped_count": 2,
     "errors": [],
     "timestamp": "2026-04-03T22:00:00+08:00"
   }
   ```

3. **创建定时任务**
   - 建议频率：每周一次（周六或周日）
   - 时间：项目低负载时段

4. **配置任务内容**
   - 使用批量快照端点 `POST /api/cron/progress-snapshot`
   - **必须携带 `X-API-Token` Header**，否则返回 401 Unauthorized

5. **通知配置**
   - 快照失败时发送飞书通知
   - 成功时不通知（避免骚扰）

**Cron 表达式示例**：

| 频率 | 表达式 | 说明 |
|------|--------|------|
| 每周六 22:00 | `0 22 * * 6` | 每周六晚间 |
| 每两周周六 | `0 22 * * 6` (奇数周) | 每两周一次 |
| 每月最后一天 | `0 22 28-31 * *` | 月末 |

**OpenClaw Cron 配置示例**：
```json
{
  "name": "Tracker Weekly Snapshot",
  "schedule": {
    "kind": "cron",
    "expr": "0 22 * * 6",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "AUTONOMOUS: 定时抓取所有项目快照\n\n## 执行步骤\n\n### 1. 创建快照\n使用 Token 认证调用快照 API：\n```bash\ncurl -X POST \"http://localhost:8080/api/cron/progress-snapshot\" \\\n  -H \"X-API-Token: ${CRON_API_TOKEN}\" \\\n  -H \"Content-Type: application/json\"\n```\n\n### 2. 判断执行结果\n- 如果返回包含 `\"success\": true`，则快照创建成功\n- 否则为失败\n\n### 3. 发送飞书通知\n失败时发送飞书通知，成功时不通知。",
    "timeoutSeconds": 300
  }
}
```

### 方式二：通过独立脚本（Linux Crontab）

适用于：无 OpenClaw 环境。

**创建快照脚本**：
```bash
#!/bin/bash
# /opt/tracker/snapshot.sh

TRACKER_URL="http://localhost:8080"
CRON_TOKEN="your-secure-token-here"  # 必须配置

# 调用批量快照 API（自动处理所有项目）
response=$(curl -s -X POST "${TRACKER_URL}/api/cron/progress-snapshot" \
  -H "X-API-Token: ${CRON_TOKEN}" \
  -H "Content-Type: application/json")

echo "$(date): ${response}"

# 检查是否成功
if echo "$response" | grep -q '"success":true'; then
    exit 0
else
    exit 1
fi
```

**添加 Crontab**：
```bash
# 编辑 crontab
crontab -e

# 添加以下行（每周六 22:00 执行）
0 22 * * 6 /opt/tracker/snapshot.sh >> /var/log/tracker_snapshot.log 2>&1
```

### 方式三：Docker/Kubernetes CronJob

适用于：容器化部署环境。

**Kubernetes CronJob 示例**：
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: tracker-snapshot
spec:
  schedule: "0 22 * * 6"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: snapshot
            image: your-tracker-image
            env:
            - name: CRON_API_TOKEN
              value: "your-secure-token-here"
            command: 
            - /bin/bash
            - -c
            - |
              curl -X POST "http://localhost:8080/api/cron/progress-snapshot" \
                -H "X-API-Token: ${CRON_API_TOKEN}" \
                -H "Content-Type: application/json"
          restartPolicy: OnFailure
```

---

## 查看和管理快照

### 通过 UI 查看

1. **进入进度图表页面**
   - 选择项目 → 点击「Progress Charts」标签

2. **查看历史快照**
   - 点击「快照管理」按钮
   - 弹出窗口显示所有历史快照
   - 列表按日期倒序排列

3. **查看快照详情**
   - 点击快照列表中的任意一项
   - 显示详细信息：日期、覆盖率、TC 统计等

### 通过 API 获取快照列表

**API 接口**：
```
GET /api/progress/{project_id}/snapshots
```

**请求示例**：
```bash
curl "http://localhost:8080/api/progress/1/snapshots" \
  -b "session=<your_session_cookie>"
```

**响应示例**：
```json
{
  "success": true,
  "snapshots": [
    {
      "id": 124,
      "snapshot_date": "2026-03-24",
      "actual_coverage": 36.6,
      "tc_total": 52,
      "tc_pass_count": 21
    },
    {
      "id": 123,
      "snapshot_date": "2026-03-17",
      "actual_coverage": 35.2,
      "tc_total": 50,
      "tc_pass_count": 18
    }
  ]
}
```

### 获取特定快照详情

**API 接口**：
```
GET /api/progress/{project_id}/snapshot?date={YYYY-MM-DD}
```

**请求示例**：
```bash
curl "http://localhost:8080/api/progress/1/snapshot?date=2026-03-24" \
  -b "session=<your_session_cookie>"
```

---

## 导出快照数据

### 通过 UI 导出

1. **进入快照管理**
   - 选择项目 → 「Progress Charts」→ 「快照管理」

2. **导出数据**
   - 点击「导出进度数据」按钮
   - 选择格式：CSV 或 JSON

3. **下载文件**
   - 浏览器下载导出的文件

### 通过 API 导出

**API 接口**：
```
GET /api/progress/{project_id}/snapshot/export?format={csv|json}
```

**请求示例**：
```bash
# 导出 CSV
curl "http://localhost:8080/api/progress/1/snapshot/export?format=csv" \
  -b "session=<your_session_cookie>" \
  -o snapshot.csv

# 导出 JSON
curl "http://localhost:8080/api/progress/1/snapshot/export?format=json" \
  -b "session=<your_session_cookie>" \
  -o snapshot.json
```

### 导出数据字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| snapshot_date | TEXT | 快照日期 (YYYY-MM-DD) |
| actual_coverage | REAL | CP 实际覆盖率 (%) |
| tc_total | INTEGER | TC 总数 |
| tc_pass_count | INTEGER | TC PASS 数量 |
| p0_coverage | REAL | P0 优先级覆盖率 (%) |
| p1_coverage | REAL | P1 优先级覆盖率 (%) |
| p2_coverage | REAL | P2 优先级覆盖率 (%) |
| p3_coverage | REAL | P3 优先级覆盖率 (%) |

---

## 删除快照

### 通过 UI 删除

1. **进入快照管理**
   - 选择项目 → 「Progress Charts」→ 「快照管理」

2. **删除快照**
   - 在快照列表中找到要删除的快照
   - 点击该快照行的「删除」按钮
   - 确认删除操作

3. **权限说明**
   - 仅 `admin` 角色可删除快照

### 通过 API 删除

**API 接口**：
```
DELETE /api/progress/snapshots/{snapshot_id}
```

**请求示例**：
```bash
curl -X DELETE "http://localhost:8080/api/progress/snapshots/123" \
  -b "session=<your_session_cookie>"
```

**权限要求**：
- 需要 `admin` 角色

---

## 常见问题

### Q: 快照创建失败（返回 401 Unauthorized）？

**可能原因**：v0.11.0+ 定时快照必须使用 Token 认证，Session Cookie 方式已废弃。

| 原因 | 解决方法 |
|------|----------|
| 未配置 CRON_API_TOKEN | 在 systemd service 中添加 `Environment="CRON_API_TOKEN=..."` |
| Token 错误 | 确认 Token 与配置的 `CRON_API_TOKEN` 一致 |
| 使用旧的 Session 方式 | 改用 `POST /api/cron/progress-snapshot` + `X-API-Token` Header |

**排查步骤**：
```bash
# 1. 检查 systemd service 配置
grep CRON_API_TOKEN /etc/systemd/system/tracker.service

# 2. 测试 Token 认证
curl -X POST "http://localhost:8080/api/cron/progress-snapshot" \
  -H "X-API-Token: your-token"

# 3. 查看 API 日志
journalctl -u tracker -n 50
```

### Q: 快照创建失败怎么办？

**可能原因**：

| 原因 | 解决方法 |
|------|----------|
| 项目不存在 | 检查 project_id 是否正确 |
| 数据库写入失败 | 检查数据库文件权限 |
| 网络问题 | 检查 Tracker 服务是否运行 |

**排查步骤**：
```bash
# 1. 检查 Tracker 服务状态
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080

# 2. 检查数据库文件权限
ls -la /projects/management/tracker/shared/data/*.db

# 3. 检查 API 日志
journalctl -u tracker -n 50
```

### Q: 如何避免重复快照？

系统使用 `(project_id, snapshot_date)` 作为唯一约束，同一天重复创建会更新而非创建新记录。

如需创建多个快照于同一天，可在日期后添加时间戳：
```json
{
  "snapshot_date": "2026-03-24_1430"
}
```

### Q: 快照数据占用空间大吗？

单个快照记录很小（约 1KB），按每周一次计算：
- 一年：~52KB
- 十年：~520KB

对存储空间影响极小。

### Q: 如何备份快照数据？

快照存储在项目数据库中，备份项目数据库即备份快照：

```bash
# 备份项目数据库
cp /projects/management/tracker/shared/data/myproject.db \
   /backup/tracker_myproject_$(date +%Y%m%d).db
```

### Q: 快照显示的覆盖率是如何计算的？

**实际覆盖率计算**：
```
actual_coverage = (已关联 TC 中状态为 PASS 的 CP 覆盖率之和) / 已关联 CP 数量
```

**Priority 覆盖率计算**：
- P0/P1/P2/P3 分别计算其关联 CP 的覆盖率
- 未关联的 CP 不计入分母

### Q: 如何设置多个项目的自动快照？

**推荐：使用批量快照端点**

v0.11.0+ 推荐使用 `POST /api/cron/progress-snapshot`，自动处理所有项目（已归档项目自动跳过）：

```bash
#!/bin/bash
CRON_TOKEN="your-secure-token-here"

curl -X POST "http://localhost:8080/api/cron/progress-snapshot" \
  -H "X-API-Token: ${CRON_TOKEN}" \
  -H "Content-Type: application/json"
```

**旧方式（不推荐）**：
```bash
#!/bin/bash
for pid in $(sqlite3 data/projects.db "SELECT id FROM projects WHERE is_archived=0"); do
  curl -X POST "http://localhost:8080/api/progress/${pid}/snapshot" \
    -b "session=<your_session_cookie>"
done
```

---

## 附录

### 相关文档

| 文档 | 路径 |
|------|------|
| 用户手册 | `/dev/manual.md` |
| 总体规格书 | `/docs/SPECIFICATIONS/tracker_OVERALL_SPECS.md` |
| 发布指南 | `/docs/MANUALS/Tracker_Test_to_Production_Guide_v1.0.md` |

### 版本信息

| 项目 | 值 |
|------|-----|
| 文档版本 | v1.1 |
| 创建日期 | 2026-03-24 |
| 更新日期 | 2026-04-03 |
| 适用版本 | v0.8.0+ (v0.11.0+ 推荐使用 Token 认证) |
