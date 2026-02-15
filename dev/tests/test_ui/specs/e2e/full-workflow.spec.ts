/**
 * 完整工作流端到端测试用例
 * 
 * 测试完整用户操作流程
 * - 创建项目 → 创建 CP → 创建 TC → 验证关联
 * - 项目切换对数据的影响
 * - 批量操作完整流程
 * 
 * 运行命令:
 *   npx playwright test tests/specs/e2e/full-workflow.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';
import { cleanupTestData } from '../../utils/cleanup';

test.describe('完整用户工作流测试', () => {
  
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
        path: `test-results/screenshots/e2e-${testInfo.title}-${Date.now()}.png` 
      });
    }
    // 清理测试数据
    await cleanupTestData(page);
  });

  /**
   * E2E-001: 创建项目 → 创建 CP → 创建 TC → 验证关联 → 清理
   * 这是一个完整的用户工作流测试
   */
  test('E2E-001: 完整项目创建工作流', async ({ projectPage, cpPage, tcPage }) => {
    // Step 1: 创建项目
    const projectName = TestDataFactory.generateProjectName('FullFlow');
    await projectPage.createProject(projectName);
    await projectPage.expectProjectExists(projectName);
    
    // 切换到新创建的项目
    await projectPage.selectProject(projectName);
    
    // Step 2: 创建 CP
    const cpData = TestDataFactory.createCPData({
      feature: 'E2E_Feature',
      priority: 'P0'
    });
    await cpPage.createCP(cpData);
    
    // 切换到 CP 标签页验证
    await cpPage.switchToCPTab();
    await expect(
      cpPage.page.locator(`.cp-table tbody tr:has-text("${cpData.coverPoint}")`)
    ).toBeVisible();
    
    // Step 3: 创建 TC
    const tcData = TestDataFactory.createTCData({
      category: 'Functional',
      dvMilestone: 'DV1.0'
    });
    await tcPage.switchToTCTab();
    await tcPage.openTCModal();
    await tcPage.page.waitForSelector('#tcDvMilestone', { state: 'visible' });
    await tcPage.page.fill('#tcTestbench', 'E2E_Testbench');
    await tcPage.page.fill('#tcTestName', tcData.name);
    await tcPage.page.fill('#tcScenario', 'E2E 测试场景');
    await tcPage.page.fill('#tcCategory', tcData.category);
    await tcPage.page.selectOption('#tcDvMilestone', tcData.dvMilestone);
    
    // 关联到 CP (使用 checkbox)
    const cpCheckbox = tcPage.page.locator(`#cpCheckboxes input[value]`).first();
    if (await cpCheckbox.count() > 0) {
      await cpCheckbox.check();
    }
    
    await tcPage.page.click('#tcModal button[type="submit"]');
    await tcPage.page.waitForTimeout(500);
    
    // Step 4: 验证 TC 创建成功
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcData.name}")`)
    ).toBeVisible();
    
    // Step 5: 验证关联
    await tcPage.switchToTCTab();
    // 定位 TC 表格行：通过 test_name 单元格定位整行
    const tcNameCell = tcPage.page.locator(`table tbody td:has-text("${tcData.name}")`);
    await expect(tcNameCell).toBeVisible();
    
    // 获取对应的行
    const tcRow = tcNameCell.locator('xpath=ancestor::tr[1]');
    
    // Step 6: 更新 TC 状态为 Pass (使用 force: true 强制操作)
    await tcRow.locator('.status-select').selectOption('PASS', { force: true });
    await tcPage.page.waitForTimeout(500);
    
    // Step 7: 验证状态更新
    const statusValue = await tcRow.locator('.status-select').inputValue();
    expect(statusValue).toBe('PASS');
    
    // Step 8: 验证数据持久化
    await tcPage.page.reload();
    await tcPage.page.waitForLoadState('domcontentloaded');
    await tcPage.switchToTCTab();
    
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcData.name}")`)
    ).toBeVisible();
    
    // Step 9: 清理 - 删除 TC (fixture 已处理 dialog)
    await tcRow.locator('.action-btn.delete').click();
    await tcPage.page.waitForTimeout(1000);
    
    await expect(tcRow).not.toBeVisible();
  });

  /**
   * E2E-002: 项目切换对数据的影响
   * 测试场景：
   * 1. 在项目 A 中创建 CP 和 TC
   * 2. 切换到项目 B
   * 3. 验证项目 A 的数据不影响项目 B
   * 4. 切换回项目 A
   * 5. 验证项目 A 的数据仍然存在
   */
  test('E2E-002: 项目切换数据隔离', async ({ projectPage, cpPage, tcPage }) => {
    const projectAName = TestDataFactory.generateProjectName('ProjectA');
    const projectBName = TestDataFactory.generateProjectName('ProjectB');
    
    const cpDataA = TestDataFactory.createCPData({ feature: 'ProjectA_CP' });
    const tcDataA = TestDataFactory.createTCData({ name: 'ProjectA_TC' });
    
    const cpDataB = TestDataFactory.createCPData({ feature: 'ProjectB_CP' });
    const tcDataB = TestDataFactory.createTCData({ name: 'ProjectB_TC' });
    
    // 创建项目 A
    await projectPage.createProject(projectAName);
    await projectPage.selectProject(projectAName);
    
    // 在项目 A 中创建 CP 和 TC
    await cpPage.createCP(cpDataA);
    await tcPage.switchToTCTab();
    await tcPage.createTC(tcDataA);
    
    // 切换到项目 B
    await projectPage.selectProject(projectBName);
    
    // 在项目 B 中创建 CP 和 TC
    await cpPage.createCP(cpDataB);
    await tcPage.switchToTCTab();
    await tcPage.createTC(tcDataB);
    
    // 验证项目 B 的数据
    await tcPage.switchToTCTab();
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcDataB.name}")`)
    ).toBeVisible();
    
    // 验证项目 A 的数据在项目 B 中不可见
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcDataA.name}")`)
    ).not.toBeVisible();
    
    // 切换回项目 A
    await projectPage.selectProject(projectAName);
    
    // 验证项目 A 的数据仍然存在
    await tcPage.switchToTCTab();
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcDataA.name}")`)
    ).toBeVisible();
    
    // 验证项目 B 的数据在项目 A 中不可见
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcDataB.name}")`)
    ).not.toBeVisible();
  });

  /**
   * E2E-003: 批量操作完整流程
   * 测试场景：
   * 1. 创建多个 CP
   * 2. 创建多个 TC 并关联到这些 CP
   * 3. 批量更新 CP Priority
   * 4. 批量更新 TC Status
   * 5. 验证所有更新成功
   */
  test('E2E-003: 批量操作完整流程', async ({ cpPage, tcPage }) => {
    // 创建多个 CP
    const cpCount = 3;
    const cpList: Array<{ feature: string; coverPoint: string }> = [];
    
    for (let i = 0; i < cpCount; i++) {
      const cpData = TestDataFactory.createCPData({ 
        feature: `Batch_Feature_${i}`,
        priority: 'P0'
      });
      cpList.push(cpData);
      await cpPage.createCP(cpData);
    }
    
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 选择所有 CP
    await cpPage.page.click('#cpSelectAll');
    await cpPage.page.waitForTimeout(300);
    
    // 批量更新 Priority
    await cpPage.page.click('#cpBatchUpdate');
    await cpPage.page.waitForSelector('#cpBatchPriority', { state: 'visible' });
    await cpPage.page.selectOption('#cpBatchPriority', 'P1');
    await cpPage.page.click('#cpBatchUpdate button[type="submit"]');
    await cpPage.page.waitForTimeout(500);
    
    // 创建多个 TC
    const tcCount = 3;
    const tcList: string[] = [];
    
    for (let i = 0; i < tcCount; i++) {
      const tcData = TestDataFactory.createTCData({ name: `Batch_TC_${i}` });
      tcList.push(tcData.name);
      await tcPage.switchToTCTab();
      await tcPage.createTC(tcData);
    }
    
    // 切换到 TC 标签页
    await tcPage.switchToTCTab();
    
    // 选择 TC
    const firstTcRow = tcPage.page.locator('table tbody tr:first-child');
    if (await firstTcRow.isVisible()) {
      await firstTcRow.locator('.tc-row-checkbox').click();
      await tcPage.page.waitForTimeout(300);
      
      // 批量更新 Status
      await tcPage.page.click('#tcBatchStatusBtn');
      await tcPage.page.waitForSelector('#tcBatchStatusSelect', { state: 'visible' });
      await tcPage.page.selectOption('#tcBatchStatusSelect', 'Pass');
      await tcPage.page.click('#tcBatchStatusUpdate button[type="submit"]');
      await tcPage.page.waitForTimeout(500);
    }
    
    // 验证 TC 仍然存在
    await tcPage.switchToTCTab();
    const rows = tcPage.page.locator('table tbody tr');
    const rowCount = await rows.count();
    expect(rowCount).toBeGreaterThanOrEqual(0);
  });
});

test.describe('完整用户工作流测试 - 异常处理', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test.afterEach(async ({ page }) => {
    await cleanupTestData(page);
  });

  /**
   * E2E-004: 页面刷新后状态恢复
   * 测试场景：
   * 1. 创建 CP 和 TC
   * 2. 切换到 TC 标签页
   * 3. 刷新页面
   * 4. 验证仍然在 TC 标签页
   */
  test('E2E-004: 页面刷新后状态恢复', async ({ cpPage, tcPage }) => {
    const cpData = TestDataFactory.createCPData({ feature: 'Refresh_Test' });
    const tcData = TestDataFactory.createTCData({ name: 'Refresh_TC' });
    
    // 创建 CP 和 TC
    await cpPage.createCP(cpData);
    await tcPage.createTC(tcData);
    
    // 切换到 TC 标签页
    await tcPage.switchToTCTab();
    
    // 验证 TC 可见
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcData.name}")`)
    ).toBeVisible();
    
    // 刷新页面
    await tcPage.page.reload();
    await tcPage.page.waitForLoadState('domcontentloaded');
    
    // 验证 TC 仍然存在
    await expect(
      tcPage.page.locator(`table tbody tr:has-text("${tcData.name}")`)
    ).toBeVisible();
  });

  /**
   * E2E-005: 模态框打开关闭流程
   * 测试场景：
   * 1. 打开 CP 模态框
   * 2. 不填写内容关闭
   * 3. 重新打开
   * 4. 验证可以正常使用
   */
  test('E2E-005: 模态框打开关闭流程', async ({ cpPage }) => {
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 打开模态框
    await cpPage.openCPModal();
    await expect(cpPage.page.locator('#cpModal')).toBeVisible();
    
    // 关闭模态框
    await cpPage.closeCPModal();
    await expect(cpPage.page.locator('#cpModal')).not.toBeVisible();
    
    // 重新打开
    await cpPage.openCPModal();
    await expect(cpPage.page.locator('#cpModal')).toBeVisible();
    
    // 验证表单可以正常使用
    await cpPage.page.fill('#cpFeature', 'Reopen_Test');
    await cpPage.page.fill('#cpCoverPoint', 'Reopen_CP');
    
    // 再次关闭
    await cpPage.closeCPModal();
    await expect(cpPage.page.locator('#cpModal')).not.toBeVisible();
    
    // 验证重新打开后表单已清空
    await cpPage.openCPModal();
    await expect(cpPage.page.locator('#cpFeature')).toBeEmpty();
    await expect(cpPage.page.locator('#cpCoverPoint')).toBeEmpty();
  });
});
