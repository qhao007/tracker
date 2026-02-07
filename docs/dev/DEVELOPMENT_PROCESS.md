# Tracker 开发流程规范

> **版本**: v1.0 | **创建日期**: 2026-02-05 | **状态**: 生效

---

## 目录

1. [概述](#1-概述)
2. [Git 分支管理](#2-git-分支管理)
3. [需求提交流程](#3-需求提交流程)
4. [开发流程](#4-开发流程)
5. [测试流程](#5-测试流程)
6. [发布流程](#6-发布流程)
7. [文档规范](#7-文档规范)

---

## 1. 概述

### 1.1 目的

本文档定义了 Tracker 项目的开发流程规范，确保团队协作高效、代码质量可控、版本发布可追溯。

### 1.2 适用范围

- 所有参与 Tracker 项目开发的人员
- 代码提交、评审、发布流程

### 1.3 核心原则

| 原则 | 说明 |
|------|------|
| **代码隔离** | Git 只维护 dev/ 代码，发布到独立目录 |
| **数据安全** | 用户数据与测试数据物理隔离 |
| **流程规范** | 需求 → 开发 → 测试 → 发布 |

---

## 2. Git 分支管理

### 2.1 分支结构

```
main (稳定代码，对应 /release/tracker/current)
│
├── develop (开发主分支，存放 dev/ 代码)
│   ├── feature/* (功能开发分支)
│   ├── release/* (发布分支)
│   └── hotfix/* (紧急修复分支)
│
└── tags (在 main 分支上创建)
```

### 2.2 分支说明

| 分支 | 来源 | 合并到 | 用途 |
|------|------|--------|------|
| **main** | - | - | 生产环境代码 |
| **develop** | main | - | 开发主分支 |
| **feature** | develop | develop | 新功能开发 |
| **release** | develop | main + develop | 发布准备 |
| **hotfix** | main | main + develop | 紧急修复 |

### 2.3 常用命令

```bash
# 查看所有分支
git branch -a

# 创建功能分支
git checkout develop
git checkout -b feature/user-auth

# 合并功能分支
git checkout develop
git merge feature/user-auth --no-ff -m "feat: 添加用户认证"

# 创建标签
git checkout main
git tag -a v0.4.0 -m "Release v0.4.0"

# 查看提交历史
git log --oneline --graph --all
```

---

## 3. 需求提交流程

### 3.1 需求类型

| 类型 | 说明 | 模板 |
|------|------|------|
| **新功能** | 新增功能模块 | TEMPLATE_FEATURE_REQUEST.md |
| **批量需求** | 多个简单需求 | BATCH_REQUESTS_TEMPLATE.md |
| **Bug 修复** | 修复缺陷 | BugLog |

### 3.2 需求提交流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        需求提交流程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣ 用户提交需求                                                │
│     └── 填写模板 → 放到 /projects/management/feedbacks/new/     │
│                                                                  │
│  2️⃣ 需求评审                                                    │
│     └── 小栗子细化 → 评估工作量 → 确定优先级                    │
│                                                                  │
│  3️⃣ 需求确认                                                    │
│     └── 生成正式文档 → 用户确认 → 进入开发                      │
│                                                                  │
│  4️⃣ 开发实现                                                    │
│     └── Git 分支 → 编码 → 测试 → 提交                          │
│                                                                  │
│  5️⃣ 发布上线                                                    │
│     └── 执行 release.py → 切换版本 → 重启服务                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 需求模板

#### 3.3.1 单个详细需求

```bash
# 使用模板
cp /projects/management/feedbacks/new/TEMPLATE_FEATURE_REQUEST.md \
   /projects/management/feedbacks/new/功能名称_YYYYMMDD.md
```

**模板位置**: `/projects/management/feedbacks/new/TEMPLATE_FEATURE_REQUEST.md`

#### 3.3.2 批量简单需求

```bash
# 使用批量模板
cp /projects/management/feedbacks/new/BATCH_REQUESTS_TEMPLATE.md \
   /projects/management/feedbacks/new/REQUESTS_YYYYMMDD.md
```

**模板位置**: `/projects/management/feedbacks/new/BATCH_REQUESTS_TEMPLATE.md`

### 3.4 需求处理流程

```mermaid
graph TD
    A[用户提交需求] --> B{需求类型?}
    B -->|简单需求| C[使用批量模板]
    B -->|详细需求| D[使用详细模板]
    C --> E[小栗子细化需求]
    D --> E
    E --> F[评估工作量]
    F --> G[确定优先级]
    G --> H[生成正式 Feature Request]
    H --> I[用户确认]
    I --> J[进入开发]
```

### 3.5 需求存放位置

| 类型 | 目录 |
|------|------|
| 新需求 | `/projects/management/feedbacks/new/` |
| 已评审需求 | `/projects/management/feedbacks/reviewed/` |
| 开发中需求 | `/projects/management/feedbacks/in-progress/` |
| 已完成需求 | `/projects/management/feedbacks/completed/` |

---

## 4. 开发流程

### 4.1 日常开发流程

```bash
# 1. 确保开发分支最新
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/功能名称

# 3. 开发实现
#    - 修改 dev/ 目录下的代码
#    - 在 dev 版本测试

# 4. 提交代码
git add .
git commit -m "feat: 功能说明"

# 5. 合并到 develop
git checkout develop
git merge feature/功能名称 --no-ff -m "merge: 合并功能名称"

# 6. 推送
git push origin develop
```

### 4.2 开发环境

| 项目 | 配置 |
|------|------|
| **开发版** | `dev/` 目录，端口 8081，test_data |
| **测试数据** | `/projects/management/tracker/shared/data/test_data/` |
| **启动命令** | `cd dev && python3 server_test.py` |

### 4.3 代码规范

#### 4.3.1 提交信息规范

```
<type>: <subject>

<body>

<footer>
```

**Type 类型**:

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | `feat: 添加用户认证功能` |
| fix | Bug 修复 | `fix: 修复项目切换数据丢失问题` |
| docs | 文档更新 | `docs: 更新规格书` |
| style | 代码格式 | `style: 格式化代码` |
| refactor | 重构 | `refactor: 重构 API 结构` |
| test | 测试 | `test: 添加单元测试` |
| chore | 构建/工具 | `chore: 更新依赖版本` |

#### 4.3.2 代码质量

- Python 代码遵循 PEP 8
- 前端代码保持简洁
- 关键函数添加注释

---

## 5. 测试流程

### 5.1 测试类型

| 测试类型 | 执行方式 | 覆盖范围 | 测试文件 |
|----------|----------|----------|----------|
| **单元测试** | pytest | API 接口 | `tests/test_api.py` |
| **Playwright 冒烟测试** | UI 自动化 | 核心功能点 | `tests/test_smoke.spec.ts` |
| **BugLog 回归测试** | UI 自动化 | Bug 修复验证 | `tests/tracker.spec.ts` |
| **playwright_firefox.js** | UI 自动化 | 基础功能验证 | `playwright_firefox.js` |
| **手动测试** | 人工验收 | 界面体验 | - |

### 5.2 测试执行

```bash
# ========== API 测试 (dev 版本) ==========
cd dev
PYTHONPATH=. pytest tests/test_api.py -v
# 覆盖: 17 个 API 接口测试 (100% 通过)

# ========== Playwright 冒烟测试 ==========
cd dev
npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000
# 覆盖: F001, F004, F005, F007, F012 核心功能
# 测试文件: tests/test_smoke.spec.ts
# 期望: 6/6 通过

# ========== BugLog 回归测试 ==========
cd dev
npx playwright test tests/tracker.spec.ts --project=firefox --timeout=60000
# 覆盖: BUG-002, BUG-007, BUG-008, BUG-009, BUG-010, FEAT-001
# 测试文件: tests/tracker.spec.ts
# 期望: 11/11 通过

# ========== playwright_firefox.js ==========
cd dev
node playwright_firefox.js
# 覆盖: P001-P014 基础功能验证
# 测试文件: playwright_firefox.js
```

### 5.3 Bug 处理流程

测试中发现代码 bug 时，必须添加到 BugLog：

**添加步骤**:
1. 填写 BugLog 模板 (`/projects/management/feedbacks/new/BugLog_YYYYMMDD.md`)
2. 提交到 feedbacks/new/ 目录
3. 评审后标记为待修复
4. 修复后更新 tracker_BUGLOG.md
5. 编写回归测试用例

**BugLog 模板位置**: `/projects/management/feedbacks/new/BugLog_YYYYMMDD.md`

### 5.4 测试报告发布

测试完成后，必须按照测试报告模板发布结果：

**报告要求**:
1. 使用模板: `docs/dev/TEMPLATE_TEST_REPORT.md`
2. 包含整体测试开始和完成时间
3. 包含所有测试类型的通过/失败统计
4. 包含 BugLog 回归测试详细结果
5. 发布到: `docs/dev/TRACKER_TEST_REPORT_v{version}_{YYYYMMDD}.md`

**报告模板结构**:
```
## 测试摘要
| 测试类型 | 总数 | 通过 | 失败 | 通过率 |

## 测试执行时间
 | 开始时间 || 测试阶段 完成时间 | 持续时间 |

## API 测试结果
...

## Playwright 冒烟测试结果
...

## BugLog 回归测试结果
...
```

**发布命令**:
```bash
# 1. 复制测试报告模板
cp docs/dev/TEMPLATE_TEST_REPORT.md \
   docs/dev/TRACKER_TEST_REPORT_v0.5.0_20260207.md

# 2. 编辑测试报告，填写测试结果

# 3. 提交测试报告
git add docs/dev/TRACKER_TEST_REPORT_*.md
git commit -m "docs: 添加 v0.5.0 测试报告"
```

### 5.3 测试数据

| 测试类型 | 数据目录 | 说明 |
|----------|----------|------|
| **pytest API 测试** | `test_data/` | dev 版本使用，独立测试 |
| **Playwright 冒烟测试** | `test_data/` | 使用测试项目数据 |
| **BugLog 回归测试** | `test_data/` | 使用测试项目数据 |
| **playwright_firefox.js** | `user_data/` | stable 版本，只读验证 |
| **stable 冒烟测试** | `user_data/` | 用户数据，只读操作 |

### 5.4 测试标准

| 版本 | 通过标准 | 测试范围 |
|------|----------|----------|
| **dev** | 100% 通过 | API + Playwright + BugLog 回归 |
| **stable** | 100% 通过 | playwright_firefox.js (只读) |

### 5.5 常见测试问题

**Q: 测试数据不足导致测试失败？**

A: 补充测试数据：
```bash
# 创建测试项目
python3 scripts/data_manager.py create
```

---

## 6. 发布流程

### 6.1 执行发布准备脚本

> **重要**: 只有发布准备脚本成功完成后，才可以执行发布脚本。

```bash
cd /projects/management/tracker

# 1. 演练模式（只检查，不实际操作）
python3 scripts/release_preparation.py --dry-run --version v0.5.0

# 2. 执行完整发布准备
python3 scripts/release_preparation.py --version v0.5.0
```

**发布准备脚本执行内容**:
| 步骤 | 内容 | 失败处理 |
|------|------|----------|
| 1 | API 测试 (pytest) | ❌ 中止发布 |
| 2 | Playwright 冒烟测试 | ❌ 中止发布 |
| 3 | BugLog 回归测试 | ⚠️ 部分通过可继续 |
| 4 | Git 状态检查 | ❌ 中止发布 |
| 5 | Merge 和 Tag | ❌ 中止发布 |

**发布准备脚本选项**:
| 选项 | 说明 |
|------|------|
| `--dry-run` | 演练模式（只检查） |
| `--version` | 版本号 (必需) |
| `--skip-tests` | 跳过测试执行 |
| `--skip-merge-tag` | 跳过 merge 和 tag |
| `--force` | 强制继续（忽略警告） |

> **规则 1**: 发布准备脚本必须成功（exit code 0）才能执行发布脚本。  
> **规则 2**: 发布脚本执行过程中报错，则发行中止。

**发布流程**:
```
发布准备脚本 → Git Merge & Tag → 发布脚本 → 服务重启
     ✅              ✅           ✅         ✅
```

**手动执行方式（不推荐）**:
```bash
# 1. dev 版本 API 测试全部通过 (17/17) ✅
cd dev && PYTHONPATH=. pytest tests/test_api.py -v

# 2. dev 版本 Playwright 冒烟测试通过 (6/6) ✅
cd dev && npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000

# 3. dev 版本 BugLog 回归测试通过 (11/11) ✅
cd dev && npx playwright test tests/tracker.spec.ts --project=firefox --timeout=90000

# 4. Git 代码已合并到 develop ✅
git checkout develop && git status

# 5. 创建发布标签
git checkout main
git merge develop
git tag -a v0.5.0 -m "Release v0.5.0"
```

### 6.2 执行发布### 6.2 执行发布

```bash
cd /projects/management/tracker

# 演练模式（推荐先执行）
python3 scripts/release.py --dry-run

# 实际发布
python3 scripts/release.py --version v0.4.0 --force
```

### 6.3 发布后验证

```bash
# 检查服务状态
sudo systemctl status tracker

# 验证 API
curl http://localhost:8080/api/version
```

### 6.4 回滚

```bash
# 方式1：使用发布脚本回滚
cd /projects/management/tracker
python3 scripts/release.py --rollback --force

# 方式2：手动切换版本
sudo rm /release/tracker/current
sudo ln -s /release/tracker/v0.3.x /release/tracker/current
sudo systemctl restart tracker
```

---

## 7. 文档规范

### 7.1 文档类型

| 类型 | 文件名 | 说明 |
|------|--------|------|
| 规格书 | `tracker_SPECIFICATION.md` | 功能定义、架构设计 |
| 测试计划 | `tracker_TEST_PLAN.md` | 测试策略、用例 |
| 发布报告 | `TRACKER_TEST_REPORT_*.md` | 测试结果 |
| 功能需求 | `FEATURE_*.md` | 新功能详细定义 |
| 开发规范 | `DEVELOPMENT_PROCESS.md` | 本文档 |

### 7.2 文档存放位置

```
/projects/management/tracker/docs/
├── dev/                  # 开发相关文档
│   ├── tracker_SPECIFICATION.md
│   ├── tracker_TEST_PLAN.md
│   ├── DEVELOPMENT_PROCESS.md
│   ├── TEMPLATE_FEATURE_REQUEST.md
│   └── TEMPLATE_RELEASE_NOTES.md
│
└── user/                  # 用户文档
    └── user_manual.md
```

### 7.3 版本历史

每次发布或重大变更后更新本文档版本号。

---

## 附录 A: 快速参考

### Git 命令速查

```bash
# 分支操作
git branch -a              # 查看所有分支
git checkout develop       # 切换到 develop
git checkout -b feature/xxx # 创建功能分支
git branch -d feature/xxx  # 删除分支

# 代码提交
git add .
git commit -m "feat: xxx"
git push origin develop

# 标签操作
git tag -a v0.4.0 -m "Release v0.4.0"
git push origin main --tags
```

### 发布命令速查

```bash
# 演练
python3 scripts/release.py --dry-run

# 发布
python3 scripts/release.py --version v0.4.0 --force

# 回滚
python3 scripts/release.py --rollback --force
```

### 服务管理

```bash
# 重启服务
sudo systemctl restart tracker

# 查看状态
sudo systemctl status tracker

# 查看日志
journalctl -u tracker -f
```

---

**文档版本**: v1.1  
**最后更新**: 2026-02-07  
**维护者**: 小栗子 🌰
