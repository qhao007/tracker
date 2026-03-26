# UI 测试适配报告 - v0.10.x 前端变更

> **报告日期**: 2026-03-27
> **版本**: v0.10.4
> **状态**: ✅ 全部集成测试通过

---

## 1. 问题背景

### 1.1 v0.10.x 前端主要变更

| 变更项 | 描述 | 影响 |
|--------|------|------|
| **Intro 引导页** | 首次访问显示5页引导（commit `7114143`） | 遮挡登录表单，测试无法操作 UI 元素 |
| **changePasswordModal** | admin 首次登录需修改密码 | 测试超时或无法完成登录流程 |
| **BUG-096 修复** | TC 目标日期编辑后渲染问题（commit `4bc5178`） | 需验证测试覆盖 |
| **BUG-098** | `saveCP()` 缺少 `renderCP()` 调用 | 创建的 CP 不显示在列表中 |
| **BUG-099** | `deleteCP()` 缺少 `renderCP()` 调用 | 删除的 CP 仍显示在列表中 |
| **BUG-100** | `deleteTC()` 缺少 `renderTC()` 调用 | 删除的 TC 仍显示在列表中 |

### 1.2 问题根因

1. **Intro 引导页逻辑**：
   - 通过 `localStorage.getItem('tracker_intro_seen')` 控制显示
   - 测试中 `localStorage.clear()` 会导致每次都弹出引导页
   - 引导页 `.intro-cta-btn` 覆盖在登录表单之上

2. **HOME 环境变量问题**：
   - `playwright.config.ts` 硬编码 `HOME: '/root'`
   - 普通用户(hqi)无 `/root` 目录写权限
   - 导致 Firefox glib/GIO 配置失败，浏览器挂起

3. **UI 渲染同步问题 (BUG-098/BUG-099/BUG-100)**：
   - **问题类型**: 异步数据加载后未同步刷新 UI
   - `saveCP()` 和 `deleteCP()` 只调用 `loadCP()` 加载数据
   - `deleteTC()` 只调用 `loadTC()` 加载数据
   - 没有调用 `renderCP()`/`renderTC()` 刷新 UI
   - 导致创建的 CP 不显示，删除的 CP/TC 仍显示

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

### 2.2 前端 Bug 修复 (index.html)

#### BUG-098: saveCP() 缺少 renderCP()

**位置**: `index.html` 第 2852 行

**修改前**:
```javascript
if (result.success) { closeModal('cpModal'); await Promise.all([loadCP(), loadStats()]); }
```

**修改后**:
```javascript
if (result.success) { closeModal('cpModal'); await Promise.all([loadCP(), loadStats()]); renderCP(); }
```

#### BUG-099: deleteCP() 缺少 renderCP()

**位置**: `index.html` 第 2885 行

**修改前**:
```javascript
await loadCP();
} catch (e) { alert('删除失败'); }
```

**修改后**:
```javascript
await loadCP();
renderCP();
} catch (e) { alert('删除失败'); }
```

#### BUG-100: deleteTC() 缺少 renderTC()

**位置**: `index.html` 第 2906 行

**修改前**:
```javascript
await Promise.all([loadTC(), loadStats()]);
} catch (e) { alert('删除失败'); }
```

**修改后**:
```javascript
await Promise.all([loadTC(), loadStats()]);
renderTC();
} catch (e) { alert('删除失败'); }
```

### 2.3 冒烟测试修改

#### 01-smoke.spec.ts

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
  // ... 登录逻辑 ...
  // 处理首次登录密码修改模态框（v0.10.x 新增）
  const changePwdModal = page.locator('#changePasswordModal');
  if (await changePwdModal.isVisible().catch(() => false)) {
    await page.fill('#newPassword', 'admin123');
    await page.fill('#confirmPassword', 'admin123');
    await page.click('#changePasswordModal button.btn-primary');
    await page.waitForSelector('#changePasswordModal', { state: 'hidden', timeout: 10000 });
    await page.waitForTimeout(1000);
  }
}
```

#### 02-login.spec.ts

1. **添加 beforeEach 处理引导页**
2. **loginAs 函数移除冗余 goto**

### 2.4 集成测试修改

#### connections.spec.ts

| 修改项 | 说明 |
|--------|------|
| 移除 afterEach 中的 `cleanupProjectData()` | 该函数调用 page.reload() 导致项目选择丢失 |
| 移除 CONN-002/003/004 的 `test.skip` | BUG-098 修复后不再需要跳过 |

#### link-status.spec.ts

| 修改项 | 说明 |
|--------|------|
| UI-LINK-003/004 关联逻辑 | 修复选择器，使用 TC Modal 中的 `#cpCheckboxes` 勾选 CP |

#### actual_curve.spec.ts

| 修改项 | 说明 |
|--------|------|
| UI-ACT-012 添加引导页处理 | reload 后需要重新处理引导页 |

#### cp.spec.ts

| 修改项 | 说明 |
|--------|------|
| `loginAsAdmin` 移到文件顶部 | 供第二个 describe 块使用 |
| CP-009 reload 后添加引导页处理 | 等待 500ms 确保引导页动态加载完成 |

#### 10-help.spec.ts

| 修改项 | 说明 |
|--------|------|
| HELP-004/008 使用 `waitUntil: 'commit'` | 避免 CDN 加载 marked.js 超时 |

---

## 3. 测试运行结果

### 3.1 冒烟测试 ✅

```
Running 14 tests using 1 worker

  ✓ 01-smoke.spec.ts: SMOKE-001 ~ SMOKE-014 (14/14)

✅ 14/14 通过 (1.3 分钟)
```

### 3.2 集成测试 ✅

| 文件 | 结果 | 说明 |
|------|------|------|
| connections.spec.ts | ✅ 5/5 | CP-TC 关联测试 |
| link-status.spec.ts | ✅ 4/4 | 关联状态测试 |
| actual_curve.spec.ts | ✅ 11/11 | 实际曲线与快照测试 |
| cp.spec.ts | ✅ 8/8 | CP CRUD 测试 (1 skipped 为设计跳过) |
| 10-help.spec.ts | ✅ 5/5 | 帮助手册测试 (4 skipped 为设计跳过) |

**总计**: 33 个测试通过

---

## 4. Bug 记录

### BUG-098: saveCP() 未调用 renderCP()

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-26 |
| **修复日期** | 2026-03-27 |
| **修复人** | Claude Code |
| **Commit** | `c15caaa` (chore: 更新 VERSION 文件为 0.10.4) |

**描述**: v0.10.x 中 `saveCP()` 创建 CP 后调用 `loadCP()` 但未调用 `renderCP()` 刷新 UI。

**影响测试**:
- CONN-002, CONN-003, CONN-004
- CP-001, CP-002, CP-003, CP-009

**修复**: 在 `await Promise.all([loadCP(), loadStats()]);` 后添加 `renderCP();`

---

### BUG-099: deleteCP() 未调用 renderCP()

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-27 |
| **修复日期** | 2026-03-27 |
| **修复人** | Claude Code |

**描述**: `deleteCP()` 删除 CP 后调用 `loadCP()` 但未调用 `renderCP()` 刷新 UI。

**影响测试**: CP-003 (删除 CP)

**修复**: 在 `await loadCP();` 后添加 `renderCP();`

---

### BUG-100: deleteTC() 未调用 renderTC()

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-27 |
| **修复日期** | 2026-03-27 |
| **修复人** | Claude Code |

**描述**: `deleteTC()` 删除 TC 后调用 `loadTC()` 和 `loadStats()` 但未调用 `renderTC()` 刷新 UI，导致删除的 TC 仍显示在列表中。

**影响测试**: SMOKE-014 (删除 TC)

**修复**: 在 `await Promise.all([loadTC(), loadStats()]);` 后添加 `renderTC();`

---

## 5. 运行命令

### 5.1 冒烟测试
```bash
cd /projects/management/tracker/dev
HOME=/home/hqi XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/smoke/ --project=firefox --timeout=60000
```

### 5.2 集成测试
```bash
cd /projects/management/tracker/dev
HOME=/home/hqi XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/integration/ --project=firefox --timeout=60000
```

### 5.3 单个测试文件
```bash
cd /projects/management/tracker/dev
HOME=/home/hqi XDG_RUNTIME_DIR=/tmp npx playwright test tests/test_ui/specs/integration/connections.spec.ts --project=firefox --timeout=60000
```

### 5.4 环境要求
- Firefox 浏览器 (通过 `npx playwright install firefox` 安装)
- HOME 环境变量指向可写目录
- XDG_RUNTIME_DIR 设置为 `/tmp`

---

## 6. 修复的文件清单

### 前端文件
| 文件 | 修改内容 |
|------|----------|
| `dev/index.html` | BUG-098: saveCP() 添加 renderCP(); BUG-099: deleteCP() 添加 renderCP(); BUG-100: deleteTC() 添加 renderTC(); |

### 测试文件
| 文件 | 修改内容 |
|------|----------|
| `dev/playwright.config.ts` | HOME 环境变量动态获取 |
| `dev/tests/test_ui/specs/smoke/01-smoke.spec.ts` | beforeEach + 密码模态框处理 |
| `dev/tests/test_ui/specs/smoke/02-login.spec.ts` | beforeEach 处理引导页 |
| `dev/tests/test_ui/specs/integration/connections.spec.ts` | 移除 cleanupProjectData, 移除 test.skip |
| `dev/tests/test_ui/specs/integration/link-status.spec.ts` | 修复关联逻辑选择器 |
| `dev/tests/test_ui/specs/integration/actual_curve.spec.ts` | 添加引导页处理 |
| `dev/tests/test_ui/specs/integration/cp.spec.ts` | loginAsAdmin 移到全局, 修复 reload 处理 |
| `dev/tests/test_ui/specs/integration/10-help.spec.ts` | waitUntil: 'commit' 避免 CDN 超时 |

### 文档文件
| 文件 | 修改内容 |
|------|----------|
| `docs/BUGLOG/tracker_BUG_RECORD.md` | 添加 BUG-098, BUG-099, BUG-100 记录 |

---

## 7. 回归风险评估

### 7.1 renderCP()/renderTC() 修复影响

| 修复内容 | 风险等级 | 说明 |
|----------|----------|------|
| `saveCP()` 添加 `renderCP()` | 低 | 创建后刷新列表显示，符合预期行为 |
| `deleteCP()` 添加 `renderCP()` | 低 | 删除后刷新列表显示，符合预期行为 |
| `deleteTC()` 添加 `renderTC()` | 低 | 删除后刷新列表显示，符合预期行为 |

**回归测试**: 已通过全部 47 个测试（14 冒烟 + 33 集成），无回归风险。

---

## 8. 总结

| 项目 | 状态 |
|------|------|
| Playwright 配置修复 | ✅ 完成 |
| 冒烟测试修复 | ✅ 14/14 通过 |
| 集成测试修复 | ✅ 33/33 通过 |
| BUG-098 修复 (saveCP) | ✅ 完成 |
| BUG-099 修复 (deleteCP) | ✅ 完成 |
| BUG-100 修复 (deleteTC) | ✅ 完成 |

**关键修改**:
- `index.html`: saveCP() 添加 renderCP(); deleteCP() 添加 renderCP(); deleteTC() 添加 renderTC()
- `playwright.config.ts`: HOME 环境变量改为动态获取
- 集成测试: 引导页处理、关联逻辑修复、CDN 超时处理

---

*报告更新: 2026-03-27 | 署名: Claude Code*
