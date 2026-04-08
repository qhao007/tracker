# Tracker v0.12.0 测试覆盖增强计划

> **版本**: v0.12.0
> **创建日期**: 2026-04-08
> **状态**: 待执行
> **基于**: TRACKER_TEST_PLAN_v0.12.0.md 补充

---

## 1. 概述

### 1.1 背景

v0.12.0 测试计划（TRACKER_TEST_PLAN_v0.12.0）存在以下覆盖缺口：

| 缺失领域 | 缺失测试数 | 优先级 |
|----------|------------|--------|
| 快照功能 API 测试 | 6 | P1 |
| 去除组件验证 | 5 | P2 |
| 详情弹窗刷新 | 3 | P2 |
| 矩阵/Owner 颜色阈值 | 7 | P2 |
| **合计** | **21** | |

### 1.2 目标

补充缺失测试用例，使 v0.12.0 测试覆盖率达到 95% 以上。

---

## 2. 缺失测试详情

### 2.1 快照功能 API 测试 (§9.3) - P1

> **优先级**: P1
> **原因**: 快照增强是 v0.12.0 的核心功能之一

#### 2.1.1 测试用例

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-SNAP-001 | test_snapshot_cp_states_saved | 快照保存 cp_states | progress_data 包含 cp_states 字段 | §4.1 |
| API-SNAP-002 | test_snapshot_tc_states_saved | 快照保存 tc_states | progress_data 包含 tc_states 字段 | §4.1 |
| API-SNAP-003 | test_snapshot_old_format_compat | 旧快照兼容性 | cp_states 为 null 时 API 正常返回 | §4.2 |
| API-SNAP-004 | test_snapshot_tc_sum_valid | TC 统计一致性 | pass + fail + not_run = total | §9.3 |
| API-SNAP-005 | test_snapshot_coverage_rate_calc | 覆盖率计算 | rate = Σ(cp_states[].coverage_rate) / N | §9.3 |
| API-SNAP-006 | test_snapshot_linked_tcs_count | linked_tcs 计数 | linked_tcs = COUNT(tc_cp_connections) | §9.3 |

#### 2.1.2 测试实现位置

```
dev/tests/test_api/test_api_snapshot.py  # 新建
```

#### 2.1.3 测试数据要求

| 数据 | 要求 |
|------|------|
| CP 数量 | >= 5 (覆盖不同 coverage_rate 值) |
| TC 数量 | >= 10 (覆盖不同 status) |
| TC-CP 连接 | >= 3 (验证 linked_tcs 计数) |

---

### 2.2 去除组件验证 - P2

> **优先级**: P2
> **原因**: 确保 v0.11.0 组件已正确移除

#### 2.2.1 测试用例

| 测试 ID | 测试名称 | 测试目标 | 验证方法 |
|---------|----------|----------|----------|
| UI-REMOVE-001 | 去除总CP卡片 | 概览页无"总 CP 卡片" | 检查 `.total-cp-card` 或 `.cp-total` 不存在 |
| UI-REMOVE-002 | 去除覆盖率卡片 | 概览页无独立"覆盖率卡片" | 检查 `.coverage-card` 或类似选择器不存在 |
| UI-REMOVE-003 | 去除Feature分布图 | 概览页无 Feature 分布图 | 检查 `.feature-chart` 或 `#featureChart` 不存在 |
| UI-REMOVE-004 | 去除Top5未覆盖 | 概览页无"Top 5 未覆盖" | 检查 `.top5-uncovered` 或类似选择器不存在 |
| UI-REMOVE-005 | 去除Recent Activity | 概览页无 Recent Activity | 检查 `.recent-activity` 或 `#recentActivity` 不存在 |

#### 2.2.2 测试实现位置

```
dev/tests/test_ui/specs/integration/dashboard-removal.spec.ts  # 新建
```

#### 2.2.3 注意事项

- 这些测试在数据丰富的项目（如 SOC_DV）上验证
- 如果组件存在但隐藏（display:none），也算未移除

---

### 2.3 详情弹窗刷新功能 - P2

> **优先级**: P2
> **原因**: 规格书 §9.6 要求"详情弹窗支持刷新数据"

#### 2.3.1 测试用例

| 测试 ID | 测试名称 | 测试目标 | 验证步骤 |
|---------|----------|----------|----------|
| UI-REFRESH-001 | 空洞详情刷新 | 弹窗内刷新按钮更新数据 | 1. 打开空洞详情弹窗<br>2. 点击刷新按钮<br>3. 验证数据更新 |
| UI-REFRESH-002 | Owner详情刷新 | 弹窗内刷新按钮更新数据 | 1. 打开 Owner 详情弹窗<br>2. 点击刷新按钮<br>3. 验证数据更新 |
| UI-REFRESH-003 | 矩阵详情刷新 | 弹窗内刷新按钮更新数据 | 1. 点击矩阵单元格<br>2. 打开详情弹窗<br>3. 点击刷新按钮<br>4. 验证数据更新 |

#### 2.3.2 测试实现位置

在现有测试文件中补充：
- `coverage-holes.spec.ts` - 补充 UI-REFRESH-001
- `owner-dist.spec.ts` - 补充 UI-REFRESH-002
- `coverage-matrix.spec.ts` - 补充 UI-REFRESH-003

#### 2.3.3 注意事项

- 刷新后数据应与 API 最新返回一致
- 刷新过程应有 loading 状态

---

### 2.4 矩阵颜色阈值验证 - P2

> **优先级**: P2
> **原因**: 规格书 §3.5 定义了精确的颜色阈值

#### 2.4.1 测试用例

| 测试 ID | 测试名称 | 测试目标 | 验证方法 |
|---------|----------|----------|----------|
| UI-MAT-006 | 绿色阈值 >=80% | >=80% 显示绿色 | 检查单元格 backgroundColor ≈ #22c55e |
| UI-MAT-007 | 橙色阈值 50-79% | 50-79% 显示橙色 | 检查单元格 backgroundColor ≈ #f59e0b |
| UI-MAT-008 | 红色阈值 20-49% | 20-49% 显示红色 | 检查单元格 backgroundColor ≈ #ef4444 |
| UI-MAT-009 | 深红阈值 <20% | <20% 显示深红 | 检查单元格 backgroundColor ≈ #991b1b |

#### 2.4.2 测试实现位置

在 `coverage-matrix.spec.ts` 中补充

#### 2.4.3 注意事项

- 颜色验证使用 CSS rgb/rgba 值比较，允许 ±5 误差
- 优先验证已存在的矩阵数据，避免创建新测试数据

---

### 2.5 Owner 通过率颜色阈值验证 - P2

> **优先级**: P2
> **原因**: 规格书 §3.4 定义了精确的颜色阈值

#### 2.5.1 测试用例

| 测试 ID | 测试名称 | 测试目标 | 验证方法 |
|---------|----------|----------|----------|
| UI-OWNER-006 | 绿色 >=90% | >=90% 显示绿色 | 检查通过率文本颜色 ≈ #22c55e |
| UI-OWNER-007 | 橙色 70-89% | 70-89% 显示橙色 | 检查通过率文本颜色 ≈ #f59e0b |
| UI-OWNER-008 | 红色 <70% | <70% 显示红色 | 检查通过率文本颜色 ≈ #ef4444 |

#### 2.5.2 测试实现位置

在 `owner-dist.spec.ts` 中补充

---

## 3. 测试开发任务分解

### 3.1 任务清单

| 任务 | 文件 | 测试数 | 优先级 | 预估工时 |
|------|------|--------|--------|----------|
| 快照 API 测试 | `test_api_snapshot.py` | 6 | P1 | 1.5h |
| 去除组件验证 | `dashboard-removal.spec.ts` | 5 | P2 | 1h |
| 详情弹窗刷新 | 现有文件补充 | 3 | P2 | 1h |
| 矩阵颜色阈值 | `coverage-matrix.spec.ts` 补充 | 4 | P2 | 0.5h |
| Owner 颜色阈值 | `owner-dist.spec.ts` 补充 | 3 | P2 | 0.5h |
| **合计** | | **21** | | **4.5h** |

### 3.2 执行顺序

```
1. API 快照测试 (P1) → 2. 去除组件验证 → 3. 详情弹窗刷新 → 4. 颜色阈值验证
```

---

## 4. 测试命令

### 4.1 快照 API 测试

```bash
# 运行快照 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_snapshot.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

### 4.2 UI 测试

```bash
# 运行新增的去除组件测试
cd /projects/management/tracker/dev
PLAYWRIGHT_BROWSERS_PATH=/projects/management/tracker/dev/.playwright-browsers \
HOME=/tmp XDG_RUNTIME_DIR=/tmp XDG_CONFIG_HOME=/tmp/xdg \
npx playwright test tests/test_ui/specs/integration/dashboard-removal.spec.ts --project=firefox

# 运行所有集成测试
PLAYWRIGHT_BROWSERS_PATH=/projects/management/tracker/dev/.playwright-browsers \
HOME=/tmp XDG_RUNTIME_DIR=/tmp XDG_CONFIG_HOME=/tmp/xdg \
npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 5. 验收标准

### 5.1 测试通过标准

| 检查项 | 标准 |
|--------|------|
| 快照 API 测试 | 6/6 通过 |
| 去除组件验证 | 5/5 通过 |
| 详情弹窗刷新 | 3/3 通过 |
| 矩阵颜色阈值 | 4/4 通过 |
| Owner 颜色阈值 | 3/3 通过 |
| **总计** | **21/21** |

### 5.2 测试覆盖率目标

| 指标 | 当前 | 目标 |
|------|------|------|
| 规格覆盖率 | ~70% | >= 95% |
| API 测试用例数 | 28 | 34 |
| UI 测试用例数 | 25 | 46 |

---

## 6. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 颜色阈值验证不稳定 | 测试偶发失败 | 使用 RGB 范围比较，允许 ±5 误差 |
| 快照数据依赖历史 | 测试数据不足 | 使用 SOC_DV 项目数据 |
| 去除组件验证选择器 | 前端类名变化导致失败 | 与前端开发者确认稳定的类名/ID |

---

## 7. 相关文档

| 文档 | 路径 |
|------|------|
| 版本规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.12.0.md` |
| 测试计划 | `docs/PLANS/TRACKER_TEST_PLAN_v0.12.0.md` |
| Bug 记录 | `docs/BUGLOG/tracker_BUG_RECORD.md` |
| 测试报告 | `docs/REPORTS/TEST_REPORT_v0.12.0_20260407.md` |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-04-08 | 初始版本 | Claude Code |

---

**文档创建时间**: 2026-04-08
**创建人**: Claude Code
