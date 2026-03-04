# Smoke 测试 **计划简化方案

>名称**: UI Smoke 测试精简计划
> **创建日期**: 2026-03-04
> **状态**: 待讨论

---

## 1. 背景

当前 `tests/test_ui/specs/smoke/` 目录下有 **13 个测试文件**，共 **56 个测试用例**。

存在以下问题：
1. **重复测试多**: 权限相关测试分散在 6 个文件中，内容高度重叠
2. **分类不合理**: 功能性测试（项目删除、创建者）混入冒烟测试
3. **文件粒度细**: 13 个文件中包含 1-10 个测试，部分文件过少

---

## 2. 当前测试统计

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

## 3. 问题分析

### 3.1 权限测试重复

| 测试文件 | 测试内容 | 与其他文件重叠 |
|----------|----------|----------------|
| api-permission.spec.ts | guest 增删改 TC/CP | 与 auth-permission 重叠 |
| auth-permission.spec.ts | 未登录/API/用户权限 | 与其他权限测试重叠 |
| frontend-permission.spec.ts | UI 按钮可见性 | 与 ui-permission 重叠 |
| ui-permission.spec.ts | guest/admin 按钮 | 与 frontend 重叠 |
| user-role-permission.spec.ts | user 角色限制 | 与 auth 重叠 |
| project-permission.spec.ts | 三种角色访问项目 | 重复验证 |

**6 个文件** 测试权限相关内容，可合并。

### 3.2 测试分类问题

- `smoke.spec.ts` 混入业务逻辑（SMOKE-005 创建项目）
- `project-delete.spec.ts` 应属于功能测试，非冒烟测试
- `created-by.spec.ts` 仅 1 个测试，单独文件过于细化

### 3.3 执行效率

56 个测试用例全部顺序执行，耗时较长。实际上很多测试可以并行或跳过。

---

## 4. 简化方案

### 4.1 目标

- 测试文件: 13 → 4
- 测试用例: 56 → ~24
- 减少: **57%**

### 4.2 合并后结构

```
tests/test_ui/specs/smoke/
├── 01-smoke.spec.ts      (8 tests) - 核心冒烟
├── 02-login.spec.ts     (4 tests) - 登录功能
├── 03-permissions.spec.ts (6 tests) - 权限测试
└── 04-functionality.spec.ts (6 tests) - 核心功能
```

### 4.3 详细设计

#### 01-smoke.spec.ts (8 tests)

**原则**: 只测试最基础的 UI 元素加载和导航

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| SMOKE-001 | 页面加载 | 首页可访问，显示核心元素 |
| SMOKE-002 | 项目切换 | 下拉框可选择项目 |
| SMOKE-003 | CP 标签切换 | 点击 CP 标签显示内容 |
| SMOKE-004 | TC 标签切换 | 点击 TC 标签显示内容 |
| SMOKE-005 | 模态框打开/关闭 | 点击按钮打开，点击遮罩关闭 |
| SMOKE-006 | 登录后显示用户名 | 登录后在 Header 显示用户 |
| SMOKE-007 | guest 无用户管理按钮 | guest 登录后不显示用户管理 |
| SMOKE-008 | user 无删除项目按钮 | user 登录后不显示删除按钮 |

#### 02-login.spec.ts (4 tests)

**原则**: 只保留登录核心功能

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| LOGIN-001 | 登录表单显示 | 用户名/密码输入框存在 |
| LOGIN-002 | admin 登录成功 | admin 登录后跳转首页 |
| LOGIN-003 | guest 登录成功 | guest 登录成功 |
| LOGIN-004 | 错误密码提示 | 错误密码显示错误信息 |

#### 03-permissions.spec.ts (6 tests)

**原则**: 合并所有权限测试，每个场景只保留 1 个代表性测试

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| PERM-001 | 未登录访问 API 被拒绝 | 返回 401 |
| PERM-002 | guest 无法创建 TC | 返回 403 |
| PERM-003 | guest 无法删除 TC | 返回 403 |
| PERM-004 | admin 可删除项目 | 删除成功 |
| PERM-005 | user 无法删除项目 | 返回 403 |
| PERM-006 | 三种角色都能访问项目 | 返回 200 |

#### 04-functionality.spec.ts (6 tests)

**原则**: 核心业务功能，每个功能保留代表性测试

| ID | 测试名称 | 验证内容 |
|----|----------|----------|
| FUNC-001 | 创建并验证项目 | 创建新项目，验证存在 |
| FUNC-002 | 用户管理模态框 | admin 可打开用户管理 |
| FUNC-003 | 项目删除确认 | 删除前弹出确认框 |
| FUNC-004 | 帮助手册可访问 | 点击帮助打开手册 |
| FUNC-005 | CP 模态框打开 | 点击 +CP 打开对话框 |
| FUNC-006 | TC 模态框打开 | 点击 +TC 打开对话框 |

---

## 5. 实施计划

### 5.1 实施步骤

1. **创建新测试文件** (4 个文件)
2. **逐个迁移测试用例**
3. **运行验证确保功能不变**
4. **删除旧测试文件**
5. **更新 CLAUDE.md 文档**

### 5.2 预计时间

| 步骤 | 时间 |
|------|------|
| 创建新文件 | 10 min |
| 迁移测试 | 30 min |
| 验证测试 | 20 min |
| 清理旧文件 | 5 min |
| **总计** | **~65 min** |

---

## 6. 讨论要点

> 待与产品负责人讨论确认

1. **测试覆盖度**: 精简后是否满足质量要求？
2. **测试策略**: 是否需要保留部分重复测试作为回归保护？
3. **执行频率**: 精简后测试是否改为每日运行？

---

## 7. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 漏测风险 | 精简可能遗漏边界情况 | 保留核心路径，覆盖率 > 80% |
| 维护性 | 新人理解成本 | 注释清晰，每个测试有说明 |

---

**文档创建时间**: 2026-03-04
**创建人**: 小栗子
