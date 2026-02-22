/**
 * 登录功能 UI 测试 - v0.7.1
 * TDD 流程：先写测试 → 失败 → 写代码 → 通过
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:8081';

test.describe('登录功能', () => {

  test('登录页面应该显示登录表单', async ({ page }) => {
    await page.goto(BASE_URL);
    // 等待页面加载
    await page.waitForLoadState('domcontentloaded');
    // 检查是否有登录相关的元素
    const hasLoginOverlay = await page.locator('#loginOverlay').count() > 0;
    const hasLoginForm = await page.locator('#loginForm').count() > 0;
    expect(hasLoginOverlay || hasLoginForm).toBeTruthy();
  });

  test('访客登录按钮应该存在', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');
    const guestBtn = page.locator('#guestLoginBtn');
    await expect(guestBtn).toBeVisible();
  });

  test('管理员登录应该成功', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');

    // 填写登录表单
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');

    // 等待登录完成
    await page.waitForTimeout(2000);

    // 验证登录成功 - 显示用户名
    const userInfo = page.locator('#userInfo');
    await expect(userInfo).toBeVisible();
  });

  test('访客登录应该成功', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');

    // 点击访客登录
    await page.click('#guestLoginBtn');

    // 等待登录完成
    await page.waitForTimeout(2000);

    // 验证登录成功 - 显示访客
    const username = page.locator('#currentUsername');
    await expect(username).toContainText('guest');
  });

  test('错误密码应显示错误提示', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');

    // 输入错误的密码
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'wrongpassword');
    await page.click('#loginForm button[type="submit"]');

    // 等待错误提示
    await page.waitForTimeout(1000);

    // 验证错误提示显示
    const errorMsg = page.locator('#loginError');
    await expect(errorMsg).toBeVisible();
  });

  test('登录后应显示用户名', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');

    // 登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');

    // 等待登录完成
    await page.waitForTimeout(2000);

    // 验证显示用户名
    const username = page.locator('#currentUsername');
    await expect(username).toContainText('admin');
  });
});
