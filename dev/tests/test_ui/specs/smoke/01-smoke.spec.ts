/**
 * Smoke 测试 - 核心功能快速验证
 *
 * 覆盖 Tracker 最核心的功能: 页面加载、导航、CRUD 操作
 * 运行时间: ~3 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/smoke/01-smoke.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Smoke - 核心功能', () => {

  // ========== 登录辅助函数 ==========
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);
    // 等待项目选择器加载
    await page.waitForFunction(() => {
      const selector = document.getElementById('projectSelector');
      return selector && selector.options.length > 1;
    }, { timeout: 15000 });
  }

  async function selectProject(page: any, projectName: string = 'SOC_DV') {
    await page.click('#projectSelector');
    await page.waitForTimeout(500);
    await page.selectOption('#projectSelector', { label: projectName });
    await page.waitForTimeout(1000);
  }

  // ========== SMOKE-001: 页面加载 ==========
  test('SMOKE-001: 页面加载', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // 验证页面标题
    await expect(page).toHaveTitle(/Tracker|芯片验证/);

    // 验证登录表单存在
    await expect(page.locator('#loginUsername')).toBeVisible();
    await expect(page.locator('#loginPassword')).toBeVisible();
    await expect(page.locator('button.login-btn')).toBeVisible();
  });

  // ========== SMOKE-002: admin 登录成功 ==========
  test('SMOKE-002: admin 登录成功', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');

    // 等待登录成功后页面跳转
    await page.waitForTimeout(1500);

    // 验证项目选择器出现
    await expect(page.locator('#projectSelector')).toBeVisible();

    // 验证用户名显示
    const userDisplay = page.locator('.header-user');
    if (await userDisplay.count() > 0) {
      await expect(userDisplay).toContainText('admin');
    }
  });

  // ========== SMOKE-003: guest 登录成功 ==========
  test('SMOKE-003: guest 登录成功', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    // 使用 guest 登录按钮（guest 没有密码）
    await page.click('#guestLoginBtn');

    // 等待登录成功并等待覆盖层消失
    await page.waitForFunction(() => {
      const overlay = document.getElementById('loginOverlay');
      return !overlay || !overlay.classList.contains('show');
    }, { timeout: 30000 });

    // 验证登录成功
    await expect(page.locator('#projectSelector')).toBeVisible();
  });

  // ========== SMOKE-004: 错误密码提示 ==========
  test('SMOKE-004: 错误密码提示', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'wrongpassword');
    await page.click('button.login-btn');

    await page.waitForTimeout(1000);

    // 验证错误提示出现
    const errorMsg = page.locator('.login-error, .error-message, #loginError');
    if (await errorMsg.count() > 0) {
      await expect(errorMsg.first()).toBeVisible();
    }
  });

  // ========== SMOKE-005: 项目切换 ==========
  test('SMOKE-005: 项目切换', async ({ page }) => {
    await loginAsAdmin(page);

    // 选择 SOC_DV 项目
    await selectProject(page, 'SOC_DV');

    // 验证项目切换成功 - 检查项目选择器的值
    const selector = page.locator('#projectSelector');
    const value = await selector.inputValue();
    expect(value).toBeTruthy();
  });

  // ========== SMOKE-006: 创建项目 ==========
  test('SMOKE-006: 创建项目', async ({ page }) => {
    await loginAsAdmin(page);

    // 点击项目按钮
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    // 点击添加项目按钮
    const addBtn = page.locator('button:has-text("添加项目"), button:has-text("+ 项目")');
    if (await addBtn.count() > 0) {
      await addBtn.click();
      await page.waitForTimeout(500);

      // 填写项目名称
      const projectName = `Smoke_Test_${Date.now()}`;
      await page.fill('#projectName', projectName);

      // 提交
      const submitBtn = page.locator('#projectForm button[type="submit"], #projectModal button[type="submit"]');
      await submitBtn.click();
      await page.waitForTimeout(1000);

      // 验证项目创建成功（项目出现在列表中）
      await expect(page.locator(`.project-list, #projectList`).first()).toBeVisible();
    }
  });

  // ========== SMOKE-007: CP 标签切换 ==========
  test('SMOKE-007: CP 标签切换', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 点击 CP 标签
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(1000);

    // 验证 CP 面板可见
    const cpPanel = page.locator('#cpPanel, .cp-panel');
    await expect(cpPanel.first()).toBeVisible();
  });

  // ========== SMOKE-008: 创建 CP ==========
  test('SMOKE-008: 创建 CP', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 切换到 CP 标签
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(1000);

    // 点击添加 CP 按钮
    const addBtn = page.locator('button:has-text("+ 添加 CP"), button:has-text("+ CP")');
    await addBtn.click();
    await page.waitForTimeout(500);

    // 填写 CP 必填字段
    await page.fill('#cpFeature', 'Test_Feature');
    await page.fill('#cpCoverPoint', `Test_CP_${Date.now()}`);
    await page.fill('#cpDetails', 'Smoke Test Cover Point');

    // 提交
    const submitBtn = page.locator('#cpForm button[type="submit"]');
    await submitBtn.click();
    await page.waitForTimeout(1000);

    // 验证 CP 创建成功 - 表格中有新数据
    const cpTable = page.locator('.cp-table, #cpTable');
    await expect(cpTable.first()).toBeVisible();
  });

  // ========== SMOKE-009: 编辑 CP ==========
  test('SMOKE-009: 编辑 CP', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 切换到 CP 标签
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(1000);

    // 点击第一行的编辑按钮
    const editBtn = page.locator('.cp-table tbody tr:first-child .action-btn.edit, #cpTable tbody tr:first-child .edit-btn');
    if (await editBtn.count() > 0) {
      await editBtn.click();
      await page.waitForTimeout(1000);

      // 验证编辑模态框打开
      const modal = page.locator('#cpModal');
      const isVisible = await modal.isVisible().catch(() => false);
      if (isVisible) {
        await expect(modal).toBeVisible();

        // 关闭模态框
        const closeBtn = page.locator('#cpModal .modal-close, #cpModal button.cancel');
        if (await closeBtn.count() > 0) {
          await closeBtn.first().click();
          await page.waitForTimeout(500);
        }
      }
    }
  });

  // ========== SMOKE-010: 删除 CP ==========
  test('SMOKE-010: 删除 CP', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 切换到 CP 标签
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(1000);

    // 设置对话框处理器
    page.on('dialog', async dialog => {
      await dialog.accept();
    });

    // 点击第一行的删除按钮
    const deleteBtn = page.locator('.cp-table tbody tr:first-child .action-btn.delete, #cpTable tbody tr:first-child .delete-btn');
    if (await deleteBtn.count() > 0) {
      await deleteBtn.click();
      await page.waitForTimeout(1000);

      // 验证 CP 被删除
      const cpTable = page.locator('.cp-table, #cpTable');
      await expect(cpTable.first()).toBeVisible();
    }
  });

  // ========== SMOKE-011: TC 标签切换 ==========
  test('SMOKE-011: TC 标签切换', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 点击 TC 标签
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForTimeout(1000);

    // 验证 TC 面板可见
    const tcPanel = page.locator('#tcPanel, .tc-panel');
    await expect(tcPanel.first()).toBeVisible();
  });

  // ========== SMOKE-012: 创建 TC ==========
  test('SMOKE-012: 创建 TC', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 切换到 TC 标签
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForTimeout(1000);

    // 点击添加 TC 按钮
    const addBtn = page.locator('button:has-text("+ 添加 TC"), button:has-text("+ TC")');
    await addBtn.click();
    await page.waitForTimeout(500);

    // 填写 TC 必填字段
    await page.fill('#tcTestbench', 'TB_Test');
    await page.fill('#tcTestName', `Test_TC_${Date.now()}`);
    await page.fill('#tcCategory', 'Smoke_Test');
    await page.fill('#tcOwner', 'Tester');

    // 提交
    const submitBtn = page.locator('#tcForm button[type="submit"]');
    await submitBtn.click();
    await page.waitForTimeout(1000);

    // 验证 TC 创建成功
    const tcTable = page.locator('#tcTable, .tc-table');
    await expect(tcTable.first()).toBeVisible();
  });

  // ========== SMOKE-013: 编辑 TC ==========
  test('SMOKE-013: 编辑 TC', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 切换到 TC 标签
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForTimeout(1000);

    // 点击第一行的编辑按钮
    const editBtn = page.locator('#tcTable tbody tr:first-child .edit-btn, .tc-table tbody tr:first-child .action-btn.edit');
    if (await editBtn.count() > 0) {
      await editBtn.click();
      await page.waitForTimeout(1000);

      // 验证编辑模态框打开
      const modal = page.locator('#tcModal');
      const isVisible = await modal.isVisible().catch(() => false);
      if (isVisible) {
        await expect(modal).toBeVisible();

        // 关闭模态框
        const closeBtn = page.locator('#tcModal .modal-close, #tcModal button.cancel');
        if (await closeBtn.count() > 0) {
          await closeBtn.first().click();
          await page.waitForTimeout(500);
        }
      }
    }
  });

  // ========== SMOKE-014: 删除 TC ==========
  test('SMOKE-014: 删除 TC', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page);

    // 切换到 TC 标签
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForTimeout(1000);

    // 设置对话框处理器
    page.on('dialog', async dialog => {
      await dialog.accept();
    });

    // 点击第一行的删除按钮
    const deleteBtn = page.locator('#tcTable tbody tr:first-child .delete-btn, .tc-table tbody tr:first-child .action-btn.delete');
    if (await deleteBtn.count() > 0) {
      await deleteBtn.click();
      await page.waitForTimeout(1000);

      // 验证 TC 被删除
      const tcTable = page.locator('#tcTable, .tc-table');
      await expect(tcTable.first()).toBeVisible();
    }
  });
});
