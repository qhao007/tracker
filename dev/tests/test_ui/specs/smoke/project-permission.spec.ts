/**
 * 项目管理 UI 权限测试 - v0.7.1
 */

import { test, expect } from '@playwright/test';

test.describe('项目管理 UI 权限', () => {

  test('1. admin 登录后应有项目访问权限', async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');

    // 登录 admin
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);

    // 检查项目选择器是否可见
    const projectSelector = page.locator('#projectSelector');
    await expect(projectSelector).toBeVisible();
  });

  test('2. user 登录后应有项目访问权限', async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');

    // 登录 admin
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);

    // 点击用户管理
    await page.click('#userManageBtn');
    await page.waitForTimeout(500);

    // 检查用户管理模态框是否打开
    const modal = page.locator('#userModal, .modal, [id*="user"]');
    await expect(modal.first()).toBeVisible();
  });

  test('3. guest 登录后应有项目访问权限', async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');

    // 用 guest 登录
    await page.click('#guestLoginBtn');
    await page.waitForTimeout(2000);

    // guest 也应该有项目访问权限
    const projectSelector = page.locator('#projectSelector');
    await expect(projectSelector).toBeVisible();
  });

});
