/**
 * 全局 Playwright 配置
 * 
 * 此文件定义全局的测试配置和 hooks
 */

import { defineConfig, devices } from '@playwright/test';
import { path as pathUtils } from '@playwright/test/lib/common/config';
import * as fs from 'fs';
import * as path from 'path';

/**
 * 全局配置
 */
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
    ['html', { outputFolder: 'test-results/html', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],

  // 使用共享浏览器配置
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

    // 语言设置
    locale: 'zh-CN',
  },

  // 项目配置
  projects: [
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  // WebServer 配置（可选，用于 CI/CD）
  webServer: {
    command: 'cd /projects/management/tracker/dev && python3 server.py',
    url: 'http://localhost:8081',
    reuseExistingServer: true,
    timeout: 30000,
    env: {
      PYTHONPATH: '/projects/management/tracker/dev',
    },
  },

  // 全局 teardown
  globalTeardown: pathUtils.resolveProjectDir('./tests/global-teardown.ts'),
});

/**
 * 全局 Teardown
 * 测试套件执行完毕后清理
 */
export async function globalTeardown() {
  console.log('\n🧹 Running global teardown...');

  // 清理测试结果目录
  const testResultsDir = './test-results';
  if (fs.existsSync(testResultsDir)) {
    try {
      // 保留最近 5 次的测试结果
      const dirs = fs.readdirSync(testResultsDir)
        .filter(dir => fs.statSync(path.join(testResultsDir, dir)).isDirectory())
        .sort((a, b) => {
          const statA = fs.statSync(path.join(testResultsDir, a));
          const statB = fs.statSync(path.join(testResultsDir, b));
          return statB.mtimeMs - statA.mtimeMs;
        });

      // 删除旧的测试结果
      for (let i = 5; i < dirs.length; i++) {
        const oldDir = path.join(testResultsDir, dirs[i]);
        fs.rmSync(oldDir, { recursive: true, force: true });
        console.log(`  Removed old test results: ${dirs[i]}`);
      }
    } catch (error) {
      console.warn('  Failed to cleanup old test results:', error);
    }
  }

  console.log('✅ Global teardown complete.\n');
}
