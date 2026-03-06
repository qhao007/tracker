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
   - [6.1 执行发布准备脚本](#61-执行发布准备脚本)
   - [6.2 执行发布](#62-执行发布)
   - [6.3 发布后验证](#63-发布后验证)
   - [6.4 回滚](#64-回滚)
   - [6.5 部署配置](#65-部署配置)
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
| **流程规范** | 需求 → 版本规格书 → 测试计划 → 开发 → 测试 → 合并 → 发布准备 → 发布执行 → 发布验证 |

### 1.4 总体流程图

  ┌─────────────────────────────────────────────────────────────────────────────┐                                      
  │                           Tracker 整体开发流程                                │                                    
  └─────────────────────────────────────────────────────────────────────────────┘                                      
                                                                                                                       
     ┌──────────┐                                                                                                      
     │ 用户提交  │  填写模板 → /projects/management/feedbacks/new/                                                     
     │  需求    │                                                                                                      
     └────┬─────┘                                                                                                      
          ▼                                                                                                            
     ┌──────────┐                                                                                                      
     │ 需求评审  │  小栗子细化 → 评估工作量 → 确定优先级                                                               
     └────┬─────┘                                                                                                      
          ▼                                                                                                            
     ┌──────────┐                                                                                                      
     │ 需求确认  │  生成正式文档 → 用户确认                                                                            
     └────┬─────┘                                                                                                      
          ▼                                                                                                            
     ┌──────────┐                                                                                                      
     │ 版本规格书 │  定义功能规格 → 验收标准                                                                           
     └────┬─────┘                                                                                                      
          ▼                                                                                                            
     ┌──────────┐                                                                                                      
     │ 测试计划  │  定义测试用例 → 任务分解                                                                            
     └────┬─────┘                                                                                                      
          ▼                                                                                                            
     ┌──────────┐                                                                                                      
     │ 开发实现  │  Git分支 → 编码 → 测试 → 提交                                                                       
     └────┬─────┘                                                                                                      
          ▼                                                                                                            
     ┌──────────────┐                                                                                                 
     │ ⚠️ 用户确认  │  报告测试结果 → 用户明确确认后才能发布                                                           
     └──────┬───────┘                                                                                                 
          ▼                                                                                                            
     ┌──────────┐                                                                                                      
     │ 发布上线  │  执行release_preparation.py → 执行release.py → 切换版本 → 重启服务                                
     └──────────┘                                                                   

---

## 2. Git 分支管理

> **注意**: 本项目已配置远程仓库，所有代码变更需要推送到远程仓库进行备份和协作。

### 2.1 远程仓库配置

| 配置项 | 值 |
|--------|-----|
| **仓库地址** | `git@github.com:qhao007/tracker.git` |
| **分支** | `main` (稳定版), `develop` (开发版) |

#### 2.1.1 首次配置

```bash
# 添加远程仓库（如果未配置）
cd /projects/management/tracker
git remote add origin git@github.com:qhao007/tracker.git

# 推送现有分支
git push --set-upstream origin develop
git push --set-upstream origin main

# 后续推送
git push origin develop
git push origin main
```

### 2.1 分支结构


main (稳定代码，对应 /release/tracker/current)
│
├── develop (开发主分支，存放 dev/ 代码)
│   ├── feature/* (功能开发分支)
│   ├── release/* (发布分支)
│   └── hotfix/* (紧急修复分支)
│
└── tags (在 main 分支上创建)


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


---

## 3. 需求提交流程

### 3.1 需求类型

| 类型 | 说明 | 模板 |
|------|------|------|
| **新功能** | 新增功能模块 | TEMPLATE_FEATURE_REQUEST.md |
| **批量需求** | 多个简单需求 | BATCH_REQUESTS_TEMPLATE.md |
| **Bug 修复** | 修复缺陷 | TEMPLATE_BUGLOG.md |

### 3.2 需求提交流程



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
│     └── 生成正式文档 → 用户确认                                 │
│                                                                  │
│  4️⃣ 创建版本规格书                                              │
│     └── 基于需求文档 → 定义功能规格 → 验收标准                  │
│                                                                  │
│  5️⃣ 创建测试计划                                                │
│     └── 基于规格书 → 定义测试用例 → 任务分解                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘




### 3.3 版本规格书与测试计划创建流程

> **重要**：每次需求确认后，必须先创建版本规格书，然后基于规格书创建测试计划，才能进入开发阶段。

#### 3.3.1 版本规格书创建

**触发条件**：需求确认后（3️⃣ 步骤完成）

**创建步骤**：
1. 复制规格书模板
2. 基于已确认的需求文档填写功能规格
3. 定义验收标准
4. 保存到 `docs/SPECIFICATIONS/tracker_SPECS_vX.X.X.md`

**模板位置**：`docs/TEMPLATES/TEMPLATE_VERSION_SPECIFICATION.md`

**示例**：
```bash
# 复制规格书模板
cp docs/TEMPLATES/TEMPLATE_VERSION_SPECIFICATION.md \
   docs/SPECIFICATIONS/tracker_SPECS_v0.7.0.md


#### 3.3.2 测试计划创建

**触发条件**：版本规格书创建完成后（4️⃣ 步骤完成）

**创建步骤**：
1. 复制测试计划模板
2. 基于版本规格书定义测试用例
3. 分解测试开发任务
4. 保存到 `docs/PLANS/TRACKER_TEST_PLAN_vX.X.X.md`

**模板位置**：`docs/TEMPLATES/TEMPLATE_TEST_PLAN.md`

**示例**：
```bash
# 复制测试计划模板
cp docs/TEMPLATES/TEMPLATE_TEST_PLAN.md \
   docs/PLANS/TRACKER_TEST_PLAN_v0.7.0.md


#### 3.3.3 文档目录规范

| 文档类型 | 目录 | 示例 |
|----------|------|------|
| 版本规格书 | `docs/SPECIFICATIONS/` | `tracker_SPECS_v0.7.0.md` |
| 测试计划 | `docs/PLANS/` | `TRACKER_TEST_PLAN_v0.7.0.md` |
| 测试报告 | `docs/REPORTS/` | `TRACKER_TEST_REPORT_v0.7.0_20260216.md` |

#### 3.3.4 版本规格书内容要求

版本规格书必须包含以下内容：

| 章节 | 说明 |
|------|------|
| 需求清单 | 列出本版本所有功能需求 |
| 功能详情 | 每个功能的详细描述 |
| API 接口 | API 设计（如有） |
| 验收标准 | 功能完成的判定条件 |

#### 3.3.5 测试计划内容要求

测试计划必须包含以下内容：

| 章节 | 说明 |
|------|------|
| 版本概述 | 对应规格书、目标功能 |
| API 测试计划 | 基于规格书的 API 测试用例 |
| UI 测试计划 | 基于规格书的 UI 测试用例 |
| 任务分解 | 测试开发任务分配 |
| 验收标准 | 测试完成的判定条件 |


### 3.4 需求模板


#### 3.4.1 单个详细需求

```bash
# 使用模板
cp /projects/management/feedbacks/new/TEMPLATE_FEATURE_REQUEST.md \
   /projects/management/feedbacks/new/功能名称_YYYYMMDD.md


**模板位置**: `/projects/management/feedbacks/new/TEMPLATE_FEATURE_REQUEST.md`

#### 3.4.2 批量简单需求

```bash
# 使用批量模板
cp /projects/management/feedbacks/new/BATCH_REQUESTS_TEMPLATE.md \
   /projects/management/feedbacks/new/REQUESTS_YYYYMMDD.md


**模板位置**: `/projects/management/feedbacks/new/BATCH_REQUESTS_TEMPLATE.md`

### 3.5 需求处理流程

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


### 3.6 需求存放位置

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

# 4. 开发测试
#    - 执行 ESLint 检查: cd dev && bash check_frontent.sh
#    - 执行 API 测试: cd dev && PYTHONPATH=. pytest tests/test_api/ -v --reruns 2
#    - 执行冒烟测试: cd dev && npx playwright test tests/test_ui/specs/smoke/smoke.spec.ts --project=firefox
#    - ⚠️ 必须所有测试通过后才能提交代码
#    - ⚠️ 如果测试需要重试才能通过，必须修复根因，不能依赖重试

# 5. 提交代码
git add .
git commit -m "feat: 功能说明"

# 6. 合并到 develop 前，先更新版本号
#    - 编辑 dev/VERSION 文件，更新版本号（如 v0.6.1 → v0.6.2）
#    - git add dev/VERSION && git commit -m "chore: 更新 VERSION 文件为 v0.6.2"

# 7. 合并到 develop
git checkout develop
git merge feature/功能名称 --no-ff -m "merge: 合并功能名称"

# 8. ⚠️ 等待用户确认发布
#    - 向用户报告测试结果（API测试、冒烟测试、ESLint）
#    - 等待用户明确确认后，才能进入发布流程
#    - 用户确认方式：口头/飞书/邮件确认

# 9. 推送
git push origin develop


**⚠️ 重要**: 
- 步骤 4（开发测试）是必需的，所有测试必须通过后才能执行步骤 5（提交代码）。
- **步骤 6（更新版本号）是必需的**，每次合并新功能到 develop 前必须更新 VERSION 文件，确保 develop 分支始终显示下一个开发版本的版本号。
- **步骤 8（用户确认）是必需的**，未经用户确认禁止执行任何发布相关工作。

### 4.2 开发环境

| 项目 | 配置 |
|------|------|
| **生产版** | `/release/tracker/v{version}/`，端口 8080，user_data |
| **开发版** | `dev/`，端口 8081，test_data |
| **测试数据** | `/projects/management/tracker/shared/data/test_data/` |
| **WSGI 入口** | `wsgi.py` (定义 app 对象供 gunicorn 加载) |

#### 4.2.1 服务启动说明

| 文件 | 用途 | 位置 |
|------|------|------|
| `start_server_test.sh` | 测试版启动脚本 | `dev/` |
| `server.py` | Flask 应用入口 | `dev/` (源码) |
| `server.py` | Flask 应用入口 | `release/tracker/v{version}/` (发布版) |

**启动方式：**
- **测试版 (8081)**: `dev/start_server_test.sh`
- **生产版 (8080)**: 通过 systemd 服务管理，或 `release/tracker/v{version}/server.py`

> **生产环境部署配置**: 详细说明见 [6.5 部署配置](#65-部署配置)

### 4.3 代码规范

#### 4.3.1 提交信息规范


<type>: <subject>

<body>

<footer>


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

#### 4.3.3 ESLint 检查（前端代码）

**适用场景**: 每次提交包含前端代码（index.html, JavaScript 文件）的 CI 检查。

**检查内容**:
1. **ESLint 检查**: HTML 文件中的 JavaScript 语法错误
2. **关键函数完整性检查**: renderTC, renderCP, loadCP, loadTC 等核心函数
3. **API 端点检查**: API_BASE 和 /api/* 端点定义

**执行命令**:
```bash
# 在项目根目录执行
cd /projects/management/tracker/dev
bash check_frontent.sh


**检查输出示例**:

=== Tracker 前端代码检查 ===

1. ESLint 检查...
   ✅ ESLint 检查通过

2. 关键函数完整性检查...
   ✅ renderTC 函数存在
   ✅ renderCP 函数存在
   ...

3. API 端点检查...
   ✅ API_BASE 定义正确
   ✅ API 端点定义完整

=== 检查通过 ✅ ===


**CI 集成**: 在 `.github/workflows/` 或等价 CI 系统中添加步骤：
```yaml
- name: Frontend Code Check
  run: cd dev && bash check_frontent.sh


**失败处理**: ESLint 检查失败时，禁止合并代码，必须修复后才能提交。

---

## 5. 测试流程

### 5.1 测试类型

| 测试类型 | 执行方式 | 覆盖范围 | 测试文件 | 执行频率 |
|----------|----------|----------|----------|----------|
| **ESLint 检查** | 脚本 | 前端 JS 语法 | `check_frontent.sh` | 每次提交 |
| **API 测试** | pytest | API 接口 | `tests/test_api/` | 每次提交 |
| **Playwright 冒烟测试** | UI 自动化 | 核心功能点 | `tests/test_ui/specs/smoke/` | 每次提交 |
| **兼容性测试** | Python 脚本 | 数据库兼容性 | `scripts/tracker_ops.py` | 发布前 |

### 5.1.1 ESLint 检查（前端代码）

| 检查项 | 说明 | 命令 |
|--------|------|------|
| ESLint 检查 | HTML 中的 JavaScript 语法错误 | `bash check_frontent.sh` |
| 关键函数检查 | renderTC, renderCP, loadCP, loadTC 等 | `bash check_frontent.sh` |
| API 端点检查 | API_BASE 和 /api/* 端点定义 | `bash check_frontent.sh` |

### 5.2 测试执行

```bash
# ========== ESLint 检查 (dev 版本，前端代码) ==========
cd /projects/management/tracker/dev
bash check_frontent.sh
# 覆盖: JavaScript 语法、关键函数完整性、API 端点
# 期望: 全部检查通过 ✅

# ========== API 测试 (dev 版本) ==========
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/ -v
# 覆盖: API 接口测试
# 期望: 全部通过

# ========== Playwright 冒烟测试 ==========
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/smoke/ --project=firefox
# 覆盖: 页面访问、项目加载、数据加载、控制台错误检测
# 期望: 全部通过

# ========== 兼容性测试 ==========
cd /projects/management/tracker
# 复制用户数据到测试目录
python3 scripts/tracker_ops.py sync
# 执行兼容性检查
python3 scripts/tracker_ops.py check
# 执行 API 兼容性测试
python3 scripts/tracker_ops.py test
# 清理测试数据
python3 scripts/tracker_ops.py clean


### 5.3 Bug 处理流程

测试中发现代码 bug 时，必须添加到 Bug Record：

**添加步骤**:
1. 填写 Bug 模板 (`docs/TEMPLATES/TEMPLATE_BUGLOG.md`)
2. 提交到 feedbacks/new/ 目录
3. 评审后标记为待修复
4. 修复后更新 `docs/BUGLOG/tracker_BUG_RECORD.md`

**Bug 模板位置**: `docs/TEMPLATES/TEMPLATE_BUGLOG.md`

### 5.4 测试报告发布

测试完成后，必须按照测试报告模板发布结果：

**报告要求**:
1. 使用模板: `TEMPLATES/TEST_REPORT.md`
2. 包含整体测试开始和完成时间
3. 包含所有测试类型的通过/失败统计
4. 发布到: `docs/REPORTS/TRACKER_TEST_REPORT_v{version}_{YYYYMMDD}.md`

**报告模板结构**:

## 测试摘要
| 测试类型 | 总数 | 通过 | 失败 | 通过率 |

## 测试执行时间
 | 开始时间 || 测试阶段 完成时间 | 持续时间 |

## API 测试结果
...

## Playwright 冒烟测试结果
...

## 兼容性测试结果
...


**发布命令**:
```bash
# 1. 复制测试报告模板
cp TEMPLATES/TEST_REPORT.md \
   docs/REPORTS/TRACKER_TEST_REPORT_v0.6.0_20260208.md

# 2. 编辑测试报告，填写测试结果

# 3. 提交测试报告
git add docs/REPORTS/TRACKER_TEST_REPORT_*.md
git commit -m "docs: 添加 v0.6.0 测试报告"


### 5.5 测试数据

| 测试类型 | 数据目录 | 说明 |
|----------|----------|------|
| **pytest API 测试** | `test_data/` | dev 版本使用，独立测试 |
| **Playwright 冒烟测试** | `test_data/` | 使用测试项目数据 |
| **兼容性测试** | `user_data/` → `test_data/` | 复制用户数据验证兼容性 |

### 5.6 测试标准

| 版本 | 通过标准 | 测试范围 |
|------|----------|----------|
| **dev** | 100% 通过 | API + 冒烟测试 |
| **stable** | 100% 通过 | 兼容性测试 (只读) |

### 5.7 常见测试问题

**Q: 测试数据不足导致测试失败？**

A: 补充测试数据：
```bash
# 创建测试项目
python3 scripts/data_manager.py create


**Q: 如何测试用户数据兼容性？**

A: 执行兼容性测试：
```bash
cd /projects/management/tracker
python3 scripts/data_manager.py sync  # 复制用户数据
# 在 http://localhost:8081 测试
python3 scripts/data_manager.py clean # 清理


---

## 6. 发布流程

> **重要**: 只有发布准备脚本成功完成后，才可以执行发布脚本。

**发布流程**:

0. ⚠️ 用户确认发布（必需）
   ├── 向用户报告测试结果
   ├── 用户明确确认后才能继续
   └── 确认方式：口头/飞书/邮件

1. 执行发布准备脚本
   ├── API 测试
   ├── 冒烟测试
   ├── 兼容性测试
   ├── VERSION 更新和提交 ← 自动
   ├── Git 状态检查
   └── Merge 和 Tag ← 自动

2. 执行发布脚本


### 6.0 用户确认发布（必需步骤）

> ⚠️ **未经用户确认，禁止执行任何发布相关工作！**

在执行发布准备脚本之前，必须完成用户确认步骤：

**用户确认内容**：
1. 测试结果报告
   - API 测试：通过/失败数量
   - 冒烟测试：通过/失败数量
   - ESLint 检查结果
   
2. 版本变更说明
   - 新增功能列表
   - Bug 修复列表
   - 已知问题（如有）

3. 风险评估
   - 是否有数据库变更
   - 是否影响现有数据
   - 回滚方案

**用户确认方式**：
- 口头确认
- 飞书消息确认
- 邮件确认

**确认后**：
- 获得用户明确授权后，才能执行发布准备脚本
- 在发布流程记录中标注确认时间和确认方式


### 6.1 执行发布准备脚本

```bash
cd /projects/management/tracker

# 演练模式（只检查，不实际操作）
python3 scripts/release_preparation.py --dry-run --version v0.6.0

# 执行完整发布准备
python3 scripts/release_preparation.py --version v0.6.0


**发布准备脚本执行内容**:
| 步骤 | 内容 | 失败处理 |
|------|------|----------|
| 1 | API 测试 (pytest tests/test_api/) | ❌ 中止发布 |
| 2 | Playwright 冒烟测试 (tests/test_ui/specs/smoke/) | ❌ 中止发布 |
| 3 | 兼容性测试 (tracker_ops.py) | ⚠️ 部分通过可继续 |
| 4 | VERSION 更新和提交 | ❌ 中止发布 |
| 5 | Git 状态检查 | ❌ 中止发布 |
| 6 | Merge 和 Tag | ❌ 中止发布 |

**发布准备脚本选项**:
| 选项 | 说明 |
|------|------|
| `--dry-run` | 演练模式（只检查） |
| `--version` | 版本号 (必需) |
| `--skip-tests` | 跳过测试执行 |
| `--skip-version` | 跳过 VERSION 更新 |
| `--force` | 强制继续（忽略警告） |

> **规则 1**: 发布准备脚本必须成功（exit code 0）才能执行发布脚本。  
> **规则 2**: 发布脚本执行过程中报错，则发行中止。

### 6.2 执行发布

```bash
cd /projects/management/tracker

# 演练模式（推荐先执行）
python3 scripts/release.py --dry-run

# 实际发布
python3 scripts/release.py --version v0.5.0 --force


### 6.3 发布后验证

```bash
# 检查服务状态
sudo systemctl status tracker

# 验证 API
curl http://localhost:8080/api/version


### 6.4 回滚

```bash
# 方式1：使用发布脚本回滚
cd /projects/management/tracker
python3 scripts/release.py --rollback --force

# 方式2：手动切换版本
sudo rm /release/tracker/current
sudo ln -s /release/tracker/v0.3.x /release/tracker/current
sudo systemctl restart tracker


---


### 6.5 部署配置

#### 6.5.1 systemd 服务配置

生产环境通过 systemd 服务管理，配置文件位于 `/etc/systemd/system/tracker.service`:

```ini
[Unit]
Description=Tracker Chip Verification Management System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/release/tracker/current
Environment="FLASK_ENV=production"
Environment="FLASK_SECRET_KEY=your-secret-key-change-in-production"
Environment="CRON_API_TOKEN=your-cron-token-change-in-production"
ExecStart=/usr/bin/python3 /release/tracker/current/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**创建服务文件**:
```bash
sudo nano /etc/systemd/system/tracker.service
sudo systemctl daemon-reload
sudo systemctl enable tracker
sudo systemctl start tracker
```

#### 6.5.2 环境变量配置

| 变量 | 说明 | 必填 | 示例值 |
|------|------|------|--------|
| `FLASK_ENV` | 运行环境 | ✅ | `production` |
| `FLASK_SECRET_KEY` | Flask Session 加密密钥 | ✅ | (随机字符串，**必须更改**) |
| `CRON_API_TOKEN` | 定时任务认证 Token | v0.8.2+ | (随机字符串，**必须更改**) |

**重要安全提醒**:
- `FLASK_SECRET_KEY` 必须使用随机字符串，不能使用默认值
- `CRON_API_TOKEN` 用于定时任务接口认证，v0.8.2+ 需要配置
- 环境变量在服务启动时加载，修改后需要重启服务生效

#### 6.5.3 服务管理命令

```bash
# 启动服务
sudo systemctl start tracker

# 停止服务
sudo systemctl stop tracker

# 重启服务
sudo systemctl restart tracker

# 查看状态
sudo systemctl status tracker

# 查看实时日志
journalctl -u tracker -f

# 查看最近日志
journalctl -u tracker -n 50
```

#### 6.5.4 端口配置

| 端口 | 用途 | 数据目录 |
|------|------|----------|
| 8080 | 生产环境 | `shared/data/user_data/` |
| 8081 | 测试环境 | `shared/data/test_data/` |

**启动方式**:
- **生产版 (8080)**: 通过 systemd 服务管理
- **测试版 (8081)**: `dev/start_server_test.sh`


## 7. 文档规范

### 7.1 文档类型

| 类型 | 文件名 | 说明 |
|------|--------|------|
| 规格书 | `tracker_SPECIFICATION.md` | 功能定义、架构设计 |
| 测试计划 | `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md`<br>`docs/DEVELOPMENT/API_TESTING_STRATEGY.md`<br>`docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md` | 测试策略、用例 |
| 发布报告 | `TRACKER_TEST_REPORT_*.md` | 测试结果 |
| 功能需求 | `FEATURE_*.md` | 新功能详细定义 |
| 开发规范 | `DEVELOPMENT_PROCESS.md` | 本文档 |

### 7.2 文档存放位置


/projects/management/tracker/docs/
├── DEVELOPMENT/           # 开发相关文档
│   ├── DEVELOPMENT_PROCESS.md
│   ├── UI_TESTING_STRATEGY.md
│   ├── API_TESTING_STRATEGY.md
│   ├── TEST_EXECUTION_PLAN.md
│   ├── TEMPLATE_FEATURE_REQUEST.md
│   └── TEMPLATE_RELEASE_NOTES.md
│
└── user/                  # 用户文档
    └── user_manual.md


### 7.3 版本历史

每次发布或重大变更后更新本文档版本号。

---

## 附录 A: 快速参考

### Git 命令速查

```bash
# 远程仓库配置
git remote -v                              # 查看远程仓库
git remote add origin git@github.com:xxx  # 添加远程仓库
git remote set-url origin git@xxx         # 更新远程仓库地址

# 分支操作
git branch -a              # 查看所有分支
git checkout develop       # 切换到 develop
git checkout -b feature/xxx # 创建功能分支
git branch -d feature/xxx  # 删除分支

# 代码提交
git add .
git commit -m "feat: xxx"

# 推送（推送到远程仓库）
git push origin develop              # 推送到 develop 分支
git push origin main                # 推送到 main 分支
git push --set-upstream origin develop  # 首次推送并设置上游

# 拉取
git pull origin develop             # 拉取 develop 分支

# 标签操作
git tag -a v0.4.0 -m "Release v0.4.0"
git push origin main --tags


### 发布命令速查

```bash
# 演练
python3 scripts/release.py --dry-run

# 发布
python3 scripts/release.py --version v0.4.0 --force

# 回滚
python3 scripts/release.py --rollback --force


### 服务管理

> 详细说明见 [6.5 部署配置](#65-部署配置)

#### 测试版 (8081)
```bash
# 重启测试服务
pkill -f "gunicorn.*8081"
cd /projects/management/tracker/dev && python3 -m gunicorn -c gunicorn.conf.py "app:create_app()" --bind 0.0.0.0:8081 --daemon

# 查看测试服务是否运行
ps aux | grep "gunicorn.*8081"

# 测试服务是否正常
curl -s http://localhost:8081/api/version
```


---

**文档版本**: v1.9  
**最后更新**: 2026-03-06

---

## 更新日志

### 2026-03-06

- 新增远程仓库配置 (2.1 远程仓库配置)
- 添加 Git 推送命令到日常开发流程
- 更新 Git 命令速查（附录A），添加远程仓库操作
**维护者**: 小栗子 🌰

### 2026-03-03

- 更新 API 测试命令，添加 `--reruns 2` 参数
- 新增要求：测试需要重试时必须修复根因  
**维护者**: 小栗子 🌰
