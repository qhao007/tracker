/**
 * 项目管理 UI 测试 - Page Object Model 示例
 * 
 * 展示如何使用新创建的框架：
 * - Page Objects (project.page.ts)
 * - Test Data Factory (test-data.factory.ts)
 * 
 * 运行命令:
 *   npx playwright test tests/demo/project.pom.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';
import { ProjectPage } from '../pages/project.page';
import { TestDataFactory } from '../fixtures/test-data.factory';

test.describe('项目管理测试 (POM 示例)', () => {
  let projectPage: ProjectPage;

  test.beforeEach(async ({ page }) => {
    projectPage = new ProjectPage(page);
    await projectPage.navigate();
  });

  // UI-PROJ-001: 创建项目 - 正常
  test('UI-PROJ-001: 创建项目 - 正常', async () => {
    const projectData = TestDataFactory.createProjectData();
    
    await projectPage.createProject(projectData.name);
    
    // 验证
    await projectPage.expectProjectExists(projectData.name);
  });

  // UI-PROJ-003: 创建项目 - 特殊字符
  test('UI-PROJ-003: 创建项目 - 特殊字符', async () => {
    const projectName = `TestUI_Special_${TestDataFactory.getTimestampPrefix()}_ABC`;
    
    await projectPage.createProject(projectName);
    await projectPage.expectProjectExists(projectName);
  });

  // UI-PROJ-004: 创建项目 - 超长名称
  test('UI-PROJ-004: 创建项目 - 超长名称', async () => {
    const timestamp = TestDataFactory.getTimestampPrefix();
    const projectName = `TestUI_Long_${timestamp}_${'a'.repeat(50)}`;
    
    await projectPage.createProject(projectName);
    await projectPage.expectProjectExists(timestamp); // 验证部分匹配
  });

  // UI-PROJ-005: 切换项目
  test('UI-PROJ-005: 切换项目', async () => {
    const projectData1 = TestDataFactory.createProjectData({ name: `Switch_A_${TestDataFactory.getTimestampPrefix()}` });
    const projectData2 = TestDataFactory.createProjectData({ name: `Switch_B_${TestDataFactory.getTimestampPrefix()}` });
    
    // 创建两个项目
    await projectPage.createProject(projectData1.name);
    await projectPage.createProject(projectData2.name);
    
    // 切换到最后一个项目
    await projectPage.selectProject(projectData2.name);
    
    // 验证
    await expect(
      projectPage.page.locator('#projectSelector option:checked')
    ).toContainText(projectData2.name.split('_').pop() || '');
  });

  // UI-PROJ-006: 项目切换数据刷新
  test('UI-PROJ-006: 项目切换数据刷新', async () => {
    const projectData1 = TestDataFactory.createProjectData({ name: `Refresh_A_${TestDataFactory.getTimestampPrefix()}` });
    const projectData2 = TestDataFactory.createProjectData({ name: `Refresh_B_${TestDataFactory.getTimestampPrefix()}` });
    
    await projectPage.createProject(projectData1.name);
    await projectPage.createProject(projectData2.name);
    
    // 切换并验证
    await projectPage.selectProject(projectData2.name);
    await projectPage.page.waitForTimeout(1500);
    
    await projectPage.expectEmptyProject();
  });

  // UI-PROJ-008: 重复名称检测
  test('UI-PROJ-008: 创建重复名称项目', async () => {
    const projectData = TestDataFactory.createProjectData();
    
    await projectPage.createProject(projectData.name);
    const initialCount = await projectPage.page.locator('#projectSelector option').count();
    
    // 尝试重复创建
    await projectPage.createProject(projectData.name);
    const currentCount = await projectPage.page.locator('#projectSelector option').count();
    
    expect(currentCount).toBe(initialCount);
  });

  // UI-PROJ-009: 模态框打开关闭
  test('UI-PROJ-009: 项目模态框打开关闭', async () => {
    await projectPage.openProjectModal();
    await projectPage.expectModalVisible();
    
    await projectPage.closeProjectModal();
    await projectPage.expectModalHidden();
  });
});
