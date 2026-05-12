# Tracker v0.14.0 测试计划

> **测试版本**: v0.14.0
> **对应规格书**: tracker_SPECS_v0.14.0.md
> **创建日期**: 2026-05-12
> **状态**: 待开发
> **预估开发时间**: 4h (API 2h + UI 2h)

---

## 1. 版本概述

### 1.1 版本目标

实现项目材料包导出功能，支持一键导出项目概览、覆盖率数据、TC/CP统计、Dashboard数据、Feature列表、快照历史、Wiki内容，整理为 ZIP 下载包。

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.14.0.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-EXP-001 | 项目概览导出 | P0 | 1h |
| REQ-EXP-002 | 覆盖率数据导出 | P0 | 1h |
| REQ-EXP-003 | TC/CP 统计导出 | P0 | 1h |
| REQ-EXP-004 | Dashboard 数据导出 | P1 | 2h |
| REQ-EXP-005 | Feature 列表导出 | P1 | 1h |
| REQ-EXP-006 | 快照历史导出 | P2 | 1h |
| REQ-EXP-007 | Wiki 内容导出 | P2 | 1h |
| REQ-EXP-008 | ZIP 打包下载 | P0 | 1h |
| REQ-EXP-009 | 权限控制 | P0 | 0.5h |
| REQ-EXP-010 | API 支持 | P1 | 1h |

---

## 2. API 测试计划

### 2.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── conftest.py                    # 共享 fixture
├── test_export_package.py         # 导出功能测试
```

### 2.2 新增 API 测试用例

#### 2.2.1 导出功能测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| EXP-API-001 | test_export_package_as_admin | 管理员导出项目材料包 | 返回 ZIP 文件，状态码 200 | REQ-EXP-008 |
| EXP-API-002 | test_export_package_as_user | 普通用户调用导出 API | 返回 403 FORBIDDEN | REQ-EXP-009 |
| EXP-API-003 | test_export_package_as_guest | 访客调用导出 API | 返回 403 FORBIDDEN | REQ-EXP-009 |
| EXP-API-004 | test_export_package_unauthenticated | 未登录调用导出 API | 返回 401 UNAUTHORIZED | REQ-EXP-009 |
| EXP-API-005 | test_export_nonexistent_project | 导出不存在的项目 | 返回 404 PROJECT_NOT_FOUND | REQ-EXP-009 |
| EXP-API-006 | test_export_package_content | 验证 ZIP 内容 | ZIP 包含所有预期文件 | REQ-EXP-001~007 |
| EXP-API-007 | test_export_project_overview | 验证项目概览文件 | 包含项目名称、coverage_mode 等 | REQ-EXP-001 |
| EXP-API-008 | test_export_coverage_trend | 验证覆盖率数据 | 包含当前覆盖率、里程碑、历史数据 | REQ-EXP-002 |
| EXP-API-009 | test_export_tc_cp_statistics | 验证 TC/CP 统计 | 包含 TC 状态分布、CP 按 Feature 统计 | REQ-EXP-003 |
| EXP-API-010 | test_export_dashboard_data | 验证 Dashboard 数据 | 包含 Matrix、Owner 分布数据 | REQ-EXP-004 |
| EXP-API-011 | test_export_feature_list | 验证 Feature 列表 | 包含 Feature 统计汇总 | REQ-EXP-005 |
| EXP-API-012 | test_export_snapshots | 验证快照历史 | 包含所有 project_progress 记录 | REQ-EXP-006 |
| EXP-API-013 | test_export_wiki_content | 验证 Wiki 内容 | 包含 index.json、changes_index.json、pages/*.html | REQ-EXP-007 |
| EXP-API-014 | test_export_filename_format | 验证文件名格式 | 文件名为 project_export_{name}_{YYYYMMDD_HHMMSS}.zip | REQ-EXP-008 |

#### 2.2.2 边界条件测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| EXP-API-015 | test_export_special_chars_in_project_name | 项目名含特殊字符 | 空格替换为 _，其他字符移除 | REQ-EXP-008 |
| EXP-API-016 | test_export_empty_project | 空项目（无 TC/CP） | 生成 ZIP，包含空数据文件 | REQ-EXP-001~007 |
| EXP-API-017 | test_export_large_project | 大项目（500+ TC） | 导出时间 < 60秒 | REQ-EXP-008 |

#### 2.2.3 异常场景测试

| 测试 ID | 测试方法 | 测试目标 | 异常场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| EXP-API-018 | test_export_invalid_project_id | 无效项目 ID | 返回 404 PROJECT_NOT_FOUND | REQ-EXP-009 |
| EXP-API-019 | test_export_without_wiki | 项目无 Wiki | ZIP 中无 wiki/ 目录或为空 | REQ-EXP-007 |

### 2.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| client fixture | `conftest.py` | Flask test_client |
| admin_client fixture | `conftest.py` | 管理员权限 test_client |
| user_client fixture | `conftest.py` | 普通用户 test_client |
| test_project fixture | `conftest.py` | 测试项目创建/清理 |

### 2.4 API 测试命令

```bash
# 运行导出功能 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_export_package.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 3. UI 测试计划

### 3.1 测试框架

基于 [UI 测试策略](./DEVELOPMENT/UI_TESTING_STRATEGY.md)，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/
├── conftest.ts                     # Playwright 配置
├── utils/
│   ├── dialog-helper.ts            # Dialog 处理工具
│   └── cleanup.ts                  # 测试数据清理工具
├── specs/
│   └── integration/
│       └── export_package.spec.ts  # 导出功能测试
```

### 3.2 新增 UI 测试用例

#### 3.2.1 功能测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| EXP-UI-001 | export_button_visible_for_admin | 管理员可以看到导出按钮 | REQ-EXP-009 | P0 |
| EXP-UI-002 | export_button_hidden_for_user | 普通用户看不到导出按钮 | REQ-EXP-009 | P0 |
| EXP-UI-003 | export_button_hidden_for_guest | 访客看不到导出按钮 | REQ-EXP-009 | P0 |
| EXP-UI-004 | click_export_downloads_zip | 点击导出按钮下载 ZIP | REQ-EXP-008 | P0 |
| EXP-UI-005 | export_shows_loading_state | 导出中显示加载状态 | REQ-EXP-009 | P1 |

#### 3.2.2 交互测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| EXP-UI-006 | export_success_shows_toast | 导出成功显示 toast | REQ-EXP-009 | P1 |
| EXP-UI-007 | export_failure_shows_error | 导出失败显示错误信息 | REQ-EXP-009 | P1 |

#### 3.2.3 边界场景测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| EXP-UI-008 | export_button_position | 导出按钮在项目列表每行末 | REQ-EXP-009 | P2 |

### 3.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| dialogHelper | `utils/dialog-helper.ts` | 安全处理对话框 |
| cleanupTestData | `utils/cleanup.ts` | 清理测试数据 |

### 3.4 UI 测试命令

```bash
# 运行导出功能 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/export_package.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox

# 运行所有 UI 测试
npx playwright test tests/test_ui/ --project=firefox
```

---

## 4. 测试开发任务分解

### 4.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发导出权限测试 (EXP-API-001~005) | test_export_package.py | 1h | 待开始 |
| 开发导出内容验证测试 (EXP-API-006~014) | test_export_package.py | 0.5h | 待开始 |
| 开发边界/异常测试 (EXP-API-015~019) | test_export_package.py | 0.5h | 待开始 |

### 4.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发权限可见性测试 (EXP-UI-001~003) | export_package.spec.ts | 0.5h | 待开始 |
| 开发导出交互测试 (EXP-UI-004~005) | export_package.spec.ts | 0.5h | 待开始 |
| 开发成功/失败反馈测试 (EXP-UI-006~007) | export_package.spec.ts | 0.5h | 待开始 |
| 开发边界场景测试 (EXP-UI-008) | export_package.spec.ts | 0.5h | 待开始 |

---

## 5. 验收标准

### 5.1 API 测试验收

- [ ] 所有 19 个新增测试用例通过
- [ ] 测试 ID 编号规范 (EXP-API-XXX)
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理

### 5.2 UI 测试验收

- [ ] 所有 8 个新增测试用例通过
- [ ] 使用 dialog-helper 处理对话框
- [ ] 使用 cleanup 工具清理测试数据

---

## 6. 测试执行计划

### 6.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_export_package.py -v

# 3. 运行 UI 测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/export_package.spec.ts --project=firefox
```

### 6.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速、稳定，验证后端逻辑 |
| 2 | UI 集成测试 | 验证前端功能和权限控制 |

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| ZIP 内容验证复杂 | 测试失败 | 使用 zipfile 模块正确解析 ZIP 内容 |
| 大项目导出超时 | 测试失败 | 设置合理的超时时间（60秒） |
| Wiki 目录可能为空 | 测试失败 | 测试无 Wiki 的项目场景 |
| 测试数据冲突 | 测试失败 | 使用时间戳命名，每次清理 |

---

## 8. 测试数据准备

### 8.1 测试项目要求

| 测试场景 | 项目要求 |
|----------|----------|
| 基本导出 | 有 TC、CP、Feature 的项目 |
| 大项目导出 | 500+ TC 的项目 |
| 空项目导出 | 无 TC、CP 的项目 |
| 无 Wiki 导出 | 项目无 Wiki 目录 |
| 含 Wiki 导出 | 项目有 Wiki 内容（中英文） |

### 8.2 测试数据清理

- 测试后自动删除创建的测试项目
- 使用 `cleanupProjectData` 工具

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-05-12 | 初始测试计划 | OpenClaw |

---

**文档创建时间**: 2026-05-12 12:05:00
**创建人**: OpenClaw