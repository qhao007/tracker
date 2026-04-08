# Tracker v0.12.0 测试计划

> **测试版本**: v0.12.0
> **对应规格书**: tracker_SPECS_v0.12.0.md
> **创建日期**: 2026-04-07
> **状态**: 待开发
> **预估开发时间**: ~20h

---

## 1. 版本概述

### 1.1 版本目标

Dashboard 增强功能：
- 新增 4 Tab 结构（概览/空洞/Owner/矩阵）
- 覆盖率空洞看板
- TC Owner 分布
- Feature × Priority 覆盖率矩阵
- 快照 CP + TC 状态信息增强
- FC 页面 Group 覆盖率显示

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.12.0.md` |
| 需求文档 | `/projects/management/feedbacks/reviewed/REQ_DASHBOARD_ENHANCEMENT_v1.0.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| #1 | Dashboard Tab 重构 | P1 | 2h |
| #2 | 覆盖率空洞看板 | P1 | 4h |
| #3 | TC Owner 分布 | P1 | 5h |
| #4 | Feature × Priority 覆盖率矩阵 | P2 | 4h |
| #5 | 快照 CP + TC 状态信息 | P1 | 3h |
| #6 | FC 页面 Group 覆盖率显示 | P2 | 2h |

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
├── test_api_exception.py         # 异常场景测试
└── test_api_dashboard.py          # Dashboard 新增 API 测试 ← 新增
```

### 2.2 新增 API 测试用例

#### 2.2.1 Dashboard Stats API 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-DASH-001 | test_dashboard_stats_basic | 测试获取概览统计 | 返回 overview/by_feature/by_priority | §7.1 |
| API-DASH-002 | test_dashboard_stats_week_change | 测试周环比计算 | 返回正确环比变化 | §6 |
| API-DASH-003 | test_dashboard_stats_no_snapshot | 测试无快照数据 | 返回 "--" 或 null | §6 |

#### 2.2.2 Coverage Holes API 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-HOLE-001 | test_coverage_holes_basic | 测试获取空洞列表 | 返回 critical/warning/attention | §7.1 |
| API-HOLE-002 | test_coverage_holes_critical | 测试严重空洞识别 | linked_tcs≥3 + coverage=0 | §3.3 |
| API-HOLE-003 | test_coverage_holes_warning | 测试警告空洞识别 | linked_tcs 1-2 + coverage=0 | §3.3 |
| API-HOLE-004 | test_coverage_holes_attention | 测试关注空洞识别 | 0% < coverage < 10% | §3.3 |
| API-HOLE-005 | test_coverage_holes_no_linked_tc | 测试排除未关联 TC 的 CP | 不返回 linked_tcs=0 | §3.3 |
| API-HOLE-006 | test_coverage_holes_all_tc_fail | 测试排除全部 TC 失败的 CP | 不返回全部 FAIL 的 CP | §3.3 |

#### 2.2.3 Owner Stats API 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-OWNER-001 | test_owner_stats_basic | 测试获取 Owner 列表 | 返回所有 Owner | §7.2 |
| API-OWNER-002 | test_owner_stats_pass_rate | 测试通过率计算 | pass/total 正确 | §7.2 |
| API-OWNER-003 | test_owner_stats_unassigned | 测试未分配 TC | 显示 (未分配) | §7.2 |
| API-OWNER-004 | test_owner_stats_summary | 测试汇总统计 | total_owners/unassigned_tc_count | §7.2 |

#### 2.2.4 Coverage Matrix API 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-MATRIX-001 | test_coverage_matrix_basic | 测试获取矩阵 | 返回所有 features/priorities | §7.3 |
| API-MATRIX-002 | test_coverage_matrix_covered | 测试已覆盖计数 | covered/total 正确 | §7.3 |
| API-MATRIX-003 | test_coverage_matrix_cp_ids | 测试 CP ID 列表 | 返回 cp_ids 数组 | §7.3 |
| API-MATRIX-004 | test_coverage_matrix_weak_areas | 测试薄弱区域 | 返回 < 50% 的单元格 | §3.5 |
| API-MATRIX-005 | test_coverage_matrix_severity | 测试告警级别 | critical/warning 正确 | §3.5 |

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
# 运行 Dashboard 新增 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_dashboard.py -v

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
│   ├── dialog-helper.ts           # Dialog 处理工具
│   └── cleanup.ts                 # 测试数据清理工具
└── specs/
    ├── smoke/                     # 冒烟测试
    └── integration/               # 集成测试
        ├── dashboard-tabs.spec.ts  # Dashboard Tab 测试 ← 新增
        ├── coverage-holes.spec.ts # 空洞看板测试 ← 新增
        ├── owner-dist.spec.ts     # Owner 分布测试 ← 新增
        └── coverage-matrix.spec.ts # 覆盖率矩阵测试 ← 新增
```

### 3.2 新增 UI 测试用例

#### 3.2.1 Dashboard Tabs 测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-TAB-001 | Tab 切换 | 各 Tab 切换正常 | §3.1 | P1 |
| UI-TAB-002 | Tab 内容加载 | Tab 内容正确显示 | §3.1 | P1 |
| UI-TAB-003 | Tab 动画 | 切换有过渡动画 | §11.7 | P2 |

#### 3.2.2 概览页测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-OVER-001 | 趋势图显示 | 7天趋势图正确渲染 | §3.2 | P1 |
| UI-OVER-002 | 数字卡片显示 | 已覆盖/未关联/TC通过率显示 | §3.2 | P1 |
| UI-OVER-003 | 周环比显示 | 正确显示变化值或 "--" | §6 | P1 |
| UI-OVER-004 | 矩阵预览 | Top 4 Features 显示 | §3.2 | P1 |
| UI-OVER-005 | 空洞摘要 | Top 3 严重空洞显示 | §3.2 | P1 |
| UI-OVER-006 | Owner摘要 | Top 3 Owner 显示 | §3.2 | P1 |

#### 3.2.3 覆盖空洞看板测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-HOLE-001 | 空洞卡片显示 | 严重/警告/关注分级显示 | §3.3 | P1 |
| UI-HOLE-002 | 空洞详情弹窗 | 点击显示关联 TC 列表 | §3.3 | P1 |
| UI-HOLE-003 | 弹窗关闭-ESC | ESC 键关闭弹窗 | §11.6 | P1 |
| UI-HOLE-004 | 弹窗关闭-遮罩 | 点击遮罩关闭弹窗 | §11.6 | P1 |
| UI-HOLE-005 | 空数据显示 | 无空洞时显示提示 | §11.5 | P2 |
| UI-HOLE-006 | 加载状态 | 加载中显示 skeleton | §11.6 | P2 |

#### 3.2.4 Owner 分布测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-OWNER-001 | Owner 列表显示 | 所有 Owner 显示 | §3.4 | P1 |
| UI-OWNER-002 | 通过率颜色 | 根据阈值显示正确颜色 | §3.4 | P1 |
| UI-OWNER-003 | Owner 详情弹窗 | 点击显示 TC 列表 | §3.4 | P1 |
| UI-OWNER-004 | TC 列表分页 | >20 条时显示查看全部 | §3.4 | P2 |
| UI-OWNER-005 | 空数据显示 | 无 TC 时显示提示 | §11.5 | P2 |

#### 3.2.5 覆盖率矩阵测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-MAT-001 | 矩阵显示 | Feature × Priority 正确渲染 | §3.5 | P1 |
| UI-MAT-002 | 单元格颜色 | 根据阈值显示正确颜色 | §3.5 | P1 |
| UI-MAT-003 | 薄弱区域告警 | < 50% 显示告警 | §3.5 | P1 |
| UI-MAT-004 | 单元格详情 | 点击显示 CP 列表 | §3.5 | P1 |
| UI-MAT-005 | 空数据显示 | 无 CP 时显示提示 | §11.5 | P2 |

#### 3.2.6 FC Group 覆盖率测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FC-001 | Group 覆盖率显示 | 每行显示组覆盖率 | §5.1 | P1 |
| UI-FC-002 | 覆盖率计算 | 组覆盖率 = 平均值 | §5.1 | P1 |
| UI-FC-003 | 颜色显示 | 根据阈值显示颜色 | §5.1 | P2 |

### 3.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| dialogHelper | `utils/dialog-helper.ts` | 安全处理对话框 |
| cleanupTestData | `utils/cleanup.ts` | 清理测试数据 |
| testProject | `conftest.ts` | 测试项目 fixture |

### 3.4 UI 测试命令

```bash
# 运行 Dashboard 新增 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/dashboard-tabs.spec.ts --project=firefox
npx playwright test tests/test_ui/specs/integration/coverage-holes.spec.ts --project=firefox
npx playwright test tests/test_ui/specs/integration/owner-dist.spec.ts --project=firefox
npx playwright test tests/test_ui/specs/integration/coverage-matrix.spec.ts --project=firefox

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
| Dashboard Stats API 测试 | `test_api_dashboard.py` | 1h | 待开始 |
| Coverage Holes API 测试 | `test_api_dashboard.py` | 2h | 待开始 |
| Owner Stats API 测试 | `test_api_dashboard.py` | 1h | 待开始 |
| Coverage Matrix API 测试 | `test_api_dashboard.py` | 1h | 待开始 |

### 4.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| Dashboard Tabs 测试 | `dashboard-tabs.spec.ts` | 1h | 待开始 |
| 概览页测试 | `dashboard-tabs.spec.ts` | 2h | 待开始 |
| 覆盖空洞看板测试 | `coverage-holes.spec.ts` | 3h | 待开始 |
| Owner 分布测试 | `owner-dist.spec.ts` | 2h | 待开始 |
| 覆盖率矩阵测试 | `coverage-matrix.spec.ts` | 2h | 待开始 |
| FC Group 覆盖率测试 | `coverage-holes.spec.ts` | 1h | 待开始 |

---

## 5. 验收标准

### 5.1 API 测试验收

- [ ] 所有 18 个新增 API 测试用例通过
- [ ] 遵循测试 ID 编号规范
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理

### 5.2 UI 测试验收

- [ ] 所有 24 个新增 UI 测试用例通过
- [ ] 使用 dialog-helper 处理对话框
- [ ] 使用 cleanup 工具清理测试数据
- [ ] 测试通过后自动清理数据

### 5.3 验收检查清单

| 检查项 | 要求 |
|--------|------|
| Tab 切换 | 无白屏，有过渡动画 |
| 空洞分级 | 严重/警告/关注颜色正确 |
| Owner 通过率 | 前端计算正确，颜色正确 |
| 矩阵颜色 | 阈值正确映射 |
| 弹窗交互 | ESC 和遮罩可关闭 |
| 空数据 | 显示友好提示 |
| 加载状态 | 显示 skeleton/spinner |
| 详情弹窗刷新 | 支持刷新数据 |

---

## 6. 测试执行计划

### 6.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v

# 3. 运行 UI 测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/ --project=firefox
```

### 6.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速、稳定，验证后端逻辑 |
| 2 | UI 冒烟测试 | 验证核心功能可用 |
| 3 | UI 集成测试 | 验证完整功能流程 |

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 测试数据冲突 | 测试失败 | 使用时间戳命名，每次清理 |
| 内存不足 | UI 测试超时 | 分批执行测试 |
| 服务未启动 | 测试失败 | 检查服务状态 |
| 快照数据依赖 | 测试不稳定 | 使用 fixture 管理测试数据 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-04-07 | 初始版本 | OpenClaw |

---

**模板版本**: v1.0
**创建日期**: 2026-04-07
