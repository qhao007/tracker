/**
 * 清除浏览器缓存脚本
 * 运行: npx playwright test --project=firefox clear-cache.spec.ts
 */

import { test, expect } from '@playwright/test';

test('清除测试版缓存', async ({ page }) => {
  // 打开测试版
  await page.goto('http://localhost:8081', { waitUntil: 'networkidle' });
  
  // 清除所有缓存
  const context = page.context();
  await context.clearCookies();
  
  // 清除 Local Storage
  await page.evaluate(() => localStorage.clear());
  await page.evaluate(() => sessionStorage.clear());
  
  // 刷新页面
  await page.reload({ waitUntil: 'networkidle' });
  
  console.log('✅ 缓存已清除');
});
