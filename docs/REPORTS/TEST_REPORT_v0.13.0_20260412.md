# Tracker v0.13.0 Wiki API 测试报告

> **测试版本**: v0.13.0
> **测试日期**: 2026-04-12
> **测试工程师**: Claude Code (Subagent C)
> **状态**: ✅ 完成

---

## 1. 测试结果摘要

### 1.1 Wiki API 测试

| 测试文件 | 测试总数 | 通过 | 失败 | 状态 |
|----------|----------|------|------|------|
| `test_api_wiki.py` | 12 | 12 | 0 | ✅ 通过 |

### 1.2 回归测试

| 测试文件 | 测试总数 | 通过 | 失败 | 状态 |
|----------|----------|------|------|------|
| `test_api_wiki.py` | 12 | 12 | 0 | ✅ 通过 |
| `test_api_dashboard.py` | 31 | 31 | 0 | ✅ 通过 |

---

## 2. 新增测试用例 (API-WIKI-001 ~ API-WIKI-031)

### 2.1 基础路由测试 (API-WIKI-001 ~ API-WIKI-005)

| 用例ID | 测试方法 | 测试目标 | 结果 |
|--------|----------|----------|------|
| API-WIKI-001 | test_wiki_index_returns_json | GET /wiki/<slug>/index.json 返回 JSON | ✅ 通过 |
| API-WIKI-002 | test_wiki_page_returns_html | GET /wiki/<slug>/pages/<path> 返回 HTML | ✅ 通过 |
| API-WIKI-003 | test_wiki_changes_index_returns_json | GET /wiki/<slug>/changes_index.json 返回变更历史 | ✅ 通过 |
| API-WIKI-004 | test_wiki_exists_returns_status | GET /wiki/exists/<slug> 返回 has_wiki 和 source | ✅ 通过 |
| API-WIKI-005 | test_wiki_slug_generation_consistency | 项目名转 slug 前后端一致 | ✅ 通过 |

### 2.2 路径遍历防护测试 (API-WIKI-010 ~ API-WIKI-012)

| 用例ID | 测试方法 | 测试目标 | 结果 |
|--------|----------|----------|------|
| API-WIKI-010 | test_wiki_path_traversal_blocked_dotdot | 路径包含 `../` 时被拦截 | ✅ 通过 |
| API-WIKI-011 | test_wiki_path_traversal_blocked_absolute | 绝对路径被拦截 | ✅ 通过 |
| API-WIKI-012 | test_wiki_invalid_extension_blocked | 非 .html 文件被拦截 | ✅ 通过 |

### 2.3 降级逻辑测试 (API-WIKI-020 ~ API-WIKI-021)

| 用例ID | 测试方法 | 测试目标 | 结果 |
|--------|----------|----------|------|
| API-WIKI-020 | test_wiki_fallback_to_global | 项目 Wiki 不存在时降级到 _global | ✅ 通过 |
| API-WIKI-021 | test_wiki_global_also_missing | 全局 Wiki 也不存在时返回 404 | ✅ 通过 |

### 2.4 Wiki 不存在测试 (API-WIKI-030 ~ API-WIKI-031)

| 用例ID | 测试方法 | 测试目标 | 结果 |
|--------|----------|----------|------|
| API-WIKI-030 | test_wiki_page_not_found | 页面不存在时返回 404 | ✅ 通过 |
| API-WIKI-031 | test_wiki_exists_none | Wiki 完全不存在时 source 为 none | ✅ 通过 |

---

## 3. 测试修复记录

### 3.1 初始失败测试

运行初始测试时发现 3 个测试失败：

| 测试方法 | 失败原因 | 修复方案 |
|----------|----------|----------|
| test_wiki_path_traversal_blocked_absolute | Flask 对 `//` URL 返回 308 重定向，测试期望直接返回 400 | 修改测试使用 `follow_redirects=True`，验证最终返回 400 |
| test_wiki_global_also_missing | 测试无法在现有测试环境下执行（`_global` wiki 始终存在） | 使用 monkeypatch 隔离测试，临时覆盖 `get_wiki_base_path` |
| test_wiki_exists_none | 同上，测试场景无法在现有环境实现 | 使用 monkeypatch + importlib 获取实际模块进行隔离测试 |

### 3.2 修复详情

#### 修复 1: test_wiki_path_traversal_blocked_absolute

**问题**: Flask 对 `//etc/passwd` URL 进行 308 重定向，路由处理函数未直接收到请求。

**修复**:
```python
# 修复前
response = client.get('/wiki/soc_dv/pages//etc/passwd')
assert response.status_code == 400

# 修复后
response = client.get('/wiki/soc_dv/pages//etc/passwd', follow_redirects=True)
assert response.status_code == 400
```

#### 修复 2 & 3: test_wiki_global_also_missing 和 test_wiki_exists_none

**问题**: 测试需要验证"当项目 Wiki 和 `_global` Wiki 都不存在时"的行为，但测试环境中 `_global` 始终存在，导致无法测试该场景。

**修复**: 使用 pytest 的 `monkeypatch` 和 `importlib` 隔离测试：
```python
import importlib
import app.wiki as wiki_module
wiki_mod = importlib.import_module('app.wiki')  # 获取实际模块
temp_wiki_root = tmp_path / "wiki"
temp_wiki_root.mkdir()
monkeypatch.setattr(wiki_mod, 'get_wiki_base_path', lambda: str(temp_wiki_root))
```

---

## 4. 测试数据说明

### 4.1 Wiki 测试数据位置

- **测试 Wiki 数据**: `/projects/management/tracker/dev/data/wiki/`
  - `_global/`: 全局 Wiki（始终存在）
  - `soc_dv/`: 项目 Wiki

### 4.2 测试隔离

对于需要验证"Wiki 不存在"场景的测试，使用 `tmp_path` fixture 创建临时 Wiki 目录，确保测试隔离。

---

## 5. 结论

### 5.1 测试完成度

- [x] API-WIKI-001 ~ API-WIKI-005 基础路由测试
- [x] API-WIKI-010 ~ API-WIKI-012 路径遍历防护测试
- [x] API-WIKI-020 ~ API-WIKI-021 降级逻辑测试
- [x] API-WIKI-030 ~ API-WIKI-031 Wiki 不存在测试

### 5.2 测试结果

| 指标 | 值 |
|------|-----|
| 测试总数 | 12 |
| 通过 | 12 |
| 失败 | 0 |
| 通过率 | 100% |

### 5.3 备注

- 所有 Wiki API 测试用例均已实现并通过
- 测试隔离问题已通过 monkeypatch 解决
- 路径遍历防护功能验证通过

---

**报告生成时间**: 2026-04-12
**报告生成人**: Claude Code

---

## 6. Wiki UI 测试结果 (Subagent D)

### 6.1 测试结果汇总

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 通过率 |
|----------|------|------|------|------|--------|
| Wiki UI 测试 | 20 | 13 | 7 | 0 | **65%** |

### 6.2 新增UI测试用例

| 文件 | 用例数 | 结果 |
|------|--------|------|
| wiki.spec.ts | 20 | ⚠️ 部分失败 |

### 6.3 测试用例详情

#### 4.2.1 Wiki Tab 基本功能测试

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-WIKI-001 | Wiki Tab 按钮显示 | ✅ 通过 |
| UI-WIKI-002 | 点击 Wiki Tab 切换到 Wiki 视图 | ✅ 通过 |
| UI-WIKI-003 | guest 用户看不到 Wiki Tab | ✅ 通过 |

#### 4.2.2 Wiki 导航测试

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-WIKI-010 | 左侧导航正确显示页面列表 | ❌ 失败 - 应用 Bug |
| UI-WIKI-011 | 点击导航加载对应页面 | ❌ 失败 - 应用 Bug |
| UI-WIKI-012 | 当前页高亮显示 | ✅ 通过 |
| UI-WIKI-013 | 导航按 category 分组显示 | ✅ 通过 |

#### 4.2.3 Wiki 内容显示测试

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-WIKI-020 | 加载中显示加载动画 | ✅ 通过 |
| UI-WIKI-021 | 页面内容正确渲染 | ❌ 失败 - 应用 Bug |
| UI-WIKI-022 | 加载失败显示重试按钮 | ❌ 失败 - 应用 Bug |

#### 4.2.4 Wiki 项目切换联动测试

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-WIKI-030 | 切换项目后 Wiki 内容刷新 | ✅ 通过 |
| UI-WIKI-031 | 无 Wiki 时显示空状态 | ❌ 失败 - 应用 Bug |
| UI-WIKI-032 | 无项目 Wiki 时降级到全局 | ❌ 失败 - 应用 Bug |

#### 4.2.5 Wiki 子 Tab 测试

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-WIKI-040 | 默认显示文档 Tab | ✅ 通过 |
| UI-WIKI-041 | 切换到变更历史 Tab | ✅ 通过 |
| UI-WIKI-042 | 切换到搜索 Tab | ✅ 通过 |
| UI-WIKI-043 | 变更历史正确显示版本列表 | ✅ 通过 |

#### 4.2.6 Wiki 搜索测试

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-WIKI-050 | 搜索过滤结果 | ✅ 通过 |
| UI-WIKI-051 | 点击搜索结果加载页面 | ✅ 通过 |

#### 4.2.7 Wiki 右侧信息栏测试

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-WIKI-060 | 右侧显示最近更新 | ❌ 失败 - 应用 Bug |

### 6.4 失败用例分析

| 测试 | 原因分析 | 问题类型 | 修复方案 | 状态 |
|------|----------|----------|----------|------|
| UI-WIKI-010 | Wiki 导航项未渲染 - `renderWikiNav` 未被正确调用或 `wikiIndexData.pages` 数据未正确传递 | 应用 Bug | 前端 `loadWiki` 函数中 `wikiIndexData.pages` 可能为 undefined，需检查数据流 | 待修复 |
| UI-WIKI-011 | 依赖于 UI-WIKI-010，前提条件不满足 | 应用 Bug | 同上 | 待修复 |
| UI-WIKI-021 | `#wikiPageContent` 隐藏 - Wiki 内容面板未正确显示 | 应用 Bug | `loadWiki` 成功但内容区未正确渲染，需检查 `renderWikiPageContent` | 待修复 |
| UI-WIKI-022 | Wiki 内容为空 - 内容区 text length 为 0 | 应用 Bug | 同上 | 待修复 |
| UI-WIKI-031 | 无 Wiki 时内容区为空 - 可能 Wiki 加载后又显示空状态 | 应用 Bug | 需验证 Wiki 内容加载流程 | 待修复 |
| UI-WIKI-032 | 全局 Wiki 导航未显示 - nav items count 为 0 | 应用 Bug | 降级到全局 Wiki 后导航未正确渲染 | 待修复 |
| UI-WIKI-060 | `#wikiRecentChanges` 隐藏 - 右侧最近更新区域未显示 | 应用 Bug | `loadWikiChanges` 可能未正确调用或 `renderWikiChanges` 未正确渲染 | 待修复 |

### 6.5 应用 Bug 记录

以下 Bug 需记录到 Buglog 并由开发团队修复：

**Bug-WIKI-001: Wiki 导航项不显示**
- 现象: 点击 Wiki Tab 后，左侧导航面板为空，无导航项显示
- 根因: API `/wiki/soc_dv/index.json` 返回正确数据，但前端 `renderWikiNav` 未正确渲染
- 影响: UI-WIKI-010, UI-WIKI-011
- 状态: 待修复

**Bug-WIKI-002: Wiki 内容区域不显示**
- 现象: Wiki 页面内容区域隐藏或为空
- 根因: `#wikiPageContent` 元素虽然存在但 `display: none` 或内容为空
- 影响: UI-WIKI-021, UI-WIKI-022, UI-WIKI-031
- 状态: 待修复

**Bug-WIKI-003: Wiki 右侧信息栏不显示**
- 现象: 右侧"最近更新"区域隐藏
- 根因: `#wikiRecentChanges` 元素未正确显示
- 影响: UI-WIKI-060
- 状态: 待修复

### 6.6 备注

1. **测试环境**: 测试服务器运行 v0.12.2，但前端代码包含 v0.13.0 Wiki 功能
2. **API 验证**: Wiki API (`/wiki/<slug>/index.json`) 返回正确数据，后端功能正常
3. **前端问题**: 问题集中在前端 Wiki 内容渲染流程，可能与 `loadWiki` → `renderWikiNav/renderWikiPageContent/renderWikiChanges` 调用链有关
4. **建议**: 开发团队需检查前端 Wiki 渲染逻辑，特别是 `wikiIndexData` 状态管理和 DOM 更新

---

**UI 测试完成时间**: 2026-04-12
**UI 测试工程师**: Claude Code (Subagent D)

---

## 7. 手工测试结果 (Subagent E)

### 7.1 测试执行记录

| 测试项 | 工具 | 结果 | 备注 |
|--------|------|------|------|
| 登录界面样式 | playwright | ✅ 正常 | 页面正常渲染 |
| 登录功能 | playwright | ✅ 正常 | JS 表单提交成功 |
| Wiki Tab 切换 | playwright | ⚠️ 有问题 | Tab 存在但相关元素有问题 |
| 控制台错误 | playwright | ⚠️ 有警告 | 见下文 |
| Wiki 导航项显示 | playwright | ❌ Bug 已确认 | #wikiNav 元素不存在 |
| Wiki 内容区域显示 | playwright | ❌ Bug 已确认 | #wikiPageContent 隐藏 |
| Wiki 右侧信息栏显示 | playwright | ❌ Bug 已确认 | #wikiRecentChanges 隐藏 |

### 7.2 控制台检查结果

```
[ERROR] Failed to load resource: the server responded with a status of 404 (NOT FOUND)
```

**注**: 404 错误在部分测试中出现，可能与 Wiki 页面加载有关。

### 7.3 Wiki 元素状态验证

| 元素 ID | 存在 | 可见 | 状态 |
|---------|------|------|------|
| `#wikiNav` | ❌ 否 | - | Bug-WIKI-001 已确认 |
| `#wikiPageContent` | ✅ 是 | ❌ 否 | Bug-WIKI-002 已确认 |
| `#wikiRecentChanges` | ✅ 是 | ❌ 否 | Bug-WIKI-003 已确认 |
| `#wikiPanel` | ✅ 是 | ✅ 是 | 外层容器正常 |

### 7.4 应用代码问题修复 (待修复)

#### Bug-WIKI-001: Wiki 导航项不显示 (已确认)

**问题**: 点击 Wiki Tab 后，左侧导航面板 `#wikiNav` 元素在 DOM 中不存在。

**根因**: 前端 `renderWikiNav` 函数未被调用或执行异常，导致 `#wikiNav` 元素未创建。

**验证方法**:
```javascript
// 在浏览器控制台执行
document.querySelector('#wikiNav') // 返回 null
```

#### Bug-WIKI-002: Wiki 内容区域不显示 (已确认)

**问题**: Wiki 页面内容区域 `#wikiPageContent` 元素存在于 DOM，但 `visibility: hidden` 或 `display: none`。

**根因**: Wiki 内容加载后未正确设置显示状态。

**验证方法**:
```javascript
// 在浏览器控制台执行
const el = document.querySelector('#wikiPageContent');
el ? getComputedStyle(el).display : 'not found' // 返回 'none'
```

#### Bug-WIKI-003: Wiki 右侧信息栏不显示 (已确认)

**问题**: Wiki 右侧"最近更新"区域 `#wikiRecentChanges` 元素存在于 DOM，但 `visibility: hidden` 或 `display: none`。

**根因**: `loadWikiChanges()` 未正确调用或渲染后未设置显示状态。

**验证方法**:
```javascript
// 在浏览器控制台执行
const el = document.querySelector('#wikiRecentChanges');
el ? getComputedStyle(el).display : 'not found' // 返回 'none'
```

### 7.5 备注

1. **测试工具**: 使用 Playwright (v1.58.0) 进行浏览器自动化测试，agent-browser 因权限问题不可用
2. **测试方法**: 使用 `page.evaluate()` 直接操作 DOM 和提交表单，绕过 UI 拦截问题
3. **测试用户**: admin (已登录状态)
4. **Wiki 页面状态**: Wiki Tab 可以点击，页面有切换，但内容区域全部隐藏

---

**手工测试完成时间**: 2026-04-12
**手工测试工程师**: Claude Code (Subagent E)

