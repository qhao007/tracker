/**
 * 清理测试数据工具
 *
 * 提供测试数据清理功能，确保测试间不互相干扰
 *
 * 使用方法:
 *   import { cleanupTestData } from './utils/cleanup';
 *   await cleanupTestData(page);
 */

import { Page } from '@playwright/test';
import { dialogHelper, handleDialog } from './dialog-helper';

export const TEST_DATA_PREFIX = 'TestUI_';
export const CLEANUP_DELAY = 300;
export const CLEANUP_TIMEOUT = 10000;
export const MAX_KEEP_ITEMS = 5; // 保留的最新数据数量

/**
 * 清理测试数据
 * 删除所有以 TEST_DATA_PREFIX 开头的项目、CP、TC
 *
 * @param page - Playwright 页面对象
 */
export async function cleanupTestData(page: Page): Promise<void> {
  try {
    // 检查当前页面是否在测试站点
    const currentUrl = page.url();

    if (!currentUrl.includes('localhost:8081')) {
      // 不在测试站点，先导航
      await page.goto('http://localhost:8081');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForSelector('#projectSelector', { timeout: 10000 });
    }

    // 清理以 TEST_DATA_PREFIX 开头的项目
    await cleanupProjects(page);

    // 等待清理操作完成
    await page.waitForTimeout(CLEANUP_DELAY);

    console.log('✅ 测试数据清理完成');
  } catch (error) {
    console.warn('⚠️ 清理测试数据时出错:', error);
    // 不抛出错误，确保清理失败不影响测试继续
  }
}

/**
 * 清理测试创建的项目
 *
 * @param page - Playwright 页面对象
 */
async function cleanupProjects(page: Page): Promise<void> {
  try {
    const prefix = TEST_DATA_PREFIX;

    // 获取项目列表
    const projectSelector = page.locator('#projectSelector option');
    const count = await projectSelector.count();

    // 收集要删除的项目 ID
    const projectsToDelete: { id: number; name: string }[] = [];

    for (let i = 0; i < count; i++) {
      const option = projectSelector.nth(i);
      const text = await option.textContent();

      if (text && (text.startsWith(prefix) || text.includes('TestUI_'))) {
        const value = await option.getAttribute('value');
        if (value) {
          projectsToDelete.push({ id: parseInt(value), name: text });
        }
      }
    }

    // 使用 API 删除项目（前端没有删除按钮）
    for (const project of projectsToDelete) {
      console.log(`🗑️ 删除测试项目: ${project.name}`);

      try {
        // 直接调用 API 删除项目
        await page.evaluate(async (projectId) => {
          const response = await fetch(`/api/projects/${projectId}`, {
            method: 'DELETE',
            credentials: 'include'
          });
          return response.json();
        }, project.id);

        // 等待删除完成
        await page.waitForTimeout(500);
      } catch (e) {
        console.warn(`⚠️ 删除项目 ${project.name} 失败:`, e);
      }
    }

    // 刷新页面以更新项目列表 (使用 domcontentloaded 避免等待 CDN 资源)
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForSelector('#projectSelector', { timeout: 10000 });

    console.log(`✅ 项目清理完成，共删除 ${projectsToDelete.length} 个测试项目`);
  } catch (error) {
    console.warn('⚠️ 清理项目时出错:', error);
  }
}

/**
 * 清理单个测试数据
 *
 * @param page - Playwright 页面对象
 * @param dataType - 数据类型 ('project' | 'cp' | 'tc')
 * @param name - 数据名称
 */
export async function cleanupSingleData(
  page: Page,
  dataType: 'project' | 'cp' | 'tc',
  name: string
): Promise<void> {
  try {
    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });

    switch (dataType) {
      case 'project':
        await cleanupSingleProject(page, name);
        break;
      case 'cp':
        await cleanupSingleCP(page, name);
        break;
      case 'tc':
        await cleanupSingleTC(page, name);
        break;
    }

    console.log(`✅ 已清理 ${dataType}: ${name}`);
  } catch (error) {
    console.warn(`⚠️ 清理 ${dataType} "${name}" 时出错:`, error);
  }
}

/**
 * 清理项目内的 CP 和 TC，保留最新的 N 条
 * 用于在每组测试开始前清理数据
 *
 * @param page - Playwright 页面对象
 * @param keepCount - 保留的最新数据数量，默认 MAX_KEEP_ITEMS
 */
export async function cleanupProjectData(page: Page, keepCount: number = MAX_KEEP_ITEMS): Promise<void> {
  try {
    // 检查页面是否仍然可用
    try {
      await page.title();
    } catch (e) {
      console.warn('⚠️ 页面已关闭，跳过项目数据清理');
      return;
    }

    // 检查当前页面是否在测试站点
    const currentUrl = page.url();

    if (!currentUrl.includes('localhost:8081')) {
      // 不在测试站点，先导航
      await page.goto('http://localhost:8081');
      await page.waitForLoadState('domcontentloaded');
      await page.waitForSelector('#projectSelector', { timeout: 10000 });
    }

    console.log(`🧹 开始清理项目数据，保留最新 ${keepCount} 条...`);

    // 检查页面是否仍然可用（在操作前再次检查）
    try {
      await page.title();
    } catch (e) {
      console.warn('⚠️ 页面已关闭，跳过 CP/TC 清理');
      console.log('✅ 项目数据清理完成');
      return;
    }

    // 清理 CP
    await cleanupCPs(page, keepCount);

    // 检查页面是否仍然可用（在 CP 清理后再次检查）
    try {
      await page.title();
    } catch (e) {
      console.warn('⚠️ 页面已关闭，跳过 TC 清理');
      console.log('✅ 项目数据清理完成');
      return;
    }

    // 清理 TC
    await cleanupTCs(page, keepCount);

    console.log('✅ 项目数据清理完成');
  } catch (error) {
    console.warn('⚠️ 清理项目数据时出错:', error);
  }
}

/**
 * 清理多余的 CP，保留最新的 N 条
 */
async function cleanupCPs(page: Page, keepCount: number): Promise<void> {
  try {
    // 检查页面是否仍然可用
    try {
      await page.title();
    } catch (e) {
      console.warn('⚠️ 页面已关闭，跳过 CP 清理');
      return;
    }

    await page.click('button.tab:has-text("Cover Points")');
    await page.waitForSelector('#cpPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 获取 CP 列表行
    const cpRows = page.locator('#cpList tr:not(:first-child)'); // 跳过表头
    const count = await cpRows.count();

    if (count <= keepCount) {
      console.log(`📋 CP 数量 ${count} <= ${keepCount}，无需清理`);
      return;
    }

    const deleteCount = count - keepCount;
    console.log(`🗑️ 需要删除 ${deleteCount} 条 CP...`);

    // ✅ 使用 handleDialog 安全处理所有删除操作
    await handleDialog(page, async () => {
      // 从后往前删除（保留前面的最新数据）
      for (let i = count - 1; i >= keepCount; i--) {
        try {
          const row = cpRows.nth(i);
          const deleteBtn = row.locator('button:has-text("删除")');

          if (await deleteBtn.count() > 0) {
            await deleteBtn.click();
            await page.waitForTimeout(300);
          }
        } catch (e) {
          console.warn(`⚠️ 删除 CP 第 ${i} 行时出错:`, e);
        }
      }
    });

    console.log(`✅ CP 清理完成，当前保留 ${keepCount} 条`);
  } catch (error) {
    console.warn('⚠️ 清理 CP 时出错:', error);
  }
}

/**
 * 清理多余的 TC，保留最新的 N 条
 */
async function cleanupTCs(page: Page, keepCount: number): Promise<void> {
  try {
    // 检查页面是否仍然可用
    try {
      await page.title();
    } catch (e) {
      console.warn('⚠️ 页面已关闭，跳过 TC 清理');
      return;
    }

    await page.click('button.tab:has-text("Test Cases")');
    await page.waitForSelector('#tcPanel', { state: 'visible', timeout: 10000 });
    await page.waitForTimeout(500);

    // 获取 TC 列表行
    const tcRows = page.locator('#tcList tr:not(:first-child)'); // 跳过表头
    const count = await tcRows.count();

    if (count <= keepCount) {
      console.log(`📋 TC 数量 ${count} <= ${keepCount}，无需清理`);
      return;
    }

    const deleteCount = count - keepCount;
    console.log(`🗑️ 需要删除 ${deleteCount} 条 TC...`);

    // ✅ 使用 handleDialog 安全处理所有删除操作
    await handleDialog(page, async () => {
      // 从后往前删除（保留前面的最新数据）
      for (let i = count - 1; i >= keepCount; i--) {
        try {
          const row = tcRows.nth(i);
          const deleteBtn = row.locator('button:has-text("删除")');

          if (await deleteBtn.count() > 0) {
            await deleteBtn.click();
            await page.waitForTimeout(300);
          }
        } catch (e) {
          console.warn(`⚠️ 删除 TC 第 ${i} 行时出错:`, e);
        }
      }
    });

    console.log(`✅ TC 清理完成，当前保留 ${keepCount} 条`);
  } catch (error) {
    console.warn('⚠️ 清理 TC 时出错:', error);
  }
}

/**
 * 清理单个项目
 */
async function cleanupSingleProject(page: Page, projectName: string): Promise<void> {
  // 选择项目
  await page.selectOption('#projectSelector', { label: projectName });
  await page.waitForTimeout(300);

  // 查找并点击删除按钮
  const deleteBtn = page.locator('.project-delete-btn, [onclick*="deleteProject"]');
  if (await deleteBtn.isVisible()) {
    // ✅ 使用 dialogHelper 安全处理
    await dialogHelper.handle(page, async () => {
      await deleteBtn.click();
    });
  }
}

/**
 * 清理单个 CP
 */
async function cleanupSingleCP(page: Page, cpName: string): Promise<void> {
  // 切换到 CP 标签页
  await page.click('text=Cover Points');
  await page.waitForTimeout(500);

  // 查找 CP 行
  const cpRow = page.locator(`.cp-table tbody tr:has-text("${cpName}")`);
  if (await cpRow.isVisible()) {
    // 点击删除按钮
    const deleteBtn = cpRow.locator('.delete-btn, [onclick*="deleteCP"]');
    if (await deleteBtn.isVisible()) {
      // ✅ 使用 dialogHelper 安全处理
      await dialogHelper.handle(page, async () => {
        await deleteBtn.click();
      });
    }
  }
}

/**
 * 清理单个 TC
 */
async function cleanupSingleTC(page: Page, tcName: string): Promise<void> {
  // 切换到 TC 标签页
  await page.click('button[onclick="switchTab(\'tc\')"]');
  await page.waitForTimeout(500);

  // 查找 TC 行
  const tcRow = page.locator(`table tbody tr:has-text("${tcName}")`);
  if (await tcRow.isVisible()) {
    // 点击删除按钮
    const deleteBtn = tcRow.locator('.tc-delete-btn, [onclick*="deleteTC"]');
    if (await deleteBtn.isVisible()) {
      // ✅ 使用 dialogHelper 安全处理
      await dialogHelper.handle(page, async () => {
        await deleteBtn.click();
      });
    }
  }
}

/**
 * 清理所有测试数据（破坏性操作）
 * 仅在测试套件结束时调用
 *
 * @param page - Playwright 页面对象
 */
export async function cleanupAllTestData(page: Page): Promise<void> {
  try {
    console.log('🧹 开始清理所有测试数据...');

    await page.goto('http://localhost:8081');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('#projectSelector', { timeout: 10000 });

    // 获取所有项目
    const projectSelector = page.locator('#projectSelector option');
    const count = await projectSelector.count();

    // 从后往前删除（避免索引变化问题）
    for (let i = count - 1; i >= 0; i--) {
      try {
        const option = projectSelector.nth(i);
        const text = await option.textContent();

        // 只删除测试项目
        if (text && (text.startsWith(TEST_DATA_PREFIX) || text.includes('TestUI_'))) {
          console.log(`🗑️ 删除测试项目: ${text}`);

          await page.selectOption('#projectSelector', { index: i });
          await page.waitForTimeout(300);

          // 查找删除按钮
          const deleteBtn = page.locator('.project-delete-btn, [onclick*="deleteProject"]');
          if (await deleteBtn.isVisible()) {
            // ✅ 使用 dialogHelper 安全处理
            await dialogHelper.handle(page, async () => {
              await deleteBtn.click();
            });

            // 重新获取项目列表（因为删除了一个项目）
            break;
          }
        }
      } catch (e) {
        // 继续下一个
      }
    }

    console.log('✅ 所有测试数据清理完成');
  } catch (error) {
    console.warn('⚠️ 清理所有测试数据时出错:', error);
  }
}
