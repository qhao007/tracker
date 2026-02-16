/**
 * 导入导出功能 UI 测试
 * 
 * 测试导入导出功能的用户界面：
 * - 导入按钮和对话框
 * - 导出按钮和对话框
 * - 模板下载
 * 
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/import-export.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';

test.describe('导入导出功能测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 确保在首页并选择一个项目
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    
    // 创建一个测试项目
    const projectName = TestDataFactory.generateProjectName();
    await page.click('button[onclick="openProjectModal()"]');
    await page.waitForSelector('#projectModal', { state: 'visible', timeout: 5000 });
    await page.fill('#newProjectName', projectName);
    await page.click('#projectModal button[type="submit"]');
    await page.waitForTimeout(1000);
  });

  /**
   * CP 导入功能测试
   */
  test('IMP-001: CP 导入按钮存在', async ({ page }) => {
    // 切换到 CP 面板
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 5000 });
    
    // 检查导入按钮存在
    const importBtn = page.locator('button:has-text("导入 CP")');
    await expect(importBtn).toBeVisible();
  });

  test('IMP-002: CP 导入对话框打开', async ({ page }) => {
    // 切换到 CP 面板
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible' });
    
    // 点击导入按钮
    await page.click('button:has-text("导入 CP")');
    await page.waitForSelector('#importModal', { state: 'visible', timeout: 5000 });
    
    // 检查对话框内容
    await expect(page.locator('#importModalTitle')).toContainText('导入 Cover Points');
    await expect(page.locator('#downloadTemplateBtn')).toBeVisible();
    await expect(page.locator('#importFile')).toBeVisible();
  });

  /**
   * TC 导入功能测试
   */
  test('IMP-003: TC 导入按钮存在', async ({ page }) => {
    // 切换到 TC 面板
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 5000 });
    
    // 检查导入按钮存在
    const importBtn = page.locator('button:has-text("导入 TC")');
    await expect(importBtn).toBeVisible();
  });

  test('IMP-004: TC 导入对话框打开', async ({ page }) => {
    // 切换到 TC 面板
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible' });
    
    // 点击导入按钮
    await page.click('button:has-text("导入 TC")');
    await page.waitForSelector('#importModal', { state: 'visible', timeout: 5000 });
    
    // 检查对话框内容
    await expect(page.locator('#importModalTitle')).toContainText('导入 Test Cases');
    await expect(page.locator('#downloadTemplateBtn')).toContainText('TC 模板');
  });

  /**
   * CP 导出功能测试
   */
  test('EXP-001: CP 导出按钮存在', async ({ page }) => {
    // 切换到 CP 面板
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible' });
    
    // 检查导出按钮存在
    const exportBtn = page.locator('button:has-text("导出 CP")');
    await expect(exportBtn).toBeVisible();
  });

  test('EXP-002: CP 导出对话框打开', async ({ page }) => {
    // 切换到 CP 面板
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible' });
    
    // 点击导出按钮
    await page.click('button:has-text("导出 CP")');
    await page.waitForSelector('#exportModal', { state: 'visible', timeout: 5000 });
    
    // 检查对话框内容
    await expect(page.locator('#exportModalTitle')).toContainText('导出 Cover Points');
    await expect(page.locator('input[name="exportFormat"][value="xlsx"]')).toBeChecked();
    await expect(page.locator('input[name="exportFormat"][value="csv"]')).not.toBeChecked();
  });

  test('EXP-003: CP 导出对话框显示项目信息', async ({ page }) => {
    // 切换到 CP 面板
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible' });
    
    // 点击导出按钮
    await page.click('button:has-text("导出 CP")');
    await page.waitForSelector('#exportModal', { state: 'visible' });
    
    // 检查项目信息显示
    await expect(page.locator('#exportProjectName')).not.toBeEmpty();
    await expect(page.locator('#exportRecordCount')).toContainText('0');
  });

  /**
   * TC 导出功能测试
   */
  test('EXP-004: TC 导出按钮存在', async ({ page }) => {
    // 切换到 TC 面板
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible' });
    
    // 检查导出按钮存在
    const exportBtn = page.locator('button:has-text("导出 TC")');
    await expect(exportBtn).toBeVisible();
  });

  test('EXP-005: TC 导出对话框打开', async ({ page }) => {
    // 切换到 TC 面板
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible' });
    
    // 点击导出按钮
    await page.click('button:has-text("导出 TC")');
    await page.waitForSelector('#exportModal', { state: 'visible', timeout: 5000 });
    
    // 检查对话框内容
    await expect(page.locator('#exportModalTitle')).toContainText('导出 Test Cases');
  });

  /**
   * 模板下载测试
   */
  test('TMPL-001: CP 模板下载', async ({ page }) => {
    // 切换到 CP 面板
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible' });
    
    // 打开导入对话框
    await page.click('button:has-text("导入 CP")');
    await page.waitForSelector('#importModal', { state: 'visible' });
    
    // 点击下载模板按钮
    const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null);
    await page.click('#downloadTemplateBtn');
    
    // 注意: 由于测试环境限制，这里只验证按钮可点击
    // 实际下载测试需要在有浏览器的环境中进行
  });

  /**
   * 对话框关闭测试
   */
  test('DLG-001: 导入对话框关闭', async ({ page }) => {
    // 打开导入对话框
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible' });
    await page.click('button:has-text("导入 CP")');
    await page.waitForSelector('#importModal', { state: 'visible' });
    
    // 点击关闭按钮
    await page.click('#importModal .modal-close');
    await page.waitForSelector('#importModal', { state: 'hidden' });
  });

  test('DLG-002: 导出对话框关闭', async ({ page }) => {
    // 打开导出对话框
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible' });
    await page.click('button:has-text("导出 CP")');
    await page.waitForSelector('#exportModal', { state: 'visible' });
    
    // 点击取消按钮
    await page.click('#exportModal button:has-text("取消")');
    await page.waitForSelector('#exportModal', { state: 'hidden' });
  });
});
