# Tracker v0.13.0 补充测试计划：Dashboard FC-CP 模式支持

> **测试版本**: v0.13.0
> **对应规格书**: `tracker_SPECS_v0.13.0_DASHBOARD_FC_CP_SUPPLEMENT.md`
> **创建日期**: 2026-04-15
> **状态**: 待开发
> **预估开发时间**: 6 小时

---

## 1. 版本概述

### 1.1 版本目标

为 Dashboard FC-CP 模式支持功能（v0.13.0 补充）编写测试用例，确保功能质量。

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.13.0_DASHBOARD_FC_CP_SUPPLEMENT.md` |
| 主测试计划 | `docs/PLANS/TRACKER_TEST_PLAN_v0.13.0.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-D001 | Dashboard API 增加 FC-CP 模式检测 | P0 | 1h |
| REQ-D002 | `/api/dashboard/stats` 支持 FC-CP 模式 | P0 | 2h |
| REQ-D003 | `/api/dashboard/coverage-matrix` 支持 FC-CP 模式 | P0 | 3h |
| REQ-D004 | 前端 Dashboard 根据模式切换数据展示 | P0 | 2h |

---

## 2. 测试范围说明

### 2.1 需要测试的 API

| API Endpoint | 说明 | 需要修改 | 测试重点 |
|--------------|------|----------|---------|
| `/api/dashboard/stats` | Overview 统计 | ✅ | FC-CP 模式下返回 FC 统计 |
| `/api/dashboard/coverage-holes` | Coverage Holes | ❌ 已支持 | 回归测试 |
| `/api/dashboard/owner-stats` | Owner 分布 | ❌ 无需修改 | 回归测试 |
| `/api/dashboard/coverage-matrix` | Coverage Matrix | ✅ | FC-CP 模式下返回 FC-CP 矩阵 |

### 2.2 不需要测试的 API

- `/api/dashboard/owner-stats`：Owner Distribution 始终从 test_case 表获取，无需修改

---

## 3. 存放位置

| 文档类型 | 目录 |
|----------|------|
| 测试计划 (Test Plan) | `docs/PLANS/` ← 本文档 |
| 测试报告 (Test Report) | `docs/REPORTS/` |

---

## 4. API 测试计划

### 4.1 测试框架

基于 `docs/DEVELOPMENT/API_TESTING_STRATEGY.md`，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── conftest.py                           # 共享 fixture
├── test_api_dashboard.py                  # 现有 Dashboard 测试
└── test_api_dashboard_fc_cp.py           # ⭐ FC-CP Dashboard 测试（新增）
```

### 4.2 新增 API 测试用例

#### 4.2.1 FC-CP 模式 Stats 测试

| 测试 ID | 测试方法 | 测试目标 | 场景 | 对应规格 |
|---------|----------|----------|------|----------|
| API-DASH-FC-001 | test_dashboard_stats_fc_cp_mode | FC-CP 模式返回 FC 统计 | FC-CP 项目调用 stats API | REQ-D002 |
| API-DASH-FC-002 | test_dashboard_stats_tc_cp_mode | TC-CP 模式行为不变 | TC-CP 项目调用 stats API | REQ-D002 |
| API-DASH-FC-003 | test_dashboard_stats_response_contains_mode | 响应包含 mode 字段 | 验证 mode 字段存在 | REQ-D002 |
| API-DASH-FC-004 | test_dashboard_stats_fc_cp_count_correct | FC 统计数量正确 | 验证 total/covered 数量 | REQ-D002 |

#### 4.2.2 FC-CP 模式 Coverage Matrix 测试

| 测试 ID | 测试方法 | 测试目标 | 场景 | 对应规格 |
|---------|----------|----------|------|----------|
| API-DASH-FC-010 | test_dashboard_matrix_fc_cp_mode | FC-CP 模式返回 FC-CP 矩阵 | FC-CP 项目调用 matrix API | REQ-D003 |
| API-DASH-FC-011 | test_dashboard_matrix_tc_cp_mode | TC-CP 模式行为不变 | TC-CP 项目调用 matrix API | REQ-D003 |
| API-DASH-FC-012 | test_dashboard_matrix_response_contains_mode | 响应包含 mode 字段 | 验证 mode 字段存在 | REQ-D003 |
| API-DASH-FC-013 | test_dashboard_matrix_fc_cp_mapping_correct | FC-CP 关联关系正确 | 验证矩阵数据准确 | REQ-D003 |

#### 4.2.3 回归测试

| 测试 ID | 测试方法 | 测试目标 | 场景 | 对应规格 |
|---------|----------|----------|------|----------|
| API-DASH-FC-020 | test_dashboard_coverage_holes_fc_cp_unchanged | Coverage Holes FC-CP 仍正常 | 回归验证 | - |
| API-DASH-FC-021 | test_dashboard_owner_stats_unchanged | Owner Stats 行为不变 | 回归验证 | - |
| API-DASH-FC-022 | test_dashboard_stats_tc_cp_backward_compat | TC-CP 响应格式兼容 | 回归验证 | REQ-D002 |

### 4.3 测试数据准备

#### 4.3.1 FC-CP 模式测试项目

```python
@pytest.fixture
def fc_cp_project(test_db):
    """创建 FC-CP 模式的测试项目"""
    # 创建项目，coverage_mode = 'fc_cp'
    project_id = create_project_with_mode("FC_CP_Test_Project", "fc_cp")
    yield project_id
    # 清理已在 conftest.py 中处理

@pytest.fixture
def fc_cp_test_data(fc_cp_project):
    """创建 FC-CP 模式的测试数据"""
    project_id = fc_cp_project

    # 创建 FC（Functional Coverage）
    fc_ids = []
    for i in range(5):
        fc_id = create_functional_coverage(
            project_id=project_id,
            name=f"FC_{i+1}",
            owner=f"Owner_{i+1}"
        )
        fc_ids.append(fc_id)

    # 创建 CP（Cover Point）
    cp_ids = []
    for i in range(8):
        cp_id = create_cover_point(
            project_id=project_id,
            name=f"CP_{i+1}"
        )
        cp_ids.append(cp_id)

    # 创建 FC-CP 关联（部分关联）
    create_fc_cp_connection(project_id, fc_ids[0], cp_ids[0])
    create_fc_cp_connection(project_id, fc_ids[0], cp_ids[1])
    create_fc_cp_connection(project_id, fc_ids[1], cp_ids[0])

    return {
        "project_id": project_id,
        "fc_ids": fc_ids,
        "cp_ids": cp_ids
    }
```

#### 4.3.2 测试数据表结构

**functional_coverage 表**（需确认是否存在）：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | TEXT | FC 名称 |
| owner | TEXT | 负责人 |
| project_id | INTEGER | 所属项目 |

**fc_cp_connection 表**（需确认是否存在）：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 所属项目 |
| fc_id | INTEGER | FC 外键 |
| cp_id | INTEGER | CP 外键 |

### 4.4 API 测试命令

```bash
# 运行 Dashboard FC-CP API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_dashboard_fc_cp.py -v

# 运行所有 Dashboard API 测试
PYTHONPATH=. pytest tests/test_api/test_api_dashboard.py tests/test_api/test_api_dashboard_fc_cp.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 5. UI 集成测试计划

### 5.1 测试框架

基于 `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md`，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/
├── conftest.ts                           # Playwright 配置
└── specs/
    └── integration/
        ├── dashboard.spec.ts            # 现有 Dashboard 测试
        └── dashboard_fc_cp.spec.ts      # ⭐ FC-CP Dashboard 测试（新增）
```

### 5.2 新增 UI 测试用例

#### 5.2.1 Dashboard FC-CP Overview 测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-DASH-FC-001 | dashboard_fc_cp_overview_shows_fc_label | FC-CP 项目 Overview 显示 FC 标签 | REQ-D004 | P0 |
| UI-DASH-FC-002 | dashboard_fc_cp_overview_stats_correct | FC-CP 项目 Overview 统计数据正确 | REQ-D004 | P0 |
| UI-DASH-FC-003 | dashboard_tc_cp_overview_unchanged | TC-CP 项目 Overview 行为不变 | REQ-D004 | P0 |

#### 5.2.2 Dashboard FC-CP Coverage Matrix 测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-DASH-FC-010 | dashboard_fc_cp_matrix_shows_fc_columns | FC-CP 项目 Matrix 显示 FC 列 | REQ-D004 | P0 |
| UI-DASH-FC-011 | dashboard_fc_cp_matrix_checkbox_mapping | FC-CP Matrix 复选框映射正确 | REQ-D004 | P0 |
| UI-DASH-FC-012 | dashboard_tc_cp_matrix_unchanged | TC-CP 项目 Matrix 行为不变 | REQ-D004 | P0 |

#### 5.2.3 Dashboard 项目切换测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-DASH-FC-020 | dashboard_switch_fc_cp_to_tc_cp | 切换 TC-CP 项目后 Dashboard 刷新 | REQ-D004 | P0 |
| UI-DASH-FC-021 | dashboard_switch_tc_cp_to_fc_cp | 切换 FC-CP 项目后 Dashboard 刷新 | REQ-D004 | P0 |

#### 5.2.4 回归测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-DASH-FC-030 | dashboard_coverage_holes_fc_cp_unchanged | Coverage Holes FC-CP 显示正确 | - | P0 |
| UI-DASH-FC-031 | dashboard_owner_distribution_unchanged | Owner Distribution 行为不变 | - | P0 |

### 5.3 UI 测试辅助函数

```typescript
// dev/tests/test_ui/specs/integration/dashboard_fc_cp.spec.ts

import { test, expect } from '@playwright/test';

// 辅助函数：切换到 FC-CP 模式项目
async function switchToFcCpProject(page: Page, projectName: string) {
    await page.click('#projectSelect');
    await page.selectOption(`#projectSelect`, { label: projectName });
    await page.waitForTimeout(500); // 等待 Dashboard 刷新
}

// 辅助函数：获取 Overview 标签文本
async function getOverviewLabel(page: Page): Promise<string> {
    return await page.textContent('#overviewTotalItemsLabel');
}

// 辅助函数：获取 Matrix 表格标题
async function getMatrixTitle(page: Page): Promise<string> {
    return await page.textContent('#matrixTableTitle');
}
```

### 5.4 UI 测试命令

```bash
# 运行 Dashboard FC-CP UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/dashboard_fc_cp.spec.ts --project=firefox

# 运行所有 Dashboard UI 测试
npx playwright test tests/test_ui/specs/integration/dashboard.spec.ts tests/test_ui/specs/integration/dashboard_fc_cp.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 6. 测试开发任务分解

### 6.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 创建 FC-CP 测试文件 | `test_api_dashboard_fc_cp.py` | 0.5h | ⏳ 待开始 |
| 实现 Stats FC-CP 测试 | `test_api_dashboard_fc_cp.py` | 1h | ⏳ 待开始 |
| 实现 Matrix FC-CP 测试 | `test_api_dashboard_fc_cp.py` | 1.5h | ⏳ 待开始 |
| 实现回归测试 | `test_api_dashboard_fc_cp.py` | 0.5h | ⏳ 待开始 |
| 准备 FC-CP 测试数据 | fixture | 0.5h | ⏳ 待开始 |

### 6.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 创建 FC-CP UI 测试文件 | `dashboard_fc_cp.spec.ts` | 0.5h | ⏳ 待开始 |
| 实现 Overview 标签测试 | `dashboard_fc_cp.spec.ts` | 0.5h | ⏳ 待开始 |
| 实现 Matrix 标签测试 | `dashboard_fc_cp.spec.ts` | 1h | ⏳ 待开始 |
| 实现项目切换测试 | `dashboard_fc_cp.spec.ts` | 0.5h | ⏳ 待开始 |
| 实现回归测试 | `dashboard_fc_cp.spec.ts` | 0.5h | ⏳ 待开始 |

---

## 7. 验收标准

### 7.1 API 测试验收

- [ ] API-DASH-FC-001 ~ API-DASH-FC-004 所有 Stats 测试通过
- [ ] API-DASH-FC-010 ~ API-DASH-FC-013 所有 Matrix 测试通过
- [ ] API-DASH-FC-020 ~ API-DASH-FC-022 所有回归测试通过
- [ ] FC-CP 模式返回正确的 FC 统计数据
- [ ] TC-CP 模式行为保持不变
- [ ] 响应包含 `mode` 字段

### 7.2 UI 测试验收

- [ ] UI-DASH-FC-001 ~ UI-DASH-FC-003 所有 Overview 测试通过
- [ ] UI-DASH-FC-010 ~ UI-DASH-FC-012 所有 Matrix 测试通过
- [ ] UI-DASH-FC-020 ~ UI-DASH-FC-021 项目切换测试通过
- [ ] UI-DASH-FC-030 ~ UI-DASH-FC-031 回归测试通过
- [ ] FC-CP 模式显示 FC 标签（而非 TC）
- [ ] TC-CP 模式行为保持不变

---

## 8. 测试执行计划

### 8.1 前置条件

1. 确认 `models.py` 中存在 `FunctionalCoverage` 和 `FcCpConnection` 模型
2. 确认 FC-CP 测试项目数据已准备好

### 8.2 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_dashboard_fc_cp.py -v

# 3. 运行 UI 测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/dashboard_fc_cp.spec.ts --project=firefox
```

### 8.3 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速、稳定，验证后端逻辑 |
| 2 | UI 集成测试 | 验证前端功能和交互 |

---

## 9. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| FC 表结构与预期不符 | 测试无法运行 | 先确认 models.py 中 FC 相关模型 |
| FC-CP 测试数据缺失 | 无法验证功能 | 需要先准备测试数据 |
| UI 测试依赖 API 正确 | 连锁失败 | 先运行 API 测试确保后端正常 |

---

## 10. 相关文档

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.13.0_DASHBOARD_FC_CP_SUPPLEMENT.md` |
| 主测试计划 | `docs/PLANS/TRACKER_TEST_PLAN_v0.13.0.md` |
| API 测试策略 | `docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| UI 测试策略 | `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` |
| Dashboard API | `dev/app/api.py` |
| Dashboard 前端 | `dev/static/js/dashboard.js` |
| Dashboard 测试 | `dev/tests/test_api/test_api_dashboard.py` |

---

## 11. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-04-15 | 初始版本 | Claude Code |

---

**文档创建时间**: 2026-04-15
**创建人**: Claude Code
