# UI 测试适配报告 - v0.10.x 前端变更

> **报告日期**: 2026-03-26
> **版本**: v0.10.4
> **状态**: ✅ 冒烟测试完成，集成测试大部分通过

---

## 1. 问题背景

### 1.1 v0.10.x 前端主要变更

| 变更项 | 描述 | 影响 |
|--------|------|------|
| **Intro 引导页** | 首次访问显示5页引导（commit `7114143`） | 遮挡登录表单，测试无法操作 UI 元素 |
| **changePasswordModal** | admin 首次登录需修改密码 | 测试超时或无法完成登录流程 |
| **BUG-096 修复** | TC 目标日期编辑后渲染问题（commit `4bc5178`） | 需验证测试覆盖 |

### 1.2 问题根因

1. **Intro 引导页逻辑**：
   - 通过 `localStorage.getItem('tracker_intro_seen')` 控制显示
   - 测试中 `localStorage.clear()` 会导致每次都弹出引导页
   - 引导页 `.intro-cta-btn` 覆盖在登录表单之上

2. **HOME 环境变量问题**：
   - `playwright.config.ts` 硬编码 `HOME: '/root'`
   - 普通用户(hqi)无 `/root` 目录写权限
   - 导致 Firefox glib/GIO 配置失败，浏览器挂起

---

## 2. 修复方案

### 2.1 playwright.config.ts 修改

**文件**: `dev/playwright.config.ts`

| 修改项 | 修改前 | 修改后 |
|--------|--------|--------|
| HOME 环境变量 | `HOME: '/root'` | `HOME: process.env.HOME \|\| '/home/hqi'` |
| 移除 headless 硬编码 | `args: ['--headless']` | 移除（使用 xvfb-run 代替） |

**完整修改**:
```typescript
launchOptions: {
  env: {
    HOME: process.env.HOME || '/home/hqi',  // 动态获取当前用户目录
    XDG_RUNTIME_DIR: '/tmp',
    MOZ_ENABLE_WAYLAND: '0',
  },
},
```

### 2.2 冒烟测试修改 (2个文件)

#### 01-smoke.spec.ts

**修改内容**:

1. **添加 beforeEach 处理引导页和密码模态框**:
```typescript
test.beforeEach(async ({ page }) => {
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  // 处理引导页（v0.10.x 新增）
  const introBtn = page.locator('.intro-cta-btn');
  if (await introBtn.isVisible().catch(() => false)) {
    await introBtn.click();
    await page.waitForTimeout(500);
  }
});
```

2. **loginAsAdmin 函数添加密码模态框处理**:
```typescript
async function loginAsAdmin(page: any) {
  await page.fill('#loginUsername', 'admin');
  await page.fill('#loginPassword', 'admin123');
  await page.click('button.login-btn');
  await page.waitForTimeout(1500);

  // 处理首次登录密码修改模态框（v0.10.x 新增）
  const changePwdModal = page.locator('#changePasswordModal');
  if (await changePwdModal.isVisible().catch(() => false)) {
    await page.fill('#newPassword', 'admin123');
    await page.fill('#confirmPassword', 'admin123');
    await page.click('#changePwdModal button.btn-primary');
    await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 });
    await page.waitForTimeout(1000);
  }
  // ...
}
```

3. **SMOKE-001 测试移除重复 goto**:
```typescript
test('SMOKE-001: 页面加载', async ({ page }) => {
  // beforeEach 已经处理了引导页
  await expect(page).toHaveTitle(/Tracker|芯片验证/);
  // ...
});
```

#### 02-login.spec.ts

**修改内容**:

1. **添加 beforeEach 处理引导页**:
```typescript
test.beforeEach(async ({ page }) => {
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  const introBtn = page.locator('.intro-cta-btn');
  if (await introBtn.isVisible().catch(() => false)) {
    await introBtn.click();
    await page.waitForTimeout(500);
  }
});
```

2. **loginAs 函数移除冗余 goto**:
```typescript
async function loginAs(page: any, username: string, password: string) {
  // beforeEach 已经处理了引导页
  await page.fill('#loginUsername', username);
  await page.fill('#loginPassword', password);
  await page.click('button.login-btn');
  await page.waitForTimeout(1500);
}
```

### 2.3 集成测试修改 (16个文件)

| 分类 | 文件数 | 修改方案 |
|------|--------|----------|
| **A. loginAsAdmin 函数** | 8 个 | 更新函数添加引导页+密码模态框处理 |
| **B. beforeEach 添加** | 6 个 | 添加 beforeEach 处理引导页 |
| **C. localStorage.clear()** | 4 个 | 在 clear 后添加引导页处理 |

#### A 类文件 (loginAsAdmin 更新)
- `connections.spec.ts`
- `password.spec.ts`
- `link-status.spec.ts`
- `filter.spec.ts`
- `14-tc-filter-layout.spec.ts`
- `tc.spec.ts`
- `import-export.spec.ts`
- `cp.spec.ts`

#### B 类文件 (beforeEach 添加)
- `cp_link_filter.spec.ts`
- `scroll.spec.ts`
- `13-layout.spec.ts`
- `07-permissions-ui.spec.ts`
- `11-date-validation.spec.ts`
- `08-user-management.spec.ts`

#### C 类文件 (localStorage.clear() 后处理)
- `actual_curve.spec.ts`
- `12-feedback.spec.ts`
- `10-help.spec.ts`
- `09-project-management.spec.ts`

---

## 3. 测试运行结果

### 3.1 冒烟测试 ✅

```
Running 20 tests using 1 worker

  ✓ 01-smoke.spec.ts: SMOKE-001 ~ SMOKE-014 (14/14)
  ✓ 02-login.spec.ts: LOGIN-001 ~ LOGIN-006 (6/6)

✅ 20/20 通过 (1.9 分钟)
```

### 3.2 集成测试 ⚠️

| 文件 | 结果 | 说明 |
|------|------|------|
| 06-permissions-api.spec.ts | ✅ 12/12 | API权限测试 |
| 07-permissions-ui.spec.ts | ✅ 大部分 | UI权限测试 |
| 08-user-management.spec.ts | ✅ 8/8 | 用户管理 |
| 09-project-management.spec.ts | ✅ 4/4 | 项目管理 |
| 10-help.spec.ts | ⚠️ 部分 | 帮助手册(超时) |
| 11-date-validation.spec.ts | ✅ 4/4 | 日期验证 |
| 12-feedback.spec.ts | ✅ 5/5 | 用户反馈 |
| 13-layout.spec.ts | ✅ 2/2 | 布局测试 |
| 14-tc-filter-layout.spec.ts | ✅ 3/3 | TC过滤布局 |
| actual_curve.spec.ts | ⚠️ 部分 | 实际曲线(超时) |
| connections.spec.ts | ⚠️ 部分 | CP-TC关联(超时) |
| cp_link_filter.spec.ts | ✅ 大部分 | CP过滤 |
| cp.spec.ts | ⚠️ 部分 | CP测试(超时) |
| filter.spec.ts | ✅ 3/3 | 过滤功能 |
| import-export.spec.ts | ✅ 14/14 | 导入导出 |
| link-status.spec.ts | ⚠️ 部分 | 关联状态(超时) |
| password.spec.ts | ✅ 1/1 | 密码测试 |
| scroll.spec.ts | ✅ | 滚动测试 |

**说明**: 部分超时问题主要是测试间数据依赖，非引导页问题。

---

## 4. 运行命令

### 4.1 冒烟测试
```bash
cd /projects/management/tracker/dev
PLAYWRIGHT_BROWSERS_PATH=/tmp/.playwright HOME=/home/hqi XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/smoke/ --project=firefox --timeout=60000
```

### 4.2 集成测试
```bash
cd /projects/management/tracker/dev
PLAYWRIGHT_BROWSERS_PATH=/tmp/.playwright HOME=/home/hqi XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/integration/ --project=firefox --timeout=60000
```

### 4.3 环境要求
- Firefox 浏览器 (通过 `npx playwright install firefox` 安装)
- xvfb-run (headless 模式)
- PLAYWRIGHT_BROWSERS_PATH 设置为可写目录

---

## 5. 需要同步更新的文档

以下文档可能需要检查并同步更新：

### 5.1 测试相关文档

| 文档 | 建议检查内容 |
|------|-------------|
| `docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md` | 运行命令是否需要更新环境变量 |
| `docs/DEVELOPMENT/playwright_debug_best_practices.md` | 添加 Intro/密码模态框处理示例 |
| `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` | 更新沙箱环境配置说明 |
| `docs/PLANS/test_coverage_enhancement_plan_v0.10.x.md` | 如存在需更新 |

### 5.2 配置相关文档

| 文档 | 建议检查内容 |
|------|-------------|
| `docs/MANUALS/Tracker_Test_to_Production_Guide_v1.0.md` | 测试环境配置 |
| `docs/PLANS/RELEASE_PROCESS_IMPROVEMENT.md` | 测试脚本配置 |

### 5.3 前端变更记录

| 文档 | 建议添加内容 |
|------|-------------|
| `docs/BUGLOG/tracker_BUG_RECORD.md` | 记录 BUG-096 及引导页变更 |
| `docs/SPECIFICATIONS/tracker_OVERALL_SPECS.md` | 如有 UI 变更说明需同步 |

---

## 6. 待处理事项

### 6.1 需进一步调查的超时问题

以下测试存在超时问题，非引导页原因：

1. **connections.spec.ts** - CP-TC 关联测试
2. **link-status.spec.ts** - 关联状态测试
3. **actual_curve.spec.ts** - 快照相关测试
4. **cp.spec.ts** - 部分 CP CRUD 测试

### 6.2 建议行动

1. [ ] 调查超时测试的数据依赖问题
2. [ ] 检查 `09-project-management.spec.ts` 中的 `localStorage.clear()` 是否必要
3. [ ] 考虑将引导页处理提取为共享 fixture
4. [ ] 更新相关文档

---

## 7. 总结

| 项目 | 状态 |
|------|------|
| Playwright 配置修复 | ✅ 完成 |
| 冒烟测试修复 (2 文件) | ✅ 20/20 通过 |
| 集成测试修复 (16 文件) | ⚠️ 大部分通过 |
| 文档同步 | ⏳ 待处理 |

**关键修改**:
- `playwright.config.ts`: HOME 环境变量改为动态获取
- `01-smoke.spec.ts`: 添加 beforeEach + 密码模态框处理
- `02-login.spec.ts`: 添加 beforeEach 处理引导页
- 16 个集成测试文件: 添加引导页和密码模态框处理

---

*报告生成时间: 2026-03-26 | 署名: Claude Code*
