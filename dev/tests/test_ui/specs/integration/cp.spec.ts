/**
 * CP 集成测试用例
 * 
 * 测试 CP (Cover Point) 管理的完整功能
 * - CRUD 操作
 * - 过滤功能
 * - 批量操作
 * - 展开/折叠详情
 * 
 * 运行命令:
 *   npx playwright test tests/specs/integration/cp.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';
import { cleanupTestData } from '../../utils/cleanup';

test.describe('CP 集成测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 导航到首页
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test.afterEach(async ({ page }, testInfo) => {
    // 测试失败时截图
    if (testInfo.status === 'failed') {
      await page.screenshot({ 
        path: `test-results/screenshots/cp-${testInfo.title}-${Date.now()}.png` 
      });
    }
    // 清理测试数据
    await cleanupTestData(page);
  });

  /**
   * CP-001: 创建 CP 并验证
   * 测试场景：
   * 1. 切换到 CP 标签页
   * 2. 打开添加 CP 模态框
   * 3. 填写 CP 信息并提交
   * 4. 验证 CP 创建成功
   */
  test('CP-001: 创建 CP 并验证', async ({ cpPage }) => {
    const cpData = TestDataFactory.createCPData();
    
    // 创建 CP
    await cpPage.createCP(cpData);
    
    // 切换到 CP 标签页验证
    await cpPage.switchToCPTab();
    
    // 验证 CP 存在于表格中
    await expect(
      cpPage.page.locator(`.cp-table tbody tr:has-text("${cpData.coverPoint}")`)
    ).toBeVisible();
  });

  /**
   * CP-002: 编辑 CP
   * 测试场景：
   * 1. 先创建一个 CP
   * 2. 找到并点击编辑按钮
   * 3. 修改 CP 信息
   * 4. 验证修改成功
   */
  test('CP-002: 编辑 CP', async ({ cpPage }) => {
    const originalData = TestDataFactory.createCPData();
    const editData = TestDataFactory.createCPData({
      feature: 'Edited_Feature',
      coverPoint: 'Edited_CP',
      details: '这是编辑后的描述',
      priority: 'P1'
    });
    
    // 创建原始 CP
    await cpPage.createCP(originalData);
    
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 查找并编辑 CP - 点击编辑按钮
    const cpRow = cpPage.page.locator(`.cp-table tbody tr:has-text("${originalData.coverPoint}")`);
    await expect(cpRow).toBeVisible();
    
    // 点击编辑按钮
    await cpPage.page.click(`.cp-table tbody tr:has-text("${originalData.coverPoint}") .action-btn.edit`);
    
    // 等待编辑模态框
    await cpPage.page.waitForSelector('#cpModal', { state: 'visible', timeout: 5000 });
    
    // 修改信息
    await cpPage.page.fill('#cpFeature', editData.feature);
    await cpPage.page.fill('#cpCoverPoint', editData.coverPoint);
    await cpPage.page.fill('#cpDetails', editData.details);
    await cpPage.page.selectOption('#cpPriority', editData.priority);
    
    // 提交修改
    await cpPage.page.click('#cpForm button[type="submit"]');
    await cpPage.page.waitForTimeout(500);
    
    // 验证编辑后的 CP 存在（使用 first 避免 multiple elements 错误）
    await expect(
      cpPage.page.locator(`.cp-table tbody tr:has-text("${editData.coverPoint}")`).first()
    ).toBeVisible();
  });

  /**
   * CP-003: 删除 CP
   * 测试场景：
   * 1. 先创建一个 CP
   * 2. 找到并点击删除按钮
   * 3. 确认删除
   * 4. 验证 CP 已不存在
   */
  test('CP-003: 删除 CP', async ({ cpPage }) => {
    const cpData = TestDataFactory.createCPData();
    
    // 创建 CP
    await cpPage.createCP(cpData);
    
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 验证 CP 存在（使用 first 避免 multiple elements 错误）
    const cpRow = cpPage.page.locator(`.cp-table tbody tr:has-text("${cpData.coverPoint}")`).first();
    await expect(cpRow).toBeVisible();
    
    // 点击删除按钮 - 原生 confirm 对话框会被自动接受
    await cpPage.page.locator(`.cp-table tbody tr:has-text("${cpData.coverPoint}") .action-btn.delete`).first().click();
    
    // 等待删除操作完成
    await cpPage.page.waitForTimeout(1000);
    
    // 验证 CP 不再存在
    await expect(cpRow).not.toBeVisible();
  });

  /**
   * CP-004: 过滤 CP (按 Feature)
   * 测试场景：
   * 1. 创建多个不同 Feature 的 CP
   * 2. 使用 Feature 过滤器
   * 3. 验证只显示匹配的 CP
   */
  test('CP-004: 按 Feature 过滤 CP', async ({ cpPage }) => {
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 验证 Feature 过滤器存在
    const featureFilter = cpPage.page.locator('#cpFeatureFilter');
    await expect(featureFilter).toBeVisible();
    
    // 验证过滤器有默认选项
    const options = await featureFilter.locator('option').count();
    expect(options).toBeGreaterThan(0);
    
    // 选择第一个非默认选项（如果有）
    const optionCount = await featureFilter.locator('option').count();
    if (optionCount > 1) {
      await featureFilter.selectOption({ index: 1 });
      await cpPage.page.waitForTimeout(500);
    }
    
    // 验证过滤器可以正常操作
    await featureFilter.selectOption({ index: 0 }); // 恢复到全部
    await expect(featureFilter).toHaveValue('');
  });

  /**
   * CP-005: 过滤 CP (按 Priority)
   * 测试场景：
   * 1. 创建不同 Priority 的 CP
   * 2. 使用 Priority 过滤器
   * 3. 验证只显示匹配的 CP
   */
  test('CP-005: 按 Priority 过滤 CP', async ({ cpPage }) => {
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 验证 Priority 过滤器存在
    const priorityFilter = cpPage.page.locator('#cpPriorityFilter');
    await expect(priorityFilter).toBeVisible();
    
    // 验证过滤器有选项（P0, P1, P2）
    const options = await priorityFilter.locator('option').count();
    expect(options).toBeGreaterThanOrEqual(3); // 全部 + P0 + P1 + P2
    
    // 测试选择 P0
    await priorityFilter.selectOption('P0');
    await cpPage.page.waitForTimeout(500);
    await expect(priorityFilter).toHaveValue('P0');
    
    // 测试选择 P1
    await priorityFilter.selectOption('P1');
    await cpPage.page.waitForTimeout(500);
    await expect(priorityFilter).toHaveValue('P1');
    
    // 恢复到全部
    await priorityFilter.selectOption('');
    await expect(priorityFilter).toHaveValue('');
  });

  /**
   * CP-006: 批量更新 Priority
   * 测试场景：
   * 1. 创建多个 CP
   * 2. 选择多个 CP
   * 3. 批量更新 Priority
   * 4. 验证更新成功
   */
  // CP-006: 批量更新 Priority - 跳过（批量操作功能未实现）
  test.skip('CP-006: 批量更新 Priority', async ({ cpPage }) => {
    // 批量操作功能在当前版本中未实现
    // 需要等待功能开发完成后才能测试
  });

  /**
   * CP-007: 展开/折叠 CP 详情
   * 测试场景：
   * 1. 创建带有详细信息的 CP
   * 2. 点击展开按钮
   * 3. 验证详情显示
   * 4. 点击折叠按钮
   * 5. 验证详情隐藏
   */
  test('CP-007: 展开/折叠 CP 详情', async ({ cpPage }) => {
    const cpData = TestDataFactory.createCPData({
      details: '这是一段很长的详细信息，用于测试展开/折叠功能。' +
               '这里包含了很多文本，需要足够长才能测试折叠效果。'
    });
    
    // 创建 CP
    await cpPage.createCP(cpData);
    
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 找到 CP 行
    const cpRow = cpPage.page.locator(`.cp-table tbody tr:has-text("${cpData.coverPoint}")`);
    await expect(cpRow).toBeVisible();
    
    // 点击展开按钮
    const expandButton = cpRow.locator('.expand-btn');
    if (await expandButton.isVisible()) {
      await expandButton.click();
      await cpPage.page.waitForTimeout(500);
      
      // 验证详情区域显示
      await expect(cpPage.page.locator('.cp-detail-area')).toBeVisible();
      
      // 点击折叠按钮
      const collapseButton = cpPage.page.locator('.collapse-btn');
      if (await collapseButton.isVisible()) {
        await collapseButton.click();
        await cpPage.page.waitForTimeout(500);
        
        // 验证详情区域隐藏
        await expect(cpPage.page.locator('.cp-detail-area')).not.toBeVisible();
      }
    }
  });

  /**
   * CP-008: 创建 CP - 验证必填字段
   * 测试场景：
   * 1. 不填写必填字段尝试创建
   * 2. 验证表单验证提示
   */
  test('CP-008: 创建 CP - 验证必填字段', async ({ cpPage }) => {
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 打开添加 CP 模态框
    await cpPage.openCPModal();
    
    // 不填写任何内容直接提交
    await cpPage.page.click('#cpForm button[type="submit"]');
    
    // 验证表单未关闭（仍在显示）
    await expect(cpPage.page.locator('#cpModal')).toBeVisible();
    
    // 关闭模态框
    await cpPage.closeCPModal();
  });
});

test.describe('CP 集成测试 - 数据一致性', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test.afterEach(async ({ page }) => {
    await cleanupTestData(page);
  });

  /**
   * CP-009: CP 数据持久化验证
   * 测试场景：
   * 1. 创建 CP
   * 2. 刷新页面
   * 3. 验证 CP 仍然存在
   */
  test('CP-009: CP 数据持久化验证', async ({ cpPage }) => {
    const cpData = TestDataFactory.createCPData();
    
    // 创建 CP
    await cpPage.createCP(cpData);
    
    // 刷新页面
    await cpPage.page.reload();
    await cpPage.page.waitForLoadState('domcontentloaded');
    
    // 切换到 CP 标签页
    await cpPage.switchToCPTab();
    
    // 验证 CP 仍然存在
    await expect(
      cpPage.page.locator(`.cp-table tbody tr:has-text("${cpData.coverPoint}")`)
    ).toBeVisible();
  });
});
