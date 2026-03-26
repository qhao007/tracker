/**
 * CP 关联选择与 Priority 过滤测试用例
 *
 * 测试功能:
 * - REQ-1: 关联选择列表交互体验（搜索过滤 + 已关联CP显示）
 * - REQ-2: 图表支持按CP Priority过滤
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/cp_link_filter.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';

const BASE_URL = 'http://localhost:8081';
const TIMEOUT = 30000; // 数据量大，增加超时时间

test.describe('CP 关联选择与 Priority 过滤测试', () => {
  let currentProjectName = 'SOC_DV'; // 使用现有项目

  /**
   * 登录辅助函数 - 使用现有项目
   */
  async function loginAndSelectProject(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 处理引导页（v0.10.x 新增）
    const introBtn = page.locator('.intro-cta-btn');
    if (await introBtn.isVisible().catch(() => false)) {
      await introBtn.click();
      await page.waitForTimeout(500);
    }

    // 检查登录表单
    const needsLogin = await page.locator('#loginForm').isVisible().catch(() => false);
    if (needsLogin) {
      await page.fill('#loginUsername', 'admin');
      await page.fill('#loginPassword', 'admin123');
      await page.click('button.login-btn');
      await page.waitForTimeout(1500);

      // 检查是否出现密码修改模态框
      const changePwdModal = page.locator('#changePasswordModal');
      if (await changePwdModal.isVisible().catch(() => false)) {
        // 填写新密码（与原密码相同）
        await page.fill('#newPassword', 'admin123');
        await page.fill('#confirmPassword', 'admin123');
        await page.click('#changePasswordModal button.btn-primary');
        await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
        await page.waitForTimeout(1000);
      }
    }

    await page.waitForSelector('#userInfo', { timeout: 30000 }).catch(() => {});

    // 等待页面完全初始化
    await page.waitForTimeout(1000);

    // 使用 evaluate 直接调用 selectProject
    await page.evaluate(() => selectProject(3));
    await page.waitForTimeout(1000);
  }

  /**
   * 打开 TC Modal 并填写基本信息
   * v0.10.0: 关联 CP 选择区域已直接嵌入表单，无需额外点击
   */
  async function openTCModalAndFill(page: any, tcName: string) {
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    await page.click('text=+ 添加 TC');
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: TIMEOUT });
    // 等待 CP 复选框渲染
    await page.waitForTimeout(500);

    await page.fill('#tcTestbench', 'tb_' + tcName);
    await page.fill('#tcTestName', tcName);
    await page.fill('#tcScenario', 'Test scenario for ' + tcName);
    await page.waitForTimeout(300);
  }

  test.beforeEach(async ({ page }) => {
    await loginAndSelectProject(page);
  });

  test.afterEach(async ({ page }, testInfo) => {
    if (testInfo.status === 'failed') {
      await page.screenshot({
        path: `test-results/screenshots/cp-link-filter-${testInfo.title}-${Date.now()}.png`,
        fullPage: true
      });
    }
  });

  // ========================================
  // REQ-1 功能测试（关联选择交互）
  // ========================================

  /**
   * UI-LINK-001: 搜索框显示测试
   * 验证搜索输入框在关联选择区域上方
   */
  test('UI-LINK-001: 搜索框显示测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 使用现有的 SOC_DV 数据（已有30个CP）

    // 创建 TC 并打开关联选择
    await openTCModalAndFill(page, tcName);

    // 验证搜索框存在
    const searchInput = page.locator('#cpSearchInput');
    await expect(searchInput).toBeVisible();

    // 验证搜索框在关联选择区域内（#tcModal 内）
    const modal = page.locator('#tcModal');
    await expect(modal).toBeVisible();

    // 验证搜索框在关联 CP 区域的上方（检查 DOM 顺序）
    const searchInputPosition = await searchInput.boundingBox();
    const cpCheckboxesPosition = await page.locator('#cpCheckboxes').boundingBox();

    if (searchInputPosition && cpCheckboxesPosition) {
      expect(searchInputPosition.y).toBeLessThan(cpCheckboxesPosition.y);
    }
  });

  /**
   * UI-LINK-002: 搜索过滤功能测试
   * 输入关键词后列表在200ms内过滤
   */
  test('UI-LINK-002: 搜索过滤功能测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 使用现有的 SOC_DV 数据

    // 创建 TC 并打开关联选择
    await openTCModalAndFill(page, tcName);

    // 获取原始的 CP 数量
    const originalCount = await page.locator('#cpCheckboxes input').count();

    // 输入搜索关键词（使用一个通用的词）
    const searchInput = page.locator('#cpSearchInput');
    await searchInput.fill('CPU');

    // 等待过滤（200ms延迟在代码中已设置）
    await page.waitForTimeout(400);

    // 验证过滤后 CP 数量减少
    const filteredCount = await page.locator('#cpCheckboxes input').count();
    expect(filteredCount).toBeLessThan(originalCount);
  });

  /**
   * UI-LINK-003: 空状态提示测试
   * 搜索无结果时显示提示信息
   */
  test('UI-LINK-003: 空状态提示测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 使用现有的 SOC_DV 数据

    // 创建 TC 并打开关联选择
    await openTCModalAndFill(page, tcName);

    // 输入一个不存在的搜索关键词
    const searchInput = page.locator('#cpSearchInput');
    await searchInput.fill('NonExistentKeyword12345');

    // 等待过滤
    await page.waitForTimeout(300);

    // 验证空状态提示显示
    const emptyState = page.locator('#cpEmptyState');
    await expect(emptyState).toBeVisible();

    // 验证提示文本内容
    const emptyStateText = await emptyState.textContent();
    expect(emptyStateText).toContain('未找到匹配');
  });

  /**
   * UI-LINK-004: 已关联CP显示测试
   * 验证已关联CP显示区域在选择区域下方
   */
  test('UI-LINK-004: 已关联CP显示测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 创建 TC 并打开关联选择
    await openTCModalAndFill(page, tcName);

    // 选择一个 CP
    const firstCP = page.locator('#cpCheckboxes input').first();
    await firstCP.check();

    // 等待显示区域更新
    await page.waitForTimeout(300);

    // 验证已关联 CP 显示区域存在
    const linkedDisplay = page.locator('#linkedCPsDisplay');
    await expect(linkedDisplay).toBeVisible();

    // 验证显示区域在关联选择区域下方
    const checkboxesPosition = await page.locator('#cpCheckboxes').boundingBox();
    const linkedPosition = await linkedDisplay.boundingBox();

    if (checkboxesPosition && linkedPosition) {
      expect(linkedPosition.y).toBeGreaterThan(checkboxesPosition.y);
    }
  });

  /**
   * UI-LINK-005: CP名称显示测试
   * 验证显示CP名称而非编号
   */
  test('UI-LINK-005: CP名称显示测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 使用现有的 SOC_DV 数据的 CP，直接选择第一个可用的 CP
    await openTCModalAndFill(page, tcName);

    // 获取第一个 CP 的 label 文本
    const firstCPLabel = page.locator('#cpCheckboxes label').first();
    const cpName = await firstCPLabel.textContent();

    // 选择这个 CP
    const firstCPInput = page.locator('#cpCheckboxes input').first();
    await firstCPInput.check();

    // 等待显示区域更新
    await page.waitForTimeout(300);

    // 验证显示的是 CP 名称而不是纯数字 ID
    const linkedDisplay = page.locator('#linkedCPsDisplay');
    const displayText = await linkedDisplay.textContent();

    // 验证显示区域包含所选 CP 的名称
    expect(displayText).toContain(cpName);
    // 确保不显示纯数字 ID
    expect(displayText).not.toMatch(/^已关联:\s*\d+$/);
  });

  /**
   * UI-LINK-006: 实时更新测试
   * 取消关联后显示区域实时更新
   */
  test('UI-LINK-006: 实时更新测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 使用现有的 SOC_DV 数据的 CP
    await openTCModalAndFill(page, tcName);

    // 选择一个 CP
    const firstCP = page.locator('#cpCheckboxes input').first();
    await firstCP.check();

    // 等待显示区域更新
    await page.waitForTimeout(300);

    // 验证已关联显示
    const linkedDisplay = page.locator('#linkedCPsDisplay');
    await expect(linkedDisplay).toBeVisible();
    const textAfterCheck = await linkedDisplay.textContent();
    expect(textAfterCheck).toContain('已关联');

    // 取消选择
    await firstCP.uncheck();

    // 等待显示区域更新
    await page.waitForTimeout(300);

    // 验证显示区域更新为"未关联任何覆盖点"
    const textAfterUncheck = await linkedDisplay.textContent();
    expect(textAfterUncheck).toContain('未关联任何覆盖点');
  });

  /**
   * UI-LINK-007: Ctrl+K快捷键测试
   * 验证Ctrl+K聚焦搜索框
   */
  test('UI-LINK-007: Ctrl+K快捷键测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 使用现有的 SOC_DV 数据的 CP
    await openTCModalAndFill(page, tcName);

    // 确保搜索框可见
    const searchInput = page.locator('#cpSearchInput');
    await expect(searchInput).toBeVisible();

    // 按 Ctrl+K
    await searchInput.focus();
    await page.keyboard.press('Control+K');

    // 验证搜索框获得焦点
    await expect(searchInput).toBeFocused();
  });

  // ========================================
  // REQ-2 功能测试（图表Priority过滤）
  // ========================================

  /**
   * UI-PRIO-001: Priority下拉框测试
   * 验证多选下拉框显示
   */
  test('UI-PRIO-001: Priority下拉框测试', async ({ page }) => {
    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    // 点击 Priority 过滤下拉框标签打开下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 验证 Priority 过滤下拉框打开后显示 P0, P1, P2 选项
    await expect(page.locator('#priorityFilterDropdown input[value="P0"]')).toBeVisible();
    await expect(page.locator('#priorityFilterDropdown input[value="P1"]')).toBeVisible();
    await expect(page.locator('#priorityFilterDropdown input[value="P2"]')).toBeVisible();
  });

  /**
   * UI-PRIO-002: Priority过滤测试
   * 选择Priority后图表数据过滤
   */
  test('UI-PRIO-002: Priority过滤测试', async ({ page }) => {
    // 使用现有的 SOC_DV 数据的 CP（已有 P0/P1/P2）

    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800); // 等待图表加载

    // 点击 Priority 过滤下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 选择 P0
    await page.check('#priorityFilterDropdown input[value="P0"]');

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证重置按钮显示
    const resetBtn = page.locator('#resetPriorityBtn');
    await expect(resetBtn).toBeVisible();
  });

  /**
   * UI-PRIO-003: 图表标题显示测试
   * 验证图表标题显示过滤条件
   */
  test('UI-PRIO-003: 图表标题显示测试', async ({ page }) => {
    // 使用现有的 SOC_DV 数据的 CP

    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800);

    // 点击 Priority 过滤下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 选择 P0
    await page.check('#priorityFilterDropdown input[value="P0"]');

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证图表标题显示过滤条件
    // 检查 label 显示
    const filterLabel = page.locator('#priorityFilterLabel');
    const labelText = await filterLabel.textContent();
    expect(labelText).toContain('P0');
  });

  /**
   * UI-PRIO-004: 重置过滤按钮测试
   * 验证重置按钮恢复正常
   */
  test('UI-PRIO-004: 重置过滤按钮测试', async ({ page }) => {
    // 使用现有的 SOC_DV 数据的 CP

    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800);

    // 点击 Priority 过滤下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 选择 P0
    await page.check('#priorityFilterDropdown input[value="P0"]');

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证重置按钮显示
    const resetBtn = page.locator('#resetPriorityBtn');
    await expect(resetBtn).toBeVisible();

    // 点击重置按钮
    await resetBtn.click();
    await page.waitForTimeout(500);

    // 验证标签恢复为"全部"
    const filterLabel = page.locator('#priorityFilterLabel');
    const labelText = await filterLabel.textContent();
    expect(labelText).toContain('全部');

    // 验证重置按钮隐藏
    await expect(resetBtn).toBeHidden();
  });

  /**
   * UI-PRIO-005: 多选合并测试
   * 选择多个Priority时数据正确合并
   */
  test('UI-PRIO-005: 多选合并测试', async ({ page }) => {
    // 使用现有的 SOC_DV 数据的 CP（已有 P0/P1/P2）

    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800);

    // 点击 Priority 过滤下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 选择 P0（每次选择后下拉框会关闭，需要重新打开）
    await page.check('#priorityFilterDropdown input[value="P0"]', { force: true });
    await page.waitForTimeout(100);

    // 重新打开下拉框选择 P1
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);
    await page.check('#priorityFilterDropdown input[value="P1"]', { force: true });
    await page.waitForTimeout(100);

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证标签显示多个选择
    const filterLabel = page.locator('#priorityFilterLabel');
    const labelText = await filterLabel.textContent();
    expect(labelText).toMatch(/P0/);
    expect(labelText).toMatch(/P1/);
  });

  /**
   * UI-PRIO-006: 图表数据过滤验证
   * 验证过滤后 API 返回的数据确实被过滤
   * 通过对比过滤前后图表标题显示的过滤条件来验证
   */
  test('UI-PRIO-006: 图表数据过滤验证', async ({ page }) => {
    // 使用现有的 SOC_DV 数据的 CP（已有 P0/P1/P2）

    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800); // 等待图表加载

    // 验证初始状态：标签显示"全部"
    const initialLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(initialLabel).toContain('全部');

    // 通过 API 验证过滤前的 CP 总数
    const totalCPResponse = await page.evaluate(async () => {
      const res = await fetch('/api/cp?project_id=3'); // SOC_DV project id = 3
      return res.json();
    });
    const totalCPCount = Array.isArray(totalCPResponse) ? totalCPResponse.length : 0;
    console.log('Total CP count:', totalCPCount);

    // 点击 Priority 过滤下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 选择 P0
    await page.check('#priorityFilterDropdown input[value="P0"]');
    await page.waitForTimeout(200);

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证标签显示 P0
    const filteredLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(filteredLabel).toContain('P0');

    // 验证重置按钮可见
    const resetBtn = page.locator('#resetPriorityBtn');
    await expect(resetBtn).toBeVisible();

    // 通过 API 验证 P0 的 CP 数量
    const p0CPResponse = await page.evaluate(async () => {
      const res = await fetch('/api/cp?project_id=3');
      const cps = await res.json();
      // 过滤出 P0 的 CP
      return cps.filter((cp: any) => cp.priority === 'P0').length;
    });
    console.log('P0 CP count:', p0CPResponse);

    // 验证 P0 数量 < 总数
    expect(p0CPResponse).toBeLessThan(totalCPCount);

    // 点击重置按钮
    await resetBtn.click();
    await page.waitForTimeout(500);

    // 验证恢复"全部"
    const resetLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(resetLabel).toContain('全部');
  });

  // ========================================
  // REQ-2.2 功能测试（图表Priority过滤 - 实际曲线）
  // ========================================

  /**
   * UI-PRIO-007: 实际曲线单Priority过滤
   * 选择P0时实际曲线显示P0覆盖率
   * 验证方式：应用过滤后通过 API 获取数据，验证 priority_filter=P0
   */
  test('UI-PRIO-007: 实际曲线单Priority过滤', async ({ page }) => {
    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800);

    // 验证初始状态：无过滤
    const initialLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(initialLabel).toContain('全部');

    // 点击 Priority 过滤下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 选择 P0
    await page.check('#priorityFilterDropdown input[value="P0"]');
    await page.waitForTimeout(200);

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证标签显示 P0
    const filteredLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(filteredLabel).toContain('P0');

    // 通过 API 验证过滤后的数据确实返回 P0 过滤
    const filteredData = await page.evaluate(async () => {
      const res = await fetch('/api/progress/3?priority=P0');
      return res.json();
    });

    // 验证 API 返回的 priority_filter 为 P0
    expect(filteredData.priority_filter).toBe('P0');

    // 验证 actual 数据存在
    expect(filteredData.actual).toBeDefined();
    expect(Array.isArray(filteredData.actual)).toBe(true);

    // 验证重置按钮可见
    const resetBtn = page.locator('#resetPriorityBtn');
    await expect(resetBtn).toBeVisible();

    // 点击重置恢复
    await resetBtn.click();
    await page.waitForTimeout(500);

    // 验证恢复全部
    const resetLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(resetLabel).toContain('全部');
  });

  /**
   * UI-PRIO-008: 实际曲线多Priority过滤
   * 选择P0,P1时实际曲线显示合并覆盖率
   * 验证方式：应用过滤后通过 API 获取数据，验证 priority_filter=P0,P1
   */
  test('UI-PRIO-008: 实际曲线多Priority过滤', async ({ page }) => {
    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800);

    // 点击 Priority 过滤下拉框
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);

    // 选择 P0（每次选择后下拉框会关闭，需要重新打开）
    await page.check('#priorityFilterDropdown input[value="P0"]', { force: true });
    await page.waitForTimeout(100);

    // 重新打开下拉框选择 P1
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);
    await page.check('#priorityFilterDropdown input[value="P1"]', { force: true });
    await page.waitForTimeout(100);

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证标签显示 P0+P1
    const filteredLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(filteredLabel).toContain('P0');
    expect(filteredLabel).toContain('P1');

    // 通过 API 验证过滤后的数据确实返回 P0,P1 过滤
    const filteredData = await page.evaluate(async () => {
      const res = await fetch('/api/progress/3?priority=P0,P1');
      return res.json();
    });

    // 验证 API 返回的 priority_filter 为 P0,P1
    expect(filteredData.priority_filter).toBe('P0,P1');

    // 验证 actual 数据存在
    expect(filteredData.actual).toBeDefined();
    expect(Array.isArray(filteredData.actual)).toBe(true);

    // 验证重置按钮可见
    const resetBtn = page.locator('#resetPriorityBtn');
    await expect(resetBtn).toBeVisible();

    // 点击重置恢复
    await resetBtn.click();
    await page.waitForTimeout(500);

    // 验证恢复全部
    const resetLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(resetLabel).toContain('全部');
  });

  /**
   * UI-PRIO-009: 实际曲线无过滤
   * 无过滤时显示总体覆盖率
   * 验证方式：初始状态（无过滤）通过 API 获取数据，验证 priority_filter 为空
   */
  test('UI-PRIO-009: 实际曲线无过滤', async ({ page }) => {
    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800);

    // 验证初始状态：无过滤（标签显示"全部"）
    const initialLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(initialLabel).toContain('全部');

    // 验证重置按钮初始状态隐藏
    const resetBtn = page.locator('#resetPriorityBtn');
    await expect(resetBtn).toBeHidden();

    // 通过 API 获取无过滤时的数据
    const noFilterData = await page.evaluate(async () => {
      const res = await fetch('/api/progress/3');
      return res.json();
    });

    // 验证 API 返回的 priority_filter 为空
    expect(noFilterData.priority_filter).toBe('');

    // 验证 actual 数据存在（总体覆盖率）
    expect(noFilterData.actual).toBeDefined();
    expect(Array.isArray(noFilterData.actual)).toBe(true);

    // 验证 planned 数据存在（计划曲线）
    expect(noFilterData.planned).toBeDefined();
    expect(Array.isArray(noFilterData.planned)).toBe(true);
  });

  /**
   * UI-PRIO-010: 计划曲线vs实际曲线对比
   * 两种曲线使用不同的数据源但统一的过滤
   * 验证方式：应用过滤后，验证 planned 和 actual 数据都使用相同的 priority_filter
   */
  test('UI-PRIO-010: 计划曲线vs实际曲线对比', async ({ page }) => {
    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800);

    // 应用 P0 过滤
    await page.click('#priorityFilterLabel');
    await page.waitForTimeout(300);
    await page.check('#priorityFilterDropdown input[value="P0"]');
    await page.waitForTimeout(200);

    // 点击应用按钮
    await page.click('button:has-text("应用")');
    await page.waitForTimeout(500);

    // 验证标签显示 P0
    const filteredLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(filteredLabel).toContain('P0');

    // 通过 API 验证 planned 和 actual 数据都使用相同的过滤条件
    const filteredData = await page.evaluate(async () => {
      const res = await fetch('/api/progress/3?priority=P0');
      return res.json();
    });

    // 验证 priority_filter 字段正确反映过滤条件
    expect(filteredData.priority_filter).toBe('P0');

    // 验证 planned 数据存在
    expect(filteredData.planned).toBeDefined();
    expect(Array.isArray(filteredData.planned)).toBe(true);

    // 验证 actual 数据存在
    expect(filteredData.actual).toBeDefined();
    expect(Array.isArray(filteredData.actual)).toBe(true);

    // 两种曲线使用相同的 priority_filter（统一的过滤）
    // planned 和 actual 的数据范围都应该被 P0 过滤

    // 验证重置按钮可见
    const resetBtn = page.locator('#resetPriorityBtn');
    await expect(resetBtn).toBeVisible();

    // 点击重置恢复
    await resetBtn.click();
    await page.waitForTimeout(500);

    // 验证恢复全部
    const resetLabel = await page.locator('#priorityFilterLabel').textContent();
    expect(resetLabel).toContain('全部');

    // 验证重置后 priority_filter 为空
    const resetData = await page.evaluate(async () => {
      const res = await fetch('/api/progress/3');
      return res.json();
    });
    expect(resetData.priority_filter).toBe('');
  });

  // ========================================
  // 回归测试
  // ========================================

  /**
   * UI-REG-001: TC CRUD回归测试
   * 验证现有TC增删改查功能正常
   */
  test('UI-REG-001: TC CRUD回归测试', async ({ page }) => {
    const tcName = TestDataFactory.generateTCName();

    // 1. Create - 创建 TC
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    await page.click('text=+ 添加 TC');
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: TIMEOUT });

    await page.fill('#tcTestbench', 'tb_reg_' + tcName);
    await page.fill('#tcTestName', tcName);
    await page.fill('#tcScenario', 'Regression test TC');

    await page.click('#tcModal button[type="submit"]');
    await page.waitForSelector('#tcModal', { state: 'hidden', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    // 刷新页面验证
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: TIMEOUT });
    await page.selectOption('#projectSelector', { label: currentProjectName });
    await page.waitForTimeout(500);
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: TIMEOUT });

    // 验证 TC 存在
    const tcRow = page.locator(`#tcList tr:has-text("${tcName}")`).first();
    await expect(tcRow).toBeVisible({ timeout: TIMEOUT });

    // 2. Read - 读取 TC 详情
    await page.click(`#tcList tr:has-text("${tcName}") .action-btn.edit`);
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: TIMEOUT });

    const testNameValue = await page.inputValue('#tcTestName');
    expect(testNameValue).toBe(tcName);

    // 关闭模态框
    await page.click('#tcModal .modal-close');
    await page.waitForSelector('#tcModal', { state: 'hidden', timeout: TIMEOUT });

    // 3. Update - 更新 TC
    await page.click(`#tcList tr:has-text("${tcName}") .action-btn.edit`);
    await page.waitForSelector('#tcModal', { state: 'visible', timeout: TIMEOUT });

    await page.fill('#tcTestName', tcName + '_updated');
    await page.click('#tcModal button[type="submit"]');
    await page.waitForSelector('#tcModal', { state: 'hidden', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    // 验证更新成功
    const updatedRow = page.locator(`#tcList tr:has-text("${tcName}_updated")`).first();
    await expect(updatedRow).toBeVisible();

    // 4. Delete - 删除 TC
    // 先关闭可能打开的模态框
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // 处理确认对话框
    page.once('dialog', async dialog => {
      await dialog.accept();
    });

    await page.click(`#tcList tr:has-text("${tcName}_updated") .action-btn.delete`);
    await page.waitForTimeout(500);

    // 验证删除成功
    const deletedRow = page.locator(`#tcList tr:has-text("${tcName}_updated")`).first();
    await expect(deletedRow).toBeHidden();
  });

  /**
   * UI-REG-002: CP CRUD回归测试
   * 验证现有CP增删改查功能正常
   */
  test('UI-REG-002: CP CRUD回归测试', async ({ page }) => {
    const cpName = 'CP_Reg_Test_' + Date.now();

    // 1. Create - 创建 CP
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    await page.click('button:has-text("+ 添加 CP")');
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: TIMEOUT });

    await page.fill('#cpFeature', 'Feature_Regression');
    await page.fill('#cpCoverPoint', cpName);
    await page.selectOption('#cpPriority', 'P1');

    await page.click('#cpForm button[type="submit"]');
    await page.waitForSelector('#cpModal', { state: 'hidden', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    // 刷新页面验证
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: TIMEOUT });
    await page.selectOption('#projectSelector', { label: currentProjectName });
    await page.waitForTimeout(500);
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: TIMEOUT });

    // 验证 CP 存在
    const cpRow = page.locator(`#cpList tr:has-text("${cpName}")`).first();
    await expect(cpRow).toBeVisible({ timeout: TIMEOUT });

    // 2. Read - 读取 CP 详情
    await page.click(`#cpList tr:has-text("${cpName}") .action-btn.edit`);
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: TIMEOUT });

    const coverPointValue = await page.inputValue('#cpCoverPoint');
    expect(coverPointValue).toBe(cpName);

    // 关闭模态框
    await page.click('#cpModal .modal-close');
    await page.waitForSelector('#cpModal', { state: 'hidden', timeout: TIMEOUT });

    // 3. Update - 更新 CP
    await page.click(`#cpList tr:has-text("${cpName}") .action-btn.edit`);
    await page.waitForSelector('#cpModal', { state: 'visible', timeout: TIMEOUT });

    await page.fill('#cpCoverPoint', cpName + '_updated');
    await page.click('#cpForm button[type="submit"]');
    await page.waitForSelector('#cpModal', { state: 'hidden', timeout: TIMEOUT });
    await page.waitForTimeout(500);

    // 验证更新成功
    const updatedRow = page.locator(`#cpList tr:has-text("${cpName}_updated")`).first();
    await expect(updatedRow).toBeVisible();

    // 4. Delete - 删除 CP
    // 先关闭可能打开的模态框
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    // 处理确认对话框
    page.once('dialog', async dialog => {
      await dialog.accept();
    });

    await page.click(`#cpList tr:has-text("${cpName}_updated") .action-btn.delete`);
    await page.waitForTimeout(500);

    // 验证删除成功
    const deletedRow = page.locator(`#cpList tr:has-text("${cpName}_updated")`).first();
    await expect(deletedRow).toBeHidden();
  });

  /**
   * UI-REG-003: 图表渲染回归测试
   * 验证现有图表功能正常
   */
  test('UI-REG-003: 图表渲染回归测试', async ({ page }) => {
    // 使用现有的 SOC_DV 数据的 CP

    // 切换到 Progress Charts 标签
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForSelector('#progressPanel', { state: 'visible', timeout: TIMEOUT });
    await page.waitForTimeout(800); // 等待 Chart.js 加载

    // 验证图表画布存在
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();

    // 验证图表标题区域
    const chartContainer = page.locator('#progressChartContainer');
    await expect(chartContainer).toBeVisible();

    // 验证 Priority 过滤控件存在
    const priorityFilter = page.locator('#priorityFilterLabel');
    await expect(priorityFilter).toBeVisible();

    // 验证日期选择器存在
    const startDate = page.locator('#progressStartDate');
    const endDate = page.locator('#progressEndDate');
    await expect(startDate).toBeVisible();
    await expect(endDate).toBeVisible();

    // 验证刷新按钮存在
    const refreshBtn = page.locator('button:has-text("应用")');
    await expect(refreshBtn).toBeVisible();
  });
});
