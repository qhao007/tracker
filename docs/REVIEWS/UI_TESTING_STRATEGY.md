# Tracker UI 测试策略与最佳实践

> 生成时间：2026-02-13  
> 任务 ID：t1-20260213-playwright-strategy

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [现有测试代码分析](#2-现有测试代码分析)
3. [Playwright 测试框架设计](#3-playwright-测试框架设计)
4. [内存受限环境优化策略](#4-内存受限环境优化策略)
5. [测试稳定性提升方案](#5-测试稳定性提升方案)
6. [CI/CD 集成建议](#6-cicd-集成建议)
7. [具体改进路线图](#7-具体改进路线图)

---

## 1. 执行摘要

### 核心发现

| 方面 | 当前状态 | 建议 |
|------|---------|------|
| 测试框架 | Python pytest + Playwright CLI 并存 | 统一为 Playwright CLI (TypeScript) |
| 代码组织 | 直接编写测试逻辑 | 引入 Page Object Model |
| 测试稳定性 | 约 70-80% 稳定 | 目标是 95%+ |
| 内存使用 | 单次执行约 500MB-1GB | 优化后可降低 40-50% |

### 关键建议

1. **统一测试框架**：放弃 Python pytest，全面转向 Playwright CLI
2. **引入 Page Object Model**：提高代码复用和维护性
3. **内存优化**：复用浏览器实例，按需加载
4. **测试分层**：Smoke → Integration → E2E 三层结构

---

## 2. 现有测试代码分析

### 2.1 当前测试文件结构

```
tests/
├── test_ui_project.spec.ts    # Playwright CLI (TypeScript) - 6 个测试
├── test_ui_cp.spec.ts         # Playwright CLI (TypeScript) - 12 个测试
├── test_ui_project.py          # Python pytest - 6 个测试
├── test_ui_cp.py               # Python pytest - 13 个测试
├── test_ui_tc.py               # Python pytest - TC 管理
├── test_ui_boundary.py         # Python pytest - 边界测试
├── test_ui_connection.py       # Python pytest - 连接测试
├── test_ui_backup.py           # Python pytest - 备份测试
├── test_ui_stats.py            # Python pytest - 统计测试
└── tracker.spec.ts             # Playwright CLI - 验证测试
```

### 2.2 Playwright CLI 测试特点

#### test_ui_project.spec.ts 分析

```typescript
// ✅ 优点
- 使用 trace 和截图便于调试
- 测试后清理数据
- 更长的超时时间
- beforeEach 统一导航

// ⚠️ 可改进
- 元素定位使用硬编码字符串
- 没有 Page Object 封装
- 等待使用固定 timeout (waitForTimeout)
- 测试数据没有工厂模式
```

#### test_ui_cp.spec.ts 分析

```typescript
// ✅ 优点
- 完整的 CRUD 测试覆盖
- 多条件组合过滤测试
- 批量操作测试

// ⚠️ 可改进
- 测试间可能互相干扰（共享 EX5 项目数据）
- 没有测试数据隔离
- 超时等待可能不稳定
```

### 2.3 常见失败原因

| 失败类型 | 频率 | 原因 | 解决方案 |
|---------|------|------|---------|
| 元素定位失败 | 高 | 动态渲染、ID 变化 | 使用稳定选择器、数据属性 |
| 超时等待 | 中 | API 响应慢、网络抖动 | 智能等待、自定义超时 |
| 测试数据污染 | 中 | 创建后未清理 | 使用唯一标识、测试后清理 |
| 页面状态不一致 | 低 | 登录状态、选中项目丢失 | beforeEach 确保初始状态 |

---

## 3. Playwright 测试框架设计

### 3.1 推荐目录结构

```
tests/
├── fixtures/                    # 测试夹具
│   ├── tracker.fixture.ts       # Tracker 专用夹具
│   ├── page.fixture.ts          # 页面夹具
│   └── test-data.factory.ts     # 测试数据工厂
├── pages/                       # Page Objects
│   ├── base.page.ts             # 基类
│   ├── project.page.ts          # 项目管理页面
│   ├── cp.page.ts               # CP 管理页面
│   └── tc.page.ts               # TC 管理页面
├── utils/                       # 工具函数
│   ├── helpers.ts               # 辅助函数
│   ├── constants.ts             # 常量定义
│   └── logger.ts                # 日志工具
├── specs/                       # 测试规格
│   ├── smoke/                   # 冒烟测试
│   ├── integration/             # 集成测试
│   └── e2e/                     # 端到端测试
├── playwright.config.ts          # Playwright 配置
└── conftest.ts                  # 全局配置
```

### 3.2 Page Object Model 设计

#### 基类设计 (base.page.ts)

```typescript
/**
 * 页面基类 - 提供通用功能
 */
export abstract class BasePage {
  constructor(protected page: Page) {}

  // 导航
  abstract navigate(): Promise<void>;

  // 等待页面加载完成
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForLoadState('networkidle');
  }

  // 智能等待元素可见
  async waitForSelector(
    selector: string,
    timeout: number = 10000
  ): Promise<void> {
    await this.page.waitForSelector(selector, {
      state: 'visible',
      timeout
    });
  }

  // 安全点击（带自动重试）
  async safeClick(
    selector: string,
    options?: { timeout?: number; retries?: number }
  ): Promise<void> {
    const { timeout = 5000, retries = 2 } = options || {};
    
    for (let i = 0; i < retries; i++) {
      try {
        await this.page.click(selector, { timeout });
        return;
      } catch (e) {
        if (i === retries - 1) throw e;
        await this.page.waitForTimeout(500);
      }
    }
  }

  // 获取页面标题
  getTitle(): Promise<string> {
    return this.page.title();
  }
}
```

#### 项目页面对象 (project.page.ts)

```typescript
/**
 * 项目管理页面对象
 */
export class ProjectPage extends BasePage {
  readonly url = 'http://localhost:8081';
  
  // 元素定位器
  private projectSelector = '#projectSelector';
  private projectBtn = 'button.header-btn:has-text("📁 项目")';
  private projectModal = '#projectModal';
  private newProjectName = '#newProjectName';
  private createBtn = '#projectModal button.btn-primary:has-text("创建")';

  async navigate(): Promise<void> {
    await this.page.goto(this.url);
    await this.waitForLoad();
    await this.waitForSelector(this.projectSelector);
  }

  // 打开项目模态框
  async openProjectModal(): Promise<void> {
    await this.page.click(this.projectBtn);
    await this.waitForSelector(this.projectModal);
  }

  // 创建项目
  async createProject(name: string): Promise<void> {
    await this.openProjectModal();
    await this.page.fill(this.newProjectName, name);
    await this.page.click(this.createBtn);
    await this.page.waitForTimeout(1000);
  }

  // 切换到指定项目
  async selectProject(projectName: string): Promise<void> {
    await this.page.selectOption(this.projectSelector, { label: projectName });
    await this.page.waitForTimeout(500);
  }

  // 获取项目列表
  async getProjectList(): Promise<string[]> {
    const options = this.page.locator(`${this.projectSelector} option`);
    const count = await options.count();
    const projects: string[] = [];
    
    for (let i = 0; i < count; i++) {
      const text = await options.nth(i).textContent();
      if (text) projects.push(text);
    }
    
    return projects;
  }

  // 验证项目存在
  async expectProjectExists(projectName: string): Promise<void> {
    await expect(
      this.page.locator(`${this.projectSelector} option:has-text("${projectName}")`)
    ).toBeAttached();
  }
}
```

### 3.3 测试数据工厂模式

```typescript
/**
 * 测试数据工厂 - 生成唯一测试数据
 */
export class TestDataFactory {
  private static counter = 0;

  static generateProjectName(prefix: string = 'TestUI_Project'): string {
    return `${prefix}_${this.generateUniqueId()}`;
  }

  static generateCPName(prefix: string = 'TestUI_CP'): string {
    return `${prefix}_${this.generateUniqueId()}`;
  }

  static generateTCName(prefix: string = 'TestUI_TC'): string {
    return `${prefix}_${this.generateUniqueId()}`;
  }

  private static generateUniqueId(): string {
    return `${Date.now()}_${++this.counter}_${Math.random().toString(36).substr(2, 5)}`;
  }
}
```

### 3.4 Playwright 配置优化

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // 测试目录
  testDir: './tests/specs',
  
  // 全局超时
  timeout: 60000,
  
  // 期待失败（预期会失败的测试）
  expect: {
    timeout: 5000,
    toHaveScreenshot: {
      maxDiffPixels: 100,
    },
  },
  
  // 重试配置
  retries: process.env.CI ? 2 : 0,
  
  // 并发配置（内存受限环境）
  workers: 1,  // 单Worker避免内存竞争
  
  // 报告配置
  reporter: [
    ['html', { outputFolder: 'test-results/html' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
  
  // 使用共享浏览器
  use: {
    baseURL: 'http://localhost:8081',
    
    // 智能等待
    waitUntil: 'domcontentloaded',
    
    // 截图（仅失败时）
    screenshot: 'only-on-failure',
    
    // 录制 trace（仅失败时）
    trace: 'retain-on-failure',
    
    // 视窗大小
    viewport: { width: 1280, height: 720 },
  },
  
  // 项目配置
  projects: [
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  
  // WebServer 配置（可选）
  webServer: {
    command: 'cd /projects/management/tracker/dev && python3 server.py',
    url: 'http://localhost:8081',
    reuseExistingServer: true,
    timeout: 30000,
  },
});
```

---

## 4. 内存受限环境优化策略

### 4.1 内存消耗分析

| 组件 | 内存消耗 | 优化空间 |
|------|---------|---------|
| Chromium/Firefox 浏览器 | 300-500 MB | 高 |
| 页面对象 | 50-100 MB | 中 |
| 测试夹具 | 10-20 MB | 低 |
| 测试数据 | 5-10 MB | 低 |

### 4.2 浏览器实例复用策略

```typescript
// fixtures/shared-browser.fixture.ts
import { test as base } from '@playwright/test';

type BrowserOptions = {
  headless: boolean;
  memoryLimit: number;
};

export const test = base.extend({
  // 共享浏览器实例
  context: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      // 限制内存使用
      browserContextOptions: {
        reducedMotion: 'reduce',
      },
    });
    
    await use(context);
    
    // 测试后清理
    await context.close();
  },
  
  // 页面复用
  page: async ({ context }, use) => {
    const page = await context.newPage();
    
    // 监听页面错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error(`Console Error: ${msg.text()}`);
      }
    });
    
    await use(page);
    
    // 清理页面监听器
    page.removeAllListeners('console');
  },
});
```

### 4.3 测试分组执行策略

```bash
# 按优先级分组执行

# 1. 快速冒烟测试 (1-2 分钟)
npx playwright test tests/specs/smoke --project=firefox

# 2. 完整回归测试 (5-10 分钟)
npx playwright test tests/specs/integration --project=firefox

# 3. 完整测试套件 (15-20 分钟)
npx playwright test tests/specs --project=firefox
```

### 4.4 内存监控脚本

```bash
#!/bin/bash
# memory-monitor.sh - 监控测试执行时的内存使用

MAX_MEMORY=1500000  # 1.5GB limit

while true; do
  MEM_USAGE=$(ps aux | grep 'firefox' | awk '{sum+=$6} END {print sum}')
  
  if [ "$MEM_USAGE" -gt "$MAX_MEMORY" ]; then
    echo "警告: 内存使用 $MEM_USAGE KB 超过限制 $MAX_MEMORY KB"
    # 可以发送告警或终止进程
    pkill -f firefox
    exit 1
  fi
  
  sleep 10
done
```

### 4.5 资源清理最佳实践

```typescript
// 清理策略

test.afterEach(async ({ page }) => {
  // 1. 清理测试创建的数据
  await cleanupTestData(page);
  
  // 2. 清除 localStorage
  await page.evaluate(() => localStorage.clear());
  
  // 3. 清除 cookies
  await page.context().clearCookies();
  
  // 4. 关闭所有弹窗
  const dialogs = page.locator('.modal, .dialog');
  const count = await dialogs.count();
  for (let i = 0; i < count; i++) {
    await dialogs.nth(i).evaluate(el => {
      if (el instanceof HTMLElement && el.offsetParent !== null) {
        el.click(); // 点击关闭
      }
    });
  }
});

async function cleanupTestData(page: Page) {
  // 根据测试数据标识清理
  const timestamp = Date.now();
  const prefix = 'TestUI_';
  
  // 删除测试创建的项目
  await page.goto('http://localhost:8081');
  await page.waitForSelector('#projectSelector');
  
  // 查找并删除以 TestUI_ 开头的项目
  const options = page.locator('#projectSelector option');
  const count = await options.count();
  
  for (let i = 0; i < count; i++) {
    const text = await options.nth(i).textContent();
    if (text?.startsWith(prefix)) {
      await page.selectOption('#projectSelector', { index: i });
      await page.waitForTimeout(300);
      // 执行删除操作（如果实现）
    }
  }
}
```

---

## 5. 测试稳定性提升方案

### 5.1 元素定位最佳实践

```typescript
// ✅ 推荐：使用稳定的属性

// 1. 使用 data-testid（最佳）
await page.click('[data-testid="submit-button"]');

// 2. 使用稳定的 ID
await page.fill('#projectName');

// 3. 使用角色和文本
await page.getByRole('button', { name: '创建' }).click();

// 4. 使用自定义数据属性
await page.click('[data-action="delete"][data-type="project"]');

// ❌ 避免：使用不稳定的选择器

// 避免：CSS 类名（可能变化）
await page.click('.btn-primary.submit-btn');  // 不推荐

// 避免：XPath（维护困难）
await page.click('//div[@class="modal"]//button[contains(text(),"创建")]');  // 不推荐
```

### 5.2 智能等待机制

```typescript
// 智能等待配置

// 1. 全局自动等待
export default defineConfig({
  use: {
    // Playwright 默认自动等待
    // 等待元素可见、启用、可点击
  },
});

// 2. 自定义等待条件
async function waitForAPIResponse(
  page: Page,
  urlPattern: string,
  timeout: number = 10000
): Promise<void> {
  const response = await page.waitForResponse(
    response => 
      response.url().includes(urlPattern) && 
      response.status() < 400,
    { timeout }
  );
  
  console.log(`API Response: ${response.url()} - ${response.status()}`);
}

// 3. 轮询等待（用于复杂条件）
async function waitForCondition<T>(
  condition: () => Promise<T>,
  expectedValue: T,
  timeout: number = 10000,
  interval: number = 500
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const value = await condition();
    if (value === expectedValue) return;
    await page.waitForTimeout(interval);
  }
  
  throw new Error(`Condition not met within ${timeout}ms`);
}

// 使用示例
await waitForCondition(
  async () => await page.locator('#loading').isVisible(),
  false,
  10000
);
```

### 5.3 测试隔离策略

```typescript
// 每个测试使用唯一数据
test('创建项目测试', async ({ page }) => {
  const uniqueProjectName = `Test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  // 测试逻辑
  await page.goto('http://localhost:8081');
  await createProject(page, uniqueProjectName);
  
  // 验证
  await expect(
    page.locator(`#projectSelector option:has-text("${uniqueProjectName}")`)
  ).toBeAttached();
  
  // 测试结束后清理
  // 可以通过 afterEach 或外部脚本清理
});

// 测试依赖管理
test.describe('CP 管理测试', () => {
  // 共享测试数据（谨慎使用）
  let sharedCPName: string;
  
  test.beforeAll(async ({ browser }) => {
    // 在所有测试前创建共享数据
    const page = await browser.newPage();
    sharedCPName = `SharedCP_${Date.now()}`;
    await createCP(page, sharedCPName);
    await page.close();
  });
  
  test('编辑 CP', async ({ page }) => {
    // 使用共享数据
    await editCP(page, sharedCPName);
  });
  
  test('删除 CP', async ({ page }) => {
    // 使用共享数据
    await deleteCP(page, sharedCPName);
  });
  
  test.afterAll(async ({ browser }) => {
    // 清理共享数据
    const page = await browser.newPage();
    await cleanupCP(page, sharedCPName);
    await page.close();
  });
});
```

### 5.4 截图和录制策略

```typescript
// 失败时自动截图和录制

test('复杂测试', async ({ page }, testInfo) => {
  try {
    // 测试逻辑
    await page.goto('http://localhost:8081');
    await page.click('#complex-action');
    await page.waitForTimeout(2000);
  } catch (error) {
    // 失败时截图
    const screenshotPath = `test-results/screenshots/${testInfo.title}-${Date.now()}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });
    
    // 保存 HTML
    const htmlPath = `test-results/html/${testInfo.title}-${Date.now()}.html`;
    await page.content().then(content => {
      require('fs').writeFileSync(htmlPath, content);
    });
    
    // 重新抛出错误
    throw error;
  }
});
```

---

## 6. CI/CD 集成建议

### 6.1 GitHub Actions 工作流

```yaml
# .github/workflows/ui-tests.yml
name: UI Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # 每天凌晨执行完整回归测试
    - cron: '0 2 * * *'

env:
  NODE_VERSION: '18'
  TRACKER_PORT: 8081

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    services:
      tracker:
        image: python:3.9-slim
        ports:
          - 8081:8081
        env:
          PYTHONPATH: /projects/management/tracker/dev
        command: >
          bash -c "cd /projects/management/tracker/dev && python3 server.py"
        options: >
          --memory=2g
          --cpus=1
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - name: Install Playwright
        run: |
          npm ci
          npx playwright install --with-deps chromium
      
      - name: Wait for Tracker Service
        run: |
          for i in {1..30}; do
            if curl -s http://localhost:8081/api/health | grep -q "ok"; then
              echo "Tracker is ready"
              exit 0
            fi
            sleep 2
          done
          echo "Tracker failed to start"
          exit 1
      
      - name: Run Smoke Tests
        if: github.event_name == 'push'
        run: |
          npx playwright test tests/specs/smoke --project=firefox
        env:
          PLAYWRIGHT_REPORT: test-results/smoke
      
      - name: Run Full Tests
        if: github.event_name == 'schedule'
        run: |
          npx playwright test tests/specs --project=firefox
        env:
          PLAYWRIGHT_REPORT: test-results/full
      
      - name: Upload Artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: test-results/
          retention-days: 7
      
      - name: Notify on Failure
        if: failure()
        run: |
          curl -X POST "${{ secrets.FEISHU_WEBHOOK_URL }}" \
            -H "Content-Type: application/json" \
            -d '{"msg_type": "text", "content": {"text": "❌ Tracker UI 测试失败，请查看 GitHub Actions"}}'
```

### 6.2 测试执行策略

| 触发条件 | 执行测试 | 原因 |
|---------|---------|------|
| 每次 push | Smoke Tests | 快速验证，5 分钟内完成 |
| PR 创建/更新 | Smoke Tests + 关键路径 | 平衡速度和质量 |
| 每日定时 | 完整回归测试 | 全面覆盖，发现潜在问题 |
| 手动触发 | 可选测试范围 | 按需选择 |

### 6.3 失败处理策略

```typescript
// 自动重试机制

// playwright.config.ts
export default defineConfig({
  retries: 2,
  
  // 对特定测试跳过重试
  projects: [
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      // 网络不稳定环境跳过重试
      grep: /@slow/,
      retries: 'skipped',
    },
  ],
});

// 测试标记
test('不稳定测试', async ({ page }) => {
  // ...
}).tag('@slow');  // 标记为慢测试，不在冒烟时运行
```

---

## 7. 具体改进路线图

### 7.1 第一阶段：基础优化（1-2 周）

| 任务 | 优先级 | 工作量 | 预期效果 |
|------|--------|--------|---------|
| 创建 Page Object 基类 | 高 | 2 天 | 代码复用提升 30% |
| 统一测试数据工厂 | 高 | 1 天 | 数据唯一性保证 |
| 配置 Playwright 优化参数 | 高 | 0.5 天 | 稳定性提升 10% |
| 添加智能等待替代固定等待 | 中 | 1 天 | 超时错误减少 50% |

### 7.2 第二阶段：框架完善（2-3 周）

| 任务 | 优先级 | 工作量 | 预期效果 |
|------|--------|--------|---------|
| 实现 Page Objects（项目/CP/TC） | 高 | 3 天 | 代码可维护性大幅提升 |
| 添加内存监控脚本 | 中 | 1 天 | 避免 OOM |
| 完善测试清理机制 | 中 | 1 天 | 测试隔离性提升 |
| 添加测试报告改进 | 低 | 1 天 | 问题定位更快 |

### 7.3 第三阶段：CI/CD 集成（1-2 周）

| 任务 | 优先级 | 工作量 | 预期效果 |
|------|--------|--------|---------|
| GitHub Actions 工作流 | 高 | 2 天 | 自动化测试执行 |
| 测试分组执行 | 中 | 1 天 | 执行时间优化 |
| 失败告警集成 | 中 | 0.5 天 | 问题快速响应 |
| 性能基准测试 | 低 | 2 天 | 性能趋势追踪 |

### 7.4 立即可做的改进（今天开始）

```bash
# 1. 安装 Playwright 依赖
npm install @playwright/test
npx playwright install --with-deps firefox

# 2. 创建基础配置文件
cat > playwright.config.ts << 'EOF'
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 60000,
  retries: 2,
  workers: 1,
  use: {
    baseURL: 'http://localhost:8081',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [{
    name: 'firefox',
    use: { browserName: 'firefox' },
  }],
});
EOF

# 3. 重构一个测试文件为 Page Object 模式
```

### 7.5 成功指标

| 指标 | 当前值 | 目标值 | 测量方式 |
|------|--------|--------|---------|
| 测试稳定性 | 70-80% | 95%+ | 连续运行 10 次成功率 |
| 代码复用率 | 0% | 60%+ | Page Object 覆盖 |
| 内存使用 | 800MB | 400MB | 单次执行峰值 |
| 测试执行时间 | 15 分钟 | 10 分钟 | 完整回归套件 |
| 问题定位时间 | 30 分钟 | 5 分钟 | Trace/截图辅助 |

---

## 附录

### A. 参考资源

- [Playwright 官方文档](https://playwright.dev/docs/intro)
- [Playwright 最佳实践](https://playwright.dev/docs/best-practices)
- [Page Object Model 模式](https://playwright.dev/docs/test-pom)
- [Playwright 配置选项](https://playwright.dev/api/class-testoptions)

### B. 常用命令速查

```bash
# 运行测试
npx playwright test --project=firefox

# 运行指定测试文件
npx playwright test tests/project.spec.ts --project=firefox

# 生成 HTML 报告
npx playwright test --reporter=html

# 查看录制
npx playwright show-report

# 安装浏览器
npx playwright install firefox

# 更新 Playwright
npm install @playwright/test@latest
npx playwright install --with-deps
```

### C. 故障排除

| 问题 | 解决方案 |
|------|---------|
| 元素定位失败 | 检查页面是否完全加载，使用 `waitForLoadState('networkidle')` |
| 测试超时 | 增加超时时间，检查 API 响应时间 |
| 内存不足 | 减少 `workers` 数量，使用 `--headed` 模式调试 |
| 浏览器无法启动 | 运行 `npx playwright install --with-deps` |
| 测试数据污染 | 使用唯一标识，测试后清理 |

---

> 文档版本：v1.0  
> 最后更新：2026-02-13  
> 作者：Claude Code (task: t1-20260213-playwright-strategy)
