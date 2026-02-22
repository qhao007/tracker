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

  test('2. user 可以创建 TC', async ({ request }) => {
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

  test('3. user 可以更新 TC', async ({ request }) => {
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

  test('4. user 不能删除项目', async ({ request }) => {
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
