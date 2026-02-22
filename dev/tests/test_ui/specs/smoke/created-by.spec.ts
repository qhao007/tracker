/**
 * created_by 字段测试 - v0.7.1
 * TDD流程：先写测试 → 失败 → 写代码 → 通过
 */

import { test, expect } from '@playwright/test';

test.describe('created_by 字段', () => {
  const BASE_URL = 'http://localhost:8082';
  
  test('1. 创建 TC 时应自动记录 created_by', async ({ request }) => {
    // admin 登录
    const loginRes = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    expect(loginRes.ok()).toBeTruthy();
    
    // 创建 TC
    const tcRes = await request.post(`${BASE_URL}/api/tc`, {
      data: {
        test_name: 'Test_TC_CreatedBy',
        testbench: 'test_tb',
        project_id: 1
      }
    });
    expect(tcRes.ok()).toBeTruthy();
    
    const tcData = await tcRes.json();
    console.log('TC Response:', JSON.stringify(tcData));
    
    // 验证返回的 TC 包含 created_by
    expect(tcData.tc).toHaveProperty('created_by');
    expect(tcData.tc.created_by).toBe('admin');
  });

  test('2. 创建 CP 时应自动记录 created_by', async ({ request }) => {
    // admin 登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    // 创建 CP
    const cpRes = await request.post(`${BASE_URL}/api/cp`, {
      data: {
        cp_name: 'Test_CP_CreatedBy',
        description: 'test cp',
        project_id: 1
      }
    });
    expect(cpRes.ok()).toBeTruthy();
    
    const cpData = await cpRes.json();
    console.log('CP Response:', JSON.stringify(cpData));
    
    // 验证返回的 CP 包含 created_by
    expect(cpData.cp).toHaveProperty('created_by');
    expect(cpData.cp.created_by).toBe('admin');
  });

  test('3. guest 创建的 TC 应记录 guest', async ({ request }) => {
    // guest 登录
    await request.post(`${BASE_URL}/api/auth/guest-login`);
    
    // 创建 TC
    const tcRes = await request.post(`${BASE_URL}/api/tc`, {
      data: {
        test_name: 'Guest_TC_CreatedBy',
        testbench: 'test_tb',
        project_id: 1
      }
    });
    // guest 无法创建 TC，应该返回 403
    expect(tcRes.status()).toBe(403);
  });

  test('4. 查询 TC 列表应包含 created_by 字段', async ({ request }) => {
    // admin 登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    // 查询 TC 列表
    const listRes = await request.get(`${BASE_URL}/api/tc?project_id=1`);
    expect(listRes.ok()).toBeTruthy();
    
    const tcList = await listRes.json();
    console.log('TC List:', JSON.stringify(tcList));
    
    // 验证列表中的 TC 包含 created_by
    if (tcList.tcs && tcList.tcs.length > 0) {
      expect(tcList.tcs[0]).toHaveProperty('created_by');
    }
  });

  test('5. 查询 CP 列表应包含 created_by 字段', async ({ request }) => {
    // admin 登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    // 查询 CP 列表
    const listRes = await request.get(`${BASE_URL}/api/cp?project_id=1`);
    expect(listRes.ok()).toBeTruthy();
    
    const cpList = await listRes.json();
    console.log('CP List:', JSON.stringify(cpList));
    
    // 验证列表中的 CP 包含 created_by
    if (cpList.cps && cpList.cps.length > 0) {
      expect(cpList.cps[0]).toHaveProperty('created_by');
    }
  });
});
