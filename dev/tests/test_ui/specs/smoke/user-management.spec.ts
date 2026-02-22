/**
 * 用户管理前端测试 - v0.7.1
 * TDD流程：先写测试 → 失败 → 写代码 → 通过
 */

import { test, expect } from '@playwright/test';

test.describe('用户管理', () => {
  const BASE_URL = 'http://localhost:8081';
  
  test('1. 管理员登录后应看到用户管理入口', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('domcontentloaded');
    
    // 登录为 admin
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 验证登录成功
    await expect(page.locator('#currentUsername')).toBeVisible();
    
    // 应该有用户管理按钮
    const userManageBtn = page.locator('#userManageBtn');
    await expect(userManageBtn).toBeVisible({ timeout: 5000 });
  });

  test('2. 点击用户管理应打开模态框', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // 登录为 admin
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 点击用户管理
    await page.click('#userManageBtn');
    await page.waitForTimeout(1500);
    
    // 应该看到用户管理模态框
    const modal = page.locator('#userManageModal');
    await expect(modal).toBeVisible();
  });

  test('3. 用户管理模态框应有添加用户按钮', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // 登录为 admin
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 点击用户管理
    await page.click('#userManageBtn');
    await page.waitForTimeout(1500);
    
    // 添加用户按钮应该存在
    const addBtn = page.locator('#addUserBtn');
    await expect(addBtn).toBeVisible();
  });

  test('4. 用户列表应有内容区域', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // 登录为 admin
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 点击用户管理
    await page.click('#userManageBtn');
    await page.waitForTimeout(2000);
    
    // 用户列表区域应该存在
    const userList = page.locator('#userList');
    await expect(userList).toBeVisible();
  });
});
