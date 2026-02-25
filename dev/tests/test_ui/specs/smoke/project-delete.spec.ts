/**
 * 项目删除 UI 测试 - v0.7.1
 * 注意：项目删除功能需要项目列表管理界面，当前版本未实现
 */

import { test, expect } from '@playwright/test';

test.describe('项目删除 UI', () => {

  test('1. 项目选择器在登录后可见', async ({ page }) => {
    // 登录和项目访问已在 login.spec.ts 中测试
    test.skip(true, '登录和项目访问已在 login.spec.ts 中测试');
  });

  test('2. guest 可以访问项目', async ({ page }) => {
    // 登录和项目访问已在 login.spec.ts 中测试
    test.skip(true, '登录和项目访问已在 login.spec.ts 中测试');
  });

  test('3. 点击删除应弹出确认对话框', async ({ page }) => {
    // 项目列表管理界面尚未实现
    test.skip(true, '项目列表管理界面尚未实现');
  });

  test('4. 确认删除后项目应被删除', async ({ page }) => {
    test.skip(true, '项目列表管理界面尚未实现');
  });

  test('5. 取消删除后项目应保留', async ({ page }) => {
    test.skip(true, '项目列表管理界面尚未实现');
  });

});
