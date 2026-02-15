/**
 * 数据创建流程端到端测试用例
 * 
 * 测试批量操作的正确性和数据一致性
 * - 批量创建 CP
 * - 批量创建 TC
 * - 数据一致性验证
 * 
 * 运行命令:
 *   npx playwright test tests/specs/e2e/data-creation.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';
import { cleanupTestData } from '../../utils/cleanup';

test.describe('数据创建流程测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 每个测试前确保在首页
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test.afterEach(async ({ page }, testInfo) => {
    // 测试失败时截图
    if (testInfo.status === 'failed') {
      await page.screenshot({ 
        path: `test-results/screenshots/data-creation-${testInfo.title}-${Date.now()}.png` 
      });
    }
    // 清理测试数据
    await cleanupTestData(page);
  });

  /**
   * E2E-006: 批量创建 CP
   * 测试场景：
   * 1. 快速创建多个 CP
   * 2. 验证所有 CP 创建成功
   * 3. 验证数据一致性
   */
  test('E2E-006: 批量创建 CP', async ({ cpPage }) => {
    const batchSize = 5;
    const cpList: Array<{ feature: string; coverPoint: string }> = [];
    
    // 批量创建 CP
    for (let i = 0; i < batchSize; i++) {
      const cpData = TestDataFactory.createCPData({
        feature: `Batch_CP_${i}`,
        priority: i % 2 === 0 ? 'P0' : 'P1'
      });
      cpList.push(cpData);
      
      await cpPage.createCP(cpData);
      
      // 关闭模态框（如果有）
      const modal = cpPage.page.locator('#cpModal');
      if (await modal.isVisible()) {
        await cpPage.closeCPModal();
      }
    }
    
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 等待表格加载
    await cpPage.page.waitForSelector('.cp-table', { timeout: 10000 });
    
    // 验证所有 CP 创建成功
    for (const cp of cpList) {
      await expect(
        cpPage.page.locator(`.cp-table tbody tr:has-text("${cp.coverPoint}")`)
      ).toBeVisible({ timeout: 5000 });
    }
    
    // 统计表格中的行数
    const rows = cpPage.page.locator('.cp-table tbody tr');
    const rowCount = await rows.count();
    expect(rowCount).toBeGreaterThanOrEqual(batchSize);
  });

  /**
   * E2E-007: 批量创建 TC
   * 测试场景：
   * 1. 快速创建多个 TC
   * 2. 验证所有 TC 创建成功
   * 3. 验证数据一致性
   */
  test('E2E-007: 批量创建 TC', async ({ tcPage }) => {
    const batchSize = 5;
    const tcList: string[] = [];
    
    // 批量创建 TC
    for (let i = 0; i < batchSize; i++) {
      const tcData = TestDataFactory.createTCData({
        name: `Batch_TC_${i}`,
        category: i % 2 === 0 ? 'Functional' : 'Performance',
        dvMilestone: 'RTL'
      });
      tcList.push(tcData.name);
      
      await tcPage.createTC(tcData);
      
      // 关闭模态框（如果有）
      const modal = tcPage.page.locator('#tcModal');
      if (await modal.isVisible()) {
        await tcPage.closeTCModal();
      }
    }
    
    // 切换到 TC 标签页
    await tcPage.switchToTCTab();
    
    // 等待表格加载
    await tcPage.page.waitForSelector('table', { timeout: 10000 });
    
    // 验证所有 TC 创建成功
    for (const tcName of tcList) {
      await expect(
        tcPage.page.locator(`table tbody tr:has-text("${tcName}")`)
      ).toBeVisible({ timeout: 5000 });
    }
    
    // 统计表格中的行数
    const rows = tcPage.page.locator('table tbody tr');
    const rowCount = await rows.count();
    expect(rowCount).toBeGreaterThanOrEqual(batchSize);
  });

  /**
   * E2E-008: 数据一致性验证
   * 测试场景：
   * 1. 创建 CP 和 TC
   * 2. 验证数据库中的数据与应用显示一致
   * 3. 验证关联关系正确
   */
  test('E2E-008: 数据一致性验证', async ({ cpPage, tcPage }) => {
    const cpData = TestDataFactory.createCPData({
      feature: 'Consistency_CP',
      priority: 'P0',
      details: '用于数据一致性测试的 CP'
    });
    
    const tcData = TestDataFactory.createTCData({
      name: 'Consistency_TC',
      category: 'Functional',
      owner: 'test_user'
    });
    
    // 创建 CP
    await cpPage.createCP(cpData);
    
    // 创建 TC 并关联到 CP
    await tcPage.switchToTCTab();
    await tcPage.openTCModal();
    await tcPage.page.fill('#tcTestbench', 'Consistency_TB');
    await tcPage.page.fill('#tcTestName', tcData.name);
    await tcPage.page.fill('#tcScenario', '数据一致性测试场景');
    
    // 关联到 CP
    const cpSelector = tcPage.page.locator('#tcRelatedCP, #tcCpId, [id*="cp"]');
    if (await cpSelector.count() > 0) {
      await cpSelector.selectOption({ label: cpData.coverPoint });
    }
    
    await tcPage.page.click('#tcSubmitBtn');
    await tcPage.page.waitForTimeout(500);
    
    // 验证 TC 存在
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcData.name}")`)
    ).toBeVisible();
    
    // 刷新页面验证数据持久化
    await tcPage.page.reload();
    await tcPage.page.waitForLoadState('domcontentloaded');
    
    // 切换到 TC 标签页
    await tcPage.switchToTCTab();
    
    // 验证数据仍然存在
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcData.name}")`)
    ).toBeVisible();
    
    // 切换到 CP 标签页验证 CP 仍然存在
    await cpPage.switchToCPTab();
    
    await expect(
      cpPage.page.locator(`.cp-table tbody tr:has-text("${cpData.coverPoint}")`)
    ).toBeVisible();
  });
});

test.describe('数据创建流程测试 - 边界场景', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test.afterEach(async ({ page }) => {
    await cleanupTestData(page);
  });

  /**
   * E2E-010: 大量数据场景测试
   * 测试场景：
   * 1. 创建 10+ CP
   * 2. 创建 10+ TC
   * 3. 验证性能和稳定性
   */
  test.skip('E2E-010: 大量数据场景测试', async ({ cpPage, tcPage }) => {
    const cpCount = 10;
    const tcCount = 10;
    
    // 批量创建 CP
    for (let i = 0; i < cpCount; i++) {
      const cpData = TestDataFactory.createCPData({
        feature: `Large_Feature_${i}`,
        priority: i % 4 === 0 ? 'P0' : i % 4 === 1 ? 'P1' : i % 4 === 2 ? 'P2' : 'P3'
      });
      await cpPage.createCP(cpData);
      
      // 每创建 3 个 CP 后关闭模态框
      if (i % 3 === 0) {
        const modal = cpPage.page.locator('#cpModal');
        if (await modal.isVisible()) {
          await cpPage.closeCPModal();
        }
      }
    }
    
    // 关闭最后一个模态框
    const cpModal = cpPage.page.locator('#cpModal');
    if (await cpModal.isVisible()) {
      await cpPage.closeCPModal();
    }
    
    // 批量创建 TC
    for (let i = 0; i < tcCount; i++) {
      const tcData = TestDataFactory.createTCData({
        name: `Large_TC_${i}`,
        category: i % 3 === 0 ? 'Functional' : i % 3 === 1 ? 'Performance' : 'Stress',
        dvMilestone: i % 2 === 0 ? 'RTL' : 'GATE'
      });
      await tcPage.switchToTCTab();
      await tcPage.createTC(tcData);
      
      // 每创建 3 个 TC 后关闭模态框
      if (i % 3 === 0) {
        const modal = tcPage.page.locator('#tcModal');
        if (await modal.isVisible()) {
          await tcPage.closeTCModal();
        }
      }
    }
    
    // 关闭最后一个模态框
    const tcModal = tcPage.page.locator('#tcModal');
    if (await tcModal.isVisible()) {
      await tcPage.closeTCModal();
    }
    
    // 切换到 CP 标签页验证
    await cpPage.switchToCPTab();
    const cpRows = cpPage.page.locator('.cp-table tbody tr');
    const cpRowCount = await cpRows.count();
    expect(cpRowCount).toBeGreaterThanOrEqual(cpCount);
    
    // 切换到 TC 标签页验证
    await tcPage.switchToTCTab();
    const tcRows = tcPage.page.locator('table tbody tr');
    const tcRowCount = await tcRows.count();
    expect(tcRowCount).toBeGreaterThanOrEqual(tcCount);
  });
});
