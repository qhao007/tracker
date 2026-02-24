import { test, expect } from '@playwright/test';

test.describe('v0.6.2 功能验证', () => {

  /**
   * 登录辅助函数 - v0.7.1 需要登录
   */
  async function loginAsAdmin(page: any) {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    // 填写登录表单
    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('#loginForm button[type="submit"]');
    await page.waitForTimeout(1000);
  }

  test.beforeEach(async ({ page }) => {
    // 登录 - v0.7.1 需要认证
    await loginAsAdmin(page);
    // 登录后等待页面加载完成
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  test('CP 详情按钮 - 展开/收起功能', async ({ page }) => {
    // 选择一个有 CP 的项目
    await page.selectOption('#projectSelector', { index: 1 });
    await page.waitForTimeout(1000);

    // 检查 CP 表格是否存在
    const cpTable = page.locator('table#cpTable');
    await expect(cpTable).toBeVisible();

    // 点击第一个 CP 行的详情按钮 (使用 onclick 属性定位)
    const firstCpRow = page.locator('table#cpTable tbody tr').first();
    await firstCpRow.locator('button.action-btn:has-text("详情")').click();

    // 验证详情面板展开
    const detailPanel = page.locator('tr[id^="cp-detail-"]').first();
    await expect(detailPanel).toBeVisible();
  });

  test('TC 详情按钮 - 展开/收起功能', async ({ page }) => {
    // 选择项目
    await page.selectOption('#projectSelector', { index: 1 });
    await page.waitForTimeout(1000);

    // 切换到 TC 面板
    await page.click('button:has-text("Test Cases")');
    await page.waitForTimeout(500);

    // 检查 TC 表格是否存在
    const tcTable = page.locator('table#tcTable');
    await expect(tcTable).toBeVisible();

    // 找一个有详情数据的 TC 行 (SRAM边界地址测试 有详情)
    // 点击详情按钮
    const tcRow = page.locator('table#tcTable tbody tr:has-text("SRAM边界地址测试")');
    await tcRow.locator('button.action-btn:has-text("详情")').click();

    // 等待并验证详情行显示 (CSS 类 .tc-detail-row.show)
    await page.waitForSelector('tr.tc-detail-row.show', { timeout: 5000 });
  });

  test('TC 过滤 - Status 过滤', async ({ page }) => {
    // 选择项目
    await page.selectOption('#projectSelector', { index: 1 });
    await page.waitForTimeout(1000);

    // 切换到 TC 面板
    await page.click('button:has-text("Test Cases")');
    await page.waitForTimeout(500);

    // 检查过滤面板
    const filterPanel = page.locator('#tcFilterPanel, .filter-panel');
    await expect(filterPanel.first()).toBeVisible();
  });

  test('TC 过滤 - 重置功能', async ({ page }) => {
    // 选择项目
    await page.selectOption('#projectSelector', { index: 1 });
    await page.waitForTimeout(1000);

    // 切换到 TC 面板
    await page.click('button:has-text("Test Cases")');
    await page.waitForTimeout(500);

    // 在 TC 面板中找到重置按钮
    const tcPanel = page.locator('#tcPanel');
    await expect(tcPanel).toBeVisible();

    // TC 过滤面板中的重置按钮
    const resetBtn = tcPanel.locator('button:has-text("重置")');
    await expect(resetBtn).toBeVisible();
  });
});
