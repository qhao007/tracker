/**
 * Tracker 专用 Fixtures
 * 提供 Tracker 各个页面的 Page Objects
 * 包含自动清理机制
 */

import { test as base, TestInfo } from '@playwright/test';
import { ProjectPage } from '../pages/project.page';
import { CPPage } from '../pages/cp.page';
import { TCPage } from '../pages/tc.page';
import { cleanupTestData } from '../utils/cleanup';

/**
 * Tracker 专用测试类型
 */
type TrackerFixtures = {
  // Page Objects
  projectPage: ProjectPage;
  cpPage: CPPage;
  tcPage: TCPage;

  // 测试信息
  testInfo: TestInfo;

  // 测试数据
  uniqueProjectName: string;
  uniqueCPName: string;
  uniqueTCName: string;
};

/**
 * 定义 Tracker fixtures
 */
export const test = base.extend<TrackerFixtures>({
  /**
   * ProjectPage fixture
   */
  projectPage: async ({ page }, use) => {
    const projectPage = new ProjectPage(page);
    await use(projectPage);
  },

  /**
   * CPPage fixture
   */
  cpPage: async ({ page }, use) => {
    // 处理原生 confirm 对话框 - 忽略已处理的 dialog
    page.on('dialog', async dialog => {
      try {
        await dialog.accept();
      } catch (e) {
        // 忽略 "already handled" 错误
      }
    });
    const cpPage = new CPPage(page);
    await use(cpPage);
  },

  /**
   * TCPage fixture
   */
  tcPage: async ({ page }, use) => {
    // 处理原生 confirm 对话框 - 忽略已处理的 dialog
    page.on('dialog', async dialog => {
      try {
        await dialog.accept();
      } catch (e) {
        // 忽略 "already handled" 错误
      }
    });
    const tcPage = new TCPage(page);
    await use(tcPage);
  },

  /**
   * TestInfo fixture
   */
  testInfo: async ({}, use, testInfo) => {
    await use(testInfo);
  },

  /**
   * 唯一项目名称 fixture
   */
  uniqueProjectName: async ({}, use) => {
    const name = `TestUI_Project_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    await use(name);
  },

  /**
   * 唯一 CP 名称 fixture
   */
  uniqueCPName: async ({}, use) => {
    const name = `TestUI_CP_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    await use(name);
  },

  /**
   * 唯一 TC 名称 fixture
   */
  uniqueTCName: async ({}, use) => {
    const name = `TestUI_TC_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    await use(name);
  },
});

/**
 * 自动清理机制
 * 
 * 在每个测试后自动清理测试数据
 * 确保测试间不互相干扰
 */

// 注册全局 afterEach 钩子
base.afterEach(async ({ page }, testInfo) => {
  // 如果测试失败，截图保存
  if (testInfo.status === 'failed') {
    const screenshotDir = './test-results/screenshots';
    try {
      await page.screenshot({ 
        path: `${screenshotDir}/${testInfo.title.replace(/\s+/g, '-')}-${Date.now()}.png`,
        fullPage: true 
      });
    } catch (e) {
      console.warn('截图失败:', e);
    }
  }
  
  // 清理测试数据
  await cleanupTestData(page);
});

// ⚠️ 注意：不要在 afterAll 中关闭 browser！
// Playwright 会自动管理 browser 的生命周期
// 多个测试文件共享同一个 browser，关闭会导致后续测试失败

/**
 * 导出 fixtures 以便在其他文件中使用
 */
export { expect } from '@playwright/test';
