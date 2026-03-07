import { test, expect } from '@playwright/test';

test.describe('Progress Charts (v0.8.0)', () => {

  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:8081', { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    // 等待登录成功 - 使用 DOM 元素而不是 URL
    await page.waitForSelector('#userInfo', { timeout: 30000 });
  });

  test('UI-CHART-001: Tab 切换到 Progress Charts', async ({ page }) => {
    // 点击 Progress Charts Tab
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证 progressPanel 显示
    const progressPanel = page.locator('#progressPanel');
    await expect(progressPanel).toBeVisible();
  });

  test('UI-CHART-002: Progress Charts 面板可见', async ({ page }) => {
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证容器存在
    const progressContainer = page.locator('#progressChartContainer');
    await expect(progressContainer).toBeVisible();
  });

  // UI-CHART-003: 空项目提示显示 - 跳过：v0.8.3 版本日期是必填，无法创建无日期项目
  test.skip('UI-CHART-003: 空项目提示显示', async ({ page }) => {
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');

    // 验证空状态提示 - SOC_DV 已选中但无日期，显示日期设置提示
    const emptyState = page.locator('#progressEmptyState');
    await expect(emptyState).toBeVisible();
    await expect(emptyState).toContainText('请先设置项目起止日期');
  });

  test('UI-ISSUE-001: 项目选择框宽度固定为 200px', async ({ page }) => {
    // 检查项目选择框样式
    const projectSelector = page.locator('#projectSelector');
    await expect(projectSelector).toBeVisible();
    
    // 验证宽度
    const width = await projectSelector.evaluate((el) => {
      return window.getComputedStyle(el).width;
    });
    
    // 宽度应该接近 200px (允许一点误差)
    expect(parseInt(width)).toBeGreaterThanOrEqual(190);
    expect(parseInt(width)).toBeLessThanOrEqual(210);
  });

  test('UI-PROJ-001: 创建项目带日期', async ({ page }) => {
    // 打开项目对话框
    await page.click('#projectManageBtn');

    // 输入项目名称
    const projectName = `Test_Progress_${Date.now()}`;
    await page.fill('#newProjectName', projectName);

    // 输入日期
    await page.fill('#newProjectStartDate', '2026-01-01');
    await page.fill('#newProjectEndDate', '2026-12-31');

    // 点击创建
    await page.click('button:has-text("创建")');

    // 等待弹窗关闭
    await page.waitForSelector('#projectModal', { state: 'hidden', timeout: 5000 }).catch(() => {});
  });

  test('UI-PROJ-003: 项目列表显示日期', async ({ page }) => {
    // 打开项目对话框
    await page.click('#projectManageBtn');

    // 创建一个带日期的项目
    const projectName = `Test_Date_${Date.now()}`;
    await page.fill('#newProjectName', projectName);
    await page.fill('#newProjectStartDate', '2026-03-01');
    await page.fill('#newProjectEndDate', '2026-09-30');

    await page.click('button:has-text("创建")');

    // 等待弹窗关闭
    await page.waitForSelector('#projectModal', { state: 'hidden', timeout: 5000 }).catch(() => {});

    // 重新打开项目管理对话框查看新项目
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    // 验证新创建的项目显示日期（通过项目名称查找）
    const newProjectItem = page.locator(`.project-item:has-text("${projectName}")`);
    await expect(newProjectItem).toContainText('2026-03-01 ~ 2026-09-30');
  });
});
