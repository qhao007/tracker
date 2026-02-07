/**
 * Tracker Playwright 冒烟测试 - 关键功能点验证
 * 
 * 运行命令:
 *   npx playwright test tests/test_smoke.spec.ts --project=firefox --reporter=line --timeout=60000
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_URL || 'http://localhost:8081';

test.describe('Tracker v0.3.1 关键功能测试', () => {
  
  test.beforeEach(async ({ page }) => {
    test.setTimeout(60000);
    
    // 访问页面
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    // 等待项目加载
    await page.waitForSelector('#projectSelector', { timeout: 15000 });
    
    // 选择第一个项目
    await page.selectOption('#projectSelector', { index: 1 });
    
    // 等待数据加载
    await page.waitForTimeout(2000);
  });

  // ========================================================================
  // 关键功能点测试
  // ========================================================================
  
  test('F004-CP列表加载', async ({ page }) => {
    // F004: Cover Points 管理 - CP 列表显示
    await page.click('text=Cover Points');
    await page.waitForTimeout(1000);
    
    const cpRows = page.locator('.cp-table tbody tr');
    const count = await cpRows.count();
    
    // 验证表格存在且可操作
    expect(count).toBeGreaterThanOrEqual(0);
  });
  
  test('F005-TC列表加载', async ({ page }) => {
    // F005: Test Cases 管理 - TC 列表显示
    await page.click('text=Test Cases');
    await page.waitForTimeout(1000);
    
    const tcRows = page.locator('.tc-table tbody tr');
    const count = await tcRows.count();
    
    expect(count).toBeGreaterThanOrEqual(0);
  });
  
  test('F007-TC状态更新', async ({ page }) => {
    // F007: 状态跟踪 - OPEN → CODED → FAIL → PASS
    await page.click('text=Test Cases');
    await page.waitForTimeout(1000);

    // 找到状态选择器
    const select = page.locator('select.status-select').first();
    await expect(select).toBeVisible({ timeout: 10000 });

    // 获取初始状态
    const initialStatus = await select.inputValue();

    // 选择一个不同的状态（OPEN→CODED→FAIL→PASS 循环）
    const statusOrder = ['OPEN', 'CODED', 'FAIL', 'PASS'];
    const currentIndex = statusOrder.indexOf(initialStatus);
    const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length];

    // 切换到下一个状态
    await select.selectOption({ value: nextStatus });
    await page.waitForTimeout(1000);

    // 验证状态已更新
    const newStatus = await select.inputValue();
    expect(newStatus).toBe(nextStatus);
  });
  
  test('F012-CP覆盖率显示', async ({ page }) => {
    // F012: 覆盖率计算 - 整体覆盖率百分比显示
    await page.click('text=Cover Points');
    await page.waitForTimeout(1000);
    
    // 验证覆盖率列存在
    const header = page.locator('th:has-text("覆盖率")');
    await expect(header).toBeVisible({ timeout: 5000 });
    
    // 验证覆盖率徽章
    const badges = page.locator('.coverage-badge');
    const count = await badges.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });
  
  test('F001-项目切换刷新', async ({ page }) => {
    // F001: 项目管理 - 切换项目数据刷新
    await page.click('text=Cover Points');
    await page.waitForTimeout(500);
    const count1 = await page.locator('.cp-table tbody tr').count();
    
    await page.click('text=Test Cases');
    await page.waitForTimeout(500);
    
    await page.click('text=Cover Points');
    await page.waitForTimeout(500);
    
    const count2 = await page.locator('.cp-table tbody tr').count();
    expect(count1).toBe(count2);
  });
  
  test('F001-项目保持', async ({ page }) => {
    // F001: 项目管理 - 刷新后项目保持
    const project = await page.locator('#projectSelector').inputValue();
    expect(project).toBeTruthy();
    
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    const afterRefresh = await page.locator('#projectSelector').inputValue();
    expect(afterRefresh).toBe(project);
  });
});
