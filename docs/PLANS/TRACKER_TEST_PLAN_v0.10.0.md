# Tracker v0.10.0 测试计划

> **测试版本**: v0.10.0
> **对应规格书**: `tracker_SPECS_v0.10.0.md`
> **创建日期**: 2026-03-18
> **状态**: 待开发
> **预估开发时间**: 4 小时

---

## 1. 版本概述

### 1.1 版本目标

v0.10.0 版本主要实现以下功能：
1. 优化关联选择列表交互体验（搜索过滤 + 已关联CP显示）
2. 图表支持按CP Priority过滤
3. 前端代码JSDoc注释补充
4. 后端API错误处理日志

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.10.0.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-1 | 优化关联选择列表交互体验 | P1 | 4h |
| REQ-2 | 图表支持按CP Priority过滤 | P1 | 8h |
| REQ-2.1 | - 计划曲线 Priority 过滤 | P1 | 3h |
| REQ-2.2 | - 实际曲线 Priority 过滤 | P1 | 5h |
| REQ-3 | 前端代码JSDoc注释补充 | P2 | 6h |
| REQ-4 | 后端API错误处理日志 | P2 | 4h |

---

## 2. 存放位置

> **重要**：测试计划文件应放在 `docs/PLANS/` 目录下，不要放在 `docs/REPORTS/` 目录下。

| 文档类型 | 目录 |
|----------|------|
| 测试计划 (Test Plan) | `docs/PLANS/` ← 放在这里 |
| 测试报告 (Test Report) | `docs/REPORTS/` |

---

## 2. API 测试计划

### 2.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── conftest.py                    # 共享 fixture
├── test_api.py                   # 基础 CRUD 测试
├── test_api_boundary.py          # 边界条件测试
├── test_api_exception.py          # 异常场景测试
├── test_api_batch.py             # 批量操作测试
├── test_api_performance.py       # 性能测试
└── test_api_progress.py          # 本版本新增：进度API测试
```

### 2.2 新增 API 测试用例

#### 2.2.1 基础功能测试 (REQ-2 计划曲线)

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROG-001 | test_get_progress_without_priority | 获取进度（无过滤参数） | 返回所有CP的进度 | REQ-2.1 |
| API-PROG-002 | test_get_progress_with_single_priority | 获取进度（单Priority过滤） | 只返回指定Priority的CP进度 | REQ-2.1 |
| API-PROG-003 | test_get_progress_with_multiple_priority | 获取进度（多Priority过滤） | 返回多个Priority的CP进度 | REQ-2.1 |
| API-PROG-004 | test_get_progress_priority_case_insensitive | 获取进度（大小写不敏感） | P0/p0 都应支持 | REQ-2.1 |

#### 2.2.2 边界条件测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROG-005 | test_get_progress_empty_priority | 空Priority参数 | 返回所有CP | REQ-2 |
| API-PROG-006 | test_get_progress_invalid_priority | 无效Priority值 | 忽略无效值，返回空或全部 | REQ-2 |
| API-PROG-007 | test_get_progress_nonexistent_project | 项目不存在 | 返回错误 | REQ-2 |

#### 2.2.3 异常场景测试

| 测试 ID | 测试方法 | 测试目标 | 异常场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROG-008 | test_get_progress_invalid_project_id | 无效项目ID | 返回404错误 | REQ-2 |

#### 2.2.4 CP 数量验证测试 (v0.10.0 补充)

| 测试 ID | 测试方法 | 测试目标 | 验证方式 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROG-009 | test_priority_filter_cp_count_verification | Priority 过滤后 CP 数量验证 | 创建 3 个 CP (P0/P1/P2)，验证不同过滤条件返回不同 coverage 值，间接验证过滤生效 | REQ-2.1 |

#### 2.2.5 实际曲线 Priority 过滤测试 (v0.10.0 新增)

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROG-010 | test_actual_curve_with_single_priority | 实际曲线（单Priority过滤） | priority=P0 时 actual 返回 p0_coverage | REQ-2.2 |
| API-PROG-011 | test_actual_curve_with_multiple_priority | 实际曲线（多Priority过滤） | priority=P0,P1 时返回合并后的覆盖率 | REQ-2.2 |
| API-PROG-012 | test_actual_curve_no_priority_filter | 实际曲线（无过滤） | 无 priority 参数时返回总体 actual_coverage | REQ-2.2 |
| API-PROG-013 | test_actual_curve_priority_coverage_stored | 实际曲线覆盖率存储验证 | 快照保存后 p0_coverage~p3_coverage 字段正确存储 | REQ-2.2 |
| API-PROG-014 | test_actual_curve_priority_coverage_calculated | 实际曲线覆盖率计算验证 | 各 Priority 覆盖率 = 已覆盖CP数 / 总CP数 × 100 | REQ-2.2 |

### 2.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| client fixture | `conftest.py` | Flask test_client |
| test_project fixture | `conftest.py` | 测试项目创建/清理 |
| cleanup_tcs fixture | `conftest.py` | TC 数据自动清理 |
| cleanup_cps fixture | `conftest.py` | CP 数据自动清理 |
| TCFactory | `factories.py` | TC 测试数据生成 |
| CPFactory | `factories.py` | CP 测试数据生成 |

### 2.4 API 测试命令

```bash
# 运行本版本新增的 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_progress.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 3. UI 集成测试计划

### 3.1 测试框架

基于 [UI 测试策略](./DEVELOPMENT/UI_TESTING_STRATEGY.md)，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/
├── conftest.ts                     # Playwright 配置
├── utils/
│   ├── dialog-helper.ts            # Dialog 处理工具
│   └── cleanup.ts                  # 测试数据清理工具
├── specs/
│   ├── smoke/                      # 冒烟测试
│   ├── integration/                 # 集成测试
│   │   └── cp_link_filter.spec.ts  # 本版本新增：CP关联过滤测试
│   └── e2e/                        # 端到端测试
```

### 3.2 新增 UI 测试用例

#### 3.2.1 REQ-1 功能测试（关联选择交互）

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-LINK-001 | 搜索框显示测试 | 验证搜索输入框在关联选择区域上方 | REQ-1 | P1 |
| UI-LINK-002 | 搜索过滤功能测试 | 输入关键词后列表在200ms内过滤 | REQ-1 | P1 |
| UI-LINK-003 | 空状态提示测试 | 搜索无结果时显示提示信息 | REQ-1 | P1 |
| UI-LINK-004 | 已关联CP显示测试 | 验证已关联CP显示区域在选择区域下方 | REQ-1 | P1 |
| UI-LINK-005 | CP名称显示测试 | 验证显示CP名称而非编号 | REQ-1 | P1 |
| UI-LINK-006 | 实时更新测试 | 取消关联后显示区域实时更新 | REQ-1 | P1 |
| UI-LINK-007 | Ctrl+K快捷键测试 | 验证Ctrl+K聚焦搜索框 | REQ-1 | P2 |

#### 3.2.2 REQ-2 功能测试（图表Priority过滤 - 计划曲线）

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PRIO-001 | Priority下拉框测试 | 验证多选下拉框显示 | REQ-2.1 | P1 |
| UI-PRIO-002 | Priority过滤测试 | 选择Priority后图表数据过滤 | REQ-2.1 | P1 |
| UI-PRIO-003 | 图表标题显示测试 | 验证图表标题显示过滤条件 | REQ-2.1 | P1 |
| UI-PRIO-004 | 重置过滤按钮测试 | 验证重置按钮恢复正常 | REQ-2.1 | P1 |
| UI-PRIO-005 | 多选合并测试 | 选择多个Priority时数据正确合并 | REQ-2.1 | P1 |
| UI-PRIO-006 | 图表数据过滤验证 | 验证过滤后的图表数据点数量确实减少 | REQ-2.1 | P1 |

#### 3.2.3 REQ-2 功能测试（图表Priority过滤 - 实际曲线）

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PRIO-007 | 实际曲线单Priority过滤 | 选择P0时实际曲线显示P0覆盖率 | REQ-2.2 | P1 |
| UI-PRIO-008 | 实际曲线多Priority过滤 | 选择P0,P1时实际曲线显示合并覆盖率 | REQ-2.2 | P1 |
| UI-PRIO-009 | 实际曲线无过滤 | 无过滤时显示总体覆盖率 | REQ-2.2 | P1 |
| UI-PRIO-010 | 计划曲线vs实际曲线对比 | 两种曲线使用不同的数据源但统一的过滤 | REQ-2.2 | P1 |

#### 3.2.4 回归测试

#### 3.2.3 回归测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-REG-001 | TC CRUD回归测试 | 验证现有TC增删改查功能正常 | 全局 | P1 |
| UI-REG-002 | CP CRUD回归测试 | 验证现有CP增删改查功能正常 | 全局 | P1 |
| UI-REG-003 | 图表渲染回归测试 | 验证现有图表功能正常 | 全局 | P1 |

### 3.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| dialogHelper | `utils/dialog-helper.ts` | 安全处理对话框 |
| cleanupTestData | `utils/cleanup.ts` | 清理测试数据 |
| testProject | `conftest.ts` | 测试项目 fixture |

### 3.4 UI 测试命令

```bash
# 运行本版本新增的 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/cp_link_filter.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox

# 运行所有 UI 测试
npx playwright test tests/test_ui/ --project=firefox
```

---

## 4. 测试开发任务分解

### 4.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发进度API基础功能测试（计划曲线） | `test_api_progress.py` | 1h | 待开始 |
| 开发进度API边界条件测试 | `test_api_progress.py` | 0.5h | 待开始 |
| 开发进度API异常场景测试 | `test_api_progress.py` | 0.5h | 待开始 |
| 开发实际曲线Priority过滤测试 | `test_api_progress.py` | 1.5h | 待开始 |

### 4.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发关联选择交互测试 | `cp_link_filter.spec.ts` | 1h | 待开始 |
| 开发Priority过滤测试（计划曲线） | `cp_link_filter.spec.ts` | 1h | 待开始 |
| 开发Priority过滤测试（实际曲线） | `cp_link_filter.spec.ts` | 1.5h | 待开始 |
| 开发回归测试 | `cp_link_filter.spec.ts` | 0.5h | 待开始 |

---

## 5. 验收标准

### 5.1 API 测试验收

- [ ] API-PROG-001 ~ API-PROG-008 所有测试用例通过
- [ ] 遵循测试 ID 编号规范
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理
- [ ] 现有 API 测试不受影响（回归）

### 5.2 UI 测试验收

- [ ] UI-LINK-001 ~ UI-PRIO-005 所有测试用例通过
- [ ] UI-REG-001 ~ UI-REG-003 回归测试通过
- [ ] 使用 dialog-helper 处理对话框
- [ ] 使用 cleanup 工具清理测试数据
- [ ] 现有 UI 测试不受影响（回归）

---

## 6. 测试执行计划

### 6.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_progress.py -v

# 3. 运行 UI 测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/cp_link_filter.spec.ts --project=firefox

# 4. 运行所有测试（验证回归）
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/ --project=firefox
```

### 6.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速，稳定，验证后端逻辑 |
| 2 | UI 集成测试 | 验证前端功能 |

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 测试数据冲突 | 测试失败 | 使用时间戳命名，每次清理 |
| 内存不足 | UI 测试超时 | 分批执行测试 |
| 服务未启动 | 测试失败 | 检查服务状态 |
| Priority过滤逻辑复杂 | 边界条件遗漏 | 充分覆盖边界场景 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-18 | 初始版本 | OpenClaw |

---

**文档创建时间**: 2026-03-18
**创建人**: OpenClaw
