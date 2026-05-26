/**
 * CP List Filters UI Tests
 *
 * 测试 CP 列表新增过滤功能：
 * - UI-CPF-001: 覆盖率范围过滤 - 0%
 * - UI-CPF-002: 覆盖率范围过滤 - 1-99%
 * - UI-CPF-003: 覆盖率范围过滤 - 100%
 * - UI-CPF-004: 含 Fail 过滤
 * - UI-CPF-005: 组合过滤
 * - UI-CPF-006: 重置过滤
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/cp-list-filters.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

/**
 * 登录辅助函数
 */
async function loginAsAdmin(page: any) {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

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

    await page.fill('#loginUsername', 'admin');
    await page.fill('#loginPassword', 'admin123');
    await page.click('button.login-btn');
    await page.waitForTimeout(1500);

    const changePwdModal = page.locator('#changePasswordModal');
    if (await changePwdModal.isVisible().catch(() => false)) {
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
 * 切换到 CP Tab
 */
async function openCPTab(page: any) {
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(1500);
}

/**
 * 获取当前 CP 列表中所有 coverage badge 的文本
 */
async function getCPListCoverageTexts(page: any): Promise<string[]> {
    const badges = page.locator('#cpList .coverage-badge');
    const count = await badges.count();
    const texts: string[] = [];
    for (let i = 0; i < count; i++) {
        texts.push(await badges.nth(i).textContent() || '');
    }
    return texts;
}

/**
 * 获取当前 CP 列表行数
 */
async function getCPListCount(page: any): Promise<number> {
    const rows = page.locator('#cpList tr[data-cp-id]');
    return await rows.count();
}

test.describe('CP List Filters UI Tests', () => {

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
        await selectSOCDVProject(page);
        await openCPTab(page);
    });

    /**
     * UI-CPF-001: 覆盖率过滤 - 0% (未覆盖)
     */
    test('UI-CPF-001: 覆盖率过滤 - 0% (未覆盖)', async ({ page }) => {
        const totalBefore = await getCPListCount(page);
        expect(totalBefore).toBeGreaterThan(0);

        // 选择 0% 过滤
        await page.selectOption('#cpCoverageFilter', '0');
        await page.waitForTimeout(800);

        const totalAfter = await getCPListCount(page);
        const coverageTexts = await getCPListCoverageTexts(page);

        // 所有显示的 CP 覆盖率都应该是 0%
        for (const text of coverageTexts) {
            expect(text.trim()).toBe('0%');
        }

        // 过滤后数量应该小于等于总数
        expect(totalAfter).toBeLessThanOrEqual(totalBefore);
    });

    /**
     * UI-CPF-002: 覆盖率过滤 - 1-99% (部分覆盖)
     */
    test('UI-CPF-002: 覆盖率过滤 - 1-99% (部分覆盖)', async ({ page }) => {
        const totalBefore = await getCPListCount(page);
        expect(totalBefore).toBeGreaterThan(0);

        await page.selectOption('#cpCoverageFilter', 'partial');
        await page.waitForTimeout(800);

        const coverageTexts = await getCPListCoverageTexts(page);

        for (const text of coverageTexts) {
            const val = parseFloat(text.replace('%', ''));
            expect(val).toBeGreaterThan(0);
            expect(val).toBeLessThan(100);
        }
    });

    /**
     * UI-CPF-003: 覆盖率过滤 - 100% (完全覆盖)
     */
    test('UI-CPF-003: 覆盖率过滤 - 100% (完全覆盖)', async ({ page }) => {
        const totalBefore = await getCPListCount(page);
        expect(totalBefore).toBeGreaterThan(0);

        await page.selectOption('#cpCoverageFilter', '100');
        await page.waitForTimeout(800);

        const coverageTexts = await getCPListCoverageTexts(page);

        for (const text of coverageTexts) {
            expect(text.trim()).toBe('100%');
        }
    });

    /**
     * UI-CPF-004: 含 Fail 过滤
     */
    test('UI-CPF-004: 含 Fail 过滤', async ({ page }) => {
        const totalBefore = await getCPListCount(page);
        expect(totalBefore).toBeGreaterThan(0);

        // 勾选含 Fail
        await page.check('#cpFailFilter');
        await page.waitForTimeout(800);

        const totalAfter = await getCPListCount(page);

        // 过滤后数量应该小于等于总数（如果没有 fail 的 CP 可能为 0）
        expect(totalAfter).toBeLessThanOrEqual(totalBefore);

        // 验证显示的 coverage_detail 中包含 "F"（如 "2/6 (1F)"）
        const details = await page.locator('#cpList .coverage-detail').allTextContents();
        for (const detail of details) {
            expect(detail).toContain('F');
        }
    });

    /**
     * UI-CPF-005: 组合过滤 - 覆盖率 + 含 Fail
     */
    test('UI-CPF-005: 组合过滤 - 覆盖率100% + 含Fail', async ({ page }) => {
        await page.selectOption('#cpCoverageFilter', '100');
        await page.check('#cpFailFilter');
        await page.waitForTimeout(800);

        const coverageTexts = await getCPListCoverageTexts(page);
        const details = await page.locator('#cpList .coverage-detail').allTextContents();

        // 所有结果都应该是 100% 且含 Fail
        for (const text of coverageTexts) {
            expect(text.trim()).toBe('100%');
        }
        for (const detail of details) {
            expect(detail).toContain('F');
        }
    });

    /**
     * UI-CPF-006: 重置过滤
     */
    test('UI-CPF-006: 重置过滤', async ({ page }) => {
        const totalBefore = await getCPListCount(page);
        expect(totalBefore).toBeGreaterThan(0);

        // 先应用过滤
        await page.selectOption('#cpCoverageFilter', '0');
        await page.check('#cpFailFilter');
        await page.waitForTimeout(800);

        const totalFiltered = await getCPListCount(page);
        // 过滤后可能和原来一样也可能更少

        // 点击重置
        await page.click('button:has-text("重置")');
        await page.waitForTimeout(800);

        const totalAfterReset = await getCPListCount(page);

        // 重置后应该恢复全部数量
        expect(totalAfterReset).toBe(totalBefore);

        // 验证控件已重置
        const coverageValue = await page.locator('#cpCoverageFilter').inputValue();
        expect(coverageValue).toBe('');

        const failChecked = await page.locator('#cpFailFilter').isChecked();
        expect(failChecked).toBe(false);
    });
});
