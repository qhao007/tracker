/**
 * 过滤功能测试用例
 *
 * 测试 CP 的"未关联"过滤功能
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/filter.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';
import { cleanupTestData } from '../../utils/cleanup';

const BASE_URL = 'http://localhost:8081';

test.describe('过滤功能测试', () => {

  /**
   * 登录辅助函数
   */
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 检查是否需要登录
    const needsLogin = await page.locator('#loginForm').isVisible().catch(() => false);
    if (needsLogin) {
      await page.fill('#loginUsername', 'admin');
      await page.fill('#loginPassword', 'admin123');
      await page.click('#loginForm button[type="submit"]');
      await page.waitForTimeout(1500);
    }

    // 检查是否需要强制修改密码
    const passwordModal = page.locator('#changePasswordModal');
    const isPasswordModalVisible = await passwordModal.isVisible().catch(() => false);

    if (isPasswordModalVisible) {
      // 需要修改密码，填写新密码
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button:has-text("确认修改")');
      await page.waitForTimeout(2000);
    }

    await page.waitForSelector('#projectSelector:not([disabled])', { timeout: 10000 });
  }

  /**
   * 创建测试项目
   */
  async function createTestProject(page: any) {
    const projectName = `TestUI_Filter_${Date.now()}`;
    await page.click('button.header-btn:has-text("📁 项目")');
    await page.waitForSelector('#projectModal', { state: 'visible', timeout: 10000 });
    await page.fill('#newProjectName', projectName);

    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    const startDate = today.toISOString().split('T')[0];
    const endDate = nextMonth.toISOString().split('T')[0];
    await page.fill('#newProjectStartDate', startDate);
    await page.fill('#newProjectEndDate', endDate);
    await page.click('#projectModal button:has-text("创建")');
    await page.waitForSelector('#projectModal', { state: 'hidden', timeout: 10000 });
    await page.waitForTimeout(1000);

    await page.waitForSelector('#projectSelector option', { state: 'attached', timeout: 10000 });
    const options = await page.locator('#projectSelector option').count();
    if (options > 0) {
      const lastOptionValue = await page.locator('#projectSelector option').nth(options - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionValue);
    }
    await page.waitForTimeout(500);
    return projectName;
  }

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await createTestProject(page);
  });

  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status === 'failed') {
      await page.screenshot({
        path: `test-results/screenshots/filter-${testInfo.title}-${Date.now()}.png`
      });
    }
    await cleanupTestData(page);
  });

  /**
   * UI-FILTER-001: CP过滤"未关联"选项
   * 测试目标: 验证 CP 过滤下拉框包含"未关联"选项
   */
  test('UI-FILTER-001: CP过滤"未关联"选项', async ({ page }) => {
    // 切换到 CP 标签页
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 验证"关联状态"过滤下拉框存在
    const linkedFilter = page.locator('#cpLinkedFilter');
    await expect(linkedFilter).toBeVisible({ timeout: 5000 });

    // 验证包含"未关联"选项
    const unlinkedOption = linkedFilter.locator('option:has-text("未关联")');
    await expect(unlinkedOption).toBeVisible({ timeout: 5000 });

    // 验证"全部"选项也存在
    const allOption = linkedFilter.locator('option:has-text("全部")');
    await expect(allOption).toBeVisible({ timeout: 5000 });
  });

  /**
   * UI-FILTER-002: 过滤显示未关联CP
   * 测试目标: 选择"未关联"过滤后，只显示未关联的 CP
   */
  test('UI-FILTER-002: 过滤显示未关联CP', async ({ page }) => {
    const unlinkedCPName = TestDataFactory.generateCPName('Unlinked');
    const linkedCPName = TestDataFactory.generateCPName('Linked');
    const tcName = TestDataFactory.generateTCName('ForFilter');

    // 创建第一个 CP（未关联）
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Filter');
    await page.fill('#cpCoverPoint', unlinkedCPName);
    await page.fill('#cpDetails', '未关联CP');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 创建第二个 CP（稍后关联）
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Filter');
    await page.fill('#cpCoverPoint', linkedCPName);
    await page.fill('#cpDetails', '待关联CP');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 创建 TC 用于关联
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 TC');
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: 10000 });
    await page.fill('#tcTestbench', 'tb_filter');
    await page.fill('#tcTestName', tcName);
    await page.fill('#tcScenario', '用于过滤测试');
    await page.click('#tcModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 刷新页面
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    const options = await page.locator('#projectSelector option').count();
    if (options > 0) {
      const lastOptionValue = await page.locator('#projectSelector option').nth(options - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionValue);
    }
    await page.waitForTimeout(500);

    // 关联 TC 和 CP
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    const tcRow = page.locator(`#tcList tr:has-text("${tcName}")`).first();
    await expect(tcRow).toBeVisible({ timeout: 10000 });

    const linkBtn = tcRow.locator('button:has-text("关联")');
    if (await linkBtn.count() > 0) {
      await linkBtn.click();
      await page.waitForTimeout(1000);

      const cpCheckbox = page.locator(`.cp-select-list input[type="checkbox"]:has-text("${linkedCPName}")`);
      if (await cpCheckbox.count() > 0) {
        await cpCheckbox.check();
        await page.waitForTimeout(500);

        const confirmBtn = page.locator('button:has-text("确认关联")');
        if (await confirmBtn.count() > 0) {
          await confirmBtn.click();
          await page.waitForTimeout(2000);
        }
      }
    }

    // 刷新页面
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    const opts = await page.locator('#projectSelector option').count();
    if (opts > 0) {
      const lastOptionVal = await page.locator('#projectSelector option').nth(opts - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionVal);
    }
    await page.waitForTimeout(500);

    // 切换到 CP 面板，验证未过滤状态下显示两个 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    // 验证两个 CP 都可见
    const unlinkedRow = page.locator(`#cpList tr:has-text("${unlinkedCPName}")`).first();
    const linkedRow = page.locator(`#cpList tr:has-text("${linkedCPName}")`).first();
    await expect(unlinkedRow).toBeVisible({ timeout: 5000 });
    await expect(linkedRow).toBeVisible({ timeout: 5000 });

    // 选择"未关联"过滤
    await page.selectOption('#cpLinkedFilter', 'unlinked');
    await page.waitForTimeout(1000);

    // 验证只显示未关联的 CP
    await expect(unlinkedRow).toBeVisible({ timeout: 5000 });

    // 关联的 CP 不应该显示（或者检查它是否被过滤掉了）
    const linkedRowAfterFilter = page.locator(`#cpList tr:has-text("${linkedCPName}")`);
    const linkedCount = await linkedRowAfterFilter.count();
    // 过滤后关联的CP应该不可见
    if (linkedCount > 0) {
      await expect(linkedRowAfterFilter.first()).not.toBeVisible();
    }
  });

  /**
   * UI-FILTER-003: 清除过滤恢复正常
   * 测试目标: 清除"未关联"过滤后，恢复显示所有 CP
   */
  test('UI-FILTER-003: 清除过滤恢复正常', async ({ page }) => {
    const cpName1 = TestDataFactory.generateCPName('Filter1');
    const cpName2 = TestDataFactory.generateCPName('Filter2');

    // 创建两个 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });

    // 创建第一个 CP
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Clear');
    await page.fill('#cpCoverPoint', cpName1);
    await page.fill('#cpDetails', '测试清除过滤1');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 创建第二个 CP
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Clear');
    await page.fill('#cpCoverPoint', cpName2);
    await page.fill('#cpDetails', '测试清除过滤2');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 刷新页面
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    const options = await page.locator('#projectSelector option').count();
    if (options > 0) {
      const lastOptionValue = await page.locator('#projectSelector option').nth(options - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionValue);
    }
    await page.waitForTimeout(500);

    // 切换到 CP 面板
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    // 选择"未关联"过滤
    await page.selectOption('#cpLinkedFilter', 'unlinked');
    await page.waitForTimeout(1000);

    // 清除过滤（选择"全部"）
    await page.selectOption('#cpLinkedFilter', '');
    await page.waitForTimeout(1000);

    // 验证两个 CP 都可见
    const cpRow1 = page.locator(`#cpList tr:has-text("${cpName1}")`).first();
    const cpRow2 = page.locator(`#cpList tr:has-text("${cpName2}")`).first();
    await expect(cpRow1).toBeVisible({ timeout: 5000 });
    await expect(cpRow2).toBeVisible({ timeout: 5000 });

    // 验证过滤下拉框值恢复为空
    const linkedFilter = page.locator('#cpLinkedFilter');
    await expect(linkedFilter).toHaveValue('');
  });
});
