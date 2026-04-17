# Tracker Wiki 变更高亮深度集成方案（方案 C）

## 一、设计目标

让 Wiki 的 "变更历史" 从 "纯文本版本号列表" 升级为 "可直接阅读技术洞察内容的入口"，使每次 LLM 迭代产生的 `changes/*.html` 技术高亮页面成为 Wiki 的核心可访问资产。

## 二、改进后的 UI 布局草图

### 2.1 右侧边栏「最近更新」改进

```
┌─────────────────┐
│  📢 最近更新     │
├─────────────────┤
│ 📄 文档洞察      │  ← 新：点击直接加载 changes/doc_change_highlight.html
│ 🧩 RTL 洞察      │  ← 新：点击直接加载 changes/rtl_change_highlight.html
│ 🧪 TB 洞察       │  ← 新：点击直接加载 changes/tb_change_highlight.html
├─────────────────┤
│ ── 版本历史 ──   │
│ v1.2 · 04-16    │  ← 保留：点击切换到「变更历史」Tab
│ v1.1 · 04-15    │
│ v1.0 · 04-14    │
└─────────────────┘
```

- **洞察入口** 使用彩色标签卡片（蓝/橙/绿），永远置顶，最显眼。
- **版本历史** 缩略显示最近 3 条，点击后自动切到「变更历史」Tab 并定位到对应版本。

### 2.2 「变更历史」Tab 改进

当前「变更历史」Tab 只有一行过滤按钮 + 版本列表，内容利用率低。改进后：

```
┌─────────────────────────────────────────────────────────────────┐
│ [全部] [重要] [次要]                                            │
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│ │ 📄 文档洞察   │ │ 🧩 RTL 洞察   │ │ 🧪 TB 洞察    │  ← 顶部卡片区 │
│ │ 查看本次迭代  │ │ 查看本次迭代  │ │ 查看本次迭代  │             │
│ │ 对规格/文档   │ │ 对 RTL 设计   │ │ 对验证平台    │             │
│ │ 的修改与说明  │ │ 的修改与说明  │ │ 的修改与说明  │             │
│ └──────────────┘ └──────────────┘ └──────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│ v1.2 · 2025-04-16 · [重要]                                      │
│ 新增 APB 错误处理覆盖点                                          │
│     📄 文档: 更新 testplan.md                                    │
│     🧩 RTL:  修复 apb_fsm 状态跳转                               │
│     🧪 TB:   新增 apb_error_seq                                  │
│ ─────────────────────────────────                               │
│ v1.1 · 2025-04-15 · [次要]                                      │
│ 优化序列命名规范                                                 │
│ ...                                                             │
└─────────────────────────────────────────────────────────────────┘
```

**核心变化**：
1. **顶部新增 3 张洞察卡片**，点击后直接在当前 Tab 的内嵌区域渲染对应 HTML 内容。
2. **版本列表下方保留**，但每个版本的 `doc_changes`/`rtl_changes`/`tb_changes` 数组前增加可点击的小图标，点击后同样加载对应的高亮页面（并自动滚动到顶部）。
3. **如果某类洞察文件不存在**，对应卡片/链接自动隐藏或显示"暂无"状态。

## 三、具体代码修改方案

### 3.1 修改文件

- **目标文件**：`/projects/management/tracker/dev/index.html`
- **修改范围**：`<style>` 中的 Wiki 相关 CSS + `wikiPanel` HTML 结构 + `<script>` 中的 Wiki 渲染函数

### 3.2 HTML 结构修改

#### A) 右侧边栏 `wiki-info-panel` 结构调整

将目前的单区块：

```html
<aside class="wiki-info-panel">
    <div class="wiki-info-section">
        <h4>📢 最近更新</h4>
        <div id="wikiRecentChanges"></div>
    </div>
</aside>
```

改为双区块：

```html
<aside class="wiki-info-panel">
    <!-- 洞察快速入口 -->
    <div class="wiki-info-section">
        <h4>🔍 变更洞察</h4>
        <div id="wikiHighlightLinks">
            <a class="wiki-highlight-link doc" onclick="loadWikiPage('changes/doc_change_highlight.html')">📄 文档洞察</a>
            <a class="wiki-highlight-link rtl" onclick="loadWikiPage('changes/rtl_change_highlight.html')">🧩 RTL 洞察</a>
            <a class="wiki-highlight-link tb" onclick="loadWikiPage('changes/tb_change_highlight.html')">🧪 TB 洞察</a>
        </div>
    </div>
    <!-- 版本历史 -->
    <div class="wiki-info-section">
        <h4>📢 最近更新</h4>
        <div id="wikiRecentChanges"></div>
    </div>
</aside>
```

> 注： insight 链接的显隐在 JS 中根据 `wikiIndexData.pages` 动态判断，若不存在对应 path 则隐藏，防止 404。

#### B) 变更历史 Tab 内容区结构升级

在 `renderWikiChangesView()` 中，把原来的纯列表改为 "卡片区 + 列表区" 上下结构：

```html
<div class="wiki-changes-layout">
    <div class="wiki-changes-filter">...现有过滤按钮...</div>

    <!-- 洞察卡片区 -->
    <div class="wiki-highlight-cards" id="wikiHighlightCards">
        <div class="wiki-highlight-card doc" onclick="loadWikiPage('changes/doc_change_highlight.html')">
            <div class="wiki-highlight-icon">📄</div>
            <div class="wiki-highlight-title">文档洞察</div>
            <div class="wiki-highlight-desc">查看每次迭代对设计文档、测试计划、用户指南的修改与技术说明</div>
        </div>
        <div class="wiki-highlight-card rtl" onclick="..."> ... </div>
        <div class="wiki-highlight-card tb" onclick="..."> ... </div>
    </div>

    <!-- 版本时间线 -->
    <div id="wikiChangesList"></div>
</div>
```

### 3.3 CSS 新增/修改

在现有 `<style>` 的 Wiki 段落后追加以下样式：

```css
/* ========== 右侧边栏洞察链接 ========== */
.wiki-highlight-link {
    display: block;
    padding: 8px 10px;
    margin-bottom: 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: transform .1s, box-shadow .1s;
    text-decoration: none;
}
.wiki-highlight-link:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.wiki-highlight-link.doc { background: #e0f2fe; color: #0369a1; border-left: 3px solid #0ea5e9; }
.wiki-highlight-link.rtl { background: #ffedd5; color: #9a3412; border-left: 3px solid #f97316; }
.wiki-highlight-link.tb  { background: #dcfce7; color: #166534; border-left: 3px solid #22c55e; }
.wiki-highlight-link.hidden { display: none; }

/* ========== 变更历史 Tab 洞察卡片 ========== */
.wiki-highlight-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}
.wiki-highlight-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: box-shadow .15s, border-color .15s;
    background: white;
}
.wiki-highlight-card:hover {
    border-color: var(--color-primary, #4f46e5);
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.wiki-highlight-card.doc { border-top: 4px solid #0ea5e9; }
.wiki-highlight-card.rtl { border-top: 4px solid #f97316; }
.wiki-highlight-card.tb  { border-top: 4px solid #22c55e; }
.wiki-highlight-icon { font-size: 22px; margin-bottom: 8px; }
.wiki-highlight-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; color: #111827; }
.wiki-highlight-desc  { font-size: 12px; color: #6b7280; line-height: 1.5; }
.wiki-highlight-card.hidden { display: none; }

/* ========== 版本列表中的可点击变更类型标签 ========== */
.wiki-change-details a.change-link {
    color: var(--color-primary, #4f46e5);
    cursor: pointer;
    text-decoration: underline;
}
.wiki-change-details a.change-link:hover {
    color: #3730a3;
}
```

### 3.4 JavaScript 函数修改

#### 1) `renderWikiNav(pages)` — 排除 changes 页面

变更洞察页面不应该出现在左侧文档导航中，否则破坏导航语义。修改 `renderWikiNav`：

```javascript
function renderWikiNav(pages) {
    // ...现有代码...
    const groups = {};
    pages.forEach(page => {
        // 排除 changes 目录下的独立洞察页面，避免出现在文档导航
        if (page.path.startsWith('changes/') && page.path.endsWith('_change_highlight.html')) {
            return;
        }
        const category = page.category || 'root';
        // ...
    });
    // ...
}
```

#### 2) `renderWikiChanges(versions)` — 右侧边栏增加洞察链接显隐控制

```javascript
function renderWikiChanges(versions) {
    const container = document.getElementById('wikiRecentChanges');
    // ... 现有版本渲染逻辑不变 ...

    // 新增：根据 index.json 判断哪些洞察页面真实存在
    const hasPage = (path) => wikiIndexData && wikiIndexData.pages.some(p => p.path === path);
    document.querySelectorAll('#wikiHighlightLinks .wiki-highlight-link').forEach(link => {
        const onclick = link.getAttribute('onclick') || '';
        const match = onclick.match(/loadWikiPage\('([^']+)'\)/);
        if (match && !hasPage(match[1])) {
            link.classList.add('hidden');
        } else {
            link.classList.remove('hidden');
        }
    });
}
```

#### 3) `renderWikiChangesView()` — 顶部插入洞察卡片

```javascript
async function renderWikiChangesView() {
    const pageContent = document.getElementById('wikiPageContent');
    pageContent.innerHTML = `
        <div class="wiki-changes-layout">
            <div class="wiki-changes-filter">
                <button class="active" onclick="filterChanges('all', this)">全部</button>
                <button onclick="filterChanges('important', this)">重要</button>
                <button onclick="filterChanges('minor', this)">次要</button>
            </div>
            <div class="wiki-highlight-cards" id="wikiHighlightCards">
                <div class="wiki-highlight-card doc" data-path="changes/doc_change_highlight.html">
                    <div class="wiki-highlight-icon">📄</div>
                    <div class="wiki-highlight-title">文档洞察</div>
                    <div class="wiki-highlight-desc">查看每次迭代对设计文档、测试计划、用户指南的修改与技术说明</div>
                </div>
                <div class="wiki-highlight-card rtl" data-path="changes/rtl_change_highlight.html">
                    <div class="wiki-highlight-icon">🧩</div>
                    <div class="wiki-highlight-title">RTL 洞察</div>
                    <div class="wiki-highlight-desc">查看每次迭代对 RTL 设计、接口、状态机的修改与影响分析</div>
                </div>
                <div class="wiki-highlight-card tb" data-path="changes/tb_change_highlight.html">
                    <div class="wiki-highlight-icon">🧪</div>
                    <div class="wiki-highlight-title">TB 洞察</div>
                    <div class="wiki-highlight-desc">查看每次迭代对验证平台、序列、测试用例的修改与新增内容</div>
                </div>
            </div>
            <div id="wikiChangesList"></div>
        </div>`;

    // 绑定卡片点击事件
    pageContent.querySelectorAll('.wiki-highlight-card').forEach(card => {
        card.addEventListener('click', () => {
            const path = card.getAttribute('data-path');
            if (path) {
                // 切回 docs tab 并在主内容区加载该页面（保持左右布局可见）
                switchWikiTab('docs', document.querySelector('.wiki-tab-btn'));
                loadWikiPage(path);
            }
        });
    });

    // 新增：根据 index.json 显隐卡片
    const hasPage = (path) => wikiIndexData && wikiIndexData.pages.some(p => p.path === path);
    pageContent.querySelectorAll('.wiki-highlight-card').forEach(card => {
        const path = card.getAttribute('data-path');
        if (path && !hasPage(path)) {
            card.classList.add('hidden');
        }
    });

    // ... 后续加载 changes_index.json 逻辑不变 ...
}
```

#### 4) `renderChangesList(versions)` — 版本详情中的变更类型增加可点击链接

将原先纯文本的 `doc_changes`/`rtl_changes`/`tb_changes` 升级为：点击对应类型图标/文字，加载对应的高亮页面。

```javascript
function renderChangesList(versions) {
    const container = document.getElementById('wikiChangesList');
    if (!versions || versions.length === 0) {
        container.innerHTML = '<div class="wiki-empty">暂无变更记录</div>';
        return;
    }

    const hasPage = (path) => wikiIndexData && wikiIndexData.pages.some(p => p.path === path);

    let html = '';
    versions.forEach(v => {
        const docLink = hasPage('changes/doc_change_highlight.html')
            ? `<span class="change-link" onclick="goToWikiPage('changes/doc_change_highlight.html')">📄 文档变更</span>`
            : '📄 文档变更';
        const rtlLink = hasPage('changes/rtl_change_highlight.html')
            ? `<span class="change-link" onclick="goToWikiPage('changes/rtl_change_highlight.html')">🧩 RTL 变更</span>`
            : '🧩 RTL 变更';
        const tbLink = hasPage('changes/tb_change_highlight.html')
            ? `<span class="change-link" onclick="goToWikiPage('changes/tb_change_highlight.html')">🧪 TB 变更</span>`
            : '🧪 TB 变更';

        html += `<div class="wiki-change-item">
            <div class="wiki-change-header">
                <span class="wiki-change-version">${v.version}</span>
                <span class="wiki-change-date">${v.date}</span>
            </div>
            <div class="wiki-change-summary">
                <span class="wiki-change-type ${v.type}">${v.type === 'important' ? '重要' : '次要'}</span>
                ${v.summary}
            </div>
            <div class="wiki-change-details">
                ${v.doc_changes && v.doc_changes.length ? `<div>${docLink}: ${v.doc_changes.join(', ')}</div>` : ''}
                ${v.rtl_changes && v.rtl_changes.length ? `<div>${rtlLink}: ${v.rtl_changes.join(', ')}</div>` : ''}
                ${v.tb_changes && v.tb_changes.length ? `<div>${tbLink}: ${v.tb_changes.join(', ')}</div>` : ''}
            </div>
        </div>`;
    });
    container.innerHTML = html;
}
```

## 四、`changes_index.json` 与 `changes/*.html` 的关联逻辑

当前 `changes_index.json` 的数据结构：

```json
{
  "versions": [
    {
      "version": "v1.2",
      "date": "2025-04-16",
      "summary": "新增 APB 错误处理",
      "type": "important",
      "doc_changes": [...],
      "rtl_changes": [...],
      "tb_changes": [...]
    }
  ]
}
```

改进后的关联方式（**无需修改 JSON 结构**）：

| `changes_index.json` 字段 | 对应的 HTML 页面 | 前端映射规则 |
|--------------------------|------------------|--------------|
| `doc_changes` 数组 | `changes/doc_change_highlight.html` | 硬编码 +  existence check |
| `rtl_changes` 数组 | `changes/rtl_change_highlight.html` | 硬编码 +  existence check |
| `tb_changes` 数组 | `changes/tb_change_highlight.html` | 硬编码 +  existence check |

**为什么不需要改 JSON**：
- `build.py` 已经将 3 个 `changes/*.md` 文件编译成了 HTML 并写入了 `index.json`。
- Tracker 前端已经能通过 `wikiIndexData.pages` 判断这些页面是否存在。
- 通过硬编码的约定映射（`doc`→`doc_change_highlight.html` 等），即可把版本条目里的变更类型和实际可读的洞察文章关联起来。

## 五、部署步骤

### Step 1: 备份现有 `index.html`

```bash
ssh -o StrictHostKeyChecking=no claude_ai@124.221.165.134 \
  "cp /projects/management/tracker/dev/index.html /projects/management/tracker/dev/index.html.bak.$(date +%Y%m%d_%H%M%S)"
```

### Step 2: 本地生成修改后的 `index.html`

将上述 CSS、HTML、JS 修改点合并到现有的 `index.html` 中，生成 `index.html.new`。

### Step 3: 上传覆盖

```bash
scp -o StrictHostKeyChecking=no -i C:/Users/haoq/.ssh/id_rsa \
  index.html.new \
  claude_ai@124.221.165.134:/projects/management/tracker/dev/index.html
```

### Step 4: 验证

1. 打开 Tracker 项目页面 → Wiki Tab。
2. 确认右侧边栏出现「变更洞察」区块，且 3 个链接可点击并正确加载 HTML。
3. 点击「变更历史」子 Tab，确认顶部出现 3 张洞察卡片。
4. 在版本列表中，确认 `文档变更`/`RTL 变更`/`TB 变更` 文字变为可点击链接。
5. 如果某项目 Wiki 没有这 3 个 HTML 文件，确认对应卡片/链接自动隐藏，不报错。

## 六、回滚策略

若上线后发现问题，30 秒内可回滚：

```bash
ssh -o StrictHostKeyChecking=no claude_ai@124.221.165.134 \
  "cp /projects/management/tracker/dev/index.html.bak.XXXXXX /projects/management/tracker/dev/index.html"
```

其中 `XXXXXX` 为备份时间戳，可通过 `ls -la /projects/management/tracker/dev/index.html.bak.*` 查看。

## 七、兼容性说明

- **无破坏性变更**：现有 `changes_index.json` 结构、Wiki build 流程、`upload.py` 均无需修改。
- **向后兼容**：如果旧项目 Wiki 没有 `changes/*_change_highlight.html` 页面，对应 UI 元素会自动隐藏，不影响正常使用。
- **跨项目通用**：所有使用 tracker-wiki-update 技能部署的项目都会自动享受此改进，因为洞察页面的命名约定是统一的。
