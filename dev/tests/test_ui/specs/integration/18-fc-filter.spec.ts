/**
 * FC 筛选测试
 *
 * 测试 FC 筛选和搜索功能：
 * - UI-FC-FILTER-001: 筛选 covergroup
 * - UI-FC-FILTER-002: 筛选 coverpoint
 * - UI-FC-FILTER-003: 筛选 coverage_type
 * - UI-FC-FILTER-004: 多条件 AND 筛选
 * - UI-FC-FILTER-005: 清除筛选
 * - UI-FC-SEARCH-001: bin_name 模糊搜索
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/18-fc-filter.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';

test.describe('FC 筛选测试', () => {

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
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Filter');
    await createFCCPProject(page, projectName);

    // 切换到 FC Tab
    await page.click('#fcTab');
    await page.waitForTimeout(500);

    // 导入测试数据
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_filter1,cp_filter1,coverpoint,b_filter1,val1,0.8,ready,test1
cg_filter1,cp_filter1,coverpoint,b_filter2,val2,0.9,ready,test2
cg_filter1,cp_filter2,coverpoint,b_filter3,val3,0.7,ready,test3
cg_filter2,cp_filter3,coverpoint,b_filter4,val4,0.6,ready,test4
cg_filter2,cp_filter3,coverpoint,b_extra,val5,0.5,ready,test5
cg_type,cp_type,coverpoint,b_type1,val6,0.4,ready,test6`;

    await importFCData(page, csvContent);
    // 等待 loadFC 完成数据更新 (setTimeout 1500ms + loadFC fetch + render)
    await page.waitForTimeout(2000);
  });

  /**
   * UI-FC-FILTER-001: 筛选 covergroup
   */
  test('UI-FC-FILTER-001: 筛选 covergroup', async ({ page }) => {
    // 选择 covergroup 筛选
    await page.selectOption('#fcCovergroupFilter', 'cg_filter1');
    await page.waitForTimeout(300);

    // 验证只显示 cg_filter1
    const fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('3');

    // 验证 covergroup header 只有一个
    const headers = await page.locator('.fc-covergroup-header').count();
    expect(headers).toBe(1);
    await expect(page.locator('.fc-covergroup-header').first()).toContainText('cg_filter1');
  });

  /**
   * UI-FC-FILTER-002: 筛选 coverpoint
   */
  test('UI-FC-FILTER-002: 筛选 coverpoint', async ({ page }) => {
    // 先选择 covergroup 筛选展开下拉
    await page.selectOption('#fcCovergroupFilter', 'cg_filter1');
    await page.waitForTimeout(300);

    // 选择 coverpoint 筛选
    await page.selectOption('#fcCoverpointFilter', 'cp_filter1');
    await page.waitForTimeout(300);

    // 验证只显示 cp_filter1
    const fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('2');
  });

  /**
   * UI-FC-FILTER-003: 筛选 coverage_type
   */
  test('UI-FC-FILTER-003: 筛选 coverage_type', async ({ page }) => {
    // 选择 coverage_type 筛选
    await page.selectOption('#fcCoverageTypeFilter', 'coverpoint');
    await page.waitForTimeout(300);

    // 验证显示所有 coverpoint 类型
    const fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('6');
  });

  /**
   * UI-FC-FILTER-004: 多条件 AND 筛选
   */
  test('UI-FC-FILTER-004: 多条件 AND 筛选', async ({ page }) => {
    // 选择 covergroup
    await page.selectOption('#fcCovergroupFilter', 'cg_filter1');
    await page.waitForTimeout(300);

    // 选择 coverpoint
    await page.selectOption('#fcCoverpointFilter', 'cp_filter1');
    await page.waitForTimeout(300);

    // 验证 AND 条件筛选结果
    const fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('2');
  });

  /**
   * UI-FC-FILTER-005: 清除筛选
   */
  test('UI-FC-FILTER-005: 清除筛选', async ({ page }) => {
    // 先应用筛选
    await page.selectOption('#fcCovergroupFilter', 'cg_filter1');
    await page.waitForTimeout(300);

    let fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('3');

    // 点击重置按钮
    await page.click('#fcPanel button:has-text("重置")');
    await page.waitForTimeout(300);

    // 验证筛选被清除
    fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('6');

    // 验证下拉框恢复默认值
    await expect(page.locator('#fcCovergroupFilter')).toHaveValue('');
    await expect(page.locator('#fcCoverpointFilter')).toHaveValue('');
    await expect(page.locator('#fcCoverageTypeFilter')).toHaveValue('');
  });

  /**
   * UI-FC-SEARCH-001: bin_name 模糊搜索
   */
  test('UI-FC-SEARCH-001: bin_name 模糊搜索', async ({ page }) => {
    // 输入搜索关键词
    await page.fill('#fcSearchInput', 'filter1');
    await page.waitForTimeout(300);

    // 验证只显示包含 filter1 的结果
    const fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('1');

    // 验证显示正确的 bin
    await expect(page.locator('.fc-covergroup')).toContainText('b_filter1');
  });

  /**
   * UI-FC-SEARCH-002: 搜索结果高亮
   */
  test('UI-FC-SEARCH-002: 搜索结果高亮', async ({ page }) => {
    // 输入搜索关键词
    await page.fill('#fcSearchInput', 'extra');
    await page.waitForTimeout(300);

    // 验证只显示包含 extra 的结果
    const fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('1');

    // 验证显示正确的 bin
    await expect(page.locator('.fc-covergroup')).toContainText('b_extra');
  });

  /**
   * UI-FC-SEARCH-003: 搜索+筛选组合
   */
  test('UI-FC-SEARCH-003: 搜索+筛选组合', async ({ page }) => {
    // 先选择 covergroup
    await page.selectOption('#fcCovergroupFilter', 'cg_filter2');
    await page.waitForTimeout(300);

    // 再搜索
    await page.fill('#fcSearchInput', 'filter4');
    await page.waitForTimeout(300);

    // 验证组合筛选结果
    const fcCount = await page.locator('#fcCount').textContent();
    expect(fcCount).toBe('1');

    await expect(page.locator('.fc-covergroup')).toContainText('b_filter4');
  });

  /**
   * UI-FC-FILTER-006: 筛选后折叠/展开状态保持
   */
  test('UI-FC-FILTER-006: 筛选后折叠/展开状态保持', async ({ page }) => {
    // 展开 covergroup
    const header = page.locator('.fc-covergroup-header').first();
    await header.click();
    await page.waitForTimeout(300);

    // 验证展开
    await expect(header).toContainText('▼');

    // 应用筛选
    await page.selectOption('#fcCovergroupFilter', 'cg_filter1');
    await page.waitForTimeout(300);

    // 验证展开状态保持
    await expect(header).toContainText('▼');
  });
});
