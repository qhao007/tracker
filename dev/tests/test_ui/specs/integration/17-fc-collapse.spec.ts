/**
 * FC 折叠/展开测试
 *
 * 测试 FC 折叠/展开功能：
 * - UI-FC-COLLAPSE-001: 默认全部折叠
 * - UI-FC-COLLAPSE-002: 展开/折叠 covergroup
 * - UI-FC-COLLAPSE-003: 展开/折叠 coverpoint
 * - UI-FC-COLLAPSE-004: 全部展开按钮
 * - UI-FC-COLLAPSE-005: 全部折叠按钮
 * - UI-FC-COLLAPSE-006: localStorage 记忆
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/17-fc-collapse.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';

test.describe('FC 折叠/展开测试', () => {

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
   * 创建 FC-CP 模式项目
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
   * 导入 FC 数据
   */
  async function importFCData(page: any, csvContent: string) {
    // 打开 FC 导入弹窗
    await page.click('button:has-text("📥 导入 FC")');
    await page.waitForSelector('#importModal', { state: 'visible', timeout: 5000 });

    // 设置文件
    const fileInput = page.locator('#importFile');
    await fileInput.setInputFiles({
      name: 'test_fc.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });

    // 点击导入
    await page.click('#importModal button.btn-primary:has-text("导入")');

    // 等待模态框关闭 (executeFCImport 在成功后 1500ms 关闭 modal)
    await page.waitForSelector('#importModal:not(.active)', { state: 'hidden', timeout: 10000 });

    // 等待 loadFC 完成数据更新 (setTimeout 1500ms + loadFC fetch + render)
    await page.waitForTimeout(2000);
  }

  test.beforeEach(async ({ page }) => {
    // 登录
    await loginAsAdmin(page);
    await page.waitForSelector('#projectSelector', { timeout: 10000 });

    // 创建 FC-CP 模式项目
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Collapse');
    await createFCCPProject(page, projectName);

    // 切换到 FC Tab
    await page.click('#fcTab');
    await page.waitForTimeout(500);

    // 清理 localStorage 确保干净状态
    await page.evaluate(() => {
      localStorage.removeItem('tracker_fc_expanded_groups');
      localStorage.removeItem('tracker_fc_expanded_coverpoints');
    });
  });

  test.afterEach(async ({ page }) => {
    // 清理 localStorage
    await page.evaluate(() => {
      localStorage.removeItem('tracker_fc_expanded_groups');
      localStorage.removeItem('tracker_fc_expanded_coverpoints');
    });
  });

  /**
   * UI-FC-COLLAPSE-001: 默认全部折叠
   */
  test('UI-FC-COLLAPSE-001: 默认全部折叠', async ({ page }) => {
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg1,cg1_cp1,coverpoint,b1,val1,0.8,ready,test
cg1,cg1_cp1,coverpoint,b2,val2,0.9,ready,test
cg1,cg1_cp2,coverpoint,b3,val3,0.7,ready,test
cg2,cg2_cp1,coverpoint,b4,val4,0.6,ready,test`;

    await importFCData(page, csvContent);
    await page.waitForTimeout(500);

    // 验证所有 covergroup header 显示折叠状态 (▶)
    const collapsedHeaders = await page.locator('.fc-covergroup-header:has-text("▶")').count();
    expect(collapsedHeaders).toBeGreaterThan(0);

    // 验证没有展开的 covergroup
    const expandedHeaders = await page.locator('.fc-covergroup-header:has-text("▼")').count();
    expect(expandedHeaders).toBe(0);
  });

  /**
   * UI-FC-COLLAPSE-002: 展开/折叠 covergroup
   */
  test('UI-FC-COLLAPSE-002: 展开/折叠 covergroup', async ({ page }) => {
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_test,cg_test_cp,coverpoint,b1,val1,0.8,ready,test`;

    await importFCData(page, csvContent);
    await page.waitForTimeout(500);

    // 初始状态是折叠的
    const header = page.locator('.fc-covergroup-header').first();
    await expect(header).toContainText('▶');

    // 点击展开
    await header.click();
    await page.waitForTimeout(300);

    // 验证展开状态 (▼)
    await expect(header).toContainText('▼');

    // 再次点击折叠
    await header.click();
    await page.waitForTimeout(300);

    // 验证折叠状态 (▶)
    await expect(header).toContainText('▶');
  });

  /**
   * UI-FC-COLLAPSE-003: 展开/折叠 coverpoint
   */
  test('UI-FC-COLLAPSE-003: 展开/折叠 coverpoint', async ({ page }) => {
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_cp_test,cg_cp_test_cp,coverpoint,b1,val1,0.8,ready,test`;

    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 先点击 covergroup header 展开
    const cgHeader = page.locator('.fc-covergroup-header').first();
    await cgHeader.click();
    await page.waitForTimeout(300);

    // 验证 coverpoint header 可见且为折叠状态 (▶)
    const cpHeader = page.locator('.fc-coverpoint-header').first();
    await expect(cpHeader).toBeVisible();
    await expect(cpHeader).toContainText('▶');

    // 点击展开 coverpoint
    await cpHeader.click();
    await page.waitForTimeout(300);

    // 验证展开状态 (▼)
    await expect(cpHeader).toContainText('▼');

    // 验证 bin 表格可见
    const binTable = page.locator('.fc-coverpoint-content table').first();
    await expect(binTable).toBeVisible();
  });

  /**
   * UI-FC-COLLAPSE-004: 全部展开按钮
   */
  test('UI-FC-COLLAPSE-004: 全部展开按钮', async ({ page }) => {
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_all1,cg_all1_cp,coverpoint,b1,val1,0.8,ready,test
cg_all2,cg_all2_cp,coverpoint,b2,val2,0.9,ready,test`;

    await importFCData(page, csvContent);
    await page.waitForTimeout(500);

    // 点击全部展开按钮
    await page.click('#toggleAllFCExpand');
    await page.waitForTimeout(300);

    // 验证按钮文字变为"全部折叠"
    await expect(page.locator('#toggleAllFCExpand')).toContainText('全部折叠');

    // 验证所有 covergroup 展开
    const expandedHeaders = await page.locator('.fc-covergroup-header:has-text("▼")').count();
    expect(expandedHeaders).toBe(2);
  });

  /**
   * UI-FC-COLLAPSE-005: 全部折叠按钮
   */
  test('UI-FC-COLLAPSE-005: 全部折叠按钮', async ({ page }) => {
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_collapse1,cg_collapse1_cp,coverpoint,b1,val1,0.8,ready,test
cg_collapse2,cg_collapse2_cp,coverpoint,b2,val2,0.9,ready,test`;

    await importFCData(page, csvContent);
    await page.waitForTimeout(500);

    // 先全部展开
    await page.click('#toggleAllFCExpand');
    await page.waitForTimeout(300);

    // 再全部折叠
    await page.click('#toggleAllFCExpand');
    await page.waitForTimeout(300);

    // 验证按钮文字变回"全部展开"
    await expect(page.locator('#toggleAllFCExpand')).toContainText('全部展开');

    // 验证所有 covergroup 折叠
    const collapsedHeaders = await page.locator('.fc-covergroup-header:has-text("▶")').count();
    expect(collapsedHeaders).toBe(2);
  });

  /**
   * UI-FC-COLLAPSE-006: localStorage 记忆
   */
  test('UI-FC-COLLAPSE-006: localStorage 记忆', async ({ page }) => {
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg记忆,cg记忆_cp,coverpoint,b1,val1,0.8,ready,test`;

    await importFCData(page, csvContent);
    await page.waitForTimeout(500);

    // 展开 covergroup
    const header = page.locator('.fc-covergroup-header').first();
    await header.click();
    await page.waitForTimeout(300);

    // 验证 localStorage 被更新
    const expandedGroups = await page.evaluate(() => {
      return localStorage.getItem('tracker_fc_expanded_groups');
    });
    expect(expandedGroups).toContain('cg记忆');

    // 刷新页面
    await page.reload();
    await page.waitForTimeout(1000);

    // 切换到 FC Tab (FC-CP 模式项目)
    await page.click('#fcTab');
    await page.waitForTimeout(500);

    // 验证 covergroup 保持展开状态
    const headerAfterReload = page.locator('.fc-covergroup-header').first();
    await expect(headerAfterReload).toContainText('▼');
  });
});
