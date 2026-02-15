/**
 * 冒烟测试 - 核心功能快速验证
 * 
 * 这组测试覆盖 Tracker 最核心的功能，确保基本流程可用
 * 运行时间: 1-2 分钟
 * 
 * 运行命令:
 *   npx playwright test tests/specs/smoke --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';

test.describe('冒烟测试 - 核心功能', () => {
  
  test.beforeEach(async ({ page }) => {
    // 每个测试前确保在首页
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test('SMOKE-001: 页面加载', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/Tracker|芯片验证/);
    
    // 验证核心元素存在 - 使用更具体的选择器
    await expect(page.locator('#projectSelector')).toBeVisible();
    await expect(page.locator('button:has-text("Cover Points")')).toBeVisible();
    await expect(page.locator('button:has-text("Test Cases")')).toBeVisible();
  });

  test('SMOKE-002: 项目切换', async ({ projectPage }) => {
    // 获取项目列表
    const projects = await projectPage.getProjectList();
    expect(projects.length).toBeGreaterThan(0);
    
    // 选择第一个项目
    if (projects.length > 0) {
      await projectPage.selectProject(projects[0]);
      await expect(await projectPage.getCurrentProject()).toContain(projects[0]);
    }
  });

  test('SMOKE-003: CP 标签切换', async ({ page }) => {
    // 切换到 CP 标签页
    await page.click('button[onclick="switchTab(\'cp\')"]');
    
    // 等待 CP 面板可见
    await page.waitForSelector('#cpPanel', { timeout: 10000 });
    
    // 验证 CP 表格存在
    const cpTable = page.locator('.cp-table');
    await expect(cpTable).toBeVisible();
  });

  test('SMOKE-004: TC 标签切换', async ({ page }) => {
    // 切换到 TC 标签页
    await page.click('button[onclick="switchTab(\'tc\')"]');
    
    // 等待 TC 面板可见
    await page.waitForSelector('#tcPanel', { timeout: 10000 });
    
    // 验证 TC 表格存在
    const tcTable = page.locator('#tcPanel table');
    await expect(tcTable).toBeVisible();
  });

  test('SMOKE-005: 创建并验证项目', async ({ projectPage }) => {
    const testName = `Smoke_Test_${Date.now()}`;
    
    // 创建项目
    await projectPage.createProject(testName);
    
    // 验证项目存在
    await projectPage.expectProjectExists(testName);
    
    // 切换到新项目并验证
    await projectPage.selectProject(testName);
    const currentProject = await projectPage.getCurrentProject();
    expect(currentProject).toContain('Smoke_Test');
  });

  test('SMOKE-006: CP 页面元素', async ({ page }) => {
    // 切换到 CP 标签页
    await page.click('text=Cover Points');
    await page.waitForTimeout(500);
    
    // 等待 CP 表格加载
    await page.waitForSelector('.cp-table', { timeout: 10000 });
    
    // 验证添加按钮存在
    await expect(page.locator('button:has-text("+ 添加 CP")')).toBeVisible();
    
    // 验证过滤区域存在
    await expect(page.locator('#cpFeatureFilter')).toBeVisible();
    await expect(page.locator('#cpPriorityFilter')).toBeVisible();
  });

  test('SMOKE-007: TC 页面元素', async ({ page }) => {
    // 切换到 TC 标签页 - 使用 onclick 属性选择器
    await page.click('button[onclick="switchTab(\'tc\')"]');
    
    // 等待 TC 面板可见
    await page.waitForSelector('#tcPanel', { timeout: 10000 });
    
    // 验证 TC 表格存在
    const table = page.locator('#tcPanel table').first();
    await expect(table).toBeVisible();
  });

  test('SMOKE-008: 项目数据统计', async ({ page }) => {
    // 等待统计数据元素存在于 DOM
    await page.waitForSelector('#cpCount', { state: 'attached', timeout: 10000 });
    await page.waitForSelector('#tcCount', { state: 'attached', timeout: 10000 });
    
    // 验证 CP 和 TC 计数元素存在
    await expect(page.locator('#cpCount')).toBeAttached();
    await expect(page.locator('#tcCount')).toBeAttached();
  });
});

test.describe('冒烟测试 - 边界验证', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test('SMOKE-009: 模态框打开关闭', async ({ projectPage }) => {
    // 打开模态框
    await projectPage.openProjectModal();
    await projectPage.expectModalVisible();
    
    // 关闭模态框
    await projectPage.closeProjectModal();
    await projectPage.expectModalHidden();
  });

  test('SMOKE-010: CP 模态框打开关闭', async ({ cpPage }) => {
    await cpPage.switchToCPTab();
    
    // 打开模态框
    await cpPage.openCPModal();
    await cpPage.expectModalVisible();
    
    // 关闭模态框
    await cpPage.closeCPModal();
    await cpPage.expectModalHidden();
  });
});
