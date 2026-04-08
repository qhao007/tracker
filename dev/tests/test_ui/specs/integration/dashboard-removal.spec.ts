/**
 * Dashboard Component Removal UI Tests - v0.12.0
 *
 * 测试 Dashboard 概览页中已去除的组件不再显示：
 * - UI-REMOVE-001: 总CP卡片已去除
 * - UI-REMOVE-002: 覆盖率卡片已去除
 * - UI-REMOVE-003: Feature分布图已去除
 * - UI-REMOVE-004: Top5未覆盖已去除
 * - UI-REMOVE-005: Recent Activity已去除
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/dashboard-removal.spec.ts --project=firefox
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
 * 切换到 Dashboard 概览 Tab
 */
async function openOverviewTab(page: any) {
    await page.click('#dashboardTab');
    await page.waitForTimeout(1500);
}

test.describe('Dashboard Component Removal UI Tests', () => {

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
        await selectSOCDVProject(page);
        await openOverviewTab(page);
    });

    /**
     * UI-REMOVE-001: 去除总CP卡片 - 概览页不再显示"Total CP"标签的卡片
     *
     * v0.12.0 变更: 总CP卡片被移除，替换为"Covered"卡片(显示X/Y格式)
     */
    test('UI-REMOVE-001: 去除总CP卡片 - 概览页不再显示"Total CP"标签', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证概览卡片容器存在
        const overviewContainer = page.locator('#dashboard-overview');
        await expect(overviewContainer).toBeVisible();

        // 验证有3张概览卡片（新版本）
        const overviewCards = page.locator('.overview-card');
        const cardCount = await overviewCards.count();
        expect(cardCount).toBe(3);

        // 验证卡片标签不包含 "Total CP"（说明总CP卡片已去除）
        const labels = await page.locator('.overview-label').allTextContents();
        expect(labels).not.toContain('Total CP');

        // 验证新卡片标签为 Covered, Unlinked, TC Pass Rate
        expect(labels).toContain('Covered');
        expect(labels).toContain('Unlinked');
        expect(labels).toContain('TC Pass Rate');
    });

    /**
     * UI-REMOVE-002: 去除覆盖率卡片 - 概览页不再显示独立的"Coverage"百分比卡片
     *
     * v0.12.0 变更: 覆盖率卡片被移除，TC通过率卡片替代
     */
    test('UI-REMOVE-002: 去除覆盖率卡片 - 概览页不再显示独立的"Coverage"标签', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证概览卡片
        const overviewCards = page.locator('.overview-card');
        const cardCount = await overviewCards.count();
        expect(cardCount).toBe(3);

        // 验证标签不包含 "Coverage"（说明覆盖率卡片已去除）
        const labels = await page.locator('.overview-label').allTextContents();
        expect(labels).not.toContain('Coverage');

        // 验证标签为 Covered, Unlinked, TC Pass Rate
        expect(labels).toContain('Covered');
        expect(labels).toContain('Unlinked');
        expect(labels).toContain('TC Pass Rate');
    });

    /**
     * UI-REMOVE-003: 去除Feature分布图 - 概览页不再显示独立的Feature分布横向柱状图
     *
     * v0.12.0 变更: 独立的Feature分布图被Feature×Priority矩阵替代
     * 注意: 矩阵预览(#matrix-preview)中的feature-bar-item是新的预览组件，应该存在
     */
    test('UI-REMOVE-003: 去除Feature分布图 - 概览页不再显示独立的Feature分布图', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证 #feature-chart 不存在（独立的Feature分布图已去除）
        const featureChart = page.locator('#feature-chart');
        const chartCount = await featureChart.count();
        expect(chartCount).toBe(0);

        // 验证没有 "Feature Coverage Distribution" 标题（在概览区域）
        const dashboardOverview = page.locator('#dashboard-overview');
        const chartTitle = dashboardOverview.locator('.chart-title:has-text("Feature Coverage Distribution")');
        await expect(chartTitle).not.toBeVisible();

        // 注意: matrix-preview 中的 feature-bar-item 是新组件，这是预期的
        // 我们验证 matrix-preview 存在并显示 Top 4 Features
        const matrixPreview = page.locator('#matrix-preview');
        if (await matrixPreview.isVisible()) {
            const previewTitle = matrixPreview.locator('.summary-card-title');
            await expect(previewTitle).toContainText('Matrix Preview');
        }
    });

    /**
     * UI-REMOVE-004: 去除Top5未覆盖 - 概览页不再显示Top 5 Uncovered CP列表
     *
     * v0.12.0 变更: Top 5 Uncovered被空洞看板替代
     */
    test('UI-REMOVE-004: 去除Top5未覆盖 - 概览页不再显示Top 5 Uncovered CP', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证 #top-uncovered 不存在或不可见（Top 5已去除）
        const topUncovered = page.locator('#top-uncovered');
        await expect(topUncovered).not.toBeVisible();

        // 验证没有 "Top 5 Uncovered CPs" 标题
        const sectionTitle = page.locator('.list-card .chart-title:has-text("Top 5 Uncovered CPs")');
        await expect(sectionTitle).not.toBeVisible();
    });

    /**
     * UI-REMOVE-005: 去除Recent Activity - 概览页不再显示Recent Activity列表
     *
     * v0.12.0 变更: Recent Activity从概览页移除，移至页面底部
     */
    test('UI-REMOVE-005: 去除Recent Activity - 概览页不再显示Recent Activity', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证 #recent-activity 不存在于概览页的 dashboard-overview 或 dashboard-content 内
        // 注意: #recent-activity 可能存在于页面底部，所以我们只检查概览相关内容
        const dashboardContent = page.locator('#dashboard-content');
        const recentActivityInDashboard = dashboardContent.locator('#recent-activity');
        await expect(recentActivityInDashboard).not.toBeVisible();

        // 验证概览页内没有 "Recent Activity" 标题
        const dashboardOverview = page.locator('#dashboard-overview');
        const recentActivityTitle = dashboardOverview.locator('.chart-title:has-text("Recent Activity")');
        await expect(recentActivityTitle).not.toBeVisible();
    });

    /**
     * UI-REMOVE-BONUS: 验证Priority分布卡也已去除（v0.12.0规格说明中提到的）
     */
    test('UI-REMOVE-BONUS: 去除Priority分布卡 - 概览页不再显示Priority分布卡片', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证 #priority-cards 不存在或不可见
        const priorityCards = page.locator('#priority-cards');
        await expect(priorityCards).not.toBeVisible();

        // 验证没有 P0/P1/P2 Priority 标签
        const priorityLabels = page.locator('.priority-label');
        const labelCount = await priorityLabels.count();
        expect(labelCount).toBe(0);
    });
});
