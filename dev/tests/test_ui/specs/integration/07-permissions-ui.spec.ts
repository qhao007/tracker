/**
 * Integration 测试 - UI 权限控制
 *
 * 覆盖前端 UI 层面的权限验证
 * 运行时间: ~2 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/07-permissions-ui.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Integration - UI 权限控制', () => {

  // ========== PERM-UI-001: 未登录不显示项目列表 ==========
  test('PERM-UI-001: 未登录不显示项目列表', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // 验证登录表单存在
    await expect(page.locator('#loginUsername')).toBeVisible();
    await expect(page.locator('#loginPassword')).toBeVisible();

    // 验证项目列表不显示（在登录前）
    const projectSelector = page.locator('#projectSelector');
    // 项目选择器应该不存在或被遮罩覆盖
    await expect(projectSelector).not.toBeVisible();
  });

  // ========== PERM-UI-002: guest 无用户管理按钮 ==========
  test('PERM-UI-002: guest 无用户管理按钮', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'guest');
    await page.fill('#loginPassword', 'guest123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证用户管理按钮不存在
    const userManageBtn = page.locator('#userManageBtn');
    const count = await userManageBtn.count();

    if (count > 0) {
      const isVisible = await userManageBtn.first().isVisible().catch(() => false);
      expect(isVisible).toBe(false);
    } else {
      expect(count).toBe(0);
    }
  });

  // ========== PERM-UI-003: admin 有用户管理按钮 ==========
  test('PERM-UI-003: admin 有用户管理按钮', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证用户管理按钮存在
    const userManageBtn = page.locator('#userManageBtn');
    await expect(userManageBtn).toBeVisible();
  });

  // ========== PERM-UI-004: admin 有添加项目按钮 ==========
  test('PERM-UI-004: admin 有添加项目按钮', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 点击项目按钮
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    // 验证添加项目按钮存在
    const addBtn = page.locator('button:has-text("添加项目"), button:has-text("+ 项目")');
    await expect(addBtn.first()).toBeVisible();
  });

  // ========== PERM-UI-005: user 无删除按钮 ==========
  test('PERM-UI-005: user 无删除按钮', async ({ page }) => {
    // 先创建 user
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1000);

    try {
      await page.evaluate(async () => {
        await fetch('/api/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ username: 'testuser2', password: 'test123', role: 'user' })
        });
      });
    } catch (e) {
      // 用户可能已存在
    }

    // 登出
    await page.click('button:has-text("退出")');
    await page.waitForTimeout(1000);

    // 用 user 登录
    await page.fill('#loginUsername', 'testuser2');
    await page.fill('#loginPassword', 'test123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 点击项目按钮
    const projectBtn = page.locator('#projectManageBtn');
    if (await projectBtn.count() > 0) {
      await projectBtn.click();
      await page.waitForTimeout(500);

      // 检查删除按钮
      const deleteBtn = page.locator('button.delete-project, button[onclick*="deleteProject"]');
      const count = await deleteBtn.count();

      if (count > 0) {
        const isVisible = await deleteBtn.first().isVisible().catch(() => false);
        expect(isVisible).toBe(false);
      }
    }
  });

  // ========== PERM-UI-006: admin 访问项目 → 可见 ==========
  test('PERM-UI-006: admin 访问项目 → 可见', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证项目选择器有选项
    await page.click('#projectSelector');
    await page.waitForTimeout(500);

    const options = page.locator('#projectSelector option');
    const count = await options.count();
    expect(count).toBeGreaterThan(1); // 至少有一个项目
  });

  // ========== PERM-UI-007: user 访问项目 → 可见 ==========
  test('PERM-UI-007: user 访问项目 → 可见', async ({ page }) => {
    // 先创建 user
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1000);

    try {
      await page.evaluate(async () => {
        await fetch('/api/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ username: 'testuser3', password: 'test123', role: 'user' })
        });
      });
    } catch (e) {}

    await page.click('button:has-text("退出")');
    await page.waitForTimeout(1000);

    // 用 user 登录
    await page.fill('#loginUsername', 'testuser3');
    await page.fill('#loginPassword', 'test123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证项目选择器有选项
    await page.click('#projectSelector');
    await page.waitForTimeout(500);

    const options = page.locator('#projectSelector option');
    const count = await options.count();
    expect(count).toBeGreaterThan(1);
  });

  // ========== PERM-UI-008: guest 访问项目 → 可见 ==========
  test('PERM-UI-008: guest 访问项目 → 可见', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'guest');
    await page.fill('#loginPassword', 'guest123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证项目选择器有选项
    await page.click('#projectSelector');
    await page.waitForTimeout(500);

    const options = page.locator('#projectSelector option');
    const count = await options.count();
    expect(count).toBeGreaterThan(1);
  });

  // ========== PERM-UI-009: user 可以创建 TC ==========
  test('PERM-UI-009: user 可以创建 TC', async ({ page }) => {
    // 先创建 user
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1000);

    try {
      await page.evaluate(async () => {
        await fetch('/api/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ username: 'testuser4', password: 'test123', role: 'user' })
        });
      });
    } catch (e) {}

    await page.click('button:has-text("退出")');
    await page.waitForTimeout(1000);

    // 用 user 登录
    await page.fill('#loginUsername', 'testuser4');
    await page.fill('#loginPassword', 'test123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 选择项目
    await page.click('#projectSelector');
    await page.waitForTimeout(500);
    await page.selectOption('#projectSelector', { label: 'SOC_DV' });
    await page.waitForTimeout(1000);

    // 切换到 TC 标签
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForTimeout(1000);

    // 点击添加 TC 按钮
    const addBtn = page.locator('button:has-text("+ 添加 TC")');
    await addBtn.click();
    await page.waitForTimeout(500);

    // 验证模态框打开
    const modal = page.locator('#tcModal');
    await expect(modal).toBeVisible();
  });
});
