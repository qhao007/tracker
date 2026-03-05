# Tracker v0.9.0 版本开发规格书

> **版本**: v0.9.0
> **创建日期**: 2026-03-05
> **状态**: 已完成
> **关联需求**: BATCH_REQUESTS_20260305_FRONTEND_UI.md

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | 设计系统 - CSS 变量 | P0 | 2h |
| 2 | 核心组件样式重构 | P0 | 3h |
| 3 | 数据展示组件 | P1 | 3h |
| 4 | 表单组件优化 | P1 | 2h |
| 5 | 动画增强 | P2 | 2h |
| 6 | 样式迁移执行 | P0 | 4h |
| | **总计** | | **~16h** |

### 1.2 背景

v0.8.3 已完成日期必填和测试用户功能。v0.9.0 聚焦于前端界面优化：

- **视觉**: 采用现代 Vercel/Linear 风格
- **统一**: 建立完整的设计系统（颜色、字体、间距）
- **体验**: 添加微交互和动画效果

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 设计系统 CSS 变量 | 后端 API 变更 |
| 组件样式重构 | 数据库结构变更 |
| 动画效果 | 新功能开发 |
| 样式迁移 | 响应式布局 |

---

## 2. 需求详情

### 2.1 功能需求 #1: 设计系统 CSS 变量

**需求编号**: REQ-090-001

**需求描述**:
创建统一的 CSS 变量系统，包括颜色、字体、间距、圆角、阴影等。

**设计系统组成**:

#### 颜色系统

| 类型 | 变量 | 值 |
|------|------|-----|
| 主色 | `--color-primary` | #4f46e5 |
| 主色悬停 | `--color-primary-hover` | #4338ca |
| 主色浅色 | `--color-primary-light` | #e0e7ff |
| 成功 | `--color-success` | #22c55e |
| 警告 | `--color-warning` | #f59e0b |
| 错误 | `--color-error` | #ef4444 |
| 信息 | `--color-info` | #3b82f6 |
| 背景主色 | `--color-bg-primary` | #fafafa |
| 背景卡片 | `--color-bg-card` | #ffffff |
| 文字主色 | `--color-text-primary` | #18181b |

#### 字体系统

```css
:root {
  /* 主字体 - 系统字体兜底 */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  /* 代码字体 */
  --font-mono: 'Cascadia Code', 'Fira Code', Consolas, monospace;
}
```

#### 间距系统

基于 4px 基准: `--space-1: 0.25rem`, `--space-2: 0.5rem`, ...

#### 圆角系统

`--radius-sm: 0.25rem`, `--radius: 0.5rem`, `--radius-lg: 0.75rem`

#### 阴影系统

`--shadow-sm`, `--shadow`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`

### 2.2 功能需求 #2: 核心组件样式重构

**需求编号**: REQ-090-002

**需求描述**:
重构 Header、Tabs、Toolbar、Buttons 等核心组件样式。

#### Header 样式
- 紫色渐变背景 (#4f46e5 → #4338ca)
- 阴影效果 (shadow-md)
- 按钮悬停动画

#### Tabs 样式
- 透明背景 + 紫色底部指示器
- 悬停效果

#### Buttons 样式
- 主按钮: 紫色背景 + 悬停阴影
- 次按钮: 透明边框 + 悬停背景
- 禁用状态

### 2.3 功能需求 #3: 数据展示组件

**需求编号**: REQ-090-003

**需求描述**:
优化 Table、Stats Bar、Filter Panel 等数据展示组件。

#### Table 样式
- 白色卡片背景
- 圆角边框
- 悬停效果

#### Stats Bar 样式
- 统计数字紫色 (#4f46e5)
- 圆角边框

#### Filter Panel 样式
- 白色卡片背景
- 圆角边框

### 2.4 功能需求 #4: 表单组件优化

**需求编号**: REQ-090-004

**需求描述**:
优化 Input、Select、Modal 等表单组件样式。

#### Input/Select 样式
- 边框过渡效果
- 聚焦时紫色边框 + 阴影

#### Modal 样式
- 紫色头部背景
- 圆角边框
- 动画效果

### 2.5 功能需求 #5: 动画增强

**需求编号**: REQ-090-005

**需求描述**:
添加微交互和动画效果，提升用户体验。

#### 按钮动画
- 悬停: translateY(-2px) + shadow
- 点击: scale(0.98)

#### 卡片动画
- 悬浮: translateY(-4px) + shadow-lg

#### 模态框动画
- scaleIn 缩放淡入效果

#### 尊重用户偏好
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
  }
}
```

### 2.6 功能需求 #6: app_constants.js 整合

**需求编号**: REQ-090-006

**需求描述**:
将 app_constants.js 中的颜色定义与 design-system.css 同步。

**实现方案**:
```javascript
const COLORS = {
  STATUS: {
    PASS: 'var(--color-success, #22c55e)',
    FAIL: 'var(--color-error, #ef4444)',
  }
};
```

### 2.7 功能需求 #7: 样式迁移执行

**需求编号**: REQ-090-007

**需求描述**:
将 index.html 中的 inline 样式逐步迁移到 design-system.css。

**迁移任务**:
| 任务 | 删除行数 | 状态 |
|------|----------|------|
| T1 Header | -9 | ✅ |
| T2 Tabs | -4 | ✅ |
| T3 Toolbar | -3 | ✅ |
| T4 Table | -5 | ✅ |
| T5 Stats | -5 | ✅ |
| T6 Filter | -16 | ✅ |
| T7 Status | -6 | ✅ |
| T8 Button | -8 | ✅ |
| T9 Modal | -6 | ✅ |
| T12-T14 | -6 | ✅ |
| **总计** | **-68** | ✅ |

---

## 3. 技术实现

### 3.1 文件变更

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| dev/static/css/design-system.css | 新增 | 设计系统 CSS 变量 |
| dev/index.html | 修改 | 移除冗余样式，引入 design-system.css |
| dev/app/__init__.py | 修改 | 修复 Flask static_folder 冲突 |
| dev/static/js/app_constants.js | 修改 | 颜色使用 CSS 变量 |

### 3.2 CSS 类名兼容映射

为保持向后兼容，添加以下映射:

#### 状态徽章
```css
.status-OPEN { background: var(--color-info-bg); color: var(--color-info-text); }
.status-PASS { background: var(--color-success-bg); color: var(--color-success-text); }
.status-FAIL { background: var(--color-error-bg); color: var(--color-error-text); }
.status-CODED { background: var(--color-warning-bg); color: var(--color-warning-text); }
.status-REMOVED { background: var(--color-bg-secondary); color: var(--color-text-muted); }
```

#### 模态框
```css
.modal-header { background: var(--color-primary); }
.modal-content { border-radius: var(--radius-lg); }
```

### 3.3 JavaScript 修复

修复 app_constants.js 中 N/A 键名问题:
```javascript
// 修改前
N/A: 'N/A'

// 修改后
'N/A': 'N/A'
```

---

## 4. 验收标准

### 4.1 视觉验收

- [x] 主色调为紫色 (#4f46e5)
- [x] Tab 激活状态为紫色底部指示器
- [x] 表格有圆角和阴影
- [x] 统计数字为紫色
- [x] 按钮有悬停动画
- [x] 模态框有动画效果

### 4.2 功能验收

- [x] 所有现有功能正常工作
- [x] 页面加载无报错
- [x] 登录/登出正常
- [x] 项目管理正常
- [x] CP/TC 管理正常
- [x] 进度图表正常

### 4.3 兼容性验收

- [x] Chrome 最新版正常
- [x] Firefox 最新版正常
- [x] Edge 最新版正常
- [x] Safari 最新版正常

### 4.4 性能验收

- [x] 动画流畅无卡顿
- [x] 无强制重排 (forced reflow)
- [x] 尊重用户减少动画偏好

---

## 5. 实施记录

### 5.1 Git 提交

| 提交 | 描述 |
|------|------|
| 1bfcaa5 | 创建设计系统 CSS 变量文件 |
| d3300be | 添加基础样式重置 |
| 6a37016 | 添加按钮组件样式 |
| 1d34cf4 | 添加状态徽章组件样式 |
| b2d9f2d | 添加卡片和模态框组件样式 |
| 02a97a0 | 添加表单组件样式 |
| e780be4 | 更新 app_constants.js 使用 CSS 变量 |
| 57c6e7f | 添加 Header/Tabs/Toolbar 组件样式 |
| cb2e4d4 | 添加表格和统计栏组件样式 |
| c808fc1 | 添加过滤面板和复选框组件样式 |
| 40944b1 | 添加搜索框和操作按钮组件样式 |
| 3b24247 | 添加动画增强效果 |

### 5.2 代码审查修复

| 问题 | 修复 |
|------|------|
| Tab 激活样式冲突 | 改为底部指示器 |
| 按钮动画冲突 | 统一 translateY 策略 |
| 硬编码颜色 | 改用 CSS 变量 |
| 模态框重复定义 | 合并为一次定义 |

### 5.3 迁移执行

详见: `docs/REPORTS/v0.9.0_UI_MIGRATION_REPORT.md`

---

## 6. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.9.0 | 2026-03-05 | 前端界面优化 |
| v0.8.3 | 2026-03-04 | 日期必填、测试用户 |
| v0.8.2 | 2026-03-02 | 实际曲线、快照管理 |
| v0.8.1 | 2026-03-02 | 计划曲线 |
| v0.7.1 | 2026-02-25 | 用户认证 |

---

**规格书状态**: 已完成
**审核人**: Howard
**审核日期**: 2026-03-05
