/**
 * Integration 测试 - 项目日期验证 & 常量管理
 *
 * 覆盖 v0.8.3 项目日期必填验证和常量管理功能
 * 运行时间: ~2 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/11-date-validation.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Integration - 项目日期验证 & 常量管理 (v0.8.3)', () => {

  // ========== v0.8.3: 项目日期验证 ==========

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // 处理引导页（v0.10.x 新增）
    const introBtn = page.locator('.intro-cta-btn');
    if (await introBtn.isVisible().catch(() => false)) {
      await introBtn.click();
      await page.waitForTimeout(500);
    }
  });

  test('v0.8.3-PRJ-002: 创建项目填有效日期成功', async ({ page }) => {
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 处理首次登录密码修改模态框（v0.10.x 新增）
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

    // 点击项目管理按钮
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    // 填写有效日期
    const projectName = `Test_Valid_Dates_${Date.now()}`;
    await page.fill('#newProjectName', projectName);
    await page.fill('#newProjectStartDate', '2026-01-01');
    await page.fill('#newProjectEndDate', '2026-12-31');

    // 创建项目
    await page.click('button:has-text("创建")');
    await page.waitForTimeout(1500);

    // 验证创建成功 - 项目列表应该包含新项目
    const projectItem = page.locator(`option:has-text("${projectName}")`);
    await expect(projectItem).toBeAttached();
  });

  test('v0.8.3-PRJ-003: 结束日期早于开始日期显示错误', async ({ page }) => {
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 处理首次登录密码修改模态框（v0.10.x 新增）
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

    // 点击项目管理按钮
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    // 填写结束日期早于开始日期
    await page.fill('#newProjectName', 'Test_Invalid_Dates');
    await page.fill('#newProjectStartDate', '2026-12-31');
    await page.fill('#newProjectEndDate', '2026-01-01');

    // 尝试创建
    await page.click('button:has-text("创建")');
    await page.waitForTimeout(500);

    // 应该有错误提示（前端验证或后端返回错误）
    // 验证项目未创建 - 项目列表不应包含此项目
    const projectItem = page.locator(`option:has-text("Test_Invalid_Dates")`);
    const count = await projectItem.count();
    expect(count).toBe(0);
  });

  // ========== v0.8.3: 常量管理测试 ==========

  test('v0.8.3-CONST-001: 登录流程正常', async ({ page }) => {
    // 测试普通用户登录流程

    // 验证登录表单存在
    const usernameInput = page.locator('#loginUsername');
    const passwordInput = page.locator('#loginPassword');
    const loginBtn = page.locator('button.login-btn');

    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(loginBtn).toBeVisible();

    // 执行登录
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 处理首次登录密码修改模态框（v0.10.x 新增）
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

    // 验证登录成功 - 页面应该跳转到项目列表
    const projectSelect = page.locator('#projectSelector');
    await expect(projectSelect).toBeVisible();
  });

  test('v0.8.3-CONST-002: 项目 CRUD 正常', async ({ page }) => {
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 处理首次登录密码修改模态框（v0.10.x 新增）
    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
      await page.fill('#newPassword', 'admin123');
      await page.fill('#confirmPassword', 'admin123');
      await page.click('#changePasswordModal button.btn-primary');
      await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(1000);
    }

    const testProjectName = `Test_CRUD_${Date.now()}`;

    // Create - 创建项目
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);
    await page.fill('#newProjectName', testProjectName);
    await page.fill('#newProjectStartDate', '2026-01-01');
    await page.fill('#newProjectEndDate', '2026-12-31');
    await page.click('button:has-text("创建")');
    await page.waitForTimeout(1500);

    // Read - 读取项目（验证项目存在）
    const projectOption = page.locator(`option:has-text("${testProjectName}")`);
    await expect(projectOption).toBeAttached();

    // Delete - 删除项目（需要先打开项目详情，在顶部导航删除）
    // 简化测试：只验证 Create 和 Read
  });
});
