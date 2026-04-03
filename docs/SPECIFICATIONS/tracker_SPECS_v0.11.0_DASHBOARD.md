# Tracker v0.11.0 版本 - CP Dashboard 专项规格书

> **版本**: v0.11.0-dashboard
> **创建日期**: 2026-04-03
> **状态**: 待评审
> **基于**: v0.11.0 初始规格书
> **功能**: CP 覆盖率数据仪表板（Apple 设计风格）

---

## 1. 概述

### 1.1 功能简介

CP Dashboard 是一个新增的数据可视化页面，以 Apple 设计风格展示项目中 Cover Points (CP) 的关键覆盖率指标。页面提供概览卡片、分布图表、趋势分析和待办列表，帮助用户快速掌握项目状态。

### 1.2 设计风格

| 维度 | 规格 |
|------|------|
| 设计语言 | Apple (Human Interface Guidelines) |
| 字体 | 系统字体栈: `-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif` |
| 圆角 | 大圆角 (radius-xl: 16px)，卡片使用 radius-lg (12px) |
| 阴影 | 细微柔和阴影 (shadow-sm/shadow)，无硬边框 |
| 留白 | 大量留白，组件间距 24px+ |
| 动效 | 轻微渐入动画 (300ms ease-out)，数字跳动效果 |
| 配色 | 保持现有紫色主色调 (#4f46e5)，中性灰背景 |

### 1.3 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | Dashboard 页面布局与路由 | P0 | 1h |
| 2 | 后台 API: 获取 Dashboard 统计数据 | P0 | 2h |
| 3 | 概览卡片组件 (4项指标) | P0 | 1h |
| 4 | Feature 覆盖率分布图 | P1 | 2h |
| 5 | Priority 分布卡片 | P1 | 1h |
| 6 | 覆盖率趋势折线图 | P1 | 2h |
| 7 | Top 5 未覆盖 CP 列表 | P1 | 1h |
| 8 | Recent Activity 动态列表 | P2 | 1h |
| 9 | 响应式适配 (移动端) | P2 | 1h |
| | **总计** | | **~12h** |

---

## 2. 页面结构

### 2.1 整体布局

```
┌────────────────────────────────────────────────────────────────────┐
│  Header: Logo / 项目选择器                              [Dashboard] │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Tabs: [CP] [TC] [FC] [Dashboard]                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│  │   总 CP   │ │   已覆盖   │ │   覆盖率   │ │   未关联   │     │
│  │    156    │ │     89     │ │    57%     │ │     12     │     │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘     │
│                                                                    │
│  ┌────────────────────────────────┐ ┌───────────────────────┐    │
│  │                                │ │                       │    │
│  │   Feature 覆盖率分布           │ │   Priority 分布      │    │
│  │   (横向柱状图)                 │ │   (垂直堆叠卡片)     │    │
│  │                                │ │                       │    │
│  └────────────────────────────────┘ └───────────────────────┘    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                                                              │ │
│  │   覆盖率趋势 (折线图)                                         │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌─────────────────────────────┐ ┌─────────────────────────────┐│
│  │   Top 5 未覆盖 CP           │ │   Recent Activity           ││
│  │   1. AXI_TIMEOUT_P0        │ │   + 3 new CPs today         ││
│  │   2. BURST_ALIGN_P0        │ │   + 2 linked to TCs         ││
│  │   3. READ_DATA_ECC_P1      │ │   1 CP marked covered       ││
│  └─────────────────────────────┘ └─────────────────────────────┘│
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 网格系统

| 断点 | 屏幕宽度 | 布局 |
|------|----------|------|
| Mobile | < 640px | 单列堆叠 |
| Tablet | 640-1024px | 2列网格 |
| Desktop | > 1024px | 4列/2列混合 |

### 2.3 组件层级

```
DashboardPage
├── HeaderBar (复用现有)
├── TabBar (复用现有 + Dashboard Tab)
└── DashboardContent
    ├── OverviewCards (4卡片)
    ├── ChartsRow
    │   ├── FeatureCoverageChart
    │   └── PriorityDistribution
    ├── TrendChart (全宽)
    └── ListsRow
        ├── TopUncoveredList
        └── RecentActivityList
```

---

## 3. 功能详细设计

### 3.1 后台 API: 获取 Dashboard 统计数据

**API 设计**:

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/dashboard/stats` | 获取 Dashboard 统计数据 |

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | 是 | 项目 ID |

**响应格式**:
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_cp": 156,
      "covered_cp": 89,
      "coverage_rate": 57.1,
      "unlinked_cp": 12
    },
    "by_feature": [
      {"feature": "AXI", "total": 45, "covered": 32, "rate": 71.1},
      {"feature": "SRAM", "total": 30, "covered": 14, "rate": 46.7},
      {"feature": "CPU", "total": 50, "covered": 43, "rate": 86.0}
    ],
    "by_priority": {
      "P0": {"total": 20, "covered": 15, "rate": 75.0},
      "P1": {"total": 80, "covered": 50, "rate": 62.5},
      "P2": {"total": 56, "covered": 24, "rate": 42.9}
    },
    "trend": [
      {"date": "2026-03-28", "rate": 52.3},
      {"date": "2026-03-29", "rate": 53.1},
      {"date": "2026-03-30", "rate": 54.8},
      {"date": "2026-03-31", "rate": 55.5},
      {"date": "2026-04-01", "rate": 56.2},
      {"date": "2026-04-02", "rate": 57.1}
    ],
    "top_uncovered": [
      {"id": 1, "name": "AXI_TIMEOUT_ERR", "priority": "P0", "feature": "AXI"},
      {"id": 2, "name": "BURST_ALIGN_FAIL", "priority": "P0", "feature": "AXI"},
      {"id": 3, "name": "READ_DATA_ECC_ERR", "priority": "P1", "feature": "SRAM"}
    ],
    "recent_activity": [
      {"type": "cp_added", "count": 3, "timestamp": "2026-04-03T10:30:00"},
      {"type": "cp_linked", "count": 2, "timestamp": "2026-04-03T09:15:00"},
      {"type": "cp_covered", "count": 1, "timestamp": "2026-04-03T08:00:00"}
    ]
  }
}
```

**数据来源说明**:

1. **overview**: 从 `cover_point` 表统计，关联 `tc_cp_connections` 判断是否已覆盖
2. **by_feature**: 按 `cover_point.feature` 分组统计
3. **by_priority**: 按 `cover_point.priority` 分组统计
4. **trend**: 从 `project_progress` 表查询最近7天数据
5. **top_uncovered**: 查询未关联 TC 且未标记 covered 的 CP，按 priority 排序
6. **recent_activity**: 从 `cover_point.created_at` 和变更日志推算

**覆盖判定逻辑**:
- CP 被认为"已覆盖"当且仅当：
  - 关联的 TC 中至少有一个 `status = 'PASS'`
- CP 被认为"未关联"当且仅当：
  - `connected_tcs` 数量为 0

**错误响应**:
```json
{
  "success": false,
  "error": "Project not found",
  "code": "PROJECT_NOT_FOUND"
}
```

**权限**: 需要有效的登录会话。

---

### 3.2 概览卡片组件

**布局**: 4张等宽卡片，横向排列。

**卡片结构**:
```
┌────────────────┐
│  ─────────────  │  <- 细线装饰 (2px, 主色, 8px宽度)
│                │
│     156        │  <- 数值: 32px, font-weight: 700
│                │
│     总 CP      │  <- 标签: 13px, color: text-secondary
│                │
└────────────────┘
```

**Apple 设计细节**:
- 背景: `var(--color-bg-card)` 纯白
- 圆角: `var(--radius-lg)` (12px)
- 阴影: `var(--shadow-sm)`
- 顶部装饰线: 使用 CSS `::before` 伪元素，宽度8px，高度2px
- 数值颜色: 主色 `#4f46e5`
- 数值动画: 页面加载时从0跳动到目标值 (600ms)

**卡片内容**:

| 卡片 | 数值 | 标签 | 装饰线颜色 |
|------|------|------|------------|
| 1 | total_cp | 总 CP | #4f46e5 (主色) |
| 2 | covered_cp | 已覆盖 | #22c55e (绿色) |
| 3 | coverage_rate + % | 覆盖率 | #3b82f6 (蓝色) |
| 4 | unlinked_cp | 未关联 | #ef4444 (红色) |

**空状态**: 数值显示 `--`，标签正常显示。

---

### 3.3 Feature 覆盖率分布图

**类型**: 横向柱状图 (Horizontal Bar Chart)

**布局**:
```
┌─────────────────────────────────────────┐
│  Feature 覆盖率分布                      │  <- 标题
├─────────────────────────────────────────┤
│                                         │
│  AXI     ████████████████░░░░░  72%   │  <- 最高到最低排序
│                                         │
│  SRAM    ██████████░░░░░░░░░░░░  47%   │
│                                         │
│  CPU     ██████████████████████  96%    │
│                                         │
└─────────────────────────────────────────┘
```

**技术实现**:
- 纯 CSS 实现，无外部图表库
- 使用 `<progress>` 元素或 `div` + `width %`
- 柱子最大宽度 200px
- 百分比数字右对齐，固定宽度 40px

**颜色规则**:
| 覆盖率范围 | 柱子颜色 |
|------------|----------|
| >= 80% | #22c55e (绿色) |
| 50% - 79% | #f59e0b (橙色) |
| < 50% | #ef4444 (红色) |

**交互**:
- Hover 时柱子轻微放大 (scale 1.02)
- 显示具体数字 tooltip

---

### 3.4 Priority 分布卡片

**布局**: 3张小卡片垂直排列

```
┌─────────────────────┐
│  P0  Priority       │
│                     │
│  ████████░░  75%    │
│  15 / 20           │
└─────────────────────┘
```

**卡片数量**: 3张 (P0, P1, P2)

**颜色规则**:
| Priority | 颜色 |
|----------|------|
| P0 | #ef4444 (红色) |
| P1 | #f59e0b (橙色) |
| P2 | #22c55e (绿色) |

**显示内容**:
- Priority 标签 (P0/P1/P2)
- 进度条 (显示百分比)
- 数值: `covered / total`

---

### 3.5 覆盖率趋势折线图

**类型**: 简单折线图 (7天数据)

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│  覆盖率趋势 (7天)                                        │
├─────────────────────────────────────────────────────────┤
│     │                                                   │
│ 60% ┤                              ●──                  │
│     │                         ────                      │
│ 50% ┤                    ────                          │
│     │               ────                               │
│ 40% ┤          ────                                    │
│     │    ────                                         │
│ 30% ┤                                                   │
│     └─────────────────────────────────────────────────  │
│        3/28   3/29   3/30   3/31   4/1    4/2    4/3   │
└─────────────────────────────────────────────────────────┘
```

**技术实现**:
- 纯 CSS/SVG 实现
- Y轴: 固定 30% - 70% 范围，自动计算
- X轴: 日期标签
- 数据点: 圆点 (4px)
- 连线: 2px 实线，主色

**空数据处理**:
- 如果不足7天，只显示已有数据
- 如果完全没有数据，显示空状态插画和文字

---

### 3.6 Top 5 未覆盖 CP 列表

**内容**: 按 Priority 和创建时间排序，取前5条

**列表项结构**:
```
┌────────────────────────────────────────┐
│  ●  AXI_TIMEOUT_ERR        P0  AXI   │  <- 圆点颜色按 priority
│     未关联 TC                      >  │
└────────────────────────────────────────┘
```

**显示字段**:
| 字段 | 宽度 | 说明 |
|------|------|------|
| 优先级圆点 | 8px | 左端彩色圆点 |
| CP 名称 | flex | 左对齐 |
| Priority 标签 | 32px | 右对齐 |
| Feature | 60px | 右对齐 |
| 箭头 | 20px | 跳转指示 |

**交互**:
- 点击列表项 → 跳转到 CP Tab 并高亮对应行
- Hover 背景色变化

---

### 3.7 Recent Activity 列表

**内容**: 最近7天的关键活动汇总

**活动类型**:

| type | 图标 | 描述 |
|------|------|------|
| cp_added | + | 新增 CPs |
| cp_linked | 🔗 | 关联 TCs |
| cp_covered | ✓ | 标记已覆盖 |
| tc_pass | ✓ | TC 通过 |
| milestone | ★ | 里程碑更新 |

**列表项结构**:
```
┌────────────────────────────────────────┐
│  +  3 new CPs added today              │
│     10:30 AM                          │
└────────────────────────────────────────┘
```

**时间显示**:
- 24小时内的显示: "10:30 AM" 或 "2 hours ago"
- 超过24小时的显示: "Mar 30"

---

## 4. 前端实现

### 4.1 文件结构

```
dev/
├── app/
│   └── api.py              # 新增 /api/dashboard/stats
├── static/
│   ├── css/
│   │   └── dashboard.css   # 新增 Dashboard 样式
│   └── js/
│       └── dashboard.js    # 新增 Dashboard 逻辑
└── index.html              # 修改: 添加 Dashboard Tab 和内容区
```

### 4.2 新增文件

#### dashboard.css

```css
/* Dashboard 容器 */
.dashboard {
    padding: var(--space-6);
    max-width: var(--container-max);
    margin: 0 auto;
}

/* 概览卡片网格 */
.dashboard-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-6);
}

@media (max-width: 1024px) {
    .dashboard-overview {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .dashboard-overview {
        grid-template-columns: 1fr;
    }
}

/* 单个概览卡片 */
.overview-card {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: var(--space-5);
    position: relative;
    overflow: hidden;
}

.overview-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: var(--space-4);
    width: 32px;
    height: 3px;
    border-radius: 0 0 2px 2px;
}

.overview-card.total::before { background: var(--color-primary); }
.overview-card.covered::before { background: var(--color-success); }
.overview-card.rate::before { background: var(--color-info); }
.overview-card.unlinked::before { background: var(--color-error); }

.overview-value {
    font-size: 2rem;
    font-weight: 700;
    margin-top: var(--space-4);
    font-feature-settings: 'tnum';
    font-variant-numeric: tabular-nums;
}

.overview-label {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    margin-top: var(--space-1);
}

/* 图表行 */
.dashboard-charts {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
}

@media (max-width: 1024px) {
    .dashboard-charts {
        grid-template-columns: 1fr;
    }
}

/* 图表卡片 */
.chart-card {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: var(--space-5);
}

.chart-title {
    font-size: var(--text-base);
    font-weight: 600;
    margin-bottom: var(--space-4);
    color: var(--color-text-primary);
}

/* Feature 覆盖率条 */
.feature-bar-item {
    margin-bottom: var(--space-3);
}

.feature-bar-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--space-1);
    font-size: var(--text-sm);
}

.feature-name {
    font-weight: 500;
}

.feature-rate {
    color: var(--color-text-secondary);
}

.feature-bar {
    height: 8px;
    background: var(--color-bg-secondary);
    border-radius: var(--radius-full);
    overflow: hidden;
}

.feature-bar-fill {
    height: 100%;
    border-radius: var(--radius-full);
    transition: width 600ms cubic-bezier(0.16, 1, 0.3, 1);
}

.feature-bar-fill.high { background: var(--color-success); }
.feature-bar-fill.medium { background: var(--color-warning); }
.feature-bar-fill.low { background: var(--color-error); }

/* Priority 卡片网格 */
.priority-cards {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}

.priority-card {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.priority-dot {
    width: 10px;
    height: 10px;
    border-radius: var(--radius-full);
    flex-shrink: 0;
}

.priority-dot.p0 { background: var(--color-error); }
.priority-dot.p1 { background: var(--color-warning); }
.priority-dot.p2 { background: var(--color-success); }

.priority-info {
    flex: 1;
}

.priority-label {
    font-size: var(--text-sm);
    font-weight: 500;
}

.priority-bar {
    height: 4px;
    background: var(--color-bg-secondary);
    border-radius: var(--radius-full);
    margin-top: var(--space-1);
    overflow: hidden;
}

.priority-bar-fill {
    height: 100%;
    border-radius: var(--radius-full);
}

.priority-value {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    white-space: nowrap;
}

/* 趋势图 */
.trend-card {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: var(--space-5);
    margin-bottom: var(--space-6);
}

.trend-svg {
    width: 100%;
    height: 200px;
}

.trend-line {
    fill: none;
    stroke: var(--color-primary);
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.trend-dot {
    fill: var(--color-primary);
}

.trend-label {
    font-size: 11px;
    fill: var(--color-text-muted);
}

/* 列表行 */
.dashboard-lists {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
}

@media (max-width: 768px) {
    .dashboard-lists {
        grid-template-columns: 1fr;
    }
}

.list-card {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    padding: var(--space-4);
}

.list-item {
    display: flex;
    align-items: center;
    padding: var(--space-2) 0;
    border-bottom: 1px solid var(--color-border);
    cursor: pointer;
    transition: background var(--transition);
}

.list-item:last-child {
    border-bottom: none;
}

.list-item:hover {
    background: var(--color-bg-secondary);
    margin: 0 calc(-1 * var(--space-2));
    padding-left: var(--space-2);
    padding-right: var(--space-2);
    border-radius: var(--radius);
}

.list-icon {
    width: 8px;
    height: 8px;
    border-radius: var(--radius-full);
    margin-right: var(--space-3);
    flex-shrink: 0;
}

.list-content {
    flex: 1;
    min-width: 0;
}

.list-title {
    font-size: var(--text-sm);
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.list-meta {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    margin-top: 2px;
}

.list-tags {
    display: flex;
    gap: var(--space-2);
    flex-shrink: 0;
}

.list-tag {
    font-size: var(--text-xs);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    font-weight: 500;
}

/* Activity 列表 */
.activity-item {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    border-bottom: 1px solid var(--color-border);
}

.activity-item:last-child {
    border-bottom: none;
}

.activity-icon {
    width: 24px;
    height: 24px;
    border-radius: var(--radius-full);
    background: var(--color-bg-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    flex-shrink: 0;
}

.activity-content {
    flex: 1;
}

.activity-text {
    font-size: var(--text-sm);
}

.activity-time {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
}

/* 数字跳动动画 */
@keyframes countUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.overview-value {
    animation: countUp 600ms ease-out;
}

/* 加载状态 */
.dashboard-skeleton {
    background: linear-gradient(
        90deg,
        var(--color-bg-secondary) 25%,
        var(--color-bg-card) 50%,
        var(--color-bg-secondary) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--radius);
}

/* 空状态 */
.dashboard-empty {
    text-align: center;
    padding: var(--space-10);
    color: var(--color-text-muted);
}

.dashboard-empty-icon {
    font-size: 48px;
    margin-bottom: var(--space-3);
    opacity: 0.5;
}
```

#### dashboard.js

```javascript
/**
 * Dashboard Module
 * 获取和渲染 CP Dashboard 数据
 */

const Dashboard = {
    currentProjectId: null,
    data: null,

    // 初始化
    init(projectId) {
        this.currentProjectId = projectId;
        this.loadData();
    },

    // 加载数据
    async loadData() {
        try {
            const response = await fetch(`/api/dashboard/stats?project_id=${this.currentProjectId}`);
            const result = await response.json();

            if (result.success) {
                this.data = result.data;
                this.render();
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            console.error('Dashboard load error:', error);
            this.showError('Failed to load dashboard data');
        }
    },

    // 渲染页面
    render() {
        // 渲染概览卡片
        this.renderOverview();

        // 渲染 Feature 分布
        this.renderFeatureChart();

        // 渲染 Priority 分布
        this.renderPriorityCards();

        // 渲染趋势图
        this.renderTrendChart();

        // 渲染列表
        this.renderTopUncovered();
        this.renderRecentActivity();
    },

    // 渲染概览卡片
    renderOverview() {
        const { overview } = this.data;
        const cards = [
            { key: 'total_cp', label: '总 CP', class: 'total' },
            { key: 'covered_cp', label: '已覆盖', class: 'covered' },
            { key: 'coverage_rate', label: '覆盖率', suffix: '%', class: 'rate' },
            { key: 'unlinked_cp', label: '未关联', class: 'unlinked' }
        ];

        const container = document.getElementById('dashboard-overview');
        container.innerHTML = cards.map(card => `
            <div class="overview-card ${card.class}">
                <div class="overview-value" data-count="${overview[card.key] || 0}">
                    ${overview[card.key] !== undefined ? overview[card.key] : '--'}
                    ${card.suffix || ''}
                </div>
                <div class="overview-label">${card.label}</div>
            </div>
        `).join('');
    },

    // 渲染 Feature 覆盖率图
    renderFeatureChart() {
        const { by_feature } = this.data;
        const container = document.getElementById('feature-chart');

        if (!by_feature || by_feature.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">暂无数据</div>';
            return;
        }

        // 按覆盖率排序
        const sorted = [...by_feature].sort((a, b) => b.rate - a.rate);

        container.innerHTML = sorted.map(item => {
            const level = item.rate >= 80 ? 'high' : (item.rate >= 50 ? 'medium' : 'low');
            return `
                <div class="feature-bar-item">
                    <div class="feature-bar-header">
                        <span class="feature-name">${this.escapeHtml(item.feature)}</span>
                        <span class="feature-rate">${item.rate.toFixed(1)}%</span>
                    </div>
                    <div class="feature-bar">
                        <div class="feature-bar-fill ${level}" style="width: ${item.rate}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // 渲染 Priority 卡片
    renderPriorityCards() {
        const { by_priority } = this.data;
        const container = document.getElementById('priority-cards');

        const priorities = [
            { key: 'P0', color: 'p0' },
            { key: 'P1', color: 'p1' },
            { key: 'P2', color: 'p2' }
        ];

        container.innerHTML = priorities.map(p => {
            const data = by_priority[p.key] || { total: 0, covered: 0, rate: 0 };
            return `
                <div class="priority-card">
                    <div class="priority-dot ${p.color}"></div>
                    <div class="priority-info">
                        <div class="priority-label">${p.key} Priority</div>
                        <div class="priority-bar">
                            <div class="priority-bar-fill ${p.color}" style="width: ${data.rate}%"></div>
                        </div>
                    </div>
                    <div class="priority-value">${data.covered} / ${data.total}</div>
                </div>
            `;
        }).join('');
    },

    // 渲染趋势图
    renderTrendChart() {
        const { trend } = this.data;
        const container = document.getElementById('trend-chart');

        if (!trend || trend.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">暂无趋势数据</div>';
            return;
        }

        // 计算 SVG 坐标
        const width = container.offsetWidth || 600;
        const height = 200;
        const padding = { top: 20, right: 20, bottom: 40, left: 40 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        const rates = trend.map(d => d.rate);
        const minRate = Math.floor(Math.min(...rates) / 10) * 10;
        const maxRate = Math.ceil(Math.max(...rates) / 10) * 10;

        const xStep = chartWidth / (trend.length - 1);
        const yScale = (v) => chartHeight - ((v - minRate) / (maxRate - minRate)) * chartHeight;

        // 生成折线路径
        const pathD = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const y = padding.top + yScale(d.rate);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        }).join(' ');

        // 生成圆点
        const dots = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const y = padding.top + yScale(d.rate);
            return `<circle class="trend-dot" cx="${x}" cy="${y}" r="4" />`;
        }).join('');

        // 生成 X 轴标签
        const labels = trend.map((d, i) => {
            const x = padding.left + i * xStep;
            const date = new Date(d.date);
            const label = `${date.getMonth() + 1}/${date.getDate()}`;
            return `<text class="trend-label" x="${x}" y="${height - 10}" text-anchor="middle">${label}</text>`;
        }).join('');

        container.innerHTML = `
            <svg class="trend-svg" viewBox="0 0 ${width} ${height}">
                <!-- Y 轴 -->
                <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}" stroke="#e4e4e7" />
                <text class="trend-label" x="${padding.left - 5}" y="${padding.top + 5}" text-anchor="end">${maxRate}%</text>
                <text class="trend-label" x="${padding.left - 5}" y="${height - padding.bottom}" text-anchor="end">${minRate}%</text>

                <!-- X 轴 -->
                <line x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}" stroke="#e4e4e7" />

                <!-- 折线 -->
                <path class="trend-line" d="${pathD}" />

                <!-- 数据点 -->
                ${dots}

                <!-- 标签 -->
                ${labels}
            </svg>
        `;
    },

    // 渲染 Top 5 未覆盖
    renderTopUncovered() {
        const { top_uncovered } = this.data;
        const container = document.getElementById('top-uncovered');

        if (!top_uncovered || top_uncovered.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">所有 CP 均已覆盖</div>';
            return;
        }

        const priorityColors = { P0: '#ef4444', P1: '#f59e0b', P2: '#22c55e' };

        container.innerHTML = top_uncovered.map(item => `
            <div class="list-item" onclick="Dashboard.jumpToCP(${item.id})">
                <div class="list-icon" style="background: ${priorityColors[item.priority]}"></div>
                <div class="list-content">
                    <div class="list-title">${this.escapeHtml(item.name)}</div>
                    <div class="list-meta">${this.escapeHtml(item.feature)}</div>
                </div>
                <div class="list-tags">
                    <span class="list-tag" style="background: ${priorityColors[item.priority]}20; color: ${priorityColors[item.priority]}">${item.priority}</span>
                </div>
            </div>
        `).join('');
    },

    // 渲染 Recent Activity
    renderRecentActivity() {
        const { recent_activity } = this.data;
        const container = document.getElementById('recent-activity');

        if (!recent_activity || recent_activity.length === 0) {
            container.innerHTML = '<div class="dashboard-empty">暂无最近活动</div>';
            return;
        }

        const typeConfig = {
            cp_added: { icon: '+', text: (c) => `${c} new CPs added` },
            cp_linked: { icon: '🔗', text: (c) => `${c} CPs linked to TCs` },
            cp_covered: { icon: '✓', text: (c) => `${c} CPs marked covered` },
            tc_pass: { icon: '✓', text: (c) => `${c} TCs passed` },
            milestone: { icon: '★', text: (c) => `Milestone updated` }
        };

        container.innerHTML = recent_activity.map(item => {
            const config = typeConfig[item.type] || { icon: '•', text: () => 'Update' };
            const time = this.formatTime(item.timestamp);

            return `
                <div class="activity-item">
                    <div class="activity-icon">${config.icon}</div>
                    <div class="activity-content">
                        <div class="activity-text">${config.text(item.count)}</div>
                        <div class="activity-time">${time}</div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // 跳转到 CP 详情
    jumpToCP(cpId) {
        switchTab('cp', null);
        setTimeout(() => {
            const el = document.querySelector(`tr[data-cp-id="${cpId}"]`);
            if (el) {
                el.classList.add('cp-highlight');
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                setTimeout(() => el.classList.remove('cp-highlight'), 3000);
            }
        }, 100);
    },

    // 工具函数
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (hours < 1) return 'Just now';
        if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;

        return `${date.getMonth() + 1}/${date.getDate()}`;
    },

    showError(message) {
        const container = document.getElementById('dashboard-content');
        container.innerHTML = `
            <div class="dashboard-empty">
                <div class="dashboard-empty-icon">⚠️</div>
                <div>${this.escapeHtml(message)}</div>
            </div>
        `;
    }
};

// 初始化 Dashboard
window.initDashboard = function(projectId) {
    Dashboard.init(projectId);
};
```

### 4.3 index.html 修改

#### 添加 Dashboard Tab

找到 Tab 定义区域，添加 Dashboard Tab：

```html
<button class="tab" id="cpTab" onclick="switchTab('cp', event)">CP</button>
<button class="tab" id="tcTab" onclick="switchTab('tc', event)">TC</button>
<button class="tab" id="fcTab" onclick="switchTab('fc', event)" style="display: none;">Functional Coverage</button>
<button class="tab" id="dashboardTab" onclick="switchTab('dashboard', event)">Dashboard</button>
```

#### 添加 Dashboard 内容区

在主内容区域添加：

```html
<!-- Dashboard Content -->
<div id="dashboard-content" style="display: none;">
    <div class="dashboard">
        <!-- 概览卡片 -->
        <div id="dashboard-overview" class="dashboard-overview">
            <!-- JS 动态渲染 -->
        </div>

        <!-- 图表行 -->
        <div class="dashboard-charts">
            <!-- Feature 分布 -->
            <div class="chart-card">
                <div class="chart-title">Feature 覆盖率分布</div>
                <div id="feature-chart"></div>
            </div>

            <!-- Priority 分布 -->
            <div class="chart-card">
                <div class="chart-title">Priority 分布</div>
                <div id="priority-cards" class="priority-cards"></div>
            </div>
        </div>

        <!-- 趋势图 -->
        <div class="trend-card">
            <div class="chart-title">覆盖率趋势 (7天)</div>
            <div id="trend-chart"></div>
        </div>

        <!-- 列表行 -->
        <div class="dashboard-lists">
            <!-- Top 5 未覆盖 -->
            <div class="list-card">
                <div class="chart-title">Top 5 未覆盖 CP</div>
                <div id="top-uncovered"></div>
            </div>

            <!-- Recent Activity -->
            <div class="list-card">
                <div class="chart-title">Recent Activity</div>
                <div id="recent-activity"></div>
            </div>
        </div>
    </div>
</div>
```

#### 修改 Tab 切换逻辑

在 `switchTab` 函数中添加 dashboard 处理：

```javascript
function switchTab(tabName, event) {
    // 隐藏所有内容
    document.getElementById('cp-content').style.display = 'none';
    document.getElementById('tc-content').style.display = 'none';
    document.getElementById('fc-content').style.display = 'none';
    document.getElementById('dashboard-content').style.display = 'none';

    // 显示对应内容
    const contentMap = {
        'cp': 'cp-content',
        'tc': 'tc-content',
        'fc': 'fc-content',
        'dashboard': 'dashboard-content'
    };

    const content = document.getElementById(contentMap[tabName]);
    if (content) {
        content.style.display = 'block';
    }

    // 初始化 Dashboard（如果切换到 Dashboard Tab）
    if (tabName === 'dashboard' && currentProjectId) {
        initDashboard(currentProjectId);
    }

    // ... 其他代码
}
```

#### 引入 CSS 和 JS

在 `<head>` 中添加：

```html
<link rel="stylesheet" href="/static/css/dashboard.css">
```

在 `</body>` 前添加：

```html
<script src="/static/js/dashboard.js"></script>
```

---

## 5. 后端 API 实现

### 5.1 新增 API: GET /api/dashboard/stats

**文件**: `dev/app/api.py`

**实现位置**: 在 `get_cp` 路由之后添加

**代码逻辑**:

```python
@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """获取 Dashboard 统计数据"""
    project_id = request.args.get('project_id', type=int)

    if not project_id:
        return jsonify({'success': False, 'error': 'project_id is required'}), 400

    # 验证项目存在
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found', 'code': 'PROJECT_NOT_FOUND'}), 404

    # 1. 概览统计
    all_cps = CoverPoint.query.filter_by(project_id=project_id).all()
    total_cp = len(all_cps)

    covered_cp = 0
    unlinked_cp = 0

    for cp in all_cps:
        connected_tcs = cp.connected_tcs
        if connected_tcs:
            # 检查是否有 PASS 的 TC
            has_pass = any(tc.status == 'PASS' for tc in connected_tcs)
            if has_pass:
                covered_cp += 1
        else:
            unlinked_cp += 1

    coverage_rate = (covered_cp / total_cp * 100) if total_cp > 0 else 0

    # 2. 按 Feature 统计
    from sqlalchemy import func
    feature_stats = db.session.query(
        CoverPoint.feature,
        func.count(CoverPoint.id).label('total')
    ).filter(CoverPoint.project_id == project_id).group_by(CoverPoint.feature).all()

    by_feature = []
    for stat in feature_stats:
        feature_cps = CoverPoint.query.filter_by(project_id=project_id, feature=stat.feature).all()
        covered = 0
        for cp in feature_cps:
            if any(tc.status == 'PASS' for tc in cp.connected_tcs):
                covered += 1
        rate = (covered / stat.total * 100) if stat.total > 0 else 0
        by_feature.append({
            'feature': stat.feature,
            'total': stat.total,
            'covered': covered,
            'rate': rate
        })

    # 3. 按 Priority 统计
    priority_stats = {}
    for p in ['P0', 'P1', 'P2']:
        p_cps = CoverPoint.query.filter_by(project_id=project_id, priority=p).all()
        total = len(p_cps)
        covered = sum(1 for cp in p_cps if any(tc.status == 'PASS' for tc in cp.connected_tcs))
        rate = (covered / total * 100) if total > 0 else 0
        priority_stats[p] = {'total': total, 'covered': covered, 'rate': rate}

    # 4. 趋势数据 (从 project_progress 表)
    progress_records = ProjectProgress.query.filter_by(project_id=project_id)\
        .order_by(ProjectProgress.snapshot_date.desc())\
        .limit(7).all()
    progress_records = reversed(progress_records)  # 旧到新
    trend = [{'date': r.snapshot_date, 'rate': r.actual_coverage or 0} for r in progress_records]

    # 5. Top 5 未覆盖 CP
    uncovered_cps = CoverPoint.query.filter(
        CoverPoint.project_id == project_id
    ).outerjoin(tc_cp_connections).group_by(CoverPoint.id)\
        .having(func.count(tc_cp_connections.c.tc_id) == 0)\
        .order_by(CoverPoint.priority.asc(), CoverPoint.created_at.desc())\
        .limit(5).all()

    top_uncovered = [{
        'id': cp.id,
        'name': cp.cover_point[:50],  # 截断显示
        'priority': cp.priority,
        'feature': cp.feature
    } for cp in uncovered_cps]

    # 6. Recent Activity (简化实现)
    # 实际应从审计日志表获取，此处从 CP 创建时间推算
    from datetime import datetime, timedelta
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

    recent_cps = CoverPoint.query.filter(
        CoverPoint.project_id == project_id,
        CoverPoint.created_at >= week_ago
    ).all()

    recent_activity = []
    if recent_cps:
        recent_activity.append({
            'type': 'cp_added',
            'count': len(recent_cps),
            'timestamp': recent_cps[0].created_at
        })

    return jsonify({
        'success': True,
        'data': {
            'overview': {
                'total_cp': total_cp,
                'covered_cp': covered_cp,
                'coverage_rate': round(coverage_rate, 1),
                'unlinked_cp': unlinked_cp
            },
            'by_feature': by_feature,
            'by_priority': priority_stats,
            'trend': trend,
            'top_uncovered': top_uncovered,
            'recent_activity': recent_activity
        }
    })
```

---

## 6. CSS 变量 (design-system.css 扩展)

在现有 `design-system.css` 末尾添加：

```css
/* ===== Dashboard 扩展 ===== */

/* 容器 */
:root {
    --space-14: 3.5rem;
    --space-16: 4rem;
}

/* Dashboard 专用 */
.dashboard {
    padding: var(--space-6);
    max-width: var(--container-max);
    margin: 0 auto;
}

.dashboard-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-4);
    margin-bottom: var(--space-6);
}

.dashboard-charts {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--space-4);
    margin-bottom: var(--space-6);
}

.dashboard-lists {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
}

/* 响应式 */
@media (max-width: 1024px) {
    .dashboard-overview {
        grid-template-columns: repeat(2, 1fr);
    }
    .dashboard-charts {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .dashboard-overview {
        grid-template-columns: 1fr;
    }
    .dashboard-lists {
        grid-template-columns: 1fr;
    }
}
```

---

## 7. 验收标准

### 7.1 API 验收

| # | 标准 | 状态 |
|---|------|------|
| 1 | GET `/api/dashboard/stats` 返回正确数据结构 | ⏳ |
| 2 | `overview.total_cp` 正确统计项目 CP 总数 | ⏳ |
| 3 | `overview.covered_cp` 正确统计已覆盖 CP (有 PASS TC) | ⏳ |
| 4 | `overview.unlinked_cp` 正确统计未关联 CP | ⏳ |
| 5 | `overview.coverage_rate` 正确计算覆盖率百分比 | ⏳ |
| 6 | `by_feature` 按 feature 分组统计正确 | ⏳ |
| 7 | `by_priority` 按 priority 分组统计正确 | ⏳ |
| 8 | `trend` 返回最近7天的覆盖率数据 | ⏳ |
| 9 | `top_uncovered` 返回按 priority 排序的未覆盖 CP | ⏳ |
| 10 | 未登录访问返回 401 | ⏳ |
| 11 | project_id 不存在返回 404 | ⏳ |

### 7.2 UI 验收

| # | 标准 | 状态 |
|---|------|------|
| 12 | Dashboard Tab 正确显示在 Tab 栏 | ⏳ |
| 13 | 点击 Dashboard Tab 显示 Dashboard 内容 | ⏳ |
| 14 | 概览卡片显示 4 项指标 (总/已覆盖/覆盖率/未关联) | ⏳ |
| 15 | Feature 分布横向柱状图正确渲染 | ⏳ |
| 16 | Priority 分布卡片正确渲染 P0/P1/P2 | ⏳ |
| 17 | 趋势折线图正确显示 7 天数据 | ⏳ |
| 18 | Top 5 未覆盖 CP 列表正确显示 | ⏳ |
| 19 | Recent Activity 列表正确显示 | ⏳ |
| 20 | 点击 Top 5 项跳转到 CP Tab 并高亮 | ⏳ |
| 21 | 移动端布局正确折叠为单列 | ⏳ |
| 22 | 页面加载时数字有跳动动画 | ⏳ |
| 23 | Hover 状态正确响应 | ⏳ |
| 24 | 空数据时显示空状态提示 | ⏳ |

---

## 8. 开发计划

| 任务 | 预估时间 | 状态 | 依赖 |
|------|----------|------|------|
| 实现 GET `/api/dashboard/stats` API | 2h | ⏳ | 无 |
| 创建 dashboard.css 样式文件 | 1h | ⏳ | 无 |
| 创建 dashboard.js 模块 | 1h | ⏳ | 无 |
| 修改 index.html 添加 Tab 和内容区 | 1h | ⏳ | CSS/JS |
| 修改 switchTab 支持 dashboard | 0.5h | ⏳ | HTML |
| 引入 CSS 和 JS 文件 | 0.5h | ⏳ | HTML |
| UI 联调测试 | 1h | ⏳ | 所有任务 |
| 响应式适配测试 | 1h | ⏳ | UI |
| **总计** | **~9h** | | |

---

## 9. 技术备注

### 9.1 性能考虑

- Dashboard 数据每 30 秒自动刷新一次（可选）
- 数字动画使用 CSS `font-variant-numeric: tabular-nums` 保证对齐
- SVG 趋势图使用 viewBox 保持响应式

### 9.2 未来扩展

| 功能 | 说明 |
|------|------|
| TC Dashboard | 类似的 TC 统计数据仪表板 |
| 里程碑追踪 | 关联 project.start_date / end_date |
| 导出报表 | 导出 Dashboard PDF/Excel |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.11.0-dashboard | 2026-04-03 | 初稿创建 |

---

**文档创建时间**: 2026-04-03
**最后更新**: 2026-04-03
**创建人**: Claude Code
