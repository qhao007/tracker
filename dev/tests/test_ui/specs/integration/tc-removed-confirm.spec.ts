/**
 * TC REMOVED 状态二次确认测试
 *
 * 验证将 TC 状态改为 REMOVED 时会弹出二次确认对话框
 * - UI-REM-001: Inline select 改为 REMOVED 需要确认
 * - UI-REM-002: 取消确认后状态不变
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/tc-removed-confirm.spec.ts --project=firefox
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

test.describe('TC REMOVED Confirmation Tests', () => {

    test.beforeEach(async ({ page }) => {
        await loginAsAdmin(page);
        await selectSOCDVProject(page);
        await openTCTab(page);
    });

    /**
     * UI-REM-001: Inline select 改为 REMOVED 需要确认
     */
    test('UI-REM-001: Inline select 改为 REMOVED 弹出确认', async ({ page }) => {
        // 监听 confirm 对话框并自动接受
        page.on('dialog', async dialog => {
            expect(dialog.message()).toContain('REMOVED');
            expect(dialog.message()).toContain('清除');
            await dialog.accept();
        });

        // 找到第一个非 REMOVED 的 TC
        const selects = page.locator('#tcList select.status-select');
        const count = await selects.count();
        let targetSelect = null;
        for (let i = 0; i < count; i++) {
            const val = await selects.nth(i).inputValue();
            if (val !== 'REMOVED') {
                targetSelect = selects.nth(i);
                break;
            }
        }

        if (!targetSelect) {
            test.skip();
            return;
        }

        // 改为 REMOVED
        await targetSelect.selectOption('REMOVED');
        await page.waitForTimeout(1500);

        // 验证状态已变为 REMOVED
        const newValue = await targetSelect.inputValue();
        expect(newValue).toBe('REMOVED');
    });

    /**
     * UI-REM-002: 取消确认后状态不变
     */
    test('UI-REM-002: 取消确认后状态保持不变', async ({ page }) => {
        // 监听 confirm 对话框并自动取消
        page.on('dialog', async dialog => {
            expect(dialog.message()).toContain('REMOVED');
            await dialog.dismiss();
        });

        // 找到第一个非 REMOVED 的 TC
        const selects = page.locator('#tcList select.status-select');
        const count = await selects.count();
        let targetSelect = null;
        let originalValue = '';
        for (let i = 0; i < count; i++) {
            const val = await selects.nth(i).inputValue();
            if (val !== 'REMOVED') {
                targetSelect = selects.nth(i);
                originalValue = val;
                break;
            }
        }

        if (!targetSelect) {
            test.skip();
            return;
        }

        // 尝试改为 REMOVED（会取消确认）
        await targetSelect.selectOption('REMOVED');
        await page.waitForTimeout(800);

        // 验证状态保持原值
        const newValue = await targetSelect.inputValue();
        expect(newValue).toBe(originalValue);
    });
});
