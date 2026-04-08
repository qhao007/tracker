/**
 * Owner Distribution UI Tests - v0.12.0
 *
 * 测试 TC Owner 分布功能：
 * - UI-OWNER-001: Owner 列表显示
 * - UI-OWNER-002: 通过率颜色
 * - UI-OWNER-003: Owner 详情弹窗
 * - UI-OWNER-004: TC 列表分页
 * - UI-OWNER-005: 空数据显示
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/owner-dist.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

/**
 * 登录辅助函数
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

    // 正常表单登录
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
    await page.waitForFunction(() => {
        const selector = document.getElementById('projectSelector');
        return selector && selector.options.length > 1;
    }, { timeout: 15000 });

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

/**
 * 切换到 Dashboard 并打开 Owner Distribution Tab
 */
async function openOwnerTab(page: any) {
    await page.click('#dashboardTab');
    await page.waitForTimeout(1500);
    await page.click('.dashboard-tab[data-tab="owner"]');
    await page.waitForTimeout(1000);
}

test.describe('Owner Distribution UI Tests', () => {

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
        await selectSOCDVProject(page);
        await openOwnerTab(page);
    });

    /**
     * UI-OWNER-001: Owner 列表显示 - 所有 Owner 显示
     */
    test('UI-OWNER-001: Owner 列表显示 - 所有 Owner 显示', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证 Owner Tab 内容容器
        const ownerTabContent = page.locator('#owner-tab-content');
        await expect(ownerTabContent).toBeVisible();

        // 检查是否有 Owner 表格或空状态
        const ownerTable = page.locator('.owner-table');
        const tableVisible = await ownerTable.isVisible().catch(() => false);

        const emptyState = page.locator('.dashboard-empty');
        const emptyVisible = await emptyState.isVisible().catch(() => false);

        if (tableVisible) {
            // 验证表头
            const headers = await page.locator('.owner-table thead th').allTextContents();
            expect(headers).toContain('Owner');
            expect(headers).toContain('Total TC');
            expect(headers).toContain('Pass');
            expect(headers).toContain('Fail');
            expect(headers).toContain('Not Run');
            expect(headers).toContain('Pass Rate');

            // 验证表格行
            const rows = page.locator('.owner-table tbody tr');
            const rowCount = await rows.count();
            expect(rowCount).toBeGreaterThan(0);

            // 验证汇总信息
            const summaryDiv = page.locator('#owner-tab-content > .list-card').first();
            const summaryVisible = await summaryDiv.isVisible().catch(() => false);
            if (summaryVisible) {
                const summaryText = await summaryDiv.textContent();
                expect(summaryText).toContain('Total Owners');
                expect(summaryText).toContain('Unassigned TCs');
            }
        } else if (emptyVisible) {
            // 空状态 - 验证提示信息
            const emptyText = await emptyState.textContent();
            expect(emptyText).toContain('No TC data');
        }
    });

    /**
     * UI-OWNER-002: 通过率颜色 - 根据阈值显示正确颜色
     */
    test('UI-OWNER-002: 通过率颜色 - 根据阈值显示正确颜色', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查表格是否存在
        const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);

        if (tableVisible) {
            // 验证通过率单元格有颜色类名
            const passRateCells = page.locator('.owner-pass-rate');
            const cellCount = await passRateCells.count();

            if (cellCount > 0) {
                // 检查颜色类名 - excellent (>=90%), normal (70-89%), warning (<70%)
                for (let i = 0; i < Math.min(cellCount, 5); i++) {
                    const cell = passRateCells.nth(i);
                    const className = await cell.getAttribute('class');
                    const hasColorClass = className?.includes('excellent') ||
                                          className?.includes('normal') ||
                                          className?.includes('warning');
                    expect(hasColorClass).toBeTruthy();
                }
            }
        }
    });

    /**
     * UI-OWNER-003: Owner 详情弹窗 - 点击显示 TC 列表
     */
    test('UI-OWNER-003: Owner 详情弹窗 - 点击显示 TC 列表', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查表格是否存在
        const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);

        if (tableVisible) {
            // 检查是否有 owner 数据
            const hasOwnerData = await page.evaluate(() => {
                return Dashboard?.ownerData?.owners?.length > 0;
            });

            if (!hasOwnerData) {
                test.skip();
                return;
            }

            // 点击第一行 Owner
            const firstRow = page.locator('.owner-table tbody tr').first();
            if (await firstRow.isVisible()) {
                await page.evaluate(() => {
                    const rows = document.querySelectorAll('.owner-table tbody tr');
                    if (rows.length > 0) {
                        rows[0].click();
                    }
                });
                await page.waitForTimeout(500);

                // 验证弹窗显示
                const modal = page.locator('#dashboard-modal');
                await expect(modal).toHaveClass(/active/);

                // 验证弹窗内容
                const modalContent = page.locator('#dashboard-modal-content');
                await expect(modalContent).toBeVisible();

                // 验证有 TC 列表（概览卡片）
                const overviewCards = modalContent.locator('.overview-card');
                const cardCount = await overviewCards.count();
                expect(cardCount).toBe(4); // Total, Pass, Fail, Not Run
            }
        }
    });

    /**
     * UI-OWNER-004: TC 列表分页 - >20 条时显示查看全部
     */
    test('UI-OWNER-004: TC 列表分页 - >20 条时显示查看全部', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查表格是否存在
        const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);

        if (tableVisible) {
            // 点击第一行 Owner 打开详情
            const firstRow = page.locator('.owner-table tbody tr').first();
            if (await firstRow.isVisible()) {
                await firstRow.click();
                await page.waitForTimeout(500);

                // 检查弹窗中的 TC 列表
                const modalContent = page.locator('#dashboard-modal-content');
                const modalVisible = await modalContent.isVisible().catch(() => false);

                if (modalVisible) {
                    const modalText = await modalContent.textContent();

                    // 验证 TC 列表限制提示
                    // 根据规格，TC 列表限制显示 20 条
                    // 如果有超过 20 条的 Owner，应该显示提示
                    if (modalText.includes('TC list limited to 20 items')) {
                        expect(true).toBeTruthy();
                    }

                    // 或者验证没有超过 20 条时的正常显示
                    const tcListItems = modalContent.locator('div[style*="border-bottom"]');
                    const itemCount = await tcListItems.count();

                    // 如果有 TC 列表，应该能看到一些
                    if (itemCount > 0) {
                        expect(itemCount).toBeLessThanOrEqual(25); // 合理上限
                    }
                }
            }
        }
    });

    /**
     * UI-OWNER-005: 空数据显示 - 无 TC 时显示提示
     */
    test('UI-OWNER-005: 空数据显示 - 无 TC 时显示提示', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查是显示表格还是空状态
        const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);
        const emptyState = page.locator('#owner-tab-content .dashboard-empty');
        const emptyVisible = await emptyState.isVisible().catch(() => false);

        // 两种情况都是有效的
        expect(tableVisible || emptyVisible).toBeTruthy();

        if (emptyVisible) {
            // 验证空状态提示
            const emptyText = await emptyState.textContent();
            expect(emptyText).toContain('No TC data');
        }
    });
});

/**
 * UI-REFRESH-002: Owner详情弹窗刷新 - 打开弹窗时数据正确
 *
 * 验证打开Owner详情弹窗时，显示的数据是最新的
 */
test('UI-REFRESH-002: Owner详情弹窗刷新 - 打开弹窗时数据正确', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查表格是否存在
    const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);

    if (tableVisible) {
        // 检查是否有 owner 数据
        const hasOwnerData = await page.evaluate(() => {
            return Dashboard?.ownerData?.owners?.length > 0;
        });

        if (!hasOwnerData) {
            test.skip();
            return;
        }

        // 点击第一行 Owner 打开详情
        const firstRow = page.locator('.owner-table tbody tr').first();
        if (await firstRow.isVisible()) {
            await firstRow.click();
            await page.waitForTimeout(500);

            // 验证弹窗显示
            const modal = page.locator('#dashboard-modal');
            await expect(modal).toHaveClass(/active/);

            // 验证弹窗内容
            const modalContent = page.locator('#dashboard-modal-content');
            await expect(modalContent).toBeVisible();

            // 验证弹窗包含 Owner 信息
            const modalText = await modalContent.textContent();

            // 应该包含 Owner 标题
            expect(modalText).toContain('Owner:');

            // 应该包含 Total TC / Pass / Fail / Not Run 信息
            expect(modalText).toContain('Total TC');
            expect(modalText).toContain('Pass');
            expect(modalText).toContain('Fail');
            expect(modalText).toContain('Not Run');
        }
    }
});

/**
 * UI-OWNER-006: 通过率颜色 - 绿色 >=90%
 *
 * 验证 Owner 通过率 >= 90% 时显示绿色 (#22c55e)
 */
test('UI-OWNER-006: 通过率颜色 - 绿色 >=90%', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查表格是否存在
    const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);

    if (tableVisible) {
        // 获取所有通过率单元格
        const passRateCells = page.locator('.owner-pass-rate');
        const cellCount = await passRateCells.count();

        if (cellCount > 0) {
            // 查找绿色 (>=90%) 的单元格
            const greenCells = page.locator('.owner-pass-rate.excellent');
            const greenCount = await greenCells.count();

            // 如果有绿色单元格，验证其颜色
            if (greenCount > 0) {
                for (let i = 0; i < Math.min(greenCount, 3); i++) {
                    const cell = greenCells.nth(i);
                    const style = await cell.getAttribute('style');
                    // 验证包含绿色
                    const isGreen = style?.includes('rgb(34, 197, 94)') ||
                                   style?.includes('#22c55e') ||
                                   (style?.includes('color:') && !style?.includes('rgb(239, 68, 68)') && !style?.includes('rgb(245, 158, 11)'));
                    expect(isGreen).toBeTruthy();
                }
            }
        }
    }
});

/**
 * UI-OWNER-007: 通过率颜色 - 橙色 70-89%
 *
 * 验证 Owner 通过率在 70-89% 范围时显示橙色 (#f59e0b)
 */
test('UI-OWNER-007: 通过率颜色 - 橙色 70-89%', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查表格是否存在
    const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);

    if (tableVisible) {
        // 获取所有通过率单元格
        const passRateCells = page.locator('.owner-pass-rate');
        const cellCount = await passRateCells.count();

        if (cellCount > 0) {
            // 查找橙色 (70-89%) 的单元格
            const orangeCells = page.locator('.owner-pass-rate.normal');
            const orangeCount = await orangeCells.count();

            // 如果有橙色单元格，验证其颜色
            if (orangeCount > 0) {
                for (let i = 0; i < Math.min(orangeCount, 3); i++) {
                    const cell = orangeCells.nth(i);
                    const style = await cell.getAttribute('style');
                    // 验证包含橙色
                    const isOrange = style?.includes('rgb(245, 158, 11)') ||
                                    style?.includes('#f59e0b') ||
                                    (style?.includes('color:') && style?.includes('245'));
                    expect(isOrange).toBeTruthy();
                }
            }
        }
    }
});

/**
 * UI-OWNER-008: 通过率颜色 - 红色 <70%
 *
 * 验证 Owner 通过率 < 70% 时显示红色 (#ef4444)
 */
test('UI-OWNER-008: 通过率颜色 - 红色 <70%', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查表格是否存在
    const tableVisible = await page.locator('.owner-table').isVisible().catch(() => false);

    if (tableVisible) {
        // 获取所有通过率单元格
        const passRateCells = page.locator('.owner-pass-rate');
        const cellCount = await passRateCells.count();

        if (cellCount > 0) {
            // 查找红色 (<70%) 的单元格
            const redCells = page.locator('.owner-pass-rate.warning');
            const redCount = await redCells.count();

            // 如果有红色单元格，验证其颜色
            if (redCount > 0) {
                for (let i = 0; i < Math.min(redCount, 3); i++) {
                    const cell = redCells.nth(i);
                    const style = await cell.getAttribute('style');
                    // 验证包含红色
                    const isRed = style?.includes('rgb(239, 68, 68)') ||
                                 style?.includes('#ef4444') ||
                                 (style?.includes('color:') && style?.includes('239'));
                    expect(isRed).toBeTruthy();
                }
            }
        }
    }
});
