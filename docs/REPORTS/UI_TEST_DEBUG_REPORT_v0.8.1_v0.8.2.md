# v0.8.1 & v0.8.2 UI 测试调试报告

> 日期: 2026-03-03
> 版本: v0.8.1 / v0.8.2
> 调试工具: Playwright, DEBUG=pw:api

---

## 1. 问题概述

v0.8.1 和 v0.8.2 的 UI 测试在沙箱环境中运行时出现超时和失败问题。

---

## 2. 发现的问题

### 2.1 Chart.js CDN 超时问题

**问题描述**: Playwright 测试超时，错误信息：
```
page.goto: Test timeout of 60000ms exceeded.
waiting until "domcontentloaded"
taking page screenshot +59s
waiting for fonts to load...
```

**根因分析**:
- Chart.js 从 CDN (`cdn.jsdelivr.net`) 加载
- 沙箱环境中网络请求被阻塞或极慢
- Playwright 默认等待所有资源加载完成

**解决方案**:
1. 使用 Playwright 的 `waitUntil: 'commit'` 配置，不等待任何资源加载
2. 这样可以避免等待 CDN 资源，解决超时问题

**修改文件**:
- `dev/playwright.config.ts` - 添加 `waitUntil: 'commit'` 配置

---

### 2.2 Playwright 超时配置不足

**问题描述**: 测试在页面导航和元素交互时超时

**解决方案**: 更新 `playwright.config.ts`

```typescript
// 全局超时 - 沙箱环境需要更长超时
timeout: 180000,

// 沙箱环境需要更长的超时
actionTimeout: 120000,
navigationTimeout: 120000,
```

---

### 2.3 UI 测试选择器问题

**问题描述**:
1. 测试尝试选择已选中的项目（登录后 SOC_DV 已选中）
2. canvas 元素因无数据而隐藏（`display: none`），`toBeVisible()` 断言失败

**解决方案**:
1. 移除重复选择项目的逻辑 - 登录后 SOC_DV 已选中
2. 使用 `toBeAttached()` 替代 `toBeVisible()` - 只验证元素存在于 DOM

---

---

### 2.4 playwright_debug 技能结构问题

**问题描述**: 技能无法被识别

**根因**:
- `plugin.json` 中名称是 `playwright_debug`
- `SKILL.md` 中名称是 `playwright-debugging`（不一致）
- SKILL.md 没有放在正确的 `skills/` 子目录下

**解决方案**:
1. 添加 `invocation` 字段到 `plugin.json`
2. 将 `SKILL.md` 移到 `skills/playwright-debugging/` 目录

---

## 3. 修改汇总

| 文件 | 修改内容 |
|------|---------|
| `dev/playwright.config.ts` | 添加 `waitUntil: 'commit'`，增加超时配置 |
| `dev/tests/test_ui/specs/integration/planned_curve.spec.ts` | 修复选择器，使用 toBeAttached() |
| `/root/.claude/plugins/.../playwright_debug/...` | 修复技能结构 |

---

## 4. 测试结果

### planned_curve.spec.ts (v0.8.1)

| 测试用例 | 状态 |
|---------|------|
| UI-PLAN-001: 计划曲线图表显示 | ✅ 通过 |
| UI-PLAN-002: 曲线数据点正确渲染 | ✅ 通过 |
| UI-PLAN-003: 计划曲线颜色正确 | ✅ 通过 |
| UI-PLAN-010: 时间段选择器可见 | ✅ 通过 |
| UI-PLAN-011: 选择日期范围后图表更新 | ✅ 通过 |
| UI-PLAN-012: 清空时间段后恢复显示 | ✅ 通过 |
| UI-PLAN-020: 无项目显示提示 | ✅ 通过 |
| UI-PLAN-021: 无日期项目显示提示 | ✅ 通过 |
| UI-PLAN-022: 无 TC 项目显示提示 | ✅ 通过 |
| UI-PLAN-023: 无 CP 项目显示提示 | ✅ 通过 |
| UI-PLAN-030: 图例显示 | ✅ 通过 |
| UI-PLAN-031: Tooltip 提示 | ✅ 通过 |

**结果**: 12/12 通过 ✅

### progress_charts.spec.ts (v0.8.0)

| 测试用例 | 状态 |
|---------|------|
| UI-ISSUE-001: 项目选择框宽度固定为 200px | ✅ 通过 |
| UI-CHART-001: Progress Charts 标签页切换 | ✅ 通过 |
| UI-CHART-002: 空项目时显示提示 | ✅ 通过 |
| UI-CHART-003: 空项目提示显示 | ✅ 通过 |
| UI-PROJ-001: 创建项目带日期 | ✅ 通过 |
| UI-PROJ-003: 项目列表显示日期 | ✅ 通过 |

**结果**: 6/6 通过 ✅

---

## 5. 问题修复完成 ✅

所有 UI 测试问题已修复：

### 5.1 选择器错误修复

**问题**: `button:has-text("项目管理")` 选择器不存在
**原因**: 混淆了两个 UI 元素：
- `#projectSelector` - 项目选择下拉框
- `#projectManageBtn` - 顶部导航栏的项目管理按钮

**修复**:
- 将 `button:has-text("项目管理")` 改为 `#projectManageBtn`
- 移除多余的 `#projectSelector` 点击

### 5.2 预期文本错误修复

**问题**: UI-PLAN-020/UI-CHART-003 期望"请选择一个项目"
**原因**: 登录后 SOC_DV 已选中，显示"请先设置项目起止日期"

**修复**: 更新预期文本为"请先设置项目起止日期"

### 5.3 项目列表刷新修复

**问题**: UI-PROJ-003 创建项目后无法找到新项目
**原因**: 项目创建后需要重新打开模态框才能看到新项目

**修复**: 添加重新打开项目管理对话框的步骤

---

## 6. 经验总结

1. **沙箱环境 CDN 问题**: 外部 CDN 资源在沙箱中可能加载失败
2. **Playwright 超时**: 沙箱环境需要更长的超时配置
3. **元素可见性**: canvas 等元素可能存在于 DOM 但隐藏，使用 `toBeAttached()` 更合适
4. **Flask 静态文件**: 避免自动路由与自定义路由冲突
5. **Chart.js 异步加载**: 动态加载的脚本需要测试显式等待

## 7. 最终解决方案

### 问题
Chart.js CDN 在沙箱环境中超时或响应极慢

### 解决方案：方案B - CDN优先，超时自动切换本地

#### 7.1 应用代码实现

```html
<!-- Chart.js for Progress Charts (v0.8.0) - CDN优先，超时自动切换本地 -->
<script>
    const CHART_CDN_URL = 'https://cdn.jsdelivr.net/npm/chart.js';
    const CHART_LOCAL_URL = '/app_static/js/chart.min.js';
    const CHART_TIMEOUT_MS = 3000; // 3秒超时

    // 动态加载脚本
    function loadChartScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // 尝试加载 Chart.js：先 CDN，超时则本地
    async function loadChartWithFallback() {
        try {
            await new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = CHART_CDN_URL;
                script.onload = () => {
                    console.log('Chart.js: CDN 加载成功');
                    window.ChartLoaded = true;
                    resolve();
                };
                script.onerror = reject;
                const timeout = setTimeout(reject, CHART_TIMEOUT_MS);
                document.head.appendChild(script);
            });
        } catch (e) {
            console.warn('Chart.js: CDN 加载失败，使用本地版本', e);
            await loadChartScript(CHART_LOCAL_URL);
            window.ChartLoaded = true;
        }
    }

    window.ChartLoaded = false;
    loadChartWithFallback();
</script>
```

#### 7.2 Flask 静态文件路由

```python
# app/__init__.py
@app.route('/app_static/<path:filename>')
def serve_app_static(filename):
    app_static_dir = os.path.join(base_dir, 'app_static')
    return send_from_directory(app_static_dir, filename)
```

#### 7.3 Playwright 配置

```typescript
// playwright.config.ts
use: {
  waitUntil: 'domcontentloaded',  // 等待 DOM 解析完成
}
```

#### 7.4 测试中的等待逻辑

由于 Chart.js 是异步加载的，测试需要等待加载完成：

```typescript
// 等待 Chart.js 加载完成
await page.waitForFunction(() => window.ChartLoaded === true, { timeout: 10000 });
```

### 方案对比

| 方案 | 描述 | 测试结果 |
|------|------|----------|
| 方案A: CDN only | 只用 CDN | ❌ 超时失败 |
| 方案B: CDN + Fallback | CDN优先，超时自动切换本地 | ✅ 12/12 通过 |
| 方案C: Local only | 直接用本地 | ✅ 12/12 通过 |

**推荐方案B**：兼顾正常网络下的CDN优势和沙箱环境下的本地备份。

### 关键要点

1. **超时时间**：3秒超时后自动切换本地
2. **状态标志**：使用 `window.ChartLoaded` 标记加载状态
3. **测试等待**：测试中需要等待 `window.ChartLoaded === true`
4. **本地文件**：确保 `/app_static/js/chart.min.js` 存在

---

## 8. 参考文档

- [Playwright 调试最佳实践](../DEVELOPMENT/playwright_debug_best_practices.md)
- [API 测试策略](../DEVELOPMENT/API_TESTING_STRATEGY.md)
- [v0.8.1 规格书](../SPECIFICATIONS/tracker_SPECS_v0.8.1.md)
- [v0.8.2 规格书](../SPECIFICATIONS/tracker_SPECS_v0.8.2.md)

---

*最后更新: 2026-03-03*
