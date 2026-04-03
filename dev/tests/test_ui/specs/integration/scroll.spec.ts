/**
 * Scroll bar fixed height test
 *
 * Test table container fixed height (UI-SCROLL-004)
 *
 * Run: npx playwright test tests/test_ui/specs/integration/scroll.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8081';

test.describe('Scroll Fixed Height', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    // 处理引导页（v0.10.x 新增）
    const introBtn = page.locator('.intro-cta-btn');
    if (await introBtn.isVisible().catch(() => false)) {
      await introBtn.click();
      await page.waitForTimeout(500);
    }
  });

  test('test_height_fixed', async ({ page }) => {
    await page.waitForLoadState('domcontentloaded');

    // Use guest login (simpler, no password)
    await page.click('#guestLoginBtn');

    // Wait for project selector
    await page.waitForSelector('#projectSelector', { timeout: 15000 });

    // Wait for login overlay to disappear
    await page.waitForFunction(() => {
      const overlay = document.getElementById('loginOverlay');
      return !overlay || !overlay.classList.contains('show');
    }, { timeout: 15000 });

    // Select project
    await page.selectOption('#projectSelector', { label: 'SOC_DV' });
    await page.waitForTimeout(1500);

    // Switch to CP tab
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(1000);

    // Verify CP container
    const cpContainer = page.locator('.cp-table-container');
    await expect(cpContainer).toBeVisible();

    const cpStyle = await cpContainer.evaluate(e => {
      const s = getComputedStyle(e);
      return { maxHeight: s.maxHeight, overflowY: s.overflowY };
    });

    // max-height is dynamic (calc-based), verify it's set and reasonable
    expect(cpStyle.maxHeight).toMatch(/^\d+px$/);
    expect(cpStyle.overflowY).toBe('auto');

    // Switch to TC tab
    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForTimeout(1000);

    // Verify TC container
    const tcContainer = page.locator('.tc-table-container');
    await expect(tcContainer).toBeVisible();

    const tcStyle = await tcContainer.evaluate(e => {
      const s = getComputedStyle(e);
      return { maxHeight: s.maxHeight, overflowY: s.overflowY };
    });

    // max-height is dynamic (calc-based), verify it's set and reasonable
    expect(tcStyle.maxHeight).toMatch(/^\d+px$/);
    expect(tcStyle.overflowY).toBe('auto');
  });
});
