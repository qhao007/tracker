# Tracker v0.11.0 补充规格书评审报告

> **版本**: v0.11.0-supplement-review
> **创建日期**: 2026-03-30
> **评审人**: Claude Code
> **文档状态**: 待确认

---

## 1. 概述

### 1.1 评审范围

本报告针对 `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 进行评审，评审维度包括：

- 完整性：需求是否覆盖所有必要的功能点
- 一致性：与主规格书 v0.11.0 的契合度
- 可行性：技术实现方案的合理性
- 清晰度：描述的明确性和可执行性

### 1.2 总体评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 完整性 | ⭐⭐⭐⭐ | 7个需求覆盖了主要功能点 |
| 一致性 | ⭐⭐⭐ | 与主规格书基本一致，有几处需澄清 |
| 可行性 | ⭐⭐⭐⭐ | 设计可行，技术实现清晰 |
| 清晰度 | ⭐⭐⭐ | 描述基本清晰，部分细节不足 |

---

## 2. 问题汇总

### 2.1 问题分级

| 级别 | 数量 | 说明 |
|------|------|------|
| 🔴 需澄清 | 2 | 需求语义不明确，需与需求方确认 |
| 🟡 需补充细节 | 3 | 实现路径存在缺口，需补充 |
| 🟢 小问题 | 3 | 文档规范性问题 |

---

## 3. 🔴 需澄清的问题

### 问题 #1: 需求 #2.3 "移除添加 FC" 语义不明确

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 2.3 节

**现象**:

当前代码中 `openFCModal()` 是 **空函数（TODO 状态）**：

```javascript
// index.html:2129
function openFCModal() {
    / TODO: v0.11.0 FC 添加功能待实现 - 需要弹出 FC 添加表单
    console.log('FC 添加功能开发中');
}
```

规格书描述为"移除 FC Tab 的'添加 FC'按钮"，但该功能从未实现。

**问题**:

| 理解方式 | 结果 |
|---------|------|
| 如果是"移除一个不存在的功能" | 语义应为"跳过实现"或"确认不开发" |
| 如果是"移除已存在的功能" | 需确认是否有其他添加 FC 的入口 |

**建议**:

明确此需求的实际意图。如果是确认不开发 FC 添加功能，建议将需求标题改为：

```
2.3 确认 FC 添加功能不开发
```

并说明原因（如"FC 数据仅通过 CSV 导入，不支持手动添加"）。

---

### 问题 #2: 需求 #2.7 TC-CP 模式是否显示 FC count

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 2.7 节

**现象**:

规格书显示 TC-CP 模式的格式：
```
CP: 10 | TC: 20 | FC: 5 | TC-CP | 2026-01-01 ~ 2026-12-31
```

但 TC-CP 模式下项目通常不包含 FC 数据，显示 `FC: 5` 容易造成困惑。

**当前数据库查询**:

```sql
SELECT
    p.*,
    COUNT(DISTINCT cp.id) as cp_count,
    COUNT(DISTINCT tc.id) as tc_count,
    COUNT(DISTINCT fc.id) as fc_count  -- v0.11.0 supplement
FROM project p
LEFT JOIN functional_coverage fc ON p.id = fc.project_id
```

**问题**:

| 模式 | 当前显示 | 建议显示 |
|------|---------|---------|
| TC-CP | `CP: X \| TC: Y \| FC: Z \| TC-CP` | `CP: X \| TC: Y \| TC-CP` |
| FC-CP | `CP: X \| FC: Z \| FC-CP` | `CP: X \| FC: Z \| FC-CP` |

**建议**:

明确 TC-CP 模式下的显示规则：
- TC-CP 模式：**不显示** FC count
- FC-CP 模式：**显示** FC count

---

## 4. 🟡 需补充细节的问题

### 问题 #3: 需求 #2.4 跳转功能实现细节不足

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 2.4 节

**当前描述**:

```javascript
function jumpToFCItem(fcId) {
    switchTab('fc', null);
    // 展开对应 covergroup/coverpoint
    // 高亮 fcId 条目
}
```

**缺失的实现细节**:

| 缺失项 | 说明 |
|--------|------|
| 如何展开 covergroup/coverpoint | 需要自动调用展开逻辑 |
| 高亮 CSS 样式 | 使用什么 class？背景色？ |
| 高亮持续时间 | 3秒后是否自动取消？ |
| FC Item 如何定位 | FC list 中 fcId 对应哪个 DOM 元素？ |

**建议补充**:

```javascript
function jumpToFCItem(fcId) {
    switchTab('fc', null);

    // 1. 查找 FC item 所在的 covergroup 和 coverpoint
    const fc = functionalCoverages.find(f => f.id === fcId);
    if (!fc) {
        console.error('FC item not found:', fcId);
        return;
    }

    // 2. 展开 covergroup
    fcExpandedGroups[fc.covergroup] = true;

    // 3. 展开 coverpoint
    fcExpandedCoverpoints[`${fc.covergroup}|${fc.coverpoint}`] = true;
    renderFC();

    // 4. 高亮并滚动到视图
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

**新增 CSS**:

```css
.fc-highlight {
    background-color: #fff3cd !important;
    transition: background-color 0.3s ease;
}
```

---

### 问题 #4: 需求 #2.5 CP IDs 跳转逻辑不完整

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 2.5 节

**当前描述**:

```javascript
function jumpToCPItem(cpId) {
    switchTab('cp', null);
    toggleCPDetail(cpId);
    // 高亮 cpId 条目
}
```

**缺失项**:

| 缺失项 | 说明 |
|--------|------|
| `toggleCPDetail` 函数签名 | 需确认是否存在，参数是什么 |
| 高亮机制 | 应与 FC 跳转使用相同的 CSS class |
| 如果 CP 不存在 | 需处理异常情况 |

**建议补充**:

需确认以下函数是否存在并可用：
- `toggleCPDetail(cpId)` - 切换 CP 详情展开状态
- `highlightItem(itemId, className)` - 通用高亮函数（可选）

---

### 问题 #5: 需求 #2.6 comment 列 max-width 未指定

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 2.6 节

**当前描述**:

```css
.fc-comment-cell {
    max-width: 150px;  /* 建议值 */
    ...
}
```

**问题**:

`150px` 仅是注释中的建议值，实际开发可能因未明确而使用不同值。

**建议**:

明确 `max-width: 150px;`，并补充说明：
- 超出显示省略号
- 鼠标悬停显示完整内容（`title` 属性）

**建议的完整 CSS**:

```css
.fc-comment-cell {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
```

---

## 5. 🟢 小问题

### 问题 #6: 文档 2.2 节示例不够精确

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 2.2 节

**当前**:

```html
<!-- 当前 -->
<!-- 需要查找具体位置 -->
```

**建议**:

直接给出确切位置，减少开发时的查找成本：

```html
<!-- 修改位置: index.html:920 -->
<li id="fcTab" class="tab" onclick="switchTab('fc', event)" style="display: none;">FC</li>
```

---

### 问题 #7: API 缺少权限校验说明

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 3.1 节

**遗漏**:

批量更新 API `/api/fc/batch` 未说明以下内容：

| 项目 | 说明 |
|------|------|
| 登录验证 | 是否需要登录会话？ |
| 项目权限校验 | 只能更新当前项目下的 FC？ |
| 操作审计 | 是否记录操作日志？ |

**建议**:

在业务规则中补充：

```
- 需要有效的登录会话
- 只能更新属于当前项目的 FC items（校验 project_id）
- 建议记录操作审计日志（谁、什么时间、修改了什么）
```

---

### 问题 #8: 验收标准缺少边界条件

**位置**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md` 5.1 节

**遗漏的测试场景**:

| 场景 | 期望行为 |
|------|---------|
| `items: []` 空数组 | 返回 `{success: true, updated: 0, failed: 0}` |
| 部分成功部分失败 | 返回 `updated` 和 `failed` 正确统计 |
| 非 FC-CP 模式项目调用 | 应返回错误或拒绝 |
| `coverage_pct` 超出 0-100 范围 | 应返回校验错误 |

**建议补充**:

在验收标准中增加：

```
| 13 | `/api/fc/batch` 空数组返回 updated: 0 | ⏳ |
| 14 | `/api/fc/batch` 部分成功返回正确统计 | ⏳ |
| 15 | `/api/fc/batch` 校验 coverage_pct 范围 | ⏳ |
```

---

## 6. 与主规格书的一致性检查

| 主规格书声明 | 补充规格书 | 一致性 |
|-------------|-----------|--------|
| FC Tab 不包含"FC 详情编辑页面" | 移除"添加 FC"按钮 | ✅ 一致 |
| FC Tab 支持 CSV 导入/导出 | 保留导入/导出按钮 | ✅ 一致 |
| FC-CP 关联支持 CSV 导入 | 移除"导入 FC-CP 关联"按钮 | ⚠️ 需确认 |

**⚠️ 需确认**:

主规格书 3.1 声明 `POST /api/fc-cp-association/import` 已实现，但补充规格书要移除 UI 按钮。如果手动关联 API 仍需要，应保留入口或说明替代方案。

---

## 7. 建议的修改优先级

### 高优先级（阻塞开发）

| # | 建议 | 影响 |
|---|------|------|
| 1 | 明确"移除添加 FC"的语义 | 避免开发方向错误 |
| 2 | 明确 TC-CP 模式下是否显示 FC count | 避免 UI 显示不一致 |
| 3 | 补充跳转功能实现细节 | 确保功能可用 |

### 中优先级（提升质量）

| # | 建议 | 影响 |
|---|------|------|
| 4 | 明确 comment 列 max-width 值 | 避免 UI 不一致 |
| 5 | 补充 `/api/fc/batch` 边界条件 | 提升 API 健壮性 |
| 6 | 补充权限校验说明 | 提升安全性 |

---

## 8. 评审结论

### 8.1 总体评价

补充规格书覆盖了 v0.11.0 发布后用户反馈的主要改进点，方向正确。主要问题在于：

1. **跳转功能的实现细节不够详细** - 影响开发执行
2. **部分需求语义需要澄清** - 避免开发方向错误

### 8.2 建议行动

| 阶段 | 行动项 |
|------|--------|
| **确认中** | 与需求方确认 🔴 问题 #1、#2 |
| **开发前** | 补充 🟡 问题 #3、#4、#5 的实现细节 |
| **开发中** | 关注 🟢 问题作为 checklist |
| **测试中** | 补充边界条件测试用例 |

### 8.3 下一步

建议在确认上述 🔴 问题后，再进入开发阶段。

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.11.0-supplement-review | 2026-03-30 | 初始评审报告 |

---

**评审完成时间**: 2026-03-30
**评审人**: Claude Code
