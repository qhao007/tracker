/**
 * 页面 Fixtures
 * 提供页面级别的共享配置
 */

import { test as base } from '@playwright/test';

/**
 * 页面配置选项
 */
type PageFixtures = {
  // 页面上下文
  context: {
    viewport?: { width: number; height: number };
    locale?: string;
  };
};

/**
 * 定义页面 fixtures
 */
export const test = base.extend<PageFixtures>({
  /**
   * 页面上下文配置
   */
  context: async ({ browser }, use) => {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      locale: 'zh-CN',
    });

    await use(context);

    // 测试结束后清理上下文
    await context.close();
  },
});

/**
 * API Fixtures - 用于 API 测试
 */
import { APIRequestContext } from '@playwright/test';

type APIFixtures = {
  apiContext: APIRequestContext;
};

export const apiTest = base.extend<APIFixtures>({
  apiContext: async ({ request }, use) => {
    const apiContext = await request.newContext({
      baseURL: 'http://localhost:8081',
      extraHTTPHeaders: {
        'Content-Type': 'application/json',
      },
    });

    await use(apiContext);

    // 清理
    await apiContext.dispose();
  },
});
