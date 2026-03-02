# Tracker v0.8.0 版本开发规格书

> **版本**: v0.8.0
> **创建日期**: 2026-03-01
> **状态**: 开发中
> **关联需求**: `/projects/management/feedbacks/reviewed/tracker_FEATURE_REQUESTS_v0.8.x_20260226.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | 项目起止日期字段 | P0 | 4h |
| 2 | 基础图表框架 | P0 | 3h |
| 3 | ISSUE-001 项目选择框宽度修复 | P3 | 0.5h |
| | **总计** | | **7.5h** |

### 1.2 背景

v0.8.0 是进度图表功能的第一个版本，主要目标：
1. 为项目添加起止日期字段，为后续进度图表功能提供数据基础
2. 构建基础图表框架，为 v0.8.1/v0.8.2 的曲线展示做准备
3. 修复 ISSUE-001 项目选择框宽度问题

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 项目起止日期字段（数据库、API、前端） | 进度曲线计算和展示（v0.8.1/v0.8.2） |
| Progress Charts 页面基础框架 | 定时任务快照功能 |
| Chart.js 集成 | 批量设置日期功能 |
| ISSUE-001 修复 | admin 强制改密码 |

---

## 2. 需求详情

### 2.1 功能需求 #1: 项目起止日期字段

**需求编号**: REQ-001

**需求描述**:
为项目添加 `start_date` 和 `end_date` 字段，支持项目周期管理。

**前置条件**:
- v0.8.0 必须兼容现有项目（无日期）
- 日期字段在 v0.8.0 为可选，v0.8.3 起为必填

#### 2.1.1 数据库设计

**projects 表扩展**:
```sql
ALTER TABLE project ADD COLUMN start_date TEXT;
ALTER TABLE project ADD COLUMN end_date TEXT;
```

| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| start_date | TEXT | 项目开始日期 (YYYY-MM-DD) | NULL |
| end_date | TEXT | 项目结束日期 (YYYY-MM-DD) | NULL |

**注意**: 使用 TEXT 而非 DATE，保持与现有 `created_at` 字段的一致性。

#### 2.1.2 后端需求

**models.py 修改**:
```python
class Project(db.Model):
    # ... 现有字段 ...
    start_date = db.Column(db.String(10))  # YYYY-MM-DD
    end_date = db.Column(db.String(10))    # YYYY-MM-DD
    
    def to_dict(self):
        return {
            # ... 现有字段 ...
            'start_date': self.start_date,
            'end_date': self.end_date
        }
```

**校验规则**:
1. 如果两者都填写，`start_date` <= `end_date`
2. 日期不能早于今天（可选校验）

#### 2.1.3 API 接口

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| POST | `/api/projects` | 创建项目（支持起止日期） | ⏳ 待实现 |
| PUT | `/api/projects/<id>` | 更新项目（支持起止日期） | ⏳ 待实现 |
| GET | `/api/projects/<id>` | 获取项目（含起止日期） | ⏳ 待实现 |
| GET | `/api/projects` | 列表返回起止日期 | ⏳ 待实现 |

#### 2.1.4 前端需求

**创建项目对话框**:
- 添加日期选择器输入框
- 日期为可选（v0.8.0）
- 校验：开始日期 <= 结束日期

**项目列表**:
- 显示起止日期（如有）
- 无日期显示 "-" 或留空

**编辑项目对话框**:
- 管理员可修改起止日期
- 普通用户只读

---

### 2.2 功能需求 #2: 基础图表框架

**需求编号**: REQ-002

**需求描述**:
创建 Progress Charts 页面基础框架，集成 Chart.js，为后续曲线展示做准备。

#### 2.2.1 技术选型

**图表库**: Chart.js v4.x (CDN)

| 特点 | 说明 |
|------|------|
| 大小 | ~200KB (minified) |
| 许可证 | MIT |
| 依赖 | 无（原生 JS） |
| CDN | `https://cdn.jsdelivr.net/npm/chart.js` |

#### 2.2.2 页面设计

**页面路径**: `/progress` 或作为 Tab

**页面结构**:
```
+--------------------------------------------------+
|  [Cover Points] [Test Cases] [Progress Charts]   |
+--------------------------------------------------+
|                                                  |
|  项目选择: [Project A ▼]                         |
|                                                  |
|  ┌─────────────────────────────────────────┐   |
|  │         CP 覆盖率完成进度               │   |
|  │                                         │   |
|  │   (空项目提示或基础图表占位)            │   |
|  │                                         │   |
|  └─────────────────────────────────────────┘   |
|                                                  |
+--------------------------------------------------+
```

#### 2.2.3 前端组件

| 组件 | 功能 | 状态 |
|------|------|------|
| Tab 导航 | 切换到 Progress Charts | ⏳ 待实现 |
| 项目选择器 | 选择要查看的项目 | ⏳ 待实现 |
| 图表容器 | Chart.js 画布 | ⏳ 待实现 |
| 空状态提示 | 无数据时显示友好提示 | ⏳ 待实现 |

#### 2.2.4 数据结构

**API 返回格式（v0.8.0 基础版）**:
```json
{
  "project_id": 1,
  "project_name": "Project A",
  "start_date": "2026-01-01",
  "end_date": "2026-06-30",
  "planned": [],
  "actual": []
}
```

#### 2.2.5 时间段选择器

**功能**: 用户可选择显示的起始/结束日期

**API 支持**:
```python
@api.route("/api/progress/<project_id>")
def get_progress(project_id):
    start_date = request.args.get('start_date')  # 可选
    end_date = request.args.get('end_date')      # 可选
    # ... 返回数据
```

**⚠️ 数据粒度说明**: 保持每周粒度，不进行采样。长时间周期通过时间段选择器调整显示范围。

---

### 2.3 功能需求 #3: ISSUE-001 项目选择框宽度修复

**需求编号**: REQ-003

**需求描述**:
修复项目选择框宽度自适应导致的布局问题。

**修复方案**:
```css
.project-selector {
    width: 200px;
}
```

---

## 3. 数据库修改

### 3.1 表结构变更

```sql
-- projects 表新增字段
ALTER TABLE project ADD COLUMN start_date TEXT;
ALTER TABLE project ADD COLUMN end_date TEXT;
```

### 3.2 数据迁移脚本

**迁移文件**: `scripts/migrate_v0.8.0.py`

```python
def migrate(db_path):
    """v0.8.0 数据库迁移"""
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 添加起止日期字段
    cursor.execute("ALTER TABLE project ADD COLUMN start_date TEXT")
    cursor.execute("ALTER TABLE project ADD COLUMN end_date TEXT")
    
    conn.commit()
    conn.close()
    print("Migration v0.8.0 completed: added start_date, end_date to project table")
```

---

## 4. API 接口设计

### 4.1 接口列表

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/progress/<project_id>` | 获取项目进度数据 | ⏳ 待实现 |
| GET | `/api/projects` | 获取项目列表（含日期） | ⏳ 待实现 |
| POST | `/api/projects` | 创建项目（含日期） | ⏳ 待实现 |
| PUT | `/api/projects/<id>` | 更新项目（含日期） | ⏳ 待实现 |

### 4.2 详细 API 规范

#### 4.2.1 获取项目进度数据

**端点**: `GET /api/progress/<project_id>`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | 是 | 项目 ID |
| start_date | string | 否 | 起始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |

**响应**:
```json
{
  "project_id": 1,
  "project_name": "Project A",
  "start_date": "2026-01-01",
  "end_date": "2026-06-30",
  "planned": [],
  "actual": []
}
```

**错误响应**:
```json
{
  "error": "Project not found"
}
```

#### 4.2.2 创建项目

**端点**: `POST /api/projects`

**请求体**:
```json
{
    "name": "New Project",
    "start_date": "2026-01-01",
    "end_date": "2026-06-30"
}
```

**响应**:
```json
{
    "success": true,
    "project": {
        "id": 1,
        "name": "New Project",
        "start_date": "2026-01-01",
        "end_date": "2026-06-30"
    }
}
```

---

## 5. 前端界面设计

### 5.1 页面/组件列表

| 页面/组件 | 功能 | 状态 |
|----------|------|------|
| Progress Charts Tab | 进度图表 Tab 切换 | ⏳ 待实现 |
| 项目选择器 | 选择要查看的项目 | ⏳ 待实现 |
| 日期范围选择器 | 选择显示的起始/结束日期 | ⏳ 待实现 |
| Chart.js 图表容器 | 展示进度曲线 | ⏳ 待实现 |
| 空状态提示 | 无项目/无数据时显示 | ⏳ 待实现 |
| 创建项目日期选择器 | 创建项目时输入日期 | ⏳ 待实现 |
| 编辑项目日期选择器 | 编辑项目时修改日期 | ⏳ 待实现 |

### 5.2 界面规范

#### 5.2.1 项目选择框样式修复

**问题**: 项目选择框宽度自适应导致布局问题

**修复**:
```css
.project-selector {
    width: 200px;
    /* 现有样式保留 */
}
```

#### 5.2.2 Progress Charts 页面布局

```html
<div id="progress-charts" style="display: none;">
    <!-- 项目选择器 -->
    <div class="mb-3">
        <label>项目选择: </label>
        <select id="progress-project-select" class="project-selector">
            <!-- 选项 -->
        </select>
    </div>
    
    <!-- 时间段选择器 -->
    <div class="mb-3">
        <label>显示范围: </label>
        <input type="date" id="progress-start-date">
        <span>至</span>
        <input type="date" id="progress-end-date">
        <button id="apply-range">应用</button>
    </div>
    
    <!-- 图表容器 -->
    <div class="chart-container">
        <canvas id="progress-chart"></canvas>
    </div>
    
    <!-- 空状态提示 -->
    <div id="progress-empty-state" style="display: none;">
        <p>暂无数据，请选择项目或设置项目起止日期</p>
    </div>
</div>
```

---

## 6. 验收标准

### 6.1 项目起止日期

- [ ] 创建项目时可输入项目开始/结束日期（可选）
- [ ] 项目起止日期校验（开始日期 <= 结束日期）
- [ ] 项目列表显示起止日期（如果有）
- [ ] 管理员可编辑项目起止日期
- [ ] 现有项目（无日期）可正常访问

### 6.2 基础图表框架

- [x] Progress Charts 页面/Tab 可访问 ✅ v0.8.0
- [x] 项目选择器可用 ✅ v0.8.0
- [x] Chart.js 正确加载 ✅ v0.8.0
- [x] Chart.js 加载失败时显示友好提示（非白屏） ✅ v0.8.0
- [ ] 时间段选择器可用（选择起始/结束日期过滤显示）📅 **v0.8.1**
- [x] 无日期项目访问 Progress Charts 时显示友好提示 ✅ v0.8.0
- [ ] 长时间周期（如1年+）图表可读（通过时间段选择器调整）📅 **v0.8.1**

> **说明**: v0.8.0 为基础图表框架版本，Chart.js 集成已完成，API 已预留进度数据结构。实际曲线展示（计划曲线、实际曲线）及时间段过滤功能将在 v0.8.1/v0.8.2 中实现。

### 6.3 ISSUE-001 修复

- [x] 项目选择框宽度固定为 200px ✅ v0.8.0

---

## 7. 测试计划

### 7.1 API 测试

| 测试项 | 测试方法 |
|--------|----------|
| 创建项目带日期 | POST /api/projects |
| 创建项目不带日期 | POST /api/projects |
| 更新项目日期 | PUT /api/projects/<id> |
| 日期校验（开始 > 结束） | 应返回错误 |
| 获取项目含日期 | GET /api/projects/<id> |
| 获取进度数据 | GET /api/progress/<id> |
| 时间段过滤 | GET /api/progress/<id>?start_date=xxx&end_date=xxx |

### 7.2 前端测试

| 测试项 | 测试方法 |
|--------|----------|
| Tab 切换到 Progress Charts | 手动测试 |
| 项目选择器选择项目 | 手动测试 |
| Chart.js 加载 | 手动测试 |
| 时间段选择器生效 | 手动测试 |
| 空项目显示提示 | 手动测试 |
| 创建项目日期输入 | 手动测试 |
| 编辑项目日期修改 | 手动测试 |
| ISSUE-001 宽度修复 | 手动测试 |

---

## 8. 工作量分解

| 任务 | 预估时间 | 状态 |
|------|----------|------|
| 数据库：添加 start_date, end_date 字段 | 0.5h | ⏳ |
| models.py: 添加字段定义 | 0.5h | ⏳ |
| API: 创建/更新项目支持日期 | 1h | ⏳ |
| API: 进度数据接口 | 1h | ⏳ |
| 前端：创建项目对话框日期选择器 | 1h | ⏳ |
| 前端：项目列表显示日期 | 0.5h | ⏳ |
| 前端：编辑项目对话框日期字段 | 0.5h | ⏳ |
| 前端：Progress Charts Tab | 1h | ⏳ |
| 前端：Chart.js 集成 | 1h | ⏳ |
| 前端：时间段选择器 | 0.5h | ⏳ |
| 前端：ISSUE-001 宽度修复 | 0.5h | ⏳ |
| 测试验证 | 1.5h | ⏳ |
| **总计** | **9.5h** | |

---

## 9. 依赖

### 9.1 前端依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Chart.js | v4.x | 图表渲染 |

### 9.2 后端依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Flask | - | Web 框架 |
| SQLite | - | 数据库 |

---

## 10. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Chart.js CDN 访问不稳定 | 图表无法加载 | 考虑本地化或备选 CDN |
| 现有项目日期为空 | Progress Charts 无数据 | 显示友好提示 |

---

**文档版本**: v1.0  
**最后更新**: 2026-03-01  
**维护者**: 小栗子 🌰
