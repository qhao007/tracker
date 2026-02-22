# CLAUDE.md - Tracker 项目指南

> 本文件供 Claude Code / 小栗子 使用
> 项目: Tracker (芯片验证管理系统)
> 版本: v0.7.0 (生产)

---

## 项目结构

```
/projects/management/tracker/
├── dev/                    # 开发代码目录
│   ├── app/
│   │   ├── api.py         # Flask API 主文件
│   │   ├── models.py      # 数据模型
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_api/      # Python pytest API 测试
│   │   └── test_ui/       # Playwright UI 测试
│   │       ├── specs/
│   │       │   ├── smoke/     # 冒烟测试
│   │       │   ├── integration/ # 集成测试
│   │       │   └── e2e/       # 端到端测试
│   │       └── utils/         # 测试工具
│   ├── scripts/           # 开发工具
│   ├── server.py          # 生产服务器 (port 8080)
│   ├── start_server_test.sh # 测试服务器 (port 8081)
│   ├── index.html         # 前端页面
│   ├── package.json       # npm 依赖
│   └── eslint.config.mjs  # ESLint 配置
│
├── shared/data/            # 用户数据（绝对不动!）
│   ├── test_data/         # 测试数据
│   └── user_data/         # 用户数据
│
├── docs/                   # 文档目录
└── scripts/               # 项目级脚本
```

---

## 常用命令

### 启动服务

```bash
# 生产环境 (port 8080)
cd /projects/management/tracker/dev && python3 server.py

# 测试环境 (port 8081)
cd /projects/management/tracker/dev && ./start_server_test.sh
```

### 代码检查

```bash
# ESLint
cd /projects/management/tracker/dev && bash check_frontent.sh
```

### 测试

```bash
# API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v

# Playwright 测试 (全部)
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/ --project=firefox

# Playwright 冒烟测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/smoke/ --project=firefox

# Playwright 集成测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 代码规范

### Python

- 遵循 PEP 8
- 使用 flake8 检查
- 导入排序: 标准库 → 第三方 → 本地

### JavaScript/HTML

- 使用 ESLint 检查
- 遵循 eslint.config.mjs 配置

### Git 分支管理

```
main (生产)
│
├── develop (开发主分支)
│   └── feature/* (功能分支)
│
└── tags (发布标签)
```

**开发流程**:
1. 从 develop 创建 feature 分支
2. 开发完成后提交到 feature 分支
3. 合并回 develop
4. 合并到 main 并打标签发布

---

## 重要规则

### 🔴 红线

- **绝对不动** `shared/data/user_data/` 目录
- 用户数据删除不可恢复

### 开发规范

- 新功能必须先创建 feature 分支
- 提交前必须运行 ESLint + API 测试
- 对照规格书验收标准自测

### Bug 修复

- 必须添加测试用例
- 修复后运行完整测试套件

---

## 当前版本状态

| 版本 | 状态 | 测试 |
|------|------|------|
| v0.7.0 | 生产 | 178/178 通过 |
| v0.7.1 | 待开发 | - |

---

## 数据说明

- **测试数据**: `shared/data/test_data/` - 可操作
- **用户数据**: `shared/data/user_data/` - 绝对不动
- **数据库**: SQLite，每个项目独立 `.db` 文件

---

## 提交前检查清单

1. ESLint 检查 → 2. API 测试 → 3. 冒烟测试 → 4. 提交

**验证标准**: API 测试 100% 通过，冒烟测试 100% 通过

## 关键文件位置

| 类型 | 路径 |
|------|------|
| 需求反馈 | `/projects/management/feedbacks/` |
| 规格书 | `docs/PLANS/` |
| Bug 记录 | `docs/BUGLOG/tracker_OPEN_ISSUES.md` |
| 开发规范 | `docs/DEVELOPMENT/` |
| 测试计划 | `docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md` |

## 发布流程

```bash
# 1. 确保 develop 分支最新
git checkout develop && git pull

# 2. 创建发布分支
git checkout -b release/vX.X.X

# 3. 更新版本号
echo "vX.X.X" > VERSION

# 4. 测试通过后合并到 main
git checkout main && git merge release/vX.X.X

# 5. 创建标签
git tag -a vX.X.X -m "Release vX.X.X"
```

---

*最后更新: 2026-02-21*
