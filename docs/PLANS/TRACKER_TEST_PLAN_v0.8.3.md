# Tracker v0.8.3 测试计划

> **测试版本**: v0.8.3
> **对应规格书**: `docs/SPECIFICATIONS/tracker_SPECS_v0.8.3.md`
> **创建日期**: 2026-03-04
> **状态**: 规划中
> **预估测试时间**: 2 小时

---

## 1. 版本概述

### 1.1 版本目标

v0.8.3 主要目标：
1. 创建项目时自动创建测试用户
2. 项目日期必填验证
3. 前端常量管理

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.8.3.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-083-001 | 创建项目时自动创建测试用户 | P1 | 1h |
| REQ-083-002 | 项目日期必填验证 | P2 | 0.5h |
| REQ-083-003 | 前端常量管理 | P3 | 0.5h |

---

## 2. 存放位置

**文件路径**: `docs/PLANS/TRACKER_TEST_PLAN_v0.8.3.md`

---

## 3. API 测试计划

### 3.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── test_api.py                     # 基础 CRUD 测试
├── test_api_progress.py           # v0.8.0: 进度基础 API
├── test_api_planned_curve.py     # v0.8.1: 计划曲线 API
├── test_api_actual_curve.py      # v0.8.2: 实际曲线 API
└── test_api_user.py              # v0.8.3 新增：用户管理 API
```

### 3.2 新增 API 测试用例

#### 3.2.1 用户创建测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-USR-001 | test_create_user | 创建普通用户 | 用户创建成功 | REQ-083-001 |
| API-USR-002 | test_create_duplicate_user | 创建重复用户名 | 返回错误 | REQ-083-001 |
| API-USR-003 | test_create_user_with_project | 创建项目时创建测试用户 | 用户创建成功 | REQ-083-001 |

#### 3.2.2 项目日期验证测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PRJ-001 | test_create_project_missing_date | 创建项目缺少日期 | 返回错误 | REQ-083-002 |
| API-PRJ-002 | test_create_project_valid_dates | 创建项目有效日期 | 创建成功 | REQ-083-002 |
| API-PRJ-003 | test_create_project_end_before_start | 结束日期早于开始日期 | 返回错误 | REQ-083-002 |

### 3.3 API 测试文件结构

```python
# dev/tests/test_api/test_api_user.py
import pytest
import sqlite3
import os
import json
from pathlib import Path

# 测试配置
TEST_DB_PREFIX = "User_Test_"
TEST_DB_DIR = Path(__file__).parent.parent.parent / "shared" / "data" / "test_data"

@pytest.fixture
def test_db():
    """创建测试数据库"""
    ...

class TestUserAPI:
    """用户 API 测试"""
    
    def test_create_user(self, test_db):
        """测试创建普通用户"""
        ...
    
    def test_create_duplicate_user(self, test_db):
        """测试创建重复用户名"""
        ...
```

---

## 4. UI 测试计划

### 4.1 测试框架

基于 [UI 测试策略](./DEVELOPMENT/UI_TESTING_STRATEGY.md)，UI 测试使用 **Playwright CLI (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/specs/
├── smoke/                    # 冒烟测试
│   ├── 01-smoke.spec.ts
│   └── 02-login.spec.ts
│
└── integration/             # 集成测试
    ├── 06-permissions-api.spec.ts
    ├── 07-permissions-ui.spec.ts
    ├── 08-user-management.spec.ts     # v0.8.3 新增
    ├── 09-project-management.spec.ts
    ├── 10-help.spec.ts
    ├── actual_curve.spec.ts
    ├── planned_curve.spec.ts
    ├── progress_charts.spec.ts
    ├── cp.spec.ts
    ├── tc.spec.ts
    └── connections.spec.ts
```

### 4.2 新增 UI 测试用例

#### 4.2.1 测试用户创建测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 | 状态 |
|---------|----------|----------|----------|----------|------|
| UI-USR-001 | test_create_project_with_test_user | 创建项目时创建测试用户 | 复选框默认勾选 | REQ-083-001 | ✅ 已实现 |
| UI-USR-002 | test_test_user_credentials | 创建后显示测试用户凭据 | 显示用户名密码 | REQ-083-001 | ✅ 已实现 |
| UI-USR-003 | test_login_with_test_user | 使用测试用户登录 | 登录成功 | REQ-083-001 | ✅ 已实现 |
| UI-USR-004 | test_test_user_permissions | 测试用户权限受限 | 无 admin 功能 | REQ-083-001 | ✅ 已实现 |

#### 4.2.2 项目日期验证测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 | 状态 |
|---------|----------|----------|----------|----------|------|
| UI-PRJ-001 | test_create_project_no_dates | 创建项目不填日期 | 显示错误提示 | REQ-083-002 | ✅ 已实现 |
| UI-PRJ-002 | test_create_project_with_dates | 创建项目填有效日期 | 创建成功 | REQ-083-002 | ✅ 已实现 |
| UI-PRJ-003 | test_create_project_invalid_dates | 结束日期早于开始日期 | 显示错误提示 | REQ-083-002 | ✅ 已实现 |

#### 4.2.3 常量管理测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 | 状态 |
|---------|----------|----------|----------|----------|------|
| UI-CONST-001 | test_login_flow | 登录流程正常 | 登录成功 | REQ-083-003 | ✅ 已实现 |
| UI-CONST-002 | test_project_crud | 项目 CRUD 正常 | 功能正常 | REQ-083-003 | ✅ 已实现 |

### 4.3 UI 测试代码示例

```typescript
// dev/tests/test_ui/specs/integration/08-user-management.spec.ts

import { test, expect } from '@playwright/test';

test.describe('用户管理 - v0.8.3', () => {
  
  test('创建项目时创建测试用户', async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button:has-text("登录")');
    
    // 创建项目
    await page.click('button:has-text("新建项目")');
    
    // 验证"创建测试用户"复选框存在且默认勾选
    const checkbox = page.locator('#createTestUser');
    await expect(checkbox).toBeChecked();
    
    // 填写项目信息
    await page.fill('#projectName', 'Test Project');
    await page.fill('#startDate', '2026-01-01');
    await page.fill('#endDate', '2026-12-31');
    
    // 提交
    await page.click('button:has-text("创建")');
    
    // 验证测试用户创建成功提示
    await expect(page.locator('.test-user-info')).toContainText('test_user');
  });
  
  test('使用测试用户登录', async ({ page }) => {
    await page.goto('http://localhost:8081');
    await page.fill('#username', 'test_user');
    await page.fill('#password', 'test_user123');
    await page.click('button:has-text("登录")');
    
    // 验证登录成功
    await expect(page.locator('.project-selector')).toBeVisible();
  });
});
```

---

## 5. 测试执行计划

### 5.1 执行顺序

| 阶段 | 测试类型 | 执行命令 | 预计时间 |
|------|----------|----------|----------|
| 1 | API 测试 | `pytest tests/test_api/test_api_user.py` | 2 min |
| 2 | API 测试 | `pytest tests/test_api/test_api.py` (日期验证) | 5 min |
| 3 | UI Smoke | `npx playwright test tests/test_ui/specs/smoke/` | 3 min |
| 4 | UI Integration | `npx playwright test tests/test_ui/specs/integration/` | 20 min |

### 5.2 测试数据准备

```bash
# 清理测试数据
python3 scripts/tracker_ops.py clean

# 同步用户数据
python3 scripts/tracker_ops.py sync
```

### 5.3 回归测试

| 测试类型 | 覆盖范围 | 执行命令 |
|----------|----------|----------|
| 完整 API 测试 | 所有 API | `pytest tests/test_api/ -v` |
| Smoke 测试 | 核心功能 | `npx playwright test tests/test_ui/specs/smoke/` |

---

## 6. 验收检查清单

### 6.1 REQ-083-001 自动创建测试用户

- [ ] API: 创建用户成功
- [ ] API: 重复用户名返回错误
- [ ] UI: 复选框默认勾选
- [ ] UI: 显示测试用户凭据
- [ ] UI: 测试用户可登录
- [ ] UI: 测试用户权限受限

### 6.2 REQ-083-002 项目日期必填

- [ ] API: 缺少日期返回错误
- [ ] API: 有效日期创建成功
- [ ] API: 结束日期早于开始日期返回错误
- [ ] UI: 缺少日期显示错误提示
- [ ] UI: 有效日期创建成功

### 6.3 REQ-083-003 前端常量管理

- [ ] 功能: 登录流程正常
- [ ] 功能: 项目 CRUD 正常
- [ ] 功能: CP/TC 管理正常
- [ ] 回归: 无功能退化

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 测试用户密码安全 | 中 | 使用固定测试密码，仅用于测试环境 |
| 日期验证边界 | 低 | 覆盖所有日期格式边界情况 |
| 常量替换遗漏 | 中 | 全面回归测试 |

---

## 8. 测试时间估算

| 任务 | 预估时间 |
|------|----------|
| API 测试开发 | 1h |
| UI 测试开发 | 1h |
| 测试执行 | 0.5h |
| 问题修复 | 0.5h |
| **总计** | **~3h** |

---

## 9. 关联文档

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.8.3.md` |
| API 测试策略 | `docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| UI 测试策略 | `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` |
| v0.8.2 测试计划 | `docs/PLANS/TRACKER_TEST_PLAN_v0.8.2.md` |
