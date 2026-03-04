/**
 * Integration 测试 - API 权限控制
 *
 * 覆盖 API 层面的权限验证
 * 运行时间: ~2 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/06-permissions-api.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Integration - API 权限控制', () => {

  // ========== PERM-API-001: 未登录访问项目列表应被拒绝 ==========
  test('PERM-API-001: 未登录访问项目列表 → 401', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/projects`);
    expect(response.status()).toBe(401);
  });

  // ========== PERM-API-002: guest 创建 TC → 403 ==========
  test('PERM-API-002: guest 创建 TC → 403', async ({ request }) => {
    // 先确保 guest 用户启用
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });
    await request.patch(`${BASE_URL}/api/users/2`, {
      data: { is_active: true }
    });

    // guest 登录
    await request.post(`${BASE_URL}/api/auth/guest-login`);

    // 尝试创建 TC
    const createResponse = await request.post(`${BASE_URL}/api/tc`, {
      data: { test_name: 'guest_test', testbench: 'tb' }
    });
    expect(createResponse.status()).toBe(403);
  });

  // ========== PERM-API-003: guest 删除 TC → 403 ==========
  test('PERM-API-003: guest 删除 TC → 403', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/guest-login`);

    const res = await request.delete(`${BASE_URL}/api/tc/1?project_id=3`);
    expect(res.status()).toBe(403);
  });

  // ========== PERM-API-004: guest 更新 TC → 403 ==========
  test('PERM-API-004: guest 更新 TC → 403', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/guest-login`);

    const res = await request.put(`${BASE_URL}/api/tc/1`, {
      data: { project_id: 3, test_name: 'test' }
    });
    expect(res.status()).toBe(403);
  });

  // ========== PERM-API-005: guest 创建 CP → 403 ==========
  test('PERM-API-005: guest 创建 CP → 403', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/guest-login`);

    const res = await request.post(`${BASE_URL}/api/cp`, {
      data: { project_id: 3, cover_point: 'test_cp' }
    });
    expect(res.status()).toBe(403);
  });

  // ========== PERM-API-006: guest 删除 CP → 403 ==========
  test('PERM-API-006: guest 删除 CP → 403', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/guest-login`);

    const res = await request.delete(`${BASE_URL}/api/cp/1?project_id=3`);
    expect(res.status()).toBe(403);
  });

  // ========== PERM-API-007: guest 更新 CP → 403 ==========
  test('PERM-API-007: guest 更新 CP → 403', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/guest-login`);

    const res = await request.put(`${BASE_URL}/api/cp/1`, {
      data: { project_id: 3, cover_point: 'test' }
    });
    expect(res.status()).toBe(403);
  });

  // ========== PERM-API-008: admin 创建 TC → 200 ==========
  test('PERM-API-008: admin 创建 TC → 200', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });

    const res = await request.post(`${BASE_URL}/api/tc`, {
      data: { project_id: 3, test_name: `Admin_TC_${Date.now()}`, testbench: 'tb' }
    });
    expect(res.ok()).toBeTruthy();
  });

  // ========== PERM-API-009: admin 删除 TC → 200 ==========
  test('PERM-API-009: admin 删除 TC → 200', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });

    // 先创建 TC
    const createRes = await request.post(`${BASE_URL}/api/tc`, {
      data: { project_id: 3, test_name: `TC_Delete_${Date.now()}`, testbench: 'tb' }
    });
    const tcData = await createRes.json();
    const tcId = tcData.item?.id;

    if (tcId) {
      const res = await request.delete(`${BASE_URL}/api/tc/${tcId}?project_id=3`);
      expect(res.ok()).toBeTruthy();
    }
  });

  // ========== PERM-API-010: user 访问用户列表 → 403 ==========
  test('PERM-API-010: user 访问用户列表 → 403', async ({ request }) => {
    // 创建 user 账户
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });

    const userName = `perm_user_${Date.now()}`;
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: userName, password: 'test123', role: 'user' }
    });

    // 用 user 登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: userName, password: 'test123' }
    });

    // 尝试访问用户列表
    const res = await request.get(`${BASE_URL}/api/users`);
    expect(res.status()).toBe(403);
  });

  // ========== PERM-API-011: admin 删除项目 → 200 ==========
  test('PERM-API-011: admin 删除项目 → 200', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });

    // 创建测试项目
    const createRes = await request.post(`${BASE_URL}/api/projects`, {
      data: { name: `Delete_Me_${Date.now()}` }
    });
    const projectData = await createRes.json();
    const projectId = projectData.project?.id;

    if (projectId) {
      const res = await request.delete(`${BASE_URL}/api/projects/${projectId}`);
      expect(res.ok()).toBeTruthy();
    }
  });

  // ========== PERM-API-012: user 删除项目 → 403 ==========
  test('PERM-API-012: user 删除项目 → 403', async ({ request }) => {
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'admin123' }
    });

    // 创建普通用户
    const userName = `no_delete_${Date.now()}`;
    await request.post(`${BASE_URL}/api/users`, {
      data: { username: userName, password: 'test123', role: 'user' }
    });

    // 用普通用户登录
    await request.post(`${BASE_URL}/api/auth/login`, {
      data: { username: userName, password: 'test123' }
    });

    // 尝试删除项目
    const res = await request.delete(`${BASE_URL}/api/projects/3`);
    expect(res.status()).toBe(403);
  });
});
