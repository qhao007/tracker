/**
 * Tracker 专用 Fixtures
 * 提供 Tracker 各个页面的 Page Objects
 */

import { test as base, TestInfo } from '@playwright/test';
import { ProjectPage } from '../pages/project.page';
import { CPPage } from '../pages/cp.page';
import { TCPage } from '../pages/tc.page';

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
    const cpPage = new CPPage(page);
    await use(cpPage);
  },

  /**
   * TCPage fixture
   */
  tcPage: async ({ page }, use) => {
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
 * 导出 fixtures 以便在其他文件中使用
 */
export { expect } from '@playwright/test';
