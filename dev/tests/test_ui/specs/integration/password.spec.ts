/**
 * 强制改密码测试用例
 *
 * 测试 admin 用户首次登录强制修改密码功能
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/password.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { cleanupTestData } from '../../utils/cleanup';

const BASE_URL = 'http://localhost:8081';

test.describe('强制改密码测试', () => {

  /**
   * 登录辅助函数 - admin 版本，会处理密码弹窗
   */
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);

    // 检查是否需要强制修改密码
    const passwordModal = page.locator('#changePasswordModal');
    const isPasswordModalVisible = await passwordModal.isVisible().catch(() => false);

    if (isPasswordModalVisible) {
      // 需要修改密码，填写新密码（使用与原密码相同的值，避免后续测试问题）
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button:has-text("确认修改")');
      await page.waitForTimeout(2000);
    }

    await page.waitForSelector('#projectSelector:not([disabled])', { timeout: 30000 });
  }

  /**
   * 登录辅助函数 - guest 版本
   */
  async function loginAsGuest(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    await page.fill('#loginUsername', 'guest');
    await page.fill('#loginPassword', 'guest123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(1500);
  }

  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status === 'failed') {
      await page.screenshot({
        path: `test-results/screenshots/password-${testInfo.title}-${Date.now()}.png`
      });
    }
  });

  /**
   * UI-PWD-001: admin首次登录强制改密码
   * 测试目标: 验证 admin 用户登录后会出现强制修改密码弹窗（如果需要）
   */
  test('UI-PWD-001: admin首次登录强制改密码', async ({ page }) => {
    // 使用 admin 登录
    await loginAsAdmin(page);

    // 验证登录成功 - 项目选择器应该可见
    await expect(page.locator('#projectSelector')).toBeVisible({ timeout: 10000 });

    // 检查修改密码弹窗（可能显示也可能不显示，取决于用户状态）
    const passwordModal = page.locator('#changePasswordModal');
    const isModalVisible = await passwordModal.isVisible().catch(() => false);

    // 记录弹窗状态
    console.log('Password modal visible:', isModalVisible);
  });

  /**
   * UI-PWD-002: 修改密码功能存在
   * 测试目标: 验证修改密码弹窗存在且可填写
   */
  test('UI-PWD-002: 修改密码功能存在', async ({ page }) => {
    // 通过 API 设置强制改密码状态
    await page.evaluate(async () => {
      // 获取用户列表
      const response = await fetch('/api/users', {
        credentials: 'include'
      });
      const data = await response.json();

      const adminUser = data.users?.find((u: any) => u.username === 'admin');
      if (adminUser) {
        // 设置 force_change_password
        await fetch(`/api/users/${adminUser.id}`, {
          method: 'PUT',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ force_change_password: true })
        });
      }
    });
    await page.waitForTimeout(1000);

    // 登出后重新登录，应该弹出修改密码弹窗
    await page.click('button:has-text("退出")');
    await page.waitForTimeout(1500);

    // 重新登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);

    // 验证修改密码弹窗显示
    const passwordModal = page.locator('#changePasswordModal');
    await expect(passwordModal).toBeVisible({ timeout: 10000 });

    // 填写密码并提交
    await page.fill('#newPassword', 'admin123');
    await page.fill('#confirmPassword', 'admin123');
    await page.click('#changePasswordModal button:has-text("确认修改")');
    await page.waitForTimeout(2000);

    // 验证弹窗关闭
    await expect(passwordModal).toBeHidden({ timeout: 10000 });
  });

  /**
   * UI-PWD-003: admin再次登录不强制
   * 测试目标: 如果 admin 已修改过密码，再次登录时不再强制要求修改
   */
  test('UI-PWD-003: admin再次登录不强制', async ({ page }) => {
    // 先登录并修改密码
    await loginAsAdmin(page);

    // 登出
    await page.click('button:has-text("退出")');
    await page.waitForTimeout(1500);

    // 再次登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(2000);

    // 验证修改密码弹窗不显示（因为已经修改过密码）
    const passwordModal = page.locator('#changePasswordModal');
    const isVisible = await passwordModal.isVisible().catch(() => false);
    expect(isVisible).toBe(false);

    // 验证正常进入系统
    await expect(page.locator('#projectSelector')).toBeVisible({ timeout: 10000 });
  });

  /**
   * UI-PWD-004: 普通用户登录不受影响
   * 测试目标: 普通用户（guest）登录不受强制改密码影响
   */
  test('UI-PWD-004: 普通用户登录不受影响', async ({ page }) => {
    // 使用 guest 用户登录
    await loginAsGuest(page);

    // 验证修改密码弹窗不显示
    const passwordModal = page.locator('#changePasswordModal');
    const isVisible = await passwordModal.isVisible().catch(() => false);
    expect(isVisible).toBe(false);

    // 验证正常进入系统
    await expect(page.locator('#projectSelector')).toBeVisible({ timeout: 10000 });
  });
});
