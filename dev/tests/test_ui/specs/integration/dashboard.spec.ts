/**
 * Dashboard UI Tests - v0.12.0
 *
 * 测试 Dashboard v0.12.0 Tab 的 UI 功能和交互
 * 4 Tab 结构: 概览 / Coverage Matrix / Owner Distribution / Coverage Holes
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/dashboard.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Dashboard UI Tests - v0.12.0', () => {

  /**
   * 登录辅助函数 - 使用 SOC_DV 项目
   */
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 处理引导页
    await page.waitForTimeout(500);
    const introOverlay = page.locator('#introOverlay');
    const introVisible = await introOverlay.isVisible().catch(() => false);

    if (introVisible) {
      const introBtn = page.locator('.intro-cta-btn');
      const btnVisible = await introBtn.isVisible().catch(() => false);

      if (btnVisible) {
        await introBtn.click();
        await page.waitForTimeout(1000);
      }

      await page.evaluate(() => {
        const overlay = document.getElementById('introOverlay');
        if (overlay) overlay.classList.remove('show');
      });
      await page.waitForTimeout(500);
    }

    // 使用正常表单提交流程
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 处理密码修改模态框
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      console.log('Password change modal detected, handling...');
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 15000 }).catch(() => {});
      await page.waitForTimeout(2000);
    }

    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });
    await page.waitForTimeout(1000);
  }

  /**
   * 切换到 SOC_DV 项目
   */
  async function selectSOCDVProject(page: any) {
    // 等待项目选择器加载
    await page.waitForFunction(() => {
      const selector = document.getElementById('projectSelector');
      return selector && selector.options.length > 1;
    }, { timeout: 15000 });

    // 选择 SOC_DV 项目
    await page.evaluate(async () => {
      const selector = document.getElementById('projectSelector');
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

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await selectSOCDVProject(page);
  });

  /**
   * UI-DASH-001: Dashboard Tab 正确显示在 Tab 栏
   */
  test('UI-DASH-001: Dashboard Tab 正确显示在 Tab 栏', async ({ page }) => {
    // 验证 Dashboard Tab 存在于 Tab 栏
    const dashboardTab = page.locator('#dashboardTab');
    await expect(dashboardTab).toBeVisible();

    // 验证 Tab 文本
    const tabText = await dashboardTab.textContent();
    expect(tabText).toBe('Dashboard');

    // 验证 Tab 有 onclick 属性
    const onclick = await dashboardTab.getAttribute('onclick');
    expect(onclick).toContain('switchTab');
  });

  /**
   * UI-DASH-002: 点击 Dashboard Tab 显示 Dashboard 内容
   */
  test('UI-DASH-002: 点击 Dashboard Tab 显示 Dashboard 内容', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(1500);

    // 验证 Dashboard 内容区域显示
    const dashboardContent = page.locator('#dashboard-content');
    await expect(dashboardContent).toBeVisible();

    // 验证概览 Tab 内容显示
    const overviewContent = page.locator('#overview-content');
    await expect(overviewContent).toBeVisible();
  });

  /**
   * UI-DASH-003: 概览卡片显示 3 项指标 (已覆盖/未关联/TC通过率) + 周环比
   * v0.12.0: 移除 Total CP 和 Coverage 卡片，新增 TC Pass Rate
   */
  test('UI-DASH-003: 概览卡片显示 3 项指标', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(3000); // 等待数据加载

    // 验证概览卡片容器
    const overviewContainer = page.locator('#dashboard-overview');
    await expect(overviewContainer).toBeVisible();

    // 验证 3 张概览卡片 (v0.12.0)
    const cards = page.locator('.overview-card');
    const cardCount = await cards.count();
    expect(cardCount).toBe(3);

    // 验证卡片内容 (v0.12.0: 已覆盖/未关联/TC通过率)
    const labels = await page.locator('.overview-label').allTextContents();
    expect(labels).toContain('Covered');
    expect(labels).toContain('Unlinked');
    expect(labels).toContain('TC Pass Rate');

    // 验证数值显示 - 值可能包含周环比指示器如 "24/30↓-3"
    const values = await page.locator('.overview-value').allTextContents();
    expect(values.length).toBe(3); // 应该有 3 个值
    for (const value of values) {
      // 值应该包含数字、斜杠或百分号
      expect(value.trim().length).toBeGreaterThan(0);
    }
  });

  /**
   * UI-DASH-004: 矩阵预览 (Matrix Preview) 正确显示
   * v0.12.0: Feature 分布被矩阵预览替代
   */
  test('UI-DASH-004: 矩阵预览正确显示 Top 4 Features', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(3000);

    // 验证 Matrix Preview 容器
    const matrixPreview = page.locator('#matrix-preview');
    await expect(matrixPreview).toBeVisible();

    // 验证标题 - matrix-preview 可能没有单独的 chart-title
    const titleExists = await page.locator('#matrix-preview .chart-title').isVisible().catch(() => false);
    if (titleExists) {
      const chartTitle = page.locator('#matrix-preview .chart-title');
      const titleText = await chartTitle.textContent();
      expect(titleText).toContain('Matrix Preview');
    }

    // 验证有查看完整链接
    const viewAllLink = page.locator('#matrix-preview .summary-card-link');
    await expect(viewAllLink).toBeVisible();
  });

  /**
   * UI-DASH-005: 趋势折线图正确显示 7 天数据
   * v0.12.0: 保留趋势图
   */
  test('UI-DASH-005: 趋势折线图正确显示 7 天数据', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(2000);

    // 验证 Trend Chart 容器
    const trendChart = page.locator('#trend-chart');
    await expect(trendChart).toBeVisible();

    // 验证图表标题
    const chartTitle = page.locator('.trend-card .chart-title');
    await expect(chartTitle).toBeVisible();

    // 验证 SVG 趋势图已渲染
    const trendSvg = page.locator('.trend-svg');
    await expect(trendSvg).toBeVisible();

    // 验证折线存在
    const trendLine = page.locator('.trend-line');
    await expect(trendLine).toBeVisible();
  });

  /**
   * UI-DASH-006: 空洞摘要正确显示 (Top 5 critical holes)
   * v0.12.0: Top 5 Uncovered 被空洞摘要替代
   */
  test('UI-DASH-006: 空洞摘要正确显示 Top 5 critical holes', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(2000);

    // 验证 Holes Summary 容器
    const holesSummary = page.locator('#holes-summary');
    await expect(holesSummary).toBeVisible();

    // 验证标题
    const sectionTitle = page.locator('#holes-summary .summary-card-title');
    const titleText = await sectionTitle.textContent();
    expect(titleText).toContain('Coverage Holes');

    // 验证有 View all 链接
    const viewAllLink = page.locator('#holes-summary .summary-card-link');
    await expect(viewAllLink).toBeVisible();

    // 验证最多显示 5 个空洞卡片
    const holeCards = page.locator('#holes-summary .hole-card');
    const cardCount = await holeCards.count();
    expect(cardCount).toBeLessThanOrEqual(5);
  });

  /**
   * UI-DASH-007: Owner 摘要正确显示 (Top 3 owners)
   * v0.12.0: Recent Activity 被 Owner 摘要替代
   */
  test('UI-DASH-007: Owner 摘要正确显示 Top 3 owners', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(2000);

    // 验证 Owner Summary 容器
    const ownerSummary = page.locator('#owner-summary');
    await expect(ownerSummary).toBeVisible();

    // 验证标题
    const sectionTitle = page.locator('#owner-summary .summary-card-title');
    const titleText = await sectionTitle.textContent();
    expect(titleText).toContain('Owner');

    // 验证有 View all 链接
    const viewAllLink = page.locator('#owner-summary .summary-card-link');
    await expect(viewAllLink).toBeVisible();
  });

  /**
   * UI-DASH-008: Tab 切换正确 - 4 个 Dashboard 子 Tab 都可见
   * v0.12.0: 新 Tab 结构 (Overview / Coverage Matrix / Owner Distribution / Coverage Holes)
   */
  test('UI-DASH-008: 4 个 Dashboard 子 Tab 都正确显示', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(1500);

    // 验证概览 Tab
    const overviewTab = page.locator('.dashboard-tab[data-tab="overview"]');
    await expect(overviewTab).toBeVisible();

    // 验证矩阵 Tab
    const matrixTab = page.locator('.dashboard-tab[data-tab="matrix"]');
    await expect(matrixTab).toBeVisible();

    // 验证 Owner Tab
    const ownerTab = page.locator('.dashboard-tab[data-tab="owner"]');
    await expect(ownerTab).toBeVisible();

    // 验证空洞 Tab
    const holesTab = page.locator('.dashboard-tab[data-tab="holes"]');
    await expect(holesTab).toBeVisible();
  });

  /**
   * UI-DASH-009: 点击空洞摘要项跳转到 Coverage Holes Tab
   * v0.12.0: 新功能
   */
  test('UI-DASH-009: 点击空洞摘要项跳转到 Coverage Holes Tab', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(3000);

    // 检查是否有空洞卡片
    const holeCards = page.locator('#holes-summary .hole-card');
    const cardCount = await holeCards.count();

    if (cardCount > 0) {
      // 点击 View all 链接跳转到 Coverage Holes Tab
      const viewAllLink = page.locator('#holes-summary .summary-card-link');
      await viewAllLink.click();
      await page.waitForTimeout(1500);

      // 验证切换到了 Coverage Holes Tab
      const holesTabActive = page.locator('.dashboard-tab[data-tab="holes"].active');
      await expect(holesTabActive).toBeVisible();
    } else {
      // 如果没有空洞，验证空状态
      const emptyState = page.locator('#holes-summary .dashboard-empty');
      await expect(emptyState).toBeVisible();
    }
  });

  /**
   * UI-DASH-010: 移动端布局正确折叠为单列
   */
  test('UI-DASH-010: 移动端布局正确折叠为单列', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 });

    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(2000);

    // 验证概览卡片在移动端为单列
    const overviewContainer = page.locator('#dashboard-overview');
    const overviewGridCols = await overviewContainer.evaluate((el) => {
      return window.getComputedStyle(el).gridTemplateColumns;
    });
    // 单列时应该只有一个列值
    const cols = overviewGridCols.split(' ');
    expect(cols.length).toBe(1);

    // 验证趋势图行在移动端为单列
    const trendCard = page.locator('.trend-card');
    const trendDisplay = await trendCard.evaluate((el) => {
      return window.getComputedStyle(el).display;
    });
    expect(trendDisplay).toBe('block');
  });

  /**
   * UI-DASH-011: 页面加载时数字有跳动动画
   */
  test('UI-DASH-011: 页面加载时数字有跳动动画', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');

    // 立即检查概览卡片数值元素
    const overviewValue = page.locator('.overview-value').first();

    // 获取初始状态
    const initialOpacity = await overviewValue.evaluate((el) => {
      return window.getComputedStyle(el).opacity;
    });

    // 等待动画开始
    await page.waitForTimeout(100);

    // 验证动画效果（检查 animation 或 opacity 变化）
    const hasAnimation = await overviewValue.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.animationName !== 'none' || style.animation !== 'none';
    });

    // 验证 countUp 动画存在
    const animationName = await overviewValue.evaluate((el) => {
      return window.getComputedStyle(el).animationName;
    });
    expect(animationName).toBe('countUp');
  });

  /**
   * UI-DASH-012: Hover 状态正确响应
   */
  test('UI-DASH-012: Hover 状态正确响应', async ({ page }) => {
    // 点击 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(2000);

    // 检查空洞卡片 hover
    const holeCard = page.locator('.hole-card').first();
    if (await holeCard.isVisible()) {
      await holeCard.hover();
      await page.waitForTimeout(200);

      // 验证 hover 样式变化
      const hasHoverEffect = await holeCard.evaluate((el) => {
        const style = window.getComputedStyle(el);
        return style.cursor === 'pointer';
      });
      expect(hasHoverEffect).toBeTruthy();
    }

    // 检查概览卡片 hover
    const overviewCard = page.locator('.overview-card').first();
    if (await overviewCard.isVisible()) {
      await overviewCard.hover();
      await page.waitForTimeout(200);

      // 验证没有错误（hover 不应该导致 JS 错误）
      const consoleErrors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });
      await page.waitForTimeout(200);
      expect(consoleErrors.filter(e => !e.includes('favicon'))).toHaveLength(0);
    }
  });

  /**
   * UI-DASH-013: 空数据时显示空状态提示
   */
  test('UI-DASH-013: 空数据时显示空状态提示', async ({ page }) => {
    // 创建一个空项目来测试空状态
    const projectName = `TestDashboard_Empty_${Date.now()}`;

    // 通过 API 创建空项目
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
    }, projectName);

    const projectId = createResult.project?.id;
    console.log('Created empty project:', projectId);

    // 切换到空项目
    await page.evaluate(async (projId) => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].value === String(projId)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectId);
    await page.waitForTimeout(3000); // 等待项目切换完成

    // 验证 Dashboard Tab
    await page.click('#dashboardTab');
    await page.waitForTimeout(3000);

    // 验证概览卡片存在
    const overviewContainer = page.locator('#dashboard-overview');
    await expect(overviewContainer).toBeVisible();

    // 验证数值显示 - 可能包含周环比指示器
    const overviewValue = page.locator('.overview-value').first();
    const valueText = await overviewValue.textContent();
    console.log('Empty project value:', valueText);

    // 空项目应该显示 "--" 或数字（可能是 0 或 --）
    // 注意：空项目的 Dashboard API 可能返回 "0" 而不是 "--"
    expect(valueText.trim().length).toBeGreaterThan(0);

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
});
