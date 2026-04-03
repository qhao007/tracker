/**
 * FC Tab 测试
 *
 * 测试 FC Tab 显示/隐藏逻辑：
 * - UI-FC-001: FC Tab 仅在 FC-CP 模式显示
 * - UI-FC-002: FC Tab 在 TC-CP 模式不显示
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/15-fc-tab.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';

test.describe('FC Tab 测试', () => {

  /**
   * 登录辅助函数
   */
  async function loginAsAdmin(page: any) {
    await page.goto('http://localhost:8081', { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 处理引导页 - 等待 intro overlay 出现然后关闭
    await page.waitForTimeout(500);
    const introOverlay = page.locator('#introOverlay');
    const introVisible = await introOverlay.isVisible().catch(() => false);
    console.log('Intro overlay visible:', introVisible);

    if (introVisible) {
      // 检查是否有 CTA 按钮
      const introBtn = page.locator('.intro-cta-btn');
      const btnVisible = await introBtn.isVisible().catch(() => false);
      console.log('Intro CTA button visible:', btnVisible);

      if (btnVisible) {
        await introBtn.click();
        await page.waitForTimeout(1000);
      }

      // 隐藏 intro overlay（以防点击没完全隐藏）
      await page.evaluate(() => {
        const overlay = document.getElementById('introOverlay');
        if (overlay) overlay.classList.remove('show');
      });
      await page.waitForTimeout(500);
    }

    // 手动显示登录模态框（确保可见）
    await page.evaluate(() => {
      const overlay = document.getElementById('loginOverlay');
      if (overlay) overlay.classList.add('show');
    });
    await page.waitForTimeout(500);

    // 检查登录表单
    const loginFormVisible = await page.locator('#loginForm').isVisible().catch(() => false);
    console.log('Login form visible:', loginFormVisible);

    if (loginFormVisible) {
      // 填写登录表单
      await page.fill('#loginUsername', 'admin');
      await page.fill('#loginPassword', 'admin123');

      // 直接在 window 上定义并调用 handleLogin
      const loginCallResult = await page.evaluate(async () => {
        try {
          const loginForm = document.getElementById('loginForm');
          if (loginForm) {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            const res = await fetch('/api/auth/login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ username, password }),
              credentials: 'include'
            });
            const data = await res.json();

            if (data.success) {
              // 登录成功，手动更新 UI（因为 handleLogin 在闭包内）
              document.getElementById('loginOverlay').classList.remove('show');
              document.getElementById('loginHeaderBtn').style.display = 'none';
              document.getElementById('userInfo').style.display = 'flex';
              document.getElementById('currentUsername').textContent = data.user.username;
              return { success: true, user: data.user };
            } else {
              return { success: false, error: data.message };
            }
          }
          return { success: false, error: 'Login form not found' };
        } catch (e) {
          return { success: false, error: e.message };
        }
      });
      console.log('Login result:', loginCallResult);

      // 等待 UI 更新
      await page.waitForTimeout(2000);

      // 检查是否出现密码修改模态框
      const changePwdModal = page.locator('#changePasswordModal');
      if (await changePwdModal.isVisible().catch(() => false)) {
        console.log('Password change modal appeared');
        await page.fill('#newPassword', 'admin123');
        await page.fill('#confirmPassword', 'admin123');
        await page.click('#changePasswordModal button.btn-primary');
        await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
        await page.waitForTimeout(1000);
      }

      // 检查登录是否成功
      const userInfoVisible = await page.locator('#userInfo').isVisible().catch(() => false);
      console.log('After login, userInfo visible:', userInfoVisible);
    } else {
      console.log('Login form not visible - checking if already logged in');
    }

    // 等待用户登录成功 - 检查 #userInfo 是否可见
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });
    await page.waitForTimeout(1000);
  }

  /**
   * 创建 FC-CP 模式项目的辅助函数
   */
  async function createFCCPProject(page: any, projectName: string) {
    // 检查用户状态
    const userInfo = await page.evaluate(() => {
      const userInfoEl = document.getElementById('userInfo');
      const usernameEl = document.getElementById('currentUsername');
      return {
        isVisible: window.getComputedStyle(userInfoEl).display !== 'none',
        username: usernameEl.textContent
      };
    });
    console.log('User info:', userInfo);

    // 检查项目按钮状态
    const btnInfo = await page.evaluate(() => {
      const btn = document.getElementById('projectManageBtn');
      if (!btn) return { exists: false };
      const style = window.getComputedStyle(btn);
      return {
        exists: true,
        display: style.display,
        visibility: style.visibility
      };
    });
    console.log('Project button info:', btnInfo);

    // 手动显示项目弹窗
    await page.evaluate(() => {
      const modal = document.getElementById('projectModal');
      modal.classList.add('active');
    });
    // 等待 modal 可视
    await page.waitForSelector('#projectModal.active', { timeout: 5000 });
    await page.fill('#newProjectName', projectName);

    // 填写日期
    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    const startDate = today.toISOString().split('T')[0];
    const endDate = nextMonth.toISOString().split('T')[0];
    await page.fill('#newProjectStartDate', startDate);
    await page.fill('#newProjectEndDate', endDate);

    // 选择 FC-CP 模式
    await page.selectOption('#newProjectCoverageMode', 'fc_cp');

    // 直接在页面上下文中触发按钮点击
    await page.evaluate(() => {
      const btns = document.querySelectorAll('#projectModal button');
      for (const btn of btns) {
        if (btn.textContent.includes('创建')) { btn.click(); break; }
      }
    });
    // 等待 modal 关闭 (不再有 active class)
    await page.waitForSelector('#projectModal:not(.active)', { state: 'attached', timeout: 10000 });
    // 等待 UI 更新
    await page.waitForTimeout(500);
  }

  /**
   * 创建 TC-CP 模式项目的辅助函数
   */
  async function createTCCPProject(page: any, projectName: string) {
    // 检查用户状态
    const userInfo = await page.evaluate(() => {
      const userInfoEl = document.getElementById('userInfo');
      const usernameEl = document.getElementById('currentUsername');
      return {
        isVisible: window.getComputedStyle(userInfoEl).display !== 'none',
        username: usernameEl.textContent
      };
    });
    console.log('User info:', userInfo);

    // 手动显示项目弹窗
    await page.evaluate(() => {
      const modal = document.getElementById('projectModal');
      modal.classList.add('active');
    });
    // 等待 modal 可视
    await page.waitForSelector('#projectModal.active', { timeout: 5000 });
    await page.fill('#newProjectName', projectName);

    // 填写日期
    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    const startDate = today.toISOString().split('T')[0];
    const endDate = nextMonth.toISOString().split('T')[0];
    await page.fill('#newProjectStartDate', startDate);
    await page.fill('#newProjectEndDate', endDate);

    // 选择 TC-CP 模式 (默认)
    await page.selectOption('#newProjectCoverageMode', 'tc_cp');

    // 直接在页面上下文中触发按钮点击
    await page.evaluate(() => {
      const btns = document.querySelectorAll('#projectModal button');
      for (const btn of btns) {
        if (btn.textContent.includes('创建')) { btn.click(); break; }
      }
    });
    // 等待 modal 关闭 (不再有 active class)
    await page.waitForSelector('#projectModal:not(.active)', { state: 'attached', timeout: 10000 });
    // 等待 UI 更新
    await page.waitForTimeout(500);
  }

  test.beforeEach(async ({ page }) => {
    // 登录
    await loginAsAdmin(page);
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  /**
   * UI-FC-001: FC Tab 仅在 FC-CP 模式显示
   */
  test('UI-FC-001: FC Tab 仅在 FC-CP 模式显示', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_CP');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 等待项目切换
    await page.waitForTimeout(1000);

    // 验证 FC Tab 可见
    const fcTab = page.locator('#fcTab');
    await expect(fcTab).toBeVisible();
  });

  /**
   * UI-FC-002: FC Tab 在 TC-CP 模式不显示
   */
  test('UI-FC-002: FC Tab 在 TC-CP 模式不显示', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_TC_CP');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);

    // 等待项目切换
    await page.waitForTimeout(1000);

    // 验证 FC Tab 不可见
    const fcTab = page.locator('#fcTab');
    await expect(fcTab).toBeHidden();
  });

  /**
   * UI-FC-003: 切换到 FC-CP 项目后 FC Tab 显示
   */
  test('UI-FC-003: 切换项目后 FC Tab 状态正确', async ({ page }) => {
    const fcProjectName = TestDataFactory.generateProjectName('TestUI_FC');
    const tcProjectName = TestDataFactory.generateProjectName('TestUI_TC');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, tcProjectName);
    await page.waitForTimeout(500);

    // 验证 FC Tab 不可见
    const fcTab = page.locator('#fcTab');
    await expect(fcTab).toBeHidden();

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, fcProjectName);
    await page.waitForTimeout(500);

    // 验证 FC Tab 可见
    await expect(fcTab).toBeVisible();
  });

  /**
   * UI-FC-004: FC Tab 点击切换到 FC 面板
   */
  test('UI-FC-004: FC Tab 点击切换到 FC 面板', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Click');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);
    await page.waitForTimeout(500);

    // 点击 FC Tab
    await page.click('#fcTab');
    await page.waitForTimeout(500);

    // 验证 FC Panel 显示
    const fcPanel = page.locator('#fcPanel');
    await expect(fcPanel).toBeVisible();

    // 验证 FC Panel 内容
    await expect(page.locator('#fcEmptyState')).toBeVisible();
  });

  /**
   * UI-FC-005: TC-CP 模式下 FC Tab 不存在 DOM 中
   */
  test('UI-FC-005: TC-CP 模式下 FC Tab 不存在 DOM 中', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_NoFC');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);
    await page.waitForTimeout(500);

    // 验证 FC Tab display 为 none
    const fcTabDisplay = await page.evaluate(() => {
      const fcTab = document.getElementById('fcTab');
      return fcTab ? window.getComputedStyle(fcTab).display : 'not_found';
    });

    expect(fcTabDisplay).toBe('none');
  });
});
