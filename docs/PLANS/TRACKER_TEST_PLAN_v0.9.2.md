# Tracker v0.9.2 测试计划

> **测试版本**: v0.9.2
> **对应规格书**: `docs/SPECIFICATIONS/tracker_SPECS_v0.9.2.md`
> **创建日期**: 2026-03-14
> **状态**: 待开发
> **预估开发时间**: ~8h

---

## 1. 版本概述

### 1.1 版本目标

本版本主要实现以下功能：
- CP/TC关联状态可视化（红色+🔗图标）
- CP/TP独立滚动条支持
- CP页面"未关联"过滤选项
- admin强制改密码前端
- Manual文档更新

### 1.2 对应规格书

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.9.2.md` |

### 1.3 新增功能清单

| 功能编号 | 功能名称 | 优先级 | 预估工时 |
|----------|----------|--------|----------|
| REQ-002 | CP关联状态可视化 | P1 | 1h |
| REQ-003 | TC关联状态可视化 | P1 | 1h |
| REQ-004 | CP/TP滑动条（高度自适应屏幕） | P1 | 2.5h |
| REQ-004B | TC过滤布局与CP一致 | P1 | 0.5h |
| REQ-005 | CP未关联过滤 | P1 | 2h |
| ISSUE-017 | admin强制改密码前端 | P1 | 1h |
| REQ-001 | 更新Manual | P2 | 1h |

---

## 2. 存放位置

> **重要**：测试计划文件应放在 `docs/PLANS/` 目录下，不要放在 `docs/REPORTS/` 目录下。

| 文档类型 | 目录 |
|----------|------|
| 测试计划 (Test Plan) | `docs/PLANS/` ← 放在这里 |
| 测试报告 (Test Report) | `docs/REPORTS/` |

**本文件**: `docs/PLANS/TRACKER_TEST_PLAN_v0.9.2.md`

---

## 2. API 测试计划

### 2.1 测试框架

基于 [API 测试策略](./DEVELOPMENT/API_TESTING_STRATEGY.md)，API 测试使用 **Python pytest** 框架。

#### 测试文件位置

```
dev/tests/test_api/
├── conftest.py                    # 共享 fixture
├── test_api.py                     # 基础 CRUD 测试
├── test_api_boundary.py            # 边界条件测试
├── test_api_exception.py           # 异常场景测试
├── test_api_batch.py               # 批量操作测试
├── test_api_filter.py              # 过滤功能测试 (新增)
└── ...
```

### 2.2 新增 API 测试用例

#### 2.2.1 过滤功能测试 (REQ-005)

| 测试 ID | 测试方法 | 测试目标 | 预期结果 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-FILTER-001 | test_get_cp_with_filter_all | 获取全部CP（默认） | 返回所有CP | REQ-005 |
| API-FILTER-002 | test_get_cp_with_filter_unlinked | 获取未关联CP | 只返回linked=false的CP | REQ-005 |
| API-FILTER-003 | test_get_cp_filter_with_project | 指定项目过滤 | 按project_id过滤 | REQ-005 |

#### 2.2.2 边界条件测试

| 测试 ID | 测试方法 | 测试目标 | 边界场景 | 对应规格 |
|---------|----------|----------|----------|----------|
| API-FILTER-004 | test_get_cp_filter_invalid | 无效filter参数 | 返回错误或默认全部 | REQ-005 |

### 2.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| client fixture | `conftest.py` | Flask test_client |
| test_project fixture | `conftest.py` | 测试项目创建/清理 |
| cleanup_tcs fixture | `conftest.py` | TC 数据自动清理 |
| cleanup_cps fixture | `conftest.py` | CP 数据自动清理 |

### 2.4 API 测试命令

```bash
# 运行过滤功能测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/test_api_filter.py -v

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
│   ├── integration/                 # 集成测试
│   │   ├── cp.spec.ts              # CP功能测试
│   │   ├── tc.spec.ts              # TC功能测试
│   │   ├── link-status.spec.ts     # 关联状态可视化 (新增)
│   │   ├── filter.spec.ts          # 过滤功能测试 (新增)
│   │   └── ...
│   └── e2e/                        # 端到端测试
```

### 3.2 新增 UI 测试用例

#### 3.2.1 关联状态可视化测试 (REQ-002/003)

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-LINK-001 | test_cp_unlinked_display | 未关联CP显示红色+图标 | REQ-002 | P1 |
| UI-LINK-002 | test_tc_unlinked_display | 未关联TC显示红色+图标 | REQ-003 | P1 |
| UI-LINK-003 | test_linked_cp_normal | 关联CP正常显示 | REQ-002 | P1 |
| UI-LINK-004 | test_linked_tc_normal | 关联TC正常显示 | REQ-003 | P1 |
| UI-LINK-005 | test_link_status_refresh | 刷新后状态保持 | REQ-002/003 | P2 |

#### 3.2.2 滑动条 + 屏幕自适应测试 (REQ-004)

> **⚠️ 需求更新 (2026-03-16)**: 高度改为自适应屏幕尺寸（calc + vh + min + max），替代原来的固定 400px。

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-SCROLL-001 | test_cp_list_scroll | CP列表独立滚动 | REQ-004 | P1 |
| UI-SCROLL-002 | test_tp_list_scroll | TP列表独立滚动 | REQ-004 | P1 |
| UI-SCROLL-003 | test_header_sticky | 滚动时表头固定在容器顶部 | REQ-004 | P1 |
| UI-SCROLL-004 | test_table_height_adaptive | 表格高度随屏幕自适应 (calc+vh) | REQ-004 | P1 |
| UI-SCROLL-005 | test_scroll_works_on_large_screen | 大屏下滚动功能正常 | REQ-004 | P1 |
| UI-SCROLL-006 | test_min_height_limited | 小屏下最小高度限制(300px) | REQ-004 | P2 |
| UI-SCROLL-007 | test_max_height_limited | 大屏下最大高度限制(600px) | REQ-004 | P2 |

> **测试说明**:
> - UI-SCROLL-004: 验证 CSS `max-height: calc(100vh - 280px)` 生效
> - UI-SCROLL-005: 验证外接大屏下滚动条正常出现
> - UI-SCROLL-006/007: 通过设置不同 viewport 尺寸验证 min/max 限制

#### 3.2.3 TC过滤布局测试 (REQ-004B)

> **新增 (2026-03-16)**: 测试 TC 过滤布局与 CP 一致（单行显示）。

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FILTER-LAYOUT-001 | test_tc_filter_single_row | TC过滤选项在一行显示 | REQ-004B | P1 |
| UI-FILTER-LAYOUT-002 | test_tc_filter_all_work | 所有过滤下拉正常工作 | REQ-004B | P1 |
| UI-FILTER-LAYOUT-003 | test_tc_filter_reset_works | 重置按钮功能正常 | REQ-004B | P1 |
| UI-FILTER-LAYOUT-004 | test_tc_filter_count_display | 过滤器计数显示正常 | REQ-004B | P1 |

> **测试说明**:
> - UI-FILTER-LAYOUT-001: 验证 TC 过滤下拉都在一行，无换行
> - UI-FILTER-LAYOUT-002: 验证 Status/DV Milestone/Owner/Category 过滤都正常工作
> - UI-FILTER-LAYOUT-003: 验证重置按钮可清除所有过滤条件
> - UI-FILTER-LAYOUT-004: 验证 "显示 X/Y 条" 计数正常

#### 3.2.4 过滤功能测试 (REQ-005)

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-FILTER-001 | test_cp_filter_unlinked | CP过滤"未关联"选项 | REQ-005 | P1 |
| UI-FILTER-002 | test_cp_filter_show_unlinked | 过滤显示未关联CP | REQ-005 | P1 |
| UI-FILTER-003 | test_cp_filter_clear | 清除过滤恢复正常 | REQ-005 | P1 |

#### 3.2.5 强制改密码测试 (ISSUE-017)

| 测试 ID | 测试名称 | 测试目标 | 对应规格 | 优先级 |
|---------|----------|----------|----------|--------|
| UI-PWD-001 | test_admin_first_login_force_change | admin首次登录强制改密码 | ISSUE-017 | P1 |
| UI-PWD-002 | test_change_password_success | 修改密码成功 | ISSUE-017 | P1 |
| UI-PWD-003 | test_admin_normal_login | admin再次登录不强制 | ISSUE-017 | P1 |
| UI-PWD-004 | test_normal_user_login | 普通用户登录不受影响 | ISSUE-017 | P1 |

### 3.3 可复用的测试组件

| 组件 | 路径 | 用途 |
|------|------|------|
| dialogHelper | `utils/dialog-helper.ts` | 安全处理对话框 |
| cleanupTestData | `utils/cleanup.ts` | 清理测试数据 |
| testProject | `conftest.ts` | 测试项目 fixture |

### 3.4 UI 测试命令

```bash
# 运行关联状态可视化测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/link-status.spec.ts --project=firefox

# 运行过滤功能测试
npx playwright test tests/test_ui/specs/integration/filter.spec.ts --project=firefox

# 运行强制改密码测试
npx playwright test tests/test_ui/specs/integration/password.spec.ts --project=firefox

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
| 开发过滤功能测试 | `test_api_filter.py` | 1h | 待开始 |

### 4.2 UI 测试开发

| 任务 | 测试文件 | 预估工时 | 状态 |
|------|----------|----------|------|
| 开发关联状态可视化测试 | `link-status.spec.ts` | 2h | 待开始 |
| 开发滑动条测试 | `scroll.spec.ts` | 1h | 待开始 |
| 开发过滤功能测试 | `filter.spec.ts` | 1h | 待开始 |
| 开发强制改密码测试 | `password.spec.ts` | 1h | 待开始 |
| 开发冒烟回归测试 | `smoke/*.spec.ts` | 1h | 待开始 |

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
- [ ] 冒烟测试全部通过

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
| 3 | 冒烟测试 | 回归验证 |

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 关联状态计算性能 | 测试超时 | 大数据量测试可跳过 |
| 浏览器兼容性 | UI测试失败 | 限定Firefox/Chrome |
| 测试数据冲突 | 测试失败 | 使用时间戳命名，每次清理 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-14 | 初始版本 | OpenClaw |
| 1.1 | 2026-03-16 | 更新 REQ-004 测试用例：合并屏幕自适应测试，替代原固定 400px 测试 | OpenClaw |
| 1.2 | 2026-03-16 | 新增 REQ-004B：TC过滤布局与CP一致测试用例 | OpenClaw |

---

**文档创建时间**: 2026-03-14
**最后更新**: 2026-03-16
**创建人**: OpenClaw
