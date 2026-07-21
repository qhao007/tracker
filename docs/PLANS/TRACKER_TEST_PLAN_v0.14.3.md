# Tracker v0.14.3 测试计划

> **版本**: v0.14.3
> **功能**: 项目状态报告一键导出
> **日期**: 2026-05-28
> **署名**: Claude Code

---

## 1. 测试范围

本测试计划覆盖 v0.14.3 新增功能"项目状态报告一键导出"的全部测试活动，包括 API 测试、UI 测试和手工测试。

---

## 2. API 测试

### 2.1 测试文件

`/projects/management/tracker/dev/tests/test_api/test_api_report_export.py`

### 2.2 测试用例

| 用例 ID | 场景 | 请求 | 期望结果 | 优先级 |
|---------|------|------|----------|--------|
| API-REPORT-001 | 正常导出 Markdown | GET /api/export/project/3/report | 200, mimetype=`text/markdown`, 内容含 `#` 和项目名 | P0 |
| API-REPORT-002 | 报告 8 个章节齐全 | GET /api/export/project/3/report | 内容含"统计汇总""覆盖率""Feature""Owner""风险""附录" | P0 |
| API-REPORT-003 | 未登录访问 | GET /api/export/project/3/report | 401 Unauthorized | P0 |
| API-REPORT-004 | 项目不存在 | GET /api/export/project/99999/report | 404, code=`PROJECT_NOT_FOUND` | P0 |
| API-REPORT-005 | 文件名正确 | GET /api/export/project/3/report | Content-Disposition 含项目名和 `.md` | P1 |
| API-REPORT-006 | 数据一致性 | GET /api/export/project/3/report + GET /api/dashboard/stats | 报告中 overview 数值与 dashboard 一致 | P0 |
| API-REPORT-007 | 空项目导出 | GET /api/export/project/{empty_project}/report | 200, 内容含 0 值，不报错 | P1 |

---

## 3. UI 测试

### 3.1 测试文件

`/projects/management/tracker/dev/tests/test_ui/specs/integration/17-report-export.spec.ts`

### 3.2 测试用例

| 用例 ID | 场景 | 操作 | 期望结果 | 优先级 |
|---------|------|------|----------|--------|
| UI-REPORT-001 | 按钮可见 | 登录后选择 SOC_DV 项目 | `#exportReportBtn` 可见，文本为"📊 导出报告" | P0 |
| UI-REPORT-002 | 点击下载 .md | 点击导出报告按钮 | 触发下载，文件名含 `.md` 和项目名 | P0 |
| UI-REPORT-003 | 未选项目提示 | 不选择项目，点击导出报告 | alert 提示"请先选择一个项目" | P0 |
| UI-REPORT-004 | 报告内容验证 | 下载后读取文件内容 | 含项目名、`#` Markdown 标题、CP/TC 数据 | P1 |

---

## 4. 手工测试

### 4.1 测试项

| 测试项 | 工具 | 验证内容 |
|--------|------|----------|
| 按钮样式 | 浏览器 | 与 header 其他按钮风格一致 |
| 报告排版 | 下载的 .md 文件 | Markdown 格式正确，表格对齐 |
| 控制台错误 | agent-browser | 点击按钮后无 JS 报错 |
| 大数据量 | SOC_DV 项目 (30 CP, 52 TC) | 导出时间 < 3 秒 |

---

## 5. 测试通过标准

| 测试类型 | 通过标准 |
|----------|----------|
| API 测试 | 100% 通过，pytest 无失败 |
| UI 冒烟测试 | 100% 通过 |
| 手工测试 | 控制台无关键错误，功能正常 |

---

## 6. 测试环境

| 项 | 值 |
|----|-----|
| 测试服务器 | http://localhost:8081 |
| 测试数据 | test_data (SOC_DV 项目) |
| 测试账号 | admin / admin123 |
| 测试框架 | pytest (API), Playwright (UI) |

---

## 7. 风险与依赖

| 风险 | 缓解措施 |
|------|----------|
| Dashboard 数据查询逻辑变更 | 复用现有查询，不独立实现 |
| 大数据量导出超时 | 测试 SOC_DV (52 TC) 验证性能 |
| FC-CP 模式兼容性 | 测试中验证两种模式的数据正确性 |
