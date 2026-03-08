---
name: tracker_coverage_enhancement_workflow
description: This skill should be used when the user wants to enhance test coverage based on test_coverage_enhancement_plan, including reviewing the plan to identify missing API tests, UI tests, and manual tests, then developing those tests using the tracker development workflow pattern. Use this skill when user mentions test coverage enhancement, test coverage plan, or wants to improve test coverage for Tracker.
---

# Tracker 测试覆盖增强工作流

## 概述

Tracker 项目专用测试覆盖增强工作流，通过5个阶段子代理完成测试覆盖提升：

| 阶段 | 子代理 | 职责 |
|------|--------|------|
| 1 | **Subagent COV_A (分析)** | 审查 test_coverage_enhancement_plan，提取需要补充的测试用例列表 |
| 2 | **Subagent COV_B (API测试)** | 针对分析阶段识别的 API 测试缺口进行开发 |
| 3 | **Subagent COV_C (UI测试)** | 针对分析阶段识别的 UI 测试缺口进行开发 |
| 4 | **Subagent COV_D (手工测试)** | 针对分析阶段识别的手工测试缺口进行开发 |
| 5 | **Subagent COV_E (验收)** | 基于分析阶段输出的测试计划，验收各阶段产出 |

> **支持多轮迭代优化**: 如果 Subagent COV_E 验收不通过，将进入优化循环（1-3轮）

---

## 参数解析

用户可通过以下方式调用：
- `/tracker-coverage-enhancement-workflow v0.9.2` → 指定版本号
- `/tracker-coverage-enhancement-workflow v0.9.2 phase2-4` → 版本号 + 阶段范围
- `/tracker-coverage-enhancement-workflow phase3` → 仅指定阶段

### 参数提取规则

从用户消息中提取以下参数：

#### 1. 版本号 (`version`)

**模式**: `v\d+\.\d+\.\d+` 或 `\d+\.\d+\.\d+`

**示例**: `v0.9.2`, `0.9.1`

**用途**:
- 测试覆盖增强计划: `docs/PLANS/test_coverage_enhancement_plan_v{version}.md`
- 规格书路径: `docs/SPECIFICATIONS/tracker_SPECS_{version}.md`
- 测试报告: `docs/REPORTS/TEST_REPORT_{version}_{date}.md`

**默认值**: 如果未指定，必须询问用户

#### 2. 阶段范围 (`phases`)

**模式**: `phase(\d+)(?:-(\d+))?`

**示例**:
- `phase2` → 仅执行阶段2
- `phase2-4` → 执行阶段2、3、4
- `phase1-3` → 执行阶段1、2、3

**默认值**: 如果未指定，执行全部阶段 (1-5)

### 参数应用示例

```markdown
# 用户输入: "/tracker-coverage-enhancement-workflow v0.9.2 phase2-4"

## 解析结果
- 版本: v0.9.2
- 阶段: [2, 3, 4]

## 执行计划
1. ✅ 跳过阶段1 (测试覆盖分析)
2. ▶️ 执行阶段2 (API测试开发)
3. ▶️ 执行阶段3 (UI测试开发)
4. ▶️ 执行阶段4 (手工测试开发)
5. ✅ 跳过阶段5 (测试验收) - 或根据参数包含

## 适用场景
- 已完成测试覆盖分析，直接执行测试开发
- 需要重新运行特定类型的测试
```

### 执行逻辑

1. 解析用户消息提取 `version` 和 `phases` 参数
2. 如果版本号未指定，询问用户：`请指定版本号，例如 v0.9.2`
3. 验证版本相关文件是否存在（测试覆盖增强计划、规格书）
4. 根据 `phases` 参数决定执行哪些阶段
5. 按顺序执行指定阶段，跳过未包含的阶段

### 阶段依赖关系

| 阶段 | 依赖 | 说明 |
|------|------|------|
| 1 (分析) | 无 | 可独立执行 |
| 2 (API测试) | 1* | 需要阶段1的测试需求清单 |
| 3 (UI测试) | 1* | 需要阶段1的测试需求清单 |
| 4 (手工测试) | 1* | 需要阶段1的测试需求清单 |
| 5 (测试验收) | 2, 3, 4 | 需要测试阶段输出 |

*注: 测试阶段可以独立执行，但需要手动提供测试需求清单

## 阶段配置总览

| 阶段 | 子代理 | 模型 | max_turns | 推理深度 | 核心改进 |
|------|--------|------|-----------|---------|----------|
| 分析 | Subagent COV_A | sonnet | 2 | 高 | 无 |
| API测试 | Subagent COV_B | sonnet | **5** | 中高 | **强制环境验证** |
| UI测试 | Subagent COV_C | sonnet | **5** | 高 | **强制代码参考** |
| 手工测试 | Subagent COV_D | sonnet | 2 | 中 | 无 |
| 验收 | Subagent COV_E | opus | 2 | 高 | **强制实际运行测试** |

---

# 阶段1：测试覆盖分析 (Subagent COV_A)

## 职责定义

**测试分析工程师** - 审查测试覆盖增强计划，明确需要补充的测试用例列表和详细开发计划。

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker测试覆盖分析"
```

## 必须阅读的文档

1. `/projects/management/tracker/CLAUDE.md` - 项目基础信息
2. `/projects/management/tracker/docs/PLANS/test_coverage_enhancement_plan_v{version}.md` - **测试覆盖增强计划（必须阅读）**
3. `/projects/management/tracker/docs/SPECIFICATIONS/tracker_SPECS_v{version}.md` - 关联规格书
4. `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md` - 最新测试报告

## Prompt模板

```
# 阶段1：测试覆盖分析 (Subagent COV_A)

## 角色
你是测试分析工程师，负责审查测试覆盖增强计划，提取需要补充的测试用例。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口，test_data 目录

## 核心任务

### 1. 审查测试覆盖增强计划（必做）
- 读取 `/projects/management/tracker/docs/PLANS/test_coverage_enhancement_plan_v{version}.md`
- 分析每个 COV-XXX 问题
- 识别需要补充的测试类型（API/UI/手工）

### 2. 提取测试用例清单（必做）
对每个识别的测试需求，提取：
- **测试ID**: 如 COV-001-API, COV-001-UI
- **测试类型**: API / UI / 手工
- **测试目标**: 要验证的功能点
- **建议测试用例代码**: 从计划中提取或自行设计
- **测试文件路径**: 建议创建/修改的文件

### 3. 分类输出（必做）
按测试类型分组输出：

#### API 测试需求
| 测试ID | 问题ID | 测试目标 | 建议测试文件 | 建议测试用例 |
|--------|--------|----------|--------------|--------------|
| API-COV-001 | COV-002 | 反馈文件生成验证 | test_api_feedback.py | test_feedback_file_created |

#### UI 测试需求
| 测试ID | 问题ID | 测试目标 | 建议测试文件 | 建议测试用例 |
|--------|--------|----------|--------------|--------------|
| UI-COV-001 | COV-001 | CP覆盖率左右布局验证 | 13-layout.spec.ts | it('CP覆盖率信息应为左右布局') |

#### 手工测试需求
| 测试ID | 问题ID | 测试目标 | 检查方式 |
|--------|--------|----------|----------|
| MANUAL-COV-003 | COV-003 | switchTab非事件调用 | 代码审查+手工验证 |

### 4. 生成详细测试开发计划（必做）
为每个测试用例输出：
```markdown
#### {测试ID}: {测试目标}

**问题来源**: {COV-XXX}
**测试类型**: {API/UI/手工}
**测试文件**: {路径}
**预估工作量**: {0.5h/1h}

**测试步骤**:
1. 步骤1
2. 步骤2
...

**预期结果**:
- 结果1
- 结果2
...

**建议代码**:
```typescript
// 或 python
代码示例
```
```

## 输出格式

```
## 测试覆盖分析报告

### 1. 分析摘要

| 测试类型 | 数量 | 优先级 |
|----------|------|--------|
| API 测试 | {N} | 高/中/低 |
| UI 测试 | {N} | 高/中/低 |
| 手工测试 | {N} | 高/中/低 |

### 2. API 测试需求清单
| 测试ID | 问题ID | 测试目标 | 测试文件 | 优先级 |
|--------|--------|----------|----------|--------|
| API-COV-001 | COV-002 | 反馈文件生成验证 | test_api_feedback.py | 低 |

### 3. UI 测试需求清单
| 测试ID | 问题ID | 测试目标 | 测试文件 | 优先级 |
|--------|--------|----------|----------|--------|
| UI-COV-001 | COV-001 | CP覆盖率左右布局验证 | 13-layout.spec.ts | 中 |

### 4. 手工测试需求清单
| 测试ID | 问题ID | 测试目标 | 检查方式 | 优先级 |
|--------|--------|----------|----------|--------|
| MANUAL-COV-003 | COV-003 | switchTab非事件调用 | 代码审查 | 低 |

### 5. 详细开发计划
[每个测试用例的详细开发计划]

### 6. 验收标准
每个阶段必须产出：
- API测试: 新增测试用例 + 测试通过 + Bug记录
- UI测试: 新增测试用例 + 测试通过 + Bug记录
- 手工测试: 问题验证记录 + Bug记录
```

---

# 阶段2：API测试开发 (Subagent COV_B)

## 职责定义

**API测试工程师** - 根据阶段1的分析结果，开发和执行API测试用例。

> 本阶段配置与 tracker_code_development_workflow 的 Subagent C 一致
> **重要**: 增加环境验证环节，必须先确认测试环境配置

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker API测试开发"
- max_turns: 5  # 增加重试次数，允许自修复
```

## 必须阅读的文档

1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. **阶段1输出的测试覆盖分析报告**
3. `/projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{version}.md` - 测试计划

## Prompt模板

```
# 阶段2：API测试开发 (Subagent COV_B)

## 角色
你是专业的API测试工程师，负责使用pytest开发、调试和修复API测试用例。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口
- **测试框架**: pytest

## 测试命令
```bash
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_{name}.py -v
```

## 阶段1输出的测试需求
[从阶段1报告中提取的API测试需求]

## ⚠️ 核心改进：强制环境验证（不可跳过）

### 0. 环境配置验证（必做）

**你必须先读取 Flask 配置代码，确认测试模式下的实际路径！**

1. **读取 Flask 配置**:
   阅读 `/projects/management/tracker/dev/app/__init__.py`
   - 找到 `create_app(testing=True)` 函数
   - 确认 `DATA_DIR` 在测试模式下的实际值

2. **验证路径存在**:
   列出确认后的目录内容
   ```bash
   ls -la {你确认的路径}/feedbacks/
   ```

3. **记录确认的配置**:
   ```
   确认结果:
   - 测试模式 DATA_DIR = {实际路径}
   - feedback 目录 = {实际路径}/feedbacks
   ```

**❌ 禁止**: 直接假设路径然后编写测试代码
**✅ 必须**: 先验证再编写

---

## 核心任务

### 1. 测试用例开发（必做）
- 根据确认后的环境配置编写测试代码
- 测试文件命名: `test_api_{功能名}.py`
- 测试用例ID格式: `API-COV-XXX`

### 2. 测试执行（必做）
- 运行所有API测试
- 分析失败原因

### 3. 问题处理（必做）
- **测试失败** → 自行修复测试代码，重新运行验证
- **应用代码问题** → 确认根因 + 记录到 Buglog（不修复）

### 4. 测试报告（必做）
输出到: `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md`

## 重要：测试通过标准

你必须确保所有测试通过后才能返回！
- 如果测试失败，继续修复直到通过
- max_turns: 5 允许你有多次尝试机会

## 输出格式
```
## API测试开发结果
- 测试用例数: {N}
- 通过: {N}
- 失败: {N}

## 环境验证记录
- 确认的 DATA_DIR: {路径}

## 新增测试用例
| 用例ID | 说明 | 结果 |
|--------|------|------|
| API-COV-001 | ... | ✅ |

## Bug记录
- {bug描述}
```
```

---

# 阶段3：UI测试开发 (Subagent COV_C)

## 职责定义

**Playwright UI测试工程师** - 根据阶段1的分析结果，开发和执行UI测试用例。

> 本阶段配置与 tracker_code_development_workflow 的 Subagent D 一致
> **重要**: 增加现有代码参考环节，必须先确认正确的选择器

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker Playwright UI测试开发"
- max_turns: 5  # 增加重试次数，允许自修复
```

## 必须阅读的文档

1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. **阶段1输出的测试覆盖分析报告**
3. **必须阅读**: `/projects/management/tracker/dev/tests/test_ui/specs/smoke/01-smoke.spec.ts` - 确认选择器

## Prompt模板

```
# 阶段3：Playwright UI测试开发 (Subagent COV_C)

## 角色
你是专业的Playwright UI测试工程师，负责使用Playwright开发、调试和修复UI测试用例。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口
- **测试框架**: Playwright

## 测试命令
```bash
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/ --project=firefox
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/13-layout.spec.ts --project=firefox
```

## 阶段1输出的测试需求
[从阶段1报告中提取的UI测试需求]

## ⚠️ 核心改进：强制代码参考（不可跳过）

### 0. 选择器验证（必做）

**你必须先阅读现有测试代码，确认正确的选择器！**

1. **阅读现有UI测试**: 读取 `/projects/management/tracker/dev/tests/test_ui/specs/smoke/01-smoke.spec.ts`
   - 确认登录表单选择器: `#loginUsername` (不是 #username!)
   - 确认登录密码选择器: `#loginPassword`
   - 确认登录按钮选择器: `button.login-btn`
   - 确认登录后验证: 使用 `waitForFunction` 检查 `#projectSelector.options`

2. **确认Tab切换选择器**: 读取其他 integration 测试
   - 确认 Cover Points 按钮: `button.tab:has-text("Cover Points")`

3. **复制辅助函数**: 直接复制 `loginAsAdmin` 函数
   - 不要自己重新实现登录逻辑！

**❌ 禁止**: 凭记忆写选择器
**✅ 必须**: 先读取确认后再编写

---

## 核心任务

### 1. 测试用例开发（必做）
- 使用确认后的正确选择器编写测试代码
- 测试文件命名: `{序号}-{功能名}.spec.ts`
- 测试用例ID格式: `UI-COV-XXX`

### 2. 测试执行（必做）
- 运行新增的UI测试
- 分析失败原因

### 3. 问题处理（必做）
- **测试失败** → 自行修复测试代码，重新运行验证
- **应用代码问题** → 确认根因 + 记录到 Buglog（不修复）

### 4. 测试报告（必做）
追加到: `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md`

## 重要：测试通过标准

你必须确保所有测试通过后才能返回！
- 如果测试失败，继续修复直到通过
- max_turns: 5 允许你有多次尝试机会

## 输出格式
```
## UI测试开发结果
- 测试用例数: {N}
- 通过: {N}
- 失败: {N}

## 选择器验证记录
- 确认的登录输入框: #loginUsername
- 确认的登录按钮: button.login-btn

## 新增测试用例
| 用例ID | 说明 | 结果 |
|--------|------|------|
| UI-COV-001 | ... | ✅ |

## Bug记录
- {bug描述}
```
```

---

# 阶段4：手工测试开发 (Subagent COV_D)

## 职责定义

**手工测试工程师** - 根据阶段1的分析结果，执行手工测试和验证。

> **技能依赖**: 必须激活 `agent-browser-usage` 技能获取完整使用指南
>
> 本阶段配置与 tracker_code_development_workflow 的 Subagent E 一致

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
2. 阶段1输出的测试覆盖分析报告

## Prompt模板

```
# 阶段4：手工测试执行 (Subagent COV_D)

## 角色
你是手工测试工程师，负责使用agent-browser进行UI验证和调试。

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口
- **工具**: agent-browser

## 阶段1输出的测试需求
[从阶段1报告中提取的手工测试需求]

## 核心任务

### 1. 手工验证执行（必做）
- 验证Playwright难以测试的UI功能
- 检查控制台错误
- 验证CSS样式渲染
- 执行代码审查（针对边缘场景）

### 2. 问题定位（必做）
- 复现问题并记录步骤
- 分析控制台错误
- **应用代码问题** → 确认根因 + 记录到 Buglog（不修复）

### 3. 测试报告（必做）
追加到: `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md`

## 输出格式
```
## 手工测试执行结果
- 测试项: {N}
- 通过: {N}
- 发现问题: {N}

## 问题列表
| 问题 | 状态 |
|------|------|
| 控制台JS错误 | 已修复/待修复 |

## Bug记录
- {bug描述}
```
```

---

# 阶段5：测试验收 (Subagent COV_E)

## 职责定义

**测试验收工程师** - 验收Subagent COV_B/Subagent COV_C/Subagent COV_D的输出是否符合阶段1的分析计划要求。

> 本阶段配置与 tracker_code_development_workflow 的 Subagent F 一致
> **重要**: 必须实际运行测试验证，不能仅检查文件存在！

## 调用方式

```markdown
使用 Task 工具启动子代理：
- subagent_type: "general-purpose"
- model: "opus"
- description: "Tracker测试验收"
```

## 必须执行的验收检查

### ⚠️ 核心改进：必须实际运行测试

**你不能仅通过检查文件存在来判定测试通过！**

#### API测试验证步骤:
1. **实际运行 pytest**:
   ```bash
   cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_feedback.py -v --tb=short
   ```
2. **检查输出**:
   - 确认所有用例显示 `PASSED`
   - 如果有 `FAILED`，记录具体错误

#### UI测试验证步骤:
1. **实际运行 Playwright**:
   ```bash
   cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/13-layout.spec.ts --project=firefox
   ```
2. **检查输出**:
   - 确认所有用例显示 `passed`
   - 如果有 `failed`，记录具体错误

### 1. 验收检查清单

| 检查项 | 验收标准 |
|--------|----------|
| API测试完成度 | 阶段1识别的所有API测试用例已开发 |
| **API测试通过率** | **100% (通过实际运行验证)** |
| UI测试完成度 | 阶段1识别的所有UI测试用例已开发 |
| **UI测试通过率** | **100% (通过实际运行验证)** |
| 手工测试完成度 | 阶段1识别的所有手工测试项已执行 |
| Bug记录完整性 | 发现的问题已记录到 Buglog |
| 测试报告完整性 | 各阶段产出已追加到测试报告 |

### 2. 验收决策

**合格标准**:
- 所有验收检查项通过
- **所有测试实际运行通过**
- 或者失败项有明确说明（非阻塞性问题）

**需迭代标准**:
- 缺少必需的测试用例
- **测试用例未通过（实际运行失败）**
- Bug记录不完整

## Prompt模板

```
# 阶段5：测试验收 (Subagent COV_E)

## 角色
你是测试验收工程师，负责验证测试覆盖增强工作的产出是否符合要求。

**⚠️ 重要**: 你必须实际运行测试来验证，不能仅靠检查文件存在！

## 项目基础信息
- **项目类型**: Flask + SQLite Web 应用
- **测试环境**: 8081 端口

## 阶段1输出的测试需求
[阶段1的分析报告]

## ⚠️ 强制步骤：实际运行测试

### API测试验证（必做）
```bash
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_feedback.py -v --tb=short
```
- 记录实际运行结果
- 如果失败，标记为"需迭代"

### UI测试验证（必做）
```bash
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/13-layout.spec.ts --project=firefox
```
- 记录实际运行结果
- 如果失败，标记为"需迭代"

## 验收检查

### API测试验收 (B输出)
- [x] 已实际运行 pytest 验证
- [ ] API测试用例已开发
- [ ] 测试通过（基于实际运行结果）

### UI测试验收 (C输出)
- [x] 已实际运行 Playwright 验证
- [ ] UI测试用例已开发
- [ ] 测试通过（基于实际运行结果）

### 手工测试验收 (D输出)
- [ ] MANUAL-COV-003 已执行
- [ ] 问题已记录

## 输出格式

```
## 验收结果

### API测试验收 (B)
| 检查项 | 状态 | 说明 |
|--------|------|------|
| pytest 已运行 | ✅ | 输出: X passed |
| API-COV-002 已开发 | ✅/❌ | ... |
| 测试通过 | ✅/❌ | ... |

### UI测试验收 (C)
| 检查项 | 状态 | 说明 |
|--------|------|------|
| Playwright 已运行 | ✅ | 输出: X passed |
| UI-COV-001 已开发 | ✅/❌ | ... |
| 测试通过 | ✅/❌ | ... |

### 手工测试验收 (D)
| 检查项 | 状态 | 说明 |
|--------|------|------|
| MANUAL-COV-003 已执行 | ✅/❌ | ... |

## 总体判定

**判定**: 合格 / 需迭代

### 迭代建议（如果需迭代）
- 轮次: {N}
- 需要重做: {COV_名称}
- 具体问题: {从实际运行输出中记录的错误}

### 通过项
- [ ] {通过项}
```
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
        phases = [1, 2, 3, 4, 5]  # 默认全部阶段

    return version, phases
```

## 完整流程

```
0. ⚠️ 参数解析与前置检查
   ├── 解析版本号和阶段范围参数
   ├── 如果版本号未指定 → 询问用户
   ├── 确保测试服务器运行在 8081 端口
   └── 确保测试覆盖增强计划文件存在

1. 阶段1: 测试覆盖分析 (Subagent COV_A) [如果 phases 包含 1]
   ├── max_turns: 2
   ├── 模型: sonnet
   └── 输出: 测试覆盖分析报告

2. 阶段2: API测试开发 (Subagent COV_B) [如果 phases 包含 2]
   ├── max_turns: 5 (允许自修复)
   ├── 模型: sonnet
   ├── ⚠️ 强制: 先读取 app/__init__.py 确认 DATA_DIR
   ├── 执行: pytest测试
   └── 输出: API测试结果 + Bug记录

3. 阶段3: UI测试开发 (Subagent COV_C) [如果 phases 包含 3]
   ├── max_turns: 5 (允许自修复)
   ├── 模型: sonnet
   ├── ⚠️ 强制: 先读取 smoke 测试确认选择器
   ├── 执行: Playwright测试
   └── 输出: UI测试结果 + Bug记录

4. 阶段4: 手工测试 (Subagent COV_D) [如果 phases 包含 4]
   ├── max_turns: 2
   ├── 模型: sonnet
   ├── 执行: agent-browser验证
   └── 输出: 手工测试结果

5. 阶段5: 测试验收 (Subagent COV_E) [如果 phases 包含 5]
   ├── max_turns: 2
   ├── 模型: opus
   ├── ⚠️ 强制: 实际运行 pytest/playwright 验证
   ├── 验收: B/C/D输出检查
   └── 判定: 合格/需迭代

6. 迭代循环（如需）
   └── 根据E的判定，最多进行3轮优化
```

## 主代理职责

> 主代理专注于流程控制，**不参与实际验收判断**

### 主代理任务
1. 按顺序启动各个COV_子代理
2. 传递阶段1的测试需求给后续COV_子代理
3. 接收测试验收Subagent COV_E的判定
4. 根据E的判定决定是否需要迭代
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

# 测试报告规范

## 强制要求

### 1. 命名格式
```
/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md
```

### 2. 文档结构
必须包含以下章节：
1. **测试概览** - 环境、关联文档
2. **测试覆盖增强分析** - 阶段1输出
3. **API测试结果** - Subagent COV_B输出
4. **UI测试结果** - Subagent COV_C输出
5. **手工测试结果** - Subagent COV_D输出
6. **Bug修复记录** - 所有发现的问题
7. **验收标准** - 阶段5验收结果

### 3. 追加模式
- B/C/D分别追加内容到同一报告
- 使用 `---` 分隔各阶段内容

---

# Tracker 项目特殊规则

## 测试通过标准

| 测试类型 | 通过标准 |
|----------|----------|
| API 测试 | 100% 通过 (pytest) |
| UI 测试 | 100% 通过 (Playwright) |
| 手工测试 | 控制台无关键错误 |

## 安全规则

- 禁止修改 user_data 目录
- 禁止在生产端口 (8080) 调试
- 使用测试数据目录 (test_data) 进行开发测试

---

# 使用示例

## 示例1: 完整测试覆盖增强流程

```
用户: 请按工作流增强 v0.9.2 的测试覆盖
或: /tracker-coverage-enhancement-workflow v0.9.2
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [1, 2, 3, 4, 5]

**执行**: 完整的5个阶段

---

## 示例2: 仅执行测试开发阶段

```
用户: /tracker-coverage-enhancement-workflow v0.9.2 phase2-4
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [2, 3, 4]

**执行**:
- ✅ 跳过阶段1 (测试覆盖分析)
- ▶️ 执行阶段2 (API测试开发)
- ▶️ 执行阶段3 (UI测试开发)
- ▶️ 执行阶段4 (手工测试开发)
- ✅ 跳过阶段5 (测试验收)

**适用场景**: 已完成测试覆盖分析，直接执行测试开发

---

## 示例3: 仅执行API测试开发

```
用户: /tracker-coverage-enhancement-workflow v0.9.2 phase2
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [2]

**执行**: 仅阶段2 (API测试开发)

**适用场景**: 只需要开发或调试API测试

---

## 示例4: 仅执行测试覆盖分析

```
用户: /tracker-coverage-enhancement-workflow v0.9.2 phase1
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [1]

**执行**: 仅阶段1 (测试覆盖分析)

**适用场景**: 只需要分析测试覆盖缺口，暂不开发

---

## 示例5: 仅执行测试验收

```
用户: /tracker-coverage-enhancement-workflow v0.9.2 phase5
```

**解析结果**:
- 版本: v0.9.2
- 阶段: [5]

**执行**: 仅阶段5 (测试验收)

**适用场景**: 验收已有测试结果

---

## 示例6: 未指定版本

```
用户: /tracker-coverage-enhancement-workflow phase2-4
```

**系统响应**: `请指定版本号，例如 v0.9.2`

---

# 渐进式加载资源

## 参考文档

各阶段的详细Prompt模板保存在 `references/` 目录：

| 文件 | 阶段 | 说明 |
|------|------|------|
| `references/stage1_analysis.md` | 阶段1 | 测试覆盖分析快速参考 |
| `references/stage2_api_test.md` | 阶段2 | API测试快速参考 |
| `references/stage3_ui_test.md` | 阶段3 | UI测试快速参考 |
| `references/stage4_manual_test.md` | 阶段4 | 手工测试快速参考 |
| `references/stage5_acceptance.md` | 阶段5 | 测试验收快速参考 |
