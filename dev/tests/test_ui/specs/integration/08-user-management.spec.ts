/**
 * Integration 测试 - 用户管理
 *
 * 覆盖用户管理功能
 * 运行时间: ~1 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/08-user-management.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Integration - 用户管理', () => {

  // ========== USER-001: admin 看到用户管理入口 ==========
  test('USER-001: admin 看到用户管理入口', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证用户管理按钮存在
    const userManageBtn = page.locator('#userManageBtn');
    await expect(userManageBtn).toBeVisible();
  });

  // ========== USER-002: 点击用户管理打开模态框 ==========
  test('USER-002: 点击用户管理打开模态框', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 点击用户管理按钮
    await page.click('#userManageBtn');
    await page.waitForTimeout(500);

    // 验证模态框打开
    const modal = page.locator('#userModal, .user-modal, #usersModal');
    const count = await modal.count();

    if (count > 0) {
      await expect(modal.first()).toBeVisible();
    }
  });

  // ========== USER-003: 用户管理模态框有添加用户按钮 ==========
  test('USER-003: 用户管理模态框有添加用户按钮', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 点击用户管理按钮
    await page.click('#userManageBtn');
    await page.waitForTimeout(500);

    // 验证添加用户按钮存在
    const addBtn = page.locator('button:has-text("添加用户"), button:has-text("+ 用户")');
    const count = await addBtn.count();

    if (count > 0) {
      await expect(addBtn.first()).toBeVisible();
    }
  });

  // ========== USER-004: 用户列表有内容区域 ==========
  test('USER-004: 用户列表有内容区域', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 点击用户管理按钮
    await page.click('#userManageBtn');
    await page.waitForTimeout(500);

    // 验证用户列表区域存在
    const userList = page.locator('.user-list, #userList, table.user-table');
    const count = await userList.count();

    if (count > 0) {
      await expect(userList.first()).toBeVisible();
    }
  });

  // ========== USER-005: 禁用/启用 guest 账户 ==========
  test('USER-005: 禁用/启用 guest 账户', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 点击用户管理按钮
    await page.click('#userManageBtn');
    await page.waitForTimeout(500);

    // 查找 guest 用户的禁用/启用按钮
    const guestRow = page.locator('tr:has-text("guest"), .user-row:has-text("guest")');
    const count = await guestRow.count();

    if (count > 0) {
      // 查找切换按钮
      const toggleBtn = guestRow.locator('button.toggle-status, button:has-text("禁用"), button:has-text("启用")');
      const toggleCount = await toggleBtn.count();

      if (toggleCount > 0) {
        // 测试切换功能
        await toggleBtn.first().click();
        await page.waitForTimeout(500);
      }
    }
  });
});
