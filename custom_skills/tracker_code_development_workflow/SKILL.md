---
name: tracker_code_development_workflow
description: This skill should be used when the user wants to develop new features for Tracker (芯片验证管理系统), including Flask backend API development, frontend UI implementation, pytest API testing, Playwright UI testing, or needs to run the complete 7-stage development workflow. Must use this workflow for any Tracker v0.x.x feature development.
---

# Tracker 代码开发工作流

## 概述

Tracker 项目专用代码开发工作流，通过7个阶段子代理完成完整开发流程：

| 阶段 | 子代理 | 职责 |
|------|--------|------|
| 1 | Subagent A (开发) | 读取规格书，开发代码 |
| 2 | Subagent B (审查) | 代码审查，决策优化轮次(1-3) |
| 3 | Subagent A (优化) | 根据审查意见优化代码 |
| 4 | **Subagent C (API测试)** | **API测试开发、调试、修复** |
| 5 | **Subagent D (UI测试)** | **Playwright UI测试开发、调试、修复** |
| 6 | **Subagent E (手工测试)** | **agent-browser手工测试执行、调试** |
| 7 | **Subagent F (测试验收)** | **验收C/D/E输出，给出迭代建议** |
| - | 主代理 | 流程控制，不参与实际验收判断 |

---

## 参数解析

用户可通过以下方式调用：
- `/tracker-code-development-workflow v0.9.2` → 指定版本号
- `/tracker-code-development-workflow v0.9.2 phase4-6` → 版本号 + 阶段范围
- `/tracker-code-development-workflow phase4` → 仅指定阶段

### 参数提取规则

从用户消息中提取以下参数：

#### 1. 版本号 (`version`)

**模式**: `v\d+\.\d+\.\d+` 或 `\d+\.\d+\.\d+`

**示例**: `v0.9.2`, `0.9.1`

**用途**:
- 规格书路径: `docs/SPECIFICATIONS/tracker_SPECS_{version}.md`
- 测试计划: `docs/PLANS/TEST_PLAN_{version}.md`
- 测试报告: `docs/REPORTS/TEST_REPORT_{version}_{date}.md`

**默认值**: 如果未指定，必须询问用户

#### 2. 阶段范围 (`phases`)

**模式**: `phase(\d+)(?:-(\d+))?`

**示例**:
- `phase4` → 仅执行阶段4
- `phase4-6` → 执行阶段4、5、6
- `phase1-3` → 执行阶段1、2、3

**默认值**: 如果未指定，执行全部阶段 (1-7)

### 参数应用示例

```markdown
# 用户输入: "/tracker-code-development-workflow v0.9.2 phase4-6"

## 解析结果
- 版本: v0.9.2
- 阶段: [4, 5, 6]

## 执行计划
1. ✅ 跳过阶段1 (代码开发)
2. ✅ 跳过阶段2 (代码审查)
3. ✅ 跳过阶段3 (优化确认)
4. ▶️ 执行阶段4 (API测试)
5. ▶️ 执行阶段5 (UI测试)
6. ▶️ 执行阶段6 (手工测试)
7. ✅ 跳过阶段7 (测试验收) - 或根据参数包含
```

### 执行逻辑

1. 解析用户消息提取 `version` 和 `phases` 参数
2. 如果版本号未指定，询问用户：`请指定版本号，例如 v0.9.2`
3. 验证版本相关文件是否存在（规格书、测试计划）
4. 根据 `phases` 参数决定执行哪些阶段
5. 按顺序执行指定阶段，跳过未包含的阶段

## 阶段配置总览

| 阶段 | 子代理 | 模型 | max_retries | 推理深度 |
|------|--------|------|-------------|---------|
| 开发 | A | sonnet | 3 | 高 |
| 审查 | B | opus | 3 | 极高 |
| 优化 | A | sonnet | 3 | 高 |
| API测试 | C | sonnet | 3 | 中高 |
| UI测试 | D | sonnet | 3 | 高 |
| 手工测试 | E | sonnet | 2 | 中 |
| 测试验收 | F | opus | 2 | 高 |

---

# 阶段1：代码开发 (Subagent A)

> 保持不变...

---

# 阶段2：代码审查 (Subagent B)

> 保持不变...

---

# 阶段3：优化确认 (Subagent A - 复用)

> 保持不变...

---

# 阶段4：API测试 (Subagent C)

## 职责定义

**API测试工程师** - 专门负责Python pytest API测试的开发、调试和修复。

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker API测试开发"
```

## 必须激活的技能

1. **Bash** - 运行 pytest
2. **pytest** - API测试框架

## 必须阅读的文档

1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. `/projects/management/tracker/docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` - 测试流程
3. `/projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{version}.md` - **对应版本的测试计划（必须阅读）**

## Prompt模板

```
# 阶段4：API测试开发 (Subagent C)

## 角色
你是专业的API测试工程师，负责使用pytest开发、调试和修复API测试用例。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口，test_data 目录
- **测试框架**: pytest

## 测试命令
```bash
# API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v

# 特定测试文件
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_{name}.py -v
```

## 推理要求
- 推理深度：中到高
- 要求：调试时需要分步分析失败原因

## 核心任务

### 1. 新测试用例开发（必做）
- **必须根据版本测试计划开发新测试用例**
- 测试计划路径: `/projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{version}.md`
- **必须创建的测试用例**（从测试计划中提取API测试部分）:
  - 例如: API-FB-001, API-FB-002, API-FB-003
- 新测试用例必须创建在: `/projects/management/tracker/dev/tests/test_api/`
- 测试文件命名规范: `test_api_{功能名}.py`

### 2. 测试调试（必做）
- 运行测试并分析失败原因
- **应用代码问题** → 确认根因 + 报告给主代理 + 记录到 Buglog（**不修复**）
- **测试代码问题** → 修复测试代码 + **记录到测试报告**（必须修复）
- 验证修复后测试通过

### 3. Bug记录（必做）
- 应用代码问题: 记录到 `/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md`（只记录根因，不修复）
- **测试代码问题**: 修复细节记录到测试报告（见下方文档结构中的"测试代码修复记录"）
- 记录格式：参考现有bug记录格式

## 测试报告要求

### 输出路径（强制）
测试报告必须输出到以下路径：

```
/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md
```

例如：
- `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v0.9.1_20260308.md`

### 文档结构（强制）
```markdown
# Tracker v{版本号} API测试报告

> **测试类型**: API测试 | **版本**: v{版本号} | **日期**: {YYYY-MM-DD}

---

## 1. 测试概览

### 1.1 测试环境

| 项目 | 值 |
|------|-----|
| 测试服务器 | http://localhost:8081 |
| 测试框架 | pytest |
| 测试日期 | {YYYY-MM-DD} |

### 1.2 关联文档

| 文档 | 路径 |
|------|------|
| 版本规格书 | /projects/management/tracker/docs/SPECIFICATIONS/tracker_SPECS_v{版本号}.md |
| 测试计划 | /projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{版本号}.md |

### 1.3 测试结果汇总

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 通过率 |
|----------|------|------|------|------|--------|
| API 测试 | {N} | {N} | 0 | 0 | **100%** |

---

## 2. 新增测试用例

### 2.1 测试文件

| 文件 | 用例数 | 结果 |
|------|--------|------|
| test_api_{功能}.py | {N} | ✅ |

### 2.2 测试用例详情

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| API-FB-001 | 提交反馈-成功 | ✅ 通过 |
| API-FB-002 | 提交反馈-未登录 | ✅ 通过 |

---

## 3. Bug修复记录 (应用代码问题)

### BUG-XXX: {标题}

**发现日期**: {YYYY-MM-DD}
**状态**: ✅ 已修复

**问题描述**: ...
**修复方案**: ...

---

## 4. 测试代码修复记录

> 本章节记录测试代码问题的修复（与Bug修复记录区分）

| 修复ID | 问题类型 | 问题描述 | 修复方案 | 状态 |
|--------|----------|----------|----------|------|
| TEST-FIX-001 | 测试代码 | session未清理 | 在teardown中添加cleanup | ✅ |
| TEST-FIX-002 | 测试代码 | 断言错误 | 修改断言条件 | ✅ |

---

## 5. 验收标准

| 标准 | 状态 |
|------|------|
| API测试 100%通过 | ✅ |
| 新测试用例已创建 | ✅ |
| Bug已记录 (应用代码) | ✅ |
| 测试代码修复已记录 | ✅ |

---

**报告生成时间**: {YYYY-MM-DD}
**署名**: Claude Code
```

### 如果报告已存在
- 追加新内容到现有报告
- 保持文档结构完整

## 禁止事项
- 🔴 **严格禁止在非/tmp目录以外执行 rm -rf 命令**
- 禁止跳过任何测试用例

## 输出格式
```
## API测试结果
- 测试总数: {N}
- 通过: {N}
- 失败: {N}

## 新增测试用例
| 用例ID | 说明 | 结果 |
|--------|------|------|
| API-FB-001 | ... | ✅ |

## Bug记录
- {bug描述}

## 测试报告
- 路径: /projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md
- 状态: ✅ 已生成
```

---

# 阶段5：UI测试 (Subagent D)

## 职责定义

**Playwright UI测试工程师** - 专门负责Playwright UI测试的开发、调试和修复。

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker Playwright UI测试开发"
```

## 必须激活的技能

1. **Bash** - 运行 Playwright
2. **Playwright** - UI测试框架

## 必须阅读的文档

1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. `/projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{version}.md` - **对应版本的测试计划（必须阅读）**

## Prompt模板

```
# 阶段5：Playwright UI测试开发 (Subagent D)

## 角色
你是专业的Playwright UI测试工程师，负责使用Playwright开发、调试和修复UI测试用例。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口，test_data 目录
- **测试框架**: Playwright

## 测试命令
```bash
# UI 测试
# (仅运行冒烟测试 + 版本测试计划指定的新测试文件)
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/smoke/ --project=firefox

# 特定测试文件
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/12-feedback.spec.ts --project=firefox
```

## 推理要求
- 推理深度：高
- 要求：UI调试需要结合浏览器检查

## 核心任务

### 1. 新测试用例开发（必做）
- **必须根据版本测试计划开发新测试用例**
- 测试计划路径: `/projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{version}.md`
- **必须创建的测试用例**（从测试计划中提取UI测试部分）:
  - 例如: UI-FB-001, UI-FB-002, UI-CP-001, UI-TAB-001
- 新测试用例必须创建在: `/projects/management/tracker/dev/tests/test_ui/specs/integration/`
- 测试文件命名规范: `{序号}-{功能名}.spec.ts`

### 2. 测试调试（必做）
- 运行测试并分析失败原因
- **应用代码问题** → 确认根因 + 报告给主代理 + 记录到 Buglog（**不修复**）
- **测试代码问题** → 修复测试代码 + **记录到测试报告**（必须修复）
- **session隔离问题** → 修复测试代码添加清理逻辑 + **记录到测试报告**（必须修复）
- 验证修复后测试通过

### 3. Bug记录（必做）
- 应用代码问题: 记录到 `/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md`（只记录根因，不修复）
- **测试代码问题**: 修复细节记录到测试报告（见下方文档追加内容中的"X.4 失败用例分析"）

## 测试报告要求

### 输出路径（强制）
追加到已有的测试报告：
```
/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md
```

### 文档追加内容（强制）
```markdown
---

## X. UI测试结果

### X.1 测试结果汇总

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 通过率 |
|----------|------|------|------|------|--------|
| UI 冒烟测试 | {N} | {N} | 0 | 0 | **100%** |
| UI 新功能测试 | {N} | {N} | 0 | 0 | **100%** |

### X.2 新增UI测试用例

| 文件 | 用例数 | 结果 |
|------|--------|------|
| 12-feedback.spec.ts | 5 | ✅ |

### X.3 测试用例详情

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-FB-001 | 反馈标签页存在 | ✅ 通过 |
| UI-FB-002 | 反馈表单类型选择 | ✅ 通过 |

### X.4 失败用例分析

| 测试 | 原因分析 | 问题类型 | 修复方案 | 状态 |
|------|----------|----------|----------|------|
| SMOKE-001 | session未清理 | 测试代码 | 添加cleanup | ✅ |
```

## 禁止事项
- 🔴 **严格禁止在非/tmp目录以外执行 rm -rf 命令**
- 禁止跳过任何测试用例
- 禁止忽略session隔离问题

## 输出格式
```
## UI测试结果
- 冒烟测试: {N}/{N} 通过
- 新功能测试: {N}/{N} 通过

## 新增测试用例
| 用例ID | 说明 | 结果 |
|--------|------|------|
| UI-FB-001 | ... | ✅ |

## 失败分析
- {分析}

## Bug记录
- {bug描述}
```
```

---

# 阶段6：手工测试 (Subagent E)

## 职责定义

**手工测试工程师** - 使用agent-browser进行手工测试执行、调试。

> **技能依赖**: 必须激活 `agent-browser-usage` 技能获取完整使用指南
>
> 适用场景：
> - Playwright无法稳定运行的复杂UI测试
> - 需要实时观察浏览器行为的测试
> - CSS/样式调试
> - 交互流程验证

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker手工测试执行"
```

## 必须激活的技能

1. **agent-browser-usage** - 命令行浏览器自动化（必须激活，获取完整使用指南）
2. **Bash** - 辅助命令

## 必须阅读的文档

1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. 测试计划中需要手工验证的部分

## Prompt模板

```
# 阶段6：手工测试执行 (Subagent E)

## 角色
你是手工测试工程师，负责使用agent-browser进行UI验证和调试。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口
- **工具**: agent-browser

## 推理要求
- 推理深度：中
- 要求：结合代码分析和浏览器观察

## 核心任务

### 1. 手工验证（必做）
- 验证Playwright难以稳定测试的UI功能
- 检查控制台错误: `agent-browser errors`
- 检查JavaScript运行时问题
- 验证CSS样式渲染

### 2. 问题定位（必做）
- 复现问题并记录步骤
- 分析控制台错误
- 检查元素存在性和状态
- **应用代码问题** → 确认根因 + 记录到 Buglog（**不修复**）
- **测试代码问题** → 修复测试代码 + **记录到测试报告**（必须修复）

### 3. Bug记录（必做）
- 应用代码问题: 记录到 `/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md`（只记录根因，不修复）
- **测试代码问题**: 修复细节记录到测试报告

## 测试报告要求

### 输出路径（强制）
追加到已有的测试报告：
```
/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md
```

### 文档追加内容（强制）
```markdown
---

## X. 手工测试结果

### X.1 测试执行记录

| 测试项 | 工具 | 结果 | 备注 |
|--------|------|------|------|
| 登录界面样式 | agent-browser | ✅ 正常 | 紫色header |
| 登录功能 | agent-browser | ✅ 正常 | |
| 控制台错误 | agent-browser | ⚠️ 有警告 | 见下文 |

### X.2 控制台检查结果

```
[error] Identifier 'API_ENDPOINTS' has already been declared
```

### X.3 应用代码问题修复

#### BUG-XXX: API_ENDPOINTS重复声明

**问题**: 浏览器控制台报错
**根因**: app_constants.js和index.html都声明了API_ENDPOINTS
**修复**: 修改app_constants.js使用window对象
**验证**: ✅ 错误已消除

### X.4 测试代码修复记录

> 本章节记录测试代码问题的修复（与X.3应用代码问题区分）

| 修复ID | 问题类型 | 问题描述 | 修复方案 | 状态 |
|--------|----------|----------|----------|------|
| TEST-FIX-001 | 测试代码 | 测试用例未清理数据 | 在teardown中添加cleanup | ✅ |
```

## 禁止事项
- 🔴 **严格禁止在非/tmp目录以外执行 rm -rf 命令**

## 输出格式
```
## 手工测试结果
- 测试项: {N}
- 通过: {N}
- 发现问题: {N}

## 问题列表
| 问题 | 状态 |
|------|------|
| 控制台JS错误 | 已修复 |

## Bug记录
- {bug描述}
```
```

---

# 阶段7：测试验收 (Subagent F)

## 职责定义

**测试验收工程师** - 验收Subagent C/D/E的输出是否符合要求，并给出迭代建议。

> **重要**: 主代理不参与实际验收判断，完全依赖测试验收Subagent的反馈。

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "opus"
- description: "Tracker测试验收"
```

## 必须激活的技能

1. **Bash** - 验证文件存在和测试结果
2. **Read** - 检查文档内容

## 必须执行的验收检查

### 1. API测试验收 (Subagent C输出)

| 检查项 | 验收标准 |
|--------|----------|
| 新测试文件存在 | `/projects/management/tracker/dev/tests/test_api/test_api_{name}.py` |
| 测试用例数量 | >= 测试计划要求的API测试用例数 |
| 测试通过率 | 100% |
| Bug记录 | 至少记录了发现的应用代码问题 |
| 测试报告 | 存在于 `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md` |

### 2. UI测试验收 (Subagent D输出)

| 检查项 | 验收标准 |
|--------|----------|
| 新测试文件存在 | `/projects/management/tracker/dev/tests/test_ui/specs/integration/{name}.spec.ts` |
| 测试用例数量 | >= 测试计划要求的UI测试用例数 |
| 测试通过率 | 100% |
| Bug记录 | 至少记录了发现的应用代码问题 |

### 3. 手工测试验收 (Subagent E输出)

| 检查项 | 验收标准 |
|--------|----------|
| 控制台检查 | 已执行控制台错误检查 |
| 问题记录 | 发现的问题已记录 |
| 修复验证 | 已验证问题是否修复 |

## Prompt模板

```
# 阶段7：测试验收 (Subagent F)

## 角色
你是测试验收工程师，负责验证测试阶段的输出是否符合要求。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口

## 验收标准

### API测试验收 (C输出)
- [ ] 新测试文件存在
- [ ] 测试用例数量 >= 要求
- [ ] 测试通过率 100%
- [ ] Bug记录完整
- [ ] 测试报告已生成

### UI测试验收 (D输出)
- [ ] 新测试文件存在
- [ ] 测试用例数量 >= 要求
- [ ] 测试通过率 100%
- [ ] Bug记录完整

### 手工测试验收 (E输出)
- [ ] 控制台检查已执行
- [ ] 问题已记录

## 验证命令
```bash
# 检查API测试文件
ls /projects/management/tracker/dev/tests/test_api/test_api_*.py

# 检查UI测试文件
ls /projects/management/tracker/dev/tests/test_ui/specs/integration/*.spec.ts

# 检查测试报告
ls /projects/management/tracker/docs/REPORTS/TEST_REPORT_v{version}_*.md

# 运行API测试验证
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v --tb=short

# 检查Bug记录
grep -l "BUG-" /projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md
```

## 验收决策

### 合格标准
- 所有验收检查项通过
- 或者失败项有明确说明（非阻塞性问题）

### 迭代建议

如果不合格，给出具体迭代建议：
1. 哪个Subagent需要重做
2. 具体需要补充什么
3. 预计需要几轮迭代

## 输出格式

```
## 验收结果

### API测试验收 (C)
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 新测试文件存在 | ✅/❌ | ... |
| 测试用例数量 | ✅/❌ | ... |

### UI测试验收 (D)
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 新测试文件存在 | ✅/❌ | ... |

### 手工测试验收 (E)
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 控制台检查 | ✅/❌ | ... |

## 总体判定

**判定**: 合格/需迭代

### 迭代建议
- 轮次: {N}
- 需要重做: {Subagent名称}
- 具体要求:
  1. ...
  2. ...

### 通过项
- [ ] {通过项}
```

---

# 工作流执行流程

## 参数解析（第一步）

在开始任何工作前，必须先解析参数：

```python
# 参数解析逻辑（伪代码）
import re

def parse_args(user_message):
    # 提取版本号
    version_match = re.search(r'v?(\d+\.\d+\.\d+)', user_message)
    version = version_match.group(0) if version_match else None

    # 提取阶段范围
    phase_match = re.search(r'phase(\d+)(?:-(\d+))?', user_message)
    if phase_match:
        start = int(phase_match.group(1))
        end = int(phase_match.group(2)) if phase_match.group(2) else start
        phases = list(range(start, end + 1))
    else:
        phases = [1, 2, 3, 4, 5, 6, 7]  # 默认全部阶段

    return version, phases
```

## 完整流程

```
0. ⚠️ 参数解析与分支检查（前置步骤）
   ├── 解析版本号和阶段范围参数
   ├── 如果版本号未指定 → 询问用户
   ├── 确保当前在 develop 分支
   ├── 从 develop 创建 feature/* 分支
   └── 绝对禁止在 main 分支上开发

1. 验证输入
   ├── 检查规格文档是否存在 (docs/PLANS/)
   └── 加载项目基础信息 (CLAUDE.md)

2. 阶段1: 代码开发 (Subagent A) [如果 phases 包含 1]
   ├── max_retries: 3
   ├── 模型: sonnet
   └── 输出: 代码实现 + 自检报告

3. 阶段2: 代码审查 (Subagent B) [如果 phases 包含 2]
   ├── max_retries: 3
   ├── 模型: opus
   ├── 输出: 审查意见 + 优化决策
   └── 决策: 需要优化? 轮次1-3?

4. 循环优化 (1-3轮，由B决定) [如果 phases 包含 3]
   └── 阶段3: 优化确认 (Subagent A)

5. 阶段4: API测试 (Subagent C) [如果 phases 包含 4]
   ├── max_retries: 3
   ├── 模型: sonnet
   ├── 执行: pytest测试
   ├── 输出: 测试结果 + Bug记录 + 测试报告
   └── 报告路径: /projects/management/tracker/docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md

6. 阶段5: UI测试 (Subagent D) [如果 phases 包含 5]
   ├── max_retries: 3
   ├── 模型: sonnet
   ├── 执行: Playwright测试
   ├── 输出: 测试结果 + Bug记录
   └── 追加到测试报告

7. 阶段6: 手工测试 (Subagent E) [如果 phases 包含 6]
   ├── max_retries: 2
   ├── 模型: sonnet
   ├── 执行: agent-browser验证
   ├── 输出: 问题记录
   └── 追加到测试报告

8. 阶段7: 测试验收 (Subagent F) [如果 phases 包含 7]
   ├── max_retries: 2
   ├── 模型: opus
   ├── 验收: C/D/E输出检查
   └── 判定: 合格/需迭代

9. 流程结束
   └── 主代理输出最终报告
```

## 阶段依赖关系

当指定阶段范围时，注意以下依赖：

| 阶段 | 依赖 | 说明 |
|------|------|------|
| 1 (开发) | 无 | 可独立执行 |
| 2 (审查) | 1 | 需要阶段1的输出 |
| 3 (优化) | 1, 2 | 需要阶段2的审查意见 |
| 4 (API测试) | 无* | 可独立执行，但需要代码已实现 |
| 5 (UI测试) | 无* | 可独立执行，但需要代码已实现 |
| 6 (手工测试) | 无* | 可独立执行，但需要代码已实现 |
| 7 (测试验收) | 4, 5, 6 | 需要测试阶段输出 |

*注: 测试阶段可以独立执行已有功能的测试，不依赖开发阶段

## 主代理职责

> **重要**: 主代理专注于流程控制，**不参与实际验收判断**

### 主代理任务
1. 按顺序启动各个Subagent
2. 传递必要信息给下一个Subagent
3. 接收测试验收Subagent (F)的判定
4. 根据F的判定决定是否需要迭代
5. 输出最终报告
6. **执行工作流评估（必做）**

### 主代理不做的
- ❌ 不直接判断测试是否通过
- ❌ 不直接分析测试失败原因
- ❌ 不修复代码或测试
- ❌ 不做验收决策

---

## 工作流评估（必做）

### 评估要求

每次工作流执行完成后，主代理必须执行工作流评估：

1. **收集子代理元数据**:
   - 记录每个Task工具返回的 `task_id`
   - 记录 `total_tokens` 和 `duration_ms`

2. **评估子代理完成度**:
   | 完成度 | 标准 |
   |--------|------|
   | 100% | 完全自主完成，无需干预 |
   | 80% | 有小问题，轻微协助 |
   | 60% | 有较大问题，需要修复 |
   | 40% | 完全失败，主代理重做 |

3. **生成评估报告**:
   ```bash
   # 复制评估模板
   cp /projects/management/tracker/logs/workflow_evaluation_TEMPLATE.md \
      /projects/management/tracker/logs/workflow_evaluation_YYYY-MM-DD.md

   # 填充数据（自动为主）
   ```

4. **输出评估摘要**:
   - 平均完成度
   - 主代理干预次数
   - 发现的问题
   - 改进建议

### 评估模板位置
```
/projects/management/tracker/logs/workflow_evaluation_TEMPLATE.md
```

### 评估输出示例
```
## 工作流评估摘要

### 资源消耗
- 总Token: ~XX,XXX
- 总执行时间: ~XX秒

### 质量评估
- 平均完成度: XX%
- 主代理干预: X次

### 问题记录
- P001: [问题描述]
- ...

### 改进建议
- [改进项]
```

---

# 使用示例

## 示例1: 完整开发流程

```
用户: 请按工作流开发 v0.9.2 的新功能
或: /tracker-code-development-workflow v0.9.2
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [1, 2, 3, 4, 5, 6, 7]

**执行**: 完整的7个阶段

---

## 示例2: 仅执行测试阶段

```
用户: /tracker-code-development-workflow v0.9.2 phase4-6
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [4, 5, 6]

**执行**:
- ✅ 跳过阶段1-3 (开发/审查/优化)
- ▶️ 执行阶段4 (API测试)
- ▶️ 执行阶段5 (UI测试)
- ▶️ 执行阶段6 (手工测试)
- ✅ 跳过阶段7 (测试验收)

**适用场景**: 代码已开发完成，只需补充测试

---

## 示例3: 仅执行API测试

```
用户: /tracker-code-development-workflow v0.9.2 phase4
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [4]

**执行**: 仅阶段4 (API测试)

**适用场景**: 只需要开发或调试API测试

---

## 示例4: 开发+审查阶段

```
用户: /tracker-code-development-workflow v0.9.2 phase1-3
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [1, 2, 3]

**执行**: 阶段1-3 (开发 → 审查 → 优化)

**适用场景**: 只开发代码，暂不测试

---

## 示例5: 仅测试验收

```
用户: /tracker-code-development-workflow v0.9.2 phase7
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [7]

**执行**: 仅阶段7 (测试验收)

**适用场景**: 验收已有测试结果

---

## 示例6: 未指定版本

```
用户: /tracker-code-development-workflow phase4-6
```

**系统响应**: `请指定版本号，例如 v0.9.2`

---

# 测试报告规范

## 强制要求

### 1. 命名格式
```
/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md
```

示例：
- `TEST_REPORT_v0.9.1_20260308.md`

### 2. 文档结构
必须包含以下章节：
1. **测试概览** - 环境、关联文档、结果汇总
2. **API测试结果** - Subagent C输出
3. **UI测试结果** - Subagent D输出
4. **手工测试结果** - Subagent E输出
5. **Bug修复记录** - 所有发现的问题
6. **验收标准** - 各项检查状态

### 3. 追加模式
- C/D/E分别追加内容到同一报告
- 使用 `---` 分隔各阶段内容

---

# 经验教训总结

## 常见问题及解决方案

### 1. 测试阶段职责不清
**问题**: Subagent C和D职责重叠，导致重复工作或遗漏
**解决**: 明确分离C(D/E)职责，各司其职

### 2. 测试报告未生成
**问题**: 子代理忘记生成报告或路径不明确
**解决**: 强制规定报告路径和格式，每个测试阶段必须追加到报告

### 3. 主代理做验收判断
**问题**: 主代理既控制流程又做判断，标准不统一
**解决**: 新增Subagent F专门做验收，主代理只负责流程控制

### 4. Bug记录不完整
**问题**: 发现的Bug未记录到BugLog
**解决**: 每个测试阶段都必须记录Bug，作为验收检查项

### 5. agent-browser使用不规范
**问题**: 忘记加--args "--no-sandbox"导致测试失败
**解决**: 在技能文档中强制标注，配置alias

---

# Tracker 项目特殊规则

## 分支管理规则

> 详细规范见: `/projects/management/tracker/docs/DEVELOPMENT/coding_standard.md` 第10章

| 规则 | 说明 |
|------|------|
| 🔴 **禁止 main 直接开发** | 绝对不允许在 main 分支上直接修改/提交代码 |
| 🔴 **禁止 develop 直接开发** | 不允许在 develop 分支上直接开发功能 |
| ✅ **必须创建功能分支** | 所有开发必须从 develop 创建 feature/* 或 bugfix/* 分支 |

## 测试通过标准

| 测试类型 | 通过标准 |
|----------|----------|
| 前端检查 | 100% 通过 (check_frontent.sh) |
| API 测试 | 100% 通过 (pytest) |
| UI 冒烟测试 | 100% 通过 (Playwright) |
| 手工测试 | 控制台无关键错误 |

## 安全规则

- 禁止修改 user_data 目录
- 禁止在生产端口 (8080) 调试
- 使用测试数据目录 (test_data) 进行开发测试

## 版本管理

- 开发版本号格式: v0.x.x
- 每次合并到 develop 前更新 VERSION 文件

---

# 渐进式加载资源

## 参考文档

各阶段的详细Prompt模板保存在 `references/` 目录：

| 文件 | 阶段 | 说明 |
|------|------|------|
| `references/stage1_development.md` | 阶段1 | 代码开发快速参考 |
| `references/stage2_review.md` | 阶段2 | 代码审查快速参考 |
| `references/stage3_optimize.md` | 阶段3 | 优化确认快速参考 |
| `references/stage4_api_test.md` | 阶段4 | API测试快速参考 |
| `references/stage5_ui_test.md` | 阶段5 | UI测试快速参考 |
| `references/stage6_manual_test.md` | 阶段6 | 手工测试快速参考 |
| `references/stage7_acceptance.md` | 阶段7 | 测试验收快速参考 |

## 工具脚本

`scripts/` 目录包含验证工具：

| 脚本 | 功能 |
|------|------|
| `scripts/verify_deliverables.py` | 验证交付物完整性 |
| `scripts/run_tests.py` | 统一测试执行入口 |

### 使用示例

```bash
# 验证交付物
python scripts/verify_deliverables.py --version 0.9.1

# 运行所有测试
python scripts/run_tests.py --all

# 只运行API测试
python scripts/run_tests.py --api
```

## 测试用例

`evals/` 目录包含技能评估测试用例：

| 文件 | 说明 |
|------|------|
| `evals/evals.json` | 4个测试用例定义 |
