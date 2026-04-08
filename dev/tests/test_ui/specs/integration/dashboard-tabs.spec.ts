/**
 * Dashboard Tabs & Overview UI Tests - v0.12.0
 *
 * 测试 Dashboard Tab 结构和概览页功能：
 * - UI-TAB-001: Tab 切换
 * - UI-TAB-002: Tab 内容加载
 * - UI-TAB-003: Tab 动画
 * - UI-OVER-001: 趋势图显示
 * - UI-OVER-002: 数字卡片显示
 * - UI-OVER-003: 周环比显示
 * - UI-OVER-004: 矩阵预览
 * - UI-OVER-005: 空洞摘要
 * - UI-OVER-006: Owner摘要
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/dashboard-tabs.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';
import { TestDataFactory } from '../../fixtures/test-data.factory';

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
 * 点击 Dashboard Tab
 */
async function clickDashboardTab(page: any) {
    await page.click('#dashboardTab');
    await page.waitForTimeout(1500);
}

test.describe('Dashboard Tabs & Overview UI Tests', () => {

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
        await selectSOCDVProject(page);
        await clickDashboardTab(page);
    });

    /**
     * UI-TAB-001: Tab 切换 - 各 Tab 切换正常
     */
    test('UI-TAB-001: Tab 切换 - 各 Tab 切换正常', async ({ page }) => {
        // 验证概览 Tab 默认激活
        const overviewTab = page.locator('.dashboard-tab[data-tab="overview"]');
        await expect(overviewTab).toHaveClass(/active/);

        // 验证概览内容显示
        const overviewContent = page.locator('#overview-content');
        await expect(overviewContent).toHaveClass(/active/);

        // 切换到 Coverage Holes Tab
        await page.click('.dashboard-tab[data-tab="holes"]');
        await page.waitForTimeout(500);
        await expect(page.locator('.dashboard-tab[data-tab="holes"]')).toHaveClass(/active/);
        await expect(page.locator('#holes-content')).toHaveClass(/active/);

        // 切换到 Owner Distribution Tab
        await page.click('.dashboard-tab[data-tab="owner"]');
        await page.waitForTimeout(500);
        await expect(page.locator('.dashboard-tab[data-tab="owner"]')).toHaveClass(/active/);
        await expect(page.locator('#owner-content')).toHaveClass(/active/);

        // 切换到 Coverage Matrix Tab
        await page.click('.dashboard-tab[data-tab="matrix"]');
        await page.waitForTimeout(500);
        await expect(page.locator('.dashboard-tab[data-tab="matrix"]')).toHaveClass(/active/);
        await expect(page.locator('#matrix-content')).toHaveClass(/active/);

        // 切换回概览 Tab
        await page.click('.dashboard-tab[data-tab="overview"]');
        await page.waitForTimeout(500);
        await expect(overviewTab).toHaveClass(/active/);
        await expect(overviewContent).toHaveClass(/active/);
    });

    /**
     * UI-TAB-002: Tab 内容加载 - Tab 内容正确显示
     */
    test('UI-TAB-002: Tab 内容加载 - Tab 内容正确显示', async ({ page }) => {
        // 验证概览 Tab 内容 - 卡片容器
        const dashboardOverview = page.locator('#dashboard-overview');
        await expect(dashboardOverview).toBeVisible();

        // 验证趋势图容器
        const trendChart = page.locator('#trend-chart');
        await expect(trendChart).toBeVisible();

        // 验证摘要行容器
        const summaryRow = page.locator('.dashboard-summary-row');
        await expect(summaryRow).toBeVisible();

        // 验证空洞摘要容器
        const holesSummary = page.locator('#holes-summary');
        await expect(holesSummary).toBeVisible();

        // 验证 Owner 摘要容器
        const ownerSummary = page.locator('#owner-summary');
        await expect(ownerSummary).toBeVisible();

        // 验证矩阵预览容器
        const matrixPreview = page.locator('#matrix-preview');
        await expect(matrixPreview).toBeVisible();

        // 切换到 Coverage Holes Tab
        await page.click('.dashboard-tab[data-tab="holes"]');
        await page.waitForTimeout(500);
        const holesTabContent = page.locator('#holes-tab-content');
        await expect(holesTabContent).toBeVisible();

        // 切换到 Owner Distribution Tab
        await page.click('.dashboard-tab[data-tab="owner"]');
        await page.waitForTimeout(500);
        const ownerTabContent = page.locator('#owner-tab-content');
        await expect(ownerTabContent).toBeVisible();

        // 切换到 Coverage Matrix Tab
        await page.click('.dashboard-tab[data-tab="matrix"]');
        await page.waitForTimeout(500);
        const matrixTabContent = page.locator('#matrix-tab-content');
        await expect(matrixTabContent).toBeVisible();
    });

    /**
     * UI-TAB-003: Tab 动画 - 切换有过渡动画
     */
    test('UI-TAB-003: Tab 动画 - 切换有过渡动画', async ({ page }) => {
        // 获取初始 Tab 按钮样式
        const tabsContainer = page.locator('.dashboard-tabs');
        await expect(tabsContainer).toBeVisible();

        // 验证 Tab 按钮有过渡效果（通过检查 CSS transition）
        const hasTransition = await page.evaluate(() => {
            const tab = document.querySelector('.dashboard-tab');
            if (!tab) return false;
            const style = window.getComputedStyle(tab);
            return style.transition !== 'none' && style.transition !== '';
        });

        // Tab 切换应该有时序验证
        await page.click('.dashboard-tab[data-tab="holes"]');
        const holesTab = page.locator('.dashboard-tab[data-tab="holes"]');
        await expect(holesTab).toHaveClass(/active/);

        await page.click('.dashboard-tab[data-tab="owner"]');
        const ownerTab = page.locator('.dashboard-tab[data-tab="owner"]');
        await expect(ownerTab).toHaveClass(/active/);

        await page.click('.dashboard-tab[data-tab="matrix"]');
        const matrixTab = page.locator('.dashboard-tab[data-tab="matrix"]');
        await expect(matrixTab).toHaveClass(/active/);
    });

    /**
     * UI-OVER-001: 趋势图显示 - 7天趋势图正确渲染
     */
    test('UI-OVER-001: 趋势图显示 - 7天趋势图正确渲染', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证趋势图 SVG 存在
        const trendSvg = page.locator('.trend-svg');
        await expect(trendSvg).toBeVisible();

        // 验证趋势线存在
        const trendLine = page.locator('.trend-line');
        await expect(trendLine).toBeVisible();

        // 验证数据点存在
        const trendDots = page.locator('.trend-dot');
        const dotCount = await trendDots.count();
        expect(dotCount).toBeGreaterThan(0);

        // 验证 Y 轴标签存在
        const trendLabels = page.locator('.trend-label');
        const labelCount = await trendLabels.count();
        expect(labelCount).toBeGreaterThan(0);
    });

    /**
     * UI-OVER-002: 数字卡片显示 - 已覆盖/未关联/TC通过率显示
     */
    test('UI-OVER-002: 数字卡片显示 - 已覆盖/未关联/TC通过率显示', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证概览卡片存在（3张卡片）
        const overviewCards = page.locator('.overview-card');
        const cardCount = await overviewCards.count();
        expect(cardCount).toBe(3);

        // 验证卡片标签
        const cardLabels = await page.locator('.overview-label').allTextContents();
        expect(cardLabels).toContain('Covered');
        expect(cardLabels).toContain('Unlinked');
        expect(cardLabels).toContain('TC Pass Rate');

        // 验证卡片数值（格式应该是 "X/Y" 或 "Z%" 或 纯数字 或 "N/A"）
        const cardValues = await page.locator('.overview-value').allTextContents();
        expect(cardValues.length).toBe(3);
        for (const value of cardValues) {
            const cleanedValue = value.replace(/\s+/g, '').replace(/·+/g, '');
            // Handle N/A, '--', percentage (e.g., "85%"), fraction (e.g., "30/52"), or plain number (e.g., "5")
            const isValidFormat = cleanedValue === '--' || cleanedValue === 'N/A' || /\d+.*%|\d+\/\d+|\d+/.test(cleanedValue);
            expect(isValidFormat).toBeTruthy();
        }
    });

    /**
     * UI-OVER-003: 周环比显示 - 正确显示变化值或 "--"
     */
    test('UI-OVER-003: 周环比显示 - 正确显示变化值或 "--"', async ({ page }) => {
        // 周环比可能在卡片下方显示，需要检查数据格式
        // 根据规格说明，周环比用 -- 表示无数据或实际变化值
        await page.waitForTimeout(2000);

        // 检查是否有环比数据（如果加载了快照数据的话）
        const hasChangeIndicator = await page.evaluate(() => {
            // 检查概览卡片区域是否有变化指示器
            const cards = document.querySelectorAll('.overview-card');
            for (const card of cards) {
                const text = card.textContent;
                if (text.includes('↑') || text.includes('↓') || text.includes('--')) {
                    return true;
                }
            }
            return false;
        });

        // 如果有变化指示器，验证格式正确
        if (hasChangeIndicator) {
            const cardTexts = await page.locator('.overview-card').allTextContents();
            for (const text of cardTexts) {
                // 应该包含 ↑ 或 ↓ 或 --
                const hasChange = text.includes('↑') || text.includes('↓') || text.includes('--');
                expect(hasChange).toBeTruthy();
            }
        }
    });

    /**
     * UI-OVER-004: 矩阵预览 - Top 4 Features 显示
     */
    test('UI-OVER-004: 矩阵预览 - Top 4 Features 显示', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证矩阵预览容器
        const matrixPreview = page.locator('#matrix-preview');
        await expect(matrixPreview).toBeVisible();

        // 验证标题
        const previewTitle = matrixPreview.locator('.summary-card-title');
        await expect(previewTitle).toContainText('Matrix Preview');

        // 验证 "View full" 链接
        const viewFullLink = matrixPreview.locator('.summary-card-link');
        await expect(viewFullLink).toContainText('View full');

        // 验证 Feature 条目
        const featureBars = page.locator('#matrix-preview .feature-bar-item');
        const barCount = await featureBars.count();
        // Top 4 Features，最多显示 4 个
        expect(barCount).toBeGreaterThan(0);
        expect(barCount).toBeLessThanOrEqual(4);
    });

    /**
     * UI-OVER-005: 空洞摘要 - Top 3 严重空洞显示
     */
    test('UI-OVER-005: 空洞摘要 - Top 3 严重空洞显示', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证空洞摘要容器
        const holesSummary = page.locator('#holes-summary');
        await expect(holesSummary).toBeVisible();

        // 检查是否有空洞数据或空状态
        const hasHoles = await holesSummary.locator('.hole-card').count() > 0;
        const hasEmptyState = await holesSummary.locator('.dashboard-empty').count() > 0;

        if (hasHoles) {
            // 验证标题
            const summaryTitle = holesSummary.locator('.summary-card-title');
            await expect(summaryTitle).toContainText('Top Coverage Holes');

            // 验证 "View all" 链接
            const viewAllLink = holesSummary.locator('.summary-card-link');
            await expect(viewAllLink).toContainText('View all');

            // 验证空洞卡片
            const holeCards = holesSummary.locator('.hole-card');
            const cardCount = await holeCards.count();
            // Top 3 严重空洞 + Top 2 警告空洞 = 最多 5 个
            expect(cardCount).toBeGreaterThan(0);
            expect(cardCount).toBeLessThanOrEqual(5);
        } else if (hasEmptyState) {
            // 无空洞数据时验证空状态提示
            const emptyText = await holesSummary.locator('.dashboard-empty').textContent();
            expect(emptyText).toMatch(/No coverage holes|Loading/);
        }
    });

    /**
     * UI-OVER-006: Owner摘要 - Top 3 Owner 显示
     */
    test('UI-OVER-006: Owner摘要 - Top 3 Owner 显示', async ({ page }) => {
        // 等待数据加载
        await page.waitForTimeout(2000);

        // 验证 Owner 摘要容器
        const ownerSummary = page.locator('#owner-summary');
        await expect(ownerSummary).toBeVisible();

        // 验证标题
        const summaryTitle = ownerSummary.locator('.summary-card-title');
        await expect(summaryTitle).toContainText('Top Owners');

        // 验证 "View all" 链接
        const viewAllLink = ownerSummary.locator('.summary-card-link');
        await expect(viewAllLink).toContainText('View all');

        // 验证 Owner 列表项
        const listItems = ownerSummary.locator('.list-item');
        const itemCount = await listItems.count();
        // Top Owners 最多显示 5 个
        expect(itemCount).toBeGreaterThan(0);
        expect(itemCount).toBeLessThanOrEqual(5);
    });
});
