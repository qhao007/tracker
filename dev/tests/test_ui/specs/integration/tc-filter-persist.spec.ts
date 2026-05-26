/**
 * TC 过滤持久化测试
 *
 * 验证修改 TC 状态后，过滤条件保持生效
 * - UI-TCF-001: Status 过滤在修改 TC 后保持
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/tc-filter-persist.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

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

async function openTCTab(page: any) {
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForTimeout(1500);
}

/**
 * 获取当前TC列表中所有 status cell 的文本
 */
async function getTCStatusTexts(page: any): Promise<string[]> {
    // 获取所有 status select 的选中值
    return await page.locator('#tcList select.status-select').evaluateAll(
        selects => selects.map(s => s.value).filter(v => v)
    );
}

test.describe('TC Filter Persistence Tests', () => {

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
        await selectSOCDVProject(page);
        await openTCTab(page);
    });

    /**
     * UI-TCF-001: Status 过滤在修改 TC 后保持
     */
    test('UI-TCF-001: Status 过滤在修改 TC 后保持', async ({ page }) => {
        // 1. 选择 OPEN status 过滤
        await page.selectOption('#tcStatusFilter', 'OPEN');
        await page.waitForTimeout(800);

        // 2. 验证列表只显示 OPEN 的 TC
        const statusesBefore = await getTCStatusTexts(page);
        expect(statusesBefore.length).toBeGreaterThan(0);
        for (const status of statusesBefore) {
            expect(status).toBe('OPEN');
        }

        const countBefore = await page.locator('#tcList tr:has(select.status-select)').count();

        // 3. 修改第一个 TC 的 status（通过 inline dropdown）
        const firstStatusSelect = page.locator('#tcList tr:has(select.status-select)').first().locator('select.status-select');
        await firstStatusSelect.selectOption('CODED');
        await page.waitForTimeout(1500);

        // 4. 验证过滤仍然生效 - 列表仍然只显示 OPEN（修改的那个已消失）
        const statusesAfter = await getTCStatusTexts(page);
        for (const status of statusesAfter) {
            expect(status).toBe('OPEN');
        }

        // 5. 验证数量减少了 1（因为修改的那个 TC 从 OPEN 变成了 CODED）
        const countAfter = await page.locator('#tcList tr:has(select.status-select)').count();
        expect(countAfter).toBe(countBefore - 1);

        // 6. 验证过滤框仍然显示 OPEN
        const filterValue = await page.locator('#tcStatusFilter').inputValue();
        expect(filterValue).toBe('OPEN');
    });
});
