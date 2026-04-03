# Tracker FC-CP 模式测试增强覆盖计划

> **版本**: v0.11.0-test-enhancement
> **创建日期**: 2026-04-02
> **审阅人**: Claude Code
> **基于**: BUG-127 & 覆盖率计算分析

---

## 1. 概述

### 1.1 背景

在调试 BUG-127（FC-CP 模式下 CP 未关联高亮错误）时，发现以下问题：

1. **CP 未关联高亮机制** - `renderCP()` 依赖 `functionalCoverages` 数据，但该数据仅在切换到 FC Tab 时加载
2. **FC-CP 模式覆盖率计算** - `get_coverpoints()` API 始终使用 TC 连接计算覆盖率，未考虑 FC-CP 模式

### 1.2 问题分析

#### 问题 1: CP 未关联高亮机制

| 组件 | 问题 |
|------|------|
| **API** `/api/cp` | 未返回 `linked` 状态（CP 是否有关联） |
| **前端** `renderCP()` | 通过 `functionalCoverages[i].cp_ids` 本地计算关联状态 |
| **BUG** | `functionalCoverages` 仅在切换 FC Tab 时加载，CP Tab 查看时为空 |

**影响**: FC-CP 模式下，所有 CP 都显示为红色（未关联），即使已关联 FC。

#### 问题 2: FC-CP 模式覆盖率计算

| 组件 | 问题 |
|------|------|
| **API** `get_coverpoints()` | coverage 基于 `tc_cp_connections` 计算 PASS 比例 |
| **规格** | FC-CP 模式下 coverage 应基于 FC 的 `coverage_pct` |
| **BUG** | API 未检查 `coverage_mode`，始终使用 TC 连接 |

**当前计算逻辑** (api.py:1588-1623):
```python
# 计算覆盖率：统计关联 TC 中 PASS 的比例
cursor.execute("""
    SELECT tc.status FROM test_case tc
    INNER JOIN tc_cp_connections tcc ON tc.id = tcc.tc_id
    WHERE tcc.cp_id = ?
""", (cp_id,))
```

**期望计算逻辑** (FC-CP 模式):
```python
# 计算覆盖率：基于关联 FC 的 coverage_pct 平均值
cursor.execute("""
    SELECT fc.coverage_pct FROM functional_coverage fc
    INNER JOIN fc_cp_association fcca ON fc.id = fcca.fc_id
    WHERE fcca.cp_id = ?
""", (cp_id,))
```

---

## 2. 测试增强计划

### 2.1 CP 未关联高亮测试增强

#### 现有测试

| 测试ID | 覆盖内容 | 状态 |
|--------|----------|------|
| UI-CP-LINK-003 | FC-CP模式未关联FC的CP应该高亮 | ✅ 已覆盖 |
| UI-CP-LINK-004 | FC-CP模式有关联FC的CP正常显示 | ✅ 已覆盖 |
| UI-FC-CP-001 | CP详情页显示关联FC | ✅ 已覆盖 |
| UI-FC-CP-002 | FC-CP关联导入 | ✅ 已覆盖 |

#### 缺失测试

| 测试ID | 测试名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|----------|----------|----------|--------|
| UI-CP-LINK-EXT-001 | CP Tab首次加载时FC-CP关联状态正确 | 创建FC-CP项目，导入FC和关联，直接访问CP Tab | 已关联CP不高亮 | P1 |
| UI-CP-LINK-EXT-002 | 切换到FC Tab再回CP Tab关联状态正确 | 先访问FC Tab，再切换回CP Tab | 已关联CP不高亮 | P1 |
| UI-CP-LINK-EXT-003 | 导入FC-CP关联后立即刷新CP列表 | 创建FC-CP项目，导入FC，导入关联CSV | CP高亮状态立即更新 | P1 |
| UI-CP-LINK-EXT-004 | 删除FC-CP关联后CP恢复高亮 | 已有FC-CP关联，删除关联 | 对应CP恢复高亮 | P2 |

### 2.2 FC-CP 模式覆盖率测试增强

#### 现有测试

| 测试ID | 覆盖内容 | 状态 |
|--------|----------|------|
| 无 | FC-CP模式覆盖率计算 | ❌ 缺失 |

#### 缺失测试 - API

| 测试ID | 测试名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|----------|----------|----------|--------|
| API-CP-COVERAGE-001 | TC-CP模式CP覆盖率计算 | TC-CP项目，CP关联TC(2 PASS/1 FAIL) | coverage=66.7% | P1 |
| API-CP-COVERAGE-002 | FC-CP模式CP覆盖率计算(单个FC) | FC-CP项目，CP关联FC(coverage_pct=85.0) | coverage=85.0% | P1 |
| API-CP-COVERAGE-003 | FC-CP模式CP覆盖率计算(多个FC) | FC-CP项目，CP关联2个FC(85.0, 95.0) | coverage=90.0% | P1 |
| API-CP-COVERAGE-004 | FC-CP模式CP无关联FC | FC-CP项目，CP无关联FC | coverage=0% | P1 |
| API-CP-COVERAGE-005 | FC-CP模式CP关联FC但coverage_pct为NULL | FC关联CP但FC.coverage_pct=NULL | coverage=0% | P2 |
| API-CP-COVERAGE-006 | TC-CP模式覆盖detail格式 | TC-CP项目，3个TC(2 PASS) | coverage_detail="2/3" | P1 |
| API-CP-COVERAGE-007 | FC-CP模式覆盖detail格式 | FC-CP项目，2个FC | coverage_detail="2" 或显示"2 FCs" | P2 |

#### 缺失测试 - UI

| 测试ID | 测试名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|----------|----------|----------|--------|
| UI-CP-COVERAGE-001 | TC-CP模式CP列表显示覆盖率 | TC-CP项目，CP关联TC | 显示正确PASS/FAIL比例 | P1 |
| UI-CP-COVERAGE-002 | FC-CP模式CP列表显示覆盖率 | FC-CP项目，CP关联FC | 显示FC coverage_pct平均值 | P1 |
| UI-CP-COVERAGE-003 | FC-CP模式覆盖率颜色-100% | FC-CP项目，所有FC coverage_pct=100% | 显示绿色(100%) | P1 |
| UI-CP-COVERAGE-004 | FC-CP模式覆盖率颜色-部分 | FC-CP项目，部分FC coverage_pct>0 | 显示黄色 | P1 |
| UI-CP-COVERAGE-005 | FC-CP模式覆盖率颜色-0% | FC-CP项目，所有FC coverage_pct=0% | 显示红色(0%) | P1 |
| UI-CP-COVERAGE-006 | CP详情页显示FC覆盖率 | FC-CP模式，展开CP详情 | 显示关联FC的coverage_pct | P1 |
| UI-CP-COVERAGE-007 | Progress Charts显示FC-CP覆盖率 | FC-CP项目，查看Progress Charts | 图表反映CP覆盖率 | P2 |

### 2.3 覆盖率Badge显示逻辑测试

| 测试ID | 测试名称 | 测试步骤 | 预期结果 | 优先级 |
|--------|----------|----------|----------|--------|
| UI-COVERAGE-BADGE-001 | 覆盖率100%显示绿色 | CP关联FC且全部coverage_pct=100% | badge class=bg-green | P1 |
| UI-COVERAGE-BADGE-002 | 覆盖率0%显示红色 | CP无关联FC或所有coverage_pct=0% | badge class=bg-red | P1 |
| UI-COVERAGE-BADGE-003 | 覆盖率0-100%之间显示黄色 | CP关联部分FC coverage_pct>0 | badge class=bg-yellow | P1 |

---

## 3. 测试文件规划

### 3.1 新增 API 测试

**文件**: `dev/tests/test_api/test_api_cp_coverage_fc_mode.py`

```python
# Test cases: API-CP-COVERAGE-001 ~ 007
# 覆盖 FC-CP 模式下 CP 覆盖率计算
```

### 3.2 新增 UI 测试

**文件**: `dev/tests/test_ui/specs/integration/fc_cp_coverage.spec.ts`

```typescript
// Test cases: UI-CP-COVERAGE-001 ~ 007, UI-COVERAGE-BADGE-001 ~ 003
// Test cases: UI-CP-LINK-EXT-001 ~ 004
// 覆盖 FC-CP 模式 CP 覆盖率显示和高亮
```

---

## 4. 执行计划

### 4.1 第一阶段: API 测试开发 (优先级 P1)

| 任务 | 测试文件 | 预估工时 |
|------|----------|----------|
| API-CP-COVERAGE-001~004 | test_api_cp_coverage_fc_mode.py | 1h |
| API-CP-COVERAGE-006 | test_api_cp_coverage_fc_mode.py | 0.5h |

### 4.2 第二阶段: UI 测试开发 (优先级 P1)

| 任务 | 测试文件 | 预估工时 |
|------|----------|----------|
| UI-CP-LINK-EXT-001~003 | fc_cp_coverage.spec.ts | 1h |
| UI-CP-COVERAGE-001~005 | fc_cp_coverage.spec.ts | 1.5h |
| UI-COVERAGE-BADGE-001~003 | fc_cp_coverage.spec.ts | 0.5h |

### 4.3 第三阶段: 详细测试 (优先级 P2)

| 任务 | 测试文件 | 预估工时 |
|------|----------|----------|
| API-CP-COVERAGE-005, 007 | test_api_cp_coverage_fc_mode.py | 0.5h |
| UI-CP-LINK-EXT-004 | fc_cp_coverage.spec.ts | 0.5h |
| UI-CP-COVERAGE-006~007 | fc_cp_coverage.spec.ts | 1h |

---

## 5. 测试数据准备

### 5.1 TC-CP 模式测试数据

```json
{
  "project": { "name": "Test_TC_CP_Coverage", "coverage_mode": "tc_cp" },
  "cp": { "feature": "feat1", "cover_point": "CP_TC_Cov" },
  "tcs": [
    { "test_name": "TC_PASS_1", "status": "PASS" },
    { "test_name": "TC_PASS_2", "status": "PASS" },
    { "test_name": "TC_FAIL_1", "status": "FAIL" }
  ]
}
```

### 5.2 FC-CP 模式测试数据

```json
{
  "project": { "name": "Test_FC_CP_Coverage", "coverage_mode": "fc_cp" },
  "cp": { "feature": "feat1", "cover_point": "CP_FC_Cov" },
  "fcs": [
    { "bin_name": "fc_bin_1", "coverage_pct": 85.0, "status": "ready" },
    { "bin_name": "fc_bin_2", "coverage_pct": 95.0, "status": "ready" }
  ],
  "fc_cp_associations": [
    { "cp_cover_point": "CP_FC_Cov", "fc_bin_name": "fc_bin_1" },
    { "cp_cover_point": "CP_FC_Cov", "fc_bin_name": "fc_bin_2" }
  ]
}
```

---

## 6. 验收标准

### 6.1 CP 未关联高亮

| 标准 | 测试ID |
|------|--------|
| FC-CP模式下CP Tab首次加载已关联CP不高亮 | UI-CP-LINK-EXT-001 |
| 切换Tab后关联状态保持正确 | UI-CP-LINK-EXT-002 |
| 导入关联后立即刷新高亮状态 | UI-CP-LINK-EXT-003 |
| 删除关联后CP恢复高亮 | UI-CP-LINK-EXT-004 |

### 6.2 FC-CP 覆盖率计算

| 标准 | 测试ID |
|------|--------|
| TC-CP模式使用TC PASS比例计算 | API-CP-COVERAGE-001 |
| FC-CP模式使用FC coverage_pct平均值 | API-CP-COVERAGE-002~003 |
| 无关联FC时coverage=0% | API-CP-COVERAGE-004 |
| UI正确显示覆盖率数值 | UI-CP-COVERAGE-001~002 |
| UI正确显示覆盖率颜色 | UI-COVERAGE-BADGE-001~003 |

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| API需要修改以支持FC-CP覆盖率计算 | 高 | 先确认API修改方案 |
| UI需要修改以区分TC-CP/FC-CP显示 | 高 | 确认前端数据流 |
| 测试数据复杂 | 中 | 使用fixture简化 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.11.0-test-enhancement | 2026-04-02 | 初始版本 |

---

**文档创建时间**: 2026-04-02
**创建人**: Claude Code
