# Tracker v0.13.0 测试计划

> **测试版本**: v0.13.0
> **对应规格书**: `tracker_SPECS_v0.13.0.md`
> **创建日期**: 2026-04-12
> **状态**: 待开发
> **预估开发时间**: 6 小时

---

## 1. 版本概述

### 1.1 版本目标

为 Wiki 集成功能（v0.13.0）编写测试用例，确保功能质量。

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.13.0.md` |
| 需求分析 | `/projects/management/feedbacks/reviewed/requirements_analysis_WIKI_INTEGRATION_v0.13.0_20260412.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-W001 | Wiki Tab 按钮 | P0 | 0.5h |
| REQ-W002 | Wiki 后端路由（/wiki/* Blueprint） | P0 | 4h |
| REQ-W003 | Wiki 文档视图（三栏布局） | P0 | 6h |
| REQ-W004 | Wiki 项目切换联动 | P0 | 2h |
| REQ-W005 | Wiki 变更历史视图 | P1 | 3h |
| REQ-W006 | Wiki 搜索功能 | P1 | 3h |
| REQ-W007 | Wiki 环境隔离（生产/测试分开） | P0 | 0.5h |

---

## 2. 存放位置

| 文档类型 | 目录 |
|----------|------|
| 测试计划 (Test Plan) | `docs/PLANS/` ← 本文档 |
| 测试报告 (Test Report) | `docs/REPORTS/` |

---

## 3. API 测试计划

### 3.1 测试框架

基于 `docs/DEVELOPMENT/API_TESTING_STRATEGY.md`，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── conftest.py                     # 共享 fixture
├── test_api.py                     # 基础 CRUD
└── test_api_wiki.py               # ⭐ Wiki 功能测试（新增）
```

### 3.2 新增 API 测试用例

#### 3.2.1 基础路由测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-WIKI-001 | test_wiki_index_returns_json | GET /wiki/<slug>/index.json 返回 JSON | 返回正确的 JSON 格式 | REQ-W002 |
| API-WIKI-002 | test_wiki_page_returns_html | GET /wiki/<slug>/pages/<path> 返回 HTML | 返回 HTML 内容 | REQ-W002 |
| API-WIKI-003 | test_wiki_changes_index_returns_json | GET /wiki/<slug>/changes_index.json | 返回变更历史 JSON | REQ-W002 |
| API-WIKI-004 | test_wiki_exists_returns_status | GET /wiki/exists/<slug> | 返回 has_wiki 和 source | REQ-W002 |
| API-WIKI-005 | test_wiki_slug_generation_consistency | 项目名转 slug 前后端一致 | Python 和 JS 生成相同 slug | REQ-W002 |

#### 3.2.2 路径遍历防护测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-WIKI-010 | test_wiki_path_traversal_blocked_dotdot | 路径包含 `../` 时被拦截 | 返回 400 错误 | REQ-W002 |
| API-WIKI-011 | test_wiki_path_traversal_blocked_absolute | 绝对路径被拦截 | 返回 400 错误 | REQ-W002 |
| API-WIKI-012 | test_wiki_invalid_extension_blocked | 非 .html 文件被拦截 | 返回 400 错误 | REQ-W002 |

#### 3.2.3 降级逻辑测试

| 测试 ID | 测试方法 | 测试目标 | 场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-WIKI-020 | test_wiki_fallback_to_global | 项目 Wiki 不存在时降级到 _global | 返回 _global/index.json | REQ-W002 |
| API-WIKI-021 | test_wiki_global_also_missing | 全局 Wiki 也不存在时返回 404 | 返回 404 | REQ-W002 |

#### 3.2.4 Wiki 不存在测试

| 测试 ID | 测试方法 | 测试目标 | 场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-WIKI-030 | test_wiki_page_not_found | 页面不存在时返回 404 | 返回 404 | REQ-W002 |
| API-WIKI-031 | test_wiki_exists_none | Wiki 完全不存在时 source 为 none | source = "none" | REQ-W002 |

### 3.3 测试数据准备

Wiki 功能需要准备测试用的 Wiki 内容文件：

```
dev/tests/test_data/wiki/                    # 测试 Wiki 内容
├── _global/                               # 全局 Wiki
│   ├── index.json
│   └── pages/
│       ├── index.html
│       └── faq.html
└── test_project/                          # 测试项目 Wiki
    ├── index.json
    ├── changes_index.json
    └── pages/
        ├── index.html
        └── concepts/
            └── test.html
```

**测试数据初始化 fixture**：
```python
@pytest.fixture
def wiki_test_data(tmp_path):
    """创建测试用 Wiki 目录结构"""
    wiki_root = tmp_path / "wiki"
    wiki_root.mkdir()
    
    # 创建 _global Wiki
    global_wiki = wiki_root / "_global"
    global_wiki.mkdir()
    (global_wiki / "index.json").write_text('{"pages": []}')
    
    yield wiki_root
```

### 3.4 API 测试命令

```bash
# 运行 Wiki API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_wiki.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 4. UI 集成测试计划

### 4.1 测试框架

基于 `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md`，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/
├── conftest.ts                     # Playwright 配置
├── utils/
│   ├── dialog-helper.ts           # Dialog 处理
│   └── cleanup.ts                 # 数据清理
└── specs/
    └── integration/
        └── wiki.spec.ts          # ⭐ Wiki 功能测试（新增）
```

### 4.2 新增 UI 测试用例

#### 4.2.1 Wiki Tab 基本功能测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-WIKI-001 | wiki_tab_button_visible | Wiki Tab 按钮显示 | REQ-W001 | P0 |
| UI-WIKI-002 | wiki_tab_click_switches | 点击 Wiki Tab 切换到 Wiki 视图 | REQ-W001 | P0 |
| UI-WIKI-003 | wiki_tab_guest_hidden | guest 用户看不到 Wiki Tab | REQ-W001 | P0 |

#### 4.2.2 Wiki 导航测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-WIKI-010 | wiki_nav_renders_pages | 左侧导航正确显示页面列表 | REQ-W003 | P0 |
| UI-WIKI-011 | wiki_nav_click_loads_page | 点击导航加载对应页面 | REQ-W003 | P0 |
| UI-WIKI-012 | wiki_nav_current_highlighted | 当前页高亮显示 | REQ-W003 | P0 |
| UI-WIKI-013 | wiki_nav_categories_grouped | 导航按 category 分组显示 | REQ-W003 | P1 |

#### 4.2.3 Wiki 内容显示测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-WIKI-020 | wiki_content_loading_shows_spinner | 加载中显示加载动画 | REQ-W003 | P1 |
| UI-WIKI-021 | wiki_content_loads_html | 页面内容正确渲染 | REQ-W003 | P0 |
| UI-WIKI-022 | wiki_content_error_shows_retry | 加载失败显示重试按钮 | REQ-W003 | P1 |

#### 4.2.4 Wiki 项目切换联动测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-WIKI-030 | wiki_switch_project_refreshes | 切换项目后 Wiki 内容刷新 | REQ-W004 | P0 |
| UI-WIKI-031 | wiki_no_content_shows_empty | 无 Wiki 时显示空状态 | REQ-W004 | P0 |
| UI-WIKI-032 | wiki_fallback_to_global | 无项目 Wiki 时降级到全局 | REQ-W004 | P1 |

#### 4.2.5 Wiki 子 Tab 测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-WIKI-040 | wiki_subtab_docs_default | 默认显示文档 Tab | REQ-W003 | P0 |
| UI-WIKI-041 | wiki_subtab_changes_switch | 切换到变更历史 Tab | REQ-W005 | P1 |
| UI-WIKI-042 | wiki_subtab_search_switch | 切换到搜索 Tab | REQ-W006 | P1 |
| UI-WIKI-043 | wiki_changes_render_versions | 变更历史正确显示版本列表 | REQ-W005 | P1 |

#### 4.2.6 Wiki 搜索测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-WIKI-050 | wiki_search_filters_results | 搜索过滤结果 | REQ-W006 | P1 |
| UI-WIKI-051 | wiki_search_result_click_loads | 点击搜索结果加载页面 | REQ-W006 | P1 |

#### 4.2.7 Wiki 右侧信息栏测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-WIKI-060 | wiki_recent_changes_shown | 右侧显示最近更新 | REQ-W003 | P1 |

### 4.3 UI 测试辅助函数

```typescript
// dev/tests/test_ui/specs/integration/wiki.spec.ts

import { test, expect } from '@playwright/test';
import { dialogHelper } from '../../utils/dialog-helper';

// 辅助函数：等待 Wiki 内容加载完成
async function waitForWikiLoad(page: Page) {
    await page.waitForSelector('#wikiPanel', { state: 'visible' });
    await page.waitForSelector('.wiki-loading, .wiki-article, .wiki-empty', { timeout: 5000 });
}

// 辅助函数：加载指定 Wiki 页面
async function loadWikiPage(page: Page, pagePath: string) {
    await page.click(`[data-page="${pagePath}"]`);
    await page.waitForSelector('.wiki-article');
}
```

### 4.4 UI 测试命令

```bash
# 运行 Wiki UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/wiki.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox

# 运行所有 UI 测试
npx playwright test tests/test_ui/ --project=firefox
```

---

## 5. 测试开发任务分解

### 5.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 创建测试文件 + 基础路由测试 | `test_api_wiki.py` | 1h | ⏳ 待开始 |
| 路径遍历防护测试 | `test_api_wiki.py` | 0.5h | ⏳ 待开始 |
| 降级逻辑测试 | `test_api_wiki.py` | 0.5h | ⏳ 待开始 |
| 准备测试 Wiki 数据 | fixture | 0.5h | ⏳ 待开始 |

### 5.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| Wiki Tab 基本功能测试 | `wiki.spec.ts` | 1h | ⏳ 待开始 |
| Wiki 导航测试 | `wiki.spec.ts` | 1h | ⏳ 待开始 |
| Wiki 内容显示测试 | `wiki.spec.ts` | 1h | ⏳ 待开始 |
| Wiki 项目切换联动测试 | `wiki.spec.ts` | 1h | ⏳ 待开始 |
| Wiki 子 Tab + 搜索测试 | `wiki.spec.ts` | 1h | ⏳ 待开始 |

---

## 6. 验收标准

### 6.1 API 测试验收

- [ ] API-WIKI-001 ~ API-WIKI-012 所有测试通过
- [ ] 路径遍历攻击被正确拦截
- [ ] 降级逻辑正确工作
- [ ] 测试数据自动清理

### 6.2 UI 测试验收

- [ ] UI-WIKI-001 ~ UI-WIKI-060 所有测试通过
- [ ] Wiki Tab 切换正常
- [ ] 项目切换联动正常
- [ ] 搜索功能正常
- [ ] 错误处理正常

---

## 7. 测试执行计划

### 7.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_wiki.py -v

# 3. 运行 UI 测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/wiki.spec.ts --project=firefox
```

### 7.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速、稳定，验证后端逻辑 |
| 2 | UI 集成测试 | 验证前端功能和交互 |

---

## 8. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 测试 Wiki 数据准备复杂 | 测试不稳定 | 使用 fixture 自动创建/清理 |
| Wiki 内容为空时部分功能无法测试 | 覆盖不完整 | 准备完整的测试数据 |
| UI 测试依赖 Wiki 数据存在 | 测试前置条件 | 在 beforeEach 中确保数据就绪 |

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-04-12 | 初始版本 | OpenClaw |

---

**文档创建时间**: 2026-04-12 05:40:00
**创建人**: OpenClaw
