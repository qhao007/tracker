# Tracker v0.16.0 规格书

> **版本**: v0.16.0
> **创建日期**: 2026-07-21
> **功能**: 材料包自动生成 Validation Summary PPT + 图表标签修复（BUG-112/113）
> **状态**: 已完成
> **署名**: Claude Code

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 说明 |
|---|------|--------|------|
| 1 | Validation Summary PPT 自动生成 | P0 | 导出材料包时在 ZIP 内新增 `summary/validation_summary.pptx`，版式与汇报样张一致 |
| 2 | PPT 模板机制 | P0 | 基于样张的模板文件 + 语义化形状命名，数据按名填充 |
| 3 | 评语规则自动生成 | P1 | 按 P1 覆盖率阈值与 P0 完成度自动生成右下角评语 |
| 4 | 覆盖率环比行 | P1 | 取最近两条快照计算 pp 差值，快照不足时自动删除该行 |
| 5 | Feature 图标签修复 (BUG-112) | P0 | 材料包截图丢失百分比/未覆盖标签 → `afterDraw` 插件 |
| 6 | P0/P1 图百分比标签 (BUG-113) | P0 | 柱顶百分比标注，三条导出路径同时生效 |
| 7 | API 测试 | P0 | 生成器单元测试 12 项 + 材料包 PPT 集成测试 6 项 |

### 1.2 背景

用户向管理层汇报时需要一页 "Functional Validation Summary" PPT（样张：`Tracker_update_example_ppt.pptx`），包含 4 个 KPI 卡片、Feature 覆盖进度图、P0/P1 重点模块对比图和评语。此前这些内容需手工从 Tracker 各处抄数制作。

同时发现两个图表缺陷：材料包导出的 Feature 图缺少百分比/未覆盖标签；P0/P1 图在任何导出路径下都没有百分比标注。

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 材料包 ZIP 内生成 `summary/validation_summary.pptx` | 独立 PPT 导出端点/按钮 |
| 模板法生成（版式与样张一致） | PPT 内图表的服务端渲染（复用前端截图） |
| 覆盖率简单占比口径 | 加权覆盖率口径 |
| 状态文字静态占位（导出后用户编辑） | 导出弹窗备注输入框 |
| 两个图表标签缺陷修复 | 图表配色/版式重设计 |

### 1.4 口径决策（用户确认）

1. 覆盖率保持简单占比（covered/total），不做加权；
2. 右上状态文字为纯占位符，导出后手工编辑；
3. PPT 放入材料包 `summary/` 子目录，不新增导出入口；
4. 材料包与 PPT 内的图表必须带百分比/未覆盖信息（修复 BUG-112/113）。

---

## 2. 需求详情

### 2.1 需求 REQ-PPT-001: Validation Summary PPT 生成

**需求描述**:
导出项目材料包时，自动生成一页 `{项目名}-Functional Validation Summary` 幻灯片，写入 ZIP 的 `summary/validation_summary.pptx`。

**内容映射**:

| 样张元素 | 数据来源 |
|----------|----------|
| 标题 | 项目名 + `-Functional Validation Summary` |
| KPI1 CP 覆盖率 | `_get_project_report_data().overview.coverage_rate`（简单占比） |
| KPI1 环比行 | `project_progress` 最近两条有效快照 `actual_coverage` 差值，格式 `较 M/D ±x.xpp`；不足两条删除该形状 |
| KPI2 已覆盖 CP | `overview.covered_cp` |
| KPI3 未覆盖 CP | `overview.total_cp - covered_cp` |
| KPI4 P0/P1 拆分 | `by_priority.P0.total / P1.total`，占比按 P0+P1 总数计算 |
| 评语 | 规则生成（见 REQ-PPT-003） |
| 状态文字 | 模板静态占位，不修改 |
| 左图 / 右图 | 材料包导出的 `feature` / `p0p1` 图表截图，等比缩放居中于占位区域 |

**异常处理**: PPT 生成失败仅记录警告日志，不影响材料包其他内容；无图表截图时移除模板占位图（不留样张假数据）。

### 2.2 需求 REQ-PPT-002: PPT 模板机制

**需求描述**:
以样张为基础制作模板 `dev/app/templates/validation_summary_template.pptx`，形状重命名为语义名称（KPI 文本框位于组合形状内，需递归遍历）。

**模板构建脚本**: `scripts/build_validation_summary_template.py <样张.pptx>`，更新版式后重新执行即可。

**形状命名**（生成器依赖）: `title`、`kpi_coverage_value/label/delta`、`kpi_covered_value/label`、`kpi_uncovered_value/label`、`kpi_p0p1_value/label/split`、`commentary`、`status_note`、`chart_feature`、`chart_p0p1`。

**文本填充规则**: 保留首个 run 的字体格式，替换文本并清除多余 run/段落。

### 2.3 需求 REQ-PPT-003: 评语规则生成

**规则**:
- 遍历 `coverage_matrix`：P1 覆盖率 `< 70%`（与图表红色档位一致）的 Feature 按覆盖率升序取前 5 个，生成 `{ names } 的 P1 功能覆盖率不高`
- 所有含 P0 的 Feature 均全部覆盖时，追加 `但 P0 核心功能已全部覆盖`；否则提示 `P0 核心功能尚未全部覆盖，需优先补齐`
- 无匹配时兜底：`各 Feature 覆盖率进展正常`

### 2.4 需求 REQ-CHART-001: Feature 图标签修复 (BUG-112)

**问题**: 标签绘制挂在 `animation.onComplete`（动画 1000ms），材料包导出在切换后 300ms 截图导致标签丢失。

**修复**: 迁移至内联插件 `featureCoverageLabels` 的 `afterDraw` 钩子，逐帧绘制，绘制逻辑不变。

### 2.5 需求 REQ-CHART-002: P0/P1 图百分比标签 (BUG-113)

**修复**: 新增内联插件 `p0p1BarValueLabels`，在 `afterDraw` 中基于 `getDatasetMeta()` 的柱体位置，于柱顶绘制 `{value}%`（P0/P1 双数据集）。渲染函数共用，进度页单张导出、批量导出、材料包截图、PPT 内嵌图四者自动一致。

---

## 3. 数据库修改

无。

---

## 4. API 接口设计

无新增端点。行为变更：

### POST /api/export/project/<id>/package

- ZIP 新增条目：`summary/validation_summary.pptx`
- README.md 清单增加对应说明行
- 权限不变（admin）

---

## 5. 前端界面设计

无界面变更。图表渲染内部改动：

- `renderFeatureCoverageChart`：`animation.onComplete` 标签绘制 → 内联插件 `afterDraw`
- `renderP0P1ComparisonChart`：新增柱顶百分比内联插件

---

## 6. 验收标准

| # | 标准 | 验证方式 |
|---|------|----------|
| 1 | ZIP 含 `summary/validation_summary.pptx` 且 python-pptx 可打开 | pytest EXP-API-026 |
| 2 | PPT 标题/KPI 数值与项目数据一致 | pytest EXP-API-027 + PPT-UNIT-001 |
| 3 | 快照 ≥2 条显示环比行，否则删除 | pytest EXP-API-030 / PPT-UNIT-004 |
| 4 | 评语按规则生成 | pytest PPT-UNIT-005~007 |
| 5 | 传入截图时 PPT 嵌入 2 图，未传入时无样张占位图 | pytest EXP-API-028/029 |
| 6 | PPT 生成失败不影响材料包 | pytest EXP-API-031 |
| 7 | 材料包 Feature 图 300ms 截图带百分比/未覆盖标签 | Playwright 人工核验 |
| 8 | P0/P1 图柱顶带百分比 | Playwright 人工核验 |

---

## 7. 开发计划

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 图表标签修复（BUG-112/113） | ✅ 完成 |
| 2 | 模板构建脚本 + 模板生成 | ✅ 完成 |
| 3 | `dev/app/ppt_report.py` 生成器 | ✅ 完成 |
| 4 | 接入材料包导出 + README 清单 | ✅ 完成 |
| 5 | 测试（18 项新增）+ Playwright 端到端核验 | ✅ 完成 |

---

## 8. 风险评估

| 风险 | 等级 | 缓解 |
|------|------|------|
| 新增 python-pptx 依赖 | 低 | 纯 Python 库，requirements.txt 已声明；生成失败有降级保护 |
| 模板形状改名导致生成器失配 | 低 | 构建脚本与生成器共用命名约定；单元测试覆盖 |
| 长项目名/评语溢出文本框 | 低 | 评语限制列 5 个 Feature；文本框保留模板字体自动换行 |
| `afterDraw` 逐帧绘制性能 | 低 | 绘制内容极少（≤20 个标签），无感知开销 |

---

## 9. 相关文档

- `docs/BUGLOG/tracker_BUG_RECORD.md` — BUG-112 / BUG-113
- `docs/SPECIFICATIONS/tracker_SPECS_v0.14.0.md` — 材料包导出
- `docs/SPECIFICATIONS/tracker_SPECS_v0.15.0.md` — 图表截图集成
- `scripts/build_validation_summary_template.py` — 模板构建脚本

---

## 10. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.16.0 | 2026-07-21 | 初始版本 |
