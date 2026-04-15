# Tracker v0.13.0 版本开发规格书

> **版本**: v0.13.0
> **创建日期**: 2026-04-12
> **状态**: 待评审
> **关联需求**: `/projects/management/feedbacks/reviewed/requirements_analysis_WIKI_INTEGRATION_v0.13.0_20260412.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | Wiki Tab 按钮 | P0 | 0.5h |
| 2 | Wiki 后端路由（/wiki/* Blueprint） | P0 | 4h |
| 3 | Wiki 文档视图（三栏布局） | P0 | 6h |
| 4 | Wiki 项目切换联动 | P0 | 2h |
| 5 | Wiki 变更历史视图 | P1 | 3h |
| 6 | Wiki 搜索功能 | P1 | 3h |
| 7 | Wiki 环境隔离（生产/测试分开） | P0 | 0.5h |
| 8 | Wiki 生命周期管理（项目删除时清理 Wiki） | P0 | 1h |
| 9 | 示例 Wiki 内容（_global/） | P1 | 4h |
| 10 | 测试与优化 | P1 | 6h |
| | **总计** | | **~28h** |

### 1.2 背景

Tracker 目前是纯数据管理工具，缺乏项目文档管理能力。验证团队需要在 Tracker 内部查看项目相关的技术文档（如协议规范、验证环境架构、使用指南、变更历史等），减少在多个工具间切换的成本。

**核心设计决策**：
- Wiki 内容是**项目数据**，存储在 `shared/data/{user,test}_data/wiki/`
- 与 Tracker 应用分离，项目方可直接更新，无需触碰 Tracker 代码
- 支持定期同步（如每周 regression 结果更新）
- 每个项目有独立的 Wiki 内容，实现项目级隔离

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| Wiki Tab 界面（子导航：文档/变更历史/搜索） | Wiki 内容在线编辑 UI |
| 项目级 Wiki 内容展示 | Wiki 内容版本管理 |
| Wiki 页面索引和搜索 | Wiki 与 CP/TC 的联动 |
| 后端静态文件服务 | Markdown 构建（内容直接是 HTML） |
| 项目切换联动 | 移动端适配 |
| 环境隔离（生产/测试分开） | |

---

## 2. 需求详情

### 2.1 功能需求 #1：Wiki Tab 按钮

**需求编号**: REQ-W001

**需求描述**:
在 Tracker Tab 栏新增"📚 Wiki"按钮，点击后切换到 Wiki 视图。

**前端需求**:
- 在 `switchTab()` 函数添加 'wiki' 分支
- Wiki Tab 按钮仅登录用户可见（guest 用户隐藏）
- Tab 切换时调用 `loadWiki()` 加载 Wiki 内容

**验收标准**:
- [ ] Wiki Tab 按钮显示在 Tab 栏（位于 Dashboard 后）
- [ ] 点击切换到 Wiki 视图
- [ ] guest 用户看不到 Wiki Tab

---

### 2.2 功能需求 #2：Wiki 后端路由

**需求编号**: REQ-W002

**需求描述**:
新增 Flask Blueprint 提供 `/wiki/*` 路由，指向 `shared/data/{user,test}_data/wiki/` 目录。

**后端需求**:
- 创建 `app/wiki.py` Blueprint
- 实现以下路由：
  - `GET /wiki/<slug>/index.json` - 获取 Wiki 索引
  - `GET /wiki/<slug>/pages/<path>` - 获取 Wiki 页面 HTML
  - `GET /wiki/<slug>/changes_index.json` - 获取变更历史
  - `GET /wiki/exists/<slug>` - 检查 Wiki 是否存在
- 路径遍历防护
- CSP Header
- 项目无 Wiki 时降级到 `_global/` 全局 Wiki

**Wiki 内容存储**:
```
shared/data/
├── user_data/wiki/           # 生产 Wiki
│   ├── _global/             # 全局 Wiki
│   │   ├── index.json
│   │   └── pages/
│   └── {project_slug}/      # 项目 Wiki
│       ├── index.json
│       ├── changes_index.json
│       └── pages/
└── test_data/wiki/          # 测试 Wiki（结构同上）
```

**验收标准**:
- [ ] `/wiki/<slug>/index.json` 返回正确的 JSON 格式
- [ ] `/wiki/<slug>/pages/<path>` 返回 HTML 内容
- [ ] 路径遍历攻击被拦截（`../` 等）
- [ ] 项目无 Wiki 时降级到 `_global/`
- [ ] Flask Blueprint 正确注册

---

### 2.3 功能需求 #3：Wiki 文档视图

**需求编号**: REQ-W003

**需求描述**:
Wiki Tab 内的主视图，采用三栏布局：左侧导航、中间内容、右侧信息栏。

**前端需求**:
- **左侧导航栏**（220px）：
  - 按 category 分组显示页面列表
  - 使用 Emoji 图标（与 Tracker 风格一致）
  - 当前页高亮显示
  - 点击加载对应页面
- **中间内容区**（flex: 1）：
  - 显示 Wiki 页面 HTML 内容
  - Wiki 内容使用 `.wiki-article` 样式层
  - 支持加载动画
  - 支持错误状态显示
- **右侧信息栏**（200px）：
  - 显示"最近更新"列表
  - 基于 `changes_index.json` 动态渲染

**Wiki 内容 HTML 规范**:
```html
<article class="wiki-article">
    <h1>页面标题</h1>
    <p>正文内容...</p>
    <table class="wiki-table">...</table>
</article>
```

**验收标准**:
- [ ] 三栏布局正确显示
- [ ] 左侧导航分组清晰
- [ ] 点击导航加载对应页面
- [ ] 当前页高亮
- [ ] 加载中显示加载动画
- [ ] 加载失败显示错误 + 重试按钮
- [ ] 右侧显示最近更新

---

### 2.4 功能需求 #4：Wiki 项目切换联动

**需求编号**: REQ-W004

**需求描述**:
切换 Tracker 项目时，Wiki 内容同步刷新为新项目的 Wiki。

**前端需求**:
- `selectProject()` 函数中检测项目切换
- 如果当前在 Wiki Tab，自动调用 `loadWiki()` 刷新
- slug 生成规则：`getProjectSlug(projectName)`

**slug 生成规则**:
| 项目名称 | Slug |
|----------|------|
| SPI-to-APB Bridge | `spi_to_apb_bridge` |
| USB3.0 Controller | `usb3_controller` |

```python
def get_project_slug(project_name):
    import re
    slug = project_name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug
```

**验收标准**:
- [ ] 切换项目后 Wiki 内容同步刷新
- [ ] 新项目无 Wiki 时降级到全局 Wiki
- [ ] 全局 Wiki 也没有时显示"暂无 Wiki 文档"

---

### 2.5 功能需求 #5：Wiki 变更历史视图

**需求编号**: REQ-W005

**需求描述**:
Wiki Tab 的子 Tab，显示项目的变更历史记录。

**前端需求**:
- 子 Tab 切换（文档/变更历史/搜索）
- 加载 `/wiki/<slug>/changes_index.json`
- 按版本分组显示变更记录
- 支持"全部/重要/次要"筛选

**changes_index.json 格式**:
```json
{
  "versions": [
    {
      "version": "v2.2",
      "date": "2026-04-12",
      "summary": "代码审查报告",
      "type": "important",
      "doc_changes": ["docs/review.md"],
      "rtl_changes": [],
      "tb_changes": ["tb/axi_agent.svh"]
    }
  ]
}
```

**验收标准**:
- [ ] 子 Tab 切换正常
- [ ] 变更历史正确显示
- [ ] 筛选功能正常

---

### 2.6 功能需求 #6：Wiki 搜索功能

**需求编号**: REQ-W006

**需求描述**:
Wiki Tab 的子 Tab，支持在当前项目 Wiki 中搜索页面。

**前端需求**:
- 搜索输入框
- 基于 `index.json` 的 `title`、`tags` 字段过滤
- 搜索结果点击跳转到对应页面

**验收标准**:
- [ ] 搜索输入响应 < 100ms
- [ ] 搜索结果正确匹配 title 和 tags
- [ ] 点击结果加载对应页面

---

### 2.7 功能需求 #7：Wiki 环境隔离

**需求编号**: REQ-W007

**需求描述**:
生产环境和测试环境的 Wiki 内容完全隔离。

**实现方式**:
- Flask 应用通过 `DATA_ROOT` 环境变量判断当前环境
- `/wiki/*` 路由映射到 `$DATA_ROOT/wiki/`
- 生产环境（port 8080）加载 `shared/data/user_data/wiki/`
- 测试环境（port 8081）加载 `shared/data/test_data/wiki/`

**验收标准**:
- [ ] 测试环境修改 Wiki 不影响生产环境
- [ ] 正确加载对应环境的 Wiki 内容

---

### 2.8 功能需求 #8：Wiki 生命周期管理

**需求编号**: REQ-W008

**需求描述**:
项目删除时，Wiki 内容跟随删除。

**实现方式**:
- 项目删除时，Tracker 后端在删除项目数据库的同时，删除对应的 Wiki 目录
- Wiki 目录位于 `shared/data/{user,test}_data/wiki/{project_slug}/`
- 删除前会自动创建归档备份（如果 Wiki 目录存在）

**注意**: 此功能需要在 Tracker 项目删除逻辑中增加 Wiki 目录清理代码，不属于 Wiki 功能本身的实现范围。

**验收标准**:
- [ ] 项目删除后 Wiki 目录一并删除
- [ ] 删除前 Wiki 内容已归档备份（如有）

---

## 3. 数据格式定义

### 3.1 index.json 结构

```json
{
  "version": "1.0",
  "updated_at": "2026-04-12T10:00:00Z",
  "updated_by": "admin",
  "pages": [
    {
      "path": "index.html",
      "title": "Wiki 首页",
      "category": "root",
      "order": 0,
      "tags": ["首页"]
    },
    {
      "path": "concepts/bridge_architecture.html",
      "title": "Bridge 架构",
      "category": "concepts",
      "order": 1,
      "tags": ["架构", "Bridge"]
    }
  ]
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| version | ✅ | 格式版本 |
| updated_at | ❌ | 最后更新时间 |
| pages | ✅ | 页面列表 |
| pages[].path | ✅ | 相对于 pages/ 目录的路径 |
| pages[].title | ✅ | 页面标题 |
| pages[].category | ❌ | 分类 |
| pages[].order | ❌ | 排序序号 |
| pages[].tags | ❌ | 标签（用于搜索） |

### 3.2 changes_index.json 结构

```json
{
  "versions": [
    {
      "version": "v2.2",
      "date": "2026-04-12",
      "summary": "代码审查报告",
      "type": "important",
      "doc_changes": ["docs/review.md"],
      "rtl_changes": [],
      "tb_changes": ["tb/axi_agent.svh"]
    }
  ]
}
```

---

## 4. API 接口设计

### 4.1 接口列表

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/wiki/<slug>/index.json` | 获取 Wiki 索引 | ⏳ 待实现 |
| GET | `/wiki/<slug>/pages/<path>` | 获取 Wiki 页面 HTML | ⏳ 待实现 |
| GET | `/wiki/<slug>/changes_index.json` | 获取变更历史 | ⏳ 待实现 |
| GET | `/wiki/exists/<slug>` | 检查 Wiki 是否存在 | ⏳ 待实现 |

### 4.2 详细 API 规范

#### 4.2.1 获取 Wiki 索引

**端点**: `GET /wiki/<slug>/index.json`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| slug | string | 项目 slug |

**响应（成功）**:
```json
{
  "version": "1.0",
  "pages": [...]
}
```

**响应（Wiki 不存在，降级到全局）**:
- 返回 `_global/index.json` 内容

**响应（完全无 Wiki）**:
```json
{
  "error": "Wiki not found",
  "project_slug": "xxx"
}
```

**状态码**:
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 404 | Wiki 完全不存在 |

---

#### 4.2.2 获取 Wiki 页面

**端点**: `GET /wiki/<slug>/pages/<path>`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| slug | string | 项目 slug |
| path | string | 页面路径（如 `concepts/bridge.html`） |

**响应**: HTML 页面内容

**错误响应**:
```json
{
  "error": "Page not found"
}
```

**状态码**:
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 路径遍历攻击拦截 |
| 404 | 页面不存在 |

---

#### 4.2.3 检查 Wiki 是否存在

**端点**: `GET /wiki/exists/<slug>`

**响应**:
```json
{
  "project_slug": "spi_to_apb_bridge",
  "has_wiki": true,
  "source": "project"
}
```

| source | 说明 |
|--------|------|
| project | 有项目专属 Wiki |
| global | 只有全局 Wiki |
| none | 无 Wiki |

---

#### 4.2.4 获取变更历史索引

**端点**: `GET /wiki/<slug>/changes_index.json`

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| slug | string | 项目 slug |

**响应（成功）**:
```json
{
  "versions": [
    {
      "version": "v2.2",
      "date": "2026-04-12",
      "summary": "代码审查报告",
      "type": "important",
      "doc_changes": ["docs/review.md"],
      "rtl_changes": [],
      "tb_changes": ["tb/axi_agent.svh"]
    }
  ]
}
```

**响应（无变更历史）**:
```json
{
  "versions": []
}
```

**状态码**:
| 状态码 | 含义 |
|--------|------|
| 200 | 成功（即使无内容也返回 200） |

---

## 4.3 后端辅助函数

### slug 生成规则

前后端必须使用相同的 slug 生成规则：

```python
import re

def get_project_slug(project_name: str) -> str:
    """
    项目名转 slug，用于 Wiki 目录命名
    规则：
    1. 转小写
    2. 移除特殊字符（只保留字母、数字、空格、连字符）
    3. 空格/连字符转为下划线
    """
    slug = project_name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)      # 移除特殊字符
    slug = re.sub(r'[-\s]+', '_', slug)         # 空格/连字符转下划线
    slug = slug.strip('_')                      # 移除首尾下划线
    return slug

# 示例：
# "SPI-to-APB Bridge" → "spi_to_apb_bridge"
# "USB3.0 Controller" → "usb3_controller"
# "Project @#$%" → "project__"
```

```javascript
// 前端 JavaScript 实现
function getProjectSlug(projectName) {
    return projectName
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '')      // 移除特殊字符
        .replace(/[-\s]+/g, '_')       // 空格/连字符转下划线
        .replace(/^_+|_+$/g, '');      // 移除首尾下划线
}
```

---

## 5. 前端界面设计

### 5.1 Wiki Tab 布局

```
┌─────────────────────────────────────────────────────────────────┐
│ [CP] [TC] [FC] [Progress] [Dashboard] [📚 Wiki]                │
├─────────────────────────────────────────────────────────────────┤
│ [📄 文档] [📊 变更历史] [🔍 搜索]  ← 子导航                    │
├─────────────┬───────────────────────────────┬───────────────────┤
│ 📂 导航树   │                               │ 📢 最近更新        │
│             │                               │                   │
│ 📖 快速开始 │      📄 Wiki 文档内容          │ v2.2 今天         │
│   - Wiki首页│                               │ v2.1 昨天         │
│   - 环境搭建│      [渲染的 HTML 内容]        │                   │
│ 💡 核心概念 │                               │ 📊 变更统计        │
│   - SPI协议 │                               │ ───────────       │
│   - APB协议 │                               │ 📄 +1 🔧 0 🧪+1  │
│ 📋 使用指南 │                               │                   │
│ ❓ 帮助     │                               │                   │
└─────────────┴───────────────────────────────┴───────────────────┘
     220px              flex: 1                    200px
```

### 5.2 Wiki Tab HTML 结构

```html
<!-- Wiki Panel -->
<div id="wikiPanel" style="display: none;">
    <!-- 子导航栏 -->
    <div class="wiki-sub-tabs" role="tablist">
        <button class="wiki-tab-btn active" onclick="switchWikiTab('docs', this)">📄 文档</button>
        <button class="wiki-tab-btn" onclick="switchWikiTab('changes', this)">📊 变更历史</button>
        <button class="wiki-tab-btn" onclick="switchWikiTab('search', this)">🔍 搜索</button>
    </div>

    <!-- 三栏布局 -->
    <div class="wiki-tab-content">
        <div class="wiki-layout">
            <!-- 左侧导航 -->
            <aside class="wiki-nav-panel" id="wikiNavPanel">
                <!-- 动态渲染 -->
            </aside>

            <!-- 中间内容 -->
            <main class="wiki-main-panel">
                <div id="wikiPageContent" class="wiki-page-content">
                    <!-- 动态加载 -->
                </div>
            </main>

            <!-- 右侧信息栏 -->
            <aside class="wiki-info-panel">
                <div class="wiki-info-section">
                    <h4>📢 最近更新</h4>
                    <div id="wikiRecentChanges"></div>
                </div>
            </aside>
        </div>
    </div>
</div>
```

### 5.3 Wiki CSS 样式要点

```css
/* Wiki Tab 容器 */
.wiki-sub-tabs {
    display: flex;
    gap: 5px;
    padding: 10px 15px;
    background: #f8f9fa;
    border-bottom: 1px solid #ddd;
}

/* 三栏布局 */
.wiki-layout {
    display: flex;
    height: calc(100vh - 180px);
}

.wiki-nav-panel {
    width: 220px;
    background: white;
    border-right: 1px solid #ddd;
    padding: 15px;
    overflow-y: auto;
}

.wiki-main-panel {
    flex: 1;
    background: white;
    overflow-y: auto;
}

.wiki-info-panel {
    width: 200px;
    background: #f8f9fa;
    border-left: 1px solid #ddd;
    padding: 15px;
    overflow-y: auto;
}

/* Wiki 内容样式层 */
.wiki-article {
    padding: 20px;
    max-width: 900px;
}

.wiki-article h1 {
    font-size: 24px;
    color: var(--primary-color, #2170bb);
    border-bottom: 2px solid var(--primary-color, #2170bb);
}

/* 加载动画 */
.wiki-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid #ddd;
    border-top-color: var(--primary-color, #2170bb);
    border-radius: 50%;
    animation: wiki-spin 0.8s linear infinite;
}

/* 错误状态 */
.wiki-error {
    text-align: center;
    padding: 40px;
    color: #666;
}

/* 无内容状态 */
.wiki-empty {
    text-align: center;
    padding: 60px;
    color: #999;
}
```

### 5.4 前端 JavaScript 函数

| 函数 | 说明 |
|------|------|
| `switchTab(tab, event)` | Tab 切换，添加 wiki 分支 |
| `getProjectSlug(name)` | 项目名转 slug |
| `loadWiki()` | 加载 Wiki 内容（index.json + 第一页） |
| `loadWikiPage(path)` | 加载指定页面 |
| `switchWikiTab(tab, btn)` | Wiki 子 Tab 切换 |
| `searchWiki()` | 搜索 Wiki（基于 index.json 过滤 title/tags） |
| `fetchWithRetry(url, retries)` | 带重试的 fetch（3 次重试） |
| `renderWikiNav(pages)` | 渲染导航树（按 category 分组） |
| `renderWikiPageContent(html)` | 渲染页面 HTML 内容 |
| `renderWikiChanges(data)` | 渲染变更历史列表 |
| `renderWikiSearchResults(results)` | 渲染搜索结果列表 |
| `renderWikiNoContent()` | 显示无 Wiki 状态 |
| `renderWikiLoading()` | 显示加载动画 |
| `renderWikiError()` | 显示错误状态 + 重试按钮 |
| `updateNavHighlight(path)` | 更新导航高亮 |

---

## 6. 验收标准

### 6.1 Wiki Tab 基本功能

- [ ] Wiki Tab 按钮显示在 Tab 栏（位于 Dashboard 后）
- [ ] 点击切换到 Wiki 视图
- [ ] guest 用户看不到 Wiki Tab

### 6.2 Wiki 后端路由

- [ ] `/wiki/<slug>/index.json` 返回正确的 JSON 格式
- [ ] `/wiki/<slug>/pages/<path>` 返回 HTML 内容
- [ ] 路径遍历攻击被拦截（`../` 等）
- [ ] 项目无 Wiki 时降级到 `_global/`
- [ ] 生产/测试环境 Wiki 隔离

### 6.3 Wiki 文档视图

- [ ] 三栏布局正确显示
- [ ] 左侧导航分组清晰
- [ ] 点击导航加载对应页面
- [ ] 当前页高亮
- [ ] 加载中显示加载动画
- [ ] 加载失败显示错误 + 重试按钮
- [ ] 右侧显示最近更新

### 6.4 Wiki 项目切换联动

- [ ] 切换项目后 Wiki 内容同步刷新
- [ ] 新项目无 Wiki 时降级到全局 Wiki
- [ ] 全局 Wiki 也没有时显示"暂无 Wiki 文档"

### 6.5 Wiki 变更历史

- [ ] 子 Tab 切换正常
- [ ] 变更历史正确显示
- [ ] 筛选功能正常

### 6.6 Wiki 搜索

- [ ] 搜索输入响应 < 100ms
- [ ] 搜索结果正确匹配 title 和 tags
- [ ] 点击结果加载对应页面

### 6.7 Wiki 生命周期管理

- [ ] 项目删除时 Wiki 目录一并删除
- [ ] 删除前 Wiki 内容已归档备份

### 6.8 性能要求

| 指标 | 目标 |
|------|------|
| Wiki Tab 首次切换 | < 1s |
| Wiki 页面切换 | < 500ms |
| 搜索响应 | < 100ms |

---

## 7. 开发计划

### 7.1 开发任务

| 任务 | 状态 | 预计时间 |
|------|------|----------|
| 创建 `app/wiki.py` Blueprint | ⏳ 待实现 | 1h |
| 实现 `/wiki/<slug>/index.json` 路由 | ⏳ 待实现 | 0.5h |
| 实现 `/wiki/<slug>/pages/<path>` 路由 | ⏳ 待实现 | 1h |
| 实现 `/wiki/<slug>/changes_index.json` 路由 | ⏳ 待实现 | 0.5h |
| 实现 `/wiki/exists/<slug>` 路由 | ⏳ 待实现 | 0.5h |
| 路径遍历防护 + CSP Header | ⏳ 待实现 | 0.5h |
| 注册 Blueprint 到 app | ⏳ 待实现 | 0.5h |
| 添加 Wiki Tab HTML/CSS/JS | ⏳ 待实现 | 8h |
| 实现 `loadWiki()`, `loadWikiPage()` 等 | ⏳ 待实现 | 3h |
| 实现子 Tab 切换、搜索 | ⏳ 待实现 | 2h |
| 实现项目切换联动 | ⏳ 待实现 | 1h |
| 准备 `_global/` 示例内容 | ⏳ 待实现 | 4h |
| API 单元测试 | ⏳ 待实现 | 2h |
| UI 集成测试 | ⏳ 待实现 | 2h |
| 回归测试 | ⏳ 待实现 | 2h |

### 7.2 里程碑

| 里程碑 | 计划日期 | 状态 |
|--------|----------|------|
| 后端路由开发完成 | +2 天 | ⏳ 待完成 |
| 前端 Wiki Tab 完成 | +4 天 | ⏳ 待完成 |
| 示例内容完成 | +4.5 天 | ⏳ 待完成 |
| 测试完成 | +5.5 天 | ⏳ 待完成 |
| 发布 | +6 天 | ⏳ 待完成 |

---

## 8. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| index.json 格式错误导致加载失败 | 中 | 低 | 提供模板 + 校验脚本 |
| 浏览器缓存旧版本 Wiki | 中 | 中 | URL 添加版本参数或用户手动刷新 |
| 项目名称含特殊字符导致 slug 不一致 | 中 | 低 | slug 冲突检测 + 警告 |

---

## 9. 相关文档

| 文档 | 路径 |
|------|------|
| 需求分析文档 | `/projects/management/feedbacks/reviewed/requirements_analysis_WIKI_INTEGRATION_v0.13.0_20260412.md` |
| 技术评估 | `/projects/management/feedbacks/reviewed/01_technical_assessment_WIKI_INTEGRATION_v0.13.0.md` |
| 完整性评估 | `/projects/management/feedbacks/reviewed/02_completeness_assessment_WIKI_INTEGRATION_v0.13.0.md` |
| UX 评估 | `/projects/management/feedbacks/reviewed/03_ux_assessment_WIKI_INTEGRATION_v0.13.0.md` |
| 开发规范 | `/projects/management/tracker/docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| API 测试策略 | `/projects/management/tracker/docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| UI 测试策略 | `/projects/management/tracker/docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.13.0 | 2026-04-12 | 初始版本 |

---

**文档创建时间**: 2026-04-12 05:35:00
**创建人**: OpenClaw
