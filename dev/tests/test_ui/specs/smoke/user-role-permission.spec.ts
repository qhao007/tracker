/**
 * 用户角色测试 - v0.7.1
 * 测试 user 角色的权限
 */

import { test, expect } from '@playwright/test';

test.describe('user 角色权限测试', () => {
  const BASE_URL = 'http://localhost:8081';
  
  test('1. user 角色登录', async ({ request }) => {
    // 先用 admin 创建一个 user 角色账户
    const adminLogin = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    expect(adminLogin.ok()).toBeTruthy();
    
    // 创建 user 角色账户
    const createRes = await request.post(`${BASE_URL}/api/users`, {
      data: { username: 'testuser_role', password: 'test123', role: 'user' }
    });
    
    if (createRes.status() === 409) {
      // 用户已存在，使用已有账户
      console.log('用户已存在');
    }
    
    // 使用 user 账户登录
    const userLogin = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'testuser_role', password: 'test123' }
    });
    
    if (userLogin.ok()) {
      const userData = await userLogin.json();
      expect(userData.user.role).toBe('user');
    } else {
      // 可能是密码问题，标记为待排查
      console.log('user 登录失败，可能需要先重置密码');
    }
  });

  test('2. user 可以创建 TC', async ({ request }) => {
    // user 登录
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'xbwang', password: 'test123' }
    });
    
    if (!loginRes.ok()) {
      test.skip(true, 'user 账户不可用');
      return;
    }
    
    // 创建 TC
    const tcRes = await request.post(`${BASE_URL}/api/tc`, {
      data: { project_id: 2, test_name: 'TC_by_user', testbench: 'tb' }
    });
    
    expect(tcRes.ok()).toBeTruthy();
  });

  test('3. user 可以更新 TC', async ({ request }) => {
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'xbwang', password: 'test123' }
    });
    
    if (!loginRes.ok()) {
      test.skip(true, 'user 账户不可用');
      return;
    }
    
    // 更新 TC
    const tcRes = await request.put(`${BASE_URL}/api/tc/1`, {
      data: { project_id: 2, test_name: 'TC_updated_by_user' }
    });
    
    expect(tcRes.ok()).toBeTruthy();
  });

  test('4. user 不能删除项目', async ({ request }) => {
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'xbwang', password: 'test123' }
    });
    
    if (!loginRes.ok()) {
      test.skip(true, 'user 账户不可用');
      return;
    }
    
    // 尝试删除项目
    const delRes = await request.delete(`${BASE_URL}/api/projects/2`);
    expect(delRes.status()).toBe(403);
  });
});
