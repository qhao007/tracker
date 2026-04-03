# Tracker v0.11.0 版本补充规格书

> **版本**: v0.11.0-supplement
> **创建日期**: 2026-03-30
> **状态**: 待开发（待确认反馈）
> **基于**: v0.11.0 初始规格书
> **评审报告**: `tracker_SPECS_v0.11.0_SUPPLEMENT_REVIEW.md`

---

## 1. 概述

### 1.1 补充需求列表

| # | 需求 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | 后台 API 批量更新 FC coverage_pct / status | P1 | 2h |
| 2 | FC 表头显示 "Functional Coverage" | P2 | 0.5h |
| 3 | 确认 FC 添加功能不开发，移除对应按钮 | P2 | 0.5h |
| 4 | CP 详情页显示关联 FC Item，支持点击跳转 | P1 | 2h |
| 5 | FC Bin 条目显示关联 CP ID 列（可点击跳转） | P1 | 3h |
| 6 | FC Bin 条目 comment 列控制最大长度 | P2 | 0.5h |
| 7 | 项目对话框显示 coverage_mode 和 FC 个数 | P1 | 2h |
| | **总计** | | **~10.5h** |

---

## 2. 详细需求

### 2.1 后台 API 批量更新 FC coverage_pct / status

**需求描述**: 支持通过 API 批量更新 FC items 的 coverage_pct 和 status 字段

**API 设计**:

| 方法 | 路径 | 功能 |
|------|------|------|
| PUT | `/api/fc/batch` | 批量更新 FC items |

**请求体格式**:
```json
{
  "items": [
    {
      "id": 1,
      "coverage_pct": 98.5,
      "status": "ready"
    },
    {
      "id": 2,
      "coverage_pct": 85.0,
      "status": "missing"
    }
  ]
}
```

**响应格式**:
```json
{
  "success": true,
  "updated": 2,
  "failed": 0,
  "errors": []
}
```

**错误响应**:
```json
{
  "success": false,
  "updated": 1,
  "failed": 1,
  "errors": [
    {"id": 999, "error": "FC item not found"}
  ]
}
```

**业务规则**:
- `id` 必填，必须是有效的 FC item ID
- `coverage_pct` 可选，范围 0.0 ~ 100.0，超出范围返回校验错误
- `status` 可选，仅接受 `missing` 或 `ready`
- 至少需要提供 `coverage_pct` 或 `status` 其中之一
- 部分更新支持（只更新提供的字段）
- 需要有效的登录会话
- 只能更新属于当前项目的 FC items（校验 project_id）
- 建议记录操作审计日志

**边界条件**:
| 场景 | 期望行为 |
|------|---------|
| `items: []` 空数组 | 返回 `{success: true, updated: 0, failed: 0}` |
| 部分成功部分失败 | 返回 `updated` 和 `failed` 正确统计 |
| `coverage_pct` 超出 0-100 范围 | 返回校验错误 |
| 非 FC-CP 模式项目调用 | 返回 `{success: false, error: "Not in FC-CP mode"}` |

---

### 2.2 FC 表头显示 "Functional Coverage"

**需求描述**: FC Tab 的标题应显示完整名称 "Functional Coverage"，而非缩写

**修改位置**: `index.html:920`

**修改前**:
```html
<button class="tab" id="fcTab" onclick="switchTab('fc', event)" style="display: none;">FC</button>
```

**修改后**:
```html
<button class="tab" id="fcTab" onclick="switchTab('fc', event)" style="display: none;">Functional Coverage</button>
```

---

### 2.3 确认 FC 添加功能不开发，移除对应按钮

**需求描述**: `openFCModal()` 函数是空函数（TODO 状态），FC 添加功能确认不开发（FC 数据仅通过 CSV 导入）。移除 FC Tab 中的"添加 FC"和"导入 FC-CP 关联"按钮。

**修改位置**: `index.html:1024` 和 `index.html:1027`

**移除按钮**:
- `+ 添加 FC` (index.html:1024，`onclick="openFCModal()"`)
- `📥 导入 FC-CP 关联` (index.html:1027，`onclick="openFC_CPAssocImportModal()"`)

**保留按钮**:
- `📥 导入 FC` (index.html:1025)
- `📤 导出 FC` (通过 `exportData('fc')`)

**注意**: `POST /api/fc-cp-association/import` API 仍然保留，可用于 CSV 导入 FC-CP 关联数据。

---

### 2.4 CP 详情页显示关联 FC Item，支持点击跳转

**需求描述**: CP 详情展开后，显示关联的 FC items，点击后跳转到 FC Tab 并高亮对应条目

**修改要求**:
1. FC Item 名称改为可点击链接
2. 点击后：
   - 切换到 FC Tab
   - 自动展开对应的 covergroup 和 coverpoint
   - 高亮对应 bin 条目（临时背景色，持续 3 秒）
   - 自动滚动到视图中心

**修改位置**: `index.html` 中 CP 详情渲染 FC 关联的部分

**UI 样式**:
```html
<td style="padding: 4px 8px;">
  <a href="#" onclick="jumpToFCItem(${fc.id}); return false;" style="color: #0066cc; text-decoration: underline;">
    ${escapeHtml(fc.fc_bin_name || '')}
  </a>
</td>
```

**跳转函数实现** (index.html):

```javascript
// 跳转到 FC Item 并高亮
function jumpToFCItem(fcId) {
    switchTab('fc', null);

    // 1. 查找 FC item
    const fc = functionalCoverages.find(f => f.id === fcId);
    if (!fc) {
        console.error('FC item not found:', fcId);
        return;
    }

    // 2. 展开 covergroup（如果未展开）
    if (!fcExpandedGroups[fc.covergroup]) {
        fcExpandedGroups[fc.covergroup] = true;
    }

    // 3. 展开 coverpoint（如果未展开）
    const cpKey = `${fc.covergroup}|${fc.coverpoint}`;
    if (!fcExpandedCoverpoints[cpKey]) {
        fcExpandedCoverpoints[cpKey] = true;
    }

    // 4. 重新渲染 FC 表格
    renderFC();

    // 5. 高亮并滚动到视图（延迟确保 DOM 已渲染）
    setTimeout(() => {
        const el = document.querySelector(`tr[data-fc-id="${fcId}"]`);
        if (el) {
            el.classList.add('fc-highlight');
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => el.classList.remove('fc-highlight'), 3000);
        }
    }, 100);
}
```

**新增 CSS 样式**:

```css
.fc-highlight {
    background-color: #fff3cd !important;
    transition: background-color 0.3s ease;
}
```

**数据属性**: 需要在 FC bin 行添加 `data-fc-id` 属性：
```html
<tr style="border-bottom: 1px solid #eee;" data-fc-id="${bin.id}">
```

---

### 2.5 FC Bin 条目显示关联 CP ID 列

**需求描述**: 每个 FC bin 条目增加一列 "CP IDs"，显示关联的 CP ID（可能多个），点击可跳转到 CP 页面对应条目

**FC Table 修改后列**:
| Bin Name | Bin Value | Type | Coverage | Status | CP IDs | Comments |

**数据来源**: 从 `fc_cp_association` 表查询关联的 CP IDs

**API 需求**: 后端 `/api/fc` 返回时需包含关联的 CP IDs：
```json
{
  "id": 1,
  "bin_name": "addr_max",
  "cp_ids": [1, 3, 5],
  ...
}
```

**UI 样式**:
```html
<td style="padding: 4px 8px;">
  ${bin.cp_ids && bin.cp_ids.length > 0 
    ? bin.cp_ids.map(cpId => 
        `<a href="#" onclick="jumpToCPItem(${cpId}); return false;" style="color: #0066cc; text-decoration: underline;">CP_${cpId}</a>`
      ).join(', ')
    : '-'}
</td>
```

**跳转函数实现**:

```javascript
// 跳转到 CP Item 并高亮
function jumpToCPItem(cpId) {
    switchTab('cp', null);

    // 1. 展开 CP 详情（如果未展开）
    toggleCPDetail(cpId);

    // 2. 高亮 CP 行（延迟确保 DOM 已渲染）
    setTimeout(() => {
        const el = document.querySelector(`tr[data-cp-id="${cpId}"]`);
        if (el) {
            el.classList.add('cp-highlight');
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => el.classList.remove('cp-highlight'), 3000);
        }
    }, 100);
}
```

**新增 CSS 样式**:

```css
.cp-highlight {
    background-color: #fff3cd !important;
    transition: background-color 0.3s ease;
}
```

**修改位置**: `index.html` 中 FC 表格渲染部分（renderFC 函数内）

---

### 2.6 FC Bin 条目 comment 列控制最大长度

**需求描述**: comment 列内容过长时截断显示，鼠标悬停显示完整内容

**修改位置**: `index.html` 中 FC 表格 comment 列单元格

**样式规则** (必须使用):
```css
.fc-comment-cell {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

**HTML**:
```html
<td class="fc-comment-cell" title="${escapeHtml(bin.comments || '')}">
    ${escapeHtml(bin.comments || '')}
</td>
```

---

### 2.7 项目对话框显示 coverage_mode 和 FC 个数

**需求描述**: 项目列表中每个项目需要显示 coverage_mode 信息和 FC 个数（仅 FC-CP 模式）

**显示规则**:
| 模式 | 显示内容 |
|------|----------|
| TC-CP | `CP: X \| TC: Y \| TC-CP \| 日期`（不显示 FC count） |
| FC-CP | `CP: X \| FC: Z \| FC-CP \| 日期`（不显示 TC count） |

**修改位置**: `index.html:3604` 中项目列表渲染

**当前代码**:
```javascript
return `<div class="project-info"><span class="project-name">${p.name}</span><span class="project-meta">CP: ${p.cp_count} | TC: ${p.tc_count}${p.start_date ? ' | ' + p.start_date + ' ~ ' + p.end_date : ''}</span></div>`;
```

**修改后代码**:
```javascript
// 根据 coverage_mode 显示不同信息
const metaParts = [`CP: ${p.cp_count}`];
if (p.coverage_mode === 'fc_cp') {
    metaParts.push(`FC: ${p.fc_count || 0}`);
} else {
    metaParts.push(`TC: ${p.tc_count}`);
}
metaParts.push(p.coverage_mode === 'fc_cp' ? 'FC-CP' : 'TC-CP');
if (p.start_date) {
    metaParts.push(`${p.start_date} ~ ${p.end_date}`);
}

return `<div class="project-info"><span class="project-name">${p.name}</span><span class="project-meta">${metaParts.join(' | ')}</span></div>`;
```

---

## 3. API 变更

### 3.1 新增 API

#### PUT /api/fc/batch - 批量更新 FC Items

**请求**:
```http
PUT /api/fc/batch
Content-Type: application/json
Cookie: session=<session_id>

{
  "project_id": 1,
  "items": [
    {"id": 1, "coverage_pct": 98.5, "status": "ready"},
    {"id": 2, "coverage_pct": 85.0}
  ]
}
```

**响应（成功）**:
```json
{
  "success": true,
  "updated": 2,
  "failed": 0,
  "errors": []
}
```

**响应（部分成功）**:
```json
{
  "success": false,
  "updated": 1,
  "failed": 1,
  "errors": [
    {"id": 999, "error": "FC item not found"}
  ]
}
```

**响应（校验错误）**:
```json
{
  "success": false,
  "error": "Invalid coverage_pct value",
  "details": [
    {"id": 1, "coverage_pct": 150.0, "error": "Value must be between 0 and 100"}
  ]
}
```

**权限校验**:
- 需要有效的登录会话
- 只能更新属于当前项目的 FC items
- 建议记录操作审计日志（操作人、操作时间、修改内容）

### 3.2 修改 API

#### GET /api/fc - 返回 cp_ids 字段

**新增字段**: `cp_ids` - 关联的 CP ID 列表

```json
{
  "id": 1,
  "covergroup": "apb_protocol_cg",
  "coverpoint": "cp_addr_range",
  "bin_name": "addr_max",
  "bin_val": "{32'hFFFFFFFC}",
  "coverage_type": "coverpoint",
  "coverage_pct": 98.5,
  "status": "ready",
  "comments": "Address range coverage",
  "cp_ids": [1, 3, 5],
  "created_at": "2026-03-27 10:00:00"
}
```

**查询逻辑**:
```sql
SELECT fc.*, GROUP_CONCAT(fca.cp_id) as cp_ids
FROM functional_coverage fc
LEFT JOIN fc_cp_association fca ON fc.id = fca.fc_id
WHERE fc.project_id = ?
GROUP BY fc.id
```

#### GET /api/projects - 返回 fc_count 字段

**修改位置**: `app/api.py` 的 `get_projects()` 函数

**新增字段**:
```json
{
  "id": 1,
  "name": "Project A",
  "cp_count": 10,
  "tc_count": 20,
  "fc_count": 5,
  "coverage_mode": "fc_cp",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31"
}
```

**数据库查询**:
```sql
SELECT 
    p.*,
    COUNT(DISTINCT cp.id) as cp_count,
    COUNT(DISTINCT tc.id) as tc_count,
    COUNT(DISTINCT fc.id) as fc_count
FROM project p
LEFT JOIN cover_point cp ON p.id = cp.project_id
LEFT JOIN test_case tc ON p.id = tc.project_id
LEFT JOIN functional_coverage fc ON p.id = fc.project_id
GROUP BY p.id
```

---

## 4. 前端修改

### 4.1 文件清单

| 文件 | 修改内容 |
|------|----------|
| `index.html` | FC Tab 标题、按钮移除、CP IDs 列、comment 截断、项目列表显示、跳转函数、CSS 高亮 |
| `app/api.py` | 新增 `/api/fc/batch` API，修改 `/api/fc` 返回 cp_ids，修改 `get_projects` 查询 |

### 4.2 CSS 新增

```css
/* FC/CP 高亮样式 */
.fc-highlight, .cp-highlight {
    background-color: #fff3cd !important;
    transition: background-color 0.3s ease;
}

/* FC comment 截断 */
.fc-comment-cell {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

### 4.3 新增 JS 函数

| 函数 | 位置 | 功能 |
|------|------|------|
| `jumpToFCItem(fcId)` | index.html | 跳转到 FC Item 并高亮 |
| `jumpToCPItem(cpId)` | index.html | 跳转到 CP Item 并高亮 |
| `batchUpdateFC(items)` | index.html | 调用 `/api/fc/batch` |

---

## 5. 验收标准

### 5.1 API 验收

| # | 标准 | 状态 |
|---|------|------|
| 1 | `/api/fc/batch` 支持批量更新 coverage_pct | ⏳ |
| 2 | `/api/fc/batch` 支持批量更新 status | ⏳ |
| 3 | `/api/fc/batch` 部分更新正常工作 | ⏳ |
| 4 | `/api/fc/batch` 空数组返回 updated: 0 | ⏳ |
| 5 | `/api/fc/batch` 部分成功返回正确统计 | ⏳ |
| 6 | `/api/fc/batch` 校验 coverage_pct 范围 (0-100) | ⏳ |
| 7 | `/api/fc/batch` 非 FC-CP 模式返回错误 | ⏳ |
| 8 | `/api/fc` 返回 cp_ids 字段 | ⏳ |
| 9 | `/api/projects` 返回 fc_count 字段 | ⏳ |

### 5.2 UI 验收

| # | 标准 | 状态 |
|---|------|------|
| 10 | FC Tab 标题显示 "Functional Coverage" | ⏳ |
| 11 | FC Tab 移除"添加 FC"按钮 | ⏳ |
| 12 | FC Tab 移除"导入 FC-CP 关联"按钮 | ⏳ |
| 13 | CP 详情中 FC Item 可点击跳转 | ⏳ |
| 14 | FC Bin 条目显示关联 CP IDs | ⏳ |
| 15 | CP IDs 可点击跳转到 CP 详情 | ⏳ |
| 16 | 跳转后自动展开对应 covergroup/coverpoint | ⏳ |
| 17 | 跳转后高亮持续 3 秒后消失 | ⏳ |
| 18 | 跳转后自动滚动到条目位置 | ⏳ |
| 19 | FC Comment 列超过 150px 时截断 | ⏳ |
| 20 | FC Comment 列鼠标悬停显示完整内容 | ⏳ |
| 21 | TC-CP 模式项目显示 TC count，不显示 FC | ⏳ |
| 22 | FC-CP 模式项目显示 FC count，不显示 TC | ⏳ |
| 23 | 项目列表显示 coverage_mode 标签 | ⏳ |

---

## 6. 开发计划

| 任务 | 预估时间 | 状态 |
|------|----------|------|
| 实现 `/api/fc/batch` API | 2h | ⏳ |
| 修改 `/api/fc` 返回 cp_ids | 1h | ⏳ |
| 修改 `get_projects` 返回 fc_count | 1h | ⏳ |
| FC Tab 标题修改 | 0.5h | ⏳ |
| 移除 FC Tab 按钮 | 0.5h | ⏳ |
| 添加跳转函数和 CSS 高亮 | 1h | ⏳ |
| CP 详情 FC 跳转功能 | 1h | ⏳ |
| FC Bin 显示 CP IDs 列 | 2h | ⏳ |
| FC Comment 截断 | 0.5h | ⏳ |
| 项目对话框显示扩展信息 | 1h | ⏳ |
| **总计** | **~10.5h** | |

---

## 7. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.11.0-supplement | 2026-03-30 | 补充需求规格 |
| v0.11.0-supplement | 2026-03-30 | 根据评审反馈更新：明确语义、补充实现细节、添加边界条件 |

---

**文档创建时间**: 2026-03-30
**最后更新**: 2026-03-30
**创建人**: OpenClaw
