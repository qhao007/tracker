import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // 测试目录
  testDir: './tests',

  // 排除旧测试文件（模块导入路径已失效）
  testIgnore: '**/smoke/archives/**',

  // 测试输出目录
  outputDir: './test-results/playwright-output',

  // 全局超时 - 沙箱环境需要更长超时
  timeout: 180000,

  // 期待失败（预期会失败的测试）
  expect: {
    timeout: 10000,
    toHaveScreenshot: {
      maxDiffPixels: 100,
    },
  },

  // 重试配置
  retries: process.env.CI ? 2 : 0,

  // 并发配置（内存受限环境）
  workers: 1,

  // 报告配置
  reporter: [
    ['html', { outputFolder: 'test-results/playwright-html' }],
    ['json', { outputFile: 'test-results/playwright-json/report.json' }],
    ['list']
  ],

  // 使用共享浏览器
  use: {
    baseURL: 'http://localhost:8081',

    // 智能等待 - 等待 DOM 解析完成，允许 Chart.js 异步加载
    waitUntil: 'domcontentloaded',

    // 沙箱环境需要更长的超时
    actionTimeout: 120000,
    navigationTimeout: 120000,

    // 截图（仅失败时）
    screenshot: 'only-on-failure',

    // 录制 trace（仅失败时）
    trace: 'retain-on-failure',

    // 视窗大小
    viewport: { width: 1280, height: 720 },

    // 沙箱环境：设置 HOME 环境变量
    launchOptions: {
      env: {
        HOME: '/root',
        XDG_RUNTIME_DIR: '/tmp',
      },
    },
  },

  // 项目配置
  projects: [
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],

  // WebServer 配置（复用 8081 测试服务）
  webServer: {
    command: 'cd /projects/management/tracker/dev && gunicorn --workers 2 --bind 0.0.0.0:8081 wsgi:app',
    url: 'http://localhost:8081',
    reuseExistingServer: true,
    timeout: 30000,
  },
});
