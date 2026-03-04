# Smoke 测试简化方案

> **名称**: UI Smoke 测试精简计划
> **创建日期**: 2026-03-04
> **状态**: ✅ 已确认

---

## 1. 背景

当前 `tests/test_ui/specs/smoke/` 目录下有 **13 个测试文件**，共 **56 个测试用例**。

存在以下问题：
1. **重复测试多**: 权限相关测试分散在 6 个文件中，内容高度重叠
2. **分类不合理**: 功能性测试（项目删除、创建者）混入冒烟测试
3. **文件粒度细**: 13 个文件中包含 1-10 个测试，部分文件过少

---

## 2. 设计原则

### 2.1 核心理念

- **Smoke 测试**: 快速验证核心功能，执行时间 < 5 分钟
- **Integration 测试**: 完整回归测试，覆盖所有功能
- **100% 覆盖**: Smoke + Integration 一起覆盖所有功能

### 2.2 测试分层

| 层级 | 目标 | 执行时间 | 覆盖范围 |
|------|------|----------|----------|
| Smoke | 快速冒烟 | ~3 min | 核心路径 |
| Integration | 完整回归 | ~15 min | 所有功能 |
| **总计** | **完整覆盖** | **~18 min** | **100%** |

---

## 3. 当前测试统计

| 文件 | 测试数 | 功能类别 |
|------|--------|----------|
| smoke.spec.ts | 10 | 核心冒烟 |
| login.spec.ts | 6 | 登录 |
| api-permission.spec.ts | 6 | API 权限 |
| auth-permission.spec.ts | 6 | 认证权限 |
| user-role-permission.spec.ts | 5 | 用户角色权限 |
| project-delete.spec.ts | 5 | 项目删除 |
| user-management.spec.ts | 4 | 用户管理 |
| frontend-permission.spec.ts | 4 | 前端权限 |
| project-permission.spec.ts | 3 | 项目权限 |
| manual.spec.ts | 3 | 帮助手册 |
| ui-permission.spec.ts | 2 | UI 权限 |
| toggle-user.spec.ts | 1 | 切换用户 |
| created-by.spec.ts | 1 | 创建者 |
| **总计** | **56** | |

---

## 4. 简化方案

### 4.1 目标

- 测试文件: 13 → 4
- Smoke 测试: 56 → ~16
- 覆盖率: Smoke 核心路径 + Integration 完整覆盖 = 100%

### 4.2 合并后 Smoke 结构 (16 tests)

```
tests/test_ui/specs/smoke/
├── 01-smoke.spec.ts      (10 tests) - 核心冒烟
└── 02-login.spec.ts     (6 tests)  - 登录功能
```

### 4.3 详细设计

#### 01-smoke.spec.ts (14 tests)

**原则**: 核心冒烟 - 页面加载 + **核心 CRUD (F001/F004/F005)** + 权限按钮

| ID | 测试名称 | 验证内容 | 对应规格 |
|----|----------|----------|----------|
| SMOKE-001 | 页面加载 | 首页可访问，显示核心元素 | 基础 |
| SMOKE-002 | admin 登录成功 | admin 登录后跳转首页 | 认证 |
| SMOKE-003 | guest 登录成功 | guest 登录成功 | 认证 |
| SMOKE-004 | 错误密码提示 | 错误密码显示错误信息 | 认证 |
| SMOKE-005 | 项目切换 | 下拉框可选择项目 | **F001** |
| **SMOKE-006** | **创建项目** | **创建新项目，验证存在** | **F001 (核心!)** |
| SMOKE-007 | CP 标签切换 | 点击 CP 标签显示内容 | F004 |
| **SMOKE-008** | **创建 CP** | **点击 +CP，填写必填字段，创建成功** | **F004** |
| **SMOKE-009** | **编辑 CP** | **点击编辑，修改内容，保存成功** | **F004** |
| **SMOKE-010** | **删除 CP** | **点击删除，确认后删除成功** | **F004** |
| SMOKE-011 | TC 标签切换 | 点击 TC 标签显示内容 | F005 |
| **SMOKE-012** | **创建 TC** | **点击 +TC，填写必填字段，创建成功** | **F005** |
| **SMOKE-013** | **编辑 TC** | **点击编辑，修改内容，保存成功** | **F005** |
| **SMOKE-014** | **删除 TC** | **点击删除，确认后删除成功** | **F005** |

#### 02-login.spec.ts (6 tests)

**原则**: 登录功能 - 成功/失败/角色

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| LOGIN-001 | 登录后显示用户名 | 登录后在 Header 显示用户 |
| LOGIN-002 | guest 无用户管理按钮 | guest 登录后不显示用户管理 |
| LOGIN-003 | user 无删除项目按钮 | user 登录后不显示删除按钮 |
| LOGIN-004 | 登录后 Cookie | 登录后 session cookie 存在 |
| LOGIN-005 | 登出功能 | 点击退出后跳转登录页 |
| LOGIN-006 | Progress Charts Tab | 点击切换到进度图表 |

### 4.4 核心功能覆盖确认

根据 `tracker_OVERALL_SPECS.md` 规格书:

| 功能ID | 功能 | Smoke 测试 | Integration |
|--------|------|------------|-------------|
| **F001** | 项目管理（创建/切换） | ✅ SMOKE-005,006 | - |
| **F004** | Cover Points 管理 | ✅ SMOKE-008-010 | ✅ 完整测试 |
| **F005** | Test Cases 管理 | ✅ SMOKE-012-014 | ✅ 完整测试 |
| F006 | TC 关联 CP | - | ✅ Integration |
| F007 | 状态跟踪 | - | ✅ Integration |
| F020-F025 | 日期/批量/Priority | - | ✅ Integration |
| F027-F030 | 过滤功能 | - | ✅ Integration |
| F031-F037 | 进度图表/快照 | - | ✅ Integration |

**Smoke 测试覆盖**: 3 个核心 P0 功能 (F001, F004, F005)
**Integration 测试覆盖**: 所有其他功能

---

## 5. Integration 补充方案

### 5.1 需要从 Smoke 移到 Integration 的测试

| 原 Smoke 文件 | 测试数 | 移到 Integration |
|---------------|--------|------------------|
| api-permission.spec.ts | 6 | 06-permissions-api.spec.ts |
| auth-permission.spec.ts | 6 | 06-permissions-api.spec.ts |
| user-role-permission.spec.ts | 5 | 07-permissions-ui.spec.ts |
| frontend-permission.spec.ts | 4 | 07-permissions-ui.spec.ts |
| ui-permission.spec.ts | 2 | 07-permissions-ui.spec.ts |
| project-permission.spec.ts | 3 | 07-permissions-ui.spec.ts |
| user-management.spec.ts | 4 | 08-user-management.spec.ts |
| project-delete.spec.ts | 5 | 09-project-management.spec.ts |
| manual.spec.ts | 3 | 10-help.spec.ts |
| toggle-user.spec.ts | 1 | 08-user-management.spec.ts |
| created-by.spec.ts | 1 | 05-tc.spec.ts (已有) |

### 5.2 新增 Integration 文件结构

```
tests/test_ui/specs/integration/
├── existing files...
├── 06-permissions-api.spec.ts   (新增) - API 权限
├── 07-permissions-ui.spec.ts     (新增) - UI 权限
├── 08-user-management.spec.ts     (新增) - 用户管理
├── 09-project-management.spec.ts  (新增) - 项目管理
└── 10-help.spec.ts               (新增) - 帮助手册
```

### 5.3 新增 Integration 测试内容

#### 06-permissions-api.spec.ts (12 tests)

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| PERM-API-001 | 未登录访问项目列表 → 401 | 认证边界 |
| PERM-API-002 | guest 创建 TC → 403 | API 权限 |
| PERM-API-003 | guest 删除 TC → 403 | API 权限 |
| PERM-API-004 | guest 更新 TC → 403 | API 权限 |
| PERM-API-005 | guest 创建 CP → 403 | API 权限 |
| PERM-API-006 | guest 删除 CP → 403 | API 权限 |
| PERM-API-007 | guest 更新 CP → 403 | API 权限 |
| PERM-API-008 | admin 创建 TC → 200 | Admin 权限 |
| PERM-API-009 | admin 删除 TC → 200 | Admin 权限 |
| PERM-API-010 | user 访问用户列表 → 403 | 角色权限 |
| PERM-API-011 | admin 删除项目 → 200 | Admin 权限 |
| PERM-API-012 | user 删除项目 → 403 | 角色权限 |

#### 07-permissions-ui.spec.ts (9 tests)

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| PERM-UI-001 | 未登录不显示项目列表 | UI 权限 |
| PERM-UI-002 | guest 无用户管理按钮 | UI 权限 |
| PERM-UI-003 | admin 有用户管理按钮 | UI 权限 |
| PERM-UI-004 | admin 有添加项目按钮 | UI 权限 |
| PERM-UI-005 | user 无删除按钮 | UI 权限 |
| PERM-UI-006 | admin 访问项目 → 可见 | 项目权限 |
| PERM-UI-007 | user 访问项目 → 可见 | 项目权限 |
| PERM-UI-008 | guest 访问项目 → 可见 | 项目权限 |
| PERM-UI-009 | user 可以创建 TC | 角色权限 |

#### 08-user-management.spec.ts (5 tests)

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| USER-001 | admin 看到用户管理入口 | 用户管理 |
| USER-002 | 点击打开用户管理模态框 | 用户管理 |
| USER-003 | 添加用户按钮存在 | 用户管理 |
| USER-004 | 用户列表有内容区域 | 用户管理 |
| USER-005 | 禁用/启用 guest 账户 | 账户管理 |

#### 09-project-management.spec.ts (5 tests)

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| PROJ-001 | 项目选择器可见 | 项目管理 |
| PROJ-002 | guest 可访问项目 | 项目权限 |
| PROJ-003 | 点击删除弹出确认框 | 删除确认 |
| PROJ-004 | 确认删除后项目被删除 | 删除功能 |
| PROJ-005 | 取消删除后项目保留 | 取消删除 |

#### 10-help.spec.ts (3 tests)

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| HELP-001 | 帮助按钮在 Header 显示 | 帮助入口 |
| HELP-002 | 点击帮助打开手册页面 | 帮助功能 |
| HELP-003 | 手册页面可访问 | 帮助内容 |

---

## 6. 覆盖分析

### 6.1 Smoke + Integration 覆盖矩阵

| 功能模块 | Smoke | Integration | 总计 |
|---------|-------|-------------|------|
| 页面加载 | 1 | 0 | 1 |
| 项目切换 | 1 | 0 | 1 |
| 标签切换 | 2 | 0 | 2 |
| 模态框 | 1 | 0 | 1 |
| 登录/登出 | 6 | 0 | 6 |
| 权限(API) | 0 | 12 | 12 |
| 权限(UI) | 2 | 9 | 11 |
| 用户管理 | 0 | 5 | 5 |
| 项目管理 | 0 | 5 | 5 |
| CP 功能 | 0 | 8 | 8 |
| TC 功能 | 0 | 11 | 11 |
| 导入导出 | 0 | 14 | 14 |
| 进度图表 | 1 | 6 | 7 |
| 计划曲线 | 0 | 12 | 12 |
| 实际曲线/快照 | 0 | 11 | 11 |
| 连接关系 | 0 | 5 | 5 |
| 帮助手册 | 1 | 3 | 4 |
| **总计** | **15** | **101** | **116** |

### 6.2 执行时间估算

| 测试集 | 测试数 | 估计时间 |
|--------|--------|----------|
| Smoke | 16 | ~3 min |
| Integration (原有) | 67 | ~12 min |
| Integration (新增) | 34 | ~6 min |
| **总计** | **117** | **~21 min** |

---

## 7. 实施计划

### 7.1 实施步骤

1. **简化 Smoke 测试** (10 min)
   - 创建 01-smoke.spec.ts (10 tests)
   - 创建 02-login.spec.ts (6 tests)
   - 删除旧的 13 个文件

2. **创建 Integration 权限测试** (20 min)
   - 创建 06-permissions-api.spec.ts
   - 创建 07-permissions-ui.spec.ts

3. **创建 Integration 管理测试** (15 min)
   - 创建 08-user-management.spec.ts
   - 创建 09-project-management.spec.ts
   - 创建 10-help.spec.ts

4. **验证测试** (10 min)
   - 运行所有测试确保通过

### 7.2 预计时间

| 步骤 | 时间 |
|------|------|
| 简化 Smoke | 10 min |
| 创建权限测试 | 20 min |
| 创建管理测试 | 15 min |
| 验证测试 | 10 min |
| **总计** | **~55 min** |

---

## 8. 讨论要点

> 待与产品负责人讨论确认

1. **测试覆盖度**: 116 个测试是否满足 100% 覆盖要求？
2. **执行频率**: Smoke 每日运行？Integration 每周运行？
3. **新增测试**: 新增的 34 个 Integration 测试是否需要全部实现？

---

**文档创建时间**: 2026-03-04
**创建人**: 小栗子
