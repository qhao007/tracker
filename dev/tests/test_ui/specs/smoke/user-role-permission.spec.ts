/**
 * 用户角色测试 - v0.7.1
 * 测试 user 角色的权限
 */

import { test, expect } from '@playwright/test';

test.describe('user 角色权限测试', () => {
  const BASE_URL = 'http://localhost:8081';
  
  // 动态生成测试用户名
  const testUsername = `testuser_${Date.now()}`;
  const testPassword = 'test123';
  
  test('1. user 角色登录', async ({ request }) => {
    // 先用 admin 创建一个 user 角色账户
    const adminLogin = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    expect(adminLogin.ok()).toBeTruthy();
    
    // 创建 user 角色账户
    const createRes = await request.post(`${BASE_URL}/api/users`, {
      data: { username: testUsername, password: testPassword, role: 'user' }
    });
    
    // 用户可能已存在（409）或创建成功（201）
    expect([200, 201, 409]).toContain(createRes.status());
    
    // 使用 user 账户登录
    const userLogin = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: testUsername, password: testPassword }
    });
    
    expect(userLogin.ok()).toBeTruthy();
    const userData = await userLogin.json();
    expect(userData.user.role).toBe('user');
  });

  test('2. user 登录后项目管理按钮不可见', async ({ page, request }) => {
    // 先用 admin 创建测试用户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    // 创建 user 账户
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: testUsername, password: testPassword, role: 'user' }
    });
    
    // 退出 admin
    await request.post(`${BASE_URL}/api/auth/logout`);
    
    // 等待退出完成
    await page.waitForTimeout(500);
    
    // 刷新页面到登录状态
    await page.goto(BASE_URL);
    await page.waitForSelector('#loginForm', { timeout: 10000 });
    
    // 使用 user 账户通过 UI 登录
    await page.fill('#loginUsername', testUsername);
    await page.fill('#loginPassword', testPassword);
    await page.click('#loginForm button[type="submit"]');
    
    // 等待登录完成，验证 userInfo 可见
    await page.waitForSelector('#userInfo', { timeout: 10000 });
    
    // 验证当前用户名是 testUsername
    const currentUsername = await page.locator('#currentUsername').textContent();
    expect(currentUsername).toBe(testUsername);
    
    // 验证项目管理按钮不可见
    const projectManageBtn = page.locator('#projectManageBtn');
    await expect(projectManageBtn).toBeHidden();
  });
  
  test('3. user 可以创建 TC', async ({ request }) => {
    // 先用 admin 创建测试用户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: testUsername, password: testPassword, role: 'user' }
    });
    
    // user 登录
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: testUsername, password: testPassword }
    });
    expect(loginRes.ok()).toBeTruthy();
    
    // 创建 TC
    const tcRes = await request.post(`${BASE_URL}/api/tc`, {
      data: { project_id: 2, test_name: 'TC_by_user', testbench: 'tb' }
    });
    
    expect(tcRes.ok()).toBeTruthy();
  });

  test('4. user 可以更新 TC', async ({ request }) => {
    // 先用 admin 创建测试用户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: testUsername, password: testPassword, role: 'user' }
    });
    
    // user 登录
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: testUsername, password: testPassword }
    });
    expect(loginRes.ok()).toBeTruthy();
    
    // 更新 TC
    const tcRes = await request.put(`${BASE_URL}/api/tc/1`, {
      data: { project_id: 2, test_name: 'TC_updated_by_user' }
    });
    
    expect(tcRes.ok()).toBeTruthy();
  });

  test('5. user 不能删除项目', async ({ request }) => {
    // 先用 admin 创建测试用户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: testUsername, password: testPassword, role: 'user' }
    });
    
    // user 登录
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: testUsername, password: testPassword }
    });
    expect(loginRes.ok()).toBeTruthy();
    
    // 尝试删除项目 - 应该返回 403
    const delRes = await request.delete(`${BASE_URL}/api/projects/2`);
    expect(delRes.status()).toBe(403);
  });
});
