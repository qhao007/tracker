# Tracker v0.11.0 版本补充规格书 - 定时快照任务增强

> **版本**: v0.11.0-supplement-snapshot-cron
> **创建日期**: 2026-04-03
> **状态**: 开发中
> **基于**: v0.11.0 初始规格书
> **关联需求**: BUG-129 (快照 cron job 认证缺失)

---

## 1. 概述

### 1.1 问题背景

**问题描述**: 当前定时快照 cron job 调用 `POST /api/progress/{project_id}/snapshot` 时缺少认证信息，导致 API 返回 `Unauthorized`，快照创建失败。

**影响**: 每周五 22:00 的快照任务虽然显示"完成"，但实际上快照未生成。

### 1.2 解决方案

采用 **Token 认证方案**：
- 为 Cron Job 分配专用的 API Token
- 新增白名单端点 `/api/cron/progress-snapshot`
- Token 认证优于 Session Cookie（无状态、适合自动化）

### 1.3 需求列表

| # | 需求 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | 添加 `CRON_API_TOKEN` 配置项 | P1 | 0.5h |
| 2 | 新增 `/api/cron/progress-snapshot` 端点 (Token 认证) | P1 | 1h |
| 3 | 更新 Cron Job 调用方式 (携带 Token) | P1 | 0.5h |
| 4 | 文档更新 (部署说明) | P2 | 0.5h |
| | **总计** | | **~2.5h** |

---

## 2. 详细需求

### 2.1 添加 CRON_API_TOKEN 配置项

**需求描述**: 在 gunicorn 配置中添加 `CRON_API_TOKEN` 配置项，支持通过环境变量或配置文件注入。

**配置方式**: 环境变量（推荐）

```bash
# 在 systemd service 或启动脚本中设置
CRON_API_TOKEN=your-secure-token-here
```

**配置文件更新**: 无需修改代码，从环境变量读取。

### 2.2 修复 `/api/cron/progress-snapshot` 端点

**需求描述**: 端点已存在（v0.8.2），但存在以下问题需要修复：

| # | 问题 | 说明 |
|---|------|------|
| 1 | Token 验证方式错误 | 使用 `current_app.config.get('CRON_API_TOKEN')` 但从未设置，应改为 `os.environ.get('CRON_API_TOKEN')` |
| 2 | 缺少 Priority 覆盖率字段 | v0.11.0 快照需包含 `p0_coverage/p1_coverage/p2_coverage/p3_coverage`，当前 INSERT 缺失 |
| 3 | 响应格式不一致 | 规格书要求 `created_count/skipped_count/errors/timestamp`，当前是 `message/count` |

**API 设计**:

| 方法 | 路径 | 功能 | 认证方式 |
|------|------|------|----------|
| POST | `/api/cron/progress-snapshot` | 批量创建所有项目快照 | X-API-Token Header |

**请求格式**:

```
POST /api/cron/progress-snapshot
X-API-Token: <CRON_API_TOKEN>
Content-Type: application/json
```

**响应格式**:

成功:
```json
{
  "success": true,
  "created_count": 3,
  "skipped_count": 2,
  "errors": [],
  "timestamp": "2026-04-03T22:00:00+08:00"
}
```

失败 (Token 无效):
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing X-API-Token"
}
```

**代码实现位置**: `/app/api.py` (`cron_progress_snapshot` 函数)

**修复要点**:
1. Token 验证改为 `os.environ.get('CRON_API_TOKEN')`
2. INSERT 语句添加 `p0_coverage, p1_coverage, p2_coverage, p3_coverage` 字段
3. 响应格式改为 `created_count/skipped_count/errors/timestamp`

### 2.3 更新 Cron Job 调用方式

**需求描述**: 更新 OpenClaw Cron Job 配置，使用 Token 认证方式调用快照 API。

**更新内容**:

```bash
# 新的 curl 调用方式
curl -X POST "http://localhost:8080/api/cron/progress-snapshot" \
  -H "X-API-Token: ${CRON_API_TOKEN}" \
  -H "Content-Type: application/json"
```

**OpenClaw Cron Job 配置更新**:

```json
{
  "payload": {
    "message": "AUTONOMOUS: 定时抓取所有项目快照\n\n## 执行步骤\n\n### 1. 创建快照\n使用 Token 认证调用快照 API：\n```bash\ncurl -X POST \"http://localhost:8080/api/cron/progress-snapshot\" \\\n  -H \"X-API-Token: ${CRON_API_TOKEN}\" \\\n  -H \"Content-Type: application/json\"\n```\n\n### 2. 判断执行结果\n- 如果返回包含 `\"success\": true`，则快照创建成功\n- 否则为失败\n\n### 3. 发送飞书通知\n..."
  }
}
```

### 2.4 文档更新

**需求描述**: 更新部署文档，说明如何配置 CRON_API_TOKEN。

**更新文件**:
- `docs/DEVELOPMENT/DEPLOYMENT_GUIDE.md` (如有)
- `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md`

**配置说明**:
```markdown
## 定时快照任务配置

### 配置步骤

1. **生成安全的 Token**
```bash
openssl rand -hex 32
```

2. **配置环境变量**

方式 A: systemd service (`/etc/systemd/system/tracker.service`)
```ini
[Service]
Environment="CRON_API_TOKEN=your-generated-token"
```

方式 B: 启动脚本
```bash
export CRON_API_TOKEN=your-generated-token
```

3. **验证配置**
```bash
curl -X POST "http://localhost:8080/api/cron/progress-snapshot" \
  -H "X-API-Token: ${CRON_API_TOKEN}"
# 应返回 {"success": true, ...}
```

### 安全建议

- Token 应该足够长 (32+ 字符)
- Token 应该妥善保管，不要提交到 Git
- 定期轮换 Token
```

---

## 3. 验收标准

| # | 验收标准 | 测试方法 |
|---|----------|----------|
| 1 | 不带 Token 请求返回 401 | `curl -X POST http://localhost:8080/api/cron/progress-snapshot` |
| 2 | 错误 Token 返回 401 | `curl -X POST http://localhost:8080/api/cron/progress-snapshot -H "X-API-Token: wrong"` |
| 3 | 正确 Token 返回成功 | `curl -X POST http://localhost:8080/api/cron/progress-snapshot -H "X-API-Token: correct"` |
| 4 | 快照正确创建（含 Priority 覆盖率） | 验证 `project_progress` 表有新记录且含 p0-p3_coverage |
| 5 | 已归档项目被跳过 | 验证已归档项目不创建快照 |
| 6 | Token 为空时返回 500 | 验证 `CRON_API_TOKEN` 未配置时返回特定错误 |

---

## 4. 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| Token 泄露 | Medium | 使用安全的随机 Token，不硬编码 |
| Token 配置遗漏 | Low | 添加启动检查，Token 为空时警告 |
| 向后兼容 | None | 新增端点不影响现有 API |

---

## 5. 未来扩展 (可选)

| # | 扩展点 | 说明 |
|---|--------|------|
| 1 | 支持指定日期范围 | 支持创建历史日期的快照 |
| 2 | 快照数据压缩 | 定期压缩旧的快照数据 |
| 3 | 快照状态通知 | 发送邮件/钉钉通知快照创建结果 |

---

## 6. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.11.0-supplement-snapshot-cron | 2026-04-03 | 初始版本 |
| v0.11.0-supplement-snapshot-cron | 2026-04-03 | 移除 project_ids 功能，改为处理所有项目；明确修复 BUG-129 |

---

**评审报告**: 待评审
