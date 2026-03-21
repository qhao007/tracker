# CLAUDE.md - Tracker 项目指南

> 本文件供 Claude Code / 小栗子 使用
> 项目: Tracker (芯片验证管理系统)
> 版本: v0.x.x (下个版本)

---

## 📋 项目概述

**Tracker** 是一个芯片验证管理系统，用于管理测试用例 (TC) 和覆盖点 (CP)。

| 属性 | 值 |
|------|-----|
| 类型 | Flask + SQLite Web 应用 |
| 前端 | 原生 HTML/JS (无框架) |
| 端口 | 8080 (生产) / 8081 (测试) |
| 数据 | 每个项目独立 SQLite 数据库 |

---

## 🚀 快速命令

### 服务

> **⚠️ 重要**: `server.py` 是生产版本脚本，**绝对不能修改或干扰**

```bash
# 生产 (8080) - 使用 user_data
cd /projects/management/tracker/dev && python3 server.py

# 测试 (8081) - 使用 test_data
cd /projects/management/tracker/dev && ./start_server_test.sh
```

**测试服务器管理**:
- 使用 `./start_server_test.sh` 启动测试服务器（8081 端口）
- 测试服务器使用 gunicorn 运行，修改代码后需要重启:
  ```bash
  pkill -9 gunicorn && gunicorn -w 2 -b 0.0.0.0:8081 'app:create_app()' --daemon
  ```

### 测试

> **UI 测试内存原则**: 以内存消耗最小为原则进行测试，使用 `--project=firefox` 仅运行 Firefox 浏览器

```bash
# API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v

# UI 冒烟测试 (需先设置环境变量)
cd /projects/management/tracker/dev && HOME=/root XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/smoke/ --project=firefox

# UI 集成测试
cd /projects/management/tracker/dev && HOME=/root XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

### UI 测试调试

**清理测试数据**: 大量测试项目会导致超时，运行以下命令清理:
```bash
python3 scripts/tracker_ops.py clean
```

**Playwright 沙箱环境**: 如遇 Firefox 启动失败，添加环境变量:
```bash
HOME=/root XDG_RUNTIME_DIR=/tmp npx playwright test ...
```
或在 `playwright.config.ts` 中配置:
```typescript
launchOptions: {
  env: { HOME: '/root', XDG_RUNTIME_DIR: '/tmp' }
}
```

**测试数据原则**: 使用现有 SOC_DV 项目数据 (30 CP)，避免在每个测试中创建新数据

### 代码检查

```bash
cd /projects/management/tracker/dev && bash check_frontent.sh
```

---

## 📁 关键文件

### 后端

| 文件 | 说明 |
|------|------|
| `dev/app/api.py` | Flask API 路由 |
| `dev/app/models.py` | SQLAlchemy 模型 |

### 前端

| 文件 | 说明 |
|------|------|
| `dev/index.html` | 单页面应用入口 |

### 测试

| 路径 | 说明 |
|------|------|
| `dev/tests/test_api/` | Python pytest API 测试 |
| `dev/tests/test_ui/specs/smoke/` | Playwright 冒烟测试 |
| `dev/tests/test_ui/specs/integration/` | Playwright 集成测试 |

---

## 🔌 API 端点 (关键)

### 认证

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/logout` | 登出 |

### 项目

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| POST | `/api/projects` | 创建项目 |
| DELETE | `/api/projects/{id}` | 删除项目 |

### TC (测试用例)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/tc?project_id={id}` | 获取 TC 列表 |
| POST | `/api/tc` | 创建 TC |
| PUT | `/api/tc/{id}` | 更新 TC |
| DELETE | `/api/tc/{id}` | 删除 TC |
| PATCH | `/api/tc/{id}/status` | 更新状态 |

### CP (覆盖点)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/cp?project_id={id}` | 获取 CP 列表 |
| POST | `/api/cp` | 创建 CP |
| PUT | `/api/cp/{id}` | 更新 CP |
| DELETE | `/api/cp/{id}` | 删除 CP |

---

## 🗄️ 数据库 Schema

### 表: test_case (TC)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| testbench | TEXT | 测试台名称 |
| test_name | TEXT | 测试名称 |
| scenario | TEXT | 测试场景 |
| status | TEXT | 状态 (PASS/FAIL/OPEN/CODED) |
| owner | TEXT | 负责人 |
| category | TEXT | 类别 |
| target_date | TEXT | 目标日期 |

### 表: cover_point (CP)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | 覆盖点名称 |
| description | TEXT | 描述 |
| priority | TEXT | 优先级 (P0/P1/P2) |

---

## 🌳 项目目录结构

```
/projects/management/tracker/
├── CLAUDE.md                    # 项目指南
├── dev/                        # 开发目录
│   ├── app/                    # Flask 应用
│   │   ├── api.py              # API 路由
│   │   ├── models.py           # 数据模型
│   │   └── __init__.py
│   ├── static/                 # 静态资源
│   │   ├── js/
│   │   └── css/
│   ├── index.html              # SPA 入口
│   ├── server.py               # 生产服务器
│   ├── start_server_test.sh    # 测试服务器启动脚本
│   ├── check_frontent.sh       # 前端检查脚本
│   └── tests/                  # 测试目录
│       ├── test_api/            # pytest API 测试
│       └── test_ui/             # Playwright UI 测试
│           ├── specs/
│           │   ├── smoke/      # 冒烟测试
│           │   ├── integration/# 集成测试
│           │   └── e2e/        # 端到端测试
│           ├── pages/          # 页面对象
│           ├── fixtures/       # 测试fixtures
│           └── utils/          # 工具函数
├── shared/                     # 共享数据
│   └── data/
│       ├── test_data/          # 测试数据 (可操作)
│       └── user_data/          # 用户数据 (禁止操作)
├── docs/                       # 文档
├── scripts/                    # 脚本
├── custom_skills/              # 自定义技能
└── logs/                       # 开发日志
```

---

## ⚠️ 安全规则

### 🔴 绝对禁止

| 规则 | 说明 |
|------|------|
|不动 user_data| 禁止操作 `shared/data/user_data/` 目录|
|不动生产端口| 禁止在 8080 端口调试，8080 是生产环境|
|不碰用户数据| 禁止通过文件操作修改用户数据|
|不手工发布| 禁止用 `cp/ln/gunicorn` 等手工命令发布，必须用 release.py |

### 数据目录

| 目录 | 用途 | 可操作 |
|------|------|--------|
| `shared/data/test_data/` | 测试数据 | ✅ |
| `shared/data/user_data/` | 用户数据 | ❌ |

---

## 🔧 开发流程

### 分支策略

```
main (生产)
│
├── develop (开发主分支)
│   └── feature/* (功能分支)
│
└── tags (发布标签)
```

### 开发步骤

1. `git checkout develop`
2. `git checkout -b feature/xxx`
3. 开发 + 测试
4. `git commit`
5. PR 到 develop
6. 合并到 main 后打标签

### 提交前检查

- [ ] ESLint 通过
- [ ] API 测试 100% 通过
- [ ] 冒烟测试通过

---

## 📚 文档位置

| 类型 | 路径 |
|------|------|
| 需求反馈 | `/projects/management/feedbacks/` |
| 规格书 | `docs/PLANS/` |
| Bug 记录 | `docs/BUGLOG/` |
| 开发规范 | `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| **编程标准** | `docs/DEVELOPMENT/coding_standard.md` |
| 测试计划 | `docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md` |

---

## 📖 编程标准

> 后续版本开发请遵循 `docs/DEVELOPMENT/coding_standard.md` 中的编程标准

包含以下内容：
- Python 后端代码规范 (PEP 8)
- 前端 JavaScript 规范
- API 设计标准 (RESTful)
- 数据库操作标准
- 测试代码标准 (pytest + Playwright)
- 错误处理规范
- 安全规范

---

## 🚀 开发工作流

> Tracker 项目专用开发工作流，使用方式：直接告诉我"请按工作流开发 xxx"

**位置**: `custom_skills/tracker_code_development_workflow/SKILL.md`

**流程**: 开发(Subagent A) → 审查(Subagent B，1-3轮优化) → 测试(Subagent C) → 确认(Subagent D)

---

## 🛠️ 已安装技能

> 项目本地技能放在 `.claude/skills/<skill-name>/SKILL.md`

| 技能 | 位置 | 说明 |
|------|------|------|
| `tracker_code_development_workflow` | `.claude/skills/` | Tracker 代码开发工作流 |
| `tracker-coverage-enhancement-workflow` | `.claude/skills/` | 测试覆盖增强工作流 |
| `playwright-debug` | `.claude/skills/` | Playwright 调试最佳实践 |

### Skill 使用与创建

- **创建新技能**: 使用 `skill-creator` skill 引导工作流
- **Skill 描述**: 包含具体触发关键词，而非泛泛描述
- **项目本地技能**: 放在 `.claude/skills/<skill-name>/SKILL.md`

---

## 📝 开发日志规则

> 重要：每次完成开发相关工作后，必须记录到 `logs/` 目录

### 规则
- 使用 `logs/TEMPLATE.md` 模板创建日志
- 文件命名格式: `YYYY-MM-DD.md`
- 每日工作结束后更新或创建日志

### 示例
```bash
# 创建新日志
cp logs/TEMPLATE.md logs/2026-03-07.md
```

---

## ✍️ 文档署名

> 本项目所有文档的署名: **Claude Code**

---

## 📊 版本状态

| 版本 | 状态 | 测试 |
|------|------|------|
| v0.9.0 | 生产 | - |
| v0.x.x | 开发中 | (下个版本，版本号待定) |

---

## 🔔 飞书通知

> 项目已配置飞书 Webhook，完成任务后可发送通知

**Webhook URL**:
```
https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3
```

**发送文本消息**:
```bash
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3" \
  -H "Content-Type: application/json" \
  -d '{"msg_type": "text", "content": {"text": "你的消息内容"}}'
```

**发送卡片消息**:
```bash
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {"tag": "plain_text", "content": "✅ 任务完成"},
        "template": "green"
      },
      "elements": [
        {"tag": "markdown", "content": "**内容**: 你的消息"}
      ]
    }
  }'
```

> **权限**: 已在 `.claude/settings.local.json` 中预批准，无需手动确认

---

*最后更新: 2026-03-13 | 署名: Claude Code*
