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
- 外部 CDN 资源加载超时
- `waitUntil` 设置不当

**waitUntil 选项详解**:

| 选项 | 等待内容 | 适用场景 |
|------|---------|---------|
| `load` | 所有资源（包括 CDN、字体等） | 完整页面加载 |
| `domcontentloaded` | DOM 解析完成 | 大多数测试 |
| `commit` | 仅导航提交，不等待任何资源 | 沙箱环境、快速测试 |

```typescript
// 方案 1: 使用 commit 模式（推荐沙箱环境）
await page.goto('http://localhost:8081', { waitUntil: 'commit' });

// 方案 2: 使用 domcontentloaded
await page.goto('http://localhost:8081', { waitUntil: 'domcontentloaded' });

// 方案 3: 增加超时时间
await page.goto('http://localhost:8081', { timeout: 120000 });

// 方案 4: 全局配置
// playwright.config.ts
use: {
  waitUntil: 'commit',  // 不等待任何资源
  actionTimeout: 120000,
  navigationTimeout: 120000,
}
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

### 1.5 登录后默认状态问题

**问题**: 测试假设"无项目"状态，但登录后已有默认项目选中

**常见原因**:
- 登录后自动选中上次项目
- 测试数据初始化了默认项目

**解决方案**:
```typescript
// 错误：假设无项目
await expect(emptyState).toContainText('请选择一个项目');  // 失败！

// 正确：检查实际显示的状态
await expect(emptyState).toContainText('请先设置项目起止日期');

// 或者：先清除选中状态（如果应用支持）
// 或者：调整测试逻辑以适应默认状态
```

### 1.6 创建项目后列表刷新问题

**问题**: 创建项目后无法在新打开的列表中找到新项目

**原因**: 项目创建后需要重新打开模态框刷新列表

**解决方案**:
```typescript
// 创建项目
await page.click('#projectManageBtn');
await page.fill('#newProjectName', 'Test_Project');
await page.click('button:has-text("创建")');

// 重新打开项目管理对话框查看新项目
await page.click('#projectManageBtn');
await page.waitForTimeout(500);

// 现在可以找到新项目
await expect(page.locator('.project-item:has-text("Test_Project")')).toBeVisible();
```

---

---

### 1.4 选择器混淆问题

**问题**: 测试找不到元素或点击错误的元素

**常见原因**: 混淆了不同的 UI 元素

**示例**:
- `#projectSelector` - 项目选择下拉框（`<select>` 元素）
- `#projectManageBtn` - 顶部导航栏的项目管理按钮

**调试方法**: 查看页面截图
```typescript
// 截图会显示在错误消息中
// 检查页面实际显示的内容
```

**解决方案**:
```typescript
// 错误：点击下拉框后在下拉框内找"项目管理"按钮
await page.click('#projectSelector');
await page.click('button:has-text("项目管理")');  // 不存在！

// 正确：直接点击导航栏按钮
await page.click('#projectManageBtn');
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
| `toBeAttached()` | 元素存在于 DOM（即使隐藏）|
| `toBeEnabled()` | 元素需要可交互 |
| `toHaveText()` | 元素文本需要匹配 |
| `waitForTimeout()` | 等待动画/过渡（慎用）|

**重要区别**: `toBeVisible()` vs `toBeAttached()`

```typescript
// toBeVisible() - 元素必须可见（display: none 会失败）
await expect(page.locator('#chartCanvas')).toBeVisible();

// toBeAttached() - 元素只需存在于 DOM（即使隐藏）
await expect(page.locator('#chartCanvas')).toBeAttached();

// 示例：canvas 元素可能因无数据而隐藏const
 chartCanvas = page.locator('#progressChart');
await expect(chartCanvas).toBeAttached();  // 推荐
```

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

#### 方案 3: CDN优先 + 超时自动切换本地（推荐方案）

**应用代码实现**：
```html
<!-- Chart.js - CDN优先，超时自动切换本地 -->
<script>
    const CHART_CDN_URL = 'https://cdn.jsdelivr.net/npm/chart.js';
    const CHART_LOCAL_URL = '/app_static/js/chart.min.js';
    const CHART_TIMEOUT_MS = 3000; // 3秒超时

    function loadChartScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async function loadChartWithFallback() {
        try {
            await new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = CHART_CDN_URL;
                script.onload = () => { window.ChartLoaded = true; resolve(); };
                script.onerror = reject;
                const timeout = setTimeout(reject, CHART_TIMEOUT_MS);
                document.head.appendChild(script);
            });
        } catch (e) {
            // CDN 失败，使用本地版本
            await loadChartScript(CHART_LOCAL_URL);
            window.ChartLoaded = true;
        }
    }

    window.ChartLoaded = false;
    loadChartWithFallback();
</script>
```

**Flask 路由配置**：
```python
@app.route('/app_static/<path:filename>')
def serve_app_static(filename):
    return send_from_directory(os.path.join(base_dir, 'app_static'), filename)
```

#### 方案 4: Playwright 配置优化

```typescript
// playwright.config.ts
use: {
  // 等待 DOM 解析完成，允许 Chart.js 异步加载
  waitUntil: 'domcontentloaded',

  // 增加超时（沙箱环境）
  actionTimeout: 120000,
  navigationTimeout: 120000,
}
```

#### 方案 5: 测试中等待异步加载的资源

当应用使用异步加载（如方案3）时，测试需要显式等待资源加载完成：

```typescript
// 等待 Chart.js 加载完成
await page.waitForFunction(() => window.ChartLoaded === true, { timeout: 10000 });
```

**重要提示**：
- 如果应用使用 CDN + Fallback 方案，测试**必须**等待 `window.ChartLoaded === true`
- 否则测试可能在 Chart.js 加载完成前就检查页面状态，导致误判

### 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 方案1: 移除CDN | 简单 | 需要改代码 | 本地开发 |
| 方案2: 本地文件 | 稳定 | 需手动更新 | 生产环境 |
| **方案3: CDN+Fallback** | 兼顾两者 | 需测试配合 | **推荐** |
| 方案4: waitUntil:commit | 最快 | 可能丢资源 | 不推荐 |

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

## 9. 快速调试命令

```bash
# 运行单个测试
npx playwright test tests/xxx.spec.ts -g "test-name" --project=firefox

# DEBUG 模式查看详细日志
DEBUG=pw:api npx playwright test --project=firefox

# 查看 trace
npx playwright show-trace test-results/xxx/trace.zip

# 仅列出测试
npx playwright test tests/xxx.spec.ts --list
```

---

*最后更新: 2026-03-03*
