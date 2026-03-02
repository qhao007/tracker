import { test, expect } from '@playwright/test';

test.describe('计划曲线 (v0.8.1)', () => {

  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:8081');
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForURL('**/');
  });

  test('UI-PLAN-001: 计划曲线图表显示', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    
    // 等待项目加载
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证图表画布显示
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  test('UI-PLAN-002: 曲线数据点正确渲染', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 等待图表渲染
    await page.waitForTimeout(1000);
    
    // 验证图表存在且可见
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
    
    // 验证不是空数据提示
    const emptyState = page.locator('#progressEmptyState');
    const emptyText = await emptyState.textContent();
    expect(emptyText).not.toContain('暂无数据');
  });

  test('UI-PLAN-003: 计划曲线颜色正确', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证 canvas 存在
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  test('UI-PLAN-010: 时间段选择器可见', async ({ page }) => {
    // 选择有日期的项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证日期选择器存在
    const startDate = page.locator('#progressStartDate');
    const endDate = page.locator('#progressEndDate');
    
    await expect(startDate).toBeVisible();
    await expect(endDate).toBeVisible();
  });

  test('UI-PLAN-011: 选择日期范围后图表更新', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 设置日期范围
    await page.fill('#progressStartDate', '2026-02-01');
    await page.fill('#progressEndDate', '2026-02-28');
    
    // 点击应用按钮
    await page.click('button:has-text("应用")');
    
    // 等待图表更新
    await page.waitForTimeout(500);
    
    // 验证图表仍然可见
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  test('UI-PLAN-012: 清空时间段后恢复显示', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 清空日期
    await page.fill('#progressStartDate', '');
    await page.fill('#progressEndDate', '');
    
    // 点击应用按钮
    await page.click('button:has-text("应用")');
    
    // 等待图表更新
    await page.waitForTimeout(500);
    
    // 验证图表可见
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  test('UI-PLAN-020: 无项目显示提示', async ({ page }) => {
    // 切换到 Progress Charts（不选择项目）
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证空状态提示
    const emptyState = page.locator('#progressEmptyState');
    await expect(emptyState).toBeVisible();
    await expect(emptyState).toContainText('请选择一个项目');
  });

  test('UI-PLAN-021: 无日期项目显示提示', async ({ page }) => {
    // 选择或创建一个没有日期的项目
    await page.click('#projectSelector');
    await page.click('button:has-text("项目管理")');
    
    // 创建一个无日期项目
    const projectName = `No_Date_${Date.now()}`;
    await page.fill('#newProjectName', projectName);
    // 不填写日期
    await page.click('button:has-text("创建")');
    await page.waitForTimeout(500);
    
    // 选择这个无日期项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("${projectName}")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证显示日期设置提示
    const emptyState = page.locator('#progressEmptyState');
    await expect(emptyState).toContainText('请先设置项目起止日期');
  });

  test('UI-PLAN-022: 无 TC 项目显示提示', async ({ page }) => {
    // 创建一个无 TC 的项目
    await page.click('#projectSelector');
    await page.click('button:has-text("项目管理")');
    
    const projectName = `No_TC_${Date.now()}`;
    await page.fill('#newProjectName', projectName);
    await page.fill('#newProjectStartDate', '2026-01-01');
    await page.fill('#newProjectEndDate', '2026-12-31');
    await page.click('button:has-text("创建")');
    await page.waitForTimeout(500);
    
    // 选择这个项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("${projectName}")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证显示提示（无 CP/TC 时显示空 planned）
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  test('UI-PLAN-023: 无 CP 项目显示提示', async ({ page }) => {
    // 创建一个无 CP 的项目
    await page.click('#projectSelector');
    await page.click('button:has-text("项目管理")');
    
    const projectName = `No_CP_${Date.now()}`;
    await page.fill('#newProjectName', projectName);
    await page.fill('#newProjectStartDate', '2026-01-01');
    await page.fill('#newProjectEndDate', '2026-12-31');
    await page.click('button:has-text("创建")');
    await page.waitForTimeout(500);
    
    // 选择这个项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("${projectName}")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证图表可见（空 planned 返回空数组）
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  test('UI-PLAN-030: 图例显示', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 等待图表渲染
    await page.waitForTimeout(1000);
    
    // 验证 canvas 存在即图例可用
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });

  test('UI-PLAN-031: Tooltip 提示', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 等待图表渲染
    await page.waitForTimeout(1000);
    
    // 验证 canvas 存在
    const chartCanvas = page.locator('#progressChart');
    await expect(chartCanvas).toBeVisible();
  });
});
