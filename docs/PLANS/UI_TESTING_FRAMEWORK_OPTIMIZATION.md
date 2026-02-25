# Tracker UI 测试框架优化计划

## 1. 需求分析

### 背景

Tracker 项目当前使用 Playwright CLI (TypeScript) 进行 UI 测试，已建立基础框架：
- Page Object Model (base.page.ts + 3 个页面类)
- Fixtures (tracker.fixture.ts)
- 测试数据工厂 (test-data.factory.ts)
- 测试分层 (smoke/integration/e2e)

但随着测试用例增加，存在以下问题：
1. **内存占用高** - 单次执行约 500MB-1GB
2. **代码复用不足** - 通用组件（如 Modal、Table）未提取
3. **维护成本上升** - 新测试用例编写重复逻辑

### 目标

| 指标 | 当前值 | 目标值 | 改善幅度 |
|------|--------|--------|----------|
| 内存占用 | 800MB | 400MB | -50% |
| 代码复用率 | ~30% | 70% | +133% |
| 测试执行时间 | 15 分钟 | 10 分钟 | -33% |
| 维护效率 | - | 显著提升 | - |

### 范围

**包含**:
- Playwright 内存优化配置
- 通用组件层建设 (components/)
- Fixtures 增强（懒加载、内存监控）
- 测试工具封装

**不包含**:
- 测试用例本身的重写
- CI/CD 集成（已在其他计划中）
- 性能基准测试系统

---

## 2. 任务分解

| ID | 任务 | 依赖 | 优先级 | 预估时间 |
|----|------|------|--------|----------|
| T1 | Playwright 内存配置优化 | - | P0 | 1h |
| T2 | 创建通用组件层 (components/) | T1 | P1 | 3h |
| T3 | Fixtures 增强（懒加载+内存监控） | T1 | P1 | 2h |
| T4 | 编写组件使用示例 | T2 | P2 | 1h |
| T5 | 文档更新与验证 | T4, T3 | P2 | 1h |

---

## 3. 实施步骤

### T1: Playwright 内存配置优化

**目标**: 通过配置调整减少内存占用 30-50%

**步骤**:

1. 编辑 `playwright.config.ts`，添加优化配置：

```typescript
// 新增 launchOptions 配置
launchOptions: {
  args: [
    '--disable-dev-shm-usage',       // 避免 /dev/shm 空间不足
    '--disable-gpu',                 // 禁用 GPU（headless 模式）
    '--no-sandbox',                  // 沙箱相关
    '--disable-setuid-sandbox',
    '--disable-web-security',        // 减少安全检查
  ]
},

// 新增 contextOptions 配置
contextOptions: {
  reducedMotion: 'reduce',          // 减少动画
  deviceScaleFactor: 1,              // 降低分辨率
},

// 增强现有配置
fullyParallel: false,               // 串行执行，减少内存峰值
```

2. 验证配置生效：
```bash
npx playwright test tests/test_ui/specs/smoke/ --project=firefox
```

**验证**: 
- 内存监控脚本显示峰值内存 < 500MB
- 测试通过率不受影响

---

### T2: 创建通用组件层

**目标**: 提取重复 UI 组件，提高代码复用率

**步骤**:

1. 创建目录结构：
```
tests/test_ui/
├── components/                    # 新增
│   ├── modal.component.ts        # 模态框组件
│   ├── table.component.ts        # 表格组件
│   ├── form.component.ts         # 表单组件
│   ├── dialog.helper.ts         # Dialog 处理增强
│   └── index.ts                 # 统一导出
```

2. 实现 ModalComponent (`modal.component.ts`):

```typescript
import { Page, Locator } from '@playwright/test';

export class ModalComponent {
  private modal: Locator;
  private closeButton: Locator;
  private overlay: Locator;

  constructor(private page: Page, modalSelector: string) {
    this.modal = this.page.locator(modalSelector);
    this.closeButton = this.modal.locator('.close, .modal-close, [data-dismiss="modal"]');
    this.overlay = this.page.locator('.modal-backdrop, .overlay');
  }

  async open(triggerAction: () => Promise<void>): Promise<void> {
    await triggerAction();
    await this.modal.waitFor({ state: 'visible' });
  }

  async close(options?: { clickOverlay?: boolean; pressEscape?: boolean }): Promise<void> {
    const { clickOverlay = false, pressEscape = false } = options || {};
    
    if (pressEscape) {
      await this.page.keyboard.press('Escape');
    } else if (clickOverlay) {
      await this.overlay.click({ position: { x: 10, y: 10 } });
    } else {
      await this.closeButton.click();
    }
    
    await this.modal.waitFor({ state: 'hidden' });
  }

  async fillForm(data: Record<string, string>): Promise<void> {
    for (const [field, value] of Object.entries(data)) {
      const input = this.modal.locator(`input[name="${field}"], textarea[name="${field}"], select[name="${field}"]`);
      await input.fill(value);
    }
  }

  async expectVisible(): Promise<void> {
    await expect(this.modal).toBeVisible();
  }

  async getErrorMessage(): Promise<string> {
    const error = this.modal.locator('.error-message, .alert-danger');
    return await error.textContent() || '';
  }
}
```

3. 实现 TableComponent (`table.component.ts`):

```typescript
import { Page, Locator, expect } from '@playwright/test';

export class TableComponent {
  private table: Locator;
  private rows: Locator;
  private headers: Locator;

  constructor(private page: Page, tableSelector: string) {
    this.table = this.page.locator(tableSelector);
    this.rows = this.table.locator('tbody tr');
    this.headers = this.table.locator('thead th');
  }

  async getRowCount(): Promise<number> {
    return await this.rows.count();
  }

  async getCellValue(rowIndex: number, columnIndex: number): Promise<string> {
    const cell = this.rows.nth(rowIndex).locator('td').nth(columnIndex);
    return await cell.textContent() || '';
  }

  async findRow(columnIndex: number, value: string): Promise<number> {
    const count = await this.rows.count();
    for (let i = 0; i < count; i++) {
      const cellValue = await this.getCellValue(i, columnIndex);
      if (cellValue.includes(value)) return i;
    }
    return -1;
  }

  async clickActionInRow(rowIndex: number, actionSelector: string): Promise<void> {
    const actionBtn = this.rows.nth(rowIndex).locator(actionSelector);
    await actionBtn.click();
  }

  async waitForLoading(): Promise<void> {
    const loading = this.table.locator('.loading, .spinner');
    if (await loading.count() > 0) {
      await loading.waitFor({ state: 'hidden' });
    }
  }

  async expectRowCount(expected: number): Promise<void> {
    await expect(this.rows).toHaveCount(expected);
  }
}
```

4. 统一导出 (`index.ts`):

```typescript
export { ModalComponent } from './modal.component';
export { TableComponent } from './table.component';
export { FormComponent } from './form.component';
```

**验证**:
- 新测试用例使用组件编写，代码量减少 30%+
- 组件方法覆盖 80%+ 常见场景

---

### T3: Fixtures 增强

**目标**: 添加懒加载和内存监控能力

**步骤**:

1. 创建 `fixtures/enhanced.fixture.ts`:

```typescript
import { test as base, Page } from '@playwright/test';
import { ProjectPage } from '../pages/project.page';
import { CPPage } from '../pages/cp.page';
import { TCPage } from '../pages/tc.page';

/**
 * 增强版 Fixtures
 * - 懒加载 Page Objects（仅在访问时创建）
 * - 内存监控
 */
export const test = base.extend<{
  // 懒加载页面
  lazyPage: (name: 'project' | 'cp' | 'tc') => Promise<ProjectPage | CPPage | TCPage>;
  
  // 内存跟踪
  memoryTracker: {
    startMemory: number;
    getDelta: () => number;
  };
}>({
  // 懒加载 Page Objects
  lazyPage: async ({ page }, use) => {
    const cache = new Map<string, ProjectPage | CPPage | TCPage>();
    
    const getPage = async (name: 'project' | 'cp' | 'tc') => {
      if (!cache.has(name)) {
        switch (name) {
          case 'project':
            cache.set(name, new ProjectPage(page));
            break;
          case 'cp':
            cache.set(name, new CPPage(page));
            break;
          case 'tc':
            cache.set(name, new TCPage(page));
            break;
        }
      }
      return cache.get(name)!;
    };
    
    await use(getPage);
    cache.clear();
  },
  
  // 内存监控
  memoryTracker: async ({}, use) => {
    const startMemory = process.memoryUsage().heapUsed;
    await use({
      startMemory,
      getDelta: () => process.memoryUsage().heapUsed - startMemory
    });
  },
});
```

2. 更新 `tracker.fixture.ts` 集成新功能：

```typescript
// 在现有 fixture 中添加内存监控钩子
base.beforeEach(async ({}, testInfo) => {
  console.log(`[${testInfo.title}] 开始 - 内存: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`);
});

base.afterEach(async ({}, testInfo) => {
  console.log(`[${testInfo.title}] 结束 - 内存: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`);
});
```

**验证**:
- 内存使用可追踪
- Page Objects 按需加载

---

### T4: 编写组件使用示例

**目标**: 提供最佳实践文档

**步骤**:

1. 创建示例测试文件 `demo/components-demo.spec.ts`:

```typescript
import { test } from '../fixtures/enhanced.fixture';
import { ModalComponent } from '../components/modal.component';
import { TableComponent } from '../components/table.component';

test('使用 ModalComponent 创建项目', async ({ page }) => {
  const modal = new ModalComponent(page, '#projectModal');
  
  // 打开模态框
  await modal.open(async () => {
    await page.click('#addProjectBtn');
  });
  
  // 填写表单
  await modal.fillForm({
    name: 'Test_Project',
    description: '测试项目'
  });
  
  // 提交
  await page.click('#submitBtn');
  
  // 等待关闭
  await modal.close();
});

test('使用 TableComponent 管理 CP', async ({ page }) => {
  const table = new TableComponent(page, '#cpTable');
  
  // 等待加载
  await table.waitForLoading();
  
  // 查找行
  const rowIndex = await table.findRow(0, 'TestCP');
  
  if (rowIndex >= 0) {
    // 点击编辑按钮
    await table.clickActionInRow(rowIndex, '.edit-btn');
  }
});
```

2. 运行示例验证

**验证**:
- 示例测试通过
- 代码可读性提升

---

### T5: 文档更新与验证

**步骤**:

1. 更新 `UI_TESTING_STRATEGY.md`：
   - 添加新框架结构
   - 更新最佳实践
   - 添加组件使用指南

2. 全面验证：
```bash
# 冒烟测试
npx playwright test tests/test_ui/specs/smoke/ --project=firefox

# 集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox

# 检查内存
bash scripts/memory-monitor.sh &
```

**验证**:
- 所有测试通过
- 内存峰值 < 500MB
- 代码复用率提升验证

---

## 4. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 浏览器兼容性问题 | 高 | 先在 dev 环境验证，Firefox 为主力浏览器 |
| 组件抽象过度 | 中 | 保持组件轻量，只封装高频场景 |
| 现有测试破坏 | 高 | 先备份，运行完整测试套件验证 |
| 内存监控不准确 | 低 | 使用多轮测试取平均值 |

---

## 5. 时间线

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| Day 1 上午 | T1: Playwright 内存配置优化 | 1h |
| Day 1 下午 | T2: 创建通用组件层 | 3h |
| Day 2 上午 | T3: Fixtures 增强 | 2h |
| Day 2 下午 | T4: 编写组件使用示例 | 1h |
| Day 2 下午 | T5: 文档更新与验证 | 1h |

**预计总时间**: 8h (1 个工作日)

**里程碑**:
- [ ] T1 完成 → 内存优化配置生效
- [ ] T2 完成 → 组件层可用
- [ ] T5 完成 → 完整优化方案落地

---

## 6. 验收标准

### T1 验收
- [ ] `playwright.config.ts` 包含所有优化配置
- [ ] 测试执行内存峰值 < 500MB
- [ ] 测试通过率 = 100%

### T2 验收
- [ ] `components/` 目录包含 3+ 组件
- [ ] 组件覆盖常用场景
- [ ] 有统一导出入口

### T3 验收
- [ ] `enhanced.fixture.ts` 包含懒加载和内存监控
- [ ] 现有测试可无缝迁移

### T4 验收
- [ ] 有可运行的示例测试
- [ ] 代码量比原有方式减少 30%+

### T5 验收
- [ ] 文档已更新
- [ ] 完整测试套件通过

---

## 7. 相关文件

| 文件 | 操作 |
|------|------|
| `playwright.config.ts` | 修改 |
| `tests/test_ui/components/` | 新建 |
| `tests/test_ui/fixtures/enhanced.fixture.ts` | 新建 |
| `tests/test_ui/demo/components-demo.spec.ts` | 新建 |
| `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` | 更新 |

---

*文档版本: v1.0*  
*创建日期: 2026-02-24*  
*计划类型: UI 测试框架优化*
