# Tracker v0.9.1 测试报告

> **测试类型**: API + UI 集成测试 | **版本**: v0.9.1 | **日期**: 2026-03-08

---

## 1. 测试概览

### 1.1 测试环境

| 项目 | 值 |
|------|-----|
| 测试服务器 | http://localhost:8081 |
| 浏览器 | Firefox (Playwright) |
| 测试框架 | pytest + Playwright |
| 测试日期 | 2026-03-08 |

### 1.2 关联文档

| 文档 | 路径 |
|------|------|
| 版本规格书 | `/projects/management/tracker/docs/SPECIFICATIONS/tracker_v0.9.1_SPEC.md` |
| 测试计划 | `/projects/management/tracker/docs/PLANS/TEST_PLAN_v0.9.1.md` |

### 1.3 测试结果汇总

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 通过率 |
|----------|------|------|------|------|--------|
| API 测试 | 215 | 215 | 0 | 0 | **100%** |
| UI 冒烟测试 | 20 | 20 | 0 | 0 | **100%** |
| UI 反馈测试 | 5 | 5 | 0 | 0 | **100%** |
| **总计** | **240** | **240** | **0** | **0** | **100%** |

---

## 2. API 测试结果

### 2.1 测试文件

| 文件 | 用例数 | 结果 |
|------|--------|------|
| `test_api.py` | 约50个 | ✅ 通过 |
| `test_api_auth.py` | 约30个 | ✅ 通过 |
| `test_api_batch.py` | 约15个 | ✅ 通过 |
| `test_api_actual_curve.py` | 约15个 | ✅ 通过 |
| `test_api_boundary.py` | 约20个 | ✅ 通过 |
| `test_api_exception.py` | 约15个 | ✅ 通过 |
| `test_api_import_export.py` | 约20个 | ✅ 通过 |
| `test_api_performance.py` | 约10个 | ✅ 通过 |
| `test_api_planned_curve.py` | 约15个 | ✅ 通过 |
| `test_api_progress.py` | 约5个 | ✅ 通过 |
| `test_api_feedback.py` | **8个** | ✅ 通过 |

### 2.2 新增测试用例 (v0.9.1)

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| `API-FB-001` | 提交反馈接口 - 成功 | ✅ 通过 |
| `API-FB-002` | 提交反馈接口 - 未登录 | ✅ 通过 |
| `API-FB-003` | 提交反馈接口 - 缺少类型 | ✅ 通过 |
| `API-FB-004` | 提交反馈接口 - 无效类型 | ✅ 通过 |
| `API-FB-005` | 提交反馈接口 - 缺少标题 | ✅ 通过 |
| `API-FB-006` | 提交反馈接口 - 缺少描述 | ✅ 通过 |
| `API-FB-007` | 提交反馈接口 - 空请求体 | ✅ 通过 |
| `API-FB-008` | 提交反馈接口 - 所有类型 | ✅ 通过 |

---

## 3. v0.9.1 功能验证

### 3.1 功能列表

| # | 功能 | 代码位置 | 状态 |
|---|------|----------|------|
| 1 | CP 页面覆盖率左右布局 | `index.html:22` (`.coverage-wrapper`) | ✅ 已实现 |
| 2 | 用户反馈功能 - API | `api.py:3358-3413` | ✅ 已实现 |
| 3 | 用户反馈功能 - UI | `index.html:690-729` | ✅ 已实现 |
| 4 | switchTab 函数改进 | `index.html:1663-1675` | ✅ 已实现 |
| 5 | 常量替换 (API_ENDPOINTS) | `index.html:975` | ✅ 已实现 |

### 3.2 REQ-001: CP 页面覆盖率左右布局

**需求**: 当前 CP 表格中，每一行的覆盖率信息是上下分两行显示，期望改为左右显示。

**实现**:
- CSS `.coverage-wrapper` 使用 `display: flex; align-items: center; gap: 8px;`
- 覆盖率和详情并排显示，减少行高

**验证**: ✅ 代码已实现

### 3.3 REQ-002: 用户反馈功能

**需求**: 在"关于"对话框中增加用户反馈功能。

**实现**:
- API: `POST /api/feedback` - 提交反馈
- UI: 反馈标签页 + 表单 + 提交按钮
- 反馈保存到 `user_data/feedbacks/FEEDBACK_*.json`

**验证**:
- API 测试: 8/8 通过 ✅
- UI 测试: 5/5 通过 ✅

### 3.4 ISSUE-014: switchTab 函数改进

**需求**: 修改函数签名支持传入 event 参数。

**实现**:
```javascript
function switchTab(tab, event) {
    currentTab = tab;
    // 使用 event.currentTarget 替代 event.target
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
    // 非事件调用场景正常工作
}
```

**验证**: ✅ 代码已实现

### 3.5 ISSUE-015: 常量替换

**需求**: `app_constants.js` 文件已创建，需要在代码中实际使用。

**实现**:
- `API_ENDPOINTS.PROJECTS`, `API_ENDPOINTS.COVER_POINTS` 等已在多处使用
- `SESSION_KEYS` 未使用（可后续优化）

**验证**: ✅ 关键常量已替换

---

## 4. UI 测试用例

### 4.1 新增测试文件

- 路径: `tests/test_ui/specs/integration/12-feedback.spec.ts`

### 4.2 测试用例详情

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| `UI-FB-001` | 反馈标签页存在 | ✅ 通过 |
| `UI-FB-002` | 反馈表单类型选择 | ✅ 通过 |
| `UI-FB-003` | 反馈表单必填验证 | ✅ 通过 |
| `UI-FB-004` | 反馈提交成功提示 | ✅ 通过 |
| `UI-FB-005` | 反馈列表显示 | ✅ 通过 |

---

## 5. UI 测试结果 (2026-03-08)

### 5.1 测试结果汇总

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 通过率 |
|----------|------|------|------|------|--------|
| UI 冒烟测试 | 20 | 20 | 0 | 0 | **100%** |
| UI 反馈测试 | 5 | 5 | 0 | 0 | **100%** |

### 5.2 测试用例详情

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-FB-001 | 反馈标签页存在 | ✅ 通过 |
| UI-FB-002 | 反馈表单类型选择 | ✅ 通过 |
| UI-FB-003 | 反馈表单必填验证 | ✅ 通过 |
| UI-FB-004 | 反馈提交成功提示 | ✅ 通过 |
| UI-FB-005 | 反馈列表显示 | ✅ 通过 |

### 5.3 冒烟测试详情

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| SMOKE-001 | 页面加载 | ✅ 通过 |
| SMOKE-002 | admin 登录成功 | ✅ 通过 |
| SMOKE-003 | guest 登录成功 | ✅ 通过 |
| SMOKE-004 | 错误密码提示 | ✅ 通过 |
| SMOKE-005 | 项目切换 | ✅ 通过 |
| SMOKE-006 | 创建项目 | ✅ 通过 |
| SMOKE-007 | CP 标签切换 | ✅ 通过 |
| SMOKE-008 | 创建 CP | ✅ 通过 |
| SMOKE-009 | 编辑 CP | ✅ 通过 |
| SMOKE-010 | 删除 CP | ✅ 通过 |
| SMOKE-011 | TC 标签切换 | ✅ 通过 |
| SMOKE-012 | 创建 TC | ✅ 通过 |
| SMOKE-013 | 编辑 TC | ✅ 通过 |
| SMOKE-014 | 删除 TC | ✅ 通过 |
| LOGIN-001 | 登录后显示用户名 | ✅ 通过 |
| LOGIN-002 | guest 无用户管理按钮 | ✅ 通过 |
| LOGIN-003 | user 无删除项目按钮 | ✅ 通过 |
| LOGIN-004 | 登录后 Cookie | ✅ 通过 |
| LOGIN-005 | 登出功能 | ✅ 通过 |
| LOGIN-006 | Progress Charts Tab | ✅ 通过 |

### 5.4 失败用例分析

| 测试 | 原因分析 | 问题类型 | 修复方案 | 状态 |
|------|----------|----------|----------|------|
| (无) | - | - | - | - |

### 5.5 测试代码修复记录

| Bug ID | 问题描述 | 问题类型 | 修复方案 | 状态 |
|--------|----------|----------|----------|------|
| TEST-001 | 选择器 `button:has-text("关于")` 匹配到多个元素（头部按钮和Tab按钮） | 测试代码问题 | 使用更精确的选择器 `button.header-btn:has-text("关于")` | ✅ 已修复 |

---

## 6. Bug修复记录 (2026-03-08)

### 5.1 BUG-082: switchTab 函数参数缺失导致登录模态框无法关闭

**发现日期**: 2026-03-08

**问题描述**:
- 函数重构时修改了 `switchTab(tab, event)` 的签名
- 但HTML调用处未同步更新为 `switchTab('cp', event)`
- 导致点击Tab按钮时 `event` 为 undefined
- 登录后 `hideLoginModal()` 调用成功但模态框未实际关闭

**根因**:
- v0.9.1开发时只修改了JS函数定义，未同步更新HTML调用

**修复**:
```html
<!-- 修复前 -->
<button onclick="switchTab('cp')">Cover Points</button>

<!-- 修复后 -->
<button onclick="switchTab('cp', event)">Cover Points</button>
```

**影响文件**:
- `dev/index.html` 第301-303行

**验证**: ✅ 使用agent-browser测试确认修复成功

---

### 5.2 BUG-083: API_ENDPOINTS 重复声明错误

**发现日期**: 2026-03-08

**问题描述**:
- 控制台报错: `Identifier 'API_ENDPOINTS' has already been declared`
- 页面加载时JS错误导致部分功能异常

**根因**:
- `app_constants.js` 中定义了 `const API_ENDPOINTS = {...}`
- `index.html` 中也定义了 `const API_ENDPOINTS = {...}`
- 两个文件都被加载，导致重复声明

**修复**:
1. 修改 `app_constants.js`: 改用 `window.API_ENDPOINTS`
2. 修改 `index.html`: 使用 `Object.assign()` 覆盖而非重新声明

**影响文件**:
- `dev/static/js/app_constants.js` 第16行
- `dev/index.html` 第779行

**验证**: ✅ 使用agent-browser `errors`命令确认无JS错误

---

### 5.3 BUG-084: Chart.js CDN 加载超时警告

**发现日期**: 2026-03-08

**问题描述**:
- 控制台警告: `Chart.js: CDN 加载失败，使用本地版本 Error: CDN timeout`

**根因**: 网络环境导致CDN访问超时

**影响**: 非阻塞性，使用本地Chart.js fallback正常

**状态**: 已知问题，不影响功能

---

## 6. UI 测试 session 隔离问题

### 6.1 问题描述

Playwright 冒烟测试在 CI/自动化环境中可能出现 session 隔离问题，导致测试间状态污染。

### 6.2 影响范围

UI 冒烟测试

### 6.3 建议

- 添加 `testIsolation: true` 配置
- 或在每个测试前显式清理 cookie 和 localStorage

**状态**: 非阻塞性问题，功能正常

---

## 7. 手工测试结果 (agent-browser)

### 7.1 测试执行记录

| 测试项 | 工具 | 结果 | 备注 |
|--------|------|------|------|
| 页面加载 | agent-browser | ✅ 正常 | 显示登录界面 |
| 登录功能 | agent-browser | ✅ 正常 | admin/admin123 登录成功 |
| 项目切换 | agent-browser | ✅ 正常 | 项目下拉框可用 |
| CP页面显示 | agent-browser | ✅ 正常 | 显示CP表格列表 |
| Progress Charts | agent-browser | ✅ 正常 | 显示覆盖率图表 |
| 反馈功能 | agent-browser | ✅ 正常 | 表单提交成功 |
| 控制台错误 | agent-browser | ✅ 无错误 | 无JS运行时错误 |

### 7.2 控制台检查结果

```
[warning] Chart.js: CDN 加载失败，使用本地版本 Error: CDN timeout
```
- Chart.js CDN 超时，但已回退到本地版本，功能正常

```
[error] Failed to load resource: the server responded with a status of 401 (UNAUTHORIZED)
```
- 401 错误是正常的（未登录状态访问受保护资源）

### 7.3 问题记录

| 问题 | 状态 |
|------|------|
| Chart.js CDN 超时 | 已知问题，已使用本地 fallback |
| 未登录 401 错误 | 正常行为 |

### 7.4 手工测试结论

所有手工测试项目均通过，无阻塞性问题。

---

## 8. 验收标准

| 标准 | 状态 |
|------|------|
| ESLint 检查通过 | ✅ |
| API 测试 215/215 通过 | ✅ |
| UI 冒烟测试 20/20 通过 | ✅ |
| REQ-002 API 测试通过 | ✅ |
| REQ-002 UI 测试通过 | ✅ |

---

## 9. 测试报告

- HTML 报告: `/projects/management/tracker/dev/report.html`

---

**报告生成时间**: 2026-03-08
**署名**: Claude Code
