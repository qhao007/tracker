/**
 * Tracker Playwright 冒烟测试
 *
 * 目的：验证开发版服务是否正常运行
 * 运行命令: npx playwright test tests/test_smoke.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_URL || 'http://localhost:8081';

test.describe('前端完整性检查', () => {
  test('页面基本访问', async ({ page }) => {
    // 1. 直接访问页面
    const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // 2. 验证 HTTP 状态码
    expect(response?.status()).toBe(200);

    // 3. 验证页面标题（简单检查）
    await expect(page).toHaveTitle(/.*Tracker.*/);
  });

  test('项目列表加载', async ({ page }) => {
    const errors = [];
    
    // 收集控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(`Console Error: ${msg.text()}`);
      }
    });
    page.on('pageerror', err => {
      errors.push(`Page Error: ${err.message}`);
    });

    await page.goto(BASE_URL);
    
    // 等待项目加载（最多 5 秒）
    await page.waitForSelector('#projectSelector:not(:empty)', { timeout: 5000 });
    
    // 验证项目选择器有选项
    const options = page.locator('#projectSelector option');
    await expect(options.first()).not.toHaveAttribute('value', '');
    
    // 检查控制台错误
    if (errors.length > 0) {
      console.error('前端错误:', errors);
      throw new Error(`发现 ${errors.length} 个前端 JS 错误: ${errors.join('; ')}`);
    }
  });

  test('选择项目后数据加载', async ({ page }) => {
    const errors = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(`Console Error: ${msg.text()}`);
      }
    });
    page.on('pageerror', err => {
      errors.push(`Page Error: ${err.message}`);
    });

    await page.goto(BASE_URL);
    
    // 等待项目加载
    await page.waitForSelector('#projectSelector:not(:empty)', { timeout: 5000 });
    
    // 选择第一个项目
    await page.selectOption('#projectSelector', { index: 0 });
    
    // 等待数据加载（CP 列表）
    await page.waitForSelector('#cpList tr', { timeout: 5000 });
    
    // 等待统计数据加载
    await expect(page.locator('#statTC')).not.toHaveText('0', { timeout: 3000 });
    
    // 检查控制台错误
    if (errors.length > 0) {
      console.error('前端错误:', errors);
      throw new Error(`发现 ${errors.length} 个前端 JS 错误: ${errors.join('; ')}`);
    }
  });
});
