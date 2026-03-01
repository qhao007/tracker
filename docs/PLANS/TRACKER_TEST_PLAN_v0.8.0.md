# Tracker v0.8.0 测试计划

> **测试版本**: v0.8.0
> **对应规格书**: `docs/SPECIFICATIONS/tracker_SPECS_v0.8.0.md`
> **创建日期**: 2026-03-01
> **状态**: 待开发
> **预估开发时间**: 3 小时

---

## 1. 版本概述

### 1.1 版本目标

v0.8.0 是进度图表功能的第一个版本，主要目标：
1. 为项目添加起止日期字段
2. 构建 Progress Charts 页面基础框架
3. 修复 ISSUE-001 项目选择框宽度问题

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.8.0.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-001 | 项目起止日期字段 | P0 | 4h |
| REQ-002 | 基础图表框架 | P0 | 3h |
| REQ-003 | ISSUE-001 项目选择框宽度修复 | P3 | 0.5h |

---

## 2. 存放位置

> **重要**：测试计划文件应放在 `docs/PLANS/` 目录下，不要放在 `docs/REPORTS/` 目录下。

**文件路径**: `docs/PLANS/TRACKER_TEST_PLAN_v0.8.0.md`

---

## 3. API 测试计划

### 3.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── test_api.py                     # 基础 CRUD 测试
├── test_api_boundary.py             # 边界条件测试
├── test_api_exception.py            # 异常场景测试
└── test_api_progress.py             # v0.8.0 新增：进度图表 API
```

### 3.2 新增 API 测试用例

#### 3.2.1 项目日期字段测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROJ-001 | test_create_project_with_dates | 创建项目带日期 | 日期正确保存 | REQ-001 |
| API-PROJ-002 | test_create_project_without_dates | 创建项目不带日期 | 日期为空 | REQ-001 |
| API-PROJ-003 | test_update_project_dates | 更新项目日期 | 日期正确更新 | REQ-001 |
| API-PROJ-004 | test_get_project_with_dates | 获取项目含日期 | 返回正确日期 | REQ-001 |
| API-PROJ-005 | test_list_projects_with_dates | 项目列表含日期 | 返回日期字段 | REQ-001 |

#### 3.2.2 日期校验测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROJ-006 | test_date_validation_start_after_end | 开始日期 > 结束日期 | 返回 400 错误 | REQ-001 |
| API-PROJ-007 | test_date_validation_past_date | 日期早于今天 | 可选校验（v0.8.0） | REQ-001 |
| API-PROJ-008 | test_date_validation_empty | 日期为空 | 允许创建 | REQ-001 |

#### 3.2.3 进度数据 API 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROG-001 | test_get_progress_basic | 获取进度数据 | 返回基础结构 | REQ-002 |
| API-PROG-002 | test_get_progress_with_dates | 获取进度数据含日期 | 返回项目日期 | REQ-002 |
| API-PROG-003 | test_get_progress_date_filter | 时间段过滤 | 返回过滤后数据 | REQ-002 |
| API-PROG-004 | test_get_progress_no_dates | 无日期项目 | 返回空planned/actual | REQ-002 |

### 3.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| client fixture | `conftest.py` | Flask test_client |
| test_project fixture | `conftest.py` | 测试项目创建/清理 |

### 3.4 API 测试命令

```bash
# 运行新增的 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_progress.py -v

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
│   ├── dialog-helper.ts            # Dialog 处理工具
│   └── cleanup.ts                  # 测试数据清理工具
└── specs/
    └── integration/
        └── progress_charts.spec.ts  # v0.8.0 新增
```

### 4.2 新增 UI 测试用例

#### 4.2.1 项目日期功能测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PROJ-001 | 创建项目带日期 | 创建项目时输入日期 | REQ-001 | P1 |
| UI-PROJ-002 | 创建项目不带日期 | 创建项目不输入日期 | REQ-001 | P1 |
| UI-PROJ-003 | 编辑项目日期 | 修改项目起止日期 | REQ-001 | P1 |
| UI-PROJ-004 | 项目列表显示日期 | 验证日期显示 | REQ-001 | P1 |

#### 4.2.2 Progress Charts 页面测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-CHART-001 | Tab 切换到 Progress Charts | 切换到进度图表页面 | REQ-002 | P1 |
| UI-CHART-002 | 项目选择器 | 选择不同项目 | REQ-002 | P1 |
| UI-CHART-003 | Chart.js 加载 | 验证图表库加载 | REQ-002 | P1 |
| UI-CHART-004 | 时间段选择器 | 选择日期范围 | REQ-002 | P1 |
| UI-CHART-005 | 空项目提示 | 无日期项目显示提示 | REQ-002 | P1 |

#### 4.2.3 ISSUE-001 修复验证

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-ISSUE-001 | 项目选择框宽度 | 验证宽度为 200px | REQ-003 | P1 |

### 4.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| dialogHelper | `utils/dialog-helper.ts` | 安全处理对话框 |
| cleanupTestData | `utils/cleanup.ts` | 清理测试数据 |

### 4.4 UI 测试命令

```bash
# 运行新增的 UI 集成测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/progress_charts.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 5. 测试开发任务分解

### 5.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发项目日期 CRUD 测试 | `test_api_progress.py` | 1h | 待开始 |
| 开发日期校验测试 | `test_api_progress.py` | 0.5h | 待开始 |
| 开发进度 API 测试 | `test_api_progress.py` | 0.5h | 待开始 |

### 5.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发项目日期 UI 测试 | `progress_charts.spec.ts` | 0.5h | 待开始 |
| 开发图表页面 UI 测试 | `progress_charts.spec.ts` | 0.5h | 待开始 |
| 开发 ISSUE-001 验证测试 | `progress_charts.spec.ts` | 0.25h | 待开始 |

---

## 6. 验收标准

### 6.1 API 测试验收

- [ ] 所有新增 API 测试用例通过
- [ ] 遵循测试 ID 编号规范
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理

### 6.2 UI 测试验收

- [ ] 所有新增 UI 测试用例通过
- [ ] 使用 dialog-helper 处理对话框
- [ ] 使用 cleanup 工具清理测试数据

---

## 7. 测试执行计划

### 7.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_progress.py -v

# 3. 运行 UI 集成测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/progress_charts.spec.ts --project=firefox
```

### 7.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速，稳定，验证后端逻辑 |
| 2 | UI 集成测试 | 验证前端功能 |

---

## 8. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 测试数据冲突 | 测试失败 | 使用时间戳命名，每次清理 |
| Chart.js CDN 不可用 | 图表测试失败 | 使用 mock 或检查网络 |
| 日期校验规则变更 | 测试失败 | 与规格书保持同步 |

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-01 | 初始版本 | 小栗子 🌰 |

---

**模板版本**: v1.0
**创建日期**: 2026-03-01
