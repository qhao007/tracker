/**
 * Dialog 处理工具
 *
 * 提供安全的 dialog 处理方式，避免竞态条件
 *
 * 使用方法:
 * import { dialogHelper } from './utils/dialog-helper';
 *
 * // 方式1: 自动模式（推荐用于 cleanup）
 * await dialogHelper.handle(page, async () => {
 *   await page.click('.delete-btn');
 * });
 *
 * // 方式2: 全局模式（推荐用于测试 setup/teardown）
 * setupDialogHandler(page);
 * await page.click('.delete-btn');
 * teardownDialogHandler(page);
 */
import { Page } from '@playwright/test';

type DialogHandler = (dialog: any) => Promise<void>;

interface DialogHelperConfig {
  /** 等待 dialog 超时时间 (ms) */
  dialogTimeout?: number;
  /** 处理 dialog 前是否检查已处理 */
  checkHandled?: boolean;
}

/**
 * Dialog 处理工具类
 */
export class DialogHelper {
  private static instance: DialogHelper;
  private activeHandlers: Map<string, DialogHandler> = new Map();
  private dialogTimeout: number = 5000;
  private checkHandled: boolean = true;

  private constructor(config: DialogHelperConfig = {}) {
    this.dialogTimeout = config.dialogTimeout ?? this.dialogTimeout;
    this.checkHandled = config.checkHandled ?? this.checkHandled;
  }

  /**
   * 获取单例实例
   */
  static getInstance(config?: DialogHelperConfig): DialogHelper {
    if (!DialogHelper.instance) {
      DialogHelper.instance = new DialogHelper(config);
    }
    return DialogHelper.instance;
  }

  /**
   * 创建唯一 handler ID
   */
  private createHandlerId(page: Page): string {
    const guid = (page as any)._guid || Math.random().toString(36).slice(2);
    return `dialog-handler-${guid}`;
  }

  /**
   * 设置全局 dialog 处理器
   *
   * @param page - Playwright 页面对象
   * @param handler - 自定义处理器 (可选，默认 accept)
   */
  setup(page: Page, handler?: DialogHandler): void {
    const handlerId = this.createHandlerId(page);

    // 移除已存在的处理器
    this.teardown(page);

    const dialogHandler: DialogHandler = async (dialog) => {
      // 检查是否已被处理
      if (this.checkHandled && (dialog as any)._handled) {
        return;
      }
      try {
        if (handler) {
          await handler(dialog);
        } else {
          await dialog.accept();
        }
        (dialog as any)._handled = true;
      } catch (error) {
        // 静默忽略 "already handled" 错误
        if (!error.message?.includes('already handled')) {
          console.warn(`⚠️ Dialog 处理失败:`, error);
        }
      }
    };

    this.activeHandlers.set(handlerId, dialogHandler);
    page.on('dialog', dialogHandler);
    console.log(`✅ Dialog 处理器已设置 (${handlerId})`);
  }

  /**
   * 移除全局 dialog 处理器
   */
  teardown(page: Page): void {
    const handlerId = this.createHandlerId(page);
    const handler = this.activeHandlers.get(handlerId);
    if (handler) {
      page.off('dialog', handler);
      this.activeHandlers.delete(handlerId);
      console.log(`✅ Dialog 处理器已移除 (${handlerId})`);
    }
  }

  /**
   * 安全处理模式
   *
   * 在回调执行期间自动设置/移除处理器
   *
   * @param page - Playwright 页面对象
   * @param callback - 要执行的操作
   */
  async handle<T>(page: Page, callback: () => Promise<T>): Promise<T> {
    const handlerId = this.createHandlerId(page);
    const dialogHandler: DialogHandler = async (dialog) => {
      try {
        await dialog.accept();
        (dialog as any)._handled = true;
      } catch (error) {
        // 忽略 "already handled" 错误
        if (!error.message?.includes('already handled')) {
          throw error;
        }
      }
    };

    page.on('dialog', dialogHandler);
    this.activeHandlers.set(handlerId, dialogHandler);

    try {
      return await callback();
    } finally {
      page.off('dialog', dialogHandler);
      this.activeHandlers.delete(handlerId);
    }
  }

  /**
   * 静默处理模式
   *
   * 忽略 "already handled" 错误，适合已知可能多次触发 dialog 的场景
   *
   * @param page - Playwright 页面对象
   */
  setupSilent(page: Page): void {
    const handlerId = this.createHandlerId(page);
    const dialogHandler: DialogHandler = async (dialog) => {
      try {
        await dialog.accept();
        (dialog as any)._handled = true;
      } catch (error) {
        // 静默忽略 "already handled" 错误
        if (!error.message?.includes('already handled')) {
          console.warn(`⚠️ Dialog 处理警告:`, error);
        }
      }
    };

    page.on('dialog', dialogHandler);
    this.activeHandlers.set(handlerId, dialogHandler);
  }
}

/**
 * 便捷函数：安全处理单个 dialog 操作
 */
export async function handleDialog<T>(
  page: Page,
  callback: () => Promise<T>,
  options?: DialogHelperConfig
): Promise<T> {
  const helper = DialogHelper.getInstance(options);
  return await helper.handle(page, callback);
}

/**
 * 便捷函数：设置全局 dialog 处理器
 */
export function setupDialogHandler(page: Page, options?: DialogHelperConfig): void {
  const helper = DialogHelper.getInstance(options);
  helper.setup(page);
}

/**
 * 便捷函数：移除全局 dialog 处理器
 */
export function teardownDialogHandler(page: Page): void {
  const helper = DialogHelper.getInstance();
  helper.teardown(page);
}

// 导出默认实例
export const dialogHelper = DialogHelper.getInstance();
