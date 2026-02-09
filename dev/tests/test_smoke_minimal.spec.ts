/**
 * Tracker Playwright 冒烟测试 - 极简版
 *
 * 目的：验证开发版服务是否正常运行
 * 运行命令: npx playwright test tests/test_smoke_minimal.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_URL || 'http://localhost:8081';

test('冒烟测试 - 页面基本访问', async ({ page }) => {
  // 1. 直接访问页面
  const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

  // 2. 验证 HTTP 状态码
  expect(response?.status()).toBe(200);

  // 3. 验证页面标题（简单检查）
  await expect(page).toHaveTitle(/.*Tracker.*/);

  // 4. 验证项目选择器存在（核心功能入口）
  await expect(page.locator('#projectSelector')).toBeVisible();
});
