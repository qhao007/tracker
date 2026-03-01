# Playwright 偶发性超时问题分析报告

> **分析日期**: 2026-03-01
> **分析人**: Claude (小栗子)
> **项目**: Tracker v0.8.0

---

## 问题描述

在运行 Playwright UI 测试时，出现偶发性的 `page.goto` 超时错误：

```
Error: page.goto: Test timeout of 60000ms exceeded.
Call log:
  - navigating to "http://localhost:8081/", waiting until "load"
```

### 错误特征

- **偶发性**: 约 50% 概率失败，不是每次都发生
- **环境相关**: 主要出现在沙箱/Docker 环境中
- **测试运行时间**: 每次运行约 5-6 分钟，其中大部分时间在等待超时

---

## 根因分析

### 调查过程

1. **检查服务器状态**: 服务器正常运行，HTTP 响应时间正常 (0.002s)
2. **检查浏览器状态**: Firefox 已安装，版本正常
3. **使用 DEBUG 模式**: `DEBUG=pw:api npx playwright test ...`

### 关键发现

从 DEBUG 日志中发现：

```
navigated to "http://localhost:8081/"
taking page screenshot +59s
waiting for fonts to load...
page.goto failed
```

### 根因确认

**Chart.js CDN (`cdn.jsdelivr.net`) 在沙箱环境中导致网络请求超时**

- Playwright 默认等待所有资源加载完成（包括外部 CDN 资源）
- 在沙箱环境中，外部网络请求被阻塞或极慢
- 导致 `page.goto` 等待资源加载超时

### 验证

| 测试条件 | 结果 |
|----------|------|
| 有 Chart.js CDN | 偶发性超时 (约 50%) |
| 无 Chart.js CDN | 6/6 全部通过 (14.6s) |

---

## 解决方案

### 方案 1: 测试时移除 CDN（推荐）

在开发和测试环境中移除 Chart.js CDN：

```html
<!-- 生产环境使用 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- 测试环境：移除或注释 -->
<!-- <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> -->
```

**优点**: 无需修改代码，一行注释即可切换
**缺点**: 测试环境和生产环境不一致

### 方案 2: 本地化 Chart.js

```bash
# 下载 Chart.js 到本地
mkdir -p static/js
curl -o static/js/chart.umd.js https://cdn.jsdelivr.net/npm/chart.js/dist/chart.umd.js
```

```html
<!-- 修改 HTML 引用 -->
<script src="/static/js/chart.umd.js"></script>
```

**优点**:
- 测试和生产环境一致
- 离线可用

**缺点**:
- 需要手动更新版本
- 增加部署复杂度
- 失去 CDN 加速

### 方案 3: 使用 --no-sandbox 参数

在 Playwright 配置中添加浏览器启动参数：

```typescript
// playwright.config.ts
projects: [
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'] },
    launchOptions: {
      args: ['-no-sandbox', '--disable-dev-shm-usage'],
    },
  },
],
```

**注意**: 经过测试，此方案在当前环境中无效

### 方案 4: 接受偶发性失败

在本地开发环境中，偶发性超时是可接受的：

- 这是外部环境限制，不是代码问题
- 可以在 CI 环境中使用更稳定的配置

---

## ✅ 最终修复方案 (2026-03-01 更新)

### 方案 5: 调整 Playwright 等待策略（推荐 ✅）

**核心思路**: 不等待所有外部资源加载完成，只等待 DOM 内容就绪

**修改文件**: `dev/tests/test_ui/clear-cache.spec.ts`

```typescript
// 修改前 (会等待所有资源包括 CDN)
await page.goto('http://localhost:8081', { waitUntil: 'networkidle' });

// 修改后 (只等待 DOM 就绪)
await page.goto('http://localhost:8081', { waitUntil: 'domcontentloaded' });
```

**为什么有效**:
- `networkidle`: 等待所有网络请求完成（包括 CDN，容易超时）
- `domcontentloaded`: 只等待 HTML 解析完成，不等待外部资源

**配置位置**: 也可以在 `playwright.config.ts` 中全局设置：

```typescript
// playwright.config.ts
use: {
  baseURL: 'http://localhost:8081',
  waitUntil: 'domcontentloaded',  // 全局生效
},
```

---

## 测试结果

### 修复前

| 条件 | 结果 |
|------|------|
| 有 Chart.js CDN | 偶发性超时 (约 50%) |
| 无 Chart.js CDN | 6/6 通过 (14.6s) |

### 修复后

| 测试用例 | 结果 | 耗时 |
|----------|------|------|
| UI-CHART-001: Tab 切换到 Progress Charts | ✅ 通过 | 2.5s |
| UI-CHART-002: Progress Charts 面板可见 | ✅ 通过 | 1.4s |
| UI-CHART-003: 空项目提示显示 | ✅ 通过 | 1.1s |
| UI-ISSUE-001: 项目选择框宽度 200px | ✅ 通过 | 2.7s |
| **总计** | **4/4 通过** | **7.7s** |

### 结论

- ✅ 问题已解决
- ✅ 测试运行时间从 5-6 分钟缩短到 7.7 秒
- ✅ 保留 CDN（生产/测试环境一致）
- ✅ 无需修改代码逻辑

---

## 文档记录

| 文档 | 路径 |
|------|------|
| Playwright 调试最佳实践 | `docs/DEVELOPMENT/playwright_debug_best_practices.md` |
| 本报告 | `docs/REPORTS/playwright_timeout_analysis.md` |

---

## 后续建议

1. **长期方案**: 考虑使用私有 npm 仓库或打包工具管理前端依赖
2. **CI 环境**: 在 CI 配置中预先下载依赖，减少网络依赖
3. **监控**: 如果在生产环境中遇到 Chart.js 加载问题，添加错误处理和降级方案

---

*报告完成*
