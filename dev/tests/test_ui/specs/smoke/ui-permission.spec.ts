/**
 * 前端权限控制测试 - v0.7.1
 * TDD流程：先写测试 → 失败 → 写代码 → 通过
 */

import { test, expect } from '@playwright/test';

test.describe('前端权限控制', () => {
  const BASE_URL = 'http://localhost:8081';

  test('1. guest 登录后不应有用户管理入口', async ({ page, request }) => {
    // 先启用 guest 用户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    await request.patch(`${BASE_URL}/api/users/2`, {
      data: { is_active: true }
    });

    await page.goto(BASE_URL);
    
    // guest 登录
    await page.click('#guestLoginBtn');
    await page.waitForTimeout(1500);
    
    // 验证是 guest 登录
    await expect(page.locator('#currentUsername')).toHaveText('guest');
    
    // guest 不应该有用户管理入口
    const userManageBtn = page.locator('#userManageBtn');
    const count = await userManageBtn.count();
    
    // 如果按钮存在，应该不可见或不存在
    if (count > 0) {
      await expect(userManageBtn).not.toBeVisible();
    }
  });

  test('2. admin 登录后应有用户管理入口', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // admin 登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(1500);
    
    // admin 应该有用户管理入口
    const userManageBtn = page.locator('#userManageBtn');
    await expect(userManageBtn).toBeVisible();
  });
});
