# Tracker vX.X.X 测试计划

> **测试版本**: vX.X.X
> **对应规格书**: tracker_SPECS_vX.X.X.md
> **创建日期**: YYYY-MM-DD
> **状态**: 待开发
> **预估开发时间**: X 小时

---

## 1. 版本概述

### 1.1 版本目标

（简要描述本版本的主要功能和目标）

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_vX.X.X.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| #XX | 功能名称 | P1 | Xh |

---

## 2. 存放位置

> **重要**：测试计划文件应放在 `docs/PLANS/` 目录下，不要放在 `docs/REPORTS/` 目录下。

| 文档类型 | 目录 |
|----------|------|
| 测试计划 (Test Plan) | `docs/PLANS/` ← 放在这里 |
| 测试报告 (Test Report) | `docs/REPORTS/` |
| 代码审查报告 | `docs/REPORTS/` |

**示例**：`docs/PLANS/TRACKER_TEST_PLAN_v0.7.0.md`

---

## 2. API 测试计划

### 2.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── conftest.py                    # 共享 fixture（如有）
├── test_api.py                     # 基础 CRUD 测试
├── test_api_boundary.py            # 边界条件测试
├── test_api_exception.py           # 异常场景测试
├── test_api_batch.py               # 批量操作测试
├── test_api_performance.py         # 性能测试
└── test_api_{功能名}.py            # 本版本新增测试文件
```

### 2.2 新增 API 测试用例

#### 2.2.1 基础 CRUD 测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-CRUD-XXX | test_xxx | 测试功能 | 返回正确数据 | #XX |

#### 2.2.2 边界条件测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-BOUND-XXX | test_xxx | 测试边界条件 | 特殊值/极端值 | #XX |

#### 2.2.3 异常场景测试

| 测试 ID | 测试方法 | 测试目标 | 异常场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-EXCP-XXX | test_xxx | 测试异常处理 | 错误输入/资源不存在 | #XX |

#### 2.2.4 批量操作测试（如有）

| 测试 ID | 测试方法 | 测试目标 | 批量场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-BATCH-XXX | test_xxx | 测试批量操作 | 批量 CRUD | #XX |

### 2.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| client fixture | `conftest.py` | Flask test_client |
| test_project fixture | `conftest.py` | 测试项目创建/清理 |
| cleanup_tcs fixture | `conftest.py` | TC 数据自动清理 |
| cleanup_cps fixture | `conftest.py` | CP 数据自动清理 |
| TCFactory | `factories.py` | TC 测试数据生成 |
| CPFactory | `factories.py` | CP 测试数据生成 |

### 2.4 API 测试命令

```bash
# 运行本版本新增的 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_{功能名}.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 3. UI 集成测试计划

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
│   ├── smoke/                      # 冒烟测试
│   ├── integration/                 # 集成测试 ← 新增测试放这里
│   │   └── {功能名}.spec.ts        # 本版本新增测试文件
│   └── e2e/                        # 端到端测试
```

### 3.2 新增 UI 测试用例

#### 3.2.1 功能测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-XXX-001 | 测试名称 | 测试功能 | #XX | P1 |

#### 3.2.2 交互测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-XXX-002 | 测试名称 | 测试用户交互 | #XX | P1 |

#### 3.2.3 边界场景测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-XXX-003 | 测试名称 | 测试边界场景 | #XX | P2 |

### 3.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| dialogHelper | `utils/dialog-helper.ts` | 安全处理对话框 |
| cleanupTestData | `utils/cleanup.ts` | 清理测试数据 |
| testProject | `conftest.ts` | 测试项目 fixture |

### 3.4 UI 测试命令

```bash
# 运行本版本新增的 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/{功能名}.spec.ts --project=firefox

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
| 开发基础 CRUD 测试 | `test_api_{功能名}.py` | Xh | 待开始 |
| 开发边界条件测试 | `test_api_{功能名}.py` | Xh | 待开始 |
| 开发异常场景测试 | `test_api_{功能名}.py` | Xh | 待开始 |

### 4.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发功能测试 | `{功能名}.spec.ts` | Xh | 待开始 |
| 开发交互测试 | `{功能名}.spec.ts` | Xh | 待开始 |
| 开发边界场景测试 | `{功能名}.spec.ts` | Xh | 待开始 |

---

## 5. 验收标准

### 5.1 API 测试验收

- [ ] 所有新增测试用例通过
- [ ] 遵循测试 ID 编号规范
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理

### 5.2 UI 测试验收

- [ ] 所有新增测试用例通过
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
| 2 | UI 集成测试 | 验证前端功能 |

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 测试数据冲突 | 测试失败 | 使用时间戳命名，每次清理 |
| 内存不足 | UI 测试超时 | 分批执行测试 |
| 服务未启动 | 测试失败 | 检查服务状态 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | YYYY-MM-DD | 初始版本 | [姓名] |

---

**模板版本**: v1.0
**创建日期**: 2026-02-16
