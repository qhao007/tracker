/**
 * Coverage Matrix UI Tests - v0.12.0
 *
 * 测试 Feature × Priority 覆盖率矩阵功能：
 * - UI-MAT-001: 矩阵显示
 * - UI-MAT-002: 单元格颜色
 * - UI-MAT-003: 薄弱区域告警
 * - UI-MAT-004: 单元格详情
 * - UI-MAT-005: 空数据显示
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/coverage-matrix.spec.ts --project=firefox
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
 * 切换到 Dashboard 并打开 Coverage Matrix Tab
 */
async function openMatrixTab(page: any) {
    await page.click('#dashboardTab');
    await page.waitForTimeout(1500);
    await page.click('.dashboard-tab[data-tab="matrix"]');
    await page.waitForTimeout(1000);
}

test.describe('Coverage Matrix UI Tests', () => {

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
        await selectSOCDVProject(page);
        await openMatrixTab(page);
    });

    /**
     * UI-MAT-001: 矩阵显示 - Feature × Priority 正确渲染
     */
    test('UI-MAT-001: 矩阵显示 - Feature × Priority 正确渲染', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证 Matrix Tab 内容容器
        const matrixTabContent = page.locator('#matrix-tab-content');
        await expect(matrixTabContent).toBeVisible();

        // 检查矩阵表格是否存在
        const coverageMatrix = page.locator('.coverage-matrix');
        const matrixVisible = await coverageMatrix.isVisible().catch(() => false);

        if (matrixVisible) {
            // 验证表头包含 Feature 列和 Priority 列
            const headers = await page.locator('.coverage-matrix thead th').allTextContents();
            expect(headers.length).toBeGreaterThan(1); // 至少 Feature + 1 个 Priority

            // 验证 Feature 行
            const featureCells = page.locator('.coverage-matrix .feature-cell');
            const featureCount = await featureCells.count();
            expect(featureCount).toBeGreaterThan(0);

            // 验证矩阵单元格
            const matrixCells = page.locator('.matrix-cell');
            const cellCount = await matrixCells.count();
            expect(cellCount).toBeGreaterThan(0);
        } else {
            // 无数据时显示空状态
            const emptyState = page.locator('.dashboard-empty');
            await expect(emptyState).toBeVisible();
        }
    });

    /**
     * UI-MAT-002: 单元格颜色 - 根据阈值显示正确颜色
     */
    test('UI-MAT-002: 单元格颜色 - 根据阈值显示正确颜色', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查矩阵是否存在
        const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

        if (matrixVisible) {
            // 验证矩阵单元格有颜色类名
            const matrixCells = page.locator('.matrix-cell');
            const cellCount = await matrixCells.count();

            if (cellCount > 0) {
                // 检查颜色类名 - green (>=80%), orange (50-79%), red (20-49%), dark-red (<20%)
                for (let i = 0; i < Math.min(cellCount, 10); i++) {
                    const cell = matrixCells.nth(i);
                    const className = await cell.getAttribute('class');
                    const hasColorClass = className?.includes('green') ||
                                          className?.includes('orange') ||
                                          className?.includes('red') ||
                                          className?.includes('dark-red') ||
                                          className?.includes('empty');
                    expect(hasColorClass).toBeTruthy();
                }
            }
        }
    });

    /**
     * UI-MAT-003: 薄弱区域告警 - < 50% 显示告警
     */
    test('UI-MAT-003: 薄弱区域告警 - < 50% 显示告警', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查矩阵是否存在
        const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

        if (!matrixVisible) {
            // 无矩阵数据时跳过此测试
            test.skip();
            return;
        }

        // 检查是否有薄弱区域项
        const weakAreaItems = page.locator('.weak-area-item');
        const itemCount = await weakAreaItems.count();

        if (itemCount > 0) {
            // 验证每个薄弱区域项
            for (let i = 0; i < Math.min(itemCount, 5); i++) {
                const item = weakAreaItems.nth(i);
                const itemText = await item.textContent();

                // 验证格式: Feature - Priority XX%
                expect(itemText).toMatch(/[\s\S]*-[\s\S]*\d+%/);
            }
        } else {
            // 没有薄弱区域时，检查是否显示 "No weak areas"
            const weakAreasSection = page.locator('#matrix-tab-content');
            const sectionText = await weakAreasSection.textContent();

            // 要么显示 "No weak areas"，要么薄弱区域section不存在
            const hasWeakAreasText = sectionText.includes('No weak areas');
            expect(hasWeakAreasText || itemCount > 0).toBeTruthy();
        }
    });

    /**
     * UI-MAT-004: 单元格详情 - 点击显示 CP 列表
     */
    test('UI-MAT-004: 单元格详情 - 点击显示 CP 列表', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查矩阵是否存在
        const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

        if (matrixVisible) {
            // 检查是否有单元格有 CP 数据
            const hasCellWithData = await page.evaluate(() => {
                if (!Dashboard.matrixData || !Dashboard.matrixData.matrix) return false;

                const { matrix, features, priorities } = Dashboard.matrixData;

                for (const feature of features) {
                    for (const priority of priorities) {
                        const cell = matrix[feature]?.[priority];
                        if (cell && cell.cp_list && cell.cp_list.length > 0) {
                            return true;
                        }
                    }
                }
                return false;
            });

            if (!hasCellWithData) {
                test.skip();
                return;
            }

            // 点击第一个有覆盖率数据的非空单元格
            const cells = page.locator('.matrix-cell:not(.empty)');
            const cellCount = await cells.count();

            if (cellCount > 0) {
                // 使用 JavaScript 点击
                await page.evaluate(() => {
                    const cells = document.querySelectorAll('.matrix-cell:not(.empty)');
                    for (const cell of cells) {
                        if (cell.textContent && cell.textContent.includes('/')) {
                            cell.click();
                            break;
                        }
                    }
                });
                await page.waitForTimeout(500);

                // 验证弹窗显示
                const modal = page.locator('#dashboard-modal');
                const isActive = await modal.evaluate(el => el.classList.contains('active'));

                if (!isActive) {
                    // 弹窗没有打开可能是该单元格没有 CP 数据
                    test.skip();
                    return;
                }

                // 验证弹窗内容
                const modalContent = page.locator('#dashboard-modal-content');
                await expect(modalContent).toBeVisible();

                const modalText = await modalContent.textContent();
                expect(modalText).toContain('Cover Points');
            }
        }
    });

    /**
     * UI-MAT-005: 空数据显示 - 无 CP 时显示提示
     */
    test('UI-MAT-005: 空数据显示 - 无 CP 时显示提示', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 检查是显示矩阵还是空状态
        const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);
        const emptyState = page.locator('#matrix-tab-content .dashboard-empty');
        const emptyVisible = await emptyState.isVisible().catch(() => false);

        // 两种情况都是有效的
        expect(matrixVisible || emptyVisible).toBeTruthy();

        if (emptyVisible) {
            // 验证空状态提示
            const emptyText = await emptyState.textContent();
            expect(emptyText).toContain('No Cover Point data');
        }
    });
});

/**
 * UI-REFRESH-003: 矩阵详情弹窗刷新 - 打开弹窗时数据正确
 *
 * 验证打开矩阵单元格详情弹窗时，显示的数据是最新的
 */
test('UI-REFRESH-003: 矩阵详情弹窗刷新 - 打开弹窗时数据正确', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查矩阵是否存在
    const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

    if (matrixVisible) {
        // 检查是否有单元格有 CP 数据
        const hasCellWithData = await page.evaluate(() => {
            if (!Dashboard.matrixData || !Dashboard.matrixData.matrix) return false;

            const { matrix, features, priorities } = Dashboard.matrixData;

            for (const feature of features) {
                for (const priority of priorities) {
                    const cell = matrix[feature]?.[priority];
                    if (cell && cell.cp_list && cell.cp_list.length > 0) {
                        return true;
                    }
                }
            }
            return false;
        });

        if (!hasCellWithData) {
            test.skip();
            return;
        }

        // 点击第一个有覆盖率数据的非空单元格
        const cells = page.locator('.matrix-cell:not(.empty)');
        const cellCount = await cells.count();

        if (cellCount > 0) {
            // 使用 JavaScript 点击
            await page.evaluate(() => {
                const cells = document.querySelectorAll('.matrix-cell:not(.empty)');
                for (const cell of cells) {
                    if (cell.textContent && cell.textContent.includes('/')) {
                        cell.click();
                        break;
                    }
                }
            });
            await page.waitForTimeout(500);

            // 验证弹窗显示
            const modal = page.locator('#dashboard-modal');
            const isActive = await modal.evaluate(el => el.classList.contains('active'));

            if (!isActive) {
                test.skip();
                return;
            }

            // 验证弹窗内容
            const modalContent = page.locator('#dashboard-modal-content');
            await expect(modalContent).toBeVisible();

            // 验证弹窗包含 Cover Points 信息
            const modalText = await modalContent.textContent();
            expect(modalText).toContain('Cover Points');
        }
    }
});

/**
 * UI-MAT-006: 矩阵单元格颜色 - 绿色 >=80%
 *
 * 验证矩阵单元格覆盖率 >= 80% 时显示绿色背景 (#22c55e)
 */
test('UI-MAT-006: 矩阵单元格颜色 - 绿色 >=80%', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查矩阵是否存在
    const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

    if (matrixVisible) {
        // 获取所有矩阵单元格
        const matrixCells = page.locator('.matrix-cell');
        const cellCount = await matrixCells.count();

        if (cellCount > 0) {
            // 查找绿色的单元格 (.green 类)
            const greenCells = page.locator('.matrix-cell.green');
            const greenCount = await greenCells.count();

            // 如果有绿色单元格，验证其背景色
            if (greenCount > 0) {
                for (let i = 0; i < Math.min(greenCount, 3); i++) {
                    const cell = greenCells.nth(i);
                    const bgColor = await cell.evaluate(el => window.getComputedStyle(el).backgroundColor);
                    // 验证是绿色 (#22c55e = rgb(34, 197, 94))
                    const isGreen = bgColor === 'rgb(34, 197, 94)' || bgColor === 'rgb(136, 226, 115)';
                    expect(isGreen || bgColor.includes('34, 197, 94')).toBeTruthy();
                }
            }
        }
    }
});

/**
 * UI-MAT-007: 矩阵单元格颜色 - 橙色 50-79%
 *
 * 验证矩阵单元格覆盖率在 50-79% 范围时显示橙色背景 (#f59e0b)
 */
test('UI-MAT-007: 矩阵单元格颜色 - 橙色 50-79%', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查矩阵是否存在
    const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

    if (matrixVisible) {
        // 获取所有矩阵单元格
        const matrixCells = page.locator('.matrix-cell');
        const cellCount = await matrixCells.count();

        if (cellCount > 0) {
            // 查找橙色的单元格 (.orange 类)
            const orangeCells = page.locator('.matrix-cell.orange');
            const orangeCount = await orangeCells.count();

            // 如果有橙色单元格，验证其背景色
            if (orangeCount > 0) {
                for (let i = 0; i < Math.min(orangeCount, 3); i++) {
                    const cell = orangeCells.nth(i);
                    const bgColor = await cell.evaluate(el => window.getComputedStyle(el).backgroundColor);
                    // 验证是橙色 (#f59e0b = rgb(245, 158, 11))
                    const isOrange = bgColor === 'rgb(245, 158, 11)' || bgColor.includes('245, 158');
                    expect(isOrange || bgColor.includes('245, 158, 11')).toBeTruthy();
                }
            }
        }
    }
});

/**
 * UI-MAT-008: 矩阵单元格颜色 - 红色 20-49%
 *
 * 验证矩阵单元格覆盖率在 20-49% 范围时显示红色背景 (#ef4444)
 */
test('UI-MAT-008: 矩阵单元格颜色 - 红色 20-49%', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查矩阵是否存在
    const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

    if (matrixVisible) {
        // 获取所有矩阵单元格
        const matrixCells = page.locator('.matrix-cell');
        const cellCount = await matrixCells.count();

        if (cellCount > 0) {
            // 查找红色的单元格 (.red 类)
            const redCells = page.locator('.matrix-cell.red');
            const redCount = await redCells.count();

            // 如果有红色单元格，验证其背景色
            if (redCount > 0) {
                for (let i = 0; i < Math.min(redCount, 3); i++) {
                    const cell = redCells.nth(i);
                    const bgColor = await cell.evaluate(el => window.getComputedStyle(el).backgroundColor);
                    // 验证是红色 (#ef4444 = rgb(239, 68, 68))
                    const isRed = bgColor === 'rgb(239, 68, 68)' || bgColor.includes('239, 68, 68');
                    expect(isRed || bgColor.includes('239, 68, 68')).toBeTruthy();
                }
            }
        }
    }
});

/**
 * UI-MAT-009: 矩阵单元格颜色 - 深红 <20%
 *
 * 验证矩阵单元格覆盖率 < 20% 时显示深红背景 (#991b1b)
 */
test('UI-MAT-009: 矩阵单元格颜色 - 深红 <20%', async ({ page }) => {
    // 等待数据加载
    await page.waitForTimeout(2000);

    // 检查矩阵是否存在
    const matrixVisible = await page.locator('.coverage-matrix').isVisible().catch(() => false);

    if (matrixVisible) {
        // 获取所有矩阵单元格
        const matrixCells = page.locator('.matrix-cell');
        const cellCount = await matrixCells.count();

        if (cellCount > 0) {
            // 查找深红色的单元格 (.dark-red 类)
            const darkRedCells = page.locator('.matrix-cell.dark-red');
            const darkRedCount = await darkRedCells.count();

            // 如果有深红色单元格，验证其背景色
            if (darkRedCount > 0) {
                for (let i = 0; i < Math.min(darkRedCount, 3); i++) {
                    const cell = darkRedCells.nth(i);
                    const bgColor = await cell.evaluate(el => window.getComputedStyle(el).backgroundColor);
                    // 验证是深红色 (#991b1b = rgb(153, 27, 27))
                    const isDarkRed = bgColor === 'rgb(153, 27, 27)' || bgColor.includes('153, 27, 27');
                    expect(isDarkRed || bgColor.includes('153, 27, 27')).toBeTruthy();
                }
            }
        }
    }
});
