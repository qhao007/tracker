# CP 覆盖率增强方案

> 目标：TC-CP 模式下，FAIL 状态的 TC 也算覆盖；并能在 UI 区分"全部 PASS 的 100%"和"有 FAIL 的 100%"。
> 计划曲线不修改。

---

## 一、后端改动

### 1.1 `/api/cp` — CP 列表页 (api.py ~1940)

**变更**：
- `passed` → `covered_tc` (status in ('PASS', 'FAIL'))
- 新增 `fail_count`、`pass_count`
- `coverage` = covered_tc / total * 100
- `coverage_detail` 格式调整

```python
# BEFORE
passed = sum(1 for tc in connected_tcs if tc["status"] == "PASS")
coverage = round(passed / total * 100, 1) if total > 0 else 0.0
coverage_detail = f"{passed}/{total}"

# AFTER
covered_tc = sum(1 for tc in connected_tcs if tc["status"] in ('PASS', 'FAIL'))
pass_count = sum(1 for tc in connected_tcs if tc["status"] == 'PASS')
fail_count = sum(1 for tc in connected_tcs if tc["status"] == 'FAIL')
coverage = round(covered_tc / total * 100, 1) if total > 0 else 0.0
if fail_count > 0:
    coverage_detail = f"{covered_tc}/{total} ({fail_count}F)"
else:
    coverage_detail = f"{covered_tc}/{total}"

# 返回字段增加 pass_count, fail_count
"coverage": coverage,
"coverage_detail": coverage_detail,
"pass_count": pass_count,
"fail_count": fail_count,
```

### 1.2 `calculate_current_coverage()` — 快照计算 (api.py ~1384)

**变更**：TC-CP 分支

```python
# BEFORE
pass_tc = sum(1 for tc in connected_tcs if tc[1] == 'PASS')
cp_rate = (pass_tc / total_tc) * 100
if pass_tc > 0:
    covered_cps += 1

# AFTER
covered_tc = sum(1 for tc in connected_tcs if tc[1] in ('PASS', 'FAIL'))
pass_tc = sum(1 for tc in connected_tcs if tc[1] == 'PASS')
fail_tc = sum(1 for tc in connected_tcs if tc[1] == 'FAIL')
cp_rate = (covered_tc / total_tc) * 100
if covered_tc > 0:
    covered_cps += 1

# cp_states 增加 pass_count / fail_count
cp_states[str(cp_id)] = {
    'name': cp_name,
    'coverage_rate': round(cp_rate, 1),
    'linked_tcs': len(linked_tcs),
    'pass_count': pass_tc,
    'fail_count': fail_tc,
}
```

### 1.3 Priority 覆盖率计算 (api.py ~1462)

**变更**：TC-CP 分支，同上逻辑。

```python
# BEFORE
pass_tc = sum(1 for tc in connected_tcs if tc[0] == 'PASS')
cp_rate = (pass_tc / total_tc) * 100
if pass_tc > 0:
    p_covered += 1

# AFTER
covered_tc = sum(1 for tc in connected_tcs if tc[0] in ('PASS', 'FAIL'))
cp_rate = (covered_tc / total_tc) * 100
if covered_tc > 0:
    p_covered += 1
```

### 1.4 `/api/dashboard/stats` (api.py ~5498)

**变更**：TC-CP 分支

```python
# BEFORE
pass_tc = sum(1 for tc in connected_tcs if tc[0] == 'PASS')
cp_rate = (pass_tc / total_tc) * 100

covered_cp = sum(1 for cp in all_cps if any(
    tc[0] == 'PASS' for tc in ...
))

# AFTER
covered_tc = sum(1 for tc in connected_tcs if tc[0] in ('PASS', 'FAIL'))
cp_rate = (covered_tc / total_tc) * 100

covered_cp = sum(1 for cp in all_cps if any(
    tc[0] in ('PASS', 'FAIL') for tc in ...
))
```

### 1.5 `/api/dashboard/coverage-matrix` (api.py ~6194)

**变更**：TC-CP 分支

```python
# BEFORE
pass_tc = sum(1 for tc in connected_tcs if tc[0] == 'PASS')
cp_coverage_rate = round((pass_tc / len(connected_tcs)) * 100, 1)
if pass_tc > 0:
    matrix[feature][priority]['covered'] += 1

# AFTER
covered_tc = sum(1 for tc in connected_tcs if tc[0] in ('PASS', 'FAIL'))
pass_tc = sum(1 for tc in connected_tcs if tc[0] == 'PASS')
fail_tc = sum(1 for tc in connected_tcs if tc[0] == 'FAIL')
cp_coverage_rate = round((covered_tc / len(connected_tcs)) * 100, 1)
if covered_tc > 0:
    matrix[feature][priority]['covered'] += 1

# cp_list 增加 pass_count / fail_count
matrix[feature][priority]['cp_list'].append({
    'id': cp_id,
    'name': cp_name,
    'coverage_rate': cp_coverage_rate,
    'pass_count': pass_tc,
    'fail_count': fail_tc,
})
```

### 1.6 `/api/dashboard/coverage-holes` (api.py ~5937)

**变更**：空洞定义 + 新增 risk 类别

```python
# BEFORE: 空洞 = 有关联TC但 coverage_rate = 0 (即所有TC都不是PASS)
pass_tc = sum(1 for tc in linked_tcs if tc[2] == 'PASS')
coverage_rate = (pass_tc / linked_tc_count) * 100
if coverage_rate > 0:
    continue  # 不是空洞

# AFTER: 空洞 = 有关联TC但 covered_tc = 0 (即所有TC都是CODED/OPEN/REMOVED)
covered_tc = sum(1 for tc in linked_tcs if tc[2] in ('PASS', 'FAIL'))
pass_tc = sum(1 for tc in linked_tcs if tc[2] == 'PASS')
fail_tc = sum(1 for tc in linked_tcs if tc[2] == 'FAIL')
coverage_rate = (covered_tc / linked_tc_count) * 100 if linked_tc_count > 0 else 0

if coverage_rate > 0:
    # 不是空洞，检查是否属于 risk（100%覆盖但有FAIL）
    if coverage_rate == 100 and fail_tc > 0:
        risk.append(hole_entry)
    continue

# hole_entry 增加 pass_count / fail_count
hole_entry = {
    ...,
    'pass_count': pass_tc,
    'fail_count': fail_tc,
}
```

返回结构：
```python
{
    'critical': [...],
    'warning': [...],
    'attention': [...],
    'risk': [...],  # 新增
}
```

### 1.7 导出材料包 `/api/export/project` (api.py ~4705)

**变更**：coverage_matrix 的 covered 计算

```python
# BEFORE: tc.status = 'PASS'
# AFTER: tc.status IN ('PASS', 'FAIL')
```

---

## 二、前端改动

### 2.1 CP 列表页 Badge 颜色 (index.html ~3316)

**变更**：新增橙色 badge 类，区分"有FAIL的100%"

```html
<!-- BEFORE -->
<span class="coverage-badge ${cp.coverage === 100 ? 'bg-green' : cp.coverage > 0 ? 'bg-yellow' : 'bg-red'}">

<!-- AFTER -->
<span class="coverage-badge ${cp.coverage === 100 && cp.fail_count === 0 ? 'bg-green' : cp.coverage === 100 && cp.fail_count > 0 ? 'bg-orange' : cp.coverage > 0 ? 'bg-yellow' : 'bg-red'}">
```

新增 CSS：
```css
.bg-orange { background: #f97316; color: white; }
```

### 2.2 Dashboard Coverage Holes 面板 (dashboard.js)

**变更**：新增 Risk 列

```javascript
// renderHoles 方法增加 risk 列
const { critical, warning, attention, risk } = this.holesData;

container.innerHTML = `
    <div class="holes-kanban">
        ${this.renderHoleColumn('critical', '🔴 Critical', critical)}
        ${this.renderHoleColumn('warning', '🟡 Warning', warning)}
        ${this.renderHoleColumn('attention', '🟡 Attention', attention)}
        ${this.renderHoleColumn('risk', '🟠 At Risk', risk)}
    </div>
`;
```

新增 risk 的样式（橙色边框/背景）。

### 2.3 Dashboard Coverage Matrix 弹窗 (dashboard.js ~820)

**变更**：CP 详情增加状态分布

```javascript
// 在弹窗中显示每个 CP 的 pass/fail 数量
<span style="width: 60px; text-align: right; ...">${cp.coverage_rate}%</span>
// 增加 tooltip 或额外行显示 pass_count / fail_count
```

### 2.4 Dashboard Stats 面板 (dashboard.js ~220)

**变更**：Covered 卡片值不变，但 hover tooltip 或周环比语义需说明新口径。
（当前实现暂不动，因为值本身仍是 covered_cp/total_cp）

---

## 三、测试验证点

1. **CP 列表页**：
   - 全部 PASS 的 CP → 绿色 badge
   - 有 FAIL 但 100% 覆盖 → 橙色 badge
   - 部分覆盖 → 黄色 badge
   - 0% 覆盖 → 红色 badge
   - coverage_detail 显示 `X/Y` 或 `X/Y (NF)`

2. **Dashboard Stats**：
   - covered_cp 计算正确（PASS+FAIL）
   - coverage_rate 计算正确

3. **Coverage Matrix**：
   - covered 计数正确
   - weak_areas 判定正确

4. **Coverage Holes**：
   - Critical/Warning/Attention 只包含没有 PASS/FAIL 的 CP
   - Risk 列显示 100% 覆盖但有 FAIL 的 CP

5. **导出材料包**：
   - coverage_matrix 的 covered 值正确

6. **计划曲线**：不变，验证不受影响

7. **FC-CP 模式**：完全不受影响

---

## 四、改动统计

| 文件 | 改动位置数 | 说明 |
|------|-----------|------|
| `dev/app/api.py` | 7 处 | CP列表、current_coverage、priority_coverage、dashboard_stats、coverage_matrix、coverage_holes、export_project |
| `dev/index.html` | 2 处 | Badge颜色逻辑 + CSS |
| `dev/static/js/dashboard.js` | 3 处 | Holes面板、Matrix弹窗、样式 |
| **总计** | **~12 处** | |

---

*方案完成，等待确认后进入开发。*
