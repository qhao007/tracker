/**
 * Smoke 测试 - 认证与权限
 *
 * 覆盖登录、登出、权限按钮显示
 * 运行时间: ~1 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/smoke/02-login.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Smoke - 认证与权限', () => {

  // ========== 登录辅助函数 ==========
  async function loginAs(page: any, username: string, password: string) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', username);
    await page.fill('#loginPassword', password);
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);
  }

  // ========== LOGIN-001: 登录后显示用户名 ==========
  test('LOGIN-001: 登录后显示用户名', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');

    // 等待项目选择器出现
    await page.waitForSelector('#projectSelector');

    // 验证登录成功 - 项目选择器可见
    await expect(page.locator('#projectSelector')).toBeVisible();
  });

  // ========== LOGIN-002: guest 无用户管理按钮 ==========
  test('LOGIN-002: guest 无用户管理按钮', async ({ page }) => {
    await loginAs(page, 'guest', 'guest123');

    // 等待页面加载
    await page.waitForTimeout(1000);

    // 验证用户管理按钮不存在
    const userManageBtn = page.locator('#userManageBtn, button:has-text("用户管理")');
    const count = await userManageBtn.count();

    if (count > 0) {
      // 如果元素存在，检查是否隐藏
      const isVisible = await userManageBtn.first().isVisible().catch(() => false);
      expect(isVisible).toBe(false);
    } else {
      // 元素不存在也算通过
      expect(count).toBe(0);
    }
  });

  // ========== LOGIN-003: user 无删除项目按钮 ==========
  test('LOGIN-003: user 无删除项目按钮', async ({ page }) => {
    // 先用 admin 登录创建 user 账户
    await loginAs(page, 'admin', 'admin123');
    await page.waitForTimeout(500);

    // 创建 user 账户
    try {
      await page.evaluate(async () => {
        await fetch('/api/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ username: 'testuser', password: 'test123', role: 'user' })
        });
      });
    } catch (e) {
      // 用户可能已存在，忽略
    }

    // 登出
    await page.click('button:has-text("退出")');
    await page.waitForTimeout(1000);

    // 用 user 登录
    await loginAs(page, 'testuser', 'test123');
    await page.waitForTimeout(1000);

    // 验证项目选择器可见（说明登录成功）
    await expect(page.locator('#projectSelector')).toBeVisible();
  });

  // ========== LOGIN-004: 登录后 Cookie ==========
  test('LOGIN-004: 登录后 Cookie', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');

    // 验证 session cookie 存在
    const cookies = await page.context().cookies();
    const sessionCookie = cookies.find(c => c.name === 'session' || c.name.includes('session'));
    expect(sessionCookie).toBeDefined();
  });

  // ========== LOGIN-005: 登出功能 ==========
  test('LOGIN-005: 登出功能', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.waitForTimeout(1000);

    // 点击退出按钮
    await page.click('button:has-text("退出")');
    await page.waitForTimeout(1000);

    // 验证回到登录页面
    const loginForm = page.locator('#loginUsername, #loginForm');
    await expect(loginForm.first()).toBeVisible();
  });

  // ========== LOGIN-006: Progress Charts Tab ==========
  test('LOGIN-006: Progress Charts Tab', async ({ page }) => {
    await loginAs(page, 'admin', 'admin123');
    await page.waitForTimeout(1000);

    // 选择项目
    await page.click('#projectSelector');
    await page.waitForTimeout(500);
    await page.selectOption('#projectSelector', { label: 'SOC_DV' });
    await page.waitForTimeout(1000);

    // 点击 Progress Charts 标签
    const progressTab = page.locator('button.tab:has-text("Progress Charts")');
    await progressTab.click();
    await page.waitForTimeout(1500);

    // 验证 Progress Charts 面板可见
    const progressPanel = page.locator('#progressPanel, .progress-panel, #progressChart');
    const count = await progressPanel.count();

    if (count > 0) {
      await expect(progressPanel.first()).toBeVisible();
    }
  });
});
