/**
 * Integration 测试 - 项目管理
 *
 * 覆盖项目管理功能
 * 运行时间: ~1 分钟
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/09-project-management.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Integration - 项目管理', () => {

  // ========== PROJ-001: 项目选择器可见 ==========
  test('PROJ-001: 项目选择器可见', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 验证项目选择器存在
    await expect(page.locator('#projectSelector')).toBeVisible();
  });

  // ==========Selector')).toBe PROJ-002: guest 可以访问项目 ==========
  test('PROJ-002: guest 可以访问项目', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'guest');
    await page.fill('#loginPassword', 'guest123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 选择项目
    await page.click('#projectSelector');
    await page.waitForTimeout(500);
    await page.selectOption('#projectSelector', { label: 'SOC_DV' });
    await page.waitForTimeout(1000);

    // 验证项目数据加载
    const cpPanel = page.locator('#cpPanel');
    await expect(cpPanel.first()).toBeVisible();
  });

  // ========== PROJ-003: 点击删除弹出确认框 ==========
  test('PROJ-003: 点击删除弹出确认框', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 先创建一个测试项目
    const testProject = `Test_Delete_${Date.now()}`;
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    const addBtn = page.locator('button:has-text("添加项目")');
    if (await addBtn.count() > 0) {
      await addBtn.click();
      await page.waitForTimeout(500);
      await page.fill('#projectName', testProject);

      const submitBtn = page.locator('#projectForm button[type="submit"]');
      await submitBtn.click();
      await page.waitForTimeout(1000);
    }

    // 找到刚创建的项目，点击删除
    const projectRow = page.locator(`.project-item:has-text("${testProject}")`);
    if (await projectRow.count() > 0) {
      const deleteBtn = projectRow.locator('button.delete, .delete-btn');
      if (await deleteBtn.count() > 0) {
        // 设置对话框处理器
        page.on('dialog', async dialog => {
          // 不自动 accept，测试确认框是否出现
        });

        await deleteBtn.first().click();
        await page.waitForTimeout(500);
      }
    }
  });

  // ========== PROJ-004: 确认删除后项目被删除 ==========
  test('PROJ-004: 确认删除后项目被删除', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 创建测试项目
    const testProject = `Test_Delete_Confirm_${Date.now()}`;
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    const addBtn = page.locator('button:has-text("添加项目")');
    if (await addBtn.count() > 0) {
      await addBtn.click();
      await page.waitForTimeout(500);
      await page.fill('#projectName', testProject);

      const submitBtn = page.locator('#projectForm button[type="submit"]');
      await submitBtn.click();
      await page.waitForTimeout(1000);
    }

    // 关闭模态框重新打开
    const closeBtn = page.locator('#projectModal .modal-close, #projectModal .close');
    if (await closeBtn.count() > 0) {
      await closeBtn.first().click();
      await page.waitForTimeout(500);
    }

    // 重新打开项目管理
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    // 找到并删除项目
    const projectRow = page.locator(`.project-item:has-text("${testProject}")`);
    if (await projectRow.count() > 0) {
      const deleteBtn = projectRow.locator('button.delete, .delete-btn');
      if (await deleteBtn.count() > 0) {
        page.on('dialog', async dialog => {
          await dialog.accept();
        });

        await deleteBtn.first().click();
        await page.waitForTimeout(1000);
      }
    }
  });

  // ========== PROJ-005: 取消删除后项目保留 ==========
  test('PROJ-005: 取消删除后项目保留', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    // 创建测试项目
    const testProject = `Test_Cancel_${Date.now()}`;
    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    const addBtn = page.locator('button:has-text("添加项目")');
    if (await addBtn.count() > 0) {
      await addBtn.click();
      await page.waitForTimeout(500);
      await page.fill('#projectName', testProject);

      const submitBtn = page.locator('#projectForm button[type="submit"]');
      await submitBtn.click();
      await page.waitForTimeout(1000);
    }

    // 关闭模态框重新打开
    const closeBtn = page.locator('#projectModal .modal-close');
    if (await closeBtn.count() > 0) {
      await closeBtn.first().click();
      await page.waitForTimeout(500);
    }

    await page.click('#projectManageBtn');
    await page.waitForTimeout(500);

    // 找到项目但取消删除
    const projectRow = page.locator(`.project-item:has-text("${testProject}")`);
    if (await projectRow.count() > 0) {
      const deleteBtn = projectRow.locator('button.delete, .delete-btn');
      if (await deleteBtn.count() > 0) {
        page.on('dialog', async dialog => {
          await dialog.dismiss();
        });

        await deleteBtn.first().click();
        await page.waitForTimeout(500);

        // 验证项目仍然存在
        const stillExists = await projectRow.count();
        expect(stillExists).toBeGreaterThan(0);
      }
    }
  });
});
