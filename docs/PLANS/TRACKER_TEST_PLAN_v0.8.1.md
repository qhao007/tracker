# Tracker v0.8.1 测试计划

> **测试版本**: v0.8.1
> **对应规格书**: `docs/SPECIFICATIONS/tracker_SPECS_v0.8.1.md`
> **创建日期**: 2026-03-02
> **状态**: 待开发
> **预估开发时间**: 2 小时

---

## 1. 版本概述

### 1.1 版本目标

v0.8.1 是进度图表功能的第二个版本，主要目标：
1. 实现 CP 覆盖率计划曲线计算和展示
2. 添加时间段选择器（日期范围过滤）
3. 优化 tracker_ops.py 兼容性测试脚本

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.8.1.md` |
| 需求文档 | `/projects/management/feedbacks/reviewed/tracker_FEATURE_REQUESTS_v0.8.x_20260226.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-081-001 | 计划曲线覆盖率计算算法 | P0 | 3h |
| REQ-081-002 | 计划曲线 API | P0 | 2h |
| REQ-081-003 | 前端计划曲线渲染 | P0 | 2h |
| REQ-081-004 | 时间段选择器 | P1 | 1h |
| REQ-081-005 | 边界处理（无 TC/CP/日期） | P1 | 1h |
| REQ-081-006 | tracker_ops.py 优化 | P3 | 1h |

---

## 2. 存放位置

> **重要**：测试计划文件应放在 `docs/PLANS/` 目录下，不要放在 `docs/REPORTS/` 目录下。

**文件路径**: `docs/PLANS/TRACKER_TEST_PLAN_v0.8.1.md`

---

## 3. API 测试计划

### 3.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── test_api.py                     # 基础 CRUD 测试
├── test_api_progress.py            # v0.8.0: 进度基础 API
└── test_api_planned_curve.py      # v0.8.1 新增：计划曲线 API
```

### 3.2 新增 API 测试用例

#### 3.2.1 计划曲线覆盖率计算测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PLAN-001 | test_calculate_coverage_basic | 基础覆盖率计算 | 覆盖率正确 | REQ-081-001 |
| API-PLAN-002 | test_calculate_coverage_with_pass_tcs | 带 Pass 状态 TC | 仅计算 Pass | REQ-081-001 |
| API-PLAN-003 | test_calculate_coverage_no_tcs | 无 TC | 覆盖率 0% | REQ-081-001 |
| API-PLAN-004 | test_calculate_coverage_no_cps | 无 CP | 避免除零错误 | REQ-081-001 |
| API-PLAN-005 | test_calculate_coverage_dedup | CP 去重 | 去重后计算正确 | REQ-081-001 |

#### 3.2.2 计划曲线 API 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PLAN-010 | test_get_progress_with_planned | 获取含计划曲线数据 | 返回 planned 数组 | REQ-081-002 |
| API-PLAN-011 | test_get_progress_date_filter | 时间段过滤 | 返回过滤后数据 | REQ-081-002 |
| API-PLAN-012 | test_get_progress_start_after_end | 开始 > 结束 | 返回 400 错误 | REQ-081-002 |
| API-PLAN-013 | test_get_progress_no_dates | 无日期项目 | 返回空 planned | REQ-081-002 |
| API-PLAN-014 | test_get_progress_week_boundary | Week 边界 | 周一为起始 | REQ-081-001 |

#### 3.2.3 边界情况测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PLAN-020 | test_get_progress_empty_project | 空项目 | 无 CP/TC | REQ-081-005 |
| API-PLAN-021 | test_get_progress_no_target_date | TC 无 target_date | 跳过该 TC | REQ-081-005 |
| API-PLAN-022 | test_get_progress_future_target | target_date 在未来 | 不计入覆盖 | REQ-081-005 |

### 3.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| client fixture | `conftest.py` | Flask test_client |
| test_project fixture | `conftest.py` | 测试项目创建/清理 |
| auth_client fixture | `conftest.py` | 认证客户端 |

### 3.4 API 测试命令

```bash
# 运行新增的计划曲线 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_planned_curve.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 4. UI 集成测试计划

### 4.1 测试框架

基于 [UI 测试策略](./DEVELOPMENT/UI_TESTING_STRATEGY.md)，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/
├── conftest.ts                     # Playwright 配置
├── utils/
│   ├── dialog-helper.ts           # Dialog 处理工具
│   └── cleanup.ts                 # 测试数据清理工具
└── specs/
    └── integration/
        └── planned_curve.spec.ts  # v0.8.1 新增
```

### 4.2 新增 UI 测试用例

#### 4.2.1 计划曲线渲染测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PLAN-001 | 计划曲线显示 | 图表显示计划曲线 | REQ-081-003 | P1 |
| UI-PLAN-002 | 曲线数据点 | 数据点正确渲染 | REQ-081-003 | P1 |
| UI-PLAN-003 | 曲线颜色 | 计划曲线颜色正确 | REQ-081-003 | P1 |

#### 4.2.2 时间段选择器测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PLAN-010 | 时间段选择器可见 | 日期选择器显示 | REQ-081-004 | P1 |
| UI-PLAN-011 | 选择日期范围 | 选择后图表更新 | REQ-081-004 | P1 |
| UI-PLAN-012 | 清空时间段 | 清空后恢复显示 | REQ-081-004 | P1 |

#### 4.2.3 边界情况测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PLAN-020 | 无项目提示 | 无项目时显示提示 | REQ-081-005 | P1 |
| UI-PLAN-021 | 无日期项目提示 | 项目无日期显示提示 | REQ-081-005 | P1 |
| UI-PLAN-022 | 无 TC 项目提示 | 无 TC 时显示提示 | REQ-081-005 | P1 |
| UI-PLAN-023 | 无 CP 项目提示 | 无 CP 时显示提示 | REQ-081-005 | P1 |

#### 4.2.4 图例和 Tooltip 测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PLAN-030 | 图例显示 | 图例正确显示 | REQ-081-003 | P2 |
| UI-PLAN-031 | Tooltip 提示 | 悬停显示详细信息 | REQ-081-003 | P2 |

### 4.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| dialogHelper | `utils/dialog-helper.ts` | 安全处理对话框 |
| cleanupTestData | `utils/cleanup.ts` | 清理测试数据 |

### 4.4 UI 测试命令

```bash
# 运行新增的计划曲线 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/planned_curve.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 5. 运维工具测试计划

### 5.1 tracker_ops.py 优化测试

#### 5.1.1 测试目标

验证 check 命令不再对系统数据库（users.db、tracker.db）报错

#### 5.1.2 测试用例

| 测试 ID | 测试方法 | 测试目标 | 预期结果 |
|---------|----------|----------|----------|
| OPS-001 | test_check_skips_users_db | check 跳过 users.db | 无错误报告 |
| OPS-002 | test_check_skips_tracker_db | check 跳过 tracker.db | 无错误报告 |
| OPS-003 | test_check_validates_project_db | check 验证项目数据库 | 正常检查 |

#### 5.1.3 测试命令

```bash
cd /projects/management/tracker
python3 scripts/tracker_ops.py check
```

---

## 6. 测试开发任务分解

### 6.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发计划曲线计算测试 | `test_api_planned_curve.py` | 1h | 待开始 |
| 开发计划曲线 API 测试 | `test_api_planned_curve.py` | 0.5h | 待开始 |
| 开发边界情况测试 | `test_api_planned_curve.py` | 0.5h | 待开始 |

### 6.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发计划曲线渲染测试 | `planned_curve.spec.ts` | 0.5h | 待开始 |
| 开发时间段选择器测试 | `planned_curve.spec.ts` | 0.5h | 待开始 |
| 开发边界情况测试 | `planned_curve.spec.ts` | 0.5h | 待开始 |
| 开发图例/Tooltip 测试 | `planned_curve.spec.ts` | 0.25h | 待开始 |

### 6.3 运维工具测试

| 任务 | 测试方式 | 预估工时 | 状态 |
|------|----------|----------|------|
| tracker_ops.py 优化验证 | 手动执行 | 0.25h | 待开始 |

---

## 7. 验收标准

### 7.1 API 测试验收

- [ ] 所有新增 API 测试用例通过
- [ ] 遵循测试 ID 编号规范 (API-PLAN-xxx)
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理

### 7.2 UI 测试验收

- [ ] 所有新增 UI 测试用例通过
- [ ] 遵循测试 ID 编号规范 (UI-PLAN-xxx)
- [ ] 使用 dialog-helper 处理对话框
- [ ] 使用 cleanup 工具清理测试数据

### 7.3 运维工具验收

- [ ] check 命令不再报告 users.db 错误
- [ ] 项目数据库检查功能正常

---

## 8. 测试执行计划

### 8.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_planned_curve.py -v

# 3. 运行 UI 集成测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/planned_curve.spec.ts --project=firefox

# 4. 验证 tracker_ops.py
cd /projects/management/tracker && python3 scripts/tracker_ops.py check
```

### 8.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速，稳定，验证后端逻辑 |
| 2 | UI 集成测试 | 验证前端功能 |
| 3 | 运维工具测试 | 验证脚本优化 |

---

## 9. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 计划曲线算法复杂 | 测试用例难以覆盖 | 参考需求文档 SQL 逐步验证 |
| Week 边界处理 | 可能有时区问题 | 使用 UTC 时间处理 |
| Chart.js 多曲线渲染 | 样式冲突 | 先验证单曲线，再添加多曲线 |
| 测试数据依赖 | 测试不稳定 | 使用固定测试项目 EX5 |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-02 | 初始版本 | 小栗子 🌰 |

---

**模板版本**: v1.0
**创建日期**: 2026-03-02
