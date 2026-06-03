/**
 * Integration 测试 - Progress Charts 增强功能 (v0.15.0)
 *
 * 覆盖图表类型切换 Tabs、导出功能、过滤交互
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/18-progress-charts.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

// 测试数据：使用已存在的 SOC_DV 项目 (id=3)
const TEST_PROJECT_NAME = 'SOC_DV';

test.describe('Integration - Progress Charts v0.15.0 增强功能', () => {

  /**
   * 登录为 admin 用户
   */
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 处理引导页
    const introBtn = page.locator('.intro-cta-btn');
    if (await introBtn.isVisible().catch(() => false)) {
      await introBtn.click();
      await page.waitForTimeout(500);
    }

    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');

    // 处理首次登录密码修改模态框
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

    await page.waitForTimeout(2000);
    await page.waitForSelector('#projectSelector', { state: 'visible', timeout: 10000 });
  }

  /**
   * 选择 SOC_DV 项目
   */
  async function selectSOCDVProject(page: any) {
    await page.waitForFunction(() => {
      const selector = document.getElementById('projectSelector');
      return selector && selector.options.length > 1;
    }, { timeout: 15000 });

    await page.evaluate(() => {
      const selector = document.getElementById('projectSelector') as HTMLSelectElement;
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes('SOC_DV')) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    });
    await page.waitForTimeout(2000);
  }

  /**
   * 进入 Progress Charts Tab
   */
  async function enterProgressCharts(page: any) {
    await page.click('button.tab:has-text("Progress Charts")');
    await page.waitForTimeout(2000);
  }

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await selectSOCDVProject(page);
    await enterProgressCharts(page);
  });

  // ========== PC-UI-001: 覆盖趋势图表默认显示 ==========
  test('PC-UI-001: 覆盖趋势图表默认显示', async ({ page }) => {
    // 验证 progressPanel 显示
    const progressPanel = page.locator('#progressPanel');
    await expect(progressPanel).toBeVisible();

    // 验证"覆盖趋势"tab 为 active
    const trendTab = page.locator('.chart-tab[data-chart="trend"]');
    await expect(trendTab).toBeVisible();
    const trendActive = await trendTab.evaluate((el) => el.classList.contains('active'));
    expect(trendActive).toBe(true);

    // 验证图表 canvas 存在（可能正在加载或已渲染）
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  // ========== PC-UI-002: 切换到 Feature CP 覆盖图表 ==========
  test('PC-UI-002: 切换到 Feature CP 覆盖图表', async ({ page }) => {
    const featureTab = page.locator('.chart-tab[data-chart="feature"]');
    await expect(featureTab).toBeVisible();

    // 点击 Feature 覆盖 tab
    await featureTab.click();
    await page.waitForTimeout(1500);

    // 验证 tab 变为 active
    const featureActive = await featureTab.evaluate((el) => el.classList.contains('active'));
    expect(featureActive).toBe(true);

    // 验证趋势 tab 不再是 active
    const trendTab = page.locator('.chart-tab[data-chart="trend"]');
    const trendActive = await trendTab.evaluate((el) => el.classList.contains('active'));
    expect(trendActive).toBe(false);

    // 验证 canvas 仍然可见
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  // ========== PC-UI-003: 切换到 P0/P1 对比图表 ==========
  test('PC-UI-003: 切换到 P0/P1 对比图表', async ({ page }) => {
    const p0p1Tab = page.locator('.chart-tab[data-chart="p0p1"]');
    await expect(p0p1Tab).toBeVisible();

    // 点击 P0/P1 对比 tab
    await p0p1Tab.click();
    await page.waitForTimeout(1500);

    // 验证 tab 变为 active
    const p0p1Active = await p0p1Tab.evaluate((el) => el.classList.contains('active'));
    expect(p0p1Active).toBe(true);

    // 验证其他 tabs 不再是 active
    const trendTab = page.locator('.chart-tab[data-chart="trend"]');
    const trendActive = await trendTab.evaluate((el) => el.classList.contains('active'));
    expect(trendActive).toBe(false);

    const featureTab = page.locator('.chart-tab[data-chart="feature"]');
    const featureActive = await featureTab.evaluate((el) => el.classList.contains('active'));
    expect(featureActive).toBe(false);

    // 验证 canvas 仍然可见
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  // ========== PC-UI-004: 切换回覆盖趋势图表 ==========
  test('PC-UI-004: 切换回覆盖趋势图表', async ({ page }) => {
    // 先切换到 feature
    const featureTab = page.locator('.chart-tab[data-chart="feature"]');
    await featureTab.click();
    await page.waitForTimeout(1000);

    // 再切换回 trend
    const trendTab = page.locator('.chart-tab[data-chart="trend"]');
    await trendTab.click();
    await page.waitForTimeout(1500);

    // 验证 trend tab 为 active
    const trendActive = await trendTab.evaluate((el) => el.classList.contains('active'));
    expect(trendActive).toBe(true);

    // 验证 feature tab 不再是 active
    const featureActive = await featureTab.evaluate((el) => el.classList.contains('active'));
    expect(featureActive).toBe(false);

    // 验证 canvas 仍然可见
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  // ========== PC-UI-005: 导出下拉菜单显示 ==========
  test('PC-UI-005: 导出下拉菜单显示', async ({ page }) => {
    const exportBtn = page.locator('#chartExportBtn');
    await expect(exportBtn).toBeVisible();

    // 点击导出按钮
    await exportBtn.click();
    await page.waitForTimeout(500);

    // 验证下拉菜单显示
    const exportMenu = page.locator('#chartExportMenu');
    const menuDisplay = await exportMenu.evaluate((el) =>
      window.getComputedStyle(el).display
    );
    expect(menuDisplay).toBe('block');

    // 验证有两个选项
    const menuButtons = exportMenu.locator('button');
    const buttonCount = await menuButtons.count();
    expect(buttonCount).toBe(2);

    // 验证选项文本
    const btnTexts = await menuButtons.allTextContents();
    expect(btnTexts[0]).toContain('导出当前图表');
    expect(btnTexts[1]).toContain('导出全部图表');

    // 点击其他地方关闭菜单
    await page.click('#progressChartContainer');
    await page.waitForTimeout(300);
    const menuDisplayAfter = await exportMenu.evaluate((el) =>
      window.getComputedStyle(el).display
    );
    expect(menuDisplayAfter).toBe('none');
  });

  // ========== PC-UI-006: Priority 过滤对图表生效 ==========
  test('PC-UI-006: Priority 过滤对图表生效', async ({ page }) => {
    // 打开 Priority 过滤下拉
    const priorityFilterBtn = page.locator('#priorityFilterBtn');
    await priorityFilterBtn.click();
    await page.waitForTimeout(500);

    // 选择 P0
    const p0Checkbox = page.locator('#priorityFilterDropdown input[value="P0"]');
    await p0Checkbox.check();
    await page.waitForTimeout(300);

    // 点击应用按钮
    const applyBtn = page.locator('button:has-text("应用")');
    await applyBtn.click();
    await page.waitForTimeout(2000);

    // 验证 canvas 仍然存在（图表已刷新）
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();

    // 验证 Priority 标签显示 P0
    const priorityLabel = page.locator('#priorityFilterLabel');
    const labelText = await priorityLabel.textContent();
    expect(labelText).toContain('P0');
  });

  // ========== PC-UI-007: 日期过滤对图表生效 ==========
  test('PC-UI-007: 日期过滤对图表生效', async ({ page }) => {
    // 修改日期范围
    const startDateInput = page.locator('#progressStartDate');
    const endDateInput = page.locator('#progressEndDate');

    // 获取当前日期值
    const currentStart = await startDateInput.inputValue();
    const currentEnd = await endDateInput.inputValue();

    // 如果日期选择器有值，缩小日期范围
    if (currentStart && currentEnd) {
      // 将结束日期设为开始日期后 7 天
      const start = new Date(currentStart);
      const newEnd = new Date(start);
      newEnd.setDate(newEnd.getDate() + 7);
      const newEndStr = newEnd.toISOString().split('T')[0];

      await endDateInput.fill(newEndStr);
      await page.waitForTimeout(300);
    }

    // 点击应用按钮
    const applyBtn = page.locator('button:has-text("应用")');
    await applyBtn.click();
    await page.waitForTimeout(2000);

    // 验证 canvas 仍然存在（图表已刷新）
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  // ========== PC-UI-008: 空项目图表状态 ==========
  test('PC-UI-008: 空项目图表状态', async ({ page }) => {
    // 创建一个空项目（无 CP）
    const emptyProjectName = `TestUI_EmptyChart_${Date.now()}`;

    const createResult = await page.evaluate(async (name) => {
      const today = new Date();
      const nextMonth = new Date(today);
      nextMonth.setMonth(nextMonth.getMonth() + 1);
      const startDate = today.toISOString().split('T')[0];
      const endDate = nextMonth.toISOString().split('T')[0];

      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          start_date: startDate,
          end_date: endDate,
          coverage_mode: 'tc_cp'
        }),
        credentials: 'include'
      });
      return await res.json();
    }, emptyProjectName);

    const projectId = createResult.project?.id;
    console.log('Created empty project:', projectId);

    // 切换到空项目
    await page.evaluate((projId) => {
      const selector = document.getElementById('projectSelector') as HTMLSelectElement;
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].value === String(projId)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectId);
    await page.waitForTimeout(3000);

    // 确保在 Progress Charts Tab
    await enterProgressCharts(page);

    // 验证空状态提示显示（空项目无 CP，但设置了日期）
    // 注意：空项目有日期但无 CP，应该显示空状态或空图表
    const emptyState = page.locator('#progressEmptyState');
    const chartCanvas = page.locator('#progressChart');

    // 空状态或 canvas 至少有一个可见
    const emptyVisible = await emptyState.isVisible().catch(() => false);
    const canvasVisible = await chartCanvas.isVisible().catch(() => false);

    // 空项目应该显示空状态（因为无 CP 数据）
    // 或者显示空图表（canvas 可见但数据为空）
    expect(emptyVisible || canvasVisible).toBe(true);

    // 清理测试项目
    if (projectId) {
      await page.evaluate(async (projId) => {
        await fetch(`/api/projects/${projId}`, {
          method: 'DELETE',
          credentials: 'include'
        });
      }, projectId);
    }
  });

  // ========== PC-UI-009: 三个 Tab 按钮都可见 ==========
  test('PC-UI-009: 三个图表 Tab 按钮都正确显示', async ({ page }) => {
    const trendTab = page.locator('.chart-tab[data-chart="trend"]');
    const featureTab = page.locator('.chart-tab[data-chart="feature"]');
    const p0p1Tab = page.locator('.chart-tab[data-chart="p0p1"]');

    await expect(trendTab).toBeVisible();
    await expect(featureTab).toBeVisible();
    await expect(p0p1Tab).toBeVisible();

    // 验证 Tab 文本
    const trendText = await trendTab.textContent();
    const featureText = await featureTab.textContent();
    const p0p1Text = await p0p1Tab.textContent();

    expect(trendText).toContain('覆盖趋势');
    expect(featureText).toContain('Feature覆盖');
    expect(p0p1Text).toContain('P0/P1对比');
  });

  // ========== PC-UI-010: 导出当前图表无 JS 错误 ==========
  test('PC-UI-010: 导出当前图表无 JavaScript 错误', async ({ page }) => {
    // 收集控制台错误
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 点击导出按钮
    const exportBtn = page.locator('#chartExportBtn');
    await exportBtn.click();
    await page.waitForTimeout(500);

    // 点击"导出当前图表"
    const exportCurrentBtn = page.locator('#chartExportMenu button:first-child');
    await exportCurrentBtn.click();
    await page.waitForTimeout(1000);

    // 验证没有 JavaScript 错误（排除 favicon 等非关键错误）
    const criticalErrors = consoleErrors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('Source map') &&
      !e.includes('chunk')
    );
    expect(criticalErrors).toHaveLength(0);
  });

  // ========== PC-UI-011: Tab 切换无控制台错误 ==========
  test('PC-UI-011: Tab 切换无控制台错误', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // 依次切换三个 tab
    const tabs = ['feature', 'p0p1', 'trend'];
    for (const tabType of tabs) {
      const tab = page.locator(`.chart-tab[data-chart="${tabType}"]`);
      await tab.click();
      await page.waitForTimeout(1500);
    }

    // 验证没有关键错误
    const criticalErrors = consoleErrors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('Source map') &&
      !e.includes('chunk')
    );
    expect(criticalErrors).toHaveLength(0);
  });
});
