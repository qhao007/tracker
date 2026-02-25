/**
 * 禁用/启用用户测试 - v0.7.1
 */

import { test, expect } from '@playwright/test';

test.describe('用户管理 - 禁用/启用', () => {
  const BASE_URL = 'http://localhost:8081';
  
  test('禁用和启用 guest 账户', async ({ page }) => {
    // 1. 登录 admin
    await page.goto(BASE_URL);
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // 2. 打开用户管理
    await page.click('#userManageBtn');
    await page.waitForTimeout(1000);
    
    // 3. 获取 guest 行
    const guestRow = page.locator('#userList table tbody tr:has-text("guest")');
    await expect(guestRow).toBeVisible();
    
    // 4. 获取初始状态
    const initialText = await guestRow.textContent();
    console.log('初始状态:', initialText);
    
    const isEnabled = initialText.includes('✅ 启用');
    console.log('Guest 已启用:', isEnabled);
    
    // 5. 点击禁用/启用按钮
    const buttonText = isEnabled ? '禁用' : '启用';
    console.log('点击按钮:', buttonText);
    
    // 使用 dialog 事件处理确认对话框
    page.on('dialog', async dialog => {
      console.log('对话框消息:', dialog.message());
      await dialog.accept();
    });
    
    await guestRow.getByRole('button', { name: buttonText }).click();
    
    // 6. 等待状态更新
    await page.waitForTimeout(2000);
    
    // 7. 获取新状态
    const newText = await guestRow.textContent();
    console.log('新状态:', newText);
    
    const newIsEnabled = newText.includes('✅ 启用');
    console.log('Guest 新状态 (已启用):', newIsEnabled);
    
    // 8. 验证状态已切换
    expect(newIsEnabled).toBe(!isEnabled);
  });
});
