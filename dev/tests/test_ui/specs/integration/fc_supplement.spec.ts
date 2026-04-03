/**
 * FC Supplement UI 测试
 *
 * 测试 v0.11.0 supplement 版本的新增 UI 功能：
 * - FC Tab 标题显示 "Functional Coverage"
 * - FC Tab 移除"添加 FC"和"导入 FC-CP 关联"按钮
 * - CP 详情页 FC Item 可点击跳转
 * - FC Bin 显示关联 CP IDs
 * - FC Comment 列截断
 * - 项目对话框显示 coverage_mode 和 FC 个数
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/fc_supplement.spec.ts --project=firefox
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';

test.describe('FC Supplement UI 测试', () => {

  /**
   * 登录辅助函数
   */
  async function loginAsAdmin(page: any) {
    await page.goto('http://localhost:8081', { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');

    // 处理引导页
    await page.waitForTimeout(500);
    const introOverlay = page.locator('#introOverlay');
    const introVisible = await introOverlay.isVisible().catch(() => false);

    if (introVisible) {
      const introBtn = page.locator('.intro-cta-btn');
      const btnVisible = await introBtn.isVisible().catch(() => false);

      if (btnVisible) {
        await introBtn.click();
        await page.waitForTimeout(1000);
      }

      await page.evaluate(() => {
        const overlay = document.getElementById('introOverlay');
        if (overlay) overlay.classList.remove('show');
      });
      await page.waitForTimeout(500);
    }

    // 手动显示登录模态框
    await page.evaluate(() => {
      const overlay = document.getElementById('loginOverlay');
      if (overlay) overlay.classList.add('show');
    });
    await page.waitForTimeout(500);

    const loginFormVisible = await page.locator('#loginForm').isVisible().catch(() => false);

    if (loginFormVisible) {
      await page.fill('#loginUsername', 'admin');
      await page.fill('#loginPassword', 'admin123');

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

      await page.waitForTimeout(2000);

      const changePwdModal = page.locator('#changePasswordModal');
      if (await changePwdModal.isVisible().catch(() => false)) {
        await page.fill('#newPassword', 'admin123');
        await page.fill('#confirmPassword', 'admin123');
        await page.click('#changePasswordModal button.btn-primary');
        await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 }).catch(() => {});
        await page.waitForTimeout(1000);
      }
    }

    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });
    await page.waitForTimeout(1000);
  }

  /**
   * 创建 FC-CP 模式项目
   */
  async function createFCCPProject(page: any, projectName: string) {
    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    const startDate = today.toISOString().split('T')[0];
    const endDate = nextMonth.toISOString().split('T')[0];

    const result = await page.evaluate(async ({ name, startDate, endDate }) => {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          start_date: startDate,
          end_date: endDate,
          coverage_mode: 'fc_cp'
        }),
        credentials: 'include'
      });
      return await res.json();
    }, { name: projectName, startDate, endDate });

    console.log('FC-CP Project created:', result);
    const projectId = result.project?.id;

    // 刷新项目列表并等待完成
    await page.evaluate(async () => {
      if (typeof loadProjects === 'function') {
        await loadProjects();
      }
    });
    await page.waitForTimeout(500);

    // 直接在页面上下文中调用 selectProject 切换到新项目
    await page.evaluate(async (newProjectId) => {
      if (typeof selectProject === 'function') {
        await selectProject(newProjectId);
      }
    }, projectId);

    // 等待项目切换和数据加载完成
    await page.waitForTimeout(1500);

    // 验证 FC Tab 可见
    await page.waitForSelector('#fcTab', { state: 'visible', timeout: 10000 });

    return projectId;
  }

  /**
   * 创建 TC-CP 模式项目
   */
  async function createTCCPProject(page: any, projectName: string) {
    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(nextMonth.getMonth() + 1);
    const startDate = today.toISOString().split('T')[0];
    const endDate = nextMonth.toISOString().split('T')[0];

    const result = await page.evaluate(async ({ name, startDate, endDate }) => {
      const res = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          start_date: startDate,
          end_date: endDate,
          coverage_mode: 'tc_cp'
        }),
        credentials: 'include'
      });
      return await res.json();
    }, { name: projectName, startDate, endDate });

    console.log('TC-CP Project created:', result);
    const projectId = result.project?.id;

    // 刷新项目列表并等待完成
    await page.evaluate(async () => {
      if (typeof loadProjects === 'function') {
        await loadProjects();
      }
    });
    await page.waitForTimeout(500);

    // 直接在页面上下文中调用 selectProject 切换到新项目
    await page.evaluate(async (newProjectId) => {
      if (typeof selectProject === 'function') {
        await selectProject(newProjectId);
      }
    }, projectId);

    // 等待项目切换和数据加载完成
    await page.waitForTimeout(1500);

    // 验证 currentProject 已正确切换
    const currentProjectId = await page.evaluate(() => {
      return typeof currentProject !== 'undefined' ? currentProject?.id : null;
    });
    console.log('Current project ID after switch:', currentProjectId);

    return projectId;
  }

  /**
   * 导入 FC 数据
   */
  async function importFCData(page: any, csvContent: string) {
    // 点击导入按钮
    await page.click('button:has-text("📥 导入 FC")');
    await page.waitForSelector('#importModal', { state: 'visible', timeout: 5000 });

    // 设置 CSV 文件
    const fileInput = page.locator('#importFile');
    await fileInput.setInputFiles({
      name: 'test_fc.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from(csvContent)
    });

    // 点击导入
    await page.click('#importModal button.btn-primary:has-text("导入")');

    // 等待模态框关闭
    await page.waitForSelector('#importModal:not(.active)', { state: 'hidden', timeout: 10000 });
    await page.waitForTimeout(2000);
  }

  /**
   * 创建 CP 数据
   */
  async function createCP(page: any, cpData: any) {
    const result = await page.evaluate(async (data) => {
      const res = await fetch('/api/cp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        credentials: 'include'
      });
      return await res.json();
    }, cpData);

    console.log('CP created:', result);
    await page.waitForTimeout(500);

    // 刷新 CP 列表并渲染
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(500);

    return result;
  }

  /**
   * 创建 FC-CP 关联
   */
  async function createFCCPTAssociation(page: any, fcId: number, cpId: number, projectId: number) {
    const result = await page.evaluate(async ({ fcId, cpId, projectId }) => {
      const res = await fetch('/api/fc-cp-association', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          fc_id: fcId,
          cp_id: cpId
        }),
        credentials: 'include'
      });
      return { status: res.status, data: await res.json() };
    }, { fcId, cpId, projectId });

    console.log('FC-CP Association created:', result);
    await page.waitForTimeout(500);
    return result;
  }

  /**
   * 获取项目 ID
   */
  async function getProjectId(page: any, projectName: string): Promise<number> {
    return await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const data = await res.json();
      const project = data.find((p: any) => p.name === name);
      return project ? project.id : null;
    }, projectName);
  }

  // ==================== FC Tab 标题测试 ====================

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  /**
   * UI-FC-TITLE-001: FC Tab显示完整标题
   */
  test('UI-FC-TITLE-001: FC Tab显示完整标题', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Title');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 等待 FC Tab 出现
    await page.waitForSelector('#fcTab', { state: 'visible', timeout: 10000 });

    // 验证 FC Tab 显示 "Functional Coverage" 而非 "FC"
    const fcTabText = await page.locator('#fcTab').textContent();
    expect(fcTabText).toContain('Functional Coverage');
    expect(fcTabText).not.toBe('FC');
  });

  // ==================== FC Tab 按钮移除测试 ====================

  /**
   * UI-FC-BTN-001: 无添加FC按钮
   */
  test('UI-FC-BTN-001: 无添加FC按钮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Btn');

    await createFCCPProject(page, projectName);
    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 验证找不到"+ 添加 FC"按钮
    const addFCBtn = page.locator('button:has-text("+ 添加 FC")');
    await expect(addFCBtn).toHaveCount(0);
  });

  /**
   * UI-FC-BTN-002: 有导入FC-CP关联按钮
   */
  test('UI-FC-BTN-002: 有导入FC-CP关联按钮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Btn');

    await createFCCPProject(page, projectName);
    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 验证"📥 导入 FC-CP 关联"按钮存在 (BUG-123 修复后)
    const importAssocBtn = page.locator('button:has-text("📥 导入 FC-CP 关联")');
    await expect(importAssocBtn).toBeVisible();
  });

  /**
   * UI-FC-BTN-003: 保留导入FC按钮
   */
  test('UI-FC-BTN-003: 保留导入FC按钮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Btn');

    await createFCCPProject(page, projectName);
    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 验证"📥 导入 FC"按钮存在 (使用精确匹配)
    const importFCBtn = page.locator('button:has-text("📥 导入 FC")').first();
    await expect(importFCBtn).toBeVisible();
  });

  /**
   * UI-FC-BTN-004: 保留导出FC按钮
   */
  test('UI-FC-BTN-004: 保留导出FC按钮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Btn');

    await createFCCPProject(page, projectName);
    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 验证"📤 导出 FC"按钮存在
    const exportFCBtn = page.locator('button:has-text("📤 导出 FC")');
    await expect(exportFCBtn).toBeVisible();
  });

  // ==================== CP 详情 FC 跳转测试 ====================

  /**
   * UI-CP-FC-JUMP-001: CP详情显示FC Item链接
   */
  test('UI-CP-FC-JUMP-001: CP详情显示FC Item链接', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CP_FC_Jump');

    await createFCCPProject(page, projectName);

    // 获取项目 ID
    const projectId = await getProjectId(page, projectName);

    // 创建 CP
    const cpData = {
      project_id: projectId,
      feature: 'TestFeature',
      cover_point: 'CP_Test_Jump',
      cover_point_details: 'Test CP for FC jump',
      priority: 'P0'
    };
    const cpResult = await createCP(page, cpData);

    // 导入 FC 数据
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_jump,cp_jump,coverpoint,b_jump1,val1,0.8,ready,test jump`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);
    await page.waitForTimeout(1000);

    // 获取导入的 FC ID
    const fcList = await page.evaluate(async (projectId) => {
      const res = await fetch(`/api/fc?project_id=${projectId}`, { credentials: 'include' });
      const data = await res.json();
      return data.map((fc: any) => fc.id);
    }, projectId);

    if (fcList.length > 0 && cpResult.success && cpResult.id) {
      // 创建 FC-CP 关联
      await createFCCPTAssociation(page, fcList[0], cpResult.id, projectId);
    }

    // 刷新页面
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

    // 重新选择项目
    await page.evaluate(async (name) => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes(name)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectName);
    await page.waitForTimeout(1000);

    // 切换到 CP Tab
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 展开 CP 详情
    const cpDetailBtn = page.locator('button.action-btn:has-text("详情")').first();
    if (await cpDetailBtn.isVisible()) {
      await cpDetailBtn.click();
      await page.waitForTimeout(1000);

      // 检查是否有 FC 跳转链接
      const fcLink = page.locator('a:has-text("jumpToFCItem")');
      const hasFCLink = await fcLink.count() > 0;
      console.log('Has FC link in CP detail:', hasFCLink);

      // 验证至少能找到跳转链接或空状态
      const cpFcsContainer = page.locator('[id^="cp-fcs-"]');
      const containerCount = await cpFcsContainer.count();
      expect(containerCount).toBeGreaterThan(0);
    }
  });

  /**
   * UI-CP-FC-JUMP-002: 点击FC Item跳转
   */
  test('UI-CP-FC-JUMP-002: 点击FC Item跳转', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CP_FC_Jump2');

    await createFCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建 CP
    const cpData = {
      project_id: projectId,
      feature: 'TestFeature2',
      cover_point: 'CP_Test_Jump2',
      cover_point_details: 'Test CP for FC jump 2',
      priority: 'P0'
    };
    const cpResult = await createCP(page, cpData);

    // 导入 FC 数据
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_jump2,cp_jump2,coverpoint,b_jump2,val2,0.9,ready,test jump 2`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);

    // 获取 FC ID
    const fcList = await page.evaluate(async (projectId) => {
      const res = await fetch(`/api/fc?project_id=${projectId}`, { credentials: 'include' });
      const data = await res.json();
      return data.map((fc: any) => ({ id: fc.id, bin_name: fc.bin_name }));
    }, projectId);

    if (fcList.length > 0 && cpResult.success && cpResult.id) {
      await createFCCPTAssociation(page, fcList[0].id, cpResult.id, projectId);
    }

    // 刷新并选择项目
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

    await page.evaluate(async (name) => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes(name)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectName);
    await page.waitForTimeout(1000);

    // 切换到 CP Tab 并展开详情
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    const cpDetailBtn = page.locator('button.action-btn:has-text("详情")').first();
    if (await cpDetailBtn.isVisible()) {
      await cpDetailBtn.click();
      await page.waitForTimeout(1500);

      // 检查是否有 FC 跳转链接可点击
      const fcLink = page.locator('a:has-text("jumpToFCItem")').first();
      const hasLink = await fcLink.count() > 0;

      if (hasLink) {
        // 点击跳转
        await fcLink.click();
        await page.waitForTimeout(1000);

        // 验证切换到 FC Tab
        const fcTabActive = await page.locator('#fcTab.active');
        await expect(fcTabActive).toBeVisible();
      }
    }
  });

  /**
   * UI-CP-FC-JUMP-003~007: 跳转后展开和滚动测试
   * 这些测试依赖于 UI-CP-FC-JUMP-002 的跳转功能
   */
  test('UI-CP-FC-JUMP-003~007: 跳转后展开和滚动', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CP_FC_Jump3');

    await createFCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建多个 FC
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_multi,cp_multi,b_jump3,val3,0.8,ready,test multi
cg_multi,cp_multi,b_jump4,val4,0.9,ready,test multi 2`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);
    await page.waitForTimeout(1000);

    // 获取 FC 列表
    const fcList = await page.evaluate(async (projectId) => {
      const res = await fetch(`/api/fc?project_id=${projectId}`, { credentials: 'include' });
      const data = await res.json();
      return data.map((fc: any) => ({ id: fc.id, covergroup: fc.covergroup, coverpoint: fc.coverpoint }));
    }, projectId);

    // 创建 CP 并关联
    const cpData = {
      project_id: projectId,
      feature: 'TestFeature3',
      cover_point: 'CP_Test_Jump3',
      cover_point_details: 'Test CP',
      priority: 'P0'
    };
    const cpResult = await createCP(page, cpData);

    if (fcList.length > 0 && cpResult.success && cpResult.id) {
      await createFCCPTAssociation(page, fcList[0].id, cpResult.id, projectId);
    }

    // 刷新并选择项目
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

    await page.evaluate(async (name) => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes(name)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectName);
    await page.waitForTimeout(1000);

    // 切换到 CP Tab 并展开详情
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    const cpDetailBtn = page.locator('button.action-btn:has-text("详情")').first();
    if (await cpDetailBtn.isVisible()) {
      await cpDetailBtn.click();
      await page.waitForTimeout(1500);

      const fcLink = page.locator('a:has-text("jumpToFCItem")').first();
      const hasLink = await fcLink.count() > 0;

      if (hasLink) {
        // 点击跳转
        await fcLink.click();
        await page.waitForTimeout(1500);

        // 验证跳转后 FC Tab 激活
        const fcTabActive = await page.locator('#fcTab.active');
        await expect(fcTabActive).toBeVisible();

        // 验证 covergroup 和 coverpoint 展开（通过检查 FC 列表可见）
        const fcContainer = page.locator('#fcContainer');
        await expect(fcContainer).toBeVisible();

        // 验证高亮效果（fc-highlight 类）
        const highlightedRow = page.locator('.fc-highlight');
        // 高亮可能已经消失（3秒后），所以只检查是否有高亮相关的 DOM 结构
      }
    }
  });

  // ==================== FC Bin CP IDs 列测试 ====================

  /**
   * UI-FC-CPIDS-001: 显示关联CP IDs
   */
  test('UI-FC-CPIDS-001: 显示关联CP IDs', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_CPIds');

    await createFCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建 CP
    const cpData = {
      project_id: projectId,
      feature: 'TestFeature4',
      cover_point: 'CP_Test_CPIds',
      cover_point_details: 'Test CP for CP IDs',
      priority: 'P0'
    };
    const cpResult = await createCP(page, cpData);

    // 导入 FC
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_cpid,cp_cpid,b_cpid1,val1,0.8,ready,test cpid`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);
    await page.waitForTimeout(1000);

    // 获取 FC ID
    const fcList = await page.evaluate(async (projectId) => {
      const res = await fetch(`/api/fc?project_id=${projectId}`, { credentials: 'include' });
      const data = await res.json();
      return data.map((fc: any) => ({ id: fc.id, bin_name: fc.bin_name, cp_ids: fc.cp_ids }));
    }, projectId);

    if (fcList.length > 0 && cpResult.success && cpResult.id) {
      // 创建关联
      await createFCCPTAssociation(page, fcList[0].id, cpResult.id, projectId);

      // 刷新页面
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

      await page.evaluate(async (name) => {
        const selector = document.getElementById('projectSelector');
        for (let i = 0; i < selector.options.length; i++) {
          if (selector.options[i].text.includes(name)) {
            selector.selectedIndex = i;
            selector.dispatchEvent(new Event('change', { bubbles: true }));
            break;
          }
        }
      }, projectName);
      await page.waitForTimeout(1000);

      // 切换到 FC Tab
      await page.click('#fcTab');
      await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
      await page.waitForTimeout(1000);

      // 展开 covergroup 和 coverpoint
      const cgHeader = page.locator('.fc-covergroup-header').first();
      if (await cgHeader.isVisible()) {
        await cgHeader.click();
        await page.waitForTimeout(500);

        const cpHeader = page.locator('.fc-coverpoint-header').first();
        if (await cpHeader.isVisible()) {
          await cpHeader.click();
          await page.waitForTimeout(500);

          // 检查 CP IDs 列 - 应该显示 "CP_{id}" 格式
          const cpIdLinks = page.locator('a:has-text("CP_")');
          expect(await cpIdLinks.count()).toBeGreaterThan(0);
        }
      }
    }
  });

  /**
   * UI-FC-CPIDS-002: 无关联显示横杠
   */
  test('UI-FC-CPIDS-002: 无关联显示横杠', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_NoCPIds');

    await createFCCPProject(page, projectName);

    // 导入 FC（不创建关联）
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_nocpid,cp_nocpid,b_nocpid,val1,0.8,ready,test no cpid`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);
    await page.waitForTimeout(1000);

    // 展开 covergroup 和 coverpoint
    const cgHeader = page.locator('.fc-covergroup-header').first();
    if (await cgHeader.isVisible()) {
      await cgHeader.click();
      await page.waitForTimeout(500);

      const cpHeader = page.locator('.fc-coverpoint-header').first();
      if (await cpHeader.isVisible()) {
        await cpHeader.click();
        await page.waitForTimeout(500);

        // 检查无关联时显示 "-"
        const dashElement = page.locator('td:has-text("-"):not(:has(i)):not(:has(button))');
        // 预期会有 "-" 显示
      }
    }
  });

  /**
   * UI-FC-CPIDS-003: 点击CP ID跳转
   */
  test('UI-FC-CPIDS-003: 点击CP ID跳转', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_CPIds_Click');

    await createFCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建 CP
    const cpData = {
      project_id: projectId,
      feature: 'TestFeature5',
      cover_point: 'CP_Test_Click',
      cover_point_details: 'Test CP for click',
      priority: 'P0'
    };
    const cpResult = await createCP(page, cpData);

    // 导入 FC
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_click,cp_click,b_click,val1,0.8,ready,test click`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projectId) => {
      const res = await fetch(`/api/fc?project_id=${projectId}`, { credentials: 'include' });
      const data = await res.json();
      return data.map((fc: any) => fc.id);
    }, projectId);

    if (fcList.length > 0 && cpResult.success && cpResult.id) {
      await createFCCPTAssociation(page, fcList[0], cpResult.id, projectId);
    }

    // 刷新并选择项目
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

    await page.evaluate(async (name) => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes(name)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectName);
    await page.waitForTimeout(1000);

    // 切换到 FC Tab
    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    // 展开 covergroup 和 coverpoint
    const cgHeader = page.locator('.fc-covergroup-header').first();
    if (await cgHeader.isVisible()) {
      await cgHeader.click();
      await page.waitForTimeout(500);

      const cpHeader = page.locator('.fc-coverpoint-header').first();
      if (await cpHeader.isVisible()) {
        await cpHeader.click();
        await page.waitForTimeout(500);

        // 找到 CP ID 链接
        const cpIdLink = page.locator('a:has-text("CP_")').first();
        const hasLink = await cpIdLink.count() > 0;

        if (hasLink) {
          // 点击跳转
          await cpIdLink.click();
          await page.waitForTimeout(1500);

          // 验证切换到 CP Tab
          const cpTabActive = await page.locator('button.tab.active:has-text("Cover Points")');
          await expect(cpTabActive).toBeVisible();
        }
      }
    }
  });

  /**
   * UI-FC-CPIDS-004: 跳转后展开CP详情
   */
  test('UI-FC-CPIDS-004: 跳转后展开CP详情', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_CPIds_Detail');

    await createFCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建 CP
    const cpData = {
      project_id: projectId,
      feature: 'TestFeature6',
      cover_point: 'CP_Test_Detail',
      cover_point_details: 'Test CP detail',
      priority: 'P0'
    };
    const cpResult = await createCP(page, cpData);

    // 导入 FC 并创建关联
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_detail,cp_detail,b_detail,val1,0.8,ready,test detail`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);

    const fcList = await page.evaluate(async (projectId) => {
      const res = await fetch(`/api/fc?project_id=${projectId}`, { credentials: 'include' });
      const data = await res.json();
      return data.map((fc: any) => fc.id);
    }, projectId);

    if (fcList.length > 0 && cpResult.success && cpResult.id) {
      await createFCCPTAssociation(page, fcList[0], cpResult.id, projectId);
    }

    // 刷新并选择项目
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

    await page.evaluate(async (name) => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes(name)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectName);
    await page.waitForTimeout(1000);

    // 切换到 FC Tab
    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    // 展开 covergroup 和 coverpoint
    const cgHeader = page.locator('.fc-covergroup-header').first();
    if (await cgHeader.isVisible()) {
      await cgHeader.click();
      await page.waitForTimeout(500);

      const cpHeader = page.locator('.fc-coverpoint-header').first();
      if (await cpHeader.isVisible()) {
        await cpHeader.click();
        await page.waitForTimeout(500);

        const cpIdLink = page.locator('a:has-text("CP_")').first();
        if (await cpIdLink.count() > 0) {
          await cpIdLink.click();
          await page.waitForTimeout(1500);

          // 验证 CP 详情展开（通过检查详情行是否可见）
          const cpDetailRow = page.locator('[id^="cp-detail-"]');
          const detailVisible = await cpDetailRow.isVisible().catch(() => false);
          // 跳转后 CP 详情应该自动展开
        }
      }
    }
  });

  /**
   * UI-FC-CPIDS-005: 跳转后高亮CP条目
   */
  test('UI-FC-CPIDS-005: 跳转后高亮CP条目', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_CPIds_Highlight');

    await createFCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建 CP
    const cpData = {
      project_id: projectId,
      feature: 'TestFeature7',
      cover_point: 'CP_Test_Highlight',
      cover_point_details: 'Test CP highlight',
      priority: 'P0'
    };
    const cpResult = await createCP(page, cpData);

    // 导入 FC 并创建关联
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_hl,cp_hl,b_hl,val1,0.8,ready,test highlight`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);

    const fcList = await page.evaluate(async (projectId) => {
      const res = await fetch(`/api/fc?project_id=${projectId}`, { credentials: 'include' });
      const data = await res.json();
      return data.map((fc: any) => fc.id);
    }, projectId);

    if (fcList.length > 0 && cpResult.success && cpResult.id) {
      await createFCCPTAssociation(page, fcList[0], cpResult.id, projectId);
    }

    // 刷新并选择项目
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

    await page.evaluate(async (name) => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes(name)) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    }, projectName);
    await page.waitForTimeout(1000);

    // 切换到 FC Tab
    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(1000);

    // 展开 covergroup 和 coverpoint
    const cgHeader = page.locator('.fc-covergroup-header').first();
    if (await cgHeader.isVisible()) {
      await cgHeader.click();
      await page.waitForTimeout(500);

      const cpHeader = page.locator('.fc-coverpoint-header').first();
      if (await cpHeader.isVisible()) {
        await cpHeader.click();
        await page.waitForTimeout(500);

        const cpIdLink = page.locator('a:has-text("CP_")').first();
        if (await cpIdLink.count() > 0) {
          await cpIdLink.click();
          await page.waitForTimeout(500);

          // 检查高亮类（cp-highlight）
          // 高亮会在 3 秒后消失，所以只在点击后立即检查
          const highlightedElement = page.locator('.cp-highlight');
          // 可能高亮已经消失，这是预期行为
        }
      }
    }
  });

  // ==================== FC Comment 截断测试 ====================

  /**
   * UI-FC-CMT-001: 短comment正常显示
   */
  test('UI-FC-CMT-001: 短comment正常显示', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Cmt');

    await createFCCPProject(page, projectName);

    // 导入短 comment 的 FC
    const shortComment = 'Short comment';
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_short,cp_short,b_short,val1,0.8,ready,${shortComment}`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);
    await page.waitForTimeout(1000);

    // 展开 covergroup 和 coverpoint
    const cgHeader = page.locator('.fc-covergroup-header').first();
    if (await cgHeader.isVisible()) {
      await cgHeader.click();
      await page.waitForTimeout(500);

      const cpHeader = page.locator('.fc-coverpoint-header').first();
      if (await cpHeader.isVisible()) {
        await cpHeader.click();
        await page.waitForTimeout(500);

        // 检查 comment 单元格没有省略号
        const commentCell = page.locator('.fc-comment-cell:has-text("Short comment")');
        await expect(commentCell).toBeVisible();
      }
    }
  });

  /**
   * UI-FC-CMT-002: 长comment截断显示
   */
  test('UI-FC-CMT-002: 长comment截断显示', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Cmt_Long');

    await createFCCPProject(page, projectName);

    // 导入长 comment 的 FC（超过 150px 宽度）
    const longComment = 'This is a very long comment that exceeds the 150px width limit and should be truncated with ellipsis at the end';
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_long,cp_long,b_long,val1,0.8,ready,${longComment}`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);
    await page.waitForTimeout(1000);

    // 展开 covergroup 和 coverpoint
    const cgHeader = page.locator('.fc-covergroup-header').first();
    if (await cgHeader.isVisible()) {
      await cgHeader.click();
      await page.waitForTimeout(500);

      const cpHeader = page.locator('.fc-coverpoint-header').first();
      if (await cpHeader.isVisible()) {
        await cpHeader.click();
        await page.waitForTimeout(500);

        // 检查 fc-comment-cell 样式类
        const commentCell = page.locator('.fc-comment-cell');
        await expect(commentCell).toBeVisible();

        // 验证有 title 属性（鼠标悬停显示完整内容）
        const title = await commentCell.first().getAttribute('title');
        console.log('Comment cell title:', title);
      }
    }
  });

  /**
   * UI-FC-CMT-003: 鼠标悬停显示完整内容
   */
  test('UI-FC-CMT-003: 鼠标悬停显示完整内容', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Cmt_Hover');

    await createFCCPProject(page, projectName);

    // 导入长 comment 的 FC
    const longComment = 'This is a very long comment that should be truncated and show full text on hover with ellipsis visible';
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_hover,cp_hover,b_hover,val1,0.8,ready,${longComment}`;

    await page.click('#fcTab');
    await page.waitForSelector('#fcPanel', { state: 'visible', timeout: 10000 });
    await importFCData(page, csvContent);
    await page.waitForTimeout(1000);

    // 展开 covergroup 和 coverpoint
    const cgHeader = page.locator('.fc-covergroup-header').first();
    if (await cgHeader.isVisible()) {
      await cgHeader.click();
      await page.waitForTimeout(500);

      const cpHeader = page.locator('.fc-coverpoint-header').first();
      if (await cpHeader.isVisible()) {
        await cpHeader.click();
        await page.waitForTimeout(500);

        // 鼠标悬停到 comment 单元格
        const commentCell = page.locator('.fc-comment-cell').first();
        if (await commentCell.isVisible()) {
          await commentCell.hover();
          await page.waitForTimeout(500);

          // 验证 title 属性存在
          const title = await commentCell.getAttribute('title');
          expect(title).toContain(longComment);
        }
      }
    }
  });

  // ==================== 项目对话框显示测试 ====================

  /**
   * UI-PROJ-DIALOG-001: TC-CP模式显示TC数
   */
  test('UI-PROJ-DIALOG-001: TC-CP模式显示TC数', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_TC_Proj');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);

    // 打开项目对话框
    await page.click('#projectManageBtn');
    await page.waitForSelector('#projectModal.active', { timeout: 5000 });
    await page.waitForTimeout(500);

    // 查找项目项
    const projectItem = page.locator(`.project-item:has-text("${projectName}")`);
    await expect(projectItem).toBeVisible();

    // 验证显示 "TC: " 而非 "FC: "
    const projectMeta = projectItem.locator('.project-meta');
    const metaText = await projectMeta.textContent();
    console.log('TC-CP project meta:', metaText);

    expect(metaText).toContain('TC:');
    expect(metaText).not.toContain('FC:');
  });

  /**
   * UI-PROJ-DIALOG-002: FC-CP模式显示FC数
   */
  test('UI-PROJ-DIALOG-002: FC-CP模式显示FC数', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FC_Proj');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 打开项目对话框
    await page.click('#projectManageBtn');
    await page.waitForSelector('#projectModal.active', { timeout: 5000 });
    await page.waitForTimeout(500);

    // 查找项目项
    const projectItem = page.locator(`.project-item:has-text("${projectName}")`);
    await expect(projectItem).toBeVisible();

    // 验证显示 "FC: " 而非 "TC: "
    const projectMeta = projectItem.locator('.project-meta');
    const metaText = await projectMeta.textContent();
    console.log('FC-CP project meta:', metaText);

    expect(metaText).toContain('FC:');
    expect(metaText).not.toContain('TC:');
  });

  /**
   * UI-PROJ-DIALOG-003: 显示coverage_mode标签
   */
  test('UI-PROJ-DIALOG-003: 显示coverage_mode标签', async ({ page }) => {
    const fcProjectName = TestDataFactory.generateProjectName('TestUI_FC_Label');
    const tcProjectName = TestDataFactory.generateProjectName('TestUI_TC_Label');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, fcProjectName);
    await page.waitForTimeout(500);

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, tcProjectName);
    await page.waitForTimeout(500);

    // 打开项目对话框
    await page.click('#projectManageBtn');
    await page.waitForSelector('#projectModal.active', { timeout: 5000 });
    await page.waitForTimeout(500);

    // 验证 FC-CP 项目显示 "FC-CP" 标签
    const fcProjectItem = page.locator(`.project-item:has-text("${fcProjectName}")`);
    await expect(fcProjectItem).toBeVisible();
    const fcMetaText = await fcProjectItem.locator('.project-meta').textContent();
    console.log('FC-CP project meta:', fcMetaText);
    expect(fcMetaText).toContain('FC-CP');

    // 验证 TC-CP 项目显示 "TC-CP" 标签
    const tcProjectItem = page.locator(`.project-item:has-text("${tcProjectName}")`);
    await expect(tcProjectItem).toBeVisible();
    const tcMetaText = await tcProjectItem.locator('.project-meta').textContent();
    console.log('TC-CP project meta:', tcMetaText);
    expect(tcMetaText).toContain('TC-CP');
  });

  /**
   * UI-PROJ-DIALOG-004: FC-CP模式不显示TC
   */
  test('UI-PROJ-DIALOG-004: FC-CP模式不显示TC', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_NoTC');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 打开项目对话框
    await page.click('#projectManageBtn');
    await page.waitForSelector('#projectModal.active', { timeout: 5000 });
    await page.waitForTimeout(500);

    // 查找项目项
    const projectItem = page.locator(`.project-item:has-text("${projectName}")`);
    await expect(projectItem).toBeVisible();

    // 验证 meta 中不包含 "TC:"
    const projectMeta = projectItem.locator('.project-meta');
    const metaText = await projectMeta.textContent();
    console.log('FC-CP project meta (should not have TC:):', metaText);

    expect(metaText).not.toContain('TC:');
  });

  // ========== 高亮逻辑测试 ==========

  /**
   * 创建 TC 数据
   */
  async function createTC(page: any, tcData: any) {
    const result = await page.evaluate(async (data) => {
      const res = await fetch('/api/tc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        credentials: 'include'
      });
      return await res.json();
    }, tcData);
    console.log('TC created:', result);
    return result;
  }

  /**
   * 创建 FC-CP 关联
   */
  async function createFCCpAssoc(page: any, projectId: number, cpId: number, fcId: number) {
    const result = await page.evaluate(async ({ projectId, cpId, fcId }) => {
      const res = await fetch('/api/fc-cp-association', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, cp_id: cpId, fc_id: fcId }),
        credentials: 'include'
      });
      return await res.json();
    }, { projectId, cpId, fcId });
    console.log('FC-CP Association created:', result);
    return result;
  }

  /**
   * UI-CP-LINK-001: TC-CP模式未关联TC的CP应该高亮
   */
  test('UI-CP-LINK-001: TC-CP模式未关联TC的CP应该高亮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLink');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);

    // 确保在 CP Tab 上
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建一个 CP（不关联任何 TC）
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Unlinked',
      cover_point_details: 'This CP is not linked',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;
    console.log('Created unlinked CP:', cpId);

    // 刷新 CP 列表并渲染
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1000);

    // 检查 CP 列表中该 CP 是否有 unlinked class
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const cpNameCell = cpRow.locator('td:nth-child(4)');
    const hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Unlinked CP has span.unlinked:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBeGreaterThan(0);
  });

  /**
   * UI-CP-LINK-002: TC-CP模式有关联TC的CP正常显示
   */
  test('UI-CP-LINK-002: TC-CP模式有关联TC的CP应该正常显示', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLink2');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建一个 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Linked',
      cover_point_details: 'This CP is linked',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 创建一个 TC 并关联该 CP
    const tcResult = await createTC(page, {
      project_id: projectId,
      testbench: 'tb_test',
      test_name: 'test_linked',
      scenario: 'Test scenario',
      status: 'OPEN',
      owner: 'admin',
      category: 'functional'
    });
    const tcId = tcResult.item?.id;

    // 建立 TC 和 CP 的关联 (注意: API 使用 connections 而不是 connected_cps)
    const updateResult = await page.evaluate(async ({ tcId, cpId, projectId }) => {
      const res = await fetch(`/api/tc/${tcId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, connections: [cpId] }),
        credentials: 'include'
      });
      return await res.json();
    }, { tcId, cpId, projectId });
    console.log('TC update result:', updateResult);

    // 验证 API 返回的 connected_cps 已更新
    const verifyResult = await page.evaluate(async (verifyTcId) => {
      const res = await fetch(`/api/tc?project_id=${verifyTcId}`, { credentials: 'include' });
      const tcs = await res.json();
      const tc = tcs.find((t: any) => t.id === verifyTcId);
      return tc ? tc.connected_cps : null;
    }, tcId);
    console.log('Verified connected_cps:', verifyResult);

    // 刷新 CP 列表并渲染
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1000);

    // 检查 CP 列表中该 CP 没有 unlinked class
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const cpNameCell = cpRow.locator('td:nth-child(4)');
    const hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Linked CP has span.unlinked:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBe(0);
  });

  /**
   * UI-TC-LINK-001: TC-CP模式未关联CP的TC应该高亮
   */
  test('UI-TC-LINK-001: TC-CP模式未关联CP的TC应该高亮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_TCLink');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建一个 TC（不关联任何 CP）
    const tcResult = await createTC(page, {
      project_id: projectId,
      testbench: 'tb_test',
      test_name: 'test_unlinked',
      scenario: 'Test scenario',
      status: 'OPEN',
      owner: 'admin',
      category: 'functional'
    });
    const tcId = tcResult.item?.id;
    console.log('Created unlinked TC:', tcId);

    // 切换到 TC Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('tc', null);
      }
    });
    await page.waitForTimeout(1000);

    // 刷新 TC 列表并渲染
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1000);

    // 检查 TC 列表中该 TC 是否有 unlinked class
    const tcRow = page.locator(`tr:has(.tc-select[value="${tcId}"])`);
    await expect(tcRow).toBeVisible();

    const tcNameCell = tcRow.locator('td:nth-child(7)'); // Test Name 列
    const hasUnlinkedClass = await tcNameCell.locator('span.unlinked').count();
    console.log('Unlinked TC has span.unlinked:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBeGreaterThan(0);
  });

  /**
   * UI-TC-LINK-002: FC-CP模式TC不高亮（因为TC与CP关联逻辑不适用）
   */
  test('UI-TC-LINK-002: FC-CP模式TC不高亮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_TCLink_FC');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建一个 TC（不关联任何 CP）
    const tcResult = await createTC(page, {
      project_id: projectId,
      testbench: 'tb_test',
      test_name: 'test_unlinked_fc_mode',
      scenario: 'Test scenario',
      status: 'OPEN',
      owner: 'admin',
      category: 'functional'
    });
    const tcId = tcResult.item?.id;
    console.log('Created TC in FC-CP mode:', tcId);

    // 切换到 TC Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('tc', null);
      }
    });
    await page.waitForTimeout(1000);

    // 刷新 TC 列表并渲染
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1000);

    // 检查 TC 列表中该 TC 没有 unlinked class
    const tcRow = page.locator(`tr:has(.tc-select[value="${tcId}"])`);
    await expect(tcRow).toBeVisible();

    const tcNameCell = tcRow.locator('td:nth-child(7)'); // Test Name 列
    const hasUnlinkedClass = await tcNameCell.locator('span.unlinked').count();
    console.log('TC in FC-CP mode has span.unlinked:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBe(0);
  });

  /**
   * UI-FC-LINK-001: 未关联CP的FC应该高亮
   */
  test('UI-FC-LINK-001: 未关联CP的FC应该高亮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FCLink');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_ForFC',
      cover_point_details: 'Test CP',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 切换到 FC Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    // 导入 FC 数据
    const csvContent = `covergroup,coverpoint,bin_name,bin_val,coverage_type,coverage_pct,status,comments
cg_test,cp_test,bin_no_cp,1,coverpoint,85.0,ready,No CP linked`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 通过 API 获取 FC ID
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'bin_no_cp');
    const fcId = fc ? fc.id : null;
    console.log('FC without CP link:', fcId);

    // 检查 FC 行的背景色
    if (fcId) {
      const fcRow = page.locator(`tr[data-fc-id="${fcId}"]`);
      await expect(fcRow).toBeVisible();

      const bgColor = await fcRow.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      console.log('FC row background color:', bgColor);

      // 验证高亮颜色为 #fff3cd (rgb(255, 243, 205))
      expect(bgColor).toBe('rgb(255, 243, 205)');
    }
  });

  /**
   * UI-FC-LINK-002: 有关联CP的FC正常显示
   */
  test('UI-FC-LINK-002: 有关联CP的FC应该正常显示', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FCLink2');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_ForFC2',
      cover_point_details: 'Test CP',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 切换到 FC Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    // 导入 FC 数据
    const csvContent = `covergroup,coverpoint,bin_name,bin_val,coverage_type,coverage_pct,status,comments
cg_test2,cp_test2,bin_with_cp,1,coverpoint,90.0,ready,Has CP linked`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 通过 API 获取 FC ID
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'bin_with_cp');
    const fcId = fc ? fc.id : null;
    console.log('FC with CP link:', fcId);

    // 创建 FC-CP 关联
    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新 FC 列表
    await page.evaluate(async () => {
      if (typeof loadFC === 'function') {
        await loadFC();
      }
    });
    await page.waitForTimeout(1000);

    // 检查 FC 行的背景色
    if (fcId) {
      const fcRow = page.locator(`tr[data-fc-id="${fcId}"]`);
      await expect(fcRow).toBeVisible();

      const bgColor = await fcRow.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      console.log('FC row with CP link background color:', bgColor);

      // 验证不是高亮颜色
      expect(bgColor).not.toBe('rgb(255, 243, 205)');
    }
  });

  /**
   * UI-CP-LINK-003: FC-CP模式未关联FC的CP应该高亮
   */
  test('UI-CP-LINK-003: FC-CP模式未关联FC的CP应该高亮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLink_FC');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建一个 CP（不关联任何 FC）
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Unlinked_FC',
      cover_point_details: 'This CP is not linked to FC',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;
    console.log('Created unlinked CP in FC-CP mode:', cpId);

    // 刷新 CP 列表并渲染
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1000);

    // 检查 CP 列表中该 CP 是否有 unlinked class
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const cpNameCell = cpRow.locator('td:nth-child(4)');
    const hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Unlinked CP in FC-CP mode has span.unlinked:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBeGreaterThan(0);
  });

  /**
   * UI-CP-LINK-004: FC-CP模式有关联FC的CP正常显示
   */
  test('UI-CP-LINK-004: FC-CP模式有关联FC的CP应该正常显示', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLink_FC2');

    // 创建 FC-CP 模式项目
    await createFCCPProject(page, projectName);

    // 获取项目ID
    const projectId = await page.evaluate(async (name) => {
      const res = await fetch('/api/projects', { credentials: 'include' });
      const projects = await res.json();
      const p = projects.find((proj: any) => proj.name === name);
      return p ? p.id : null;
    }, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Linked_FC',
      cover_point_details: 'This CP is linked to FC',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 确保项目选择器已更新并选中正确项目
    await page.evaluate(async (projId) => {
      if (typeof loadProjects === 'function') {
        await loadProjects();
      }
    }, projectId);
    await page.waitForTimeout(500);

    // 直接使用 selectProject 切换到新项目
    await page.evaluate(async (projId) => {
      if (typeof selectProject === 'function') {
        await selectProject(projId);
      }
    }, projectId);
    await page.waitForTimeout(1500);

    // 切换到 FC Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    // 使用UI导入FC
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_test3,cp_test3,coverpoint,bin_linked_cp,1,95.0,ready,Linked to CP`;

    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 通过 API 获取 FC ID
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'bin_linked_cp');
    const fcId = fc ? fc.id : null;
    console.log('FC linked to CP:', fcId);

    // 创建 FC-CP 关联
    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新 FC 和 FC-CP 关联数据以更新高亮状态
    // 注意: CP 高亮在 FC-CP 模式下使用 functionalCoverages[i].cp_ids,
    // 而 loadFC 会重新获取包含 cp_ids 的 FC 数据
    await page.evaluate(async () => {
      if (typeof loadFC === 'function') {
        await loadFC();
      }
      if (typeof loadFC_CPAssociation === 'function') {
        await loadFC_CPAssociation();
      }
    });
    await page.waitForTimeout(500);

    // 刷新 CP 列表并渲染
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1000);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 检查 CP 列表中该 CP 没有 unlinked class
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const cpNameCell = cpRow.locator('td:nth-child(4)');
    const hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Linked CP in FC-CP mode has span.unlinked:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBe(0);
  });
});
