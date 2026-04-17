# Tracker v0.13.0 补充规格书：Dashboard FC-CP 模式支持

> **版本**: v0.13.0
> **创建日期**: 2026-04-15
> **状态**: 待评审
> **类型**: 补充规格书（是对 v0.13.0 Wiki 集成规格书的扩展）
> **关联主规格书**: `tracker_SPECS_v0.13.0.md`

---

## 1. 概述

### 1.1 问题描述

Tracker Dashboard 目前存在一个严重缺陷：**仅支持 TC-CP 模式项目的展示，不支持 FC-CP 模式项目**。

| 项目模式 | 说明 | Dashboard 支持状态 |
|----------|------|-------------------|
| TC-CP | 测试用例 (TC) 关联覆盖点 (CP) | ✅ 完整支持 |
| FC-CP | 功能覆盖点 (FC) 关联覆盖点 (CP) | ❌ 仅 Coverage Holes 支持，其他 3 个 Tab 不支持 |

### 1.2 影响范围

以下 Dashboard API 端点需要修改以支持 FC-CP 模式：

| Dashboard Tab | API Endpoint | 当前状态 | 需要修改 |
|--------------|--------------|----------|----------|
| Overview | `/api/dashboard/stats` | ❌ 不支持 FC-CP | ✅ 需要 |
| Coverage Holes | `/api/dashboard/coverage-holes` | ✅ 已支持 | ❌ 无需 |
| Owner Distribution | `/api/dashboard/owner-stats` | ✅ 无需修改 | ❌ 无需 - Owner 始终从 test_case 表获取 |
| Coverage Matrix | `/api/dashboard/coverage-matrix` | ❌ 不支持 FC-CP | ✅ 需要 |

**同时，快照系统也需要支持 FC-CP 模式**，见节 2.5 和节 3.6。

### 1.3 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | Dashboard API 增加 FC-CP 模式检测 | P0 | 1h |
| 2 | `/api/dashboard/stats` 支持 FC-CP 模式 | P0 | 2h |
| 3 | `/api/dashboard/coverage-matrix` 支持 FC-CP 模式 | P0 | 3h |
| 4 | 前端 Dashboard 根据模式切换数据展示 | P0 | 2h |
| 5 | 快照系统支持 FC-CP 模式 | P0 | 3h |
| 6 | week_change 计算修复（FC-CP 模式） | P0 | 1h |
| 7 | 新增 FC-CP 模式测试数据 | P1 | 1h |
| 8 | API 测试增强 | P0 | 2h |
| 9 | UI 集成测试 | P1 | 2h |
| | **总计** | | **~17h** |

### 1.4 背景

Tracker 项目有两种覆盖率关联模式：

**TC-CP 模式**（传统模式）：
- `test_case` (TC) → `tc_cp_connection` → `cover_point` (CP)
- TC 是验证的基本单元

**FC-CP 模式**（功能覆盖模式）：
- `functional_coverage` (FC) → `fc_cp_connection` → `cover_point` (CP)
- FC 是功能覆盖点，比 TC 更抽象

Dashboard 的 4 个 Tab 需要正确识别项目模式并使用对应的数据表进行统计。

---

## 2. 数据模型分析

### 2.1 项目模式定义

项目创建时指定 `coverage_mode` 字段：

```json
{
  "id": 1,
  "name": "SOC_DV",
  "coverage_mode": "tc_cp"  // 或 "fc_cp"
}
```

### 2.2 TC-CP 模式数据流

```
test_case (TC)
    ↓ (tc_cp_connection)
cover_point (CP)
```

**相关表结构**：
- `test_case`: TC 信息
- `cover_point`: CP 信息
- `tc_cp_connection`: TC-CP 关联

### 2.3 FC-CP 模式数据流

```
functional_coverage (FC)
    ↓ (fc_cp_connection)
cover_point (CP)
```

**相关表结构**：
- `functional_coverage`: FC 信息（name, description, owner 等）
- `cover_point`: CP 信息
- `fc_cp_connection`: FC-CP 关联

### 2.4 `covered_cp` / `cp_covered` 语义定义

> **重要**：语义必须在 TC-CP 和 FC-CP 两种模式下保持一致。

| 字段 | TC-CP 语义 | FC-CP 语义 |
|------|-----------|-----------|
| `covered_cp` | 有 **PASS TC** 关联的 CP 数量 | 有 **coverage_pct > 0 的 FC** 关联的 CP 数量 |
| `unlinked_cp` | 总 CP - `covered_cp` | 总 CP - `covered_cp`（相同计算逻辑） |
| `total_cp` | 总 CP 数量 | 总 CP 数量（不变） |

**关键区别**：
- TC-CP：`covered_cp` 需要 PASS TC 才算 "covered"
- FC-CP：`covered_cp` 只要有关联 FC 且 `coverage_pct > 0` 即算 "covered"（FC 没有 pass/fail 状态）

### 2.5 快照系统改造需求

**当前问题**：
- `calculate_current_coverage()` 函数（api.py:1271-1436）只支持 TC-CP 逻辑
- 快照表 `project_progress` 中的 `cp_covered` 字段存储的是 TC-CP 语义
- FC-CP 项目保存快照时，`cp_covered` 数据无意义

**改造目标**：
- `calculate_current_coverage()` 根据 `coverage_mode` 计算正确的 `cp_covered`
- 快照保存时正确存储 FC-CP 语义
- `week_change` 计算能够跨模式工作

---

## 3. API 需求详情

### 3.1 通用修改：增加 `coverage_mode` 检测

**需求编号**: REQ-D001

**需求描述**:
在所有 Dashboard API 中，增加 `coverage_mode` 检测逻辑。

**实现模式检查**（参考 `get_dashboard_coverage_holes` 正确实现）：

```python
# 获取项目的 coverage_mode
coverage_mode = project.get('coverage_mode', 'tc_cp')
is_fc_cp_mode = coverage_mode == 'fc_cp'
```

**验收标准**:
- [ ] 所有 Dashboard API 正确读取 `coverage_mode`
- [ ] 根据模式选择使用 `tc_cp_connection` 或 `fc_cp_connection`

---

### 3.2 功能需求 #2：`/api/dashboard/stats` 支持 FC-CP

**需求编号**: REQ-D002

**当前问题**：
- `get_dashboard_stats()` (line ~4810) 只查询 `tc_cp_connections` 表
- 对 FC-CP 模式项目返回无意义的统计数据
- 当前 FC-CP 模式的 `covered_cp` 计算错误（使用 `covered_fcs` 而非正确的 CP 计数）

**修改要求**：

#### 3.2.1 FC-CP 模式 `covered_cp` 正确计算

```python
# api.py: get_dashboard_stats() 中的 FC-CP 模式部分

if is_fc_cp_mode:
    # 获取总 CP 数
    cursor.execute("SELECT COUNT(*) FROM cover_point WHERE project_id = ?", (project_id,))
    total_cp = cursor.fetchone()[0] or 0

    # FC-CP 模式: covered_cp = 有 coverage_pct > 0 的 FC 关联的 CP
    # 遍历每个 CP，检查是否有 coverage_pct > 0 的 FC 关联
    covered_cp = 0
    for cp_row in all_cps:  # all_cps 在下面查询
        cp_id = cp_row[0]
        cursor.execute("""
            SELECT fc.coverage_pct
            FROM functional_coverage fc
            INNER JOIN fc_cp_association fcca ON fc.id = fcca.fc_id
            WHERE fcca.cp_id = ?
        """, (cp_id,))
        linked_fcs = cursor.fetchall()
        if linked_fcs:
            avg_coverage = sum(fc[0] for fc in linked_fcs) / len(linked_fcs)
            if avg_coverage > 0:
                covered_cp += 1

    # unlinked_cp: 无有效 FC 关联的 CP
    unlinked_cp = total_cp - covered_cp
```

#### 3.2.2 API 响应格式

```json
{
  "mode": "fc_cp",
  "overview": {
    "total_cp": 30,
    "covered_cp": 20,
    "coverage_rate": 66.7,
    "unlinked_cp": 10,
    "tc_total": 0,
    "tc_pass": 0,
    "tc_pass_rate": 0,
    "week_change": {
      "covered_cp": null,
      "unlinked_cp": null,
      "tc_pass_rate": null
    }
  }
}
```

**验收标准**:
- [ ] FC-CP 模式项目 `covered_cp` = 有 `coverage_pct > 0` FC 关联的 CP
- [ ] FC-CP 模式项目 `unlinked_cp` = 总 CP - `covered_cp`
- [ ] 响应包含 `mode` 字段指示当前模式
- [ ] TC-CP 模式项目行为保持不变

---

### 3.3 功能需求 #3：`/api/dashboard/coverage-matrix` 支持 FC-CP

**需求编号**: REQ-D003

**当前问题**：
- `get_dashboard_coverage_matrix()` (line ~5394) 只使用 TC-CP 连接
- 对 FC-CP 模式项目，Coverage Matrix 展示错误的关联关系

**修改要求**：
- 与 `get_dashboard_stats()` 类似的 FC-CP 模式检测
- 使用 `fc_cp_association` 构建 FC-CP 矩阵

**验收标准**:
- [ ] FC-CP 模式显示 FC-CP Coverage Matrix
- [ ] TC-CP 模式行为保持不变
- [ ] 响应包含 `mode` 字段

---

### 3.4 功能需求 #4：前端 Dashboard 模式感知

**需求编号**: REQ-D004

**需求描述**:
Dashboard 的 4 个 Tab 需要根据当前项目的 `coverage_mode` 正确展示数据。

**注意**：前端展示标签保持一致（CP Covered、Unlinked、TC Pass Rate），只调整计算逻辑。

**验收标准**:
- [ ] Dashboard Overview Tab 根据模式显示正确数据
- [ ] Owner Distribution Tab 不变（始终显示 TC Owner）
- [ ] Coverage Matrix Tab 显示正确的矩阵
- [ ] 项目切换时 Dashboard 正确刷新

---

### 3.5 功能需求 #5：快照系统支持 FC-CP 模式

**需求编号**: REQ-D005

**需求描述**:
改造 `calculate_current_coverage()` 函数，使其支持 FC-CP 模式计算。

**修改位置**：
- `api.py:1271-1436` - `calculate_current_coverage()` 函数

**修改要求**：

```python
def calculate_current_coverage(project_name, coverage_mode='tc_cp'):
    """
    计算当前覆盖率（用于快照）
    v0.13.0: 支持 FC-CP 模式

    Args:
        project_name: 项目名称
        coverage_mode: 'tc_cp' 或 'fc_cp'
    """
    is_fc_cp_mode = coverage_mode == 'fc_cp'

    # 获取总 CP 数（两种模式相同）
    cursor.execute("SELECT COUNT(*) FROM cover_point")
    total_cp = cursor.fetchone()[0]

    if is_fc_cp_mode:
        # FC-CP 模式: covered_cp = 有 coverage_pct > 0 的 FC 关联的 CP
        covered_cp = 0
        for cp_row in all_cps:
            cp_id = cp_row[0]
            cursor.execute("""
                SELECT fc.coverage_pct
                FROM functional_coverage fc
                INNER JOIN fc_cp_association fcca ON fc.id = fcca.fc_id
                WHERE fcca.cp_id = ?
            """, (cp_id,))
            linked_fcs = cursor.fetchall()
            if linked_fcs:
                avg_coverage = sum(fc[0] for fc in linked_fcs) / len(linked_fcs)
                if avg_coverage > 0:
                    covered_cp += 1

        # FC-CP 模式不计算 TC 统计
        tc_pass = 0
        tc_total = 0
    else:
        # TC-CP 模式: 使用原有逻辑
        # covered_cp = 有 PASS TC 关联的 CP
        ...

    return {
        'cp_covered': covered_cp,
        'cp_total': total_cp,
        'tc_pass_count': tc_pass,
        'tc_total': tc_total,
        ...
    }
```

**验收标准**:
- [ ] `calculate_current_coverage()` 正确处理 FC-CP 模式
- [ ] FC-CP 项目的快照 `cp_covered` 数据准确
- [ ] TC-CP 项目行为保持不变

---

### 3.6 功能需求 #6：week_change 计算修复（FC-CP 模式）

**需求编号**: REQ-D006

**需求描述**:
修复 FC-CP 模式下 `week_change` 的计算。

**当前问题**：
- FC-CP 模式下 `week_change` 所有字段返回 `None`
- 因为 `covered_cp` 计算错误 + `tc_pass_rate` 始终为 0

**修改要求**：

```python
# api.py: get_dashboard_stats() 中的 week_change 计算部分

week_change = {
    'covered_cp': None,
    'unlinked_cp': None,
    'tc_pass_rate': None
}

if latest_snapshot:
    snapshot_cp_covered = latest_snapshot[2] or 0  # 快照中的 cp_covered
    snapshot_tc_total = latest_snapshot[5] if latest_snapshot[5] > 0 else 1
    snapshot_tc_pass_rate = round((latest_snapshot[4] / snapshot_tc_total) * 100, 1)

    # FC-CP 模式: 使用正确的 covered_cp 和 unlinked_cp 计算
    if is_fc_cp_mode:
        week_change['covered_cp'] = covered_cp - snapshot_cp_covered
        week_change['unlinked_cp'] = unlinked_cp - (total_cp - snapshot_cp_covered)
        # FC-CP 模式下 tc_pass_rate 可以计算（TC 数据仍然存在）
        week_change['tc_pass_rate'] = round(tc_pass_rate - snapshot_tc_pass_rate, 1)
    else:
        # TC-CP 模式: 现有逻辑
        week_change['covered_cp'] = covered_cp - snapshot_cp_covered
        week_change['unlinked_cp'] = unlinked_cp - (total_cp - snapshot_cp_covered)
        week_change['tc_pass_rate'] = round(tc_pass_rate - snapshot_tc_pass_rate, 1)
```

**注意**：
- FC-CP 模式下，如果快照是在 TC-CP 模式下创建的，week_change 可能不准确
- 这是已知的语义不一致问题，需要在切换模式后重新创建快照

**验收标准**:
- [ ] FC-CP 模式下 `week_change.covered_cp` 正确计算
- [ ] FC-CP 模式下 `week_change.unlinked_cp` 正确计算
- [ ] FC-CP 模式下 `week_change.tc_pass_rate` 正确计算（TC 数据有效时）

---

## 4. 前端需求详情

### 4.1 Dashboard Tab 模式感知

**需求编号**: REQ-D004

**需求描述**:
Dashboard 根据当前项目的 `coverage_mode` 正确展示数据。

**重要**：前端展示标签**保持一致**（CP Covered、Unlinked、TC Pass Rate），不区分 TC-CP/FC-CP 标签。

### 4.2 前端展示标签（保持不变）

| Tab | 标签 | 说明 |
|-----|------|------|
| Overview | "CP Covered" | 已覆盖的 CP 数量 |
| Overview | "Unlinked" | 未关联的 CP 数量 |
| Overview | "TC Pass Rate" | TC 通过率（FC-CP 模式下仍显示） |
| Coverage Matrix | "FC / CP Matrix" | FC-CP 模式显示 |
| Coverage Holes | "Linked FC/TC" | 根据模式显示 |

**验收标准**:
- [ ] Dashboard Overview Tab 标签不区分 TC/FC（保持原有标签）
- [ ] 数据根据模式使用正确的计算逻辑

---

## 5. 数据库表结构

### 5.1 project_progress 表

```sql
CREATE TABLE project_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    actual_coverage REAL,
    p0_coverage REAL,
    p1_coverage REAL,
    p2_coverage REAL,
    p3_coverage REAL,
    tc_pass_count INTEGER,
    tc_total INTEGER,
    cp_covered INTEGER,        -- TC-CP: 有 PASS TC 的 CP
                              -- FC-CP: 有 coverage_pct > 0 FC 的 CP
    cp_total INTEGER,
    progress_data TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    updated_by TEXT,
    UNIQUE(project_id, snapshot_date)
);
```

**注意**：快照表结构不变，`cp_covered` 字段在两种模式下含义统一。

---

## 6. API 接口变更

### 6.1 `/api/dashboard/stats` 响应格式

**TC-CP 模式**：
```json
{
  "success": true,
  "mode": "tc_cp",
  "overview": {
    "total_cp": 30,
    "covered_cp": 20,
    "coverage_rate": 66.7,
    "unlinked_cp": 10,
    "tc_total": 52,
    "tc_pass": 45,
    "tc_pass_rate": 86.5,
    "week_change": {
      "covered_cp": 2,
      "unlinked_cp": -1,
      "tc_pass_rate": 5.2
    }
  }
}
```

**FC-CP 模式**：
```json
{
  "success": true,
  "mode": "fc_cp",
  "overview": {
    "total_cp": 30,
    "covered_cp": 15,
    "coverage_rate": 50.0,
    "unlinked_cp": 15,
    "tc_total": 20,
    "tc_pass": 18,
    "tc_pass_rate": 90.0,
    "week_change": {
      "covered_cp": 1,
      "unlinked_cp": -1,
      "tc_pass_rate": 2.5
    }
  }
}
```

### 6.2 `calculate_current_coverage()` 返回值

```python
{
    'actual_coverage': 66.7,
    'tc_pass_count': 45,
    'tc_fail_count': 5,
    'tc_total': 52,
    'cp_covered': 20,      # 根据 coverage_mode 计算
    'cp_total': 30,
    'cp_states': {...},
    'tc_states': {...}
}
```

---

## 7. 测试需求

### 7.1 API 测试用例

| 测试 ID | 说明 | 模式 |
|---------|------|------|
| API-DASH-FC-001 | `covered_cp` = 有 coverage_pct > 0 FC 关联的 CP | FC-CP |
| API-DASH-FC-002 | `unlinked_cp` = total_cp - covered_cp | FC-CP |
| API-DASH-FC-003 | `week_change.covered_cp` 正确计算 | FC-CP |
| API-DASH-FC-004 | 快照 `cp_covered` 正确 | FC-CP |
| API-DASH-FC-005 | TC-CP 模式行为不变 | TC-CP |

### 7.2 回归测试

| 测试 ID | 说明 |
|---------|------|
| REGR-001 | TC-CP 项目 Dashboard 行为完全不变 |
| REGR-002 | 快照保存 TC-CP 数据正确 |
| REGR-003 | week_change TC-CP 模式计算正确 |

---

## 8. 验收标准

### 8.1 API 验收

- [ ] `/api/dashboard/stats` FC-CP 模式返回正确的 `covered_cp`
- [ ] FC-CP 模式 `covered_cp` = 有 `coverage_pct > 0` FC 关联的 CP
- [ ] FC-CP 模式 `unlinked_cp` = total_cp - covered_cp
- [ ] FC-CP 模式 `week_change` 正确计算
- [ ] TC-CP 模式行为保持不变
- [ ] 响应包含 `mode` 字段

### 8.2 快照系统验收

- [ ] `calculate_current_coverage()` 支持 FC-CP 模式
- [ ] FC-CP 项目快照 `cp_covered` 数据正确
- [ ] TC-CP 项目快照数据不变

### 8.3 回归验收

- [ ] TC-CP 模式项目 Dashboard 完全正常
- [ ] Wiki 集成功能不受影响
- [ ] 所有现有测试通过

---

## 9. 命名问题说明

### 9.1 当前命名混乱

| 名称 | 位置 | 语义问题 |
|------|------|---------|
| `covered_cp` | API 响应字段 | 清晰 |
| `cp_covered` | 数据库字段、变量 | 与 `covered_cp` 相似易混淆 |
| `covered_cps` | 局部变量 | 多了一个 `s` |

### 9.2 建议后续优化（不在本次 scope）

| 旧名称 | 新名称 |
|--------|--------|
| `cp_covered` (DB) | `cps_covered` |
| `covered_cps` | `cps_with_valid_coverage` |

**本次不做命名修改**，作为技术债务单独处理。

---

## 10. 风险与注意事项

### 10.1 快照数据一致性问题

**风险**：项目在 TC-CP 和 FC-CP 模式之间切换后，历史快照数据可能不兼容。

**缓解措施**：
- 在切换模式后提示用户重新创建快照
- 在 UI 上显示警告信息

### 10.2 week_change 计算依赖历史快照

**风险**：FC-CP 项目的 week_change 计算依赖快照中存储的 `cp_covered` 值。

**说明**：
- 如果快照是在 TC-CP 模式下创建的，FC-CP 模式下的 week_change 可能不准确
- 这是已知限制，需要在切换模式后重新创建快照

---

## 11. 相关文档

| 文档 | 路径 |
|------|------|
| 功能规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.13.0_DASHBOARD_FC_CP_SUPPLEMENT.md` |
| 主测试计划 | `docs/PLANS/TRACKER_TEST_PLAN_v0.13.0.md` |
| API 测试策略 | `docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| Dashboard API | `dev/app/api.py` (line ~4810-5521) |
| Dashboard 前端 | `dev/static/js/dashboard.js` |
| 快照系统 | `dev/app/api.py` (line ~1271-1436) |

---

## 12. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.13.0 | 2026-04-15 | 初始版本 |

---

**文档创建时间**: 2026-04-15
**创建人**: Claude Code
