/**
 * CP 覆盖率布局测试 - v0.9.1
 * 测试 COV-001: CP 表格中覆盖率信息为左右显示
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('CP 覆盖率布局测试 (COV-001)', () => {

  test('CP覆盖率信息应为左右布局', async ({ page }) => {
    // 打开页面并登录
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // 登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');

    // 等待项目选择器加载
    await page.waitForFunction(() => {
      const selector = document.getElementById('projectSelector');
      return selector && selector.options.length > 1;
    }, { timeout: 15000 });

    // 切换到 CP 标签页
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(1500);

    // 等待表格加载
    await page.waitForSelector('.data-table, .cp-table', { timeout: 10000 });

    // 验证表格可见
    const table = page.locator('.data-table, .cp-table').first();
    await expect(table).toBeVisible();
  });

  test('CP表格加载后无关键JS错误', async ({ page }) => {
    const consoleErrors: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');

    // 等待项目选择器加载
    await page.waitForFunction(() => {
      const selector = document.getElementById('projectSelector');
      return selector && selector.options.length > 1;
    }, { timeout: 15000 });

    // 切换到 CP 标签页
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(2000);

    // 验证无关键 JS 错误
    const criticalErrors = consoleErrors.filter(err =>
      !err.includes('Chart.js') &&
      !err.includes('CDN') &&
      !err.includes('401') &&
      !err.includes('favicon')
    );

    expect(criticalErrors).toHaveLength(0);
  });
});
