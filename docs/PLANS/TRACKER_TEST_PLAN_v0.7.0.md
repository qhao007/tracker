# Tracker v0.7.0 测试计划

> **测试版本**: v0.7.0
> **对应规格书**: `docs/SPECIFICATIONS/tracker_SPECS_v0.7.0.md`
> **创建日期**: 2026-02-16
> **状态**: 🔄 开发中
> **预估开发时间**: 已完成 (API 24 用例, UI 12 用例)

---

## 1. 版本概述

### 1.1 版本目标

v0.7.0 版本主要实现导入导出功能，支持从 Excel (.xlsx) 或 CSV 文件批量导入/导出 Cover Points 和 Test Cases。

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.7.0.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 | 状态 |
|----------|----------|--------|----------|------|
| #10 | 导入功能 (CP/TC) | P1 | 20h | 🔄 开发中 |
| #11 | 导出功能 (CP/TC) | P1 | 13h | 🔄 开发中 |
| #ISSUE-001 | 项目选择框宽度修复 | P3 | 0.5h | ✅ 已完成 |
| - | TS 类型修复 | Tech Debt | - | ✅ 已完成 |

---

## 2. 存放位置

> **重要**：测试计划文件应放在 `docs/PLANS/` 目录下，不要放在 `docs/REPORTS/` 目录下。

| 文档类型 | 目录 |
|----------|------|
| 测试计划 (Test Plan) | `docs/PLANS/` ← 放在这里 |
| 测试报告 (Test Report) | `docs/REPORTS/` |
| 代码审查报告 | `docs/REPORTS/` |

---

## 3. API 测试计划

### 3.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── test_api_import_export.py     # 本版本新增测试文件 (24 个测试用例)
```

### 3.2 新增 API 测试用例

#### 3.2.1 模板下载测试

| 测试 ID | 测试方法 | 测试目标 | 对应规格 |
|---------|----------|----------|----------|
| API-IMP-001 | test_get_cp_template | 下载 CP 导入模板 | #10 |
| API-IMP-002 | test_get_tc_template | 下载 TC 导入模板 | #10 |
| API-IMP-003 | test_get_template_default_type | 默认模板类型 | #10 |
| API-IMP-004 | test_get_template_invalid_type | 无效模板类型 | #10 |

#### 3.2.2 导入功能测试

| 测试 ID | 测试方法 | 测试目标 | 对应规格 |
|---------|----------|----------|----------|
| API-IMP-005 | test_import_cp_success | CP Excel 导入成功 | #10 |
| API-IMP-006 | test_import_tc_success | TC Excel 导入成功 | #10 |
| API-IMP-007 | test_import_cp_missing_required_field | CP 必填字段缺失 | #10 |
| API-IMP-008 | test_import_tc_missing_required_field | TC 必填字段缺失 | #10 |
| API-IMP-009 | test_import_cp_duplicate | CP 重名检测 | #10 |
| API-IMP-010 | test_import_missing_params | 缺少必要参数 | #10 |
| API-IMP-011 | test_import_invalid_type | 无效导入类型 | #10 |
| API-IMP-012 | test_import_invalid_project | 无效项目 ID | #10 |

#### 3.2.3 CSV 导入测试

| 测试 ID | 测试方法 | 测试目标 | 对应规格 |
|---------|----------|----------|----------|
| API-IMP-013 | test_import_cp_csv | CP CSV 导入 | #10 |
| API-IMP-014 | test_import_tc_csv | TC CSV 导入 | #10 |
| API-IMP-015 | test_import_multiple_rows_csv | CSV 多行导入 | #10 |

#### 3.2.4 导出功能测试

| 测试 ID | 测试方法 | 测试目标 | 对应规格 |
|---------|----------|----------|----------|
| API-EXP-001 | test_export_cp_xlsx | CP Excel 导出 | #11 |
| API-EXP-002 | test_export_tc_xlsx | TC Excel 导出 | #11 |
| API-EXP-003 | test_export_cp_csv | CP CSV 导出 | #11 |
| API-EXP-004 | test_export_tc_csv | TC CSV 导出 | #11 |
| API-EXP-005 | test_export_default_format | 默认导出格式 | #11 |
| API-EXP-006 | test_export_missing_params | 缺少必要参数 | #11 |
| API-EXP-007 | test_export_invalid_type | 无效导出类型 | #11 |
| API-EXP-008 | test_export_invalid_project | 无效项目 ID | #11 |
| API-EXP-009 | test_export_empty_project | 空项目导出 | #11 |

### 3.3 测试结果

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 状态 |
|----------|------|------|------|------|------|
| API 测试 | 24 | 24 | 0 | 0 | ✅ 通过 |

### 3.4 API 测试命令

```bash
# 运行导入导出 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_import_export.py -v
```

---

## 4. UI 集成测试计划

### 4.1 测试框架

基于 [UI 测试策略](./DEVELOPMENT/UI_TESTING_STRATEGY.md)，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/
├── conftest.ts                     # Playwright 配置
├── utils/
│   ├── dialog-helper.ts            # Dialog 处理工具
│   └── cleanup.ts                  # 测试数据清理工具
└── specs/
    └── integration/
        └── import-export.spec.ts   # 本版本新增测试文件 (12 个测试用例)
```

### 4.2 新增 UI 测试用例

#### 4.2.1 导入功能测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| IMP-001 | CP 导入按钮存在 | 验证 CP 页面导入按钮存在 | #10 | P1 |
| IMP-002 | CP 导入对话框打开 | 验证点击导入按钮打开对话框 | #10 | P1 |
| IMP-003 | TC 导入按钮存在 | 验证 TC 页面导入按钮存在 | #10 | P1 |
| IMP-004 | TC 导入对话框打开 | 验证点击导入按钮打开对话框 | #10 | P1 |

#### 4.2.2 导出功能测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| EXP-001 | CP 导出按钮存在 | 验证 CP 页面导出按钮存在 | #11 | P1 |
| EXP-002 | CP 导出对话框打开 | 验证点击导出按钮打开对话框 | #11 | P1 |
| EXP-003 | CP 导出对话框显示项目信息 | 验证对话框显示项目和记录数 | #11 | P2 |
| EXP-004 | TC 导出按钮存在 | 验证 TC 页面导出按钮存在 | #11 | P1 |
| EXP-005 | TC 导出对话框打开 | 验证点击导出按钮打开对话框 | #11 | P1 |

#### 4.2.3 模板下载测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| TMPL-001 | CP 模板下载 | 验证模板下载功能 | #10 | P1 |

#### 4.2.4 对话框交互测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| DLG-001 | 导入对话框关闭 | 验证导入对话框可正常关闭 | #10 | P2 |
| DLG-002 | 导出对话框关闭 | 验证导出对话框可正常关闭 | #11 | P2 |

### 4.3 测试结果

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 状态 |
|----------|------|------|------|------|------|
| UI 测试 | 12 | 0 | 2 | 10 | ⚠️ 内存不足 |

**注**：UI 测试因内存限制 (SIGKILL) 导致进程终止，部分测试未能执行。测试选择器验证正确，按钮代码存在于 `index.html`。

### 4.4 UI 测试命令

```bash
# 运行导入导出 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/import-export.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 5. 测试开发任务分解

### 5.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 模板下载测试 | `test_api_import_export.py` | 2h | ✅ 已完成 |
| 导入功能测试 | `test_api_import_export.py` | 4h | ✅ 已完成 |
| CSV 导入测试 | `test_api_import_export.py` | 2h | ✅ 已完成 |
| 导出功能测试 | `test_api_import_export.py` | 3h | ✅ 已完成 |

### 5.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 导入功能 UI 测试 | `import-export.spec.ts` | 2h | ✅ 已完成 |
| 导出功能 UI 测试 | `import-export.spec.ts` | 2h | ✅ 已完成 |
| 模板下载 UI 测试 | `import-export.spec.ts` | 1h | ✅ 已完成 |
| 对话框交互测试 | `import-export.spec.ts` | 1h | ✅ 已完成 |

---

## 6. 验收标准

### 6.1 API 测试验收

- [x] 所有新增测试用例通过 (24/24)
- [x] 遵循测试 ID 编号规范 (API-IMP-XXX, API-EXP-XXX)
- [x] 使用可复用的 fixture
- [x] 测试数据自动清理

### 6.2 UI 测试验收

- [ ] 所有新增测试用例通过 (待修复内存问题)
- [x] 使用 dialog-helper 处理对话框
- [x] 使用 cleanup 工具清理测试数据
- [x] 测试通过后自动清理数据
- [x] 测试 ID 编号规范 (IMP-XXX, EXP-XXX, TMPL-XXX, DLG-XXX)

---

## 7. 测试执行计划

### 7.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_import_export.py -v

# 3. 运行 UI 测试 (需确保内存充足)
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/import-export.spec.ts --project=firefox
```

### 7.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速、稳定，验证后端逻辑 |
| 2 | UI 集成测试 | 验证前端功能 |

---

## 8. 已知问题

### 8.1 UI 测试内存问题

| 问题 | 描述 | 影响 |
|------|------|------|
| 内存不足 | Playwright 测试进程被 SIGKILL 终止 | 部分测试无法执行 |

**缓解措施**：
1. 分批执行测试
2. 增加系统内存
3. 手动验证前端功能

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-02-16 | 初始版本 | 小栗子 🌰 |

---

**模板版本**: v1.0
**创建日期**: 2026-02-16
