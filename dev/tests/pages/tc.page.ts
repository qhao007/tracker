import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

/**
 * TC (Test Case) 管理页面对象
 * 封装 TC 管理页面的所有操作
 */
export class TCPage extends BasePage {
  readonly baseURL = 'http://localhost:8081';

  // 标签和导航
  readonly tcTab = 'text=Test Cases';
  readonly addTCBtn = 'text=添加 Test Case';

  // TC 表格
  readonly tcTable = 'table'; // 实际 HTML 中的表格元素
  readonly tcTableBody = '.tc-table tbody';
  readonly tcTableRows = 'table tbody tr';
  readonly tcSelectAll = '#tcSelectAll';
  readonly expandBtn = '.tc-expand-btn';
  readonly collapseBtn = '.tc-collapse-btn';
  readonly tcDetailArea = '.tc-detail-area';

  // TC 模态框
  readonly tcModal = '#tcModal';
  readonly tcForm = '#tcForm';
  readonly tcTestbench = '#tcTestbench';
  readonly tcTestName = '#tcTestName';
  readonly tcScenario = '#tcScenario';
  readonly tcOwner = '#tcOwner';
  readonly tcCategory = '#tcCategory';
  readonly tcDvMilestone = '#tcDvMilestone';
  readonly tcTargetDate = '#tcTargetDate';
  readonly tcStatus = '.status-select'; // 状态选择器
  readonly tcSubmitBtn = '#tcSubmitBtn';
  readonly tcCancelBtn = '#tcCancelBtn';
  readonly modalClose = '#tcModal .modal-close';

  // 过滤
  readonly statusFilter = '#tcStatusFilter';
  readonly ownerFilter = '#tcOwnerFilter';
  readonly categoryFilter = '#tcCategoryFilter';
  readonly featureFilter = '#tcFeatureFilter';
  readonly searchBtn = '#tcSearchBtn';

  // 批量操作
  readonly batchUpdateBtn = '#tcBatchUpdate';
  readonly batchStatusBtn = '#tcBatchStatusUpdate';
  readonly batchDateBtn = '#tcBatchDateUpdate';
  readonly batchStatusSelect = '#tcBatchStatusSelect';
  readonly batchDateInput = '#tcBatchDateInput';

  // 行操作
  readonly rowCheckbox = '.tc-row-checkbox';
  readonly editBtn = '.tc-edit-btn';
  readonly deleteBtn = '.tc-delete-btn';

  async navigate(): Promise<void> {
    await this.page.goto(this.baseURL);
    await this.waitForLoad();
    await this.waitForSelector('#projectSelector');
  }

  /**
   * 切换到 TC 标签页
   */
  async switchToTCTab(): Promise<void> {
    await this.page.click(this.tcTab);
    await this.page.waitForTimeout(500);
  }

  /**
   * 打开添加 TC 模态框
   */
  async openTCModal(): Promise<void> {
    await this.page.click(this.addTCBtn);
    await this.waitForSelector(this.tcModal);
  }

  /**
   * 关闭 TC 模态框
   */
  async closeTCModal(): Promise<void> {
    await this.page.click(this.modalClose);
    await this.waitForElementHidden(this.tcModal);
  }

  /**
   * 创建 TC
   */
  async createTC(data: {
    testbench: string;
    testName: string;
    scenario?: string;
    owner?: string;
    category?: string;
    dvMilestone?: string;
    targetDate?: string;
  }): Promise<void> {
    await this.switchToTCTab();
    await this.openTCModal();

    await this.page.fill(this.tcTestbench, data.testbench);
    await this.page.fill(this.tcTestName, data.testName);

    if (data.scenario) {
      await this.page.fill(this.tcScenario, data.scenario);
    }
    if (data.owner) {
      await this.page.fill(this.tcOwner, data.owner);
    }
    if (data.category) {
      await this.page.selectOption(this.tcCategory, data.category);
    }
    if (data.dvMilestone) {
      await this.page.selectOption(this.tcDvMilestone, data.dvMilestone);
    }
    if (data.targetDate) {
      await this.page.fill(this.tcTargetDate, data.targetDate);
    }

    await this.page.click(this.tcSubmitBtn);
    await this.page.waitForTimeout(500);

    // 验证创建成功
    await expect(
      this.page.locator(`${this.tcTableRows}:has-text("${data.testName}")`)
    ).toBeVisible();
  }

  /**
   * 编辑 TC
   */
  async editTC(
    testName: string,
    updates: {
      testbench?: string;
      testName?: string;
      scenario?: string;
      owner?: string;
      category?: string;
      dvMilestone?: string;
      targetDate?: string;
    }
  ): Promise<void> {
    await this.switchToTCTab();

    // 点击编辑按钮
    await this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") ${this.editBtn}`
    ).click();
    await this.waitForSelector(this.tcModal);

    // 更新字段
    if (updates.testbench) {
      await this.page.fill(this.tcTestbench, updates.testbench);
    }
    if (updates.testName) {
      await this.page.fill(this.tcTestName, updates.testName);
    }
    if (updates.scenario) {
      await this.page.fill(this.tcScenario, updates.scenario);
    }
    if (updates.owner) {
      await this.page.fill(this.tcOwner, updates.owner);
    }
    if (updates.category) {
      await this.page.selectOption(this.tcCategory, updates.category);
    }
    if (updates.dvMilestone) {
      await this.page.selectOption(this.tcDvMilestone, updates.dvMilestone);
    }
    if (updates.targetDate) {
      await this.page.fill(this.tcTargetDate, updates.targetDate);
    }

    await this.page.click(this.tcSubmitBtn);
    await this.page.waitForTimeout(500);
  }

  /**
   * 删除 TC
   */
  async deleteTC(testName: string): Promise<void> {
    await this.switchToTCTab();

    // 确认存在
    await expect(
      this.page.locator(`${this.tcTableRows}:has-text("${testName}")`)
    ).toBeVisible();

    // 点击删除按钮
    await this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") ${this.deleteBtn}`
    ).click();

    // 处理确认对话框
    this.page.on('dialog', async dialog => {
      await dialog.accept();
    });

    await this.page.waitForTimeout(500);

    // 验证已删除
    await expect(
      this.page.locator(`${this.tcTableRows}:has-text("${testName}")`)
    ).toBeHidden();
  }

  /**
   * 验证 TC 存在
   */
  async expectTCExists(testName: string): Promise<void> {
    await this.switchToTCTab();
    await expect(
      this.page.locator(`${this.tcTableRows}:has-text("${testName}")`)
    ).toBeVisible();
  }

  /**
   * 验证 TC 不存在
   */
  async expectTCNotExists(testName: string): Promise<void> {
    await this.switchToTCTab();
    await expect(
      this.page.locator(`${this.tcTableRows}:has-text("${testName}")`)
    ).toBeHidden();
  }

  /**
   * 按状态过滤
   */
  async filterByStatus(status: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.selectOption(this.statusFilter, status);
    await this.page.waitForTimeout(300);
  }

  /**
   * 按 Owner 过滤
   */
  async filterByOwner(owner: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.fill(this.ownerFilter, owner);
    await this.page.click(this.searchBtn);
    await this.page.waitForTimeout(300);
  }

  /**
   * 按 Category 过滤
   */
  async filterByCategory(category: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.selectOption(this.categoryFilter, category);
    await this.page.waitForTimeout(300);
  }

  /**
   * 按 Feature 过滤
   */
  async filterByFeature(feature: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.fill(this.featureFilter, feature);
    await this.page.click(this.searchBtn);
    await this.page.waitForTimeout(300);
  }

  /**
   * 清空过滤
   */
  async clearFilters(): Promise<void> {
    await this.switchToTCTab();
    await this.page.selectOption(this.statusFilter, '');
    await this.page.fill(this.ownerFilter, '');
    await this.page.selectOption(this.categoryFilter, '');
    await this.page.fill(this.featureFilter, '');
    await this.page.click(this.searchBtn);
    await this.page.waitForTimeout(300);
  }

  /**
   * 获取 TC 表格行数
   */
  async getTCCount(): Promise<number> {
    await this.switchToTCTab();
    return await this.page.locator(this.tcTableRows).count();
  }

  /**
   * 展开 TC 详情
   */
  async expandTCDetail(testName: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") ${this.expandBtn}`
    ).click();
    await this.page.waitForTimeout(300);
  }

  /**
   * 折叠 TC 详情
   */
  async collapseTCDetail(testName: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") ${this.collapseBtn}`
    ).click();
    await this.page.waitForTimeout(300);
  }

  /**
   * 验证 TC 详情显示
   */
  async expectTCDetailVisible(testName: string): Promise<void> {
    await expect(
      this.page.locator(`${this.tcTableRows}:has-text("${testName}") ${this.tcDetailArea}`)
    ).toBeVisible();
  }

  /**
   * 验证 TC 详情隐藏
   */
  async expectTCDetailHidden(testName: string): Promise<void> {
    await expect(
      this.page.locator(`${this.tcTableRows}:has-text("${test.tcDetailAreaName}") ${this}`)
    ).toBeHidden();
  }

  /**
   * 获取 TC 状态
   */
  async getTCStatus(testName: string): Promise<string> {
    await this.switchToTCTab();
    const statusCell = this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") .status-badge`
    );
    return (await statusCell.textContent()) || '';
  }

  /**
   * 更新 TC 状态
   */
  async updateTCStatus(testName: string, status: string): Promise<void> {
    await this.switchToTCTab();
    
    // 点击状态选择器
    await this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") ${this.tcStatus}`
    ).selectOption(status);
    
    await this.page.waitForTimeout(500);
  }

  /**
   * 全选 TC
   */
  async selectAllTC(): Promise<void> {
    await this.switchToTCTab();
    await this.page.check(this.tcSelectAll);
    await this.page.waitForTimeout(200);
  }

  /**
   * 批量更新状态
   */
  async batchUpdateStatus(status: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.click(this.batchStatusBtn);
    await this.page.selectOption(this.batchStatusSelect, status);
    await this.page.waitForTimeout(500);
  }

  /**
   * 批量更新日期
   */
  async batchUpdateDate(date: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.click(this.batchDateBtn);
    await this.page.fill(this.batchDateInput, date);
    await this.page.waitForTimeout(500);
  }

  /**
   * 选择特定 TC 行
   */
  async selectTCRow(testName: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") ${this.rowCheckbox}`
    ).check();
    await this.page.waitForTimeout(200);
  }

  /**
   * 验证模态框打开
   */
  async expectModalVisible(): Promise<void> {
    await expect(this.page.locator(this.tcModal)).toBeVisible();
  }

  /**
   * 验证模态框关闭
   */
  async expectModalHidden(): Promise<void> {
    await this.waitForElementHidden(this.tcModal);
  }

  /**
   * 验证必填字段校验
   */
  async expectValidationError(): Promise<void> {
    // 尝试提交不完整的表单
    await this.page.click(this.tcSubmitBtn);
    await this.page.waitForTimeout(300);

    // 验证模态框仍然打开
    await this.expectModalVisible();
  }

  /**
   * 切换 TC 状态（点击状态按钮）
   */
  async toggleTCStatus(testName: string): Promise<void> {
    await this.switchToTCTab();
    await this.page.locator(
      `${this.tcTableRows}:has-text("${testName}") .status-toggle`
    ).click();
    await this.page.waitForTimeout(300);
  }
}
