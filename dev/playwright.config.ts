import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // 测试目录
  testDir: './tests',

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
  workers: 1,

  // 报告配置
  reporter: [
    ['html', { outputFolder: 'test-results/report/html' }],
    ['json', { outputFile: 'test-results/report/results.json' }],
    ['list']
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
