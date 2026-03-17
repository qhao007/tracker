# Tracker v0.9.2 版本开发规格书

> **版本**: v0.9.2
> **创建日期**: 2026-03-14
> **状态**: 开发中
> **关联需求**: `/projects/management/feedbacks/reviewed/requirements_analysis_v0.9.2_20260313.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | REQ-002: CP关联状态可视化（🔗图标） | P1 | 1h |
| 2 | REQ-003: TC关联状态可视化（🔗图标） | P1 | 1h |
| 3 | REQ-004: CP/TP滑动条支持（高度自适应屏幕） | P1 | 2.5h |
| 4 | REQ-004B: TC过滤布局与CP一致（单行显示） | P1 | 0.5h |
| 5 | REQ-005: CP未关联过滤 | P1 | 2h |
| 6 | ISSUE-017: admin强制改密码前端 | P1 | 1h |
| 7 | REQ-001: 更新Manual | P2 | 1h |
| | **总计** | | **~9h (+20% buffer → 11h)** |

### 1.2 背景

v0.9.1 已于 2026-03-08 发布，本版本主要解决以下问题：
1. 用户反馈：未关联CP/TC的可视化提示
2. 用户反馈：CP/TP列表的滚动体验优化
3. 用户反馈：CP页面增加未关联过滤
4. 历史遗留：admin首次登录强制改密码前端未实现
5. 文档更新：Manual补充v0.9.1用户功能

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| CP/TC关联状态可视化（红色+🔗图标） | 自定义字段功能 |
| CP/TP独立滚动条 | 批量设置项目日期 |
| CP页面未关联过滤 | 快照数据编辑 |
| admin强制改密码前端 | 忘记密码功能 |
| Manual更新 | 移动端适配 |
| | 长周期图表优化 |

---

## 2. 需求详情

### 2.1 REQ-002: CP关联状态可视化

**需求编号**: REQ-002

**需求描述**:
未被任何TC关联的CP需要在界面上以红色加粗方式显示，并增加🔗图标辅助色盲用户区分。

**前端需求**:
- 在CP列表渲染时，计算每个CP是否被TC关联
- 未关联的CP显示 `.unlinked { color: red; font-weight: bold; }` + 🔗图标
- 关联状态计算应缓存，避免重复遍历
- 页面切换时自动重新计算

**后端需求**:
- 无（前端实时计算）

**技术实现**:
```javascript
// 计算CP关联状态
function isCPUnlinked(cpId, tcList) {
    return !tcList.some(tc => tc.cp_ids && tc.cp_ids.includes(cpId));
}

// 渲染样式
const cpHtml = isCPUnlinked(cp.id, tcList) 
    ? `<span class="unlinked">${cp.name} 🔗</span>` 
    : cp.name;
```

### 2.2 REQ-003: TC关联状态可视化

**需求编号**: REQ-003

**需求描述**:
未被任何CP关联的TC需要在界面上以红色加粗方式显示，并增加🔗图标辅助色盲用户区分。

**前端需求**:
- 在TC列表渲染时，计算每个TC是否关联了CP
- 未关联的TC显示红色加粗 + 🔗图标
- 页面切换时自动重新计算

**后端需求**:
- 无（前端实时计算）

### 2.3 REQ-004: CP/TP滑动条支持（高度自适应屏幕）

**需求编号**: REQ-004

**需求描述**:
CP列表和TP列表各自支持独立垂直滚动条，表头保持固定在可视区域顶部。**高度自适应不同屏幕尺寸**，在不同显示器上都能充分利用空间。

> **⚠️ 需求更新 (2026-03-16)**: 高度改为自适应屏幕尺寸（使用 calc + vh + min + max），替代原来的固定 400px。

**前端需求**:
- CP区域：使用 `overflow-y: auto`，表头使用 `position: sticky`
- TP区域：同上，独立于CP区域
- 高度：自适应屏幕尺寸，使用 `calc(100vh - 280px)` + 范围限制
- 兼容性：现代浏览器（Chrome/Firefox/Edge/Safari）

**CSS实现**:
```css
/* 推荐方案：带范围限制的自适应高度 */
.cp-table-container, .tc-table-container {
    overflow-y: auto;
    max-height: min(600px, calc(100vh - 280px));
    max-height: max(300px, calc(100vh - 280px));
}

.cp-table-container thead, .tc-table-container thead {
    position: sticky;
    top: 0;
    background: #f5f5f5;
    z-index: 1;
}
```

**参数说明**:
| 参数 | 值 | 说明 |
|------|-----|------|
| 280px | 顶部固定元素合计高度 | 导航栏 + 标题 + Tab + 按钮等 |
| 600px | 最大高度限制 | 防止超大屏幕下表格过高 |
| 300px | 最小高度限制 | 防止小屏幕下表格过小 |

**适配效果**:
| 屏幕高度 | 表格高度 |
|----------|----------|
| 768px (笔记本) | ~488px |
| 1080px (外接屏) | ~800px |
| 1440px (大屏) | ~600px (受 max 限制) |
| 640px (小屏) | ~360px (受 min 限制) |

**技术可行性**: ✅ 可行
- `vh` 单位：现代浏览器完全支持
- `calc()`：支持 IE9+ / 现代浏览器
- `min()` / `max()`：支持 IE9+ / 现代浏览器
- 纯 CSS 修改，无需 JS

---

### 2.4 REQ-004B: TC过滤布局与CP一致（单行显示）

**需求编号**: REQ-004B

**问题描述**: 
CP 标签页的过滤选项（搜索框、Feature、Priority、未关联）都在一行显示。而 TC 标签页的过滤选项使用独立的 `.tc-filter-panel`，每个过滤条件占一行（有 label + select），占用两行高度。视觉上不一致。

**需求描述**: 
将 TC 标签页的过滤布局改成与 CP 标签页一致，所有过滤选项在一行显示。

**前端需求**:
- 删除 TC 独立的 `<div class="tc-filter-panel">` 容器
- 将过滤 select 移到 `.toolbar-left`，与 CP 保持一致
- 去掉 `<label>` 标签，只保留下拉框
- 保留所有过滤功能（Status/DV Milestone/Owner/Category）

**HTML 修改**:
```html
<!-- 当前（需删除） -->
<div class="tc-filter-panel" id="tcFilterPanel">
    <div class="filter-row">
        <div class="filter-group">
            <label>Status</label>
            <select id="tcStatusFilter">...</select>
        </div>
        ...
    </div>
</div>

<!-- 修改后：移到 toolbar-left -->
<div class="toolbar">
    <div class="toolbar-left">
        <!-- 批量操作按钮 -->
        <button ...>📋 批量更新状态</button>
        ...
        <!-- 过滤下拉框（与 CP 一致） -->
        <select id="tcStatusFilter" onchange="applyTCFilter()">
            <option value="">全部 Status</option>
            ...
        </select>
        <select id="tcDvFilter" onchange="applyTCFilter()">
            <option value="">全部 DV Milestone</option>
            ...
        </select>
        <select id="tcOwnerFilter" onchange="applyTCFilter()">
            <option value="">全部 Owner</option>
            ...
        </select>
        <select id="tcCategoryFilter" onchange="applyTCFilter()">
            <option value="">全部 Category</option>
            ...
        </select>
        <!-- 重置按钮 -->
        <button onclick="resetTCFilter()">重置</button>
        <!-- 搜索框 -->
        <input type="text" class="search-input" placeholder="搜索...">
        <!-- 排序 -->
        <select onchange="sortTC(this.value)">...</select>
    </div>
</div>
```

**修改前后对比**:

| 状态 | CP 布局 | TC 布局（当前） | TC 布局（修改后） |
|------|---------|----------------|------------------|
| 过滤组件 | 单行（inline） | 多行（block） | 单行（inline） |
| Label | 无 | 有 | 无 |
| 容器 | `.toolbar` | `.tc-filter-panel` | `.toolbar` |

**验收标准**:
- [ ] TC 标签页过滤选项全部在一行显示（与 CP 一致）
- [ ] 所有过滤功能正常工作（Status/DV Milestone/Owner/Category）
- [ ] 重置按钮、搜索框、排序下拉位置正常
- [ ] 计数器显示正常

---

### 2.5 REQ-005: CP未关联过滤

**需求编号**: REQ-005

**需求描述**:
在CP页面Filter下拉增加"未关联"选项，可过滤出所有未被任何TC关联的CP。

**前端需求**:
- 在现有Filter下拉增加"未关联"选项
- 选择后调用带过滤参数的API
- 显示当前过滤状态

**后端需求**:
- 修改 `GET /api/cp` 支持 `filter=unlinked` 参数
- 返回 `linked=false` 或 `linked=true` 的CP

**API设计**:
| 方法 | 路径 | 参数 | 功能 |
|------|------|------|------|
| GET | `/api/cp` | `filter=unlinked` | 返回未关联的CP |
| GET | `/api/cp` | `filter=all` | 返回全部CP（默认） |

### 2.6 ISSUE-017: admin强制改密码前端

**需求编号**: ISSUE-017

**需求描述**:
admin用户首次登录后必须修改密码，前端需要强制弹窗要求修改密码，并禁用其他操作。

**前端需求**:
- 登录成功后检查 `response.user.must_change_password === true`
- 如为true，显示修改密码弹窗
- 弹窗显示时禁用其他页面操作
- 修改密码成功后刷新用户信息

**后端需求**:
- ✅ 已实现（无需修改）
- `POST /api/auth/login` 返回 `must_change_password` 字段
- `PATCH /api/auth/password` 支持修改密码

**前端逻辑**:
```javascript
// 登录成功回调
function handleLogin(data) {
    if (data.user.must_change_password === true) {
        showChangePasswordModal();
        disableAllOtherOperations();
    } else {
        navigateToHome();
    }
}
```

### 2.7 REQ-001: 更新Manual

**需求编号**: REQ-001

**需求描述**:
更新Manual文档，补充v0.9.1新增的普通用户功能（用户反馈提交）。

**文档需求**:
- 补充"用户反馈"章节
- 说明反馈入口、填写内容、提交方式
- 与v0.9.1功能一致

---

## 3. 数据库修改

本版本无数据库修改需求。

---

## 4. API 接口设计

### 4.1 接口列表

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/cp` | 获取CP列表（新增filter参数） | ⏳ 待实现 |
| GET | `/api/tc` | 获取TC列表（前端计算无需改） | ✅ 无需修改 |
| POST | `/api/auth/password` | 修改密码 | ✅ 已实现 |

### 4.2 详细 API 规范

#### 4.2.1 获取CP列表（支持过滤）

**端点**: `GET /api/cp`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | Y | 项目ID |
| filter | string | N | 过滤类型：`all`(默认), `unlinked` |

**响应**:
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "CP-001",
            "status": "Pass",
            "linked": true
        },
        {
            "id": 2,
            "name": "CP-002",
            "status": "Pass", 
            "linked": false
        }
    ],
    "total": 100
}
```

---

## 5. 前端界面设计

### 5.1 页面/组件列表

| 页面/组件 | 功能 | 状态 |
|----------|------|------|
| CP列表页 | 新增关联状态显示、🔗图标 | ⏳ 待实现 |
| TC列表页 | 新增关联状态显示、🔗图标 | ⏳ 待实现 |
| CP过滤 | 新增"未关联"过滤选项 | ⏳ 待实现 |
| 登录页 | 强制改密码弹窗 | ⏳ 待实现 |
| Manual | 补充用户反馈章节 | ⏳ 待实现 |

### 5.2 界面规范

#### 5.2.1 关联状态显示

**未关联CP/TC样式**:
```css
.unlinked {
    color: red;
    font-weight: bold;
}

.unlinked::before {
    content: "🔗 ";
}
```

#### 5.2.2 CP过滤下拉

**选项列表**:
| 选项 | 值 |
|------|-----|
| 全部 | all |
| Pass | Pass |
| Fail | Fail |
| Blocked | Blocked |
| **未关联** | **unlinked** |

#### 5.2.3 强制改密码弹窗

**要求**:
- 弹窗显示时背景页面不可操作
- 显示密码输入框 + 确认密码输入框
- 显示当前密码要求（长度≥6）
- 禁用关闭按钮

---

## 6. 验收标准

### 6.1 REQ-002/003: 关联状态可视化

- [ ] CP页面：未关联的CP显示为红色加粗 + 🔗图标
- [ ] TC页面：未关联的TC显示为红色加粗 + 🔗图标
- [ ] 关联的CP/TC正常显示，无特殊样式
- [ ] 页面切换时关联状态自动重新计算
- [ ] 刷新页面后状态保持

### 6.2 REQ-004: CP/TP滑动条

- [ ] CP列表可独立垂直滚动，TP列表不动
- [ ] TP列表可独立垂直滚动，CP列表不动
- [ ] 滚动时表头保持固定（sticky）
- [ ] 高度自适应不同屏幕尺寸（笔记本/外接屏）
- [ ] 极端屏幕尺寸下有 min(300px)/max(600px) 保护
- [ ] Chrome/Firefox/Edge/Safari 浏览器正常显示

### 6.2.1 REQ-004B: TC过滤布局与CP一致

- [ ] TC 标签页过滤选项全部在一行显示（与 CP 一致）
- [ ] 所有过滤功能正常工作（Status/DV Milestone/Owner/Category）
- [ ] 重置按钮、搜索框、排序下拉位置正常
- [ ] 计数器显示正常

### 6.3 REQ-005: 未关联过滤

- [ ] CP页面Filter下拉包含"未关联"选项
- [ ] 选择"未关联"后，只显示未关联的CP
- [ ] 过滤结果分页正常
- [ ] 取消过滤后显示全部CP

### 6.4 ISSUE-017: admin强制改密码

- [ ] admin首次登录成功后会弹窗要求修改密码
- [ ] 弹窗弹出时背景页面不可操作
- [ ] 修改密码成功后跳转首页
- [ ] 再次登录不再强制改密码
- [ ] 普通用户登录不受影响

### 6.5 REQ-001: 更新Manual

- [ ] Manual包含"用户反馈"章节
- [ ] 章节内容与v0.9.1功能一致
- [ ] 目录中有对应章节入口

---

## 7. 开发计划

### 7.1 开发任务

| 任务 | 状态 | 预计时间 |
|------|------|----------|
| REQ-002: CP关联状态可视化 | ⏳ 待开发 | 1h |
| REQ-003: TC关联状态可视化 | ⏳ 待开发 | 1h |
| REQ-004: CP/TP滑动条 | ⏳ 待开发 | 2h |
| REQ-005: CP未关联过滤 | ⏳ 待开发 | 2h |
| ISSUE-017: 强制改密码 | ⏳ 待开发 | 1h |
| REQ-001: 更新Manual | ⏳ 待开发 | 1h |
| 测试与修复 | ⏳ 待开发 | 2h |

### 7.2 里程碑

| 里程碑 | 计划日期 | 实际日期 | 状态 |
|--------|----------|----------|------|
| 开发完成 | 2026-03-XX | | ⏳ 待完成 |
| 测试完成 | 2026-03-XX | | ⏳ 待完成 |
| 发布 | 2026-03-XX | | ⏳ 待完成 |

---

## 8. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| REQ-004浏览器兼容性问题 | 中 | 低 | 使用 `position: sticky`，测试多种浏览器 |
| 关联状态计算性能问题 | 低 | 低 | 数据量大时增加缓存 |
| 强制改密码流程中断 | 中 | 低 | 确保后端API稳定 |

---

## 9. 相关文档

| 文档 | 路径 |
|------|------|
| 需求分析 | `/projects/management/feedbacks/reviewed/requirements_analysis_v0.9.2_20260313.md` |
| 开发规范 | `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| 测试策略 | `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md`<br>`docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| BugLog | `docs/BUGLOG/tracker_OPEN_ISSUES.md` |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.9.2 | 2026-03-14 | 初始版本 |
| v0.9.2 | 2026-03-16 | 更新 REQ-004：高度改为自适应屏幕尺寸（calc+vh+min+max），合并原 REQ-004A |
| v0.9.2 | 2026-03-16 | 新增 REQ-004B：TC过滤布局与CP一致（单行显示） |

---

**文档创建时间**: 2026-03-14
**最后更新**: 2026-03-16
**创建人**: OpenClaw
