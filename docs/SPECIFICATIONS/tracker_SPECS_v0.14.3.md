# Tracker v0.14.3 规格书

> **版本**: v0.14.3
> **日期**: 2026-05-28
> **功能**: 项目状态报告一键导出
> **署名**: Claude Code

---

## 1. 功能概述

为 Tracker 增加一键导出项目最新状态报告的功能。用户点击"导出报告"按钮后，系统根据当前项目的最新数据生成一份结构化的 Markdown 报告，供用户下载为 `.md` 文件。

**未来扩展**: Phase 2 将支持基于同一数据层生成 PPTX 格式报告。

---

## 2. 需求背景

Tracker 当前支持导出 CP/TC 的 Excel/CSV 原始数据，但缺乏**项目级状态报告**的一键导出能力。芯片验证团队在向管理层或客户汇报时，需要一份结构化的项目状态文稿，汇总关键指标、覆盖状态、执行进度和风险项。

---

## 3. 功能设计

### 3.1 前端入口

在顶部导航栏 `header-actions` 区域新增"📊 导出报告"按钮，与"项目"、"备份"等操作同级。

**交互流程**:
1. 用户点击"导出报告"按钮
2. 前端检查是否已选择项目，未选择则提示
3. 调用后端 API 获取 Markdown 内容
4. 前端用 Blob 创建 `.md` 文件并触发下载

**无需模态框**，一键直达下载。

### 3.2 后端 API

**新增端点**: `GET /api/export/project/<int:project_id>/report`
**权限**: `@login_required`
**返回**: Markdown 文件（`text/markdown; charset=utf-8`）

**实现架构**:
```
GET /api/export/project/<project_id>/report
    |
    v
_get_project_report_data(project_id)    <-- 可复用数据层
    |
    v
_generate_markdown_report(data) -> io.StringIO
    |
    v
send_file() with Content-Disposition: attachment
```

### 3.3 报告结构（8 页）

| 页码 | 标题 | 内容 |
|------|------|------|
| 1 | 封面 | 项目名、生成日期、验证周期、覆盖模式 |
| 2 | 执行摘要 | 核心指标表格（CP/TC 总数、覆盖率、通过率） |
| 3 | CP 覆盖状态 | 按 Priority 统计（P0/P1/P2）+ 未覆盖 CP Top 20 |
| 4 | TC 执行状态 | 按 Status 分布（OPEN/CODED/FAIL/PASS/REMOVED）+ 按 DV Milestone 分布 |
| 5 | Feature 覆盖矩阵 | Feature x Priority 矩阵（covered/total） |
| 6 | Owner 工作分布 | 每人 TC 数、PASS/FAIL/未执行、通过率 |
| 7 | 风险与待办 | 未覆盖 P0 CP、FAIL TC、逾期 OPEN TC、REMOVED TC |
| 8 | 附录 | 完整 CP 列表、完整 TC 列表 |

---

## 4. 技术设计

### 4.1 后端

**新增函数**（`dev/app/api.py`）:

| 函数 | 职责 | 位置 |
|------|------|------|
| `_get_project_report_data(project_id)` | 收集项目报告所需的全部数据，返回纯 Python dict | 插入在静态文件路由之前 |
| `_generate_markdown_report(data)` | 从数据生成 8 页 Markdown 报告 | 同上 |
| `export_project_report(project_id)` | Flask 路由，验证项目并返回 `.md` 文件 | 同上 |

**数据层设计**:
- 复用 `load_projects()` → `get_db()` 的项目查询模式
- 复用 `project.get('coverage_mode', 'tc_cp')` 判断当前模式
- 复用 Dashboard 各端点的 SQL 查询逻辑（stats、matrix、owner、holes）
- 新增：TC 按 DV Milestone 分组统计、逾期 OPEN TC 查询

**返回数据结构** (`_get_project_report_data`):
```python
{
    'project': {'name', 'start_date', 'end_date'},
    'mode': 'tc_cp' | 'fc_cp',
    'generated_at': str,
    'overview': {'total_cp', 'covered_cp', 'coverage_rate', 'unlinked_cp',
                 'tc_total', 'tc_pass', 'tc_fail', 'tc_open', 'tc_coded', 'tc_removed', 'tc_pass_rate'},
    'by_priority': {'P0': {'total', 'covered', 'rate'}, ...},
    'by_feature': [{'feature', 'total', 'covered', 'rate'}],
    'by_dv_milestone': [{'milestone', 'total', 'pass', 'fail', 'open', 'coded', 'removed'}],
    'coverage_matrix': {'features', 'priorities', 'matrix', 'row_totals', 'column_totals'},
    'owner_stats': {'owners': [{'owner', 'tc_total', 'tc_pass', 'tc_fail', 'tc_not_run'}], 'unassigned_count'},
    'coverage_holes': {'critical', 'warning', 'attention'},
    'top_uncovered': [{'id', 'name', 'priority', 'feature'}],
    'overdue_open_tcs': [{'id', 'test_name', 'owner', 'target_date'}],
    'fail_tcs': [{'id', 'test_name', 'testbench', 'owner'}],
    'removed_tcs': [{'id', 'test_name', 'testbench', 'comments'}],
    'full_cp_list': [...],
    'full_tc_list': [...]
}
```

### 4.2 前端

**按钮**（`dev/index.html`，header-actions 区域）:
```html
<button class="header-btn" id="exportReportBtn" onclick="exportProjectReport()">📊 导出报告</button>
```

**JS 函数**:
```javascript
async function exportProjectReport() {
    if (!currentProject) { alert('请先选择一个项目'); return; }
    // fetch API -> Blob -> download .md
}
```

### 4.3 依赖

**Phase 1**: 无新增依赖（纯 Python 标准库 + Flask 现有功能）
**Phase 2**: `python-pptx`（预留）

---

## 5. Phase 2 扩展设计（PPTX）

### 5.1 数据层复用

Phase 1 的 `_get_project_report_data()` 已返回完整结构化数据，Phase 2 无需改动。

### 5.2 新增生成器

```python
def _generate_pptx_report(data):
    from pptx import Presentation
    prs = Presentation()
    # 8 页幻灯片：标题页 + 内容页（文本框 + 表格）
    ...
```

### 5.3 新增端点

`GET /api/export/project/<int:project_id>/report-pptx`

---

## 6. 安全与权限

| 项 | 规则 |
|----|------|
| 权限 | `@login_required` |
| 数据访问 | 仅访问已选择项目的数据库，禁止跨项目访问 |
| 文件生成 | 服务端生成，不缓存敏感数据到磁盘 |

---

## 7. 兼容性

| 项 | 说明 |
|----|------|
| FC-CP 模式 | 报告中的覆盖率计算需兼容 FC-CP 和 TC-CP 两种模式 |
| 空项目 | 报告应优雅处理空项目（显示 0 值） |
| 浏览器 | Blob 下载兼容所有现代浏览器 |

---

## 8. 验收标准

- [ ] 点击"导出报告"按钮下载 `.md` 文件
- [ ] 报告包含 8 个章节，结构清晰
- [ ] 报告数据与 Dashboard 显示一致
- [ ] 未选择项目时给出提示
- [ ] API 测试 100% 通过
- [ ] UI 冒烟测试通过
- [ ] 前端 ESLint 通过
