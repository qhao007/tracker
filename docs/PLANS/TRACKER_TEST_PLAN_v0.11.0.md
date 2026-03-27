# Tracker v0.11.0 测试计划

> **测试版本**: v0.11.0
> **对应规格书**: tracker_SPECS_v0.11.0.md
> **创建日期**: 2026-03-27
> **状态**: 待开发
> **预估开发时间**: 3 小时

---

## 1. 版本概述

### 1.1 版本目标

本次版本新增 Functional Coverage (FC) 管理功能，包括：
- FC 表与 API
- FC-CP 关联表与 API
- 项目 coverage_mode 字段
- FC Tab 前端页面
- FC CSV 导入/导出
- 导入重名检查改进

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.11.0.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| #1 | FC 表结构与 API | P1 | 4h |
| #2 | FC-CP 关联表与 API | P1 | 2h |
| #3 | 项目 coverage_mode | P1 | 1h |
| #4 | FC Tab 前端页面 | P1 | 6h |
| #5 | FC CSV 导入/导出 | P1 | 2h |
| #6 | FC-CP 关联导入 | P1 | 1h |
| #7 | 导入重名检查改进 | P1 | 1h |
| #8 | 数据库迁移脚本 | P1 | 2h |

---

## 2. API 测试计划

### 2.1 测试框架

基于 `docs/DEVELOPMENT/API_TESTING_STRATEGY.md`，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── test_api_fc.py                    # FC 基础 CRUD 测试
├── test_api_fc_import.py             # FC 导入测试
├── test_api_fc_export.py             # FC 导出测试
├── test_api_fc_cp_association.py     # FC-CP 关联测试
└── test_api_project_mode.py         # coverage_mode 测试
```

### 2.2 新增 API 测试用例

#### 2.2.1 FC 基础 CRUD 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-FC-001 | test_get_fc_list | 获取 FC 列表 | 返回 FC 列表 | #1 |
| API-FC-002 | test_get_fc_list_with_filter | 筛选 FC | 返回筛选后列表 | #1 |
| API-FC-003 | test_fc_import_success | 成功导入 FC | 数据正确导入 | #5 |
| API-FC-004 | test_fc_import_conflict | 导入重复 FC | Skip + 报告 | #7 |
| API-FC-005 | test_fc_export | 导出 FC | 生成 CSV 文件 | #5 |

#### 2.2.2 FC-CP 关联测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-FC-CP-001 | test_get_fc_cp_associations | 获取关联列表 | 返回关联列表 | #2 |
| API-FC-CP-002 | test_create_fc_cp_association | 创建关联 | 关联创建成功 | #2 |
| API-FC-CP-003 | test_delete_fc_cp_association | 删除关联 | 关联删除成功 | #2 |
| API-FC-CP-004 | test_import_fc_cp_association | 导入关联 CSV | 关联批量创建 | #6 |

#### 2.2.3 coverage_mode 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-PROJ-001 | test_create_project_with_mode | 创建项目带 mode | 项目创建成功 | #3 |
| API-PROJ-002 | test_get_project_returns_mode | 获取项目返回 mode | mode 正确返回 | #3 |
| API-PROJ-003 | test_project_default_tc_cp | 新建项目默认 tc_cp | 默认值正确 | #3 |

#### 2.2.4 边界条件测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-BOUND-001 | test_fc_import_empty_csv | 空 CSV | 返回错误 | #5 |
| API-BOUND-002 | test_fc_import_invalid_format | 格式错误 | 返回错误 | #5 |
| API-BOUND-003 | test_fc_import_missing_required | 缺少必填字段 | 返回错误 | #5 |
| API-BOUND-004 | test_fc_unique_constraint | 唯一性约束 | 冲突时 Skip | #7 |

#### 2.2.5 导入重名检查测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-DUP-001 | test_cp_import_duplicate | CP 导入重名 | 拒绝导入 | #7 |
| API-DUP-002 | test_tc_import_duplicate | TC 导入重名 | 拒绝导入 | #7 |
| API-DUP-003 | test_cp_import_same_feature_different_sub | 同 feature 不同 sub | 允许导入 | #7 |

### 2.3 API 测试命令

```bash
# 运行本版本新增的 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_fc.py -v
PYTHONPATH=. pytest tests/test_api/test_api_fc_import.py -v
PYTHONPATH=. pytest tests/test_api/test_api_fc_cp_association.py -v
PYTHONPATH=. pytest tests/test_api/test_api_project_mode.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 3. UI 集成测试计划

### 3.1 测试框架

基于 `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md`，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/specs/integration/
├── 15-fc-tab.spec.ts                # FC Tab 测试
├── 16-fc-import-export.spec.ts      # FC 导入导出测试
├── 17-fc-collapse.spec.ts           # FC 折叠展开测试
└── 18-fc-filter.spec.ts            # FC 筛选测试
```

### 3.2 新增 UI 测试用例

#### 3.2.1 FC Tab 测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FC-001 | FC Tab 仅在 FC-CP 模式显示 | 验证 Tab 显示逻辑 | #4 | P1 |
| UI-FC-002 | FC Tab 在 TC-CP 模式不显示 | 验证 Tab 隐藏逻辑 | #4 | P1 |

#### 3.2.2 FC 折叠/展开测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FC-COLLAPSE-001 | 默认全部折叠 | 验证默认折叠状态 | #4 | P1 |
| UI-FC-COLLAPSE-002 | 展开/折叠 covergroup | 验证第一级交互 | #4 | P1 |
| UI-FC-COLLAPSE-003 | 展开/折叠 coverpoint | 验证第二级交互 | #4 | P1 |
| UI-FC-COLLAPSE-004 | 全部展开按钮 | 验证快捷操作 | #4 | P1 |
| UI-FC-COLLAPSE-005 | 全部折叠按钮 | 验证快捷操作 | #4 | P1 |
| UI-FC-COLLAPSE-006 | localStorage 记忆 | 验证状态保持 | #4 | P2 |

#### 3.2.3 FC 筛选测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FC-FILTER-001 | 筛选 covergroup | 验证筛选功能 | #4 | P1 |
| UI-FC-FILTER-002 | 筛选 coverpoint | 验证筛选功能 | #4 | P1 |
| UI-FC-FILTER-003 | 筛选 coverage_type | 验证筛选功能 | #4 | P1 |
| UI-FC-FILTER-004 | 多条件 AND 筛选 | 验证组合筛选 | #4 | P1 |
| UI-FC-FILTER-005 | 清除筛选 | 验证清除功能 | #4 | P1 |

#### 3.2.4 FC 搜索测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FC-SEARCH-001 | bin_name 模糊搜索 | 验证搜索功能 | #4 | P1 |
| UI-FC-SEARCH-002 | 搜索结果高亮 | 验证高亮显示 | #4 | P2 |

#### 3.2.5 FC 导入导出测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FC-IMPORT-001 | 导入 CSV 文件 | 验证导入功能 | #5 | P1 |
| UI-FC-IMPORT-002 | 导入预览 | 验证预览功能 | #5 | P2 |
| UI-FC-IMPORT-003 | 导入成功提示 | 验证结果提示 | #5 | P1 |
| UI-FC-EXPORT-001 | 导出 CSV 格式 | 验证导出功能 | #5 | P1 |
| UI-FC-EXPORT-002 | 导出 Excel 格式 | 验证多格式导出 | #5 | P2 |

#### 3.2.6 FC-CP 关联测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FC-CP-001 | CP 详情页显示关联 FC | 验证关联显示 | #2 | P1 |
| UI-FC-CP-002 | FC-CP 关联导入 | 验证关联导入 | #6 | P1 |

### 3.3 UI 测试命令

```bash
# 运行本版本新增的 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/15-fc-tab.spec.ts --project=firefox
npx playwright test tests/test_ui/specs/integration/16-fc-import-export.spec.ts --project=firefox
npx playwright test tests/test_ui/specs/integration/17-fc-collapse.spec.ts --project=firefox
npx playwright test tests/test_ui/specs/integration/18-fc-filter.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 4. 测试开发任务分解

### 4.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| FC 基础 CRUD + 导入导出测试 | `test_api_fc.py` | 1h | 待开始 |
| FC-CP 关联测试 | `test_api_fc_cp_association.py` | 0.5h | 待开始 |
| coverage_mode 测试 | `test_api_project_mode.py` | 0.5h | 待开始 |
| 导入重名检查测试 | `test_api_fc_import.py` | 0.5h | 待开始 |

### 4.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| FC Tab 显示测试 | `15-fc-tab.spec.ts` | 0.5h | 待开始 |
| FC 折叠展开测试 | `17-fc-collapse.spec.ts` | 1h | 待开始 |
| FC 筛选测试 | `18-fc-filter.spec.ts` | 0.5h | 待开始 |
| FC 导入导出测试 | `16-fc-import-export.spec.ts` | 0.5h | 待开始 |

---

## 5. 验收标准

### 5.1 API 测试验收

- [ ] 所有新增 API 测试用例通过
- [ ] 遵循测试 ID 编号规范 (API-FC-*, API-FC-CP-*, etc.)
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理

### 5.2 UI 测试验收

- [ ] 所有新增 UI 测试用例通过
- [ ] 使用 dialog-helper 处理对话框
- [ ] 使用 cleanup 工具清理测试数据
- [ ] 测试通过后自动清理数据

---

## 6. 测试执行计划

### 6.1 本地测试

```bash
# 1. 启动测试服务
cd /projects/management/tracker/dev && bash start_server_test.sh

# 2. 运行 API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v

# 3. 运行 UI 测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/ --project=firefox
```

### 6.2 测试执行顺序

| 顺序 | 测试类型 | 原因 |
|------|----------|------|
| 1 | API 测试 | 快速、稳定，验证后端逻辑 |
| 2 | UI 冒烟测试 | 验证核心功能 |
| 3 | UI 集成测试 | 验证完整流程 |

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| FC 数据量大导致渲染慢 | 中 | 使用折叠减少渲染量 |
| CSV 格式不标准导致导入失败 | 中 | 完善校验和错误提示 |
| 测试环境数据冲突 | 低 | 使用时间戳命名，自动清理 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-27 | 初始版本 | OpenClaw |

---

**模板版本**: v1.0
**创建日期**: 2026-03-27
