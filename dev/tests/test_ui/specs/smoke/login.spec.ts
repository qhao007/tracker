/**
 * 登录功能 UI 测试 - v0.7.1
 * TDD 流程：先写测试 → 失败 → 写代码 → 通过
 */

import { test, expect } from '@playwright/test';

test.describe('登录功能', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8081');
  });

  // ========== 登录页面元素测试 ==========

  test('登录页面应该显示用户名输入框', async ({ page }) => {
    // 检查页面是否有登录表单
    const hasLoginForm = await page.locator('input[type="text"], input[name="username"], input[id="username"]').count() > 0;
    
    if (hasLoginForm || await page.locator('text=登录').count() > 0) {
      const usernameInput = page.locator('input[type="text"], input[name="username"], input[id="username"]').first();
      await expect(usernameInput).toBeVisible();
    }
  });

  test('登录页面应该显示密码输入框', async ({ page }) => {
    const hasPasswordField = await page.locator('input[type="password"]').count() > 0;
    
    if (hasPasswordField || await page.locator('text=登录').count() > 0) {
      await expect(page.locator('input[type="password"]').first()).toBeVisible();
    }
  });

  test('登录页面应该显示登录按钮', async ({ page }) => {
    const loginButton = page.locator('button:has-text("登录")').first();
    await expect(loginButton).toBeVisible();
  });

  test('登录页面应该显示访客登录按钮', async ({ page }) => {
    const guestButton = page.locator('button:has-text("访客")').first();
    await expect(guestButton).toBeVisible();
  });

  // ========== 登录功能测试 ==========

  test('管理员应该能通过用户名密码登录', async ({ page }) => {
    // 输入用户名
    const usernameInput = page.locator('input[type="text"], input[name="username"], input[id="username"]').first();
    await usernameInput.fill('admin');
    // 输入密码
    await page.locator('input[type="password"]').first().fill('admin123');
    // 点击登录
    await page.locator('button:has-text("登录")').first().click();
    
    // 等待页面响应
    await page.waitForTimeout(1500);
    
    // 验证登录成功 - 应该显示 admin 用户名
    const pageContent = await page.content();
    expect(pageContent).toContain('admin');
  });

  test('访客应该能点击访客登录按钮登录', async ({ page }) => {
    // 点击访客登录
    await page.locator('button:has-text("访客")').first().click();
    
    // 等待页面响应
    await page.waitForTimeout(1500);
    
    // 验证访客登录成功
    const pageContent = await page.content();
    expect(pageContent).toContain('访客');
  });

  test('错误密码应该显示错误提示', async ({ page }) => {
    // 输入错误密码
    const usernameInput = page.locator('input[type="text"], input[name="username"], input[id="username"]').first();
    await usernameInput.fill('admin');
    await page.locator('input[type="password"]').first().fill('wrongpassword');
    await page.locator('button:has-text("登录")').first().click();
    
    // 等待响应
    await page.waitForTimeout(1500);
    
    // 应该显示错误信息或停留在登录页
    const stillOnLogin = await page.locator('button:has-text("登录")').count() > 0;
    expect(stillOnLogin).toBeTruthy();
  });

  // ========== 登录后功能测试 ==========

  test('登录后应该显示用户名', async ({ page }) => {
    // 先登录
    const usernameInput = page.locator('input[type="text"], input[name="username"], input[id="username"]').first();
    await usernameInput.fill('admin');
    await page.locator('input[type="password"]').first().fill('admin123');
    await page.locator('button:has-text("登录")').first().click();
    await page.waitForTimeout(1500);
    
    // 应该显示用户名
    const pageContent = await page.content();
    expect(pageContent).toContain('admin');
  });

  test('登录后应该显示登出按钮', async ({ page }) => {
    // 先登录
    const usernameInput = page.locator('input[type="text"], input[name="username"], input[id="username"]').first();
    await usernameInput.fill('admin');
    await page.locator('input[type="password"]').first().fill('admin123');
    await page.locator('button:has-text("登录")').first().click();
    await page.waitForTimeout(1500);
    
    // 应该显示登出按钮
    const logoutButton = page.locator('button:has-text("退出"), button:has-text("登出")').first();
    await expect(logoutButton).toBeVisible();
  });

  test('点击登出应该成功退出', async ({ page }) => {
    // 先登录
    const usernameInput = page.locator('input[type="text"], input[name="username"], input[id="username"]').first();
    await usernameInput.fill('admin');
    await page.locator('input[type="password"]').first().fill('admin123');
    await page.locator('button:has-text("登录")').first().click();
    await page.waitForTimeout(1500);
    
    // 点击登出
    await page.locator('button:has-text("退出"), button:has-text("登出")').first().click();
    await page.waitForTimeout(1500);
    
    // 应该回到登录状态
    const hasLoginButton = await page.locator('button:has-text("登录")').count() > 0;
    expect(hasLoginButton).toBeTruthy();
  });
});
