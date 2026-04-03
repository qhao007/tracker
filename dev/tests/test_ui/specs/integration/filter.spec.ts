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
   * 登录辅助函数 - v0.10.x 需要处理引导页和密码修改模态框
   */
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 处理引导页（v0.10.x 新增）
    const introBtn = page.locator('.intro-cta-btn');
    if (await introBtn.isVisible().catch(() => false)) {
      await introBtn.click();
      await page.waitForTimeout(500);
    }

    // 检查是否需要登录
    const needsLogin = await page.locator('#loginForm').isVisible().catch(() => false);
    if (needsLogin) {
      await page.fill('#loginUsername', 'admin');
      await page.fill('#loginPassword', 'admin123');
      await page.click('#loginForm button[type="submit"]');
      await page.waitForTimeout(1500);
    }

    // 处理首次登录密码修改模态框（v0.10.x 新增）
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

    await page.waitForSelector('#projectSelector:not([disabled])', { timeout: 10000 });
  }

  /**
   * 创建测试项目并返回项目ID
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
    // 获取所有项目选项，找到新创建的项目
    const options = await page.locator('#projectSelector option').count();
    let projectId = null;

    // 倒序查找新创建的项目（最新的在后面）
    for (let i = options - 1; i >= 0; i--) {
      const optionText = await page.locator('#projectSelector option').nth(i).textContent();
      if (optionText.includes(projectName)) {
        projectId = await page.locator('#projectSelector option').nth(i).getAttribute('value');
        break;
      }
    }

    if (projectId) {
      await page.selectOption('#projectSelector', projectId);
    } else {
      // 如果没找到，使用最后一个选项
      const lastOptionValue = await page.locator('#projectSelector option').nth(options - 1).getAttribute('value');
      await page.selectOption('#projectSelector', lastOptionValue);
      projectId = lastOptionValue;
    }
    await page.waitForTimeout(500);
    return { projectName, projectId };
  }

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    // 不需要创建新项目，使用已有的测试项目
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
    // 先创建测试项目
    await createTestProject(page);

    // 切换到 CP 标签页
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 验证"关联状态"过滤下拉框存在
    const linkedFilter = page.locator('#cpLinkedFilter');
    await expect(linkedFilter).toBeVisible({ timeout: 5000 });

    // 验证包含"未关联"选项（使用 count 验证选项存在，而非 toBeVisible）
    const unlinkedOption = linkedFilter.locator('option:has-text("未关联")');
    const unlinkedCount = await unlinkedOption.count();
    expect(unlinkedCount).toBeGreaterThan(0);

    // 验证"全部"选项也存在
    const allOption = linkedFilter.locator('option:has-text("全部")');
    const allCount = await allOption.count();
    expect(allCount).toBeGreaterThan(0);
  });

  /**
   * UI-FILTER-002: 过滤显示未关联CP
   * 测试目标: 选择"未关联"过滤后，只显示未关联的 CP
   *
   * 注意: TC-CP 关联功能无 UI 操作界面，使用 API 创建关联
   */
  test('UI-FILTER-002: 过滤显示未关联CP', async ({ page }) => {
    // 先创建测试项目并获取项目ID
    const { projectId, projectName } = await createTestProject(page);

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

    // 创建 TC
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

    // 获取 CP 和 TC 的 ID（通过 API）
    // 使用之前创建项目时捕获的 projectId
    console.log('Using project ID:', projectId);

    // 使用 API 获取 CP ID（添加 credentials）
    const cpListResponse = await page.evaluate(async (pId) => {
      const res = await fetch(`/api/cp?project_id=${pId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    console.log('CP list response:', Array.isArray(cpListResponse) ? `${cpListResponse.length} CPs` : cpListResponse);

    const unlinkedCP = Array.isArray(cpListResponse) ? cpListResponse.find((cp: any) => cp.cover_point === unlinkedCPName) : null;
    const linkedCP = Array.isArray(cpListResponse) ? cpListResponse.find((cp: any) => cp.cover_point === linkedCPName) : null;

    // 使用 API 获取 TC ID
    const tcListResponse = await page.evaluate(async (pId) => {
      const res = await fetch(`/api/tc?project_id=${pId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    console.log('TC list response:', Array.isArray(tcListResponse) ? `${tcListResponse.length} TCs` : tcListResponse);

    const tc = Array.isArray(tcListResponse) ? tcListResponse.find((t: any) => t.test_name === tcName) : null;

    if (!unlinkedCP || !linkedCP || !tc) {
      throw new Error(`数据创建失败: unlinkedCP=${!!unlinkedCP}, linkedCP=${!!linkedCP}, tc=${!!tc}`);
    }

    console.log('Found IDs - unlinkedCP:', unlinkedCP?.id, 'linkedCP:', linkedCP?.id, 'tc:', tc?.id);

    // 使用 API 关联 TC 和 CP（需要 credentials: include 携带认证信息）
    const apiResult = await page.evaluate(async ({ tcId, cpId, pId }) => {
      // 转换 project_id 为整数
      const projectIdInt = parseInt(pId, 10);
      const res = await fetch(`/api/tc/${tcId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          project_id: projectIdInt,
          connections: [cpId]
        })
      });
      const data = await res.json();
      return { ok: res.ok, status: res.status, data };
    }, { tcId: tc.id, cpId: linkedCP.id, pId: projectId });

    console.log('API Result:', JSON.stringify(apiResult));

    if (!apiResult.ok) {
      throw new Error(`API关联失败: ${JSON.stringify(apiResult)}`);
    }

    // 刷新页面验证关联
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
    await page.waitForTimeout(500);

    // 重新选择之前创建的项目
    await page.selectOption('#projectSelector', { label: projectName });
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

    // 验证关联: linkedCP 应该没有 unlinked 样式（表示已关联）
    const linkedRowUnlinkedClass = linkedRow.locator('.unlinked');
    await expect(linkedRowUnlinkedClass).not.toBeVisible({ timeout: 5000 });

    // 验证未关联: unlinkedCP 应该有 unlinked 样式（表示未关联）
    const unlinkedRowUnlinkedClass = unlinkedRow.locator('.unlinked');
    await expect(unlinkedRowUnlinkedClass).toBeVisible({ timeout: 5000 });

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
    // 先创建测试项目
    await createTestProject(page);

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
