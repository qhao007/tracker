# Tracker v0.7.1 测试计划

> **版本**: v1.1 | **创建日期**: 2026-02-21 | **状态**: 待执行 | **更新日期**: 2026-02-22
> **目标版本**: v0.7.1
> **测试框架**: Python pytest (API) + Playwright CLI (UI)

---

## 1. 需求分析

### 1.1 测试范围

本次测试覆盖 v0.7.1 的四个核心功能：

| # | 功能 | 优先级 | 测试类型 |
|---|------|--------|----------|
| 1 | 用户登录系统（含 guest 角色） | P0 | API + UI |
| 2 | 权限管理（RBAC） | P1 | API + UI |
| 3 | 项目删除功能 | P2 | API + UI |
| 4 | 用户手册 | P3 | UI |

### 1.2 测试目标

- 验证登录/登出功能正常
- 验证三种角色（admin/user/guest）权限控制正确
- 验证项目删除功能（含自动备份）
- 验证用户手册显示正常
- 验证 created_by 字段正确填充

### 1.3 不包含的测试

- 性能测试（待后续迭代）
- 安全渗透测试（待后续迭代）

---

## 2. 任务分解

### 2.1 测试任务总览

| ID | 任务 | 依赖 | 优先级 | 类型 |
|----|------|------|--------|------|
| T1 | 用户登录 API 测试 | - | P0 | API |
| T2 | 访客登录 API 测试 | T1 | P0 | API |
| T3 | 用户管理 API 测试 | T1 | P0 | API |
| T4 | Session 管理测试 | T1 | P0 | API |
| T5 | 权限控制 API 测试 | T1+T3 | P1 | API |
| T6 | 项目删除 API 测试 | T1 | P2 | API |
| T7 | created_by 填充测试 | T1 | P1 | API |
| T8 | 用户登录 UI 测试 | - | P0 | UI |
| T9 | 角色权限 UI 测试 | T8 | P1 | UI |
| T10 | 项目删除 UI 测试 | T8 | P2 | UI |
| T11 | 用户手册 UI 测试 | - | P3 | UI |

---

## 3. API 测试用例设计

### 3.1 用户登录 API 测试 (T1)

#### 3.1.1 基础登录测试

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| AUTH-API-001 | 正确用户名+密码登录 | 返回用户信息，200 |
| AUTH-API-002 | 错误用户名登录 | 返回错误，401 |
| AUTH-API-003 | 错误密码登录 | 返回错误，401 |
| AUTH-API-004 | 空用户名登录 | 返回错误，400 |
| AUTH-API-005 | 空密码登录（非 guest） | 返回错误，400 |

#### 3.1.2 默认账户测试

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| AUTH-API-006 | admin 账户登录 | 成功，role=admin |
| AUTH-API-007 | guest 账户登录 | 成功，role=guest |

---

### 3.2 访客登录 API 测试 (T2)

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| GUEST-API-001 | 访客登录按钮（无需密码） | 登录成功 |
| GUEST-API-002 | guest 账户被禁用后访客登录 | 返回错误，403 |
| GUEST-API-003 | guest 会话超时 | Session 过期 |

---

### 3.3 用户管理 API 测试 (T3)

#### 3.3.1 创建用户

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| USER-API-001 | admin 创建 user 账户 | 成功创建 |
| ADMIN-API-002 | admin 创建 guest 账户 | 成功创建 |
| USER-API-003 | 普通 user 创建账户 | 失败，403 |

#### 3.3.2 用户列表

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| USER-API-004 | admin 获取用户列表 | 返回所有用户 |
| USER-API-005 | user 获取用户列表 | 失败，403 |

#### 3.3.3 禁用/启用用户

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| USER-API-006 | admin 禁用 guest 账户 | 成功 |
| USER-API-007 | admin 启用 guest 账户 | 成功 |
| USER-API-008 | 禁用后的 user 登录 | 失败，401 |

#### 3.3.4 重置密码

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| USER-API-009 | admin 重置 user 密码 | 成功 |
| USER-API-010 | admin 重置 guest 密码 | 失败（guest 无密码） |

#### 3.3.5 删除用户

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| USER-API-011 | admin 删除 user 账户 | 成功 |
| USER-API-012 | admin 删除 guest 账户 | 失败（不可删除） |
| USER-API-013 | admin 删除自己 | 失败（不可删除自己） |

---

### 3.4 Session 管理测试 (T4)

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| SESSION-API-001 | 登录后获取当前用户 | 返回用户信息 |
| SESSION-API-002 | 未登录访问受保护 API | 返回 401 |
| SESSION-API-003 | 登出功能 | Session 清除 |
| SESSION-API-004 | Session 超时 | 自动登出 |

---

### 3.5 权限控制 API 测试 (T5)

#### 3.5.1 角色权限验证

| 用例 ID | 角色 | 操作 | 预期结果 |
|---------|------|------|----------|
| PERM-API-001 | admin | 创建 TC | ✅ 成功 |
| PERM-API-002 | admin | 删除项目 | ✅ 成功 |
| PERM-API-003 | admin | 用户管理 | ✅ 成功 |
| PERM-API-004 | user | 创建 TC | ✅ 成功 |
| PERM-API-005 | user | 删除项目 | ❌ 403 |
| PERM-API-006 | user | 用户管理 | ❌ 403 |
| PERM-API-007 | guest | 创建 TC | ❌ 403 |
| PERM-API-008 | guest | 删除项目 | ❌ 403 |
| PERM-API-009 | guest | 用户管理 | ❌ 403 |
| PERM-API-010 | guest | 查看项目 | ✅ 成功 |

#### 3.5.2 导出权限

| 用例 ID | 角色 | 操作 | 预期结果 |
|---------|------|------|----------|
| PERM-API-011 | admin | 导出 TC | ✅ 成功 |
| PERM-API-012 | user | 导出 TC | ✅ 成功 |
| PERM-API-013 | guest | 导出 TC | ❌ 403 |

#### 3.5.3 导入权限

| 用例 ID | 角色 | 操作 | 预期结果 |
|---------|------|------|----------|
| PERM-API-014 | admin | 导入 TC | ✅ 成功 |
| PERM-API-015 | user | 导入 TC | ✅ 成功 |
| PERM-API-016 | guest | 导入 TC | ❌ 403 |

#### 3.5.4 项目管理权限

| 用例 ID | 角色 | 操作 | 预期结果 |
|---------|------|------|----------|
| PERM-API-017 | admin | 创建项目 | ✅ 成功 |
| PERM-API-018 | admin | 编辑项目 | ✅ 成功 |
| PERM-API-019 | user | 创建项目 | ❌ 403 |
| PERM-API-020 | user | 编辑项目 | ❌ 403 |
| PERM-API-021 | guest | 创建项目 | ❌ 403 |
| PERM-API-022 | guest | 编辑项目 | ❌ 403 |

#### 3.5.5 批量操作权限

| 用例 ID | 角色 | 操作 | 预期结果 |
|---------|------|------|----------|
| PERM-API-023 | admin | 批量操作 TC | ✅ 成功 |
| PERM-API-024 | user | 批量操作 TC | ✅ 成功 |
| PERM-API-025 | guest | 批量操作 TC | ❌ 403 |

---

### 3.6 项目删除 API 测试 (T6)

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| DELETE-API-001 | admin 删除项目 | 成功删除，.db 文件删除 |
| DELETE-API-002 | 删除前创建归档备份 | 备份文件存在 |
| DELETE-API-003 | user 删除项目 | 失败，403 |
| DELETE-API-004 | guest 删除项目 | 失败，403 |
| DELETE-API-005 | 删除不存在的项目 | 失败，404 |

---

### 3.7 created_by 填充测试 (T7)

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| CREATED-API-001 | 创建 TC，验证 created_by | 填充当前用户名 |
| CREATED-API-002 | 创建 CP，验证 created_by | 填充当前用户名 |
| CREATED-API-003 | 现有 TC 查询 created_by | NULL 或已有值 |

---

### 3.8 暴力破解防护测试

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| BRUTE-API-001 | 连续 5 次错误密码 | 账户锁定 15 分钟 |
| BRUTE-API-002 | 锁定期间登录 | 返回错误 |
| BRUTE-API-003 | 15 分钟后解锁 | 可正常登录 |

---

### 3.9 Session 安全配置测试

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| SECURITY-API-001 | 检查 Cookie HttpOnly 属性 | 设置为 True |
| SECURITY-API-002 | 检查 Cookie SameSite 属性 | 设置为 Lax |
| SECURITY-API-003 | 检查未登录访问 / | 重定向到登录页或返回 401 |

---

## 4. UI 测试用例设计

### 4.1 用户登录 UI 测试 (T8)

#### 4.1.1 登录页面

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| AUTH-UI-001 | 登录页面显示 | 用户名、密码输入框，登录按钮 |
| AUTH-UI-002 | 访客登录按钮显示 | 按钮可见 |
| AUTH-UI-003 | 错误密码提示 | 显示错误信息 |

#### 4.1.2 登录流程

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| AUTH-UI-004 | admin 登录成功 | 跳转首页，显示用户名 |
| AUTH-UI-005 | user 登录成功 | 跳转首页，显示用户名 |
| AUTH-UI-006 | guest 登录成功 | 跳转首页，显示"访客" |
| AUTH-UI-007 | 登录后显示用户名 | Header 显示当前用户 |

#### 4.1.3 访客登录

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| GUEST-UI-001 | 点击访客登录 | 自动登录，跳转首页 |
| GUEST-UI-002 | guest 禁用后点击 | 提示"访客登录已禁用" |

---

### 4.2 角色权限 UI 测试 (T9)

#### 4.2.1 菜单权限

| 用例 ID | 角色 | 预期结果 |
|---------|------|----------|
| PERM-UI-001 | admin | 项目管理按钮可见 |
| PERM-UI-002 | admin | 用户管理按钮可见 |
| PERM-UI-003 | user | 项目管理按钮不可见 |
| PERM-UI-004 | user | 用户管理按钮不可见 |
| PERM-UI-005 | guest | 项目管理按钮不可见 |
| PERM-UI-006 | guest | 用户管理按钮不可见 |

#### 4.2.2 按钮权限

| 用例 ID | 角色 | 操作 | 预期结果 |
|---------|------|------|----------|
| PERM-UI-007 | admin | 添加按钮 | ✅ 可见 |
| PERM-UI-008 | user | 添加按钮 | ✅ 可见 |
| PERM-UI-009 | guest | 添加按钮 | ❌ 不可见 |
| PERM-UI-010 | admin | 导出按钮 | ✅ 可见 |
| PERM-UI-011 | user | 导出按钮 | ✅ 可见 |
| PERM-UI-012 | guest | 导出按钮 | ❌ 不可见 |

---

### 4.3 项目删除 UI 测试 (T10)

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| DELETE-UI-001 | admin 删除按钮可见 | 可见 |
| DELETE-UI-002 | user/guest 删除按钮不可见 | 不可见 |
| DELETE-UI-003 | 点击删除弹出确认框 | 确认对话框显示 |
| DELETE-UI-004 | 确认删除 | 项目删除成功 |
| DELETE-UI-005 | 取消删除 | 项目未被删除 |

#### 4.3.1 项目管理 UI 权限测试

| 用例 ID | 角色 | 预期结果 |
|---------|------|----------|
| PROJECT-UI-001 | user | 项目管理按钮不可见 |
| PROJECT-UI-002 | guest | 项目管理按钮不可见 |
| PROJECT-UI-003 | admin | 项目管理按钮可见 |

---

### 4.4 用户手册 UI 测试 (T11)

| 用例 ID | 说明 | 预期结果 |
|---------|------|----------|
| MANUAL-UI-001 | 帮助按钮显示 | 按钮在 Header |
| MANUAL-UI-002 | 点击帮助 | 新标签页打开 |
| MANUAL-UI-003 | Markdown 渲染 | 内容正确显示为 HTML |

---

## 5. 测试数据设计

### 5.1 测试用户

| 用户名 | 密码 | 角色 | 用途 |
|--------|------|------|------|
| admin | admin123 | admin | 管理员测试 |
| user01 | user123 | user | 普通用户测试 |
| guest | (无密码) | guest | 访客测试 |

### 5.2 测试项目

| 项目名 | 用途 |
|--------|------|
| TestAuth_Project | 权限测试 |

### 5.3 测试数据清理

- 测试后自动清理创建的测试用户
- 测试后自动清理创建的测试项目
- 使用时间戳确保数据唯一性

---

## 6. 执行计划

### 6.1 开发阶段测试

| 阶段 | 测试内容 | 执行时机 |
|------|----------|----------|
| 开发中 | 单个功能 API 测试 | 开发完成后立即执行 |
| 提交前 | ESLint + API 冒烟 + UI 冒烟 | git commit 前 |
| 合并前 | 完整 API 测试 + 完整 UI 测试 | PR/MR 前 |

### 6.2 提交前检查清单

```
□ ESLint 检查通过 (bash check_frontent.sh)
□ API 登录相关测试通过
□ Playwright 登录/权限相关 UI 测试通过
```

### 6.3 合并前检查清单

```
□ 完整 API 测试通过（所有新增用例）
□ 完整 UI 测试通过（所有新增用例）
□ 测试报告已生成
```

---

## 7. 验收标准

### 7.1 功能验收

| 功能 | 验收标准 |
|------|----------|
| 登录系统 | admin/user/guest 三种角色均可登录 |
| 访客登录 | 点击按钮自动登录，禁用后提示 |
| 用户管理 | admin 可创建/禁用/删除用户 |
| 权限控制 | 前端按钮隐藏 + 后端 API 校验 |
| 项目删除 | 删除前自动备份，可恢复 |
| 用户手册 | Markdown 正确渲染 |

### 7.2 测试通过率

| 测试类型 | 目标 |
|----------|------|
| API 测试 | 100% 通过 |
| UI 测试 | 100% 通过 |
| 整体 | 100% 通过 |

---

## 8. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Session 测试不稳定 | 中 | 使用固定超时时间测试 |
| 浏览器兼容性问题 | 低 | 使用 Firefox 测试 |
| 测试数据冲突 | 中 | 使用时间戳唯一命名 |
| 暴力破解测试耗时 | 低 | 跳过实际等待，使用 mock |

---

## 9. 测试命令速查

### 9.1 API 测试

```bash
cd /projects/management/tracker/dev

# 运行新增的认证相关 API 测试
PYTHONPATH=. pytest tests/test_api/ -v -k "auth or login or user or permission"

# 运行项目删除 API 测试
PYTHONPATH=. pytest tests/test_api/ -v -k "delete"
```

### 9.2 UI 测试

```bash
cd /projects/management/tracker/dev

# 运行登录 UI 测试
npx playwright test tests/test_ui/specs/smoke/ --project=firefox -g "login"

# 运行权限 UI 测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox -g "permission"
```

---

## 10. 文档更新记录

| 日期 | 变更 | 状态 |
|------|------|------|
| 2026-02-21 | 初始版本 | 待执行 |
| 2026-02-22 | 新增项目管理权限测试(PERM-API-017~025)、Session安全测试(SECURITY-API)、项目管理UI测试(PROJECT-UI) | 待执行 |

---

## 附件

- 需求规格书: `/projects/management/feedbacks/reviewed/tracker_FEATURE_REQUESTS_v0.7.1_20260221.md`
- 测试策略: `/projects/management/tracker/docs/DEVELOPMENT/API_TESTING_STRATEGY.md`
- UI 测试策略: `/projects/management/tracker/docs/DEVELOPMENT/UI_TESTING_STRATEGY.md`
- 执行计划: `/projects/management/tracker/docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md`
