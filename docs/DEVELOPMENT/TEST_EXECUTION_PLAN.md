# Tracker 测试执行计划

> **版本**: v1.0 | **创建日期**: 2026-02-15 | **状态**: 生效

---

## 1. 概述

本文档定义 Tracker 项目在不同开发阶段需要执行的测试类型、用例及执行规范。

### 1.1 文档目的

- 明确各开发阶段的测试要求
- 规范测试执行命令和操作流程
- 规定测试报告的生成时机和保存位置
- 定义 Bug 和测试代码问题的记录方式

### 1.2 测试阶段概览

| 阶段 | 触发条件 | 测试类型 | 是否生成报告 |
|------|----------|----------|--------------|
| 代码提交前 | 每次 `git commit` 前 | 冒烟测试 | 否 |
| 合并到 develop | Merge Request/PR | 完整集成测试 | ✅ 是 |
| 每日凌晨 3 点 | Cron 定时任务 | 集成测试 | ✅ 是 |
| 手动执行 | 用户主动触发 | E2E 测试 | 可选 |

---

## 2. 代码提交前测试

### 2.1 执行时机

每次代码提交（`git commit`）前必须执行。

### 2.2 测试类型

#### 2.2.1 ESLint 检查（前端代码）

**检查内容**:
- JavaScript 语法错误
- 关键函数完整性（renderTC, renderCP, loadCP, loadTC 等）
- API 端点定义（API_BASE 和 /api/* 端点）

**执行命令**:
```bash
cd /projects/management/tracker/dev
bash check_frontent.sh
```

**通过标准**: 所有检查项显示 ✅

---

#### 2.2.2 API 测试

**覆盖范围**: 所有 API 接口功能

**执行命令**:
```bash
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/ -v --reruns 2
```

**冒烟用例**（提交前至少执行这些核心用例）:

| 用例 ID | 说明 |
|---------|------|
| test_get_version | 版本接口可用 |
| test_get_projects | 项目列表获取 |
| test_create_project | 项目创建 |
| test_get_cp_list | CP 列表获取 |
| test_get_tc_list | TC 列表获取 |
| test_create_cp | CP 创建 |
| test_create_tc | TC 创建 |
| test_update_cp | CP 更新 |
| test_update_tc | TC 更新 |
| test_delete_cp | CP 删除 |
| test_delete_tc | TC 删除 |

**通过标准**: 冒烟用例 100% 通过

---

#### 2.2.3 Playwright 冒烟测试

**测试文件**: `tests/test_ui/specs/smoke/smoke.spec.ts`

**执行命令**:
```bash
cd /projects/management/tracker/dev
PLAYWRIGHT_BROWSERS_PATH=/tmp/.playwright HOME=/home/hqi XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/smoke/ --project=firefox --timeout=60000
```

> **注意**: v0.10.x 版本新增了 Intro 引导页，测试已适配自动处理。如遇浏览器启动问题，确保设置正确的 HOME 目录。

**冒烟用例清单** (共 20 个):

##### 01-smoke.spec.ts (14 个用例)

| 用例 ID | 说明 |
|---------|------|
| SMOKE-001 | 页面加载 |
| SMOKE-002 | admin 登录成功 |
| SMOKE-003 | guest 登录成功 |
| SMOKE-004 | 错误密码提示 |
| SMOKE-005 | 项目切换 |
| SMOKE-006 | 创建项目 |
| SMOKE-007 | CP 标签切换 |
| SMOKE-008 | 创建 CP |
| SMOKE-009 | 编辑 CP |
| SMOKE-010 | 删除 CP |
| SMOKE-011 | TC 标签切换 |
| SMOKE-012 | 创建 TC |
| SMOKE-013 | 编辑 TC |
| SMOKE-014 | 删除 TC |

##### 02-login.spec.ts (6 个用例)

| 用例 ID | 说明 |
|---------|------|
| LOGIN-001 | 登录后显示用户名 |
| LOGIN-002 | guest 无用户管理按钮 |
| LOGIN-003 | user 无删除项目按钮 |
| LOGIN-004 | 登录后 Cookie |
| LOGIN-005 | 登出功能 |
| LOGIN-006 | Progress Charts Tab |

**通过标准**: 20/20 用例通过

---

### 2.3 提交前检查清单

```
□ ESLint 检查通过 (bash check_frontent.sh)
□ API 测试冒烟用例通过 (pytest tests/test_api/ -v)
□ Playwright 冒烟测试通过 (npx playwright test tests/test_ui/specs/smoke/...)
□ 无控制台错误
□ 无新增 lint 警告
```

---

## 3. 合并到 develop 分支测试

### 3.1 执行时机

功能分支合并到 `develop` 分支前（Merge Request 或手动合并）。

### 3.2 测试类型

#### 3.2.1 完整 API 测试

**执行命令**:
```bash
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/ -v --tb=short
```

> **注意**：合并到 develop 分支时**不使用** `--reruns` 参数，确保测试真正稳定。如果需要重试才能通过的测试，必须修复根因。

**测试用例数量**: 207 个

**测试用例清单**:

| 分类 | 用例数量 | 说明 |
|------|----------|------|
| 项目管理 | 6 | 版本、列表、创建、重复、归档 |
| CP 管理 | 5 | 列表、创建、更新、删除 |
| TC 管理 | 5 | 列表、创建、更新、删除、状态 |
| 批量操作 | 14 | 批量更新状态、目标日期、DV里程碑、优先级 |
| 过滤排序 | 15 | 按 DV/Owner/Category 过滤、组合过滤、排序 |
| 导入功能 | 16 | 模板下载、CP/TC 导入、CSV 导入 |
| 导出功能 | 9 | CP/TC Excel/CSV 导出、默认格式 |
| 边界条件 | 25 | 必填字段、重复检测、无效参数 |
| 异常处理 | 16 | 无效项目ID、无效类型、空项目 |
| 性能测试 | 24 | 响应时间、吞吐量、过滤查询 |
| 认证模块 | ~40 | 登录、登出、权限检查、Cookie |
| 进度图表 | ~30 | 计划曲线、实际曲线、快照管理 |
| 认证API | ~22 | 管理员权限、用户管理 |

**通过标准**: 207/207 用例通过

---

#### 3.2.2 完整集成测试

**执行命令**:
```bash
cd /projects/management/tracker/dev
PLAYWRIGHT_BROWSERS_PATH=/tmp/.playwright HOME=/home/hqi XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/integration/ --project=firefox --timeout=60000
```

> **注意**: v0.10.x 版本新增了 Intro 引导页和 changePasswordModal，测试已适配自动处理。

**测试用例数量**: 110 个

**测试用例清单**:

##### 导入导出集成测试 (import-export.spec.ts) - v0.7.0 新增

| 用例 ID | 说明 |
|---------|------|
| IMP-001 | CP 导入按钮存在 |
| IMP-002 | CP 导入对话框打开 |
| IMP-003 | TC 导入按钮存在 |
| IMP-004 | TC 导入对话框打开 |
| EXP-001 | CP 导出按钮存在 |
| EXP-002 | CP 导出对话框打开 |
| EXP-003 | CP 导出对话框显示项目信息 |
| EXP-004 | TC 导出按钮存在 |
| EXP-005 | TC 导出对话框打开 |
| EXP-007 | CP CSV 导出触发下载 |
| EXP-008 | TC CSV 导出触发下载 |
| TMPL-001 | CP 模板下载 |
| DLG-001 | 导入对话框关闭 |
| DLG-002 | 导出对话框关闭 |

##### CP 集成测试 (cp.spec.ts)

| 用例 ID | 说明 |
|---------|------|
| CP-001 | 创建 CP 并验证 |
| CP-002 | 编辑 CP |
| CP-003 | 删除 CP |
| CP-004 | 按 Feature 过滤 CP |
| CP-005 | 按 Priority 过滤 CP |
| CP-007 | 展开/折叠 CP 详情 |
| CP-008 | 创建 CP - 验证必填字段 |
| CP-009 | CP 数据持久化验证 |

##### TC 集成测试 (tc.spec.ts)

| 用例 ID | 说明 |
|---------|------|
| TC-001 | 创建 TC 并验证 |
| TC-002 | 编辑 TC |
| TC-003 | 删除 TC |
| TC-004 | 按 Status 过滤 TC |
| TC-005 | 按 Owner 过滤 TC |
| TC-006 | 按 Category 过滤 TC |
| TC-007 | 更新 TC 状态 |
| TC-008 | 批量更新 Status |
| TC-009 | 批量更新 Target Date |
| TC-010 | 创建 TC - 验证必填字段 |
| TC-011 | TC 数据持久化验证 |

##### 连接集成测试 (connections.spec.ts)

| 用例 ID | 说明 |
|---------|------|
| CONN-001 | 创建 CP 和 TC |
| CONN-002 | 展开 CP 详情 |
| CONN-003 | 编辑 CP |
| CONN-004 | 创建多个 CP |
| CONN-005 | 创建多个 TC |

##### 其他集成测试文件

| 文件 | 用例数 | 说明 |
|------|--------|------|
| 06-permissions-api.spec.ts | 12 | API 权限验证 |
| 07-permissions-ui.spec.ts | 9 | UI 权限验证 |
| 08-user-management.spec.ts | 10 | 用户管理功能 |
| 09-project-management.spec.ts | 5 | 项目管理功能 |
| 10-help.spec.ts | 3 | 帮助手册 |
| 11-date-validation.spec.ts | 4 | 日期验证 |
| actual_curve.spec.ts | 11 | 实际曲线图表 |
| planned_curve.spec.ts | 12 | 计划曲线图表 |
| progress_charts.spec.ts | 6 | 进度图表 |

**通过标准**: 110/110 用例通过

---

### 3.3 测试报告

#### 3.3.1 报告要求

合并到 develop 分支时**必须**生成正式测试报告。

#### 3.3.2 报告保存位置

```
/projects/management/tracker/docs/REPORTS/
```

#### 3.3.3 报告命名格式

```
TRACKER_TEST_REPORT_{测试类型}_{YYYYMMDD}_{HHMM}.md
```

示例:
- `TRACKER_TEST_REPORT_INTEGRATION_20260215_1430.md`
- `TRACKER_TEST_REPORT_NIGHTLY_20260215_0300.md`

#### 3.3.4 报告内容结构

```markdown
# Tracker 集成测试报告

> **测试类型**: 合并前集成测试 | **日期**: 2026-02-15 14:30

## 测试摘要

| 测试类型 | 总数 | 通过 | 失败 | 通过率 |
|----------|------|------|------|--------|
| API 测试 | 29 | 29 | 0 | 100% |
| 集成测试 | XX | XX | 0 | 100% |

## 测试执行时间

| 开始时间 | 完成时间 | 持续时间 |
|----------|----------|----------|
| 14:25:00 | 14:35:00 | 10 分钟 |

## API 测试结果

// 测试输出...

## 集成测试结果

// 测试输出...

## 发现的问题

### 代码 Bug

// 如果发现代码 Bug，记录到 BUGLOG

### 测试代码问题

// 如果发现测试代码问题，记录在此
```

---

## 4. 每日凌晨 3 点测试

### 4.1 执行时机

每天凌晨 3:00（UTC+8），通过 Cron 任务触发。

### 4.2 测试类型

执行与「合并到 develop 分支」相同的**完整集成测试**：

1. 完整 API 测试
2. 完整集成测试（CP + TC + Connections）

### 4.3 执行方式

通过 `isolated agentTurn` 模式执行：

```json
{
  "name": "每日集成测试",
  "schedule": {
    "kind": "cron",
    "expr": "0 3 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日集成测试...",
    "timeoutSeconds": 600
  },
  "sessionTarget": "isolated"
}
```

### 4.4 测试报告

#### 4.4.1 报告要求

每日测试**必须**生成正式测试报告。

#### 4.4.2 报告保存位置

```
/projects/management/tracker/docs/REPORTS/
```

#### 4.4.3 报告命名格式

```
TRACKER_TEST_REPORT_NIGHTLY_YYYYMMDD.md
```

示例: `TRACKER_TEST_REPORT_NIGHTLY_20260215.md`

---

## 5. 手动执行测试集（E2E）

> ⚠️ **重要**: E2E 测试当前已被**跳过 (Skip)**，不可执行！
> 
> 原因: E2E 测试使用 `test.describe.skip` 标记，已从测试套件中禁用。
> 如需重新启用，需移除该标记并修复相关测试用例。

### 5.1 适用场景

> **状态**: 暂不适用 - E2E 测试已禁用

用户需要手动执行以下测试时：
- 完整端到端业务流程验证
- 大批量数据创建测试
- 数据一致性验证
- 特殊场景复现

### 5.2 测试类型

#### 5.2.1 E2E 完整工作流测试 ⚠️ 已跳过

**文件**: `tests/test_ui/specs/e2e/full-workflow.spec.ts`

**状态**: 已禁用 (使用 `test.describe.skip`)

**用例清单** (共 5 个):

| 用例 ID | 说明 | 状态 |
|---------|------|------|
| E2E-001 | 完整项目创建工作流 | ⏸️ 已跳过 |
| E2E-002 | 项目切换数据隔离 | ⏸️ 已跳过 |
| E2E-003 | 批量操作完整流程 | ⏸️ 已跳过 |
| E2E-004 | 页面刷新后状态恢复 | ⏸️ 已跳过 |
| E2E-005 | 模态框打开关闭流程 | ⏸️ 已跳过 |

---

#### 5.2.2 E2E 数据创建测试 ⚠️ 已跳过

**文件**: `tests/test_ui/specs/e2e/data-creation.spec.ts`

**状态**: 已禁用 (使用 `test.describe.skip`)

**用例清单** (共 2 个):

| 用例 ID | 说明 | 状态 |
|---------|------|------|
| E2E-006 | 批量创建 CP | ⏸️ 已跳过 |
| E2E-007 | 批量创建 TC | ⏸️ 已跳过 |
| E2E-008 | 数据一致性验证 | ⏸️ 已跳过 |

---

#### 5.2.3 完整 E2E 测试套件 ⚠️ 已跳过

**执行命令**:
```bash
# 注意: 由于测试已被 skip，执行将返回 0 个测试用例
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/e2e/ --project=firefox --timeout=60000
```

**当前状态**: 0/7 用例通过 (全部跳过)

**如需重新启用 E2E 测试**:
1. 移除 `full-workflow.spec.ts` 和 `data-creation.spec.ts` 中的 `test.describe.skip`
2. 根据当前 v0.9.0 版本更新测试用例（认证流程、UI 变化等）
3. 执行测试验证通过后移除本章节的"已跳过"标注

---

### 5.3 报告要求

E2E 测试报告为**可选**。如需生成，保存到 `docs/REPORTS/` 目录：

```
TRACKER_TEST_REPORT_E2E_YYYYMMDD.md
```

---

## 6. Bug 记录规范

### 6.1 记录位置

所有发现的代码 Bug 必须记录到 BugLog：

```
/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md
```

### 6.2 记录格式

使用 BugLog 模板（参考 `docs/BUGLOG/` 目录下的模板）：

```markdown
## Bug 记录

| 字段 | 内容 |
|------|------|
| Bug ID | BUG-XXX |
| 发现版本 | v0.6.2 |
| 发现阶段 | 集成测试 |
| 发现日期 | 2026-02-15 |
| 优先级 | P1/P2/P3 |
| 状态 | 待修复/修复中/已关闭 |

### 问题描述

// 问题描述...

### 复现步骤

1. ...
2. ...

### 预期行为

// 预期行为...

### 实际行为

// 实际行为...
```

---

## 7. 测试代码问题记录规范

### 7.1 记录位置

测试代码问题记录在**测试报告**的「发现的问题」章节中。

### 7.2 记录内容

测试代码问题包括：
- 测试用例逻辑错误
- 测试数据不足或错误
- 测试用例遗漏
- 测试环境问题（非代码 Bug）

### 7.3 记录格式

```markdown
### 测试代码问题

| 问题 ID | 类型 | 描述 | 涉及用例 | 修复建议 |
|---------|------|------|----------|----------|
| TEST-001 | 测试数据 | 测试数据不足 | TC-005 | 补充 XXX 测试数据 |
| TEST-002 | 用例逻辑 | 断言条件错误 | CP-003 | 修改断言为 XXX |
```

---

## 8. 快速参考

### 8.1 命令速查

| 阶段 | 命令 | 说明 |
|------|------|------|
| ESLint 检查 | `cd dev && bash check_frontent.sh` | 前端代码检查 |
| API 测试（本地开发） | `cd dev && PYTHONPATH=. pytest tests/test_api/ -v --reruns 2` | 允许重试 2 次 (207 用例) |
| API 测试（CI/CD） | `cd dev && PYTHONPATH=. pytest tests/test_api/ -v` | 不允许重试 (207 用例) |
| 冒烟测试 | `cd dev && npx playwright test tests/test_ui/specs/smoke/01-smoke.spec.ts tests/test_ui/specs/smoke/02-login.spec.ts --project=firefox` | UI 冒烟 (20 用例) |
| 集成测试 | `cd dev && npx playwright test tests/test_ui/specs/integration/ --project=firefox` | UI 集成 (110 用例) |
| E2E 测试 | `cd dev && npx playwright test tests/test_ui/specs/e2e/ --project=firefox` | ⚠️ 端到端 (已跳过，7 用例) |
| 完整测试 | `cd dev && npx playwright test tests/test_ui/ --project=firefox` | 全部 UI (不含 E2E) |

### 8.2 测试稳定性要求

| 测试类型 | 本地开发 | CI/CD | 说明 |
|----------|----------|-------|------|
| API 测试 | `--reruns 2` | 无重试 | 本地允许重试，CI 必须稳定 |
| UI 测试 | N/A | N/A | Playwright 自动等待，较稳定 |
| ESLint | N/A | N/A | 代码静态检查，无随机性 |

> **⚠️ 重要**：如果测试需要重试才能通过，说明存在根因问题。必须修复测试代码或应用代码，而不是依赖重试机制。

### 8.2 服务启动

```bash
# 开发版（端口 8081）
cd /projects/management/tracker/dev && ./start_server_test.sh

# 生产版（端口 8080）
cd /projects/management/tracker/dev && python3 server.py
```

---

**文档版本**: v1.3  
**创建日期**: 2026-02-15  
**更新日期**: 2026-03-07

---

## 更新日志

### v1.3 (2026-03-07)

- 更新 API 测试用例数量: 130+ → 207
- 更新冒烟测试用例清单: 10 → 20 个用例
  - 新增 02-login.spec.ts (6 个用例)
  - 更新 01-smoke.spec.ts 用例说明
- 更新集成测试用例数量: 40+ → 110 个用例
- 新增其他集成测试文件清单 (permissions, user-management, help, date-validation, curves 等)
- **E2E 测试明确标注为"已跳过"**
  - 说明跳过原因 (使用 `test.describe.skip`)
  - 添加重新启用步骤
- 更新快速参考命令，标注 E2E 测试状态
**维护者**: 小栗子 🌰

### v1.2 (2026-03-03)

- 新增测试命令速查表格，区分本地开发和 CI/CD
- 更新 API 测试命令，添加 `--reruns 2` 参数（本地开发）
- 明确 CI/CD 必须不使用重试，确保测试真正稳定
- 新增测试稳定性要求表格  
**维护者**: 小栗子 🌰
