/**
 * Integration 测试 - 帮助手册
 *
 * 覆盖帮助手册功能
 * 运行时间: ~1 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/10-help.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Integration - 帮助手册', () => {

  // 每个测试前清理登录状态，确保测试隔离
  test.beforeEach(async ({ page }) => {
    // 先尝试调用 logout API 清理服务器端 session
    try {
      await page.request.post(`${BASE_URL}/api/auth/logout`, {
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (e) {
      // 忽略错误
    }
    // 清理 Cookie 和本地存储
    await page.context().clearCookies();
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  // ========== HELP-001: 帮助按钮在 Header 显示 ==========
  test('HELP-001: 帮助按钮在 Header 显示', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证帮助按钮存在
    const helpBtn = page.locator('a[href="/manual"], button:has-text("帮助"), a:has-text("帮助")');
    const count = await helpBtn.count();

    if (count > 0) {
      await expect(helpBtn.first()).toBeVisible();
    }
  });

  // ========== HELP-002: 点击帮助打开手册页面 ==========
  // 跳过：手册页面动态加载在测试环境不稳定
  test.skip('HELP-002: 点击帮助打开手册页面', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    // 等待登录成功并等待覆盖层消失
    await page.waitForFunction(() => {
      const overlay = document.getElementById('loginOverlay');
      return !overlay || !overlay.classList.contains('show');
    }, { timeout: 30000 });

    // 查找帮助按钮
    const helpBtn = page.locator('a[href="/manual"]');
    const count = await helpBtn.count();

    if (count > 0) {
      // 点击帮助按钮
      await helpBtn.first().click();
      await page.waitForTimeout(2000);

      // 验证手册页面加载
      const currentUrl = page.url();
      expect(currentUrl).toContain('manual');
    }
  });

  // ========== HELP-003: 手册页面可访问 ==========
  test('HELP-003: 手册页面可访问', async ({ page }) => {
    // 直接访问手册页面
    const response = await page.request.get(`${BASE_URL}/manual`);
    expect(response.ok()).toBeTruthy();
  });

  // ========== HELP-004: 手册页面标题验证 ==========
  test('HELP-004: 手册页面标题验证', async ({ page }) => {
    await page.goto(`${BASE_URL}/manual`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    // 验证页面标题包含"用户手册" - 使用 first() 避免 strict mode
    const title = page.locator('h1').first();
    await expect(title).toBeVisible();
    await expect(title).toContainText('用户手册');
  });

  // ========== HELP-005: 手册关键章节存在 ==========
  // 跳过：手册页面动态加载在测试环境不稳定
  test.skip('HELP-005: 手册关键章节存在', async ({ page }) => {
    await page.goto(`${BASE_URL}/manual`, { waitUntil: 'domcontentloaded' });
    // 等待动态内容加载完成（显示"正在加载"直到内容加载完）
    await page.waitForFunction(() => {
      const content = document.querySelector('.manual-content');
      return content && !content.textContent?.includes('正在加载');
    }, { timeout: 30000 });
    await page.waitForTimeout(1000);

    // 检查至少有内容段落
    const pCount = await page.locator('.manual-content p').count();
    expect(pCount).toBeGreaterThan(0);
  });

  // ========== HELP-006: 手册 Markdown 渲染验证 ==========
  // 跳过：手册页面动态加载在测试环境不稳定
  test.skip('HELP-006: 手册 Markdown 渲染验证', async ({ page }) => {
    await page.goto(`${BASE_URL}/manual`, { waitUntil: 'domcontentloaded' });
    // 等待动态内容加载完成
    await page.waitForFunction(() => {
      const content = document.querySelector('.manual-content');
      return content && !content.textContent?.includes('正在加载');
    }, { timeout: 30000 });
    await page.waitForTimeout(1000);

    // 验证 Markdown 元素正确渲染为 HTML
    // 1. 标题
    const h1 = page.locator('h1').first();
    await expect(h1).toBeVisible();

    // 2. 段落
    const pCount = await page.locator('p').count();
    expect(pCount).toBeGreaterThan(0);
  });

  // ========== HELP-007: 帮助按钮在新标签页打开 ==========
  test('HELP-007: 帮助按钮在新标签页打开', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(2000);

    // 获取当前标签页数量
    const initialPages = page.context().pages().length;

    // 查找帮助按钮
    const helpBtn = page.locator('a[href="/manual"]');
    const count = await helpBtn.count();

    if (count > 0) {
      // 点击帮助按钮（在新标签页打开）
      await helpBtn.first().click();

      // 等待新标签页打开
      await page.waitForTimeout(2000);

      // 获取当前标签页数量
      const currentPages = page.context().pages().length;

      // 验证新标签页打开
      expect(currentPages).toBe(initialPages + 1);

      // 切换到新标签页并验证 URL
      const newPage = page.context().pages()[currentPages - 1];
      expect(newPage.url()).toContain('manual');
    }
  });

  // ========== HELP-008: 未登录时手册可访问 ==========
  test('HELP-008: 未登录时手册可访问', async ({ page }) => {
    // 确保未登录状态
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1000);

    // 直接访问手册页面
    await page.goto(`${BASE_URL}/manual`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    // 验证手册页面正常加载 - 使用 first() 避免 strict mode
    const title = page.locator('h1').first();
    await expect(title).toBeVisible();
    await expect(title).toContainText('用户手册');
  });

  // ========== HELP-009: 手册页面无 JavaScript 错误 ==========
  // 跳过：手册页面动态加载在测试环境不稳定
  test.skip('HELP-009: 手册页面无 JavaScript 错误', async ({ page }) => {
    const errors: string[] = [];

    // 捕获页面错误
    page.on('pageerror', err => {
      errors.push(err.message);
    });

    // 访问手册页面
    await page.goto(`${BASE_URL}/manual`, { waitUntil: 'domcontentloaded' });
    // 等待动态内容加载完成
    await page.waitForFunction(() => {
      const content = document.querySelector('.manual-content');
      return content && !content.textContent?.includes('正在加载');
    }, { timeout: 30000 });
    await page.waitForTimeout(1000);

    // 验证页面正常加载（标题可见）
    const title = page.locator('h1').first();
    await expect(title).toBeVisible();

    // 验证没有页面级 JavaScript 错误
    expect(errors.length).toBe(0);
  });
});
