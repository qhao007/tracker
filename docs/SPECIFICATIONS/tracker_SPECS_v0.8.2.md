# Tracker v0.8.2 版本开发规格书

> **版本**: v0.8.2
> **创建日期**: 2026-03-02
> **状态**: 规划中
> **关联需求**: `/projects/management/feedbacks/reviewed/tracker_FEATURE_REQUESTS_v0.8.x_20260226.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | CP覆盖率实际曲线显示 | P1 | 4h |
| 2 | 快照数据采集（手动/定时） | P1 | 3h |
| 3 | 快照管理（查看/删除） | P1 | 2h |
| 4 | 导出进度数据 | P2 | 1h |
| | **总计** | | **~10h** |

### 1.2 背景

v0.8.1 已实现计划曲线（基于 TC target_date 的预期覆盖率），v0.8.2 需要实现实际曲线功能，让用户可以：
- 记录每周的实际进度
- 对比计划 vs 实际的差距
- 长期跟踪项目覆盖率趋势

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 实际曲线显示 | 计划曲线（v0.8.1 已完成） |
| 手动/定时快照 | v0.8.3 日期必填 |
| 快照管理 | admin 强制改密码 |

---

## 2. 需求详情

### 2.1 功能需求 #1: 实际曲线显示

**需求编号**: REQ-082-001

**需求描述**:
在 Progress Charts 页面中显示实际覆盖率曲线，与计划曲线同时展示，便于对比计划与实际的差距。

**前端需求**:
- 图表同时显示两条曲线：计划曲线（蓝色虚线）+ 实际曲线（绿色实线）
- 实际曲线使用绿色实线区分于计划曲线的蓝色虚线
- 共用 v0.8.1 的时间段选择器

**后端需求**:
- 扩展 `/api/progress/<project_id>` 返回实际曲线数据
- 从 `project_progress` 表读取实际覆盖率数据

### 2.2 功能需求 #2: 快照数据采集

**需求编号**: REQ-082-002

**需求描述**:
支持手动触发和定时任务两种方式采集每周的实际进度快照。

**前端需求**:
- 在 Progress Charts 页面添加"刷新快照"按钮（）
- 点击后触发快照仅 admin 可见采集

**后端需求**:
- 实现快照生成算法：计算当前 Pass 状态 TC 关联的 CP 覆盖率
- API: `POST /api/progress/<project_id>/snapshot` - 手动触发
- API: `POST /api/cron/progress-snapshot` - 定时任务（需 Token 认证）
- 环境变量: `CRON_API_TOKEN` 配置

### 2.3 功能需求 #3: 快照管理

**需求编号**: REQ-082-003

**需求描述**:
管理员可以查看和删除历史快照，非管理员只能查看。

**前端需求**:
- 在 Progress Charts 页面添加"快照管理"入口（仅 admin）
- 弹出快照列表对话框
- 管理员可删除快照

**后端需求**:
- API: `GET /api/progress/<project_id>/snapshots` - 获取快照列表
- API: `DELETE /api/progress/snapshots/<id>` - 删除快照
- 权限控制：admin 可删除，user/guest 只读

### 2.4 功能需求 #4: 导出进度数据

**需求编号**: REQ-082-004

**需求描述**:
支持导出项目的进度数据（快照列表）供离线分析。

**前端需求**:
- 在快照管理对话框添加"导出"按钮

**后端需求**:
- API: `GET /api/progress/<project_id>/export` - 导出快照数据（CSV/JSON）

---

## 3. 数据库修改

### 3.1 新增表

```sql
CREATE TABLE project_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    actual_coverage REAL,
    tc_pass_count INTEGER,
    tc_total INTEGER,
    cp_covered INTEGER,
    cp_total INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    updated_by TEXT,
    UNIQUE(project_id, snapshot_date)
);
```

| 字段 | 类型 | 说明 |
|------|------|------|
| project_id | INTEGER | 项目 ID |
| snapshot_date | DATE | 快照日期 |
| actual_coverage | REAL | 实际覆盖率 (%) |
| tc_pass_count | INTEGER | Pass 状态 TC 数 |
| tc_total | INTEGER | 总 TC 数 |
| cp_covered | INTEGER | 已覆盖 CP 数 |
| cp_total | INTEGER | 总 CP 数 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TEXT | 更新时间 |
| updated_by | TEXT | 更新人 |

### 3.2 数据迁移脚本

**迁移文件**: `scripts/migrate_v0.8.2.py`

```python
def migrate():
    """创建 project_progress 表"""
    # 迁移逻辑
```

---

## 4. API 接口设计

### 4.1 接口列表

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/progress/<project_id>` | 获取完整图表数据（含实际曲线） | ⏳ 待实现 |
| POST | `/api/progress/<project_id>/snapshot` | 手动触发快照 | ⏳ 待实现 |
| POST | `/api/cron/progress-snapshot` | 定时任务接口（需 Token） | ⏳ 待实现 |
| GET | `/api/progress/<project_id>/snapshots` | 获取快照列表 | ⏳ 待实现 |
| DELETE | `/api/progress/snapshots/<id>` | 删除快照 | ⏳ 待实现 |
| GET | `/api/progress/<project_id>/export` | 导出进度数据 | ⏳ 待实现 |

### 4.2 详细 API 规范

#### 4.2.1 获取进度数据（含实际曲线）

**端点**: `GET /api/progress/<project_id>`

**响应**:
```json
{
    "project_id": 1,
    "project_name": "SOC_DV",
    "start_date": "2026-01-06",
    "end_date": "2026-04-18",
    "planned": [
        {"week": "2026-01-06", "coverage": 0},
        {"week": "2026-01-13", "coverage": 10}
    ],
    "actual": [
        {"week": "2026-01-06", "coverage": 0},
        {"week": "2026-01-13", "coverage": 5}
    ]
}
```

#### 4.2.2 手动触发快照

**端点**: `POST /api/progress/<project_id>/snapshot`

**请求头**:
```
Content-Type: application/json
Cookie: session=xxx
```

**响应**:
```json
{
    "success": true,
    "snapshot": {
        "id": 1,
        "snapshot_date": "2026-03-02",
        "actual_coverage": 40.5,
        "tc_pass_count": 20,
        "tc_total": 50,
        "cp_covered": 12,
        "cp_total": 30,
        "created_at": "2026-03-02 10:00:00"
    }
}
```

#### 4.2.3 定时任务接口

**端点**: `POST /api/cron/progress-snapshot`

**请求头**:
```
Content-Type: application/json
X-API-Token: <CRON_API_TOKEN>
```

**响应**:
```json
{
    "success": true,
    "message": "Snapshots created",
    "count": 5
}
```

**错误响应**:
```json
{
    "error": "Unauthorized"
}
```
**状态码**: 401

#### 4.2.4 获取快照列表

**端点**: `GET /api/progress/<project_id>/snapshots`

**响应**:
```json
{
    "snapshots": [
        {
            "id": 1,
            "snapshot_date": "2026-02-01",
            "actual_coverage": 45.5,
            "tc_pass_count": 20,
            "tc_total": 50,
            "cp_covered": 30,
            "cp_total": 60,
            "created_at": "2026-02-01 10:00:00"
        }
    ]
}
```

#### 4.2.5 删除快照

**端点**: `DELETE /api/progress/snapshots/<id>`

**权限**: admin only

**响应**:
```json
{
    "success": true,
    "message": "Snapshot deleted"
}
```

#### 4.2.6 导出进度数据

**端点**: `GET /api/progress/<project_id>/export`

**响应**: CSV 或 JSON 格式

---

## 5. 前端界面设计

### 5.1 页面/组件列表

| 页面/组件 | 功能 | 状态 |
|----------|------|------|
| Progress Charts | 实际曲线渲染 | ⏳ 待实现 |
| 刷新快照按钮 | 手动触发快照采集 | ⏳ 待实现 |
| 快照管理对话框 | 查看/删除快照 | ⏳ 待实现 |
| 导出按钮 | 导出进度数据 | ⏳ 待实现 |

### 5.2 界面规范

#### 5.2.1 Progress Charts 页面

**新增元素**:
| 元素 | 类型 | 说明 |
|------|------|------|
| 刷新快照按钮 | button | 位于工具栏，仅 admin 可见 |
| 快照管理按钮 | button | 位于工具栏，仅 admin 可见 |

#### 5.2.2 图表配置

**曲线样式**:
| 曲线类型 | 颜色 | 线型 | 填充 |
|----------|------|------|------|
| 计划曲线 | 蓝色 #2170bb | 虚线 dashed | 是 |
| 实际曲线 | 绿色 #28a745 | 实线 solid | 是 |

#### 5.2.3 快照管理对话框

**对话框结构**:
| 列名 | 字段 | 说明 |
|------|------|------|
| 日期 | snapshot_date | 快照日期 |
| 覆盖率 | actual_coverage | 实际覆盖率 (%) |
| TC | tc_pass_count/tc_total | Pass TC 数/总数 |
| CP | cp_covered/cp_total | 覆盖 CP 数/总数 |
| 操作 | action | 删除按钮（仅 admin） |

---

## 6. 验收标准

### 6.1 实际曲线显示 (#1)

- [ ] 实际曲线正确显示在图表中
- [ ] 实际曲线使用绿色实线（区别于计划曲线蓝色虚线）
- [ ] 计划曲线和实际曲线同时显示
- [ ] 时间段选择器同时控制两条曲线

### 6.2 快照数据采集 (#2)

- [ ] 手动刷新按钮可见（仅 admin）
- [ ] 点击后生成当周快照
- [ ] 定时任务接口正确认证（无 Token 返回 401）
- [ ] 定时任务接口可配置 CRON_API_TOKEN

### 6.3 快照管理 (#3)

- [ ] 快照管理对话框可打开
- [ ] 管理员可查看所有快照
- [ ] 管理员可删除快照（非当周快照无提示）
- [ ] 删除当周快照有提示
- [ ] 非管理员只能查看，不能删除

### 6.4 导出功能 (#4)

- [ ] 导出按钮可见（admin/user）
- [ ] 点击可下载进度数据

---

## 7. 开发计划

### 7.1 开发任务

| 任务 | 状态 | 预计时间 |
|------|------|----------|
| 数据库：创建 project_progress 表 | ⏳ 待完成 | 0.5h |
| 后端：快照生成算法 | ⏳ 待完成 | 2h |
| 后端：API 接口（手动/定时/列表/删除/导出） | ⏳ 待完成 | 2h |
| 前端：实际曲线渲染 | ⏳ 待完成 | 2h |
| 前端：刷新快照按钮 | ⏳ 待完成 | 0.5h |
| 前端：快照管理对话框 | ⏳ 待完成 | 1h |
| 前端：导出功能 | ⏳ 待完成 | 0.5h |
| 测试验证 | ⏳ 待完成 | 1.5h |

### 7.2 里程碑

| 里程碑 | 计划日期 | 实际日期 | 状态 |
|--------|----------|----------|------|
| 数据库设计完成 | 2026-03-02 | | ⏳ 待完成 |
| API 开发完成 | 2026-03-02 | | ⏳ 待完成 |
| 前端开发完成 | 2026-03-02 | | ⏳ 待完成 |
| 测试完成 | 2026-03-03 | | ⏳ 待完成 |
| 发布 | 2026-03-03 | | ⏳ 待完成 |

---

## 8. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| 定时任务配置复杂 | 中 | 低 | 提供 Cron 配置示例 |
| 快照数据量大性能问题 | 中 | 低 | 考虑分页/限制查询范围 |
| Token 安全管理 | 高 | 低 | 使用环境变量，禁止硬编码 |

---

## 9. 相关文档

| 文档 | 路径 |
|------|------|
| 需求文档 | `/projects/management/feedbacks/reviewed/tracker_FEATURE_REQUESTS_v0.8.x_20260226.md` |
| v0.8.1 规格书 | `docs/SPECIFICATIONS/tracker_SPECS_v0.8.1.md` |
| 开发规范 | `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| 测试计划 | `docs/PLANS/TRACKER_TEST_PLAN_v0.8.2.md` |

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.8.2 | 2026-03-02 | 初始版本 |

---

**文档创建时间**: 2026-03-02 22:50:00
**创建人**: 小栗子 🌰
