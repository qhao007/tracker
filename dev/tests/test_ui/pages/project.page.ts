import { Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

/**
 * 项目管理页面对象
 * 封装项目管理页面的所有操作
 */
export class ProjectPage extends BasePage {
  readonly baseURL = 'http://localhost:8081';

  // 元素定位器
  readonly projectSelector = '#projectSelector';
  readonly projectBtn = 'button.header-btn:has-text("📁 项目")';
  readonly projectModal = '#projectModal';
  readonly newProjectName = '#newProjectName';
  readonly createBtn = '#projectModal button:has-text("创建")';  // 更稳定的选择器
  readonly modalClose = '#projectModal .modal-close';

  async navigate(): Promise<void> {
    await this.page.goto(this.baseURL);
    await this.waitForLoad();
    await this.waitForSelector(this.projectSelector);
  }

  /**
   * 点击项目按钮，打开项目模态框
   */
  async openProjectModal(): Promise<void> {
    await this.page.click(this.projectBtn);
    await this.waitForSelector(this.projectModal);
  }

  /**
   * 关闭项目模态框
   */
  async closeProjectModal(): Promise<void> {
    await this.page.click(this.modalClose);
    await this.waitForElementHidden(this.projectModal);
  }

  /**
   * 创建项目
   */
  async createProject(name: string): Promise<void> {
    await this.openProjectModal();
    await this.safeFill(this.newProjectName, name);
    await this.page.click(this.createBtn);
    await this.page.waitForTimeout(1000);
    
    // 等待项目出现在下拉列表
    await expect(
      this.page.locator(`${this.projectSelector} option:has-text("${name}")`)
    ).toBeAttached();
  }

  /**
   * 切换到指定项目
   */
  async selectProject(projectName: string): Promise<void> {
    // 等待下拉框可用并包含选项
    const selector = this.page.locator(this.projectSelector);
    await selector.waitFor({ state: 'visible' });
    
    // 等待特定项目出现在选项中
    await this.page.waitForFunction(
      (name) => {
        const select = document.querySelector('#projectSelector') as HTMLSelectElement;
        return select && Array.from(select.options).some(o => o.text.includes(name));
      },
      projectName,
      { timeout: 10000 }
    );
    
    await this.page.selectOption(this.projectSelector, { label: projectName });
    await this.page.waitForTimeout(500);
  }

  /**
   * 获取所有项目列表
   */
  async getProjectList(): Promise<string[]> {
    const options = this.page.locator(`${this.projectSelector} option`);
    const count = await options.count();
    const projects: string[] = [];

    for (let i = 0; i < count; i++) {
      const text = await options.nth(i).textContent();
      if (text) projects.push(text);
    }

    return projects;
  }

  /**
   * 验证项目存在
   */
  async expectProjectExists(projectName: string): Promise<void> {
    await expect(
      this.page.locator(`${this.projectSelector} option:has-text("${projectName}")`)
    ).toBeAttached();
  }

  /**
   * 验证项目不存在
   */
  async expectProjectNotExists(projectName: string): Promise<void> {
    await expect(
      this.page.locator(`${this.projectSelector} option:has-text("${projectName}")`)
    ).toBeHidden();
  }

  /**
   * 验证项目数量
   */
  async expectProjectCount(count: number): Promise<void> {
    await expect(this.page.locator(`${this.projectSelector} option`)).toHaveCount(count);
  }

  /**
   * 获取当前选中的项目
   */
  async getCurrentProject(): Promise<string> {
    return await this.page.locator(`${this.projectSelector} option:checked`).textContent() || '';
  }

  /**
   * 验证项目模态框可见
   */
  async expectModalVisible(): Promise<void> {
    await this.expectElementVisible(this.projectModal);
  }

  /**
   * 验证项目模态框不可见
   */
  async expectModalHidden(): Promise<void> {
    await this.waitForElementHidden(this.projectModal);
  }

  /**
   * 等待项目数据加载
   */
  async waitForProjectData(): Promise<void> {
    await this.page.waitForSelector('#cpCount', { state: 'visible' });
    await this.page.waitForSelector('#tcCount', { state: 'visible' });
  }

  /**
   * 获取 CP 数量
   */
  async getCPCount(): Promise<string> {
    return await this.getText('#cpCount');
  }

  /**
   * 获取 TC 数量
   */
  async getTCCount(): Promise<string> {
    return await this.getText('#tcCount');
  }

  /**
   * 验证 CP 和 TC 数量为 0
   */
  async expectEmptyProject(): Promise<void> {
    await expect(await this.getCPCount()).toBe('0');
    await expect(await this.getTCCount()).toBe('0');
  }
}
