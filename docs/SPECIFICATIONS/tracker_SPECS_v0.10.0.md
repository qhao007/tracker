# Tracker v0.10.0 版本开发规格书

> **版本**: v0.10.0
> **创建日期**: 2026-03-18
> **状态**: 开发中
> **关联需求**: `/projects/management/feedbacks/reviewed/requirements_analysis_v0.10.0_20260317.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | REQ-1: 优化关联选择列表交互体验 | P1 | 4h |
| 2 | REQ-2: 图表支持按CP Priority过滤 | P1 | 8h |
| 2.1 | - 计划曲线 Priority 过滤 | P1 | 3h |
| 2.2 | - 实际曲线 Priority 过滤 | P1 | 5h |
| 3 | REQ-3: 前端代码JSDoc注释补充 | P2 | 6h |
| 4 | REQ-4: 后端API错误处理日志 | P2 | 4h |
| | **总计** | | **~22h** |

### 1.2 背景

v0.9.2 已于 2026-03-17 发布，本版本主要解决以下问题：
1. 用户反馈：关联选择列表交互体验待优化
2. 用户反馈：图表需支持按 CP Priority 过滤
3. 代码质量：前端核心函数缺少 JSDoc 注释
4. 代码质量：后端 API 缺少错误处理日志

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 关联选择搜索过滤功能 | API 版本变更 |
| 关联选择即时过滤功能 | 第三方依赖更新 |
| 已关联CP名称显示功能 | 自定义字段功能 |
| Priority 多选过滤功能（计划曲线） | 忘记密码功能 |
| Priority 多选过滤功能（实际曲线） | 长周期图表优化 |
| 核心函数 JSDoc 注释 | HTTPS 配置 |
| API 日志装饰器 | |
| project_progress 表扩展（P0-P3覆盖率字段） | |

---

## 2. 需求详情

### 2.1 REQ-1: 优化关联选择列表交互体验

**需求描述**:
目前 CP/TC 关联时，下拉选择列表在条目较多时不便于用户选择，且选择后也较难找到到底关联了哪些 CP。需要提供更友好的选择方案。

**实现方案**:
| 功能 | 说明 |
|------|------|
| 搜索输入框 | 独立搜索框，在关联选择下拉框的上方 |
| 即时过滤 | 支持按名称即时过滤列表项 |
| 已关联CP显示 | 在关联选择区域下方新增显示区域，显示已关联的CP名称（使用 cover_point） |

**状态管理**:
- 已选项数据存储在前端 JS 状态（coverPoints, testCases）
- 状态变更时通过重新渲染 DOM 更新 UI

**交互设计**:
- Tab 键可在搜索框和列表间切换
- Enter 键确认选择
- Escape 键关闭模态框
- Ctrl+K 快捷键聚焦搜索框

**空状态提示**:
- 搜索无结果时显示: "未找到匹配的覆盖点，尝试调整搜索关键词"

**UI 布局示意**:
```
+---------------------------+
|  🔍 搜索输入框 (独立)     |  <- 上方：搜索框
+---------------------------+
|  关联选择区域 (Checkboxes)|  <- 中间：CP 列表（过滤后）
|  ☐ CP-功能A-场景1        |
|  ☑ CP-功能B-场景2        |
|  ☐ CP-功能C-场景1        |
+---------------------------+
|  已关联: CP-功能B-场景2   |  <- 下方：已关联CP显示
+---------------------------+
```

**验收标准**:
- [ ] 搜索输入框位于关联选择区域上方
- [ ] 输入搜索词后列表在 200ms 内完成过滤
- [ ] 搜索无结果时显示空状态提示
- [ ] 支持 Ctrl+K 快捷键聚焦搜索框
- [ ] 已关联CP显示区域位于关联选择区域下方
- [ ] 已关联CP显示CP名称（cover_point），而非编号
- [ ] 取消关联后已关联CP显示区域实时更新
- [ ] 现有 TC/CP CRUD 功能正常（回归测试）

---

### 2.2 REQ-2: 图表支持按CP Priority过滤

**需求描述**:
覆盖率进度曲线图表需要支持根据 CP priority 过滤后的 CP 来生成。

**问题分析** (2026-03-19 补充):
- 当前 `project_progress` 表只存储了一个总体的 `actual_coverage` 值
- 即使选择 P0 过滤，实际曲线仍然显示相同的值（因为只读取了总体覆盖率）
- 需要扩展存储结构，使实际曲线也能按 Priority 过滤

**实现方案**:
| 功能 | 说明 |
|------|------|
| 后端 API | `GET /api/progress/<project_id>?priority=P0,P1` 支持多值过滤 |
| 前端 UI | 多选下拉框 (Checkbox multi-select)，如显示 "P0, P1" |
| 缓存策略 | 暂不需要，图表数据量小，每次请求实时计算 |

**计划曲线实现**:
- 实时从 TC/CP 表计算，根据 priority_filter 参数过滤
- 已在 v0.8.1 实现，本次扩展支持多值

**实际曲线实现** (新增):
- 扩展 `project_progress` 表，添加 P0-P3 各维度覆盖率字段
- 快照创建/更新时，计算并存储各 Priority 的覆盖率
- API 读取时根据 priority_filter 返回对应字段

**数据库设计**:
```sql
-- 扩展 project_progress 表 (v0.10.0)
ALTER TABLE project_progress ADD COLUMN p0_coverage REAL;  -- P0 CP 覆盖率
ALTER TABLE project_progress ADD COLUMN p1_coverage REAL;  -- P1 CP 覆盖率
ALTER TABLE project_progress ADD COLUMN p2_coverage REAL;  -- P2 CP 覆盖率
ALTER TABLE project_progress ADD COLUMN p3_coverage REAL;  -- P3 CP 覆盖率
```

**API 设计**:
```
GET /api/progress/<project_id>?priority=P0,P1
```

**响应数据结构**:
```json
{
    "planned": [{"week": "2026-01-01", "coverage": 85.5}, ...],
    "actual": [
        {"week": "2026-01-01", "coverage": 80.0},   // 当 priority=P0 时返回 p0_coverage
        {"week": "2026-01-08", "coverage": 82.5}
    ],
    "priority_filter": "P0"
}
```

**UI 设计**:
- Priority 过滤下拉框位于图表上方
- 图表标题显示当前过滤条件，如 "覆盖率进度 (P0+P1)"
- 提供"重置过滤"按钮，恢复默认全选状态

**验收标准**:
- [ ] API 支持 priority 参数多值过滤
- [ ] 前端 Priority 过滤使用 Checkbox multi-select 下拉框
- [ ] 图表标题显示当前过滤条件
- [ ] 提供"重置过滤"按钮
- [ ] 选择 P0 时计划曲线数据仅包含 P0 CP
- [ ] 选择 P0 时实际曲线数据仅显示 P0 覆盖率
- [ ] 选择多个 Priority 时图表数据正确合并
- [ ] 图表渲染在 500ms 内完成（回归测试）
- [ ] 现有图表功能正常（回归测试）
- [ ] 快照创建时正确计算各 Priority 覆盖率

---

### 2.3 REQ-3: 前端代码JSDoc注释补充

**需求描述**:
前端核心函数缺少 JSDoc 注释，影响代码可读性和维护性。

**实现方案**: 核心函数优先补充

**目标函数清单**:

| 优先级 | 函数类型 | 函数清单 |
|--------|----------|----------|
| P0 | API 调用函数 | `fetchProjects()`, `loadProject()`, `saveProject()`, `deleteProject()`, `fetchCP()`, `loadCP()`, `saveCP()`, `deleteCP()`, `fetchTC()`, `loadTC()`, `saveTC()`, `deleteTC()`, `updateTCStatus()` |
| P0 | Modal 管理函数 | `openProjectModal()`, `closeModal()`, `confirmDeleteProject()`, `openCPModal()`, `openTCModal()`, `closeModal()` |
| P1 | 数据处理函数 | `renderProjects()`, `renderCPTable()`, `renderTCTable()`, `applyCPFilter()`, `applyTCFilter()`, `filterCPByLinked()`, `filterTCByStatus()` |
| P2 | 事件处理函数 | `handleTabSwitch()`, `handleSearch()`, `getSelectedTCs()`, `toggleTCDetails()` |

**JSDoc 示例**:
```javascript
/**
 * 获取项目列表
 * @returns {Promise<Array>} 项目数组
 * @throws {Error} 网络错误时抛出
 */
async function fetchProjects() {
    // ...
}
```

**验收标准**:
- [ ] 所有 API 调用函数有 JSDoc 注释
- [ ] 所有 Modal 管理函数有 JSDoc 注释
- [ ] 注释包含参数和返回值说明
- [ ] 前端页面功能正常（回归测试）

---

### 2.4 REQ-4: 后端API错误处理日志

**需求描述**:
后端 API 缺少错误处理日志，关键操作如登录、删除、权限校验等未记录日志。

**实现方案**: 使用 Flask `after_request` 统一记录

**技术实现**:
```python
import logging
import time
import json

# 日志格式规范 (JSON)
def log_request(response):
    """统一记录 API 请求日志"""
    duration = time.time() - request.start_time
    
    log_data = {
        "event": "api_call",
        "endpoint": request.path,
        "method": request.method,
        "status_code": response.status_code,
        "duration_ms": int(duration * 1000),
        "user": current_user.id if current_user.is_authenticated else "anonymous",
        "ip": request.remote_addr
    }
    
    # INFO: 正常请求
    # WARNING: 4xx 客户端错误
    # ERROR: 5xx 服务器错误
    if response.status_code >= 500:
        logger.error(json.dumps(log_data))
    elif response.status_code >= 400:
        logger.warning(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))
    
    return response

@app.after_request
def after_request(response):
    return log_request(response)

# 在请求开始时记录时间
@app.before_request
def before_request():
    request.start_time = time.time()
```

**日志级别**:
| 级别 | 使用场景 |
|------|----------|
| INFO | 正常操作 (2xx) |
| WARNING | 客户端错误 (4xx) |
| ERROR | 服务器错误 (5xx) |

**日志格式示例**:
```json
{"event": "api_call", "endpoint": "/api/projects", "method": "POST", "status_code": 200, "duration_ms": 15, "user": "admin", "ip": "127.0.0.1"}
```

**性能影响**: 日志开销 < 1%，可忽略不计

**验收标准**:
- [ ] 所有 API 请求有日志记录
- [ ] 日志包含 endpoint, method, status_code, duration_ms, user, ip
- [ ] 异常错误被记录 (5xx)
- [ ] API 响应时间不受影响（回归测试）

---

## 3. 数据库修改

### 3.1 表结构变更

**project_progress 表扩展** (v0.10.0 新增):

```sql
-- 为支持实际曲线 Priority 过滤，扩展 project_progress 表
ALTER TABLE project_progress ADD COLUMN p0_coverage REAL;  -- P0 CP 覆盖率 (0-100)
ALTER TABLE project_progress ADD COLUMN p1_coverage REAL;  -- P1 CP 覆盖率 (0-100)
ALTER TABLE project_progress ADD COLUMN p2_coverage REAL;  -- P2 CP 覆盖率 (0-100)
ALTER TABLE project_progress ADD COLUMN p3_coverage REAL;  -- P3 CP 覆盖率 (0-100)
```

**新增字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| p0_coverage | REAL | P0 Priority CP 的覆盖率 |
| p1_coverage | REAL | P1 Priority CP 的覆盖率 |
| p2_coverage | REAL | P2 Priority CP 的覆盖率 |
| p3_coverage | REAL | P3 Priority CP 的覆盖率 |

**计算逻辑**:
- 快照创建时，对于每个 Priority Px，统计该 Priority 下已 Pass TC 关联的 CP 数量
- 覆盖率 = (已覆盖 CP 数 / 该 Priority 总 CP 数) × 100

### 3.2 数据迁移

**需要迁移**:
- 现有快照数据的 P0-P3 覆盖率需要重新计算
- 可通过重新生成快照或运行迁移脚本完成

**迁移脚本**:
```python
# 迁移脚本逻辑
for project in projects:
    for snapshot in get_snapshots(project.id):
        for priority in ['P0', 'P1', 'P2', 'P3']:
            coverage = calculate_priority_coverage(project.name, snapshot.date, priority)
            update_snapshot(snapshot.id, f'{priority.lower()}_coverage', coverage)
```

---

## 4. API 接口设计

### 4.1 接口列表

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/progress/<project_id>` | 获取项目进度（支持 priority 参数） | ⏳ 待实现 |

### 4.2 详细 API 规范

#### 4.2.1 获取项目进度（支持 Priority 过滤）

**端点**: `GET /api/progress/<project_id>`

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | 是 | 项目 ID |
| priority | string | 否 | Priority 过滤，多值用逗号分隔，如 "P0,P1" |

**请求头**:
```
Content-Type: application/json
```

**响应**:
```json
{
    "success": true,
    "data": {
        "project_id": 1,
        "progress_data": [...]
    }
}
```

**错误响应**:
```json
{
    "error": "错误描述"
}
```

**状态码**:
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 项目不存在 |
| 500 | 服务器错误 |

---

## 5. 前端界面设计

### 5.1 页面/组件列表

| 页面/组件 | 功能 | 状态 |
|----------|------|------|
| TC/CP 关联选择区域 | 搜索过滤 + 已关联CP显示 | ⏳ 待实现 |
| 图表 Priority 过滤 | Checkbox 多选下拉框 | ⏳ 待实现 |

### 5.2 界面规范

#### 5.2.1 TC/CP 关联选择区域

**UI 布局**:
```
+---------------------------+
|  🔍 搜索输入框 (独立)     |  <- 上方：搜索框
+---------------------------+
|  关联选择区域 (Checkboxes)|  <- 中间：CP 列表（过滤后）
+---------------------------+
|  已关联: CP-功能B-场景2   |  <- 下方：已关联CP显示
+---------------------------+
```

**表单字段**:
| 字段名 | 类型 | 必填 | 默认值 |
|--------|------|------|--------|
| cpSearch | text | N | "" |
| connected_cps | checkbox[] | N | [] |

**交互逻辑**:
- 搜索输入时，200ms 内过滤 CP 列表
- 搜索无结果显示空状态提示
- Ctrl+K 聚焦搜索框
- 勾选/取消 CP 后，下方"已关联CP显示"区域实时更新

#### 5.2.2 图表 Priority 过滤

**UI 布局**:
```
Priority 过滤: [▼ P0, P1     ]  <- 多选下拉框
               ☑ P0
               ☑ P1
               ☐ P2
               
覆盖率进度 (P0+P1)           <- 图表标题
[图表内容]
[重置过滤]                   <- 重置按钮
```

**表单字段**:
| 字段名 | 类型 | 必填 | 默认值 |
|--------|------|------|--------|
| priority_filter | checkbox[] | N | ["P0","P1","P2"] |

**交互逻辑**:
- 多选下拉框支持 Checkbox 选择
- 选择后图表标题显示过滤条件
- "重置过滤"按钮恢复全选

---

## 6. 验收标准

### 6.1 REQ-1: 关联选择交互优化

- [ ] 搜索输入框位于关联选择区域上方
- [ ] 输入搜索词后列表在 200ms 内完成过滤
- [ ] 搜索无结果时显示空状态提示
- [ ] 支持 Ctrl+K 快捷键聚焦搜索框
- [ ] 已关联CP显示区域位于关联选择区域下方
- [ ] 已关联CP显示CP名称（cover_point），而非编号
- [ ] 取消关联后已关联CP显示区域实时更新
- [ ] 现有 TC/CP CRUD 功能正常（回归测试）

### 6.2 REQ-2: 图表 Priority 过滤

- [ ] API 支持 priority 参数多值过滤
- [ ] 前端 Priority 过滤使用 Checkbox multi-select 下拉框
- [ ] 图表标题显示当前过滤条件
- [ ] 提供"重置过滤"按钮
- [ ] 选择 P0 时计划曲线数据仅包含 P0 CP
- [ ] 选择 P0 时实际曲线数据仅显示 P0 覆盖率
- [ ] 选择多个 Priority 时图表数据正确合并
- [ ] 图表渲染在 500ms 内完成（回归测试）
- [ ] 现有图表功能正常（回归测试）
- [ ] 快照创建时正确计算各 Priority 覆盖率

### 6.3 REQ-3: JSDoc 注释

- [ ] 所有 API 调用函数有 JSDoc 注释
- [ ] 所有 Modal 管理函数有 JSDoc 注释
- [ ] 注释包含参数和返回值说明
- [ ] 前端页面功能正常（回归测试）

### 6.4 REQ-4: API 日志

- [ ] 所有 API 请求有日志记录
- [ ] 日志包含 endpoint, method, status_code, duration_ms, user, ip
- [ ] 异常错误被记录 (5xx)
- [ ] API 响应时间不受影响（回归测试）

---

## 7. 开发计划

### 7.1 开发任务

| 任务 | 负责人 | 状态 | 预计时间 |
|------|--------|------|----------|
| T1: 关联选择搜索过滤前端 | OpenClaw | ⏳ 待开始 | 2h |
| T2: 已关联CP名称显示 | OpenClaw | ⏳ 待开始 | 2h |
| T3: 图表 Priority API 扩展（计划曲线） | OpenClaw | ⏳ 待开始 | 2h |
| T4: 图表 Priority 前端多选过滤 | OpenClaw | ⏳ 待开始 | 2h |
| T3a: project_progress 表扩展 | OpenClaw | ⏳ 待开始 | 1h |
| T3b: 快照创建逻辑更新 | OpenClaw | ⏳ 待开始 | 2h |
| T3c: 实际曲线 API 扩展 | OpenClaw | ⏳ 待开始 | 2h |
| T5: 前端 JSDoc 注释 - API 函数 | OpenClaw | ⏳ 待开始 | 3h |
| T6: 前端 JSDoc 注释 - Modal 函数 | OpenClaw | ⏳ 待开始 | 2h |
| T7: 后端日志装饰器实现 | OpenClaw | ⏳ 待开始 | 2h |
| T8: 后端日志装饰器应用 | OpenClaw | ⏳ 待开始 | 2h |
| T9: 测试与修复 | OpenClaw | ⏳ 待开始 | 4h |

> **注**: T1/T3/T5/T7 可并行开发（前端/后端分离）
> **注**: T3a/T3b/T3c 为 REQ-2 实际曲线 Priority 过滤新增任务

### 7.2 里程碑

| 里程碑 | 计划日期 | 实际日期 | 状态 |
|--------|----------|----------|------|
| 开发完成 | Day 5 | | ⏳ 待完成 |
| 测试完成 | Day 7 | | ⏳ 待完成 |
| 发布 | Day 8 | | ⏳ 待完成 |

---

## 8. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| 关联选择改动影响现有功能 | 中 | 低 | 充分测试，增加 UI 回归测试套件 |
| Priority 过滤计算逻辑复杂 | 低 | 低 | 先在测试环境验证 |
| JSDoc 工作量大 | 低 | 低 | 分批进行，优先核心函数 |
| 日志性能影响 | 低 | 低 | 使用 after_request 方案，预估影响 <1% |

---

## 9. 相关文档

| 文档 | 路径 |
|------|------|
| 需求文档 | `/projects/management/feedbacks/reviewed/requirements_analysis_v0.10.0_20260317.md` |
| 开发规范 | `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| 测试计划 | `docs/PLANS/TRACKER_TEST_PLAN_v0.10.0.md` |
| BugLog | `docs/BUGLOG/tracker_BUG_RECORD.md` |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.10.0 | 2026-03-18 | 初始版本 |
| v0.10.0 | 2026-03-19 | REQ-2 补充：实际曲线 Priority 过滤实现方案（扩展 project_progress 表存储 P0-P3 各维度覆盖率）|

---

**文档创建时间**: 2026-03-18
**创建人**: OpenClaw
