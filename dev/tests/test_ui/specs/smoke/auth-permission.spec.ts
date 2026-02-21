/**
 * 访问控制 API 测试 - v0.7.1
 * 使用 browserContext 保持 session
 */

import { test, expect } from '@playwright/test';

test.describe('访问控制 API', () => {
  const BASE_URL = 'http://localhost:8082';
  
  // 使用 test.beforeEach 确保每个测试独立
  test('1. 未登录访问项目列表应被拒绝', async ({ request, baseURL }) => {
    const response = await request.get(`${BASE_URL}/api/projects`);
    expect(response.status()).toBe(401);
  });

  test('2. admin 可以创建项目', async ({ request }) => {
    // 直接在一个连贯的请求流程中完成
    const loginResponse = await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    expect(loginResponse.ok()).toBeTruthy();
    
    // 使用 same-request 继续（Playwright 会自动保持 cookie）
    const createResponse = await request.post(`${BASE_URL}/api/projects`, {
      data: { name: `AdminProject_${Date.now()}` }
    });
    expect(createResponse.ok()).toBeTruthy();
  });

  test('3. 普通用户无法访问用户列表', async ({ request }) => {
    // 先用 admin 创建普通用户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    const userName = `user_${Date.now()}`;
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: userName, password: 'test123', role: 'user' }
    });
    
    // 用普通用户登录（同一个 request context 会自动保留 cookie）
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: userName, password: 'test123' }
    });
    
    // 尝试访问用户列表
    const listResponse = await request.get(`${BASE_URL}/api/users`);
    expect(listResponse.status()).toBe(403);
  });

  test('4. guest 无法创建 TC', async ({ request }) => {
    // 访客登录
    await request.post(`${BASE_URL}/api/auth/guest-login`);
    
    // 尝试创建 TC（应该被拒绝）
    const createResponse = await request.post(`${BASE_URL}/api/tc`, {
      data: { test_name: 'guest_test', testbench: 'tb' }
    });
    expect(createResponse.status()).toBe(403);
  });

  test('5. admin 可以删除项目', async ({ request }) => {
    // admin 登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    // 创建项目
    const createResponse = await request.post(`${BASE_URL}/api/projects`, {
      data: { name: `DeleteMe_${Date.now()}` }
    });
    const projectData = await createResponse.json();
    
    // 删除项目
    const deleteResponse = await request.delete(
      `${BASE_URL}/api/projects/${projectData.project.id}`
    );
    expect(deleteResponse.ok()).toBeTruthy();
  });

  test('6. 普通用户无法删除项目', async ({ request }) => {
    // 创建普通用户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    
    const userName = `cannot_delete_${Date.now()}`;
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: userName, password: 'test123', role: 'user' }
    });
    
    // 普通用户登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: userName, password: 'test123' }
    });
    
    // 尝试删除项目
    const deleteResponse = await request.delete(`${BASE_URL}/api/projects/1`);
    expect(deleteResponse.status()).toBe(403);
  });
});
