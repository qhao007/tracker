/**
 * API 权限控制测试 - v0.7.1
 * TDD流程：先写测试 → 失败 → 写代码 → 通过
 */

import { test, expect } from '@playwright/test';

test.describe('API 权限控制', () => {
  const BASE_URL = 'http://localhost:8081';
  
  test('1. guest 用户更新 TC 应返回 403', async ({ request }) => {
    // guest 登录
    await request.post(`${BASE_URL}/api/auth/guest-login`);
    
    // 尝试更新 TC
    const res = await request.put(`${BASE_URL}/api/tc/1`, {
      data: { project_id: 2, test_name: 'test' }
    });
    
    // 应该返回 403 Forbidden
    expect(res.status()).toBe(403);
  });

  test('2. guest 用户删除 TC 应返回 403', async ({ request }) => {
    // guest 登录
    await request.post(`${BASE_URL}/api/auth/guest-login`);
    
    // 尝试删除 TC
    const res = await request.delete(`${BASE_URL}/api/tc/1?project_id=2`);
    
    // 应该返回 403 Forbidden
    expect(res.status()).toBe(403);
  });

  test('3. guest 用户更新 CP 应返回 403', async ({ request }) => {
    // guest 登录
    await request.post(`${BASE_URL}/api/auth/guest-login`);
    
    // 尝试更新 CP
    const res = await request.put(`${BASE_URL}/api/cp/1`, {
      data: { project_id: 2, cp_name: 'test' }
    });
    
    // 应该返回 403 Forbidden
    expect(res.status()).toBe(403);
  });

  test('4. guest 用户删除 CP 应返回 403', async ({ request }) => {
    // guest 登录
    await request.post(`${BASE_URL}/api/auth/guest-login`);
    
    // 尝试删除 CP
    const res = await request.delete(`${BASE_URL}/api/cp/1?project_id=2`);
    
    // 应该返回 403 Forbidden
    expect(res.status()).toBe(403);
  });

  test('5. admin 用户更新 TC 应成功', async ({ request }) => {
    // admin 登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    // 尝试更新 TC
    const res = await request.put(`${BASE_URL}/api/tc/1`, {
      data: { project_id: 2, test_name: 'test_updated' }
    });
    
    // 应该返回 200
    expect(res.ok()).toBeTruthy();
  });

  test('6. admin 用户删除 TC 应成功', async ({ request }) => {
    // admin 登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    // 先创建一个 TC
    const createRes = await request.post(`${BASE_URL}/api/tc`, {
      data: { project_id: 2, test_name: 'TC_for_delete', testbench: 'tb' }
    });
    const tcData = await createRes.json();
    const tcId = tcData.item?.id;
    
    if (tcId) {
      // 删除刚创建的 TC
      const res = await request.delete(`${BASE_URL}/api/tc/${tcId}?project_id=2`);
      expect(res.ok()).toBeTruthy();
    }
  });
});
