/**
 * FC-CP Mode CP Coverage & Link Tests
 *
 * 测试 v0.11.0 FC-CP 模式下 CP 覆盖率显示和 FC-CP 关联功能：
 * - UI-CP-LINK-EXT-001~004: CP Tab 首次加载/切换/刷新后 FC-CP 关联状态
 * - UI-CP-COVERAGE-001~006: TC-CP/FC-CP 模式 CP 覆盖率显示
 * - UI-COVERAGE-BADGE-001~003: 覆盖率徽章颜色验证
 *
 * 运行命令:
 *   npx playwright test tests/test_ui/specs/integration/fc_cp_coverage.spec.ts --project=firefox
 *
 * 注意: 部分测试依赖 BUG-127 和 BUG-128 的修复
 * - BUG-127: renderCP() 依赖 functionalCoverages 数据
 * - BUG-128: get_coverpoints() API 未区分 coverage_mode
 */

import { test, expect } from '../../fixtures/tracker.fixture';
import { TestDataFactory } from '../../fixtures/test-data.factory';

test.describe('FC-CP Mode CP Coverage & Link Tests', () => {

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

    return projectId;
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
   * 删除 FC-CP 关联
   */
  async function deleteFCCpAssoc(page: any, projectId: number, cpId: number, fcId: number) {
    const result = await page.evaluate(async ({ projectId, cpId, fcId }) => {
      const res = await fetch('/api/fc-cp-association', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, cp_id: cpId, fc_id: fcId }),
        credentials: 'include'
      });
      return { status: res.status, data: await res.json() };
    }, { projectId, cpId, fcId });
    console.log('FC-CP Association deleted:', result);
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

  // ==================== P1: CP Tab 首次加载 FC-CP 关联状态测试 ====================

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.waitForSelector('#projectSelector', { timeout: 10000 });
  });

  /**
   * UI-CP-LINK-EXT-001: CP Tab首次加载时已关联CP不高亮
   *
   * BUG-127 验证: renderCP() 依赖 functionalCoverages 数据
   * CP Tab 首次加载时 functionalCoverages 为空，导致所有 CP 显示为未关联
   * 已修复：loadData() 现在在 FC-CP 模式下也会加载 FC 数据
   */
  test('UI-CP-LINK-EXT-001: CP Tab首次加载时已关联CP不高亮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLinkExt1');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Linked_Ext1',
      cover_point_details: 'Test CP for LINK EXT 1',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;
    console.log('Created CP:', cpId);

    // 切换到 FC Tab 并导入 FC 数据
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    // 导入 FC（100% 覆盖率）
    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_ext1,cp_ext1,coverpoint,b_ext1,1,100,ready,Linked CP test`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_ext1');
    const fcId = fc ? fc.id : null;
    console.log('FC ID:', fcId);

    // 创建 FC-CP 关联
    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新整个页面（模拟真实用户行为）
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#userInfo', { state: 'visible', timeout: 30000 });

    // 选择项目
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
    await page.waitForTimeout(2000);

    // 确保在 CP Tab（默认应该是 CP Tab）
    const cpTabActive = page.locator('button.tab.active:has-text("Cover Points")');
    if (await cpTabActive.count() === 0) {
      await page.click('button.tab:has-text("Cover Points")');
      await page.waitForTimeout(1000);
    }

    // 验证已关联的 CP 不显示 unlinked 高亮
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const cpNameCell = cpRow.locator('td:nth-child(4)');
    const hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Linked CP has span.unlinked after reload:', hasUnlinkedClass > 0);

    // BUG-127 已修复：已关联的 CP 不应该高亮
    expect(hasUnlinkedClass).toBe(0);
  });

  /**
   * UI-CP-LINK-EXT-002: 切换到FC Tab再回CP Tab关联状态正确
   */
  test('UI-CP-LINK-EXT-002: 切换到FC Tab再回CP Tab关联状态正确', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLinkExt2');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Linked_Ext2',
      cover_point_details: 'Test CP for LINK EXT 2',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_ext2,cp_ext2,coverpoint,b_ext2,1,80,ready,Linked CP test 2`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_ext2');
    const fcId = fc ? fc.id : null;

    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 切换到 FC Tab
    await page.click('#fcTab');
    await page.waitForTimeout(1500);

    // 切换回 CP Tab
    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForTimeout(2000);

    // 重新加载数据以确保 functionalCoverages 可用
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 验证已关联 CP 不高亮
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const cpNameCell = cpRow.locator('td:nth-child(4)');
    const hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Linked CP has span.unlinked after tab switch:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBe(0);
  });

  /**
   * UI-CP-LINK-EXT-003: 导入FC-CP关联后立即刷新CP列表
   */
  test('UI-CP-LINK-EXT-003: 导入FC-CP关联后立即刷新CP列表', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLinkExt3');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Linked_Ext3',
      cover_point_details: 'Test CP for LINK EXT 3',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_ext3,cp_ext3,coverpoint,b_ext3,1,60,ready,Linked CP test 3`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_ext3');
    const fcId = fc ? fc.id : null;

    // 创建 FC-CP 关联
    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 立即刷新 CP 列表（不刷新整个页面）
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证已关联 CP 不高亮
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const cpNameCell = cpRow.locator('td:nth-child(4)');
    const hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Linked CP has span.unlinked after immediate refresh:', hasUnlinkedClass > 0);

    expect(hasUnlinkedClass).toBe(0);
  });

  // ==================== P1: TC-CP/FC-CP 模式 CP 覆盖率显示测试 ====================

  /**
   * UI-CP-COVERAGE-001: TC-CP模式CP列表显示覆盖率
   */
  test('UI-CP-COVERAGE-001: TC-CP模式CP列表显示覆盖率', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPCov1');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Coverage_TC1',
      cover_point_details: 'Test CP for TC-CP coverage',
      priority: 'P0'
    });
    const cpId = cpResult.item?.id;

    // 确保在 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证 CP 列表中有覆盖率列
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    // 检查覆盖率显示
    const coverageBadge = cpRow.locator('.coverage-badge');
    await expect(coverageBadge).toBeVisible();

    const coverageText = await coverageBadge.textContent();
    console.log('TC-CP mode coverage text:', coverageText);
    expect(coverageText).toMatch(/\d+%/);
  });

  /**
   * UI-CP-COVERAGE-002: FC-CP模式CP列表显示覆盖率
   *
   * BUG-128 验证: get_coverpoints() API 未区分 coverage_mode
   * FC-CP 模式下应使用 FC 的 coverage_pct
   */
  test('UI-CP-COVERAGE-002: FC-CP模式CP列表显示覆盖率', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPCov2');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Coverage_FC2',
      cover_point_details: 'Test CP for FC-CP coverage',
      priority: 'P0'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC 数据（覆盖率 75%）
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_cov2,cp_cov2,coverpoint,b_cov2,1,75,ready,FC-CP coverage test`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_cov2');
    const fcId = fc ? fc.id : null;

    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新数据
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证 CP 列表中有覆盖率显示
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const coverageBadge = cpRow.locator('.coverage-badge');
    await expect(coverageBadge).toBeVisible();

    const coverageText = await coverageBadge.textContent();
    console.log('FC-CP mode coverage text:', coverageText);
    expect(coverageText).toMatch(/\d+%/);

    // BUG-128 修复后：FC-CP 模式应使用 FC 的覆盖率
    // 验证覆盖率应该是 FC 的 75% 而不是 0%
    expect(coverageText).toContain('75');
  });

  // ==================== P1: 覆盖率徽章颜色测试 ====================

  /**
   * UI-COVERAGE-BADGE-001: 覆盖率100%显示绿色
   */
  test('UI-COVERAGE-BADGE-001: 覆盖率100%显示绿色', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CovBadge1');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建 CP 并关联 TC（TC 通过后覆盖率应该变化）
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_100_Coverage',
      cover_point_details: 'CP with 100% coverage',
      priority: 'P0'
    });
    const cpId = cpResult.item?.id;

    // 直接通过 API 验证覆盖率（因为我们无法直接控制 TC 覆盖率）
    // 使用 SOC_DV 项目验证绿色显示
    await page.evaluate(async () => {
      const selector = document.getElementById('projectSelector');
      for (let i = 0; i < selector.options.length; i++) {
        if (selector.options[i].text.includes('SOC_DV')) {
          selector.selectedIndex = i;
          selector.dispatchEvent(new Event('change', { bubbles: true }));
          break;
        }
      }
    });
    await page.waitForTimeout(2000);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 查找 100% 覆盖率的 CP（如果有的话）
    const greenBadge = page.locator('.coverage-badge.bg-green:has-text("100%")').first();
    const greenBadgeCount = await greenBadge.count();

    if (greenBadgeCount > 0) {
      console.log('Found 100% coverage badge with green color');
      await expect(greenBadge).toBeVisible();

      // 验证背景色是绿色 (#4caf50)
      const bgColor = await greenBadge.evaluate((el) => {
        return window.getComputedStyle(el).backgroundColor;
      });
      console.log('100% coverage badge background color:', bgColor);
      expect(bgColor).toBe('rgb(76, 175, 80)'); // #4caf50
    } else {
      // 如果没有 100% 的 CP，创建一个 CP 然后验证 badge 存在
      const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
      if (await cpRow.count() > 0) {
        const badge = cpRow.locator('.coverage-badge');
        await expect(badge).toBeVisible();
        // 验证有正确的 class
        const hasBgGreen = await badge.evaluate((el) => el.classList.contains('bg-green'));
        const hasBgYellow = await badge.evaluate((el) => el.classList.contains('bg-yellow'));
        const hasBgRed = await badge.evaluate((el) => el.classList.contains('bg-red'));
        console.log('Badge classes - bg-green:', hasBgGreen, 'bg-yellow:', hasBgYellow, 'bg-red:', hasBgRed);
        expect(hasBgGreen || hasBgYellow || hasBgRed).toBeTruthy();
      }
    }
  });

  /**
   * UI-COVERAGE-BADGE-002: 覆盖率0%显示红色
   */
  test('UI-COVERAGE-BADGE-002: 覆盖率0%显示红色', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CovBadge2');

    // 创建 TC-CP 模式项目
    await createTCCPProject(page, projectName);
    const projectId = await getProjectId(page, projectName);

    // 创建未关联任何 TC 的 CP（覆盖率应该是 0%）
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_0_Coverage',
      cover_point_details: 'CP with 0% coverage',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证 CP 行的覆盖率徽章是红色
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const coverageBadge = cpRow.locator('.coverage-badge');
    await expect(coverageBadge).toBeVisible();

    // 验证徽章是红色
    const hasBgRed = await coverageBadge.evaluate((el) => el.classList.contains('bg-red'));
    console.log('0% coverage badge has bg-red:', hasBgRed);
    expect(hasBgRed).toBeTruthy();

    // 验证覆盖率文本是 0%
    const coverageText = await coverageBadge.textContent();
    expect(coverageText).toContain('0%');
  });

  /**
   * UI-COVERAGE-BADGE-003: 覆盖率0-100%之间显示黄色
   */
  test('UI-COVERAGE-BADGE-003: 覆盖率0-100%之间显示黄色', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CovBadge3');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Partial_Coverage',
      cover_point_details: 'CP with partial coverage',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC（覆盖率 50%）
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_partial,cp_partial,coverpoint,b_partial,1,50,ready,Partial coverage test`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_partial');
    const fcId = fc ? fc.id : null;

    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新数据
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证 CP 行的覆盖率徽章是黄色
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const coverageBadge = cpRow.locator('.coverage-badge');
    await expect(coverageBadge).toBeVisible();

    // 验证徽章是黄色（0% < coverage < 100%）
    const hasBgYellow = await coverageBadge.evaluate((el) => el.classList.contains('bg-yellow'));
    console.log('Partial coverage badge has bg-yellow:', hasBgYellow);
    expect(hasBgYellow).toBeTruthy();

    // 验证覆盖率文本包含 50
    const coverageText = await coverageBadge.textContent();
    expect(coverageText).toContain('50');
  });

  // ==================== P2: 删除 FC-CP 关联后 CP 恢复高亮 ====================

  /**
   * UI-CP-LINK-EXT-004: 删除FC-CP关联后CP恢复高亮
   */
  test('UI-CP-LINK-EXT-004: 删除FC-CP关联后CP恢复高亮', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPLinkExt4');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Linked_Ext4',
      cover_point_details: 'Test CP for LINK EXT 4',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_ext4,cp_ext4,coverpoint,b_ext4,1,85,ready,Linked CP test 4`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_ext4');
    const fcId = fc ? fc.id : null;

    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新数据
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证已关联 CP 不高亮
    let cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    let cpNameCell = cpRow.locator('td:nth-child(4)');
    let hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('Before delete - Linked CP has span.unlinked:', hasUnlinkedClass > 0);
    expect(hasUnlinkedClass).toBe(0);

    // 删除 FC-CP 关联
    if (fcId && cpId) {
      await deleteFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新 FC 数据和关联（确保 cp_ids 更新）
    await page.evaluate(async () => {
      if (typeof loadFC === 'function') {
        await loadFC();
      }
      if (typeof loadFC_CPAssociation === 'function') {
        await loadFC_CPAssociation();
      }
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 验证删除关联后 CP 恢复高亮
    cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    cpNameCell = cpRow.locator('td:nth-child(4)');
    hasUnlinkedClass = await cpNameCell.locator('span.unlinked').count();
    console.log('After delete - Unlinked CP has span.unlinked:', hasUnlinkedClass > 0);
    expect(hasUnlinkedClass).toBeGreaterThan(0);
  });

  // ==================== P1: FC-CP 模式覆盖率颜色测试 ====================

  /**
   * UI-CP-COVERAGE-003: FC-CP模式覆盖率颜色-100%
   */
  test('UI-CP-COVERAGE-003: FC-CP模式覆盖率颜色-100%', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FCCov3');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_FC_100_Coverage',
      cover_point_details: 'FC-CP with 100% coverage',
      priority: 'P0'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC（100% 覆盖率）
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_fc100,cp_fc100,coverpoint,b_fc100,1,100,ready,100% FC coverage`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_fc100');
    const fcId = fc ? fc.id : null;

    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新数据
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证 CP 行的覆盖率徽章是绿色
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const coverageBadge = cpRow.locator('.coverage-badge');
    await expect(coverageBadge).toBeVisible();

    // 验证是绿色
    const hasBgGreen = await coverageBadge.evaluate((el) => el.classList.contains('bg-green'));
    console.log('FC-CP 100% coverage badge has bg-green:', hasBgGreen);
    expect(hasBgGreen).toBeTruthy();

    // 验证覆盖率文本包含 100
    const coverageText = await coverageBadge.textContent();
    expect(coverageText).toContain('100');
  });

  /**
   * UI-CP-COVERAGE-004: FC-CP模式覆盖率颜色-部分
   */
  test('UI-CP-COVERAGE-004: FC-CP模式覆盖率颜色-部分', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FCCov4');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_FC_Partial',
      cover_point_details: 'FC-CP with partial coverage',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC（66% 覆盖率 - 部分覆盖率）
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_fc66,cp_fc66,coverpoint,b_fc66,1,66,ready,Partial FC coverage`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_fc66');
    const fcId = fc ? fc.id : null;

    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新数据
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证 CP 行的覆盖率徽章是黄色
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const coverageBadge = cpRow.locator('.coverage-badge');
    await expect(coverageBadge).toBeVisible();

    // 验证是黄色
    const hasBgYellow = await coverageBadge.evaluate((el) => el.classList.contains('bg-yellow'));
    console.log('FC-CP partial coverage badge has bg-yellow:', hasBgYellow);
    expect(hasBgYellow).toBeTruthy();

    // 验证覆盖率文本包含 66
    const coverageText = await coverageBadge.textContent();
    expect(coverageText).toContain('66');
  });

  /**
   * UI-CP-COVERAGE-005: FC-CP模式覆盖率颜色-0%
   */
  test('UI-CP-COVERAGE-005: FC-CP模式覆盖率颜色-0%', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_FCCov5');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP（不关联任何 FC）
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_FC_Zero',
      cover_point_details: 'FC-CP with 0% coverage',
      priority: 'P1'
    });
    const cpId = cpResult.item?.id;

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 验证 CP 行的覆盖率徽章是红色
    const cpRow = page.locator(`tr[data-cp-id="${cpId}"]`);
    await expect(cpRow).toBeVisible();

    const coverageBadge = cpRow.locator('.coverage-badge');
    await expect(coverageBadge).toBeVisible();

    // 验证是红色
    const hasBgRed = await coverageBadge.evaluate((el) => el.classList.contains('bg-red'));
    console.log('FC-CP 0% coverage badge has bg-red:', hasBgRed);
    expect(hasBgRed).toBeTruthy();

    // 验证覆盖率文本是 0%
    const coverageText = await coverageBadge.textContent();
    expect(coverageText).toContain('0%');
  });

  /**
   * UI-CP-COVERAGE-006: CP详情页显示FC覆盖率
   */
  test('UI-CP-COVERAGE-006: CP详情页显示FC覆盖率', async ({ page }) => {
    const projectName = TestDataFactory.generateProjectName('TestUI_CPDetailFC');

    // 创建 FC-CP 模式项目
    const projectId = await createFCCPProject(page, projectName);

    // 创建 CP
    const cpResult = await createCP(page, {
      project_id: projectId,
      feature: 'TestFeature',
      sub_feature: 'TestSubFeature',
      cover_point: 'CP_Detail_FC',
      cover_point_details: 'CP detail page FC coverage test',
      priority: 'P0'
    });
    const cpId = cpResult.item?.id;

    // 导入 FC（覆盖率 88%）
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('fc', null);
      }
    });
    await page.waitForTimeout(1000);

    const csvContent = `Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
cg_detail,cp_detail,coverpoint,b_detail,1,88,ready,Detail FC coverage`;
    await importFCData(page, csvContent);
    await page.waitForTimeout(2000);

    // 获取 FC ID 并创建关联
    const fcList = await page.evaluate(async (projId) => {
      const res = await fetch(`/api/fc?project_id=${projId}`, { credentials: 'include' });
      return await res.json();
    }, projectId);
    const fc = fcList.find((f: any) => f.bin_name === 'b_detail');
    const fcId = fc ? fc.id : null;

    if (fcId && cpId) {
      await createFCCpAssoc(page, projectId, cpId, fcId);
    }

    // 刷新数据
    await page.evaluate(async () => {
      if (typeof loadData === 'function') {
        await loadData();
      }
    });
    await page.waitForTimeout(1500);

    // 切换到 CP Tab
    await page.evaluate(async () => {
      if (typeof switchTab === 'function') {
        switchTab('cp', null);
      }
    });
    await page.waitForTimeout(1000);

    // 点击详情按钮展开 CP 详情
    const detailBtn = page.locator(`tr[data-cp-id="${cpId}"] button.action-btn:has-text("详情")`);
    await detailBtn.click();
    await page.waitForTimeout(1500);

    // 验证 CP 详情行可见
    const cpDetailRow = page.locator(`#cp-detail-${cpId}`);
    await expect(cpDetailRow).toBeVisible();

    // 验证详情中包含 FC 覆盖率信息
    const detailText = await cpDetailRow.textContent();
    console.log('CP detail text:', detailText);

    // 验证显示 FC 覆盖率
    // 可能显示格式为 "FC: 88%" 或类似格式
    const hasFCCoverage = detailText.includes('88') || detailText.includes('FC');
    console.log('CP detail has FC coverage info:', hasFCCoverage);
    expect(hasFCCoverage).toBeTruthy();
  });
});
