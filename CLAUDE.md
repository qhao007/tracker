# CLAUDE.md - Tracker 项目指南

> 本文件供 Claude Code / 小栗子 使用
> 项目: Tracker (芯片验证管理系统)
> 版本: v0.7.1 (开发中)

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

```bash
# 生产 (8080) - 使用 user_data
cd /projects/management/tracker/dev && python3 server.py

# 测试 (8081) - 使用 test_data
cd /projects/management/tracker/dev && ./start_server_test.sh
```

### 测试

> **UI 测试内存原则**: 以内存消耗最小为原则进行测试，使用 `--project=firefox` 仅运行 Firefox 浏览器

```bash
# API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v

# UI 冒烟测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/smoke/ --project=firefox

# UI 集成测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

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

## ⚠️ 安全规则

### 🔴 绝对禁止

| 规则 | 说明 |
|------|------|
|不动 user_data| 禁止操作 `shared/data/user_data/` 目录|
|不动生产端口| 禁止在 8080 端口调试，8080 是生产环境|
|不碰用户数据| 禁止通过文件操作修改用户数据|

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
| 开发规范 | `docs/DEVELOPMENT/` |
| 测试计划 | `docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md` |

---

## 📊 版本状态

| 版本 | 状态 | 测试 |
|------|------|------|
| v0.7.0 | 生产 | 178/178 通过 |
| v0.7.1 | 开发中 | 175/175 API, 12/12 登录 |

---

*最后更新: 2026-02-24*
