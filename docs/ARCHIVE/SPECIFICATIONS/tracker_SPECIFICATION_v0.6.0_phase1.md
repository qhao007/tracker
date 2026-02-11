# Tracker v0.6.0 第一阶段规格书

> **版本**: v0.6.0 Phase 1
> **创建日期**: 2026-02-07
> **状态**: 开发中
> **关联需求**: tracker_FEATURE_REQUESTS_v0.6.0_20260207.md

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 2 | Status 日期记录与显示 | P0 | 6h |
| 3 | Target Date 字段 | P0 | 7.5h |
| 4 | Removed 状态选项 | P0 | 5h |
| 4.7 | 批量修改状态 | P0 | 7h |
| 5 | DV Milestone 字段 | P0 | 7.5h |
| 6 | Cover Point Priority 字段 | P0 | 7.5h |
| | **总计** | | **~40h** |

---

## 2. 数据库修改

### 2.1 Test Case 表新增字段

```sql
-- Status 日期字段
ALTER TABLE test_cases ADD COLUMN coded_date DATE DEFAULT NULL;
ALTER TABLE test_cases ADD COLUMN fail_date DATE DEFAULT NULL;
ALTER TABLE test_cases ADD COLUMN pass_date DATE DEFAULT NULL;
ALTER TABLE test_cases ADD COLUMN removed_date DATE DEFAULT NULL;

-- Target Date 字段
ALTER TABLE test_cases ADD COLUMN target_date DATE DEFAULT NULL;

-- DV Milestone 字段
ALTER TABLE test_cases ADD COLUMN dv_milestone VARCHAR(10) DEFAULT NULL;
```

### 2.2 Cover Points 表新增字段

```sql
-- Priority 字段
ALTER TABLE cover_points ADD COLUMN priority VARCHAR(3) DEFAULT 'P0';
```

### 2.3 数据迁移

```sql
-- 为已有数据填充日期
UPDATE test_cases SET pass_date = updated_at WHERE status = 'PASS';
UPDATE test_cases SET coded_date = updated_at WHERE status = 'CODED';
UPDATE test_cases SET fail_date = updated_at WHERE status = 'FAIL';

-- DV Milestone 默认值
UPDATE test_cases SET dv_milestone = 'DV1.0' WHERE dv_milestone IS NULL;

-- CP Priority 默认值
UPDATE cover_points SET priority = 'P0' WHERE priority IS NULL;
```

---

## 3. API 接口修改

### 3.1 GET /api/tc - 获取 TC 列表

**新增响应字段**:
```json
{
  "data": [
    {
      "id": 1,
      "status": "PASS",
      "coded_date": "2026-02-01",
      "fail_date": null,
      "pass_date": "2026-02-07",
      "removed_date": null,
      "target_date": "2026-02-15",
      "dv_milestone": "DV0.5"
    }
  ]
}
```

> **说明**: TC 详情 API (`GET /api/tc/{id}`) 额外返回 `connected_cps` 字段，表示关联的 CP ID 列表。

### 3.2 PATCH /api/tc/{id}/status - 更新状态

**自动设置日期逻辑**:
```python
status_mapping = {
    'CODED': 'coded_date',
    'FAIL': 'fail_date',
    'PASS': 'pass_date',
    'REMOVED': 'removed_date'
}

def update_status(tc_id, new_status):
    tc = TestCase.get(tc_id)
    tc.status = new_status

    # 设置对应日期
    date_field = status_mapping.get(new_status)
    if date_field:
        setattr(tc, date_field, date.today())

    # 如果是 REMOVED，清除 CP 关联
    if new_status == 'REMOVED':
        tc.cover_points = []

    tc.save()
```

### 3.3 PUT /api/tc/{id} - 更新 TC

**支持更新字段**:
- `target_date`
- `dv_milestone`
- `connections` - TC 关联的 CP ID 列表（覆盖原有关联）

**请求体**:
```json
{
  "project_id": 1,
  "target_date": "2026-02-15",
  "dv_milestone": "DV0.5",
  "connections": [1, 2, 3]
}
```

> **注意**: `connections` 字段会覆盖 TC 与 CP 的关联关系。

### 3.4 POST /api/tc/batch/status - 批量更新状态

**请求体**:
```json
{
  "project_id": 1,
  "tc_ids": [1, 2, 3],
  "status": "PASS"
}
```

**响应**:
```json
{
  "success": 3,
  "failed": 0
}
```

### 3.5 POST /api/tc/batch/target_date - 批量更新 Target Date

**请求体**:
```json
{
  "project_id": 1,
  "tc_ids": [1, 2, 3],
  "target_date": "2026-02-20"
}
```

### 3.6 POST /api/tc/batch/dv_milestone - 批量更新 DV Milestone

**请求体**:
```json
{
  "project_id": 1,
  "tc_ids": [1, 2, 3],
  "dv_milestone": "DV0.5"
}
```

### 3.7 GET /api/cp - 获取 CP 列表

**新增响应字段**:
```json
{
  "data": [
    {
      "id": 1,
      "priority": "P1",
      "feature": "Feature A"
    }
  ]
}
```

### 3.8 PATCH /api/cp/{id} - 更新 CP

**支持更新字段**:
- `priority`

### 3.9 POST /api/cp/batch/priority - 批量更新 Priority

**请求体**:
```json
{
  "project_id": 1,
  "cp_ids": [1, 2, 3],
  "priority": "P2"
}
```

### 3.10 GET /api/stats - 统计数据

**修改统计规则**:
```python
def calculate_stats(project_id):
    tcs = TestCase.filter(project_id=project_id)

    total = 0
    pass_count = 0
    coded_count = 0
    fail_count = 0

    for tc in tcs:
        if tc.status == 'REMOVED':
            continue  # REMOVED 不计入任何统计

        total += 1

        if tc.status == 'PASS':
            pass_count += 1
        elif tc.status == 'CODED':
            coded_count += 1
        elif tc.status == 'FAIL':
            fail_count += 1

    pass_rate = round(pass_count / total * 100, 1) if total > 0 else 0

    return {
        'total': total,
        'pass': pass_count,
        'coded': coded_count,
        'fail': fail_count,
        'pass_rate': pass_rate
    }
```

---

## 4. 前端界面修改

### 4.1 TC 表格新增列

| 列名 | 字段 | 说明 |
|------|------|------|
| DV Milestone | dv_milestone | 下拉选择 DV0.3/DV0.5/DV0.7/DV1.0 |
| Target Date | target_date | 日期选择器 |
| Status Date | status_date | 显示对应状态的日期 |

### 4.2 TC 状态颜色

```css
.status-open { color: #6b7280; }
.status-coded { color: #3b82f6; }
.status-fail { color: #ef4444; }
.status-pass { color: #22c55e; }
.status-removed { color: #9ca3af; text-decoration: line-through; }
```

### 4.3 CP 表格新增列

| 列名 | 字段 | 说明 |
|------|------|------|
| Priority | priority | 下拉选择 P0/P1/P2 |

### 4.4 批量操作界面

**TC 表格工具栏**:
```
[选择全部] [批量更新状态 ▼] [批量修改 Target Date] [批量修改 DV Milestone]
```

### 4.5 状态变更确认逻辑

**当从 PASS 改为其他状态时**:
```javascript
async function updateStatus(tcId, newStatus) {
    const tc = await getTC(tcId);

    if (tc.status === 'PASS' && newStatus !== 'PASS') {
        // 二次确认
        const confirmed = await showConfirmDialog(
            '确认状态变更',
            `将状态从 PASS 改为 ${newStatus}？完成日期会被重置。`
        );
        if (!confirmed) return;
    }

    // 执行状态更新
    await patch(`/api/tc/${tcId}/status`, { status: newStatus });
}
```

---

## 5. 验收标准

### 5.1 Status 日期记录 (#2)

- [ ] CODED/FAIL/PASS/REMOVED 状态记录日期
- [ ] OPEN 状态不记录日期
- [ ] TC 表格显示 "Status Date" 列
- [ ] PASS → 其他状态有二次确认，提示"完成日期会被重置"

### 5.2 Target Date (#3)

- [ ] TC 表格显示 Target Date 列
- [ ] 支持单个 TC 修改 Target Date
- [ ] 支持批量修改 Target Date

### 5.3 Removed 状态 (#4)

- [ ] Status 下拉框包含 REMOVED 选项
- [ ] REMOVED 状态可转移为 CODED
- [ ] REMOVED 状态的 TC 显示删除线
- [ ] REMOVED 不计入 Total
- [ ] REMOVED 不计入 Pass Rate
- [ ] TC 状态改为 REMOVED 时自动清除与 CP 的关联

### 5.4 批量修改状态 (#4.7)

- [ ] TC 表格显示复选框列
- [ ] 支持全选
- [ ] 支持批量状态更新
- [ ] PASS → 其他状态有二次确认

### 5.5 DV Milestone (#5)

- [ ] TC 表格显示 DV Milestone 列
- [ ] 新建/编辑可选择 DV Milestone
- [ ] 默认值 DV1.0
- [ ] 支持批量修改 DV Milestone

### 5.6 CP Priority (#6)

- [ ] CP 表格显示 Priority 列
- [ ] 新建/编辑可选择 Priority
- [ ] 默认值 P0
- [ ] 支持批量修改 Priority

---

## 6. 开发计划

### 6.1 第一步: 数据库和 API

1. 添加数据库字段
2. 实现 API 接口
3. 实现统计数据逻辑

### 6.2 第二步: 前端界面

1. 添加 TC 表格新列
2. 添加 CP 表格新列
3. 实现批量操作
4. 实现状态确认逻辑

### 6.3 第三步: 测试验证

1. 编写测试用例
2. 执行 API 测试
3. 执行冒烟测试

---

## 7. 相关文档

- 需求文档: `/projects/management/feedbacks/reviewed/tracker_FEATURE_REQUESTS_v0.6.0_20260207.md`
- 开发规范: `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md`
- 测试计划: `docs/REPORTS/tracker_TEST_PLAN.md`
