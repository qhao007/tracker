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

### 1.3 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | Dashboard API 增加 FC-CP 模式检测 | P0 | 1h |
| 2 | `/api/dashboard/stats` 支持 FC-CP 模式 | P0 | 2h |
| 3 | `/api/dashboard/coverage-matrix` 支持 FC-CP 模式 | P0 | 3h |
| 4 | 前端 Dashboard 根据模式切换数据展示 | P0 | 2h |
| 5 | 新增 FC-CP 模式测试数据 | P1 | 1h |
| 6 | API 测试增强 | P0 | 2h |
| 7 | UI 集成测试 | P1 | 2h |
| | **总计** | | **~13h** |

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

### 2.4 FC 表结构（待确认）

根据 `api.py` 分析，FC 相关字段：

```python
# 可能的 FC 表字段（需确认 models.py）
class FunctionalCoverage:
    id: int
    name: str           # FC 名称
    description: str    # 描述
    owner: str          # 负责人
    priority: str       # 优先级
    status: str         # 状态
```

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

**修改要求**：

```python
# api.py: get_dashboard_stats (约 line 4810-4900)

# 1. 获取项目 coverage_mode
project = next((p for p in projects if p['id'] == project_id), None)
if not project:
    return jsonify({'error': 'Project not found'}), 404

coverage_mode = project.get('coverage_mode', 'tc_cp')
is_fc_cp_mode = coverage_mode == 'fc_cp'

# 2. 根据模式选择关联表
if is_fc_cp_mode:
    # 使用 fc_cp_connections 表
    connections = db.session.query(FcCpConnection).filter_by(project_id=project_id).all()
    # FC 统计
    total_fcs = db.session.query(FunctionalCoverage).filter_by(project_id=project_id).count()
    covered_fcs = len(set(c.fc_id for c in connections))
    coverage_rate = (covered_fcs / total_fcs * 100) if total_fcs > 0 else 0
else:
    # 使用 tc_cp_connections 表（现有逻辑）
    ...
```

**API 响应增强**：
```json
{
  "mode": "fc_cp",  // 新增：告知前端当前模式
  "stats": {
    "total_items": 52,
    "covered_items": 45,
    "coverage_rate": 86.54
  }
}
```

**验收标准**:
- [ ] FC-CP 模式项目返回 FC 统计数据（而非 TC）
- [ ] 响应包含 `mode` 字段指示当前模式
- [ ] TC-CP 模式项目行为保持不变

---

### 3.3 功能需求 #3：`/api/dashboard/coverage-matrix` 支持 FC-CP

**需求编号**: REQ-D004

**当前问题**：
- `get_dashboard_coverage_matrix()` (line ~5394) 只使用 TC-CP 连接
- 对 FC-CP 模式项目，Coverage Matrix 展示错误的关联关系

**修改要求**：

```python
# api.py: get_dashboard_coverage_matrix (约 line 5394-5500)

# 1. 检测 coverage_mode
project = next((p for p in projects if p['id'] == project_id), None)
coverage_mode = project.get('coverage_mode', 'tc_cp')
is_fc_cp_mode = coverage_mode == 'fc_cp'

# 2. 根据模式选择关联表和项
if is_fc_cp_mode:
    # 获取所有 FC 和 CP
    items = db.session.query(FunctionalCoverage).filter_by(project_id=project_id).all()
    cover_points = db.session.query(CoverPoint).filter_by(project_id=project_id).all()
    connections = db.session.query(FcCpConnection).filter_by(project_id=project_id).all()

    item_key = 'fc_id'
    item_name_key = 'name'  # FunctionalCoverage.name
else:
    # 获取所有 TC 和 CP（现有逻辑）
    items = db.session.query(TestCase).filter_by(project_id=project_id).all()
    cover_points = db.session.query(CoverPoint).filter_by(project_id=project_id).all()
    connections = db.session.query(TcCpConnection).filter_by(project_id=project_id).all()

    item_key = 'tc_id'
    item_name_key = 'test_name'  # TestCase.test_name

# 3. 构建矩阵数据
matrix = []
for item in items:
    row = {
        'item_id': item.id,
        'item_name': getattr(item, item_name_key),
        'cp_coverage': []
    }
    for cp in cover_points:
        is_covered = any(
            getattr(c, item_key) == item.id and c.cp_id == cp.id
            for c in connections
        )
        row['cp_coverage'].append({
            'cp_id': cp.id,
            'cp_name': cp.name,
            'covered': is_covered
        })
    matrix.append(row)
```

**验收标准**:
- [ ] FC-CP 模式显示 FC-CP Coverage Matrix
- [ ] TC-CP 模式行为保持不变
- [ ] 响应包含 `mode` 字段
- [ ] 矩阵行/列数据正确

---

## 4. 前端需求详情

### 4.1 Dashboard Tab 模式感知

**需求编号**: REQ-D005

**需求描述**:
Dashboard 的 4 个 Tab 需要根据当前项目的 `coverage_mode` 正确展示数据。

**修改要求**：

```javascript
// dashboard.js

// 1. 在 loadDashboard() 中获取并保存 mode
async function loadDashboard(projectId) {
    // 加载 Coverage Holes（已支持 FC-CP）
    await loadCoverageHoles(projectId);

    // 从 holesData 获取 mode（Coverage Holes API 已返回 mode）
    const mode = this.holesData?.mode || 'tc_cp';
    this.currentMode = mode;

    // 2. 根据 mode 调用对应的 API
    if (mode === 'fc_cp') {
        // 加载 FC-CP 统计数据
        await loadFcCpStats(projectId);
        await loadFcCpOwnerStats(projectId);
        await loadFcCpCoverageMatrix(projectId);
    } else {
        // 加载 TC-CP 统计数据
        await loadTcCpStats(projectId);
        await loadTcCpOwnerStats(projectId);
        await loadTcCpCoverageMatrix(projectId);
    }
}

// 3. 在 renderOverviewTab() 中根据 mode 显示不同标签
function renderOverviewTab() {
    const mode = this.currentMode;
    const label = mode === 'fc_cp' ? 'FC' : 'TC';
    const unit = mode === 'fc_cp' ? 'Functional Coverage' : 'Test Case';

    // 更新标签文本
    document.querySelector('#totalItemsLabel').textContent = `Total ${label}s`;
    document.querySelector('#coveredItemsLabel').textContent = `Covered ${label}s`;
}
```

### 4.2 前端展示标签调整

> **注意**: Owner Distribution Tab 不需要修改，Owner 始终从 test_case 表获取。

| Tab | TC-CP 模式标签 | FC-CP 模式标签 |
|-----|---------------|---------------|
| Overview | "Test Cases" | "Functional Coverages" |
| Overview | "Coverage Rate" | "Functional Coverage Rate" |
| Coverage Matrix | "TC / CP Matrix" | "FC / CP Matrix" |
| Coverage Holes | "Linked TC" | "Linked FC" |

---

## 5. 数据库表结构（待确认）

### 5.1 functional_coverage 表

```sql
-- 确认 FC 表结构（可能存在于 models.py）
CREATE TABLE functional_coverage (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    owner TEXT,
    priority TEXT,
    status TEXT,
    project_id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 5.2 fc_cp_connection 表

```sql
-- FC-CP 关联表（可能已存在）
CREATE TABLE fc_cp_connection (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    fc_id INTEGER NOT NULL,
    cp_id INTEGER NOT NULL,
    created_at TIMESTAMP
);
```

### 5.3 models.py 需要确认

需要确认 `models.py` 中是否存在：
- `FunctionalCoverage` 模型
- `FcCpConnection` 模型

---

## 6. API 接口变更

### 6.1 `/api/dashboard/stats` 响应变更

**变更前**：
```json
{
  "total_tcs": 52,
  "covered_tcs": 45,
  "coverage_rate": 86.54
}
```

**变更后**：
```json
{
  "mode": "fc_cp",
  "total_items": 52,
  "covered_items": 45,
  "coverage_rate": 86.54,
  "item_type": "FC"
}
```

### 6.2 `/api/dashboard/owner-stats` 响应变更

**变更后响应**：
```json
{
  "mode": "fc_cp",
  "owner_stats": [
    {
      "owner": "John",
      "total": 10,
      "covered": 8,
      "coverage_rate": 80.0
    }
  ]
}
```

### 6.3 `/api/dashboard/coverage-matrix` 响应变更

**变更后响应**：
```json
{
  "mode": "fc_cp",
  "items": [
    {
      "item_id": 1,
      "item_name": "FC_001",
      "cp_coverage": [
        {"cp_id": 1, "cp_name": "CP_A", "covered": true},
        {"cp_id": 2, "cp_name": "CP_B", "covered": false}
      ]
    }
  ],
  "cp_list": [
    {"id": 1, "name": "CP_A"},
    {"id": 2, "name": "CP_B"}
  ]
}
```

---

## 7. 测试需求

### 7.1 测试数据准备

需要创建一个 FC-CP 模式的测试项目：

```python
# test fixtures
FC_CP_TEST_PROJECT = {
    "name": "FC_CP_Test_Project",
    "coverage_mode": "fc_cp"
}
```

**测试数据要求**：
- 3-5 个 FC 记录
- 5-8 个 CP 记录
- 部分 FC-CP 关联

### 7.2 API 测试用例

| 测试用例 | 描述 |
|----------|------|
| test_dashboard_stats_fc_cp_mode | `/api/dashboard/stats` 返回 FC 统计 |
| test_dashboard_stats_tc_cp_mode | `/api/dashboard/stats` TC-CP 模式不变 |
| test_dashboard_matrix_fc_cp | `/api/dashboard/coverage-matrix` 返回 FC-CP 矩阵 |
| test_dashboard_owner_stats_unchanged | `/api/dashboard/owner-stats` TC-CP/FC-CP 行为一致（均查 test_case） |

### 7.3 UI 测试用例

| 测试用例 | 描述 |
|----------|------|
| test_dashboard_fc_cp_overview | FC-CP 项目 Overview Tab 显示 FC 标签 |
| test_dashboard_fc_cp_coverage_matrix | FC-CP 项目 Coverage Matrix 显示 FC-CP 矩阵 |
| test_dashboard_mode_switch | 项目切换后 Dashboard 正确刷新 |

---

## 8. 验收标准

### 8.1 API 验收

- [ ] `/api/dashboard/stats` 在 FC-CP 模式下返回 FC 统计数据
- [ ] `/api/dashboard/stats` 响应包含 `mode` 字段
- [ ] `/api/dashboard/owner-stats` 在 FC-CP 模式下返回 FC Owner 统计
- [ ] `/api/dashboard/coverage-matrix` 在 FC-CP 模式下返回 FC-CP 矩阵
- [ ] TC-CP 模式项目行为保持不变

### 8.2 前端验收

- [ ] Dashboard Overview Tab 根据模式显示正确标签（TC vs FC）
- [ ] Owner Distribution Tab 不变（始终显示 TC Owner）
- [ ] Coverage Matrix Tab 显示正确的矩阵标题
- [ ] 项目切换时 Dashboard 正确刷新

### 8.3 回归验收

- [ ] TC-CP 模式项目 Dashboard 完全正常
- [ ] Wiki 集成功能不受影响
- [ ] 所有现有测试通过

---

## 9. 开发计划

### 9.1 开发任务

| 任务 | 状态 | 预计时间 | 依赖 |
|------|------|----------|------|
| 确认 FC 表结构和 models.py | ⏳ 待确认 | 0.5h | - |
| 修改 `get_dashboard_stats()` | ⏳ 待实现 | 2h | 确认 FC 表 |
| 修改 `get_dashboard_coverage_matrix()` | ⏳ 待实现 | 3h | 确认 FC 表 |
| 前端 Dashboard 模式感知 | ⏳ 待实现 | 2h | API 修改完成 |
| 添加 FC-CP 测试数据 | ⏳ 待实现 | 1h | - |
| API 测试增强 | ⏳ 待实现 | 2h | API 修改完成 |
| UI 集成测试 | ⏳ 待实现 | 2h | 前端修改完成 |
| 回归测试 | ⏳ 待实现 | 1h | - |

### 9.2 里程碑

| 里程碑 | 计划日期 | 状态 |
|--------|----------|------|
| 确认 FC 表结构 | +0.5 天 | ⏳ 待完成 |
| API 修改完成 | +2.5 天 | ⏳ 待完成 |
| 前端修改完成 | +3.5 天 | ⏳ 待完成 |
| 测试完成 | +4.5 天 | ⏳ 待完成 |
| 发布 | +5 天 | ⏳ 待完成 |

---

## 10. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| FC 表结构与预期不符 | 高 | 中 | 先确认 models.py 是否有 FC 相关模型 |
| 前端需要较大改动 | 中 | 低 | 仅修改标签和 API 调用逻辑 |
| 现有测试回归失败 | 中 | 中 | 充分测试 TC-CP 模式保持不变 |

---

## 11. 相关文档

| 文档 | 路径 |
|------|------|
| 主规格书 (v0.13.0) | `docs/SPECIFICATIONS/tracker_SPECS_v0.13.0.md` |
| Dashboard API | `dev/app/api.py` (line ~4810-5521) |
| Dashboard 前端 | `dev/static/js/dashboard.js` |
| Dashboard 测试 | `dev/tests/test_api/test_api_dashboard.py` |

---

## 12. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.13.0 | 2026-04-15 | 初始版本 |

---

**文档创建时间**: 2026-04-15
**创建人**: Claude Code
