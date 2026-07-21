# Tracker v0.15.0 Progress Charts 增强开发方案

> **版本**: v0.15.0
> **功能**: Progress Charts 三图表展示 + 图表导出
> **创建日期**: 2026-06-02
> **状态**: 待评审
> **预估开发时间**: 1.5 天（后端 4h + 前端 6h + 测试 2h）
> **署名**: Claude Code

---

## 1. 版本概述

### 1.1 背景与目标

当前 Tracker 的 Progress Charts 页面仅展示单一的"计划曲线 vs 实际曲线"折线图，覆盖维度单一。根据用户反馈（`/projects/management/feedbacks/new/` 三张参考图），需要增强图表能力，支持以下三类图表在同一面板内切换展示：

1. **Feature CP 覆盖进度** — 按模块展示 CP 已覆盖/未覆盖数量及覆盖率
2. **P0 / P1 覆盖率模块对比** — 重点模块的 P0 与 P1 覆盖率对比
3. **里程碑趋势** — TC PASS 数量与 CP/P0 覆盖率的时间趋势组合图

同时增加**图表导出为 PNG 图片**功能，方便用户插入报告或邮件分享。

### 1.2 参考图片

| 图片文件 | 图表类型 | 说明 |
|----------|----------|------|
| `coverage_status.png` | 水平堆叠条形图 | Feature 维度 CP 覆盖进度（已覆盖 vs 未覆盖） |
| `coverage_p0_p1_comparison.png` | 分组柱状图 | 模块级 P0/P1 覆盖率对比 |
| `trend_chart.png` | 组合图（柱状+双折线+双Y轴） | 里程碑趋势：TC PASS / CP覆盖率 / P0覆盖率 |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 | 说明 |
|----------|----------|--------|----------|------|
| REQ-PC-001 | Feature CP 覆盖进度图表 | P0 | 3h | 水平堆叠条形图，按 feature 分组 |
| REQ-PC-002 | P0/P1 覆盖率模块对比图表 | P0 | 3h | 分组柱状图，支持颜色阈值 |
| REQ-PC-003 | 里程碑趋势组合图表 | P0 | 3h | 柱状图+双折线图+双Y轴 |
| REQ-PC-004 | 图表类型切换 Tab | P0 | 1h | Progress Panel 内三图表切换 |
| REQ-PC-005 | 图表导出 PNG | P1 | 1h | 单张/全部导出为 PNG 图片 |
| REQ-PC-006 | API 数据扩展 | P0 | 3h | `/api/progress` 返回 feature_coverage + trend |
| REQ-PC-007 | API 测试 | P0 | 1.5h | pytest 覆盖新增 API 字段 |
| REQ-PC-008 | UI 集成测试 | P0 | 1.5h | Playwright 验证图表切换与导出 |

---

## 2. 可行性分析

### 2.1 数据基础评估

| 图表 | 所需数据 | 现有支持 | 可行性 |
|------|----------|----------|--------|
| Feature CP 覆盖进度 | `feature` + CP `coverage_rate` + 已覆盖/未覆盖计数 | `cover_point.feature` 字段已存在；`calculate_current_coverage` 已计算每个 CP 的 coverage_rate；TC-CP 关联表 `tc_cp_connections` 已存在 | **高** — 实时聚合即可 |
| P0/P1 模块对比 | `feature` + `priority` + 平均覆盖率 | `cover_point.priority` (P0/P1/P2) 已存在；`calculate_current_coverage` 已支持按 priority 计算覆盖率 | **高** — 按 feature × priority 分组求平均 |
| 里程碑趋势 | 时间序列：TC PASS 数、CP 覆盖率、P0 覆盖率 | `project_progress` 快照表已有 `tc_pass_count`, `actual_coverage`, `p0_coverage` 等字段（v0.10.0/v0.12.0） | **中高** — 数据已存储，只需 API 透出 |
| 图表导出 PNG | Canvas 转图片 | Chart.js 基于 HTML5 Canvas，原生支持 `toDataURL('image/png')` | **高** — 前端纯实现，零后端依赖 |

### 2.2 技术约束

- **Chart.js 版本**: 当前使用 Chart.js v3/v4（通过 CDN 加载），支持 `indexAxis: 'y'`（水平条形）、`mixed` 组合图表、`yAxisID` 双Y轴
- **无新增依赖**: 无需引入 ECharts、D3 等额外图表库
- **浏览器兼容**: Canvas `toDataURL` 支持 IE9+，满足项目需求

---

## 3. 技术方案

### 3.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Progress Charts Panel                     │
├─────────────────────────────────────────────────────────────┤
│  [📈 覆盖趋势] [📊 Feature覆盖] [📉 P0/P1对比]  [📷 导出▼]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Chart.js Canvas 渲染区域                │   │
│   │                                                     │   │
│   │   根据当前 tab 渲染: line / horizontalBar / bar     │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  时间段: [2026-01-01] - [2026-06-30]  Priority: [全部 ▼]   │
│  [应用] [重置] [快照管理] [刷新快照]                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  GET /api/progress/<project_id>?start_date=...&end_date=... │
│  ─────────────────────────────────────────────────────────  │
│  Response:                                                  │
│  {                                                          │
│    planned: [...],        # 现有：计划曲线                  │
│    actual: [...],         # 现有：实际曲线                  │
│    trend: [...],          # 新增：时间序列数据              │
│    feature_coverage: [...] # 新增：Feature 聚合数据         │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 后端方案

#### 3.2.1 扩展现有 API

**端点**: `GET /api/progress/<int:project_id>`

**现有返回**:
```json
{
  "project_id": 3,
  "project_name": "SOC_DV",
  "start_date": "2026-04-01",
  "end_date": "2026-06-30",
  "planned": [{"week": "2026-04-06", "coverage": 10.0}, ...],
  "actual": [{"week": "2026-04-06", "coverage": 8.5}, ...],
  "priority_filter": ""
}
```

**扩展后新增字段**:

```json
{
  "planned": [...],
  "actual": [...],
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
    },
    ...
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
    },
    ...
  ]
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `trend` | array | 从 `project_progress` 快照表读取的时间序列，按 `snapshot_date` 升序 |
| `trend[].date` | string | 快照日期 `YYYY-MM-DD` |
| `trend[].tc_pass` | int | PASS 状态 TC 数量 |
| `trend[].tc_total` | int | 总 TC 数量 |
| `trend[].cp_coverage` | float | 实际 CP 覆盖率 (0-100) |
| `trend[].p0_coverage` | float | P0 CP 覆盖率 (0-100) |
| `feature_coverage` | array | 按 `cover_point.feature` 分组聚合的实时数据 |
| `feature_coverage[].feature` | string | Feature/模块名称 |
| `feature_coverage[].total_cp` | int | 该 Feature 下总 CP 数 |
| `feature_coverage[].covered_cp` | int | 已覆盖 CP 数（至少一个关联 TC 为 PASS/FAIL） |
| `feature_coverage[].coverage_pct` | float | 平均覆盖率 = Σ(CP coverage_rate) / total_cp |
| `feature_coverage[].p0_coverage` | float | 该 Feature 下 P0 CP 的平均覆盖率 |
| `feature_coverage[].p1_coverage` | float | 该 Feature 下 P1 CP 的平均覆盖率 |

#### 3.2.2 数据计算逻辑

**`trend` 数据生成**（复用现有快照查询逻辑）:

```python
# 从 project_progress 表读取已有字段
SELECT snapshot_date, tc_pass_count, tc_total,
       actual_coverage, p0_coverage, p1_coverage,
       cp_covered, cp_total
FROM project_progress
WHERE project_id = ?
ORDER BY snapshot_date
```

> 说明：`p0_coverage` 字段在 v0.10.0 已添加，`tc_pass_count` 在 v0.8.2 已添加，无需改表结构。

**`feature_coverage` 数据生成**（新增实时计算）:

```python
# 1. 获取项目所有 CP 的基础信息
cursor.execute("""
    SELECT id, feature, priority, cover_point
    FROM cover_point
    WHERE project_id = ?
""", (project_id,))

# 2. 对每个 CP 计算 coverage_rate（复用 calculate_current_coverage 中的逻辑）
#    - TC-CP 模式: 关联 TC 中 PASS/FAIL 数 / 总关联 TC 数
#    - FC-CP 模式: 关联 FC 的 coverage_pct 平均值

# 3. 按 feature 分组聚合
for feature in distinct_features:
    feature_cps = [cp for cp in all_cps if cp.feature == feature]
    total_cp = len(feature_cps)
    covered_cp = sum(1 for cp in feature_cps if cp.coverage_rate > 0)
    coverage_pct = round(sum(cp.coverage_rate for cp in feature_cps) / total_cp, 1)

    # P0/P1 子分组
    p0_cps = [cp for cp in feature_cps if cp.priority == 'P0']
    p0_coverage = round(sum(cp.coverage_rate for cp in p0_cps) / len(p0_cps), 1) if p0_cps else 0
    # 同理 p1...
```

> **性能考虑**: `feature_coverage` 为实时计算，如果项目 CP 数量很大（>1000），考虑：
> 1. 加入缓存（内存级，5分钟过期）
> 2. 或拆分为独立 API `GET /api/progress/<id>/features`，按需加载

#### 3.2.3 备选：独立 API（按需查询）

如果性能测试发现单次请求过慢，可拆分为：

```
GET /api/progress/<project_id>              # 现有：planned + actual
GET /api/progress/<project_id>/trend        # 新增：trend 时间序列
GET /api/progress/<project_id>/features     # 新增：feature_coverage 聚合
```

**推荐先采用扩展现有 API 方案**，若性能不达标再拆分。

---

### 3.3 前端方案

#### 3.3.1 UI 布局变更

在 `index.html` 的 `progressPanel` 内 toolbar 区域增加图表类型切换按钮组：

```html
<!-- 图表类型切换 Tabs -->
<div class="chart-type-tabs" style="display: flex; gap: 4px; margin-right: 16px;">
    <button class="chart-tab active" data-chart="trend" onclick="switchChartType('trend')">📈 覆盖趋势</button>
    <button class="chart-tab" data-chart="feature" onclick="switchChartType('feature')">📊 Feature覆盖</button>
    <button class="chart-tab" data-chart="p0p1" onclick="switchChartType('p0p1')">📉 P0/P1对比</button>
</div>

<!-- 导出按钮 -->
<div class="chart-export" style="position: relative;">
    <button onclick="toggleExportMenu()">📷 导出 ▼</button>
    <div id="exportMenu" style="display: none; position: absolute; ...">
        <button onclick="exportChart('png')">导出当前图表 (PNG)</button>
        <button onclick="exportAllCharts()">导出全部图表 (ZIP)</button>
    </div>
</div>
```

Tab 样式与现有 `dashboard-tabs` 保持一致。

#### 3.3.2 状态管理

```javascript
// 图表类型状态
let currentChartType = 'trend'; // 'trend' | 'feature' | 'p0p1'
let progressChart = null;
let currentProgressData = null;

// 切换图表类型
function switchChartType(type) {
    currentChartType = type;
    // 更新 tab 样式
    document.querySelectorAll('.chart-tab').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.chart === type);
    });
    // 重新渲染
    if (currentProgressData) {
        renderChartByType(currentProgressData);
    }
}

// 根据类型分发渲染
function renderChartByType(data) {
    if (progressChart) progressChart.destroy();
    switch (currentChartType) {
        case 'trend': renderTrendChart(data); break;
        case 'feature': renderFeatureCoverageChart(data); break;
        case 'p0p1': renderP0P1ComparisonChart(data); break;
    }
}
```

#### 3.3.3 图表渲染实现

**图1: 里程碑趋势（改造现有折线图）**

```javascript
function renderTrendChart(data) {
    const ctx = document.getElementById('progressChart').getContext('2d');
    const trend = data.trend || [];

    progressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trend.map(t => t.date),
            datasets: [
                {
                    type: 'bar',
                    label: 'TC PASS',
                    data: trend.map(t => t.tc_pass),
                    backgroundColor: '#a8d5ff',
                    borderColor: '#74b9ff',
                    borderWidth: 1,
                    yAxisID: 'y',
                    order: 3
                },
                {
                    type: 'line',
                    label: 'CP 覆盖率',
                    data: trend.map(t => t.cp_coverage),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: '#28a745',
                    tension: 0.1,
                    yAxisID: 'y1',
                    order: 2
                },
                {
                    type: 'line',
                    label: 'P0 覆盖率',
                    data: trend.map(t => t.p0_coverage),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: '#dc3545',
                    pointStyle: 'rect',
                    tension: 0.1,
                    yAxisID: 'y1',
                    order: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'TC PASS 数量' },
                    beginAtZero: true
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    title: { display: true, text: '覆盖率 (%)' },
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                title: { display: true, text: '里程碑趋势：TC PASS / CP覆盖率' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label;
                            const value = context.parsed.y;
                            if (context.dataset.yAxisID === 'y1') {
                                return `${label}: ${value}%`;
                            }
                            return `${label}: ${value}`;
                        }
                    }
                }
            }
        }
    });
}
```

**图2: Feature CP 覆盖进度（水平堆叠条形图）**

```javascript
function renderFeatureCoverageChart(data) {
    const ctx = document.getElementById('progressChart').getContext('2d');
    const features = data.feature_coverage || [];

    // 按覆盖率排序（从高到低）
    features.sort((a, b) => b.coverage_pct - a.coverage_pct);

    progressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: features.map(f => f.feature),
            datasets: [
                {
                    label: '已覆盖',
                    data: features.map(f => f.covered_cp),
                    backgroundColor: '#28a745',
                    stack: 'stack1'
                },
                {
                    label: '未覆盖',
                    data: features.map(f => f.uncovered_cp),
                    backgroundColor: '#dee2e6',
                    stack: 'stack1'
                }
            ]
        },
        options: {
            indexAxis: 'y', // 水平条形
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    title: { display: true, text: 'CP 数量' }
                },
                y: {
                    stacked: true,
                    title: { display: true, text: 'Feature' }
                }
            },
            plugins: {
                title: { display: true, text: 'Feature CP 覆盖进度' },
                tooltip: {
                    callbacks: {
                        afterBody: function(tooltipItems) {
                            const idx = tooltipItems[0].dataIndex;
                            const pct = features[idx].coverage_pct;
                            return `覆盖率: ${pct}%`;
                        }
                    }
                }
            }
        }
    });
}
```

**图3: P0 / P1 覆盖率模块对比（分组柱状图）**

```javascript
function renderP0P1ComparisonChart(data) {
    const ctx = document.getElementById('progressChart').getContext('2d');
    const features = data.feature_coverage || [];

    // 只展示有 P0 或 P1 CP 的模块
    const filtered = features.filter(f => f.p0_total > 0 || f.p1_total > 0);

    progressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filtered.map(f => f.feature),
            datasets: [
                {
                    label: 'P0 覆盖率',
                    data: filtered.map(f => f.p0_coverage),
                    backgroundColor: '#1e7e34', // 深绿色
                    borderColor: '#1e7e34',
                    borderWidth: 1
                },
                {
                    label: 'P1 覆盖率',
                    data: filtered.map(f => f.p1_coverage),
                    backgroundColor: (ctx) => {
                        const v = ctx.raw;
                        if (v < 70) return '#dc3545';     // 红色: < 70%
                        if (v < 90) return '#ffc107';     // 黄色: 70-90%
                        return '#28a745';                  // 绿色: >= 90%
                    },
                    borderColor: '#999',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: { display: true, text: '覆盖率 (%)' },
                    ticks: { callback: v => v + '%' }
                }
            },
            plugins: {
                title: { display: true, text: 'P0 / P1 覆盖率重点模块对比' },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}%`
                    }
                },
                annotation: {
                    annotations: {
                        line1: {
                            type: 'line',
                            yMin: 100,
                            yMax: 100,
                            borderColor: '#666',
                            borderWidth: 1,
                            borderDash: [5, 5],
                            label: { content: '100%', enabled: true }
                        }
                    }
                }
            }
        }
    });
}
```

> 注：100% 参考虚线使用 `chartjs-plugin-annotation` 插件，或手动在 afterDraw hook 中绘制。若不想引入新插件，可简化去掉。

#### 3.3.4 图表导出 PNG 实现

**可行性**: Chart.js 基于 Canvas，原生支持导出。

```javascript
// 导出当前显示的图表为 PNG
function exportChart(format = 'png') {
    if (!progressChart) {
        alert('暂无图表可导出');
        return;
    }

    const canvas = document.getElementById('progressChart');
    const url = canvas.toDataURL(`image/${format}`);

    const link = document.createElement('a');
    const chartName = {
        'trend': 'milestone_trend',
        'feature': 'feature_cp_coverage',
        'p0p1': 'p0_p1_comparison'
    }[currentChartType];

    link.download = `${chartName}_${currentProject.name}_${new Date().toISOString().slice(0,10)}.png`;
    link.href = url;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 导出全部三张图表（生成 ZIP）
async function exportAllCharts() {
    const types = ['trend', 'feature', 'p0p1'];
    const originalType = currentChartType;
    const images = {};

    for (const type of types) {
        switchChartType(type);
        // 等待渲染完成
        await new Promise(r => setTimeout(r, 300));
        const canvas = document.getElementById('progressChart');
        images[type] = canvas.toDataURL('image/png');
    }

    // 恢复原始图表
    switchChartType(originalType);

    // 使用 JSZip 打包下载（若不想引入 JSZip，可分别下载三张图片）
    // 简化方案：循环调用 exportChart() 三次，分别下载
    for (const [type, url] of Object.entries(images)) {
        const link = document.createElement('a');
        const chartName = {
            'trend': 'milestone_trend',
            'feature': 'feature_cp_coverage',
            'p0p1': 'p0_p1_comparison'
        }[type];
        link.download = `${chartName}_${currentProject.name}_${new Date().toISOString().slice(0,10)}.png`;
        link.href = url;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        await new Promise(r => setTimeout(r, 200));
    }
}
```

> **关于 ZIP 导出**: 若需要单文件 ZIP，可引入 `jszip` + `file-saver` 库（各约 20KB gzip）。考虑到 Tracker 当前无前端构建工具，推荐**简化方案**：分别下载三张 PNG，不打包 ZIP。

---

## 4. 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `dev/app/api.py` | 修改 | 扩展 `get_progress()` 返回 `trend` + `feature_coverage`；新增 `calculate_feature_coverage()` 辅助函数 |
| `dev/index.html` | 修改 | Progress Panel toolbar 增加图表切换 tabs + 导出按钮；新增三个 render 函数；修改 `renderProgressChart()` 为 `renderTrendChart()` |
| `dev/static/js/app_constants.js` | 无需修改 | 无新增 API 端点 |
| `dev/tests/test_api/test_api_progress.py` | 新增/修改 | 验证 `/api/progress` 返回新增字段 |
| `dev/tests/test_ui/specs/integration/17-report-export.spec.ts` 或新增 `18-progress-charts.spec.ts` | 新增 | Playwright 验证图表切换和导出功能 |

---

## 5. 测试计划

### 5.1 API 测试

**测试文件**: `dev/tests/test_api/test_api_progress.py`

| 测试 ID | 测试方法 | 测试目标 | 预期结果 |
|---------|----------|----------|----------|
| PC-API-001 | `test_progress_returns_trend` | `/api/progress/<id>` 返回包含 `trend` 字段 | `trend` 为数组，元素含 `date`, `tc_pass`, `cp_coverage`, `p0_coverage` |
| PC-API-002 | `test_progress_returns_feature_coverage` | `/api/progress/<id>` 返回包含 `feature_coverage` 字段 | `feature_coverage` 为数组，元素含 `feature`, `total_cp`, `covered_cp`, `coverage_pct`, `p0_coverage`, `p1_coverage` |
| PC-API-003 | `test_feature_coverage_calculation` | Feature 覆盖率计算正确 | 已覆盖 CP + 未覆盖 CP = 总 CP；coverage_pct 在 0-100 之间 |
| PC-API-004 | `test_progress_with_empty_project` | 空项目（无 CP）返回正确 | `feature_coverage` 为空数组，`trend` 为空数组 |
| PC-API-005 | `test_progress_priority_filter_with_feature` | Priority 过滤对 feature_coverage 生效 | 只返回符合 Priority 过滤条件的 Feature 数据 |

### 5.2 UI 集成测试

**测试文件**: `dev/tests/test_ui/specs/integration/18-progress-charts.spec.ts`

| 测试 ID | 测试场景 | 步骤 | 预期结果 |
|---------|----------|------|----------|
| PC-UI-001 | 切换 Feature CP 覆盖图表 | 登录 → 选择项目 → 进入 Progress Charts → 点击"Feature覆盖"tab | 显示水平堆叠条形图，X轴为 CP 数量 |
| PC-UI-002 | 切换 P0/P1 对比图表 | 点击"P0/P1对比"tab | 显示分组柱状图，Y轴最大值为 100% |
| PC-UI-003 | 切换回覆盖趋势图表 | 点击"覆盖趋势"tab | 显示组合图表（柱状+两条折线），双Y轴 |
| PC-UI-004 | 导出当前图表为 PNG | 点击"导出"→"导出当前图表" | 触发下载，文件名包含项目名和日期 |
| PC-UI-005 | 日期过滤后图表更新 | 修改日期范围 → 点击"应用" | 图表数据按新日期范围刷新 |

---

## 6. 工作量与排期

| 阶段 | 任务 | 预估工时 | 负责人 |
|------|------|----------|--------|
| **Day 1 上午** | 后端 API 扩展：`trend` + `feature_coverage` | 3h | Claude Code |
| **Day 1 下午** | 前端图表渲染：三个 render 函数 | 3h | Claude Code |
| **Day 2 上午** | 前端 Tab 切换 + 导出功能 | 2h | Claude Code |
| **Day 2 上午** | API 测试编写 | 1.5h | Claude Code |
| **Day 2 下午** | UI 集成测试编写 | 1.5h | Claude Code |
| **Day 2 下午** | 联调测试 + Bug 修复 | 2h | Claude Code |
| **合计** | | **13h (1.5 天)** | |

---

## 7. 风险与应对

| 风险 | 影响 | 可能性 | 应对方案 |
|------|------|--------|----------|
| `feature_coverage` 实时计算性能差（CP > 1000） | 中 | 低 | 1) 拆分为独立 API 按需加载；2) 加入 5 分钟内存缓存 |
| Chart.js mixed 图表双Y轴显示异常 | 低 | 低 | 测试多种数据组合，确保 y1 轴 `min: 0, max: 100` 固定 |
| 导出 PNG 在 Firefox 下 canvas 空白 | 低 | 低 | 确保 canvas 渲染完成后再调用 `toDataURL`，加 300ms 延迟 |
| P0/P1 颜色阈值与用户需求不一致 | 低 | 中 | 阈值参数化（`< 70%` 红，`70-90%` 黄，`>= 90%` 绿），可配置 |

---

## 8. 验收标准

- [ ] Progress Charts 面板内可切换三种图表，切换流畅无闪烁
- [ ] Feature CP 覆盖进度图：水平条形，绿色=已覆盖，灰色=未覆盖，右侧显示覆盖率百分比
- [ ] P0/P1 对比图：分组柱状，P0 深绿，P1 按阈值变色（红/黄/绿）
- [ ] 里程碑趋势图：蓝色柱状（TC PASS）+ 绿色折线（CP 覆盖率）+ 红色折线（P0 覆盖率），双Y轴
- [ ] 点击"导出"可下载当前图表为 PNG，文件名格式：`{chart_type}_{project_name}_{date}.png`
- [ ] 日期过滤和 Priority 过滤对三种图表均生效
- [ ] API 测试 100% 通过
- [ ] UI 集成测试通过（Firefox）

---

*文档结束*
