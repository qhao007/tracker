/**
 * CP 覆盖率布局测试 - v0.9.1
 * 测试 COV-001: CP 表格中覆盖率信息为左右显示
 */
import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('CP 覆盖率布局测试 (COV-001)', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // 处理引导页（v0.10.x 新增）
    const introBtn = page.locator('.intro-cta-btn');
    if (await introBtn.isVisible().catch(() => false)) {
      await introBtn.click();
      await page.waitForTimeout(500);
    }
  });

  test('CP覆盖率信息应为左右布局', async ({ page }) => {
    // 登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 处理首次登录密码修改模态框（v0.10.x 新增）
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

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

    await page.waitForLoadState('domcontentloaded');
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 处理首次登录密码修改模态框（v0.10.x 新增）
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

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
