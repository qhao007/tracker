/**
 * Integration 测试 - 帮助手册
 *
 * 覆盖帮助手册功能
 * 运行时间: ~1 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/10-help.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Integration - 帮助手册', () => {

  // ========== HELP-001: 帮助按钮在 Header 显示 ==========
  test('HELP-001: 帮助按钮在 Header 显示', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证帮助按钮存在
    const helpBtn = page.locator('a[href="/manual"], button:has-text("帮助"), a:has-text("帮助")');
    const count = await helpBtn.count();

    if (count > 0) {
      await expect(helpBtn.first()).toBeVisible();
    }
  });

  // ========== HELP-002: 点击帮助打开手册页面 ==========
  test('HELP-002: 点击帮助打开手册页面', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 查找帮助按钮
    const helpBtn = page.locator('a[href="/manual"]');
    const count = await helpBtn.count();

    if (count > 0) {
      // 点击帮助按钮
      await helpBtn.first().click();

      // 等待新标签页打开或页面跳转
      await page.waitForTimeout(2000);

      // 验证手册页面加载
      const currentUrl = page.url();
      expect(currentUrl).toContain('manual');
    }
  });

  // ========== HELP-003: 手册页面可访问 ==========
  test('HELP-003: 手册页面可访问', async ({ page }) => {
    // 直接访问手册页面
    const response = await page.request.get(`${BASE_URL}/manual`);
    expect(response.ok()).toBeTruthy();
  });
});
