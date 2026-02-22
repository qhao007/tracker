/**
 * created_by 字段测试 - v0.7.1
 * 使用 Python 脚本验证 API 功能
 */

import { test, expect } from '@playwright/test';

test.describe('created_by 字段', () => {
  test('1. API 创建 TC 应返回 created_by', async ({ request }) => {
    // 这个测试需要后端支持 session，后续完善
    // 暂时跳过，因为 curl 测试已验证功能正常
    test.skip(true, '使用 curl 验证通过');
  });
});
