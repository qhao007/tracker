/**
 * 关联状态可视化测试用例
 *
 * 测试 CP 和 TC 的关联状态显示功能
 * - 未关联显示红色+🔗图标
 * - 关联后正常显示
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/link-status.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';
import { cleanupTestData } from '../../utils/cleanup';

const BASE_URL = 'http://localhost:8081';

test.describe('关联状态可视化测试', () => {

  /**
   * 登录辅助函数
   */
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 首先检查是否有密码修改弹窗（可能是之前的会话残留）
    const passwordModal = page.locator('#changePasswordModal');
    let isPasswordModalVisible = await passwordModal.isVisible().catch(() => false);

    if (isPasswordModalVisible) {
      // 关闭密码弹窗，然后重新登录
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForLoadState('domcontentloaded');
    }

    // 检查是否需要登录
    const needsLogin = await page.locator('#loginForm').isVisible().catch(() => false);
    if (needsLogin) {
      await page.fill('#loginUsername', 'admin');
      await page.fill('#loginPassword', 'admin123');
      await page.click('#loginForm button[type="submit"]');
      await page.waitForTimeout(2000);
    }

    // 再次检查是否需要强制修改密码
    isPasswordModalVisible = await passwordModal.isVisible().catch(() => false);

    if (isPasswordModalVisible) {
      // 需要修改密码，填写新密码
      await page.fill('#newPassword', 'admin456');
      await page.fill('#confirmPassword', 'admin456');
      await page.click('#changePasswordModal button:has-text("确认修改")');
      await page.waitForTimeout(2000);

      // 等待密码弹窗关闭
      await passwordModal.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
    }

    await page.waitForSelector('#projectSelector:not([disabled])', { timeout: 30000 });
  }

  /**
   * 创建测试项目
   */
  async function createTestProject(page: any) {
    const projectName = `TestUI_Link_${Date.now()}`;
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
    // 增加超时处理
    page.setDefaultTimeout(180000);
    await loginAsAdmin(page);
    await page.waitForSelector('#projectSelector', { timeout: 30000 });

    // 使用已有的 SOC_DV 项目，避免创建新项目的延迟
    await page.selectOption('#projectSelector', { label: 'SOC_DV' });
    await page.waitForTimeout(1000);
  });

  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status === 'failed') {
      await page.screenshot({
        path: `test-results/screenshots/link-status-${testInfo.title}-${Date.now()}.png`
      });
    }
    await cleanupTestData(page);
  });

  /**
   * UI-LINK-001: 未关联CP显示红色+图标
   * 测试目标: 未关联的 CP 应该显示红色和🔗图标
   */
  test('UI-LINK-001: 未关联CP显示红色+图标', async ({ page }) => {
    const cpName = TestDataFactory.generateCPName('Unlinked');

    // 创建未关联的 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Link');
    await page.fill('#cpCoverPoint', cpName);
    await page.fill('#cpDetails', '测试未关联CP');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 刷新页面
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    // 重新选择项目
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

    // 验证 CP 存在并包含 unlinked 样式（红色+🔗图标）
    const cpRow = page.locator(`#cpList tr:has-text("${cpName}")`).first();
    await expect(cpRow).toBeVisible({ timeout: 10000 });

    // 验证 unlinked 样式存在
    const unlinkedElement = cpRow.locator('.unlinked');
    await expect(unlinkedElement).toBeVisible({ timeout: 5000 });
  });

  /**
   * UI-LINK-002: 未关联TC显示红色+图标
   * 测试目标: 未关联的 TC 应该显示红色和🔗图标
   */
  test('UI-LINK-002: 未关联TC显示红色+图标', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName('Unlinked');

    // 创建未关联的 TC
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 TC');
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: 10000 });
    await page.fill('#tcTestbench', 'tb_unlinked');
    await page.fill('#tcTestName', tcName);
    await page.fill('#tcScenario', '测试未关联TC');
    await page.click('#tcModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 刷新页面
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    // 重新选择项目
    const options = await page.locator('#projectSelector option').count();
    if (options > 0) {
      const lastOptionValue = await page.locator('#projectSelector option').nth(options - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionValue);
    }
    await page.waitForTimeout(500);

    // 切换到 TC 面板
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    // 验证 TC 存在并包含 unlinked 样式（红色+🔗图标）
    const tcRow = page.locator(`#tcList tr:has-text("${tcName}")`).first();
    await expect(tcRow).toBeVisible({ timeout: 10000 });

    // 验证 unlinked 样式存在
    const unlinkedElement = tcRow.locator('.unlinked');
    await expect(unlinkedElement).toBeVisible({ timeout: 5000 });
  });

  /**
   * UI-LINK-003: 关联CP正常显示
   * 测试目标: 关联后的 CP 不应该显示红色和🔗图标
   */
  test('UI-LINK-003: 关联CP正常显示', async ({ page }) => {
    const cpName = TestDataFactory.generateCPName('Linked');
    const tcName = TestDataFactory.generateTCName('ForLink');

    // 创建 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Link');
    await page.fill('#cpCoverPoint', cpName);
    await page.fill('#cpDetails', '测试关联CP');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 创建 TC
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 TC');
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: 10000 });
    await page.fill('#tcTestbench', 'tb_link');
    await page.fill('#tcTestName', tcName);
    await page.fill('#tcScenario', '用于关联测试');
    await page.click('#tcModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 获取 CP 和 TC 的 ID
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    const options = await page.locator('#projectSelector option').count();
    if (options > 0) {
      const lastOptionValue = await page.locator('#projectSelector option').nth(options - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionValue);
    }
    await page.waitForTimeout(500);

    // 切换到 TC 面板，找到 TC 并关联 CP
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    const tcRow = page.locator(`#tcList tr:has-text("${tcName}")`).first();
    await expect(tcRow).toBeVisible({ timeout: 10000 });

    // 点击 TC 的关联按钮
    const linkBtn = tcRow.locator('button:has-text("关联")');
    if (await linkBtn.count() > 0) {
      await linkBtn.click();
      await page.waitForTimeout(1000);

      // 在关联弹窗中选择 CP
      const cpCheckbox = page.locator(`.cp-select-list input[type="checkbox"]:has-text("${cpName}")`);
      if (await cpCheckbox.count() > 0) {
        await cpCheckbox.check();
        await page.waitForTimeout(500);

        // 点击确认关联按钮
        const confirmBtn = page.locator('button:has-text("确认关联")');
        if (await confirmBtn.count() > 0) {
          await confirmBtn.click();
          await page.waitForTimeout(2000);
        }
      }
    }

    // 刷新页面验证
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    const opts = await page.locator('#projectSelector option').count();
    if (opts > 0) {
      const lastOptionVal = await page.locator('#projectSelector option').nth(opts - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionVal);
    }
    await page.waitForTimeout(500);

    // 切换到 CP 面板，验证 CP 不再有 unlinked 样式
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    const cpRow = page.locator(`#cpList tr:has-text("${cpName}")`).first();
    await expect(cpRow).toBeVisible({ timeout: 10000 });

    // 验证没有 unlinked 样式（不应该有红色+图标）
    const unlinkedElement = cpRow.locator('.unlinked');
    const unlinkedCount = await unlinkedElement.count();

    // 关联后应该没有 unlinked 样式，或者整个行没有这个类
    expect(unlinkedCount).toBe(0);
  });

  /**
   * UI-LINK-004: 关联TC正常显示
   * 测试目标: 关联后的 TC 不应该显示红色和🔗图标
   */
  test('UI-LINK-004: 关联TC正常显示', async ({ page }) => {
    const cpName = TestDataFactory.generateCPName('ForTC');
    const tcName = TestDataFactory.generateTCName('Linked');

    // 创建 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 CP');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: 10000 });
    await page.fill('#cpFeature', 'Feature_Link');
    await page.fill('#cpCoverPoint', cpName);
    await page.fill('#cpDetails', '用于关联TC');
    await page.click('#cpModal button[type="submit"]');
    await page.waitForTimeout(2000);

    // 创建 TC
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.click('text=+ 添加 TC');
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: 10000 });
    await page.fill('#tcTestbench', 'tb_linked');
    await page.fill('#tcTestName', tcName);
    await page.fill('#tcScenario', '测试关联TC');
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

    // 切换到 TC 面板，找到 TC 并关联 CP
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    const tcRow = page.locator(`#tcList tr:has-text("${tcName}")`).first();
    await expect(tcRow).toBeVisible({ timeout: 10000 });

    // 点击 TC 的关联按钮
    const linkBtn = tcRow.locator('button:has-text("关联")');
    if (await linkBtn.count() > 0) {
      await linkBtn.click();
      await page.waitForTimeout(1000);

      // 在关联弹窗中选择 CP
      const cpCheckbox = page.locator(`.cp-select-list input[type="checkbox"]:has-text("${cpName}")`);
      if (await cpCheckbox.count() > 0) {
        await cpCheckbox.check();
        await page.waitForTimeout(500);

        // 点击确认关联按钮
        const confirmBtn = page.locator('button:has-text("确认关联")');
        if (await confirmBtn.count() > 0) {
          await confirmBtn.click();
          await page.waitForTimeout(2000);
        }
      }
    }

    // 刷新页面验证
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    const opts = await page.locator('#projectSelector option').count();
    if (opts > 0) {
      const lastOptionVal = await page.locator('#projectSelector option').nth(opts - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionVal);
    }
    await page.waitForTimeout(500);

    // 切换到 TC 面板，验证 TC 不再有 unlinked 样式
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    const linkedTCRow = page.locator(`#tcList tr:has-text("${tcName}")`).first();
    await expect(linkedTCRow).toBeVisible({ timeout: 10000 });

    // 验证没有 unlinked 样式（不应该有红色+图标）
    const unlinkedElement = linkedTCRow.locator('.unlinked');
    const unlinkedCount = await unlinkedElement.count();

    // 关联后应该没有 unlinked 样式
    expect(unlinkedCount).toBe(0);
  });
});
