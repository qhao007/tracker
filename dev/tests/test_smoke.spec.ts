/**
 * Tracker Playwright 冒烟测试 - 简化版
 *
 * 运行命令:
 *   npx playwright test tests/test_smoke.spec.ts --project=firefox --reporter=line
 *
 * 优化策略:
 * - 直接使用 test_data 下的已有项目，避免创建/删除开销
 * - 减少测试项，聚焦核心功能验证
 * - 使用条件等待替代固定延迟
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_URL || 'http://localhost:8081';

// 直接使用已有的测试项目（避免创建/删除开销）
const TEST_PROJECT_NAME = '冒烟测试专用项目_20260209_1017';

test.describe('Tracker 关键功能测试', () => {

  test.beforeEach(async ({ page }) => {
    test.setTimeout(60000);

    // 访问页面 - 使用 domcontentloaded 加速
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // 等待项目选择器可用
    await expect(page.locator('#projectSelector')).toBeVisible({ timeout: 15000 });

    // 直接选择已有的测试项目
    const projectOption = page.locator(`#projectSelector option:has-text("${TEST_PROJECT_NAME}")`);
    await expect(projectOption).toBeVisible({ timeout: 5000 });
    await page.selectOption('#projectSelector', projectOption);

    // 等待数据加载完成
    await page.waitForSelector('.cp-table tbody tr', { timeout: 10000 });
  });

  // ========================================================================
  // 测试项 1: CP 列表加载和覆盖率显示
  // ========================================================================

  test('F004+F012-CP列表和覆盖率', async ({ page }) => {
    // 验证 CP 表格可见
    await expect(page.locator('.cp-table')).toBeVisible({ timeout: 5000 });

    // 验证覆盖率列存在
    await expect(page.locator('th:has-text("覆盖率")')).toBeVisible({ timeout: 5000 });

    // 验证 Priority 列存在
    await expect(page.locator('th:has-text("Priority")')).toBeVisible({ timeout: 5000 });

    // 获取 CP 行数
    const cpRows = page.locator('.cp-table tbody tr');
    await expect(cpRows.first()).toBeVisible({ timeout: 5000 });
  });

  // ========================================================================
  // 测试项 2: TC 列表加载和状态更新
  // ========================================================================

  test('F005+F007-TC列表和状态更新', async ({ page }) => {
    // 切换到 TC 列表
    await page.click('text=Test Cases');

    // 验证 TC 表格可见
    await expect(page.locator('.tc-table')).toBeVisible({ timeout: 5000 });

    // 验证 Status Date 列存在
    await expect(page.locator('th:has-text("Status Date")')).toBeVisible({ timeout: 5000 });

    // 验证 Target Date 列存在
    await expect(page.locator('th:has-text("Target Date")')).toBeVisible({ timeout: 5000 });

    // 找到状态选择器并验证
    const statusSelect = page.locator('select.status-select').first();
    await expect(statusSelect).toBeVisible({ timeout: 5000 });

    // 测试状态更新
    const initialStatus = await statusSelect.inputValue();
    const statusOrder = ['OPEN', 'CODED', 'FAIL', 'PASS'];
    const currentIndex = statusOrder.indexOf(initialStatus);
    const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length];

    // 更新状态
    await statusSelect.selectOption({ value: nextStatus });

    // 验证状态已更新
    await expect(statusSelect).toHaveValue(nextStatus, { timeout: 5000 });
  });
});
