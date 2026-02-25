/**
 * CP-TC 关联集成测试用例
 *
 * 测试 CP 和 TC 之间的关联功能
 *
 * 运行命令:
 *   npx playwright test tests/specs/integration/connections.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';
import { TestDataFactory } from '../../fixtures/test-data.factory';
import { cleanupProjectData } from '../../utils/cleanup';
import { setupDialogHandler, teardownDialogHandler } from '../../utils/dialog-helper';

test.describe('CP-TC 关联测试', () => {

  /**
   * 登录辅助函数 - v0.7.1 需要登录
   */
  async function loginAsAdmin(page: any) {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    // 填写登录表单
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(1000);
  }

  test.beforeEach(async ({ page }) => {
    // 登录 - v0.7.1 需要认证
    await loginAsAdmin(page);
    // 登录后等待页面加载完成
    try {
      await page.waitForSelector('#projectSelector', { timeout: 10000 });
      // ✅ 设置 dialog 处理器（只设置一次）
      setupDialogHandler(page);
    } catch (e) {
      // 如果页面已关闭，忽略错误
    }
  });

  test.afterEach(async ({ page }, testInfo) => {
    // ✅ 移除 dialog 处理器
    teardownDialogHandler(page);

    if (testInfo.status === 'failed') {
      await page.screenshot({
        path: `test-results/screenshots/connection-${testInfo.title}-${Date.now()}.png`
      });
    }
    // 清理项目数据，保留最新5条
    try {
      await cleanupProjectData(page);
    } catch (e) {
      // 忽略清理错误
    }
  });

  /**
   * CONN-001: 创建 CP 和 TC
   * 简化版本：分别创建 CP 和 TC，验证基本功能
   */
  test('CONN-001: 创建 CP 和 TC', async ({ page }) => {
    const cpName = TestDataFactory.generateCPName();
    const tcName = TestDataFactory.generateTCName();

    // ❌ 删除: page.on('dialog', async dialog => { ... });

    // 1. 创建 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Conn');
    await page.fill('#cpCoverPoint', cpName);
    await page.fill('#cpDetails', '测试关联 CP');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 2. 创建 TC
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 TC');
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: 10000 });
    await page.fill('#tcTestbench', 'tb_conn');
    await page.fill('#tcTestName', tcName);
    await page.fill('#tcScenario', '关联测试场景');
    await page.click('#tcModal button[type="submit"]');
    await page.waitForTimeout(2000);
  });

  /**
   * CONN-002: 展开 CP 详情
   */
  test('CONN-002: 展开 CP 详情', async ({ page }) => {
    const cpName = TestDataFactory.generateCPName();

    // 创建 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Detail');
    await page.fill('#cpCoverPoint', cpName);
    await page.fill('#cpDetails', '测试详情');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 验证 CP 存在
    const cpRow = page.locator(`#cpList tr:has-text("${cpName}")`).first();
    await expect(cpRow).toBeVisible({ timeout: 10000 });

    // 点击详情按钮
    const detailBtn = cpRow.locator('button:has-text("详情")');
    if (await detailBtn.count() > 0) {
      await detailBtn.click();
      await page.waitForTimeout(1000);
    }
  });

  /**
   * CONN-003: 编辑 CP
   */
  test('CONN-003: 编辑 CP', async ({ page }) => {
    const cpName = TestDataFactory.generateCPName();

    // 创建 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Edit');
    await page.fill('#cpCoverPoint', cpName);
    await page.fill('#cpDetails', '原始描述');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 编辑 CP
    const cpRow = page.locator(`#cpList tr:has-text("${cpName}")`).first();
    await expect(cpRow).toBeVisible({ timeout: 10000 });

    const editBtn = cpRow.locator('button:has-text("编辑")');
    if (await editBtn.count() > 0) {
      await editBtn.click();
      await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });

      // 修改描述
      await page.fill('#cpDetails', '更新后的描述');
      await page.click('#cpModal button[type="submit"]');
      await page.waitForTimeout(2000);
    }
  });
});

test.describe('CP-TC 关联测试 - 边界场景', () => {

  /**
   * 登录辅助函数 - v0.7.1 需要登录
   */
  async function loginAsAdmin(page: any) {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    // 填写登录表单
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(1000);
  }

  test.beforeEach(async ({ page }) => {
    // 登录 - v0.7.1 需要认证
    await loginAsAdmin(page);
    // 登录后等待页面加载完成
    try {
      await page.waitForSelector('#projectSelector', { timeout: 10000 });
      // ✅ 设置 dialog 处理器
      setupDialogHandler(page);
    } catch (e) {
      // 如果页面已关闭，忽略错误
    }
    // 清理项目数据，保留最新5条
    await cleanupProjectData(page);
    await page.waitForTimeout(500);
  });

  test.afterEach(async ({ page }) => {
    // ✅ 移除 dialog 处理器
    teardownDialogHandler(page);
  });

  /**
   * CONN-004: 创建多个 CP
   */
  test('CONN-004: 创建多个 CP', async ({ page }) => {
    const cpNames = [
      TestDataFactory.generateCPName('Multi1'),
      TestDataFactory.generateCPName('Multi2'),
      TestDataFactory.generateCPName('Multi3')
    ];

    // ❌ 删除: page.on('dialog', async dialog => { ... });

    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });

    // 创建多个 CP
    for (const name of cpNames) {
      await page.click('text=+ 添加 CP');
      await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
      await page.fill('#cpFeature', 'Feature_Multi');
      await page.fill('#cpCoverPoint', name);
      await page.fill('#cpDetails', '多CP测试');
      await page.click('#cpModal button[type="submit"]');
      await page.waitForTimeout(2000);
    }

    // 验证所有 CP 都存在
    for (const name of cpNames) {
      const cpRow = page.locator(`#cpList tr:has-text("${name}")`).first();
      await expect(cpRow).toBeVisible({ timeout: 10000 });
    }
  });

  /**
   * CONN-005: 创建多个 TC
   */
  test('CONN-005: 创建多个 TC', async ({ page }) => {
    const tcNames = [
      TestDataFactory.generateTCName('Multi1'),
      TestDataFactory.generateTCName('Multi2'),
      TestDataFactory.generateTCName('Multi3')
    ];

    // ❌ 删除: page.on('dialog', async dialog => { ... });

    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });

    // 创建多个 TC
    for (const name of tcNames) {
      await page.click('text=+ 添加 TC');
      await page.waitForSelector('#tcModal', { state: 'visible', timeout: 10000 });
      await page.fill('#tcTestbench', 'tb_multi');
      await page.fill('#tcTestName', name);
      await page.fill('#tcScenario', '多TC测试');
      await page.click('#tcModal button[type="submit"]');
      await page.waitForTimeout(2000);
    }

    // 验证所有 TC 都存在
    for (const name of tcNames) {
      const tcRow = page.locator(`#tcList tr:has-text("${name}")`).first();
      await expect(tcRow).toBeVisible({ timeout: 10000 });
    }
  });
});
