# API测试开发结果报告

> **测试日期**: 2026-04-02
> **测试人**: Claude Code (Subagent COV_B)
> **测试目标**: CP 覆盖率计算 (FC-CP 模式)
> **测试文件**: `/projects/management/tracker/dev/tests/test_api/test_api_cp_coverage_fc_mode.py`

---

## 1. 测试用例执行结果

| 测试用例数 | 通过 | 失败 |
|----------|------|------|
| 10 | 8 | 2 |

### 详细结果

| 用例ID | 测试目标 | 结果 | 说明 |
|--------|----------|------|------|
| API-CP-COVERAGE-001 | TC-CP模式CP覆盖率计算 | ✅ PASS | |
| (test_cp_coverage_tc_cp_mode) | | | |
| - | TC-CP模式无关联TC | ✅ PASS | |
| - | TC-CP模式所有TC都PASS | ✅ PASS | |
| API-CP-COVERAGE-002 | FC-CP模式CP覆盖率计算(单FC) | ❌ FAIL | Bug exposed: linked=False |
| (test_cp_coverage_fc_cp_single_fc) | | | |
| API-CP-COVERAGE-003 | FC-CP模式CP覆盖率计算(多FC) | ❌ FAIL | Bug exposed: linked=False |
| (test_cp_coverage_fc_cp_multiple_fc) | | | |
| API-CP-COVERAGE-004 | FC-CP模式CP无关联FC | ✅ PASS | 正确返回 coverage=0, linked=False |
| (test_cp_coverage_fc_cp_no_fc) | | | |
| - | FC-CP模式混合场景 | ✅ PASS | 通过 (因为同时有TC连接) |
| (test_cp_coverage_fc_cp_mixed_mode) | | | |
| API-CP-COVERAGE-006 | TC-CP模式coverage_detail格式 | ✅ PASS | |
| (test_coverage_detail_format_tc_cp) | | | |
| - | coverage_detail格式-0个TC | ✅ PASS | |
| - | 项目coverage_mode设置 | ✅ PASS | |

---

## 2. 环境验证记录

| 项目 | 值 |
|------|-----|
| **DATA_DIR** | `/projects/management/tracker/dev/data` (os.path.join(base_dir, 'data')) |
| **测试框架** | pytest |
| **API 测试路径** | `/projects/management/tracker/dev/tests/test_api/` |
| **coverage_mode 是否影响覆盖率计算** | **否** (API Bug) |

---

## 3. Bug 确认

### BUG-128: get_coverpoints() API 未区分 coverage_mode

**严重性**: High

**问题描述**:
`get_coverpoints()` API 始终使用 `tc_cp_connections` 表计算 CP 覆盖率和 linked 状态，完全忽略 `coverage_mode` 设置。

**Bug 证据**:
```
[DEBUG] FC-CP mode: coverage=0.0, linked=False, expected: coverage=75.0, linked=True
[BUG CONFIRMED] API 仅检查 tc_cp_connections，不检查 fc_cp_associations
```

**影响**:
- FC-CP 模式下，CP 的 `linked` 字段错误地返回 `False`
- FC-CP 模式下，CP 的 `coverage` 始终返回 `0.0`

**问题位置**: `/projects/management/tracker/dev/app/api.py` 第 1537-1628 行

**修复建议**:
修改 `get_coverpoints()` 函数，根据项目的 `coverage_mode` 选择不同的查询逻辑

---

## 4. 测试用例详情

### 4.1 TC-CP 模式测试 (3/3 通过)

**test_cp_coverage_tc_cp_mode** - 验证 TC-CP 模式覆盖率计算
- 创建 3 个 TC (2 PASS, 1 FAIL)
- 创建 1 个 CP 并关联
- 验证覆盖率: 66.7% (2/3)
- **结果**: ✅ PASS

**test_cp_coverage_tc_cp_mode_no_tc** - 验证无关联 TC 情况
- 创建 1 个 CP，不关联任何 TC
- 验证覆盖率: 0.0, coverage_detail: "0/0"
- **结果**: ✅ PASS

**test_cp_coverage_tc_cp_mode_all_pass** - 验证全部 PASS 情况
- 创建 2 个 TC (都 PASS)
- 验证覆盖率: 100.0%
- **结果**: ✅ PASS

### 4.2 FC-CP 模式测试 (1/4 通过)

**test_cp_coverage_fc_cp_single_fc** - 验证单 FC 关联
- 创建 1 个 CP
- 创建 1 个 FC (覆盖率 75%)
- 建立 FC-CP 关联
- 验证预期: coverage=75.0, linked=True
- 验证实际: coverage=0.0, linked=False (Bug)
- **结果**: ❌ FAIL (Bug exposed)

**test_cp_coverage_fc_cp_multiple_fc** - 验证多 FC 关联
- 创建 1 个 CP
- 创建 3 个 FC (覆盖率: 100%, 50%, 75%)
- 验证预期: coverage=75.0 (均值), linked=True
- 验证实际: coverage=0.0, linked=False (Bug)
- **结果**: ❌ FAIL (Bug exposed)

**test_cp_coverage_fc_cp_no_fc** - 验证无 FC 关联
- 创建 1 个 CP，不关联任何 FC
- 验证: coverage=0.0, linked=False
- **结果**: ✅ PASS

**test_cp_coverage_fc_cp_mixed_mode** - 验证混合模式
- 创建 1 个 CP
- 同时关联 TC (PASS) 和 FC (覆盖率 80%)
- **结果**: ✅ PASS (因为同时有 TC 连接，linked=True)

### 4.3 coverage_detail 格式测试 (2/2 通过)

**test_coverage_detail_format_tc_cp** - 验证格式
- 验证 coverage_detail 格式为 "passed/total"
- **结果**: ✅ PASS

**test_coverage_detail_format_zero_tc** - 验证 0 TC 格式
- 验证 coverage_detail 为 "0/0"
- **结果**: ✅ PASS

### 4.4 项目设置验证 (1/1 通过)

**test_project_has_coverage_mode** - 验证项目设置
- 验证 FC-CP 项目设置 coverage_mode='fc_cp'
- 验证 TC-CP 项目设置 coverage_mode='tc_cp'
- **结果**: ✅ PASS

---

## 5. 结论

### 5.1 测试覆盖率

| 模式 | 覆盖率 |
|------|--------|
| TC-CP 模式 | ✅ 完整覆盖 |
| FC-CP 模式 | ⚠️ 部分覆盖 (Bug 影响) |

### 5.2 Bug 影响评估

| 影响范围 | 说明 |
|----------|------|
| **TC-CP 模式** | 无影响，所有测试通过 |
| **FC-CP 模式** | `linked` 和 `coverage` 计算错误 |

### 5.3 后续行动

1. **Bug 修复**: 需要修改 `get_coverpoints()` 函数以支持 FC-CP 模式
2. **测试增强**: 修复 Bug 后，所有测试应该通过
3. **文档更新**: Bug 已记录到 `docs/BUGLOG/tracker_BUG_RECORD.md` (BUG-128)

---

**报告生成时间**: 2026-04-02
**报告人**: Claude Code (Subagent COV_B)

---

# UI测试开发结果 (Subagent COV_C)

> **测试日期**: 2026-04-02
> **测试人**: Claude Code (Subagent COV_C)
> **测试目标**: FC-CP 模式 CP 覆盖率显示和 FC-CP 关联
> **测试文件**: `/projects/management/tracker/dev/tests/test_ui/specs/integration/fc_cp_coverage.spec.ts`

## 1. UI 测试用例执行结果

| 测试用例数 | 通过 | 失败 |
|----------|------|------|
| 13 | 8 | 5 |

### 详细结果

| 用例ID | 测试目标 | 结果 | 说明 |
|--------|----------|------|------|
| UI-CP-LINK-EXT-001 | CP Tab首次加载时已关联CP不高亮 | ✅ PASS | BUG-127 已修复 |
| UI-CP-LINK-EXT-002 | 切换到FC Tab再回CP Tab关联状态正确 | ✅ PASS | 需要显式调用 loadData() |
| UI-CP-LINK-EXT-003 | 导入FC-CP关联后立即刷新CP列表 | ✅ PASS | |
| UI-CP-COVERAGE-001 | TC-CP模式CP列表显示覆盖率 | ✅ PASS | |
| UI-COVERAGE-BADGE-001 | 覆盖率100%显示绿色 | ✅ PASS | |
| UI-COVERAGE-BADGE-002 | 覆盖率0%显示红色 | ✅ PASS | |
| UI-CP-COVERAGE-006 | CP详情页显示FC覆盖率 | ✅ PASS | |
| UI-CP-LINK-EXT-004 | 删除FC-CP关联后CP恢复高亮 | ❌ FAIL | cp_ids 数据类型问题 |
| UI-CP-COVERAGE-002 | FC-CP模式CP列表显示覆盖率 | ❌ FAIL | BUG-128 影响 |
| UI-COVERAGE-BADGE-003 | 覆盖率0-100%之间显示黄色 | ❌ FAIL | BUG-128 影响 |
| UI-CP-COVERAGE-003 | FC-CP模式覆盖率颜色-100% | ❌ FAIL | BUG-128 影响 |
| UI-CP-COVERAGE-004 | FC-CP模式覆盖率颜色-部分 | ❌ FAIL | BUG-128 影响 |

## 2. 选择器验证记录

| 选择器 | 元素 | 状态 |
|--------|------|------|
| `#loginUsername` | 登录用户名输入框 | ✅ 确认 |
| `#loginPassword` | 登录密码输入框 | ✅ 确认 |
| `button.login-btn` | 登录按钮 | ✅ 确认 |
| `#fcTab` | FC Tab 按钮 | ✅ 确认 |
| `#cpTab` | CP Tab 按钮 | ✅ 确认 |
| `.coverage-badge` | 覆盖率徽章 | ✅ 确认 |
| `span.unlinked` | 未关联标记 | ✅ 确认 |
| `tr[data-cp-id]` | CP 表格行 | ✅ 确认 |

## 3. Bug 确认

### BUG-127: CP Tab首次加载时FC-CP关联状态问题
**状态**: ✅ 已修复

`renderCP()` 依赖 `functionalCoverages` 数据。CP Tab 首次加载时 `functionalCoverages` 为空，导致所有 CP 显示为未关联。

**修复**: `loadData()` 现在在 FC-CP 模式下也会加载 FC 数据。

### BUG-128: get_coverpoints() API 未区分 coverage_mode
**状态**: ❌ 未修复

`get_coverpoints()` API 始终使用 TC 连接计算覆盖率，在 FC-CP 模式下应使用 FC 的 `coverage_pct`。

**影响测试**:
- UI-CP-COVERAGE-002: 期望 75%，实际返回 0%
- UI-CP-COVERAGE-003: 期望 100% 绿色，实际返回 0% 红色
- UI-CP-COVERAGE-004: 期望 66% 黄色，实际返回 0% 红色
- UI-COVERAGE-BADGE-003: 期望黄色，实际返回红色

### cp_ids 数据类型问题
**状态**: ❌ 部分问题

`renderCP()` 检查 `fc.cp_ids && Array.isArray(fc.cp_ids)`，期望 `cp_ids` 是数组。

但 API 通过 `GROUP_CONCAT(fca.cp_id)` 返回字符串（如 "1,2"）而非数组。

**影响测试**:
- UI-CP-LINK-EXT-004: 删除关联后 CP 未恢复高亮

## 4. 运行命令

```bash
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/integration/fc_cp_coverage.spec.ts --project=firefox
```

---

**UI测试报告生成时间**: 2026-04-02
**报告人**: Claude Code (Subagent COV_C)