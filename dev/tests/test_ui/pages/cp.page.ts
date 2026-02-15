import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

/**
 * CP (Cover Point) 管理页面对象
 * 封装 CP 管理页面的所有操作
 */
export class CPPage extends BasePage {
  readonly baseURL = 'http://localhost:8081';

  // 标签和导航
  readonly cpTab = '.tabs button.tab:has-text("Cover Points")';
  readonly addCPBtn = 'button:has-text("+ 添加 CP")';

  // CP 表格
  readonly cpTable = '.cp-table';
  readonly cpTableRows = '.cp-table tbody tr';
  readonly cpSelectAll = '#cpSelectAll';
  readonly expandBtn = '.expand-btn';
  readonly collapseBtn = '.collapse-btn';
  readonly cpDetailArea = '.cp-detail-area';

  // CP 模态框
  readonly cpModal = '#cpModal';
  readonly cpForm = '#cpForm';
  readonly cpFeature = '#cpFeature';
  readonly cpCoverPoint = '#cpCoverPoint';
  readonly cpDetails = '#cpDetails';
  readonly cpPriority = '#cpPriority';
  readonly cpSubmitBtn = '#cpForm button[type="submit"]';
  readonly modalClose = '#cpModal .modal-close';

  // 过滤
  readonly featureFilter = '#cpFeatureFilter';
  readonly priorityFilter = '#cpPriorityFilter';
  readonly searchBtn = '#cpSearchBtn';

  // 批量操作
  readonly batchUpdateBtn = '#cpBatchUpdate';
  readonly batchPrioritySelect = '#cpBatchPriority';

  async navigate(): Promise<void> {
    await this.page.goto(this.baseURL);
    await this.waitForLoad();
    await this.waitForSelector('#projectSelector');
  }

  /**
   * 切换到 CP 标签页
   */
  async switchToCPTab(): Promise<void> {
    // 直接点击 CP 标签（Playwright 会处理重复点击的情况）
    await this.page.click('button.tab:has-text("Cover Points")');
    // 等待面板切换
    await this.page.waitForTimeout(1000);
  }

  /**
   * 打开添加 CP 模态框
   */
  async openCPModal(): Promise<void> {
    await this.page.click(this.addCPBtn);
    await this.waitForSelector(this.cpModal);
  }

  /**
   * 关闭 CP 模态框
   */
  async closeCPModal(): Promise<void> {
    await this.page.click(this.modalClose);
    await this.waitForElementHidden(this.cpModal);
  }

  /**
   * 创建 CP
   */
  async createCP(data: {
    feature: string;
    coverPoint: string;
    details?: string;
    priority?: string;
  }): Promise<void> {
    await this.switchToCPTab();
    await this.openCPModal();

    await this.page.fill(this.cpFeature, data.feature);
    await this.page.fill(this.cpCoverPoint, data.coverPoint);
    
    if (data.details) {
      await this.page.fill(this.cpDetails, data.details);
    }
    
    if (data.priority) {
      await this.page.selectOption(this.cpPriority, data.priority);
    }

    await this.page.click(this.cpSubmitBtn);
    await this.page.waitForTimeout(500);

    // 验证创建成功
    await expect(
      this.page.locator(`${this.cpTableRows}:has-text("${data.coverPoint}")`)
    ).toBeVisible();
  }

  /**
   * 编辑 CP
   */
  async editCP(
    coverPoint: string,
    updates: {
      feature?: string;
      coverPoint?: string;
      details?: string;
      priority?: string;
    }
  ): Promise<void> {
    await this.switchToCPTab();

    // 点击编辑按钮
    await this.page.locator(
      `${this.cpTableRows}:has-text("${coverPoint}") .cp-edit-btn`
    ).click();
    await this.waitForSelector(this.cpModal);

    // 更新字段
    if (updates.feature) {
      await this.page.fill(this.cpFeature, updates.feature);
    }
    if (updates.coverPoint) {
      await this.page.fill(this.cpCoverPoint, updates.coverPoint);
    }
    if (updates.details) {
      await this.page.fill(this.cpDetails, updates.details);
    }
    if (updates.priority) {
      await this.page.selectOption(this.cpPriority, updates.priority);
    }

    await this.page.click(this.cpSubmitBtn);
    await this.page.waitForTimeout(500);
  }

  /**
   * 删除 CP
   */
  async deleteCP(coverPoint: string): Promise<void> {
    await this.switchToCPTab();

    // 确认存在
    await expect(
      this.page.locator(`${this.cpTableRows}:has-text("${coverPoint}")`)
    ).toBeVisible();

    // 点击删除按钮并确认
    await this.page.locator(
      `${this.cpTableRows}:has-text("${coverPoint}") .cp-delete-btn`
    ).click();

    // 处理确认对话框
    this.page.on('dialog', async dialog => {
      await dialog.accept();
    });

    await this.page.waitForTimeout(500);

    // 验证已删除
    await expect(
      this.page.locator(`${this.cpTableRows}:has-text("${coverPoint}")`)
    ).toBeHidden();
  }

  /**
   * 验证 CP 存在
   */
  async expectCPExists(coverPoint: string): Promise<void> {
    await this.switchToCPTab();
    await expect(
      this.page.locator(`${this.cpTableRows}:has-text("${coverPoint}")`)
    ).toBeVisible();
  }

  /**
   * 验证 CP 不存在
   */
  async expectCPNotExists(coverPoint: string): Promise<void> {
    await this.switchToCPTab();
    await expect(
      this.page.locator(`${this.cpTableRows}:has-text("${coverPoint}")`)
    ).toBeHidden();
  }

  /**
   * 按 feature 过滤
   */
  async filterByFeature(feature: string): Promise<void> {
    await this.switchToCPTab();
    await this.page.fill(this.featureFilter, feature);
    await this.page.click(this.searchBtn);
    await this.page.waitForTimeout(300);
  }

  /**
   * 按 priority 过滤
   */
  async filterByPriority(priority: string): Promise<void> {
    await this.switchToCPTab();
    await this.page.selectOption(this.priorityFilter, priority);
    await this.page.waitForTimeout(300);
  }

  /**
   * 清空过滤
   */
  async clearFilters(): Promise<void> {
    await this.switchToCPTab();
    await this.page.fill(this.featureFilter, '');
    await this.page.selectOption(this.priorityFilter, '');
    await this.page.click(this.searchBtn);
    await this.page.waitForTimeout(300);
  }

  /**
   * 获取 CP 表格行数
   */
  async getCPCount(): Promise<number> {
    await this.switchToCPTab();
    return await this.page.locator(this.cpTableRows).count();
  }

  /**
   * 展开 CP 详情
   */
  async expandCPDetail(coverPoint: string): Promise<void> {
    await this.switchToCPTab();
    await this.page.locator(
      `${this.cpTableRows}:has-text("${coverPoint}") ${this.expandBtn}`
    ).click();
    await this.page.waitForTimeout(300);
  }

  /**
   * 折叠 CP 详情
   */
  async collapseCPDetail(coverPoint: string): Promise<void> {
    await this.switchToCPTab();
    await this.page.locator(
      `${this.cpTableRows}:has-text("${coverPoint}") ${this.collapseBtn}`
    ).click();
    await this.page.waitForTimeout(300);
  }

  /**
   * 验证 CP 详情显示
   */
  async expectCPDetailVisible(coverPoint: string): Promise<void> {
    await expect(
      this.page.locator(`${this.cpTableRows}:has-text("${coverPoint}") ${this.cpDetailArea}`)
    ).toBeVisible();
  }

  /**
   * 验证 CP 详情隐藏
   */
  async expectCPDetailHidden(coverPoint: string): Promise<void> {
    await expect(
      this.page.locator(`${this.cpTableRows}:has-text("${coverPoint}") ${this.cpDetailArea}`)
    ).toBeHidden();
  }

  /**
   * 验证覆盖率显示
   */
  async expectCoverageDisplayed(): Promise<void> {
    await this.switchToCPTab();
    await expect(this.page.locator('th:has-text("覆盖率")')).toBeVisible();
  }

  /**
   * 获取覆盖率
   */
  async getCoverageValue(coverPoint: string): Promise<string> {
    await this.switchToCPTab();
    const badge = this.page.locator(
      `${this.cpTableRows}:has-text("${coverPoint}") .coverage-badge`
    );
    return (await badge.textContent()) || '';
  }

  /**
   * 全选 CP
   */
  async selectAllCP(): Promise<void> {
    await this.switchToCPTab();
    await this.page.check(this.cpSelectAll);
    await this.page.waitForTimeout(200);
  }

  /**
   * 批量更新 priority
   */
  async batchUpdatePriority(priority: string): Promise<void> {
    await this.switchToCPTab();
    await this.page.click(this.batchUpdateBtn);
    await this.page.selectOption(this.batchPrioritySelect, priority);
    await this.page.waitForTimeout(500);
  }

  /**
   * 验证模态框打开
   */
  async expectModalVisible(): Promise<void> {
    await expect(this.page.locator(this.cpModal)).toBeVisible();
  }

  /**
   * 验证模态框关闭
   */
  async expectModalHidden(): Promise<void> {
    await this.waitForElementHidden(this.cpModal);
  }

  /**
   * 验证必填字段校验
   */
  async expectValidationError(): Promise<void> {
    // 尝试提交不完整的表单
    await this.page.click(this.cpSubmitBtn);
    await this.page.waitForTimeout(300);

    // 验证模态框仍然打开
    await this.expectModalVisible();
  }
}
