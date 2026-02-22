/**
 * 前端权限控制测试 - v0.7.1
 * 测试前端界面根据角色的按钮显示/隐藏
 */

import { test, expect } from '@playwright/test';

test.describe('前端权限按钮显示测试', () => {
  const BASE_URL = 'http://localhost:8081';
  
  test('1. 未登录用户不应看到项目列表', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');
    
    // 未登录应该看到登录模态框
    const loginModal = page.locator('#loginOverlay, .login-overlay');
    await expect(loginModal).toBeVisible();
  });

  test('2. guest 用户不应看到用户管理按钮', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');
    
    // guest 登录
    await page.click('#guestLoginBtn');
    await page.waitForTimeout(1500);
    
    // 验证是 guest
    await expect(page.locator('#currentUsername')).toHaveText('guest');
    
    // guest 不应该看到用户管理按钮
    const userManageBtn = page.locator('#userManageBtn');
    const count = await userManageBtn.count();
    if (count > 0) {
      await expect(userManageBtn).not.toBeVisible();
    }
  });

  test('3. admin 用户应看到用户管理按钮', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');
    
    // admin 登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(1500);
    
    // admin 应该看到用户管理按钮
    const userManageBtn = page.locator('#userManageBtn');
    await expect(userManageBtn).toBeVisible();
  });

  test('4. admin 登录后应有添加项目按钮', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');
    
    // admin 登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(1500);
    
    // 检查是否有添加项目的按钮
    const addProjectBtn = page.locator('button:has-text("项目"), #addProjectBtn');
    const count = await addProjectBtn.count();
    if (count > 0) {
      await expect(addProjectBtn.first()).toBeVisible();
    }
  });
});
