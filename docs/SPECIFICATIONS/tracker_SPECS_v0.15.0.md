# Tracker v0.15.0 规格书

> **版本**: v0.15.0
> **创建日期**: 2026-07-13
> **功能**: Progress Charts 增强（三种图表 + 导出 + 双 Y 轴）+ 项目材料包图表截图集成
> **状态**: 已完成
> **署名**: Claude Code

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 说明 |
|---|------|--------|------|
| 1 | Feature CP 覆盖进度图表 | P0 | 水平堆叠条形图，按 feature 分组展示已覆盖/未覆盖 CP |
| 2 | P0/P1 覆盖率模块对比图表 | P0 | 分组柱状图，聚焦重点模块的 P0/P1 覆盖率对比 |
| 3 | 里程碑趋势组合图表 | P0 | 柱状图 + 双折线图 + 双 Y 轴，展示 TC PASS 与覆盖率趋势 |
| 4 | 图表类型切换 Tab | P0 | Progress Panel 内三种图表一键切换 |
| 5 | 图表导出 PNG | P1 | 单张/全部导出为 PNG 图片 |
| 6 | API 数据扩展 | P0 | `/api/progress/<id>` 返回 `trend` + `feature_coverage` |
| 7 | API 测试 | P0 | pytest 覆盖新增 API 字段与图表截图导出 |
| 8 | UI 集成测试 | P0 | Playwright 验证图表切换与导出功能 |
| 9 | 项目材料包图表截图集成 | P1 | 导出 ZIP 时附带三种图表 PNG |

### 1.2 背景

当前 Tracker 的 Progress Charts 页面仅展示单一的"计划曲线 vs 实际曲线"折线图，覆盖维度单一。芯片验证团队在向管理层汇报时，需要更丰富的可视化能力：按模块的 CP 覆盖进度、重点模块的 P0/P1 覆盖率对比、以及 TC PASS 数量与覆盖率随时间变化的趋势。

同时，项目材料包导出功能（v0.14.0）仅包含文本和表格数据，v0.15.0 将 Progress Charts 的截图自动打包进 ZIP，方便用户直接插入汇报材料。

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| Progress Charts 三种图表渲染与切换 | 后端图表渲染服务 |
| PNG 导出（单张/全部）| PDF 导出 |
| `/api/progress/<id>` 字段扩展 | 新增数据库表 |
| 项目材料包 ZIP 中附带图表截图 | 邮件自动发送材料包 |
| 兼容 TC-CP 与 FC-CP 两种覆盖模式 | 移动端适配优化 |

---

## 2. 需求详情

### 2.1 需求 REQ-PC-001: Feature CP 覆盖进度图表

**需求编号**: REQ-PC-001

**需求描述**:
按模块（feature）展示 CP 的已覆盖/未覆盖数量及覆盖率，使用水平堆叠条形图。

**前端需求**:
- 图表类型为水平堆叠条形图（`indexAxis: 'y'`）
- 绿色条表示已覆盖 CP，灰色条表示未覆盖 CP
- 按 `coverage_pct` 从高到低排序
- 图表标题："Feature CP 覆盖进度"

**后端需求**:
- `/api/progress/<id>` 返回 `feature_coverage` 数组
- 每个元素包含：`feature`, `total_cp`, `covered_cp`, `uncovered_cp`, `coverage_pct`

---

### 2.2 需求 REQ-PC-002: P0/P1 覆盖率模块对比图表

**需求编号**: REQ-PC-002

**需求描述**:
重点模块的 P0 与 P1 覆盖率对比，使用分组柱状图，并支持颜色阈值。

**前端需求**:
- 图表类型为分组柱状图
- P0 覆盖率使用深绿色
- P1 覆盖率按阈值变色：`<70%` 红色、`70-90%` 黄色、`>=90%` 绿色
- Y 轴范围固定 `0-100%`
- 聚焦 Top 10 低覆盖模块（需同时有 P0 和 P1 CP）

**后端需求**:
- `feature_coverage` 每个元素包含：`p0_total`, `p0_covered`, `p0_coverage`, `p1_total`, `p1_covered`, `p1_coverage`

---

### 2.3 需求 REQ-PC-003: 里程碑趋势组合图表

**需求编号**: REQ-PC-003

**需求描述**:
展示 TC PASS 数量与 CP/P0 覆盖率的时间趋势组合图。

**前端需求**:
- 柱状图表示 TC PASS 数量（左 Y 轴）
- 绿色折线表示 CP 覆盖率（右 Y 轴，`0-100%`）
- 红色折线表示 P0 覆盖率（右 Y 轴，`0-100%`）
- 图表标题："里程碑趋势：TC PASS / CP覆盖率"

**后端需求**:
- `/api/progress/<id>` 返回 `trend` 时间序列数组
- 每个元素包含：`date`, `tc_pass`, `tc_total`, `cp_coverage`, `p0_coverage`, `cp_covered`, `cp_total`

---

### 2.4 需求 REQ-PC-004: 图表类型切换 Tab

**需求编号**: REQ-PC-004

**需求描述**:
在 Progress Panel toolbar 区域增加图表类型切换按钮组。

**前端需求**:
- 三个 Tab："📈 覆盖趋势"、"📊 Feature覆盖"、"📉 P0/P1对比"
- 当前选中 Tab 高亮显示
- 切换时无页面刷新，使用同一 Canvas 重新渲染
- 状态变量 `currentChartType` 记录当前类型

---

### 2.5 需求 REQ-PC-005: 图表导出 PNG

**需求编号**: REQ-PC-005

**需求描述**:
支持将当前图表或全部图表导出为 PNG 图片。

**前端需求**:
- "导出"按钮带下拉菜单
- "导出当前图表"：下载当前显示图表的 PNG
- "导出全部图表"：依次下载三种图表的 PNG
- 文件名格式：`{chart_type}_{project_name}_{date}.png`
- 使用 Chart.js Canvas 原生 `toDataURL('image/png')` 实现

---

### 2.6 需求 REQ-PC-006: API 数据扩展

**需求编号**: REQ-PC-006

**需求描述**:
扩展现有 `/api/progress/<id>` 端点，返回趋势和 Feature 聚合数据。

**后端需求**:
- `trend` 从 `project_progress` 快照表读取
- `feature_coverage` 实时计算，支持 TC-CP 和 FC-CP 两种模式
- 支持 `priority` 查询参数过滤
- 空项目返回空数组

---

### 2.7 需求 REQ-PC-007: API 测试

**需求编号**: REQ-PC-007

**需求描述**:
使用 pytest 覆盖新增 API 字段与图表截图导出。

**后端需求**:
- `tests/test_api/test_api_progress_charts.py`：验证 trend/feature_coverage 字段与计算逻辑
- `tests/test_api/test_export_package.py`：验证图表截图导出场景

---

### 2.8 需求 REQ-PC-008: UI 集成测试

**需求编号**: REQ-PC-008

**需求描述**:
使用 Playwright 验证图表切换与导出功能。

**前端需求**:
- `tests/test_ui/specs/integration/18-progress-charts.spec.ts`：覆盖三种图表切换、导出菜单、过滤生效、空项目状态

---

### 2.9 需求 REQ-PC-009: 项目材料包图表截图集成

**需求编号**: REQ-PC-009

**需求描述**:
导出项目材料包 ZIP 时，自动附带三种 Progress Charts 的 PNG 截图。

**前端需求**:
- 点击项目选择器中的"导出材料包"按钮时
- 临时切换三种图表类型，捕获 Canvas 截图
- 将 base64 PNG 通过 POST body 发送到后端
- 导出完成后恢复原始界面状态

**后端需求**:
- `POST /api/export/project/<id>/package` 接收 `{charts: {trend, feature, p0p1}}`
- 将 base64 解码后写入 ZIP 的 `charts/` 目录
- 对无效 base64 / 非 PNG 数据进行容错处理

---

## 3. 数据库修改

本版本**无数据库表结构变更**。

复用已有表：
- `cover_point`：CP 基础信息（`feature`, `priority`）
- `test_case` / `tc_cp_connections`：TC-CP 模式下的关联状态
- `functional_coverage` / `fc_cp_association`：FC-CP 模式下的覆盖率
- `project_progress`：趋势时间序列数据

---

## 4. API 接口设计

### 4.1 接口列表

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/progress/<int:project_id>` | 获取项目进度数据（含 trend + feature_coverage） | 已完成 |
| POST | `/api/export/project/<int:project_id>/package` | 导出项目材料包 ZIP（支持图表截图） | 已完成 |

### 4.2 详细 API 规范

#### 4.2.1 获取项目进度数据

**端点**: `GET /api/progress/<int:project_id>`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 否 | 日期过滤起始（YYYY-MM-DD） |
| end_date | string | 否 | 日期过滤结束（YYYY-MM-DD） |
| priority | string | 否 | Priority 过滤，逗号分隔，如 `P0,P1` |

**响应**:
```json
{
  "project_id": 3,
  "project_name": "SOC_DV",
  "start_date": "2026-04-01",
  "end_date": "2026-06-30",
  "planned": [{"week": "2026-04-06", "coverage": 10.0}],
  "actual": [{"week": "2026-04-06", "coverage": 8.5}],
  "priority_filter": "",
  "trend": [
    {
      "date": "2026-04-03",
      "tc_pass": 30,
      "tc_total": 120,
      "cp_coverage": 22.5,
      "p0_coverage": 45.0,
      "cp_covered": 15,
      "cp_total": 52
    }
  ],
  "feature_coverage": [
    {
      "feature": "CCB",
      "total_cp": 45,
      "covered_cp": 44,
      "uncovered_cp": 1,
      "coverage_pct": 97.8,
      "p0_total": 20,
      "p0_covered": 20,
      "p0_coverage": 100.0,
      "p1_total": 15,
      "p1_covered": 14,
      "p1_coverage": 93.3
    }
  ]
}
```

**错误响应**:
```json
{"error": "项目不存在"}
```

**状态码**:
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 404 | 项目不存在 |

#### 4.2.2 导出项目材料包

**端点**: `POST /api/export/project/<int:project_id>/package`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "charts": {
    "trend": "data:image/png;base64,iVBORw0KGgo...",
    "feature": "iVBORw0KGgo...",
    "p0p1": "data:image/png;base64,iVBORw0KGgo..."
  }
}
```

**响应**: `application/zip` 二进制流

**状态码**:
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 401 | 未登录 |
| 403 | 非管理员 |
| 404 | 项目不存在 |

---

## 5. 前端界面设计

### 5.1 页面/组件列表

| 组件 | 功能 | 位置 |
|------|------|------|
| Chart Type Tabs | 三种图表切换 | Progress Panel toolbar |
| Export Dropdown | PNG 导出菜单 | Progress Panel toolbar |
| Progress Chart Canvas | Chart.js 渲染区域 | Progress Panel 主体 |
| Project Search Input | 项目选择器搜索过滤 | Project Modal |

### 5.2 Progress Charts Panel

**布局**:
```
┌─────────────────────────────────────────────────────────────┐
│  Progress Charts                                    [导出 ▼] │
├─────────────────────────────────────────────────────────────┤
│  [📈 覆盖趋势] [📊 Feature覆盖] [📉 P0/P1对比]              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              Chart.js Canvas 渲染区域                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  时间段: [____] - [____]  Priority: [全部 ▼]  [应用] [重置] │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 图表类型 Tab

- 三个按钮横向排列
- 当前选中按钮背景色高亮
- 点击调用 `switchChartType(type)` 重新渲染

### 5.4 导出菜单

- "导出"按钮点击后显示下拉菜单
- 菜单项：
  - 导出当前图表 (PNG)
  - 导出全部图表 (PNG)

### 5.5 项目选择器搜索

- 在项目选择器顶部增加搜索框
- 支持按项目名称实时过滤
- 项目按名称排序（中文按拼音）

---

## 6. 验收标准

### 6.1 Progress Charts 增强

- [x] Progress Charts 面板内可切换三种图表，切换流畅无闪烁
- [x] Feature CP 覆盖进度图：水平条形，绿色=已覆盖，灰色=未覆盖
- [x] P0/P1 对比图：分组柱状，P0 深绿，P1 按阈值变色
- [x] 里程碑趋势图：蓝色柱状（TC PASS）+ 绿色折线（CP 覆盖率）+ 红色折线（P0 覆盖率），双 Y 轴
- [x] 点击"导出"可下载当前图表为 PNG，文件名格式正确
- [x] 日期过滤和 Priority 过滤对三种图表均生效

### 6.2 API 与测试

- [x] `/api/progress/<id>` 正确返回 `trend` 和 `feature_coverage`
- [x] `feature_coverage` 计算覆盖 TC-CP 和 FC-CP 两种模式
- [x] API 测试 100% 通过
- [x] UI 集成测试通过

### 6.3 项目材料包图表集成

- [x] 导出 ZIP 包含 `charts/coverage_trend.png`
- [x] 导出 ZIP 包含 `charts/feature_coverage.png`
- [x] 导出 ZIP 包含 `charts/p0p1_comparison.png`
- [x] 无效图表数据不影响整体导出

---

## 7. 开发计划

### 7.1 开发任务

| 任务 | 负责人 | 状态 | 完成日期 |
|------|--------|------|----------|
| 后端 API 扩展：trend + feature_coverage | Claude Code | 已完成 | 2026-06-02 |
| 前端图表渲染：三个 render 函数 | Claude Code | 已完成 | 2026-06-02 |
| 前端 Tab 切换 + 导出功能 | Claude Code | 已完成 | 2026-06-02 |
| API 测试编写 | Claude Code | 已完成 | 2026-06-02 |
| UI 集成测试编写 | Claude Code | 已完成 | 2026-06-02 |
| 项目材料包图表截图集成 | Claude Code | 已完成 | 2026-07-13 |
| 图表截图导出测试补充 | Claude Code | 已完成 | 2026-07-13 |
| 版本号与规格书更新 | Claude Code | 已完成 | 2026-07-13 |

### 7.2 里程碑

| 里程碑 | 计划日期 | 实际日期 | 状态 |
|--------|----------|----------|------|
| API 开发完成 | 2026-06-02 | 2026-06-02 | 已完成 |
| 前端开发完成 | 2026-06-02 | 2026-06-02 | 已完成 |
| 测试完成 | 2026-06-02 | 2026-07-13 | 已完成 |
| 规格书发布 | 2026-07-13 | 2026-07-13 | 已完成 |

---

## 8. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| feature_coverage 实时计算性能差（CP > 1000） | 中 | 低 | 1) 拆分为独立 API 按需加载；2) 加入内存缓存 |
| Chart.js mixed 图表双 Y 轴显示异常 | 低 | 低 | 固定 y1 轴 `min: 0, max: 100` |
| 导出 PNG 在 Firefox 下 canvas 空白 | 低 | 低 | 确保渲染完成后再调用 `toDataURL`，加 300ms 延迟 |
| 项目材料包导出时图表捕获失败 | 低 | 低 | try/catch 捕获，失败时仍正常导出 ZIP |

---

## 9. 相关文档

| 文档 | 路径 |
|------|------|
| 开发方案 | `docs/PLANS/progress_charts_enhancement_plan_v0.15.0.md` |
| 测试报告 | `docs/REPORTS/TEST_REPORT_v0.15.0_20260602.md` |
| Bug 记录 | `docs/BUGLOG/tracker_BUG_RECORD.md` |
| 开发规范 | `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| 编程标准 | `docs/DEVELOPMENT/coding_standard.md` |
| 测试计划 | `docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md` |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.15.0 | 2026-07-13 | 初始版本：Progress Charts 三图表 + PNG 导出 + 材料包图表截图集成 |

---

**文档创建时间**: 2026-07-13
**创建人**: Claude Code
