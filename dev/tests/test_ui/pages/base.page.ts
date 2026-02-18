import { Page, Locator, expect } from '@playwright/test';

/**
 * 页面基类 - 提供通用功能
 * 所有 Page Object 都应继承此类
 */
export abstract class BasePage {
  protected page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * 抽象方法：导航到页面
   */
  abstract navigate(): Promise<void>;

  /**
   * 等待页面加载完成
   */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 智能等待元素可见
   */
  async waitForSelector(
    selector: string,
    timeout: number = 10000
  ): Promise<void> {
    await this.page.waitForSelector(selector, {
      state: 'visible',
      timeout
    });
  }

  /**
   * 安全点击（带自动重试）
   */
  async safeClick(
    selector: string,
    options?: { timeout?: number; retries?: number }
  ): Promise<void> {
    const { timeout = 5000, retries = 2 } = options || {};
    
    for (let i = 0; i < retries; i++) {
      try {
        await this.page.click(selector, { timeout });
        return;
      } catch (e) {
        if (i === retries - 1) throw e;
        await this.page.waitForTimeout(500);
      }
    }
  }

  /**
   * 安全填充表单
   */
  async safeFill(selector: string, value: string): Promise<void> {
    await this.page.fill(selector, value);
  }

  /**
   * 获取元素文本
   */
  async getText(selector: string): Promise<string> {
    return await this.page.locator(selector).textContent() || '';
  }

  /**
   * 验证元素存在
   */
  async expectElementVisible(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeVisible();
  }

  /**
   * 验证元素包含文本
   */
  async expectText(selector: string, text: string): Promise<void> {
    await expect(this.page.locator(selector)).toContainText(text);
  }

  /**
   * 等待元素消失
   */
  async waitForElementHidden(selector: string, timeout: number = 10000): Promise<void> {
    await this.page.waitForSelector(selector, {
      state: 'hidden',
      timeout
    });
  }

  /**
   * 等待 API 响应
   */
  async waitForAPIResponse(
    urlPattern: string,
    timeout: number = 10000
  ): Promise<void> {
    await this.page.waitForResponse(
      response => 
        response.url().includes(urlPattern) && 
        response.status() < 400,
      { timeout }
    );
  }

  /**
   * 获取页面标题
   */
  async getTitle(): Promise<string> {
    return await this.page.title();
  }
}
