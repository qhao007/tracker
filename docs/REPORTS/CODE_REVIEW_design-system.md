# design-system.css 代码审查报告

> **版本**: v1.0 | **审查日期**: 2026-03-05 | **状态**: ✅ 已完成

---

## 1. 审查范围

文件：`dev/design-system.css`
版本：v0.9.0
功能：Tracker 设计系统 - CSS 变量与组件样式

---

## 2. 审查结果

### ✅ 优秀设计

| # | 设计点 | 说明 |
|---|--------|------|
| 1 | CSS 变量系统 | 完整的颜色、字体、间距、圆角、阴影系统 |
| 2 | 向后兼容 | 保留原有颜色变量 (L43-47) |
| 3 | 性能优化 | 使用 `transform` 和 `opacity` 动画 |
| 4 | 无障碍支持 | `@media (prefers-reduced-motion)` 尊重用户偏好 (L1064-1072) |
| 5 | 浏览器兼容 | `@supports backdrop-filter` 渐进增强 (L335-339) |
| 6 | 基础重置 | 完整的 box-sizing 重置 (L114-116) |

---

## 3. 发现的问题

### 3.1 样式冲突风险 (P1)

**问题**: `.header` 使用 `linear-gradient` 可能与现有代码冲突

```css
/* L483-491 */
.header {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  ...
}
```

**风险**: 需求规格书中 Header 优化方案是深色背景 (`--bg-dark`)，但代码使用渐变

**建议**: 与需求文档保持一致，或确认设计决策

---

### 3.2 Tab 组件样式冲突 (P1)

**问题**: Tab 激活状态使用背景色而非底部指示器

```css
/* L596-600 */
.tab.active {
  background: var(--color-primary);
  color: white;
}
```

**规格要求**: 需求文档 L212-215 要求"底部指示器替代背景色"

**建议**: 修改为底部边框指示器风格

---

### 3.3 动画性能问题 (P2)

**问题**: 按钮同时使用 transform scale 和 translateY

```css
/* L876-877 */
.btn:hover {
  transform: translateY(-1px);  /* 可能与 L171 冲突 */
}

/* L171-172 */
.btn-primary:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-md);
}
```

**风险**: 后定义的样式会覆盖前者，导致动画效果不一致

**建议**: 统一按钮悬停动画策略

---

### 3.4 缺失的样式 (P2)

| 缺失样式 | 说明 |
|----------|------|
| `.header-btn` 禁用状态 | 无 `disabled` 样式 |
| `.btn` 禁用状态 | 无 `disabled` 样式 |
| `.form-control` 错误状态 | 无 `.form-control.error` 样式 |
| 打印样式 | 无 `@media print` 样式 |

---

### 3.5 代码一致性问题 (P2)

**问题**: 模态框类名不一致

```css
/* 两种命名方式混用 */
.modal          /* L312 */
.modal-backdrop /* L330 */
.modal-content-v2 /* L341 - 为什么要 v2? */
.modal-header-v2  /* L351 */
```

**建议**: 统一命名风格，使用 BEM 或语义化命名

---

### 3.6 硬编码颜色 (P3)

**问题**: 部分组件仍有硬编码颜色

```css
/* L254-256 */
.badge-coded {
  background: #fff3e0;  /* 应使用变量 */
  color: #f57c00;
}

/* L258-261 */
.badge-removed {
  background: #f5f5f5;
  color: #9e9e9e;
}
```

---

### 3.7 重复定义 (P3)

**问题**: `.modal-content-v2` 定义两次

```css
/* L341-349 */
.modal-content-v2 { ... }

/* L402-404 */
.modal-content-v2 {
  animation: modalIn 200ms ease-out;
}
```

**建议**: 合并为一次定义

---

## 4. 审查对照表

### 4.1 需求规格符合度

| 需求项 | 状态 | 说明 |
|--------|------|------|
| 颜色系统 | ✅ 符合 | HEX 值，兼容性好 |
| 字体系统 | ✅ 符合 | 系统字体兜底 |
| 间距系统 | ✅ 符合 | 基于 4px 基准 |
| 阴影系统 | ✅ 符合 | 完整的 5 级阴影 |
| Header 样式 | ⚠️ 部分符合 | 使用渐变，非规格中的深色 |
| Tabs 样式 | ❌ 不符合 | 使用背景色，非底部指示器 |
| 按钮动画 | ⚠️ 冲突 | 多种动画定义可能冲突 |
| 动画规范 | ✅ 符合 | 100ms/150ms/200ms 规范 |

### 4.2 代码质量

| 指标 | 评分 |
|------|------|
| 变量使用 | 8/10 |
| 代码组织 | 9/10 |
| 浏览器兼容 | 9/10 |
| 性能考虑 | 8/10 |
| 命名规范 | 6/10 |

---

## 5. 修复建议

### 5.1 高优先级 (P1)

#### 1. 统一 Tab 激活样式

```css
/* 修改 L596-600 */
.tab.active {
  background: transparent;
  color: var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  margin-bottom: -2px;
}
```

#### 2. 统一 Header 样式

确认设计决策，如需保持渐变则更新规格书

---

### 5.2 中优先级 (P2)

#### 3. 修复按钮动画冲突

```css
/* 统一按钮悬停动画 */
.btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 移除 scale 效果，改为 translateY */
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
```

#### 4. 统一模态框类名

```css
/* 重命名 */
.modal-overlay      /* 替代 .modal-backdrop */
.modal-container    /* 替代 .modal-content-v2 */
.modal-header       /* 替代 .modal-header-v2 */
.modal-body         /* 替代 .modal-body-v2 */
.modal-footer       /* 替代 .modal-footer-v2 */
```

#### 5. 添加缺失样式

```css
/* 禁用状态 */
.btn:disabled,
.btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 表单错误状态 */
.form-control.error {
  border-color: var(--color-error);
}

.form-control.error:focus {
  box-shadow: 0 0 0 3px var(--color-error-bg);
}
```

---

### 5.3 低优先级 (P3)

#### 6. 合并重复定义

```css
/* L341-349 + L402-404 合并 */
.modal-content-v2 {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: modalIn 200ms ease-out;
}
```

#### 7. 替换硬编码颜色

```css
/* 使用变量替换 */
.badge-coded {
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.badge-removed {
  background: var(--color-bg-secondary);
  color: var(--color-text-muted);
}
```

---

## 6. 总结

| 指标 | 数量 |
|------|------|
| 优秀设计 | 6 |
| 高优先级问题 | 2 |
| 中优先级问题 | 3 |
| 低优先级问题 | 2 |

**审查结论**: design-system.css 整体设计优秀，变量系统完整，性能和兼容性考虑周全。主要问题在于部分组件样式与需求规格不完全一致，以及类名命名不够统一。建议优先修复 Tab 和 Header 样式问题后，再进行增量替换。

---

**审查人**: 小栗子
**审查时间**: 2026-03-05
