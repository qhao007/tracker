import { Page, Locator } from '@playwright/test';

/**
 * 辅助函数集合
 */

/**
 * 生成唯一 ID
 */
export function generateUniqueId(): string {
  return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 等待 API 响应
 */
export async function waitForAPIResponse(
  page: Page,
  urlPattern: string,
  timeout: number = 10000
): Promise<void> {
  await page.waitForResponse(
    response =>
      response.url().includes(urlPattern) &&
      response.status() < 400,
    { timeout }
  );
}

/**
 * 等待条件满足
 */
export async function waitForCondition<T>(
  page: Page,
  condition: () => Promise<T>,
  expectedValue: T,
  timeout: number = 10000,
  interval: number = 500
): Promise<void> {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const value = await condition();
    if (value === expectedValue) return;
    await page.waitForTimeout(interval);
  }

  throw new Error(`Condition not met within ${timeout}ms`);
}

/**
 * 安全点击（带重试）
 */
export async function safeClick(
  page: Page,
  selector: string,
  options?: { timeout?: number; retries?: number }
): Promise<void> {
  const { timeout = 5000, retries = 2 } = options || {};

  for (let i = 0; i < retries; i++) {
    try {
      await page.click(selector, { timeout });
      return;
    } catch (e) {
      if (i === retries - 1) throw e;
      await page.waitForTimeout(500);
    }
  }
}

/**
 * 智能等待元素可见
 */
export async function waitForElementVisible(
  page: Page,
  selector: string,
  timeout: number = 10000
): Promise<void> {
  await page.waitForSelector(selector, {
    state: 'visible',
    timeout
  });
}

/**
 * 智能等待元素消失
 */
export async function waitForElementHidden(
  page: Page,
  selector: string,
  timeout: number = 10000
): Promise<void> {
  await page.waitForSelector(selector, {
    state: 'hidden',
    timeout
  });
}

/**
 * 获取表格所有行的文本内容
 */
export async function getTableRowsText(
  tableSelector: string,
  page: Page
): Promise<string[]> {
  const rows = page.locator(`${tableSelector} tbody tr`);
  const count = await rows.count();
  const texts: string[] = [];

  for (let i = 0; i < count; i++) {
    const text = await rows.nth(i).textContent();
    if (text) texts.push(text.trim());
  }

  return texts;
}

/**
 * 等待加载动画消失
 */
export async function waitForLoadingComplete(
  page: Page,
  loadingSelector: string = '.loading, .spinner, [class*="loading"]',
  timeout: number = 10000
): Promise<void> {
  try {
    await page.waitForSelector(loadingSelector, {
      state: 'hidden',
      timeout
    });
  } catch {
    // 如果加载动画不存在，忽略错误
  }
}

/**
 * 滚动到元素可见
 */
export async function scrollIntoView(
  page: Page,
  selector: string
): Promise<void> {
  const element = page.locator(selector);
  await element.scrollIntoViewIfNeeded();
}

/**
 * 获取元素属性值
 */
export async function getElementAttribute(
  page: Page,
  selector: string,
  attribute: string
): Promise<string> {
  return (await page.locator(selector).getAttribute(attribute)) || '';
}

/**
 * 设置元素属性值
 */
export async function setElementAttribute(
  page: Page,
  selector: string,
  attribute: string,
  value: string
): Promise<void> {
  await page.evaluate(
    (sel: string, attr: string, val: string) => {
      const el = document.querySelector(sel);
      if (el) el.setAttribute(attr, val);
    },
    selector,
    attribute,
    value
  );
}

/**
 * 清除输入框内容
 */
export async function clearInput(
  page: Page,
  selector: string
): Promise<void> {
  await page.locator(selector).clear();
}

/**
 * 等待 DOM 稳定（多次检查元素存在）
 */
export async function waitForDOMStable(
  page: Page,
  selector: string,
  checkCount: number = 3,
  interval: number = 200
): Promise<void> {
  for (let i = 0; i < checkCount; i++) {
    const count = await page.locator(selector).count();
    if (count > 0) {
      await page.waitForTimeout(interval);
    }
  }
}

/**
 * 格式化时间戳为日期字符串
 */
export function formatTimestampToDate(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toISOString().split('T')[0];
}

/**
 * 生成测试数据前缀
 */
export function getTestDataPrefix(): string {
  return `TestUI_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
}

/**
 * 截取字符串（用于长名称测试）
 */
export function truncateString(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength);
}

/**
 * 重复字符串
 */
export function repeatString(str: string, count: number): string {
  return str.repeat(count);
}
