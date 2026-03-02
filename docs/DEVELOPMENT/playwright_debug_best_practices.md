# Playwright 调试经验与最佳实践

> 本文档记录 Playwright UI 测试调试过程中的经验、最佳实践和常见错误
> 适用于 Tracker 项目的 UI 测试开发

---

## 1. 常见错误与解决方案

### 1.1 元素选择器错误

**问题**: 测试找不到页面元素

**常见原因**:
- 元素 ID/类名不正确
- 元素尚未渲染完成
- 选择器语法错误

**解决方案**:
```typescript
// 错误示例
await page.fill('#username', 'admin');  // 实际 ID 是 #loginUsername

// 正确示例
await page.fill('#loginUsername', 'admin');
await page.fill('#loginPassword', 'admin123');
await page.click('button.login-btn');
```

**调试技巧**:
```bash
# 使用 curl 检查页面 HTML
curl -s http://localhost:8081 | grep -E 'id="xxx"'

# 使用 Playwright inspect
npx playwright codegen http://localhost:8081
```

---

### 1.2 页面导航超时

**问题**: `page.goto()` 超时

**常见原因**:
- 服务器未启动
- 网络延迟
- 沙箱/容器环境中的浏览器启动问题
- `waitUntil` 设置不当

**解决方案**:
```typescript
// 方案 1: 调整 waitUntil
await page.goto('http://localhost:8081', { waitUntil: 'domcontentloaded' });

// 方案 2: 增加超时时间
await page.goto('http://localhost:8081', { timeout: 120000 });

// 方案 3: 使用 navigationTimeout 配置
test.setTimeout(120000);
```

---

### 1.3 元素交互失败

**问题**: 点击/输入元素失败

**常见原因**:
- 元素被遮挡
- 元素不可见
- 元素尚未加载

**解决方案**:
```typescript
// 等待元素可见
await expect(page.locator('#element')).toBeVisible();

// 等待元素可点击
await page.locator('#button').click({ force: true });

// 使用 hover 确保元素可见
await page.hover('#element');
await page.click('#element');
```

---

## 2. 调试技巧

### 2.1 查看页面截图

测试失败时自动保存截图：
```typescript
// playwright.config.ts
use: {
  screenshot: 'only-on-failure',
}
```

### 2.2 使用 Trace Viewer

```bash
# 查看 trace
npx playwright show-trace test-results/xxx/trace.zip
```

### 2.3 调试模式运行

```bash
# 打开浏览器并逐步执行
npx playwright test tests/xxx.spec.ts --debug

# 实时查看浏览器操作
npx playwright codegen http://localhost:8081
```

### 2.4 控制台日志

```typescript
// 捕获控制台消息
page.on('console', msg => console.log(msg.text()));

// 捕获页面错误
page.on('pageerror', err => console.log(err));
```

---

## 3. 最佳实践

### 3.1 测试组织

```typescript
// 使用 describe 组织测试
test.describe('功能模块', () => {
  // 使用 beforeEach 准备测试环境
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await login(page);
  });

  test('测试用例', async ({ page }) => {
    // 测试逻辑
  });
});
```

### 3.2 元素选择器优先级

1. **ID 选择器** (最高优先级)
   ```typescript
   page.locator('#elementId')
   ```

2. **文本选择器**
   ```typescript
   page.locator('button:has-text("提交")')
   ```

3. **角色选择器** (无障碍)
   ```typescript
   page.getByRole('button', { name: '提交' })
   ```

4. **测试 ID** (需添加 data-testid 属性)
   ```typescript
   page.getByTestId('submit-button')
   ```

### 3.3 等待策略

| 策略 | 适用场景 |
|------|----------|
| `toBeVisible()` | 元素需要可见 |
| `toBeEnabled()` | 元素需要可交互 |
| `toHaveText()` | 元素文本需要匹配 |
| `waitForTimeout()` | 等待动画/过渡（慎用）|

---

## 4. 环境配置问题

### 4.1 沙箱/容器环境超时

**问题**: 在 Docker/沙箱环境中 `page.goto()` 偶发性超时

**原因**: 浏览器在受限环境中的网络/启动问题

**解决方案**:
```typescript
// playwright.config.ts
use: {
  // 使用 domcontentloaded 减少等待
  waitUntil: 'domcontentloaded',

  // 增加超时
  actionTimeout: 60000,
  navigationTimeout: 60000,
}
```

### 4.2 浏览器兼容性问题

```typescript
// playwright.config.ts
projects: [
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'] },
  },
]
```

---

## 5. 测试维护

### 5.1 避免测试脆弱性

```typescript
// 脆弱写法
await page.waitForTimeout(1000);  // 硬编码等待

// 健壮写法
await expect(page.locator('#success-message')).toBeVisible();  // 智能等待
```

### 5.2 测试隔离

```typescript
// 每个测试使用独立数据
const uniqueName = `Test_${Date.now()}`;
await page.fill('#name', uniqueName);
```

### 5.3 清理机制

```typescript
// 使用 afterEach 清理
test.afterEach(async ({ page }) => {
  // 清理测试数据
});
```

---

## 6. 快速检查清单

- [ ] 服务器是否正常运行？
- [ ] 元素 ID/选择器是否正确？
- [ ] 是否需要等待元素加载？
- [ ] 是否使用了正确的等待策略？
- [ ] 测试数据是否唯一？
- [ ] 截图/trace 是否提供了有用信息？

---

## 8. 已知问题：沙箱环境偶发性超时

### 问题描述

在沙箱/Docker 环境中运行 Playwright 测试时，出现 `page.goto` 超时错误：

```
Error: page.goto: Test timeout of 60000ms exceeded.
Call log:
  - navigating to "http://localhost:8081/", waiting until "load"
```

### 根因分析

通过 DEBUG 日志 (`DEBUG=pw:api`) 确认：

```
navigated to "http://localhost:8081/"
taking page screenshot +59s
waiting for fonts to load...
page.goto failed
```

**根因**: Chart.js 从 CDN (`cdn.jsdelivr.net`) 加载，在沙箱环境中网络请求被阻塞或极慢，导致 Playwright 等待资源加载超时。

### 解决方案

#### 方案 1: 测试时移除 CDN（开发/测试环境）

在开发和测试环境中，可以暂时移除 Chart.js CDN：

```html
<!-- 生产环境使用 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- 测试环境可以移除，或使用本地资源 -->
<!-- <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> -->
```

#### 方案 2: 本地化外部资源（推荐长期方案）

将 Chart.js 下载到本地：

```bash
mkdir -p static/js
curl -o static/js/chart.min.js https://cdn.jsdelivr.net/npm/chart.js/dist/chart.umd.js
```

然后修改 HTML：

```html
<script src="/static/js/chart.min.js"></script>
```

#### 方案 3: 异步加载 + 错误处理

```html
<script async src="https://cdn.jsdelivr.net/npm/chart.js"
        onerror="console.warn('Chart.js loaded failed')"></script>
```

注意：异步加载可能仍然会导致超时，取决于网络环境。

#### 方案 4: Playwright 配置优化

```typescript
// playwright.config.ts
use: {
  // 使用 domcontentloaded 减少等待
  waitUntil: 'domcontentloaded',
  // 增加超时
  actionTimeout: 120000,
}
```

### 验证方法

使用 DEBUG 模式查看详细日志：

```bash
DEBUG=pw:api npx playwright test --project=firefox
```

---

## 7. 相关文档

| 文档 | 说明 |
|------|------|
| [Playwright 官方文档](https://playwright.dev/) | 完整的 Playwright 文档 |
| [Playwright API](https://playwright.dev/api/class-page) | Page 类 API |
| [选择器最佳实践](https://playwright.dev/docs/locators) | 选择器使用指南 |

---

*最后更新: 2026-03-01*
