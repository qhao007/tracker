# Tracker Wiki 运维操作指南

> **版本**: v1.0
> **创建日期**: 2026-04-12
> **适用版本**: v0.13.0+

---

## 1. 概述

Wiki 是 Tracker v0.13.0 新增的文档管理功能，用于在 Tracker 内部展示项目相关的技术文档（如协议规范、验证环境架构、使用指南、变更历史等）。

### 1.1 Wiki 存储位置

```
shared/data/
├── user_data/           # 生产环境 Wiki
│   └── wiki/
│       ├── _global/      # 全局 Wiki（所有项目共享）
│       └── {project}/    # 项目专属 Wiki
│
└── test_data/           # 测试环境 Wiki
    └── wiki/            # 结构同上
```

**重要**: 代码通过符号链接访问 Wiki 目录：
- 开发/测试环境：`dev/data/` → `../shared/data/test_data`
- 生产环境：`data/` → `../shared/data/user_data`

代码始终使用 `data/wiki/` 路径，无需修改。

---

## 2. 目录结构

### 2.1 项目 Wiki 目录

每个项目的 Wiki 目录结构：

```
{project_slug}/                  # 项目 slug 目录
├── index.json                   # Wiki 索引文件
├── changes_index.json           # 变更历史索引
└── pages/                       # Wiki 页面目录
    ├── index.html               # 首页
    ├──概念目录/
    │   └── concept.html          # 概念页面
    └── 验证目录/
        └── verification.html     # 验证文档
```

### 2.2 全局 Wiki 目录

`_global/` 目录用于存放所有项目共享的文档：

```
_global/
├── index.json
├── pages/
│   ├── index.html               # 全局首页
│   ├── faq.html                 # 常见问题
│   └── getting-started.html     # 入门指南
```

### 2.3 归档目录

删除项目 Wiki 时，系统会自动将内容备份到 `_archived/` 目录：

```
_wiki/
├── _archived/
│   └── {slug}_{timestamp}}_deleted/   # 归档备份
│       ├── index.json
│       └── pages/
└── {slug}/                      # 活动 Wiki
```

---

## 3. index.json 格式

### 3.1 文件结构

```json
{
  "version": "1.0",
  "updated_at": "2026-04-12T10:00:00Z",
  "updated_by": "admin",
  "pages": [
    {
      "path": "index.html",
      "title": "项目首页",
      "category": "root",
      "order": 0,
      "tags": ["首页", "项目"]
    },
    {
      "path": "verification/dv_plan.html",
      "title": "验证计划",
      "category": "verification",
      "order": 1,
      "tags": ["验证", "计划"]
    }
  ]
}
```

### 3.2 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| version | 是 | 格式版本，固定为 "1.0" |
| updated_at | 否 | 最后更新时间 (ISO 8601 格式) |
| updated_by | 否 | 最后更新人 |
| pages | 是 | 页面列表 |
| pages[].path | 是 | 页面路径（相对于 pages/ 目录） |
| pages[].title | 是 | 页面标题（显示在导航中） |
| pages[].category | 否 | 分类（用于导航分组） |
| pages[].order | 否 | 排序序号（数字越小越靠前） |
| pages[].tags | 否 | 标签数组（用于搜索匹配） |

---

## 4. changes_index.json 格式

### 4.1 文件结构

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
    },
    {
      "version": "v2.1",
      "date": "2026-04-01",
      "summary": "新增 AXI 验证用例",
      "type": "minor",
      "doc_changes": [],
      "rtl_changes": [],
      "tb_changes": ["tb/axi_test.svh"]
    }
  ]
}
```

### 4.2 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| versions | 是 | 版本变更列表 |
| versions[].version | 是 | 版本号（如 v1.0, v2.1） |
| versions[].date | 是 | 变更日期 |
| versions[].summary | 是 | 变更摘要 |
| versions[].type | 是 | 变更类型：important/minor |
| versions[].doc_changes | 否 | 文档变更文件列表 |
| versions[].rtl_changes | 否 | RTL 变更文件列表 |
| versions[].tb_changes | 否 | 测试台变更文件列表 |

---

## 5. Wiki 页面 HTML 格式

### 5.1 推荐模板

```html
<article class="wiki-article">
    <h1>页面标题</h1>

    <p>这是正文内容。支持 <strong>粗体</strong>、<em>斜体</em>、<code>代码</code> 等格式。</p>

    <h2>章节标题</h2>
    <p>每个主要章节使用 &lt;h2&gt;，子章节使用 &lt;h3&gt;。</p>

    <h3>子章节</h3>
    <ul>
        <li>列表项 1</li>
        <li>列表项 2</li>
    </ul>

    <h2>代码示例</h2>
    <pre><code>// 代码块
function example() {
    return true;
}</code></pre>

    <h2>表格</h2>
    <table class="wiki-table">
        <thead>
            <tr>
                <th>列1</th>
                <th>列2</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>数据1</td>
                <td>数据2</td>
            </tr>
        </tbody>
    </table>
</article>
```

### 5.2 CSS 样式类

| 类名 | 用途 |
|------|------|
| `.wiki-article` | 文章容器 |
| `.wiki-article h1` | 文章标题（蓝色下划线） |
| `.wiki-table` | 表格样式 |
| `code` | 行内代码 |
| `pre` | 代码块 |

---

## 6. 创建新项目 Wiki

### 6.1 手动创建步骤

**1. 确定项目 slug**

项目名称转换为 slug 的规则：
- 转小写
- 移除特殊字符（只保留字母、数字、空格、连字符）
- 空格/连字符转为下划线
- 移除首尾下划线

示例：
| 项目名称 | slug |
|----------|------|
| SOC_DV | `soc_dv` |
| SPI-to-APB Bridge | `spi_to_apb_bridge` |
| USB3.0 Controller | `usb3_controller` |

**2. 创建目录结构**

```bash
# 进入 Wiki 目录（以测试环境为例）
cd /projects/management/tracker/shared/data/test_data/wiki/

# 创建项目 Wiki 目录
mkdir -p my_project/pages/concepts
mkdir -p my_project/pages/verification

# 创建 index.json
cat > my_project/index.json << 'EOF'
{
  "version": "1.0",
  "updated_at": "2026-04-12T10:00:00Z",
  "updated_by": "admin",
  "pages": [
    {
      "path": "index.html",
      "title": "项目首页",
      "category": "root",
      "order": 0,
      "tags": ["首页"]
    },
    {
      "path": "concepts/overview.html",
      "title": "架构概述",
      "category": "concepts",
      "order": 1,
      "tags": ["架构", "概述"]
    }
  ]
}
EOF

# 创建首页
cat > my_project/pages/index.html << 'EOF'
<article class="wiki-article">
    <h1>My Project 首页</h1>
    <p>欢迎使用 My Project 文档。</p>
</article>
EOF
```

**3. 创建变更历史索引（可选）**

```bash
cat > my_project/changes_index.json << 'EOF'
{
  "versions": [
    {
      "version": "v1.0",
      "date": "2026-04-12",
      "summary": "初始版本",
      "type": "important"
    }
  ]
}
EOF
```

### 6.2 创建全局 Wiki

全局 Wiki 存放在 `_global/` 目录，所有项目都可以访问：

```bash
cd /projects/management/tracker/shared/data/test_data/wiki/

# 创建全局 Wiki 目录
mkdir -p _global/pages

# 创建 index.json
cat > _global/index.json << 'EOF'
{
  "version": "1.0",
  "pages": [
    {
      "path": "index.html",
      "title": "全局首页",
      "category": "root",
      "order": 0
    },
    {
      "path": "faq.html",
      "title": "常见问题",
      "category": "support",
      "order": 1,
      "tags": ["FAQ", "帮助"]
    }
  ]
}
EOF
```

---

## 7. 更新现有 Wiki

### 7.1 添加新页面

**1. 添加页面文件**

```bash
cd /projects/management/tracker/shared/data/test_data/wiki/soc_dv/

# 创建新页面
cat > pages/verification/new_feature.html << 'EOF'
<article class="wiki-article">
    <h1>新功能验证</h1>
    <p>描述新功能的验证方法和结果。</p>
</article>
EOF
```

**2. 更新 index.json**

```bash
# 编辑 index.json，添加新页面条目
{
  "pages": [
    ... existing pages ...,
    {
      "path": "verification/new_feature.html",
      "title": "新功能验证",
      "category": "verification",
      "order": 5,
      "tags": ["验证", "新功能"]
    }
  ]
}
```

### 7.2 更新变更历史

```bash
# 编辑 changes_index.json，在 versions 数组开头添加新条目
{
  "versions": [
    {
      "version": "v3.0",
      "date": "2026-04-12",
      "summary": "新增 X 模块验证",
      "type": "important",
      "tb_changes": ["tb/x_module_test.svh"]
    },
    ... existing versions ...
  ]
}
```

---

## 8. 删除项目 Wiki

### 8.1 自动归档

当通过 Tracker UI 删除项目时，对应的 Wiki 目录会自动：
1. 备份到 `_archived/{slug}_{timestamp}}_deleted/` 目录
2. 从活动目录中删除

### 8.2 手动删除（谨慎操作）

```bash
cd /projects/management/tracker/shared/data/test_data/wiki/

# 手动删除项目 Wiki（不会自动归档！）
rm -rf my_project/

# 或者先归档再删除
cp -r my_project _archived/my_project_$(date +%Y%m%d%H%M%S)_deleted
rm -rf my_project/
```

---

## 9. 项目 slug 规则

前后端使用统一的 slug 生成规则：

### Python 实现

```python
import re

def get_project_slug(project_name):
    slug = project_name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)      # 移除特殊字符
    slug = re.sub(r'[-\s]+', '_', slug)       # 空格/连字符转下划线
    slug = slug.strip('_')                     # 移除首尾下划线
    return slug
```

### JavaScript 实现

```javascript
function getProjectSlug(projectName) {
    return projectName
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '')      // 移除特殊字符
        .replace(/[-\s]+/g, '_')       // 空格/连字符转下划线
        .replace(/^_+|_+$/g, '');      // 移除首尾下划线
}
```

### 转换示例

| 项目名称 | slug |
|----------|------|
| SOC_DV | `soc_dv` |
| My Project | `my_project` |
| Test-Project | `test_project` |
| SPI-to-APB Bridge | `spi_to_apb_bridge` |
| USB3.0 Controller | `usb3_controller` |
| Project @#$% | `project` |

---

## 10. 常见问题

### Q: 项目 Wiki 和全局 Wiki 的优先级？

**A**: 项目 Wiki 优先。如果项目没有 Wiki，则降级显示全局 Wiki。如果全局也没有，显示"暂无 Wiki 文档"。

### Q: Wiki 内容支持 Markdown 吗？

**A**: 不支持。Wiki 内容直接是 HTML，可以直接在页面中编写 HTML 标签。

### Q: 如何让所有项目显示同一个 Wiki？

**A**: 可以创建全局 Wiki（`_global/`），但目前不支持让多个项目共享同一个项目级 Wiki。

### Q: Wiki 页面加载失败怎么办？

**A**: 检查：
1. `index.json` 是否存在且格式正确
2. 页面路径是否与 `pages/` 目录下的实际文件匹配
3. 页面文件是否以 `.html` 结尾
4. 浏览器控制台是否有 JavaScript 错误

### Q: 可以链接到其他 Wiki 页面吗？

**A**: 可以使用相对路径或绝对路径链接：
```html
<a href="concepts/architecture.html">架构文档</a>
```

---

## 11. 相关文档

| 文档 | 路径 |
|------|------|
| 版本规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.13.0.md` |
| Wiki 功能测试报告 | `docs/REPORTS/TEST_REPORT_v0.13.0_20260412.md` |
| Bug 记录 | `docs/BUGLOG/tracker_BUG_RECORD.md` |

---

**文档创建时间**: 2026-04-12
**创建人**: Claude Code
