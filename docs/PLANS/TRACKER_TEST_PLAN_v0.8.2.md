# Tracker v0.8.2 测试计划

> **测试版本**: v0.8.2
> **对应规格书**: `docs/SPECIFICATIONS/tracker_SPECS_v0.8.2.md`
> **创建日期**: 2026-03-02
> **状态**: 待开发
> **预估开发时间**: 2 小时

---

## 1. 版本概述

### 1.1 版本目标

v0.8.2 是进度图表功能的第三个版本，主要目标：
1. 实现 CP 覆盖率实际曲线显示
2. 添加手动/定时快照采集
3. 添加快照管理功能
4. 支持导出进度数据

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.8.2.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-082-001 | 实际曲线显示 | P1 | 4h |
| REQ-082-002 | 快照数据采集 | P1 | 3h |
| REQ-082-003 | 快照管理 | P1 | 2h |
| REQ-082-004 | 导出进度数据 | P2 | 1h |

---

## 2. 存放位置

> **重要**：测试计划文件应放在 `docs/PLANS/` 目录下，不要放在 `docs/REPORTS/` 目录下。

**文件路径**: `docs/PLANS/TRACKER_TEST_PLAN_v0.8.2.md`

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
└── test_api_actual_curve.py     # v0.8.2 新增：实际曲线 API
```

### 3.2 新增 API 测试用例

#### 3.2.1 实际曲线数据获取测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-ACT-001 | test_get_progress_with_actual | 获取含实际曲线数据 | 返回 actual 数组 | REQ-082-001 |
| API-ACT-002 | test_get_progress_actual_empty | 无快照时返回空数组 | actual=[] | REQ-082-001 |

#### 3.2.2 快照采集测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-ACT-010 | test_create_snapshot | 手动创建快照 | 快照创建成功 | REQ-082-002 |
| API-ACT-011 | test_create_snapshot_calculates | 快照计算正确覆盖率 | coverage 正确 | REQ-082-002 |
| API-ACT-012 | test_cron_snapshot_requires_token | 定时任务需 Token | 无 Token 返回 401 | REQ-082-002 |
| API-ACT-013 | test_cron_snapshot_with_token | 正确 Token 可执行 | 返回成功 | REQ-082-002 |

#### 3.2.3 快照管理测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-ACT-020 | test_get_snapshots | 获取快照列表 | 返回列表 | REQ-082-003 |
| API-ACT-021 | test_delete_snapshot_admin | admin 可删除快照 | 删除成功 | REQ-082-003 |
| API-ACT-022 | test_delete_snapshot_user | user 不可删除 | 返回 403 | REQ-082-003 |
| API-ACT-023 | test_delete_current_week_warns | 删除当周快照有提示 | 返回警告 | REQ-082-003 |

#### 3.2.4 导出功能测试

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-ACT-030 | test_export_progress | 导出进度数据 | 返回 CSV/JSON | REQ-082-004 |

### 3.3 测试命令

```bash
# 运行新增的实际曲线 API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_actual_curve.py -v

# 运行所有 API 测试
PYTHONPATH=. pytest tests/test_api/ -v
```

---

## 4. UI 测试计划

### 4.1 测试框架

基于 [UI 测试策略](./DEVELOPMENT/UI_TESTING_STRATEGY.md)，UI 测试使用 **Playwright (TypeScript)** 框架。

#### 测试文件位置

```
dev/tests/test_ui/
├── conftest.ts                     # Playwright 配置
├── utils/
│   ├── dialog-helper.ts           # Dialog 处理工具
│   └── cleanup.ts                 # 测试数据清理工具
└── specs/
    └── integration/
        ├── progress_charts.spec.ts    # v0.8.0
        ├── planned_curve.spec.ts       # v0.8.1
        └── actual_curve.spec.ts      # v0.8.2 新增
```

### 4.2 新增 UI 测试用例

#### 4.2.1 实际曲线渲染测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-ACT-001 | 实际曲线显示 | 图表显示实际曲线 | REQ-082-001 | P1 |
| UI-ACT-002 | 曲线颜色 | 实际曲线为绿色 | REQ-082-001 | P1 |
| UI-ACT-003 | 双曲线同时显示 | 计划+实际曲线 | REQ-082-001 | P1 |

#### 4.2.2 快照采集测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-ACT-010 | 刷新快照按钮 | 按钮可见（admin） | REQ-082-002 | P1 |
| UI-ACT-011 | 点击创建快照 | 点击后生成快照 | REQ-082-002 | P1 |
| UI-ACT-012 | user 看不到按钮 | user 无按钮 | REQ-082-002 | P2 |

#### 4.2.3 快照管理测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-ACT-020 | 快照管理入口 | 按钮可见（admin） | REQ-082-003 | P1 |
| UI-ACT-021 | 快照列表显示 | 显示历史快照 | REQ-082-003 | P1 |
| UI-ACT-022 | 删除快照 | admin 可删除 | REQ-082-003 | P1 |
| UI-ACT-023 | user 只读 | user 不可删除 | REQ-082-003 | P2 |

#### 4.2.4 导出功能测试

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-ACT-030 | 导出按钮 | 按钮可见 | REQ-082-004 | P2 |

### 4.3 测试命令

```bash
# 运行新增的实际曲线 UI 测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/actual_curve.spec.ts --project=firefox

# 运行所有集成测试
npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 5. 测试开发任务分解

### 5.1 API 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 实际曲线数据获取测试 | `test_api_actual_curve.py` | 0.5h | 待开始 |
| 快照采集测试 | `test_api_actual_curve.py` | 1h | 待开始 |
| 快照管理测试 | `test_api_actual_curve.py` | 0.5h | 待开始 |
| 导出功能测试 | `test_api_actual_curve.py` | 0.5h | 待开始 |

### 5.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 实际曲线渲染测试 | `actual_curve.spec.ts` | 0.5h | 待开始 |
| 快照采集测试 | `actual_curve.spec.ts` | 0.5h | 待开始 |
| 快照管理测试 | `actual_curve.spec.ts` | 0.5h | 待开始 |
| 导出功能测试 | `actual_curve.spec.ts` | 0.25h | 待开始 |

---

## 6. 验收标准

### 6.1 API 测试验收

- [ ] 所有新增 API 测试用例通过
- [ ] 遵循测试 ID 编号规范 (API-ACT-xxx)
- [ ] 使用可复用的 fixture
- [ ] 测试数据自动清理

### 6.2 UI 测试验收

- [ ] 所有新增 UI 测试用例通过
- [ ] 遵循测试 ID 编号规范 (UI-ACT-xxx)
- [ ] 使用 dialog-helper 处理对话框
- [ ] 使用 cleanup 工具清理测试数据

---

## 7. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-02 | 初始版本 | 小栗子 🌰 |

---

**模板版本**: v1.0
**创建日期**: 2026-03-02
