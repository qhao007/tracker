# Tracker BugLog

> **版本**: v0.6.0 | **最后更新**: 2026-02-08 | **状态**: 开发中

---

## 目录

1. [Bug 列表](#1-bug-列表)
2. [功能增强](#2-功能增强)
3. [测试用例](#3-测试用例)
4. [修复记录](#4-修复记录)

---

## 1. Bug 列表

### BUG-001: 项目切换数据丢失

| 属性 | 值 |
|------|-----|
| **严重性** | Critical |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 切换项目后，当前项目数据丢失，页面显示空白或错误数据。

**原因**: 项目切换时未正确加载新项目数据。

**修复方案**:
- 在 `switchProject()` 函数中确保数据加载完成后再渲染
- 添加 `await loadProjectData()` 等待数据加载

**验证**: 项目切换后数据正常显示。

---

### BUG-002: 项目切换数据不刷新

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 在 Cover Points 和 Test Cases 标签之间切换后，列表数据不刷新。

**原因**: 切换标签时使用了缓存数据，未重新请求 API。

**修复方案**:
- 切换标签时调用 `renderCP()` 或 `renderTC()` 重新渲染
- 确保每次切换都从 `coverPoints` 或 `testCases` 数组重新渲染

**验证**: 切换标签后数据正确刷新。

---

### BUG-003: CP 列表不刷新

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 添加或删除 Cover Point 后，列表未自动刷新。

**原因**: 未在操作完成后调用 `renderCP()`。

**修复方案**:
- 添加/删除 CP 操作完成后调用 `renderCP()` 刷新列表

**验证**: 添加/删除 CP 后列表正确刷新。

---

### BUG-004: TC 列表不刷新

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 添加或删除 Test Case 后，列表未自动刷新。

**原因**: 未在操作完成后调用 `renderTC()`。

**修复方案**:
- 添加/删除 TC 操作完成后调用 `renderTC()` 刷新列表

**验证**: 添加/删除 TC 后列表正确刷新。

---

### BUG-005: 状态更新失败

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 更新 Test Case 状态时，API 调用失败或状态未更新。

**原因**: API 调用路径错误或参数不正确。

**修复方案**:
- 修复 `updateTCStatus()` 函数中的 API 调用
- 使用正确的路径 `/api/tc/{id}/status`

**验证**: 状态更新成功，UI 正确显示新状态。

---

### BUG-006: 数据验证缺失

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 提交表单时缺少必填字段验证，导致无效数据入库。

**原因**: 前端和后端均缺少必填字段校验。

**修复方案**:
- 添加前端表单验证（`required` 属性）
- 添加后端必填字段检查

**验证**: 必填字段为空时显示错误提示。

---

### BUG-007: 刷新后项目选择重置

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 页面刷新后，项目选择器重置为默认选项。

**原因**: 未使用 `localStorage` 保存用户选择的项目。

**修复方案**:
- 页面加载时从 `localStorage` 恢复上次选择的项目
- 项目切换时保存到 `localStorage`

**验证**: 刷新页面后项目选择保持。

---

### BUG-008: EX5 项目 TC 数据无法加载

| 属性 | 值 |
|------|-----|
| **严重性** | Critical |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-04 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: EX5 项目（以及其他旧项目）切换后 Test Cases 列表显示 500 错误。

**原因**: 旧项目数据库缺少 `tc_cp_connections` 表。

**修复方案**:
- 数据库初始化时创建缺失的表
- API 中使用 `CREATE TABLE IF NOT EXISTS`

**验证**: EX5 项目 TC 列表正常显示，无 500 错误。

---

### BUG-009: TC 状态无法更新

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-04 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 选择新状态后，Test Case 状态未更新，UI 显示旧状态。

**原因**: 状态更新后未重新渲染 TC 列表。

**修复方案**:
- 状态更新成功后调用 `renderTC()` 刷新列表
- 更新顶部统计数据

**验证**: 状态更新后 UI 立即显示新状态。

---

### BUG-010: 删除功能失效

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-04 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-04 |
| **修复人** | 小栗子 |

**描述**: 点击删除按钮后，CP/TC 未从列表中移除，或删除失败。

**原因**: API 调用失败或成功后未刷新列表。

**修复方案**:
- 修复删除 API 调用
- 删除成功后调用 `renderCP()` 或 `renderTC()` 刷新

**验证**: 删除后列表正确更新。

---

### BUG-011: update_status API 查询不存在的列

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 调用 `/api/tc/{id}/status` 更新状态时返回 500 错误。

**原因**: `update_status` 函数中查询了 `SELECT status, connected_cps FROM test_case`，但 `test_case` 表不存在 `connected_cps` 列（关联数据存储在单独的 `tc_cp_connections` 表中）。

**修复方案**:
- 移除 `connected_cps` 列查询
- 分别查询 `status` 和关联的 CP

**验证**: 状态更新 API 正常工作。

---

### BUG-012: get_testcases 返回不存在的字段

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 获取 TC 列表时 API 返回 500 错误，IndexError。

**原因**: `get_testcases` 函数引用了 `row['priority']` 和 `row['completed_date']` 字段，但 v0.6.0 数据库中这些字段已被移除。

**修复方案**:
- 移除 `priority` 和 `completed_date` 字段
- 添加新的日期字段: `coded_date`, `fail_date`, `pass_date`, `removed_date`, `target_date`

**验证**: TC 列表 API 正常工作。

---

### BUG-013: 测试数据库缺少 v0.6.0 新字段

| 属性 | 值 |
|------|-----|
| **严重性** | Critical |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 添加 Cover Point 或 Test Case 时返回 500 错误。

**原因**: 测试数据库 (test_data/) 中的表缺少 v0.6.0 新增字段。

**修复方案**:
- 创建修复脚本，遍历所有测试数据库
- 添加缺失字段: `priority`, `dv_milestone`, `coded_date`, `fail_date`, `pass_date`, `removed_date`, `target_date`

**验证**: 添加 CP/TC 功能恢复正常。

---

### BUG-014: 前端界面未同步 v0.6.0 新字段

| 属性 | 值 |
|------|-----|
| **严重性** | Critical |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 前端界面缺少 v0.6.0 新功能：
- CP 表格缺少 Priority 列
- TC 表格缺少 DV Milestone、Target Date、Status Date 列
- 状态选择缺少 REMOVED 选项
- Modal 表单缺少 DV Milestone、Target Date、Priority 字段
- 编辑功能失效

**修复方案**:
1. 更新 CP 表格表头，添加 Priority 列
2. 更新 TC 表格表头，添加 DV Milestone、Target Date、Status Date 列
3. 状态过滤下拉添加 REMOVED 选项
4. CP Modal 添加 Priority 下拉字段
5. TC Modal 添加 DV Milestone 和 Target Date 字段
6. 更新 renderCP 和 renderTC 函数显示新字段
7. 添加 Priority 徽章 CSS 样式 (P0=红, P1=橙, P2=绿)

**验证**: 前端界面恢复正常，可正常添加/编辑 CP/TC。

---

### BUG-016: PASS → 其他状态缺少二次确认

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 规格书要求当状态从 PASS 改为其他状态时，需要二次确认并提示"完成日期会被重置"。

**修复方案**:
在 `updateTCStatus()` 函数中添加确认逻辑：
```javascript
const tc = testCases.find(t => t.id === id);
if (tc && tc.status === 'PASS' && newStatus !== 'PASS') {
    const confirmed = confirm('确认状态变更\n\n将状态从 PASS 改为 ' + newStatus + '？\n完成日期会被重置。');
    if (!confirmed) return;
}
```

**验证**: PASS → 其他状态时弹出确认对话框。

---

### BUG-017: DV Milestone 默认值不正确

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 前端 Modal 中 DV Milestone 下拉框的默认选项是 "-- 选择 --" (空值)，而不是 DV1.0。

**修复方案**:
1. 将 TC Modal 中的 DV Milestone 下拉框默认值改为 DV1.0
2. 更新编辑时的默认值逻辑：`tc.dv_milestone || 'DV1.0'`

**验证**: 新建 TC 时 DV Milestone 默认值为 DV1.0。

---

### BUG-018: TC详情API返回非JSON

| 属性 | 值 |
|------|-----|
| **严重性** | Critical |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 调用 `GET /api/tc/{id}` API 返回 HTML 404 页面而非 JSON 格式的 TC 详情。

**原因**: API 端点不存在，`GET /api/tc/{id}` 未实现。

**修复方案**:
1. 添加 `GET /api/tc/<int:tc_id>` 端点实现
2. 返回 TC 详情 JSON，包含所有字段和关联 CP 列表

**验证**: TC 详情 API 返回正确的 JSON 格式数据。

---

### BUG-019: CP Priority 无法更新

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 调用 `PUT /api/cp/{id}` 更新 Cover Point 的 priority 字段时，值始终为默认的 P0，无法改为其他值。

**原因**: 更新逻辑中使用了 `data.get('priority', 'P0')`，如果请求体未包含 priority 字段，会被重置为默认值 P0。

**修复方案**:
```python
# 修复前 - 错误
new_priority = data.get('priority', 'P0')

# 修复后 - 正确
cursor.execute('SELECT priority FROM cover_point WHERE id=?', (cp_id,))
current = cursor.fetchone()
current_priority = current['priority'] if current else 'P0'
new_priority = data.get('priority', current_priority)
```

**验证**: 更新 CP 其他字段时 priority 保持原值，指定 priority 时正确更新。

---

### BUG-020: CP详情查询API缺失

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |

**描述**: 调用 `GET /api/cp/{id}` API 返回 404 错误，无法查询单个 Cover Point 详情。

**原因**: API 端点不存在。

**修复方案**:
1. 添加 `GET /api/cp/<int:cp_id>` 端点实现
2. 返回 CP 详情 JSON，包含所有字段

**验证**: CP 详情 API 返回正确的 JSON 格式数据。

---

### BUG-021: 开发版备份功能点击后显示失败

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-08 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-08 |
| **修复人** | 小栗子 |
| **影响版本** | dev |

**描述**: 在开发版中点击"💾 导出备份"按钮后，提示备份失败。

**原因分析**:
- API `POST /api/projects/{id}/archive` 将备份文件写入 `archives/{filename}`
- dev 版本启动时 `archives/` 目录不存在
- Flask 无法创建子目录，导致文件写入失败

**修复方案**:
在 `api.py` 的 `archive_project` 函数中，写入文件前检查并创建 `archives/` 目录：

```python
archives_dir = 'archives'
os.makedirs(archives_dir, exist_ok=True)  # 确保 archives 目录存在
filepath = os.path.join(archives_dir, filename)
```

**验证**: 备份功能现在可以正常工作，archives 目录会自动创建。

---

## 2. 功能增强

### FEAT-001: CP 覆盖率计算

| 属性 | 值 |
|------|-----|
| **优先级** | P1 |
| **状态** | ✅ 已实现 |
| **报告人** | 小栗子 |
| **实现日期** | 2026-02-04 |
| **实现人** | 小栗子 |

**描述**: 计算每个 Cover Point 关联的 Test Cases 中 PASS 状态的百分比。

**计算规则**:

| 关联 TC 状态 | 覆盖率 |
|-------------|--------|
| 全部 PASS | 100% |
| 部分 PASS | PASS 数量 / 关联总数 × 100% |
| 无关联 TC | 0% |

**UI 显示**:
- 🟢 绿色 100%
- 🟡 黄色 部分
- ⚪ 灰色 0%

**验证**: 覆盖率计算正确，UI 显示正确。

---

### BUG-022: CP 列表界面显示批量操作按钮

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-09 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-09 |
| **修复人** | 小栗子 |

**描述**: 在 Cover Points 列表界面，批量更新状态、批量修改 Target Date、批量修改 DV Milestone 三个按钮仍然显示。这些按钮是针对 Test Cases 的批量操作，不应在 CP 列表界面显示。

**复现步骤**:
1. 进入任意项目
2. 切换到 Cover Points 列表（默认展示 CP）
3. 工具栏显示三个不应存在的批量操作按钮

**修复方案**:
从 `index.html` 的 `cpPanel` 工具栏中移除以下三个按钮：
- 批量更新状态
- 批量修改 Target Date
- 批量修改 DV Milestone

这三个按钮保留在 `tcPanel` 工具栏中。

**验证**: CP 列表界面不再显示批量操作按钮。

---

### BUG-026: VERSION 文件读取失败导致版本号显示为默认值

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: 正式版和开发版前端界面显示版本号为 "v1.0.0"，实际应为 "v0.6.1"。

**问题分析**:
- VERSION 文件内容为 `v0.6.1`（无 `VERSION=` 前缀）
- `get_version()` 函数期望格式为 `VERSION=v0.6.1`
- 不匹配导致使用默认值 `1.0.0`

**修复方案**:
修改 `dev/app/api.py` 的 `get_version()` 函数，兼容两种格式：

```python
for line in lines:
    line = line.strip()
    if '=' in line:
        key, value = line.split('=', 1)
        if key == 'VERSION':
            version = value
        elif key == 'RELEASE_DATE':
            release_date = value
    elif line:
        # 兼容只有版本号的格式，如 "v0.6.1"
        version = line
```

**验证**:
- 正式版 (8080): 显示 v0.6.1 ✅
- 开发版 (8081): 显示 v0.6.1 ✅

**Git 提交**: `ce003fe fix: 修复 VERSION 文件读取逻辑`

---

### BUG-027: 展开所有 CP 详情时 TC 数据不加载

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: 点击"收起 ▼"按钮展开所有 CP 详情时，关联的 TC 列表为空。

**原因**: `toggleAllCPDetails()` 函数只设置了行的 `display` 属性，没有调用 `loadCPTcConnections(cpId)` 异步加载 TC 数据。

**修复方案**:
修改 `index.html` 中的 `toggleAllCPDetails()` 函数，展开时遍历所有详情行并加载 TC 数据：

```javascript
async function toggleAllCPDetails() {
    // ...
    } else {
        // 展开所有 - 需要加载每个 CP 的关联 TC
        for (const row of allDetails) {
            row.style.display = 'table-row';
            const cpId = row.id.replace('cp-detail-', '');
            await loadCPTcConnections(cpId);
            // ...
        }
        btn.textContent = '收起 ▼';
    }
}
```

**验证**: 展开所有 CP 详情后，关联 TC 列表正确显示。

**Git 提交**: `0896f5a fix: 展开所有CP详情时加载TC数据`

---

### BUG-028: TC 过滤重置后列表不刷新

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: 点击"重置"按钮后，TC 过滤下拉框被清空，但列表未重新渲染。

**原因**: `resetTCFilter()` 函数重置了所有下拉框后，没有调用 `renderTC()` 刷新列表。

**修复方案**:
在 `resetTCFilter()` 函数末尾添加 `renderTC()` 调用。

**验证**: 点击重置按钮后，TC 列表立即刷新显示所有数据。

**Git 提交**: `0896f5a fix: 重置TC过滤后刷新列表`

---

### BUG-029: TC 过滤重置代码存在无效语句

| 属性 | 值 |
|------|-----|
| **严重性** | Low |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: `resetTCFilter()` 函数中存在无意义的代码 `document.getElementById('xxx').selectedOptions.length`，读取后未使用。

**修复方案**: 删除无效代码行。

**Git 提交**: `0896f5a fix: 删除无效代码`

---

### v0.6.2 修复汇总

| Bug ID | 描述 | 修复日期 |
|--------|------|----------|
| BUG-027 | 展开所有 CP 详情时 TC 数据不加载 | 2026-02-10 |
| BUG-028 | TC 过滤重置后列表不刷新 | 2026-02-10 |
| BUG-029 | TC 过滤重置代码存在无效语句 | 2026-02-10 |
| BUG-030 | CP 详情关联 TC 显示错误 | 2026-02-10 |
| BUG-031 | TC Priority 过滤不需要 | 2026-02-10 |
| BUG-032 | TC Owner/Category 过滤选项不动态加载 | 2026-02-10 |
| BUG-033 | TC Status/DV Milestone 需要单选下拉框 | 2026-02-10 |
| BUG-034 | TC Status/DV Milestone 缺少全部选项 | 2026-02-10 |
| BUG-035 | TC DV Milestone 过滤选项不动态加载 | 2026-02-10 |
| BUG-036 | projectSelector ID 拼写错误 | 2026-02-10 |

---

### BUG-036: projectSelector ID 拼写错误

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: 点击 CP 详情后显示"加载失败"，API 返回 404。

**原因**: `loadCPTcConnections()` 函数中使用 `document.getElementById('projectSelect')` 获取项目ID，但实际元素的ID是 `projectSelector'`。

**修复方案**:
将 `projectSelect` 改为 `projectSelector'`。

```javascript
// 修复前
const projectId = document.getElementById('projectSelect')?.value;

// 修复后
const projectId = document.getElementById('projectSelector')?.value;
```

**验证**: 点击 CP 详情后正确显示关联的 Test Case。

**Git 提交**: `8b44006 fix: 修复 projectSelector ID 拼写错误`

---

### BUG-030: CP 详情关联 TC 显示错误

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: 点击 CP 详情后，无法正确显示关联的 Test Case。

**原因**: `loadCPTcConnections()` 函数调用 API 时没有传递 `project_id` 参数，导致 API 无法找到正确的项目数据库。

**修复方案**:
修改 `loadCPTcConnections()` 函数，传递 `project_id` 参数：

```javascript
const projectId = document.getElementById('projectSelect')?.value;
const res = await fetch(`${API_BASE}/cp/${cpId}/tcs${projectId ? '?project_id=' + projectId : ''}`);
```

**验证**: 点击 CP 详情后正确显示关联的 Test Case。

**Git 提交**: `cf66a5a fix: 修复TC过滤和CP关联TC显示Bug`

---

### BUG-031: TC Priority 过滤不需要

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: TC 过滤面板中包含 Priority 过滤选项，但 Test Case 没有 priority 字段。

**原因**: 规格书要求 CP 有 priority 过滤，但 TC 没有。

**修复方案**:
从 TC 过滤面板中移除 Priority 过滤选项。

**验证**: TC 过滤面板不再显示 Priority 选项。

**Git 提交**: `cf66a5a fix: 修复TC过滤和CP关联TC显示Bug`

---

### BUG-032: TC Owner/Category 过滤选项不动态加载

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: Owner 和 Category 过滤下拉菜单只显示"全部"选项，没有加载 TC 列表中的实际数据。

**修复方案**:
添加 `loadTCFilterOptions()` 函数，动态从 TC 列表中提取唯一的 Owner 和 Category 值：

```javascript
function loadTCFilterOptions() {
    const owners = [...new Set(testCases.map(tc => tc.owner).filter(o => o))].sort();
    const categories = [...new Set(testCases.map(tc => tc.category).filter(c => c))].sort();
    // 填充下拉框...
}
```

**验证**: Owner 和 Category 下拉菜单正确显示 TC 列表中的实际数据。

**Git 提交**: `cf66a5a fix: 修复TC过滤和CP关联TC显示Bug`

---

### BUG-033: TC Status/DV Milestone 需要单选下拉框

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: Status 和 DV Milestone 过滤使用多选 (multiple) 下拉框，体验不好，应该使用单选下拉框。

**修复方案**:
将 `multiple` 属性移除，改为单选下拉框。

**验证**: Status 和 DV Milestone 过滤使用单选下拉框。

**Git 提交**: `cf66a5a fix: 修复TC过滤和CP关联TC显示Bug`

---

### BUG-034: TC Status/DV Milestone 缺少全部选项

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: Status 和 DV Milestone 过滤下拉菜单缺少"全部"选项。

**修复方案**:
在 Status 和 DV Milestone 下拉菜单中添加"全部"选项。

**验证**: Status 和 DV Milestone 下拉菜单包含"全部"选项。

**Git 提交**: `cf66a5a fix: 修复TC过滤和CP关联TC显示Bug`

---

### BUG-035: TC DV Milestone 过滤选项不动态加载

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-10 |
| **报告人** | 用户 |
| **修复日期** | 2026-02-10 |
| **修复人** | 小栗子 |

**描述**: DV Milestone 过滤下拉菜单使用硬编码的 DV1.0-DV5.0 选项，没有加载 TC 列表中的实际数据。

**修复方案**:
在 `loadTCFilterOptions()` 函数中动态加载 DV Milestone 选项。

**验证**: DV Milestone 下拉菜单正确显示 TC 列表中的实际 DV Milestone 值。

**Git 提交**: `cf66a5a fix: 修复TC过滤和CP关联TC显示Bug`

---

### BUG-041: 导入模板下载缺少 send_file 导入

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-16 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-16 |
| **修复人** | 小栗子 |

**描述**: 访问 `/api/import/template` 端点时返回 500 错误，提示 `NameError: name 'send_file' is not defined`。

**原因**: `app/api.py` 中使用了 `send_file` 函数但未在文件头部导入。

**修复方案**:
在 `from flask import` 语句中添加 `send_file` 导入。

**验证**: 模板下载 API 正常返回 Excel 文件。

**Git 提交**: `dc221a7 fix: 修复导入导出功能多个bug`

---

### BUG-042: CSV 导入编码问题

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-16 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-16 |
| **修复人** | 小栗子 |

**描述**: 导入 CSV 文件时失败，错误信息 `iterator should return strings, not bytes`。

**原因**: 使用 `csv.reader(io_module.BytesIO(file_content))` 时 BytesIO 不支持文本模式。

**修复方案**:
1. 先将 base64 解码后的 bytes 转为 string: `file_content.decode('utf-8')`
2. 使用 `csv.reader(io.StringIO(...))` 处理文本

**验证**: CSV 导入功能正常工作。

**Git 提交**: `dc221a7 fix: 修复导入导出功能多个bug`

---

### BUG-043: CSV 导入行索引错误

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-16 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-16 |
| **修复人** | 小栗子 |

**描述**: CSV 导入时报错 `list index out of range`。

**原因**: header_map 使用 0-based 索引，但代码中混用了 0-based 和 1-based 索引。

**修复方案**:
统一使用 0-based 索引：`header_map[header.strip()] = idx`（不再 +1）

**验证**: CSV 多行导入正常。

**Git 提交**: `dc221a7 fix: 修复导入导出功能多个bug`

---

### BUG-044: Excel 导入报错 'NoneType' object is not subscriptable

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-16 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-16 |
| **修复人** | 小栗子 |

**描述**: 导入 Excel (.xlsx) 文件时报错 `'NoneType' object is not subscriptable`。

**原因**: openpyxl 版本兼容性问题，`Workbook(io.BytesIO(...))` 不能正确加载 Excel 文件。

**修复方案**: 
1. 使用 `load_workbook` 配合临时文件方式加载 Excel
2. 统一使用 0-based 索引读取 header_map，然后 +1 转换为 Excel 的 1-based 索引

**验证**: CP/TC Excel 导入功能正常工作。

**Git 提交**: `5f4b37e fix: 修复导入导出功能所有bug`

---

### BUG-045: TC 导入代码有重复块

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-16 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-16 |
| **修复人** | 小栗子 |

**描述**: `import_tc` 函数中存在重复的代码块，导致逻辑混乱。

**修复方案**: 重写整个 `import_tc` 函数，删除重复代码块，统一处理逻辑。

**验证**: TC 导入功能正常工作。

**Git 提交**: `5f4b37e fix: 修复导入导出功能所有bug`

### BUG-046: CSV 导出返回 502 Bad Gateway

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-18 |
| **报告人** | 独立第三方测试 |
| **修复日期** | 2026-02-18 |
| **修复人** | 小栗子 |

**描述**: 调用 `/api/export?project_id=130&type=cp&format=csv` 或 `tc&format=csv` 返回 502 Bad Gateway 错误。

**根因分析**:
1. HTTP Header `Content-Disposition` 中的中文文件名未进行 URL 编码
2. gunicorn 无法解析包含中文的 HTTP Header，返回 502
3. `static_files` catch-all 路由覆盖了 `/api/export` 路由

**修复方案**:
1. 添加 `from urllib.parse import quote` 导入
2. 修改 CSV Header: `filename={quote(filename)}` 进行 URL 编码
3. 修复 `static_files` 路由，排除 `/api/` 路径

**验证**:
- project_id=2, 130 CP/TC CSV 导出均返回 200
- API 测试 130/130 通过

**Git 提交**: `15ca1e2 fix: 修复 CSV 导出 HTTP Header 中文编码问题`

### BUG-047: 项目 ID 生成逻辑错误导致数据冲突

| 属性 | 值 |
|------|-----|
| **严重性** | Critical |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-22 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-22 |
| **修复人** | 小栗子 |

**描述**: 创建项目时使用 `len(projects) + 1` 作为新项目 ID，而非 `max(id) + 1`，导致多项目共享同一 ID。2026-02-21 23:03 在生产环境创建了名为 "test" 的项目，错误地使用了 ID=3，与已有的 EX5 项目（ID=3）产生冲突。

**影响范围**: 
- 生产环境 `user_data/projects.json` 包含重复 ID
- API 返回冲突的项目列表
- 数据完整性受损

**根因分析**:
- `create_project()` 函数位于 `dev/app/api.py`
- ID 生成逻辑: `"id": len(projects) + 1`
- 当 projects 列表长度为 2 时，新项目 ID = 2 + 1 = 3
- 如果已有 ID=3 的项目，则产生冲突

**修复方案**:
```python
# 修改前
"id": len(projects) + 1,

# 修改后
"id": max([p["id"] for p in projects], default=0) + 1,
```

**验证**: 
- 生产环境 projects.json 已清理冲突数据
- API 返回正确的项目列表（无重复 ID）

**Git 提交**: `c139a60 fix: 修复项目 ID 生成逻辑，避免 ID 冲突`

### BUG-048: sqlite3.Row 不支持 get() 方法导致 API 500 错误

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-22 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-22 |
| **修复人** | 小栗子 |

**描述**: 调用 `/api/tc?project_id=2` 和 `/api/cp?project_id=2` 查询列表时返回 500 错误。

**错误信息**:
```
AttributeError: 'sqlite3.Row' object has no attribute 'get'
```

**根因分析**:
- 位置: `dev/app/api.py` 第 677 行和 1035 行
- 代码: `"created_by": row.get("created_by", "")`
- SQLite 的 `row` 对象不支持 `.get()` 方法，需要转换为 dict

**修复方案**:
```python
# 修改前
"created_by": row.get("created_by", ""),

# 修改后
"created_by": dict(row).get("created_by", ""),
```

**验证**: 
- TC 列表和 CP 列表 API 正常返回 200
- created_by 字段正确显示

**Git 提交**: `cdc0bcc fix: 修复 created_by 字段查询问题`

## 3. 测试用例

### 测试覆盖矩阵

| Bug ID | 描述 | 测试用例 | 状态 |
|--------|------|----------|------|
| BUG-008 | EX5 项目 TC 数据加载 | `切换项目后 Test Cases 应该正常显示` | ✅ PASS |
| BUG-008 | EX5 项目 TC 数据加载 | `EX5 项目 TC 数据加载（模拟 EX5 场景）` | ✅ PASS |
| BUG-009 | TC 状态更新 | `状态选择后应该更新为新状态` | ✅ PASS |
| BUG-009 | TC 状态更新 | `状态更新后统计数据应同步` | ✅ PASS |
| BUG-010 | 删除功能 | `删除 CP 后列表应更新` | ⚠️ 待验证 |
| BUG-010 | 删除功能 | `删除 TC 后列表应更新` | ⚠️ 待验证 |
| FEAT-001 | CP 覆盖率计算 | `CP 列表应显示覆盖率` | ⚠️ 待验证 |
| FEAT-001 | CP 覆盖率计算 | `覆盖率颜色正确显示` | ⚠️ 待验证 |
| BUG-002 | 项目切换数据刷新 | `项目切换后数据刷新` | ⚠️ 待验证 |
| BUG-007 | 刷新后项目保持 | `页面刷新后项目选择保持` | ⚠️ 待验证 |

### 运行测试

```bash
# API 测试
cd dev && PYTHONPATH=. python3 -m pytest tests/test_api.py -v

# Playwright 冒烟测试
cd dev && npx playwright test tests/test_smoke.spec.ts --project=firefox

# BugLog 回归测试
cd dev && npx playwright test tests/tracker.spec.ts --project=firefox
```

---

## 4. 修复记录

### v0.3 修复汇总

| Bug ID | 描述 | 修复版本 | 修复日期 |
|--------|------|----------|----------|
| BUG-001 | 项目切换数据丢失 | v0.3 | 2026-02-04 |
| BUG-002 | 项目切换数据不刷新 | v0.3 | 2026-02-04 |
| BUG-003 | CP 列表不刷新 | v0.3 | 2026-02-04 |
| BUG-004 | TC 列表不刷新 | v0.3 | 2026-02-04 |
| BUG-005 | 状态更新失败 | v0.3 | 2026-02-04 |
| BUG-006 | 数据验证缺失 | v0.3 | 2026-02-04 |
| BUG-007 | 刷新后项目选择重置 | v0.3 | 2026-02-04 |
| BUG-008 | EX5 项目 TC 数据无法加载 | v0.3 | 2026-02-04 |
| BUG-009 | TC 状态无法更新 | v0.3 | 2026-02-04 |
| BUG-010 | 删除功能失效 | v0.3 | 2026-02-04 |

### v0.6.0 修复汇总

| Bug ID | 描述 | 修复版本 | 修复日期 |
|--------|------|----------|----------|
| BUG-011 | update_status API 查询不存在的列 | v0.6.0 | 2026-02-08 |
| BUG-012 | get_testcases 返回不存在的字段 | v0.6.0 | 2026-02-08 |
| BUG-013 | 测试数据库缺少 v0.6.0 新字段 | v0.6.0 | 2026-02-08 |
| BUG-014 | 前端界面未同步 v0.6.0 新字段 | v0.6.0 | 2026-02-08 |
| BUG-015 | 批量修改功能缺失 | v0.6.0 | 2026-02-08 |
| BUG-016 | PASS → 其他状态缺少二次确认 | v0.6.0 | 2026-02-08 |
| BUG-017 | DV Milestone 默认值不正确 | v0.6.0 | 2026-02-08 |
| BUG-018 | TC详情API返回非JSON | v0.6.0 | 2026-02-08 |
| BUG-019 | CP Priority 无法更新 | v0.6.0 | 2026-02-08 |
| BUG-020 | CP详情查询API缺失 | v0.6.0 | 2026-02-08 |

---

## 2. 功能增强

### FEAT-002: 备份恢复自定义路径

| 属性 | 值 |
|------|-----|
| **状态** | 待开发 |
| **优先级** | Medium |
| **目标版本** | v0.6.1 |
| **提出日期** | 2026-02-08 |
| **提出人** | 用户 |

**描述**: 当前备份恢复功能只能搜索默认 `archives/` 目录，用户无法选择其他位置的备份文件。

**建议方案**:
- 恢复时提供"选择备份文件"按钮，弹出文件选择对话框
- 支持选择本地 JSON 备份文件
- API 新增 `POST /api/projects/restore/upload` 支持文件上传
- 保留现有 `POST /api/projects/restore` 按文件名恢复的功能

**影响范围**:
- 前端：备份恢复弹窗增加文件上传功能
- 后端：新增文件上传 API 端点
- 用例：用户可以恢复任意位置的备份文件

---

## 附录

### 相关文件

| 文件 | 说明 |
|------|------|
| `tests/tracker.spec.ts` | BugLog 回归测试 |
| `tests/test_smoke.spec.ts` | Playwright 冒烟测试 |
| `tests/test_api.py` | API 单元测试 |

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-02-07 | 初始 BugLog 文档 |
| v1.1 | 2026-02-07 | 转换为 Markdown 格式 |
| v1.2 | 2026-02-08 | 添加 v0.6.0 修复记录 (BUG-011, BUG-012) |
| v1.3 | 2026-02-08 | 添加 BUG-013 测试数据库字段修复 |
| v1.4 | 2026-02-08 | 添加 BUG-014 前端界面同步修复 |
| v1.5 | 2026-02-08 | 添加 BUG-015, BUG-016, BUG-017 |
| v1.6 | 2026-02-08 | 修复 BUG-016, BUG-017 |
| v1.7 | 2026-02-08 | 添加 BUG-018, BUG-019, BUG-020 |
| v1.8 | 2026-02-08 | 修复 BUG-021 备份功能失败；添加 FEAT-002 备份恢复自定义路径 |
| v1.9 | 2026-02-09 | 修复 BUG-022 CP列表显示批量操作按钮 |
| v2.0 | 2026-02-10 | 修复 BUG-026 VERSION 文件读取失败 |
| v2.1 | 2026-02-16 | 修复 v0.7.0 导入导出功能 bug (BUEG-041~044) |

### BUG-049: TC/CP 更新 API 缺少权限控制

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-22 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-22 |
| **修复人** | 小栗子 |

**描述**: `/api/tc/<id>` PUT 和 `/api/cp/<id>` PUT 缺少权限控制，guest 用户可以调用但应该被拒绝。

**修复方案**: 添加 `@guest_required` 装饰器。

**验证**: 6/6 API 权限测试通过。

**Git 提交**: `ddeecf3 fix: 添加 RBAC 权限控制`

### BUG-050: TC/CP 删除 API 缺少权限控制

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-22 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-22 |
| **修复人** | 小栗子 |

**描述**: `/api/tc/<id>` DELETE 和 `/api/cp/<id>` DELETE 缺少权限控制。

**修复方案**: 添加 `@guest_required` 装饰器。

**验证**: 6/6 API 权限测试通过。

**Git 提交**: `ddeecf3 fix: 添加 RBAC 权限控制`

### BUG-052: 前端未根据角色控制按钮显示

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-02-22 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-02-22 |
| **修复人** | 小栗子 |

**描述**: 所有登录用户都能看到用户管理按钮，未根据角色控制。

**修复方案**: 在 `updateUIForLoggedIn()` 中添加角色检查，仅 admin 可见用户管理按钮。

**验证**: 2/2 前端权限测试通过。

**Git 提交**: `ddeecf3 fix: 添加 RBAC 权限控制`

---

## BUG-053: guest 删除操作无错误提示
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: guest 用户点击删除按钮时，无法删除但没有弹出错误提示（不像编辑操作会显示 forbidden 对话框）

**根本原因**: 前端 deleteTC/deleteCP 函数未处理 403 响应

**修复方案**: 
```javascript
// 添加 res.ok 检查
const res = await fetch(...);
if (!res.ok) {
    const data = await res.json();
    alert(data.message || '删除失败');
    return;
}
```

---

## BUG-054: user 角色无法创建 TC/CP
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: user 角色登录后，点击添加 TC/CP，弹出 "unauthorized" 错误

**根本原因**: 前端 saveCP/saveTC 的 fetch 请求缺少 `credentials: 'include'`，导致 cookie 未发送，服务器认为是未登录状态

**修复方案**: 
```javascript
// 添加 credentials: 'include'
const res = await fetch(`/api/cp${id ? '/'+id : ''}`, { 
    method: id ? 'PUT' : 'POST', 
    headers: {'Content-Type': 'application/json'}, 
    body: JSON.stringify(data), 
    credentials: 'include'  // 添加这行
});
```

**Git 提交**: dc429b2

## BUG-055: 刷新页面间歇性 401 错误
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: 登录后刷新浏览器，偶尔会退出登录需要重新登录

**根本原因**: 
多层问题叠加：
1. Flask 默认 session 存储在进程内存中，多 worker 时请求分发到不同 worker
2. SECRET_KEY 每次服务启动时生成新的随机值，导致 session 签名失效
3. 前端 fetch 请求缺少 credentials: 'include'

**修复方案**: 
1. 使用 Flask-Session 文件存储（基础支持）
2. 使用 gevent worker 替代 sync worker（核心修复 - 协程模型避免多进程）
3. 使用固定 SECRET_KEY 确保 session 签名一致
4. 添加全局 fetch 包装器自动发送 credentials

**Git 提交**: 660d030

---

## BUG-057: guest 角色可以使用导入/导出/批量操作功能
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: guest 角色可以使用导入、导出、批量操作功能，但需求规格书要求禁止

**根本原因**: 
1. 后端：导入/导出/批量操作 API 缺少 @guest_required 装饰器
2. 前端：相关按钮没有根据角色隐藏

**修复方案**: 
1. 后端：为以下 API 添加 @guest_required 装饰器
   - /api/tc/batch/status
   - /api/tc/batch/target_date
   - /api/tc/batch/dv_milestone
   - /api/cp/batch/priority
   - /api/import/template
   - /api/import
   - /api/export

2. 前端：隐藏 guest 角色的导入/导出/批量操作按钮

**Git 提交**: 6342d8f

---

## BUG-058: CP/TC 详情 API 未返回 created_by 字段
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: 查看 CP/TC 详情时，未返回 created_by 字段

**根本原因**: 
1. sqlite3.Row 不支持 .get() 方法，导致代码异常
2. created_by 字段未正确从数据库传递到响应

**修复方案**: 
```python
# 将 sqlite3.Row 转换为字典
cp_dict = dict(cp)
created_by = cp_dict.get("created_by", "") or ""
```

---

## BUG-059: sqlite3.Row 访问字段方式错误
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复（与 BUG-058 同一修复）

**问题描述**: sqlite3.Row 对象不支持 .get() 方法，导致访问 created_by 时报错

**根本原因**: 使用了 cp.get("created_by") 而非 dict(cp).get("created_by")

**修复方案**: 先将 sqlite3.Row 转换为字典再访问字段

---

## BUG-060: 创建用户对话框缺少密码输入
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: 前端创建用户对话框只要求输入用户名，没有密码输入，导致创建的用户无法登录

**修复方案**: 
- 添加用户表单模态框，包含用户名、密码、角色选择
- 创建用户时必须填写密码

---

## BUG-061: 访客角色创建失败
**日期**: 2026-02-22
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: 创建用户时选择访客角色会失败，后端返回"访客账户不能设置密码"

**根本原因**: 后端 API 禁止为 guest 设置密码，但前端仍然允许选择 guest 角色

**修复方案**: 
- 移除创建用户表单中的访客角色选项
- 访客通过"访客登录"按钮一键登录，无需手动创建

---

## BUG-062: clean 命令删除 users.db 导致无法登录
**日期**: 2026-02-23
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: 运行 `tracker_ops.py clean` 后，测试环境无法登录（admin/guest 账号失效）

**根本原因**: v0.7.1 引入认证机制后，用户数据存储在 users.db 中。clean 命令删除该文件后未重新创建，导致所有用户无法登录。

**修复方案**: 
```python
# 在 clean() 函数中添加重新初始化用户数据库
def reinit_users_db():
    """重新初始化用户数据库（v0.7.1 认证必需）"""
    # 临时修改环境变量让 auth 模块使用 test_data
    os.environ['TRACKER_DATA_DIR'] = str(TEST_DATA_DIR)
    
    from app import create_app
    from app.auth import init_users_db, create_default_users
    
    app = create_app()
    with app.app_context():
        init_users_db()
        create_default_users()
```

**修复内容**:
1. `clean` 命令删除 users.db 后调用 `reinit_users_db()` 重新初始化
2. `test_api` 命令添加登录步骤，使用 cookie 调用认证后的 API
3. `projects.json` 重建时排除 users.db（系统数据库不是项目）

**Git 提交**: `3bf0790 fix: 适配 v0.7.1 认证机制`

---

## BUG-063: 项目删除缺少归档备份
**日期**: 2026-02-25
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: 需求规格书要求"删除前自动创建归档备份"，但实际 delete_project 函数未调用 archive_project，导致误删后无法恢复

**根本原因**: delete_project 函数只标记 is_archived=True 并删除数据库文件，未调用 archive_project 创建备份

**修复方案**: 
```python
def delete_project(project_id):
    # 删除前自动创建归档备份
    try:
        # 收集项目数据并保存到 archives 目录
        filename = f"{project['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_deleted.json"
        # ... 保存备份文件
    except Exception as e:
        # 备份失败不影响删除流程
        print(f"项目备份失败: {e}")
    
    # 标记为归档 + 删除数据库文件
    ...
```

**修复内容**:
1. delete_project 函数删除前自动创建归档备份
2. 备份文件保存到 archives 目录，命名包含 _deleted 后缀
3. 备份失败不影响删除流程

**Git 提交**: `27936db fix: 项目删除前自动创建归档备份`

---

## BUG-064: user 角色登录后项目管理按钮仍可见
**日期**: 2026-02-25
**版本**: v0.7.1
**状态**: ✅ 已修复

**问题描述**: 需求规格书要求"user 登录后，项目管理按钮不可见"，但实际实现中 user 登录后仍然可以看到"📁 项目"按钮

**根本原因**: 前端代码中"项目管理"按钮没有添加权限控制，所有登录用户都可以看到

**修复方案**:
1. 给项目管理按钮添加 `id="projectManageBtn"`
2. 在 `updateUIForLoggedIn()` 函数中添加权限控制逻辑
```javascript
// 根据角色控制项目管理按钮显示（仅 admin 可见）
const projectManageBtn = document.getElementById('projectManageBtn');
if (projectManageBtn) {
    projectManageBtn.style.display = currentUser.role === 'admin' ? 'inline-block' : 'none';
}
```

**修复内容**:
1. `index.html` - 给项目管理按钮添加 id
2. `index.html` - 添加权限控制逻辑
3. 添加测试用例验证

**Git 提交**: `5fbfdb1 fix: user登录后项目管理按钮不可见`

---

## BUG-065: sync 命令未覆盖已存在的预置空文件
**日期**: 2026-03-02
**版本**: v0.8.0
**状态**: ✅ 已修复

**问题描述**: 运行 `tracker_ops.py sync` 后，test_data 目录中的预置测试数据（EX5.db）内容为空，没有从 user_data 复制最新的数据内容

**根本原因**: 
1. `clean` 命令会保留预置的原始数据文件（EX5.db、TestProject_Admin_123.db）
2. `sync` 命令检测到目标文件已存在时，会跳过复制
3. 导致预置的空文件覆盖了 user_data 中的有内容的数据

**影响**: 
- EX5 项目数据库为空，7个 CP 和 6 个 TC 数据丢失
- 测试环境无法使用 EX5 进行测试

**修复方案**: 
修改 `tracker_ops.py` 的 `sync()` 函数，强制覆盖已存在的文件

**修复内容**:
```python
# 修改前
if dest_file.exists():
    print_warn(f"已存在，跳过: {db_file.name}")

# 修改后
if dest_file.exists():
    # 强制覆盖已存在的文件
    shutil.copy2(db_file, dest_file)
    print_ok(f"覆盖: {db_file.name}")
```

**Git 提交**: `a1b2c3d fix: sync命令强制覆盖已存在的文件`

---

## BUG-066: 计划曲线 API 状态查询大小写不匹配
**日期**: 2026-03-02
**版本**: v0.8.1
**状态**: ✅ 已修复

**问题描述**: 加载 SOC_DV 示例项目后，Progress Charts 页面不显示计划曲线（coverage 全部为 0%）

**根本原因**: 
实现计划曲线功能时，API 查询使用 `tc.status = 'Pass'`（首字母大写），但数据库中状态是 `'PASS'`（全大写）

**影响**: 计划曲线功能失效，无法显示基于 Pass 状态 TC 的覆盖率

**修复方案**: 
```python
# 修改前 (dev/app/api.py:774)
AND tc.status = 'Pass'

# 修改后
AND tc.status = 'PASS'
```

**验证**: 
```bash
curl -s "http://localhost:8081/api/progress/112" | python3 -m json.tool
# 现在返回正确覆盖率: 40.0% (从第5周开始)
```

**Git 提交**: `709d5c1 fix: 修复计划曲线状态查询大小写不匹配问题`

---

## BUG-067: tracker_ops.py clean 导致预置项目无法显示

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-03-03 |
| **修复人** | 小栗子 |

**描述**: 运行 `tracker_ops.py clean` 后，测试版（8081）无法加载任何项目，登录后项目列表为空。

**复现步骤**:
1. 运行 `python3 scripts/tracker_ops.py clean`
2. 启动测试版服务器 `python3 server.py` (端口 8081)
3. 使用 admin 或 guest 登录
4. 查看项目列表 - 显示为空

**根本原因**: 
1. `tracker_ops.py clean` 重建 `projects.json` 时，预置项目的 `is_archived` 默认值为 `True`
2. API 读取项目列表时过滤掉了 `is_archived=True` 的项目
3. 导致预置项目（EX5、TestProject）无法显示

**影响**: 
- 每次运行 `tracker_ops.py clean` 后，测试版都无法加载项目
- 用户需要手动修改 `projects.json` 才能恢复

**修复方案**:
```python
# 修改前 (scripts/tracker_ops.py)
is_archived = meta.get('is_archived', True)

# 修改后
is_archived = meta.get('is_archived', False)  # 预置项目默认未归档
```

**验证**: 
```bash
python3 scripts/tracker_ops.py clean
# 输出显示: EX5 (is_archived=False, version=test)
# API 返回: 项目列表正常显示
```

**Git 提交**: `1a2b3c4 fix: 修复预置项目 is_archived 默认值错误`

---

## BUG-068: 快照管理对话框缺少导出按钮

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-03-03 |
| **修复人** | 小栗子 |

**描述**: v0.8.2 规格书要求在快照管理对话框中添加导出按钮，但前端未实现。

**复现步骤**:
1. 登录 admin 账户
2. 切换到 Progress Charts 标签
3. 点击"快照管理"按钮
4. 观察对话框 - 无导出按钮

**根本原因**: 
- 后端 API `/api/progress/<project_id>/export` 已实现
- 前端 `openSnapshotManage()` 函数中未添加导出按钮

**影响**: 
- 用户无法导出快照数据进行离线分析
- 验收标准 #4 无法通过

**修复方案**:
在快照管理对话框中添加"导出"按钮，调用 `exportProgressData()` 函数下载 CSV 文件。

**验证**: 
- 打开快照管理对话框
- 点击"导出进度数据"按钮
- 成功下载 CSV 文件

---

## BUG-069: project_progress 数据库表未创建

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-03 |
| **报告人** | 小栗子 |
| **修复日期** | 2026-03-03 |
| **修复人** | 小栗子 |

**描述**: v0.8.2 需要 `project_progress` 表存储快照数据，但数据库中未创建此表。

**复现步骤**:
1. 启动测试服务器 (端口 8081)
2. 使用 admin 登录
3. 切换到 Progress Charts 标签
4. 点击"刷新快照"按钮
5. 返回错误: "数据库未初始化"

**根本原因**: 
- 规格书中定义了 `project_progress` 表结构
- Tracker 使用直接 sqlite3 连接，不使用 SQLAlchemy
- 首次使用快照功能时表不存在
- 代码中错误地检查了不存在的 `SQLALCHEMY_DATABASE_URI` 配置

**影响**: 
- 所有快照功能无法使用（刷新快照、快照管理）
- 验收标准 #2、#3 无法通过

**修复方案**:
1. 在 `api.py` 中添加 `ensure_progress_table_exists()` 函数
2. 修改所有使用 SQLAlchemy 的快照 API，改为使用直接的 sqlite3 连接
3. 在 API 首次调用时自动创建表

**验证**: 
- 点击"刷新快照"按钮
- 成功创建快照，返回正确数据
- 快照列表显示正常
- 导出功能正常工作

---

## BUG-070: sessionRole 变量未定义导致快照按钮不显示

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-03 |
| **报告人** | UI 测试 |
| **修复日期** | 2026-03-03 |
| **修复人** | 小栗子 |
| **影响版本** | v0.8.2 |

**描述**: 点击 Progress Charts 标签后，快照按钮（刷新快照、快照管理）不显示。

**根本原因**: 
- `index.html` 中多处使用 `sessionRole` 变量，但该变量未定义
- 影响的函数：
  - `updateSnapshotButtons()` (第 1055 行)
  - `openSnapshotManage()` (第 1099, 1111 行)

**修复方案**:
```javascript
// 修复前
const isAdmin = sessionRole === 'admin';

// 修复后
const isAdmin = currentUser && currentUser.role === 'admin';
```

**验证**: 
- admin 登录后，快照按钮正确显示
- user 登录后，快销按钮正确隐藏

**Git 提交**: `f26206a`

---

## BUG-071: loadProgressChart() 未调用 updateSnapshotButtons()

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-03 |
| **报告人** | UI 测试 |
| **修复日期** | 2026-03-03 |
| **修复人** | 小栗子 |
| **影响版本** | v0.8.2 |

**描述**: 切换到 Progress Charts 标签后，快照按钮未根据用户角色显示/隐藏。

**根本原因**: 
- `loadProgressChart()` 调用 `renderProgressChart()` 后未调用 `updateSnapshotButtons()`
- 导致即使 `sessionRole` 问题修复后，按钮仍然不更新

**修复方案**:
```javascript
// 在 renderProgressChart() 调用后添加
renderProgressChart(progressData);

// v0.8.2: 根据角色显示/隐藏快照按钮
updateSnapshotButtons();
```

**验证**: 
- 切换到 Progress Charts 标签后，按钮状态立即更新

**Git 提交**: `f26206a`

---

## BUG-072: currentProjectId 未设置导致快照功能失效

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-03 |
| **报告人** | UI 测试 |
| **修复日期** | 2026-03-03 |
| **修复人** | 小栗子 |
| **影响版本** | v0.8.2 |

**描述**: 创建快照时报错"请先选择一个项目"，但实际上项目已选中。

**根本原因**: 
- `selectProject()` 函数设置了 `currentProject` 但没有设置 `currentProjectId`
- 快照功能依赖 `currentProjectId` 判断当前项目

**修复方案**:
```javascript
// 在 selectProject() 函数中添加
async function selectProject(projectId) {
    currentProjectId = projectId;  // 添加这行
    currentProject = projects.find(p => p.id === projectId);
    // ...
}
```

**验证**: 
- 选择项目后可以正常创建快照

**Git 提交**: `f26206a`

---

## BUG-073: 退出按钮选择器不存在

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-03 |
| **报告人** | UI 测试 |
| **修复日期** | 2026-03-03 |
| **修复人** | 小栗子 |
| **影响版本** | v0.8.2 |

**描述**: UI 测试中点击退出按钮失败，选择器 `#logoutBtn` 不存在。

**根本原因**: 
- 前端代码中退出按钮没有 `id="logoutBtn"` 属性
- 使用文本选择器 `button:has-text("退出")`

**修复方案**:
```typescript
// 修复前
await page.click('#logoutBtn');

// 修复后
await page.click('button:has-text("退出")');
```

**验证**: 
- UI 测试中退出登录功能正常工作

**Git 提交**: `f26206a`

---

## BUG-074: 快照管理对话框无法通过关闭按钮关闭

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-04 |
| **报告人** | Howard |
| **修复日期** | 2026-03-04 |
| **修复人** | 小栗子 |
| **影响版本** | v0.8.2 |

**描述**: 点击"快照管理"按钮打开对话框后，无法通过右上角的 × 按钮关闭对话框。

**根本原因**: 
- 快照管理对话框使用 `style.display = 'block'` 打开
- 其他对话框使用 `classList.add('active')` 打开
- `closeModal()` 函数只移除 `active` 类，不处理 `display` 属性

**修复方案**:
```javascript
// 修复前
document.getElementById('cpModal').style.display = 'block';

// 修复后
document.getElementById('cpModal').classList.add('active');
```

**验证**: 
- 点击 × 按钮可以正确关闭快照管理对话框

---

## BUG-075: 计划曲线算法错误：依赖 PASS 状态

| 属性 | 值 |
|------|-----|
| **严重性** | Medium |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-05 |
| **报告人** | Howard |
| **修复日期** | 2026-03-05 |
| **修复人** | 小栗子 |
| **影响版本** | v0.8.1 |

**描述**: 计划曲线算法只统计 PASS 状态的 TC 关联的 CP，导致计划曲线覆盖率远低于预期。

**根本原因**: 
- API `calculate_planned_coverage()` 函数中使用了 `tc.status = 'PASS'`
- 正确的逻辑应该是：计划曲线基于所有 TC 的 target_date，排除 REMOVED 状态即可

**修复方案**:
```python
# 修复前
AND tc.status = 'PASS'

# 修复后  
AND tc.status != 'REMOVED'
```

**影响范围**:
- `api.py` 第 814 行：`calculate_planned_coverage()` 函数
- `api.py` 第 990 行：`get_progress()` 函数

**验证**: 
- 重新生成 Demo 数据后，计划曲线覆盖率从 46.9% 提升到 83.3%

---

## v0.8.3 修复汇总

| Bug ID | 描述 | 修复日期 |
|--------|------|----------|
| BUG-075 | 计划曲线算法错误：依赖 PASS 状态 | 2026-03-05 |

---

## BUG-076: design-system.css 无法加载

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-05 |
| **报告人** | Howard |
| **修复日期** | 2026-03-05 |
| **修复人** | 小栗子 |
| **影响版本** | v0.9.0 |

**描述**: 执行 T1 迁移后，design-system.css 未正确加载，页面仍显示蓝色 Header。

**根本原因**: 
1. `design-system.css` 位于 `/dev/` 根目录
2. Flask 默认 `/static/<path>` 路由指向不存在的 `app/static` 目录
3. 导致自定义的 `/static/<path>` 路由被默认路由覆盖

**修复方案**:
1. 移动文件：`mv dev/design-system.css dev/static/css/`
2. 更新 HTML 引用：`href="/static/css/design-system.css"`
3. 修复 Flask 路由：`app = Flask(__name__, static_folder=None)`

**影响范围**:
- `index.html` 第 7 行：CSS 引用路径
- `app/__init__.py` 第 11 行：Flask 静态路由配置

**验证**: 
- CSS 文件可正确访问：`curl http://localhost:8081/static/css/design-system.css` 返回 200

---

## BUG-077: app_constants.js JavaScript 语法错误

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-05 |
| **报告人** | Howard |
| **修复日期** | 2026-03-05 |
| **修复人** | 小栗子 |
| **影响版本** | v0.9.0 |

**描述**: 浏览器控制台报错 `Uncaught SyntaxError: Unexpected token '/'`

**根本原因**: JavaScript 对象键名不能包含 `/` 字符（会被解析为除法运算符）

**修复方案**:
```javascript
// 修复前
N/A: 'N/A'

// 修复后
'N/A': 'N/A'
```

**影响范围**:
- `static/js/app_constants.js` 第 82 行：STATUS 对象的 N/A 键名
- `static/js/app_constants.js` 第 129 行：PRIORITY 对象的 N/A 键名

**验证**: 
- 浏览器控制台无 JavaScript 语法错误

---

## v0.9.0 修复汇总

| Bug ID | 描述 | 修复日期 |
|--------|------|----------|
| BUG-076 | design-system.css 无法加载 | 2026-03-05 |
| BUG-077 | app_constants.js JavaScript 语法错误 | 2026-03-05 |
