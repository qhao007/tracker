# Tracker v0.8.3 版本开发规格书

> **版本**: v0.8.3
> **创建日期**: 2026-03-04
> **状态**: 规划中
> **关联需求**: 
> - ISSUE-008: admin 首次登录强制改密码
> - v0.8.2 规格书: 日期必填

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | 创建项目时自动创建测试用户 | P1 | 1h |
| 2 | 项目日期必填验证 | P2 | 1h |
| 3 | 前端常量管理 | P3 | 2h |
| | **总计** | | **~4h** |

### 1.2 背景

v0.8.2 已完成实际曲线和快照管理功能。v0.8.3 聚焦于测试便利性和代码质量改进：

- **便利**: 创建项目时自动创建测试用户，方便调试和演示
- **验证**: 项目创建/编辑时日期必填，避免无效项目
- **质量**: 前端代码常量统一管理，提升可维护性

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 自动创建测试用户 | admin 强制改密码 (ISSUE-008 延后) |
| 日期必填验证 | TypeScript 类型检查 |
| 常量管理 | HTTPS 支持 |

---

## 2. 需求详情

### 2.1 功能需求 #1: 创建项目时自动创建测试用户

**需求编号**: REQ-083-001

**需求描述**:
创建项目时自动创建一个普通用户（test_user），用于测试和调试。

**业务规则**:
- 创建项目时自动创建测试用户
- 用户名：test_user
- 密码：test_user123
- 角色：user（非 admin）
- 用户名需要避免重复（如 test_user_项目名）

**前端需求**:
- 创建项目对话框中添加"同时创建测试用户"复选框（默认勾选）
- 显示生成的测试用户名和密码

**后端需求**:
- 项目创建成功后，自动创建对应的测试用户
- 用户名格式：`test_user_{project_name}` 或 `test_user`
- 密码固定：`test_user123`
- 角色：`user`
- 如用户已存在，跳过创建

**API 设计**:
```
POST /api/projects (创建项目)
Request:
{
  "name": "string",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "create_test_user": true  // 新增字段
}

Response:
{
  "success": true,
  "project": {...},
  "test_user": {
    "username": "test_user_项目名",
    "password": "test_user123"
  }
}
```

### 2.2 功能需求 #2: 项目日期必填验证

**需求编号**: REQ-083-002

**需求描述**:
v0.8.2 规格书中提到"日期必填"，需要在项目创建和编辑时强制验证日期字段。

**业务规则**:
- 项目创建时，起始日期和结束日期必填
- 项目编辑时，日期可以更新
- 日期格式：YYYY-MM-DD
- 结束日期必须晚于起始日期

**前端需求**:
- 创建项目对话框中，日期字段标记为必填（*）
- 提交前验证日期已填写
- 显示友好的错误提示

**后端需求**:
- 项目创建 API 验证日期必填
- 项目更新 API 验证日期格式
- 返回明确的错误信息

**API 扩展**:
```
POST /api/projects (创建项目)
Request:
{
  "name": "string",
  "start_date": "YYYY-MM-DD",  // 必填
  "end_date": "YYYY-MM-DD",    // 必填
  ...
}

Response:
{
  "success": false,
  "error": "start_date 和 end_date 为必填项"
}
```

### 2.3 功能需求 #3: 前端常量管理

**需求编号**: REQ-083-003

**需求描述**:
前端代码中 Session key 分散在代码中（ISSUE-009/012），需要统一管理。

**问题来源**: ISSUE-009, ISSUE-012

**前端需求**:
- 创建 `app_constants.js` 文件
- 统一管理以下常量：
  ```javascript
  const SESSION_KEYS = {
    USER: 'user_id',
    USERNAME: 'username',
    ROLE: 'role'
  };
  
  const API_ENDPOINTS = {
    PROJECTS: '/api/projects',
    COVER_POINTS: '/api/cover-points',
    // ...
  };
  
  const UI_CONSTANTS = {
    DEFAULT_PAGE_SIZE: 50,
    DATE_FORMAT: 'YYYY-MM-DD',
    // ...
  };
  ```
- 所有引用改为使用常量
- 便于后续维护和修改

---

## 3. 数据库变更

### 3.1 新增字段

| 表 | 字段 | 类型 | 说明 |
|----|------|------|------|
| users | username | TEXT | 用户名（唯一） |
| users | password | TEXT | 密码哈希 |
| users | role | TEXT | 角色 (admin/user/guest) |

> 注：users 表已存在，此功能只需在创建项目时向 users 表插入新用户。

### 3.2 项目表验证

| 表 | 字段 | 变更 | 说明 |
|----|------|------|------|
| projects | start_date | 添加非空验证 | 创建时必填 |
| projects | end_date | 添加非空验证 | 创建时必填 |

### 3.3 测试用户创建

```sql
-- 创建测试用户（如不存在）
INSERT OR IGNORE INTO users (username, password, role) 
VALUES ('test_user', 'test_user123', 'user');

-- 或使用项目名区分
INSERT OR IGNORE INTO users (username, password, role) 
VALUES ('test_user_项目名', 'test_user123', 'user');
```
-- 为现有 admin 用户设置 must_change_password = False
UPDATE users SET must_change_password = 0 WHERE role = 'admin';

-- 为非 admin 用户设置为 True（可选，视需求定）
-- UPDATE users SET must_change_password = 1 WHERE role != 'admin';
```

---

## 4. 前端页面变更

### 4.1 登录后检查流程

```
用户登录
    ↓
检查 must_change_password
    ↓
├─ true → 显示强制改密码对话框 → 修改成功后刷新
└─ false → 正常跳转首页
```

### 4.2 项目日期验证

- 创建项目对话框：日期字段添加 `required` 标记
- 提交前增加前端验证
- 后端 API 返回明确错误信息

---

## 5. 测试计划

### 5.1 自动创建测试用户 (#1)

| 测试用例 | 预期结果 |
|----------|----------|
| 创建项目时勾选"创建测试用户" | 自动创建 test_user 用户 |
| 创建项目时不勾选 | 不创建测试用户 |
| 用户名重复 | 跳过创建，不报错 |
| 用测试用户登录 | 登录成功，功能受限 |

### 5.2 项目日期必填 (#2)

| 测试用例 | 预期结果 |
|----------|----------|
| 创建项目不填日期 | 提示日期为必填项 |
| 创建项目填有效日期 | 创建成功 |
| 结束日期早于起始日期 | 提示结束日期必须晚于起始日期 |

### 5.3 常量管理 (#3)

| 测试用例 | 预期结果 |
|----------|----------|
| 功能测试 | 所有功能正常使用 |
| 常量引用测试 | 引用统一，无硬编码 |

---

## 6. 验收标准

### 6.1 自动创建测试用户 (#1)

- [ ] 创建项目时显示"创建测试用户"复选框（默认勾选）
- [ ] 勾选后创建项目自动创建 test_user 用户
- [ ] 显示生成的测试用户名和密码
- [ ] 用户名重复时跳过创建
- [ ] 测试用户可登录，功能受限（非 admin）

### 6.2 项目日期必填 (#2)

- [ ] 创建项目时日期字段标记必填
- [ ] 不填日期无法提交
- [ ] 填写有效日期可以正常创建
- [ ] 结束日期早于起始日期有错误提示

### 6.3 常量管理 (#3)

- [ ] 创建 app_constants.js 文件
- [ ] Session keys 使用常量引用
- [ ] API endpoints 使用常量引用
- [ ] 所有功能正常工作

---

## 7. 开发计划

### 7.1 开发任务

| 任务 | 状态 | 预计时间 |
|------|------|----------|
| 后端：创建测试用户 API | ⏳ 待完成 | 0.5h |
| 后端：项目创建时自动创建测试用户 | ⏳ 待完成 | 0.5h |
| 前端：添加"创建测试用户"复选框 | ⏳ 待完成 | 0.5h |
| 前端：显示测试用户名密码 | ⏳ 待完成 | 0.5h |
| 前端：项目日期必填验证 | ⏳ 待完成 | 1h |
| 前端：创建 app_constants.js | ⏳ 待完成 | 1h |
| 前端：替换所有常量引用 | ⏳ 待完成 | 1h |
| 测试验证 | ⏳ 待完成 | 1h |

### 7.2 预计总时间

**~6h** (约 0.5 个工作日)

---

## 8. 关联文档

| 文档 | 说明 |
|------|------|
| ISSUE-009 | 前端代码缺少常量管理 |
| ISSUE-012 | Session key 命名分散 |
| ISSUE-008 | admin 首次登录强制改密码 (延后) |
| tracker_SPECS_v0.8.2.md | v0.8.2 规格书 |
| tracker_OVERALL_SPECS.md | 总体规格书 |
