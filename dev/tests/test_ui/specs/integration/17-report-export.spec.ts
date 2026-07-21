/**
 * Integration 测试 - 项目状态报告导出功能 (v0.14.3)
 *
 * 覆盖导出报告功能的 UI 交互
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/17-report-export.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

// 测试数据：使用已存在的 SOC_DV 项目 (id=3)
const TEST_PROJECT_ID = 3;
const TEST_PROJECT_NAME = 'SOC_DV';

test.describe('Integration - 项目状态报告导出功能', () => {

  /**
   * 等待项目列表加载完成
   */
  async function waitForProjectListLoaded(page: any) {
    await page.waitForSelector('#projectSelector', { state: 'visible', timeout: 10000 });
    await page.waitForFunction(() => {
      const combo = document.querySelector('#projectSelector');
      return combo && !combo.textContent.includes('加载项目中');
    }, { timeout: 10000 });
  }

  /**
   * 登录为 admin 用户
   */
  async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

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
    await waitForProjectListLoaded(page);
  }

  /**
   * 选择项目
   */
  async function selectProject(page: any, projectName: string = TEST_PROJECT_NAME) {
    await page.click('#projectSelector');
    await page.waitForTimeout(500);
    await page.selectOption('#projectSelector', { label: projectName });
    await page.waitForTimeout(1000);
  }

  // ========== UI-REPORT-001: 导出报告按钮可见 ==========
  test('UI-REPORT-001: 导出报告按钮可见', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page, TEST_PROJECT_NAME);

    // 验证导出报告按钮可见
    const exportBtn = page.locator('#exportReportBtn');
    await expect(exportBtn).toBeVisible();

    // 验证按钮文本
    const btnText = await exportBtn.textContent();
    expect(btnText).toContain('导出报告');
  });

  // ========== UI-REPORT-002: 点击导出按钮触发 .md 下载 ==========
  test('UI-REPORT-002: 点击导出按钮下载 .md 文件', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page, TEST_PROJECT_NAME);

    // 设置下载监听
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 30000 }),
      page.click('#exportReportBtn')
    ]);

    // 验证文件名包含 .md 和项目名
    const filename = download.suggestedFilename();
    expect(filename).toContain('.md');
    expect(filename.toLowerCase()).toContain(TEST_PROJECT_NAME.toLowerCase());
  });

  // ========== UI-REPORT-003: 未选择项目点击导出报告提示 ==========
  test('UI-REPORT-003: 未选择项目点击导出报告提示', async ({ page }) => {
    await loginAsAdmin(page);

    // 通过 evaluate 直接清除 currentProject，模拟未选择项目状态
    await page.evaluate(() => {
      // @ts-ignore
      currentProject = null;
      // @ts-ignore
      currentProjectId = null;
    });
    await page.waitForTimeout(500);

    // 设置对话框处理器并触发点击（使用 evaluate 避免 Playwright click 等待）
    const dialogMessage = await page.evaluate(async () => {
      return new Promise<string>((resolve) => {
        const originalAlert = window.alert;
        window.alert = (msg: string) => {
          window.alert = originalAlert;
          resolve(msg);
        };
        // 直接调用 onclick 处理器
        const btn = document.getElementById('exportReportBtn') as HTMLButtonElement;
        if (btn && btn.onclick) {
          (btn.onclick as any)();
        } else {
          resolve('');
        }
      });
    });

    // 验证提示内容
    expect(dialogMessage).toContain('请先选择一个项目');
  });

  // ========== UI-REPORT-004: 报告内容验证 ==========
  test('UI-REPORT-004: 报告内容验证', async ({ page }) => {
    await loginAsAdmin(page);
    await selectProject(page, TEST_PROJECT_NAME);

    // 设置下载监听并保存到临时路径
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 30000 }),
      page.click('#exportReportBtn')
    ]);

    // 保存下载文件到临时目录
    const downloadPath = '/tmp/report_test_' + Date.now() + '.md';
    await download.saveAs(downloadPath);

    // 读取文件内容
    const fs = require('fs');
    const content = fs.readFileSync(downloadPath, 'utf-8');

    // 验证内容包含项目名
    expect(content).toContain(TEST_PROJECT_NAME);

    // 验证包含 Markdown 标题
    expect(content).toContain('#');

    // 验证包含 CP 相关数据
    expect(content.toLowerCase()).toMatch(/cover point|cp|覆盖/);

    // 验证包含 TC 相关数据
    expect(content.toLowerCase()).toMatch(/test case|tc|测试/);

    // 清理临时文件
    try {
      fs.unlinkSync(downloadPath);
    } catch (e) {
      // 忽略清理错误
    }
  });
});
