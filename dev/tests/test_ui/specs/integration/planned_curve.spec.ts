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

  test('UI-PLAN-002: 时间段选择器可见', async ({ page }) => {
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

  test('UI-PLAN-003: 时间段选择器-应用按钮', async ({ page }) => {
    // 选择 SOC_DV 项目
    await page.click('#projectSelector');
    await page.click(`.project-item:has-text("SOC_DV")`);
    await page.waitForTimeout(500);
    
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 点击应用按钮
    await page.click('button:has-text("应用")');
    
    // 验证没有错误
    // 如果有错误，页面上会有错误提示
    const errorMsg = page.locator('#progressEmptyState');
    const hasError = await errorMsg.textContent();
    expect(hasError).not.toContain('加载失败');
  });

  test('UI-PLAN-004: 空项目显示提示', async ({ page }) => {
    // 切换到 Progress Charts
    await page.click('button.tab:has-text("Progress Charts")');
    
    // 验证空状态提示
    const emptyState = page.locator('#progressEmptyState');
    await expect(emptyState).toBeVisible();
    
    // 应该显示"请选择一个项目"
    await expect(emptyState).toContainText('请选择一个项目');
  });

  test('UI-PLAN-005: 无日期项目显示提示', async ({ page }) => {
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
});
