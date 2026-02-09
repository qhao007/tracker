# Tracker v0.6.1 第二阶段规格书

> **版本**: v0.6.1 | **创建日期**: 2026-02-09 | **状态**: 开发中

---

## 目录

1. [需求概述](#1-需求概述)
2. [需求详情](#2-需求详情)
3. [API 接口](#3-api-接口)
4. [界面设计](#4-界面设计)
5. [验收标准](#5-验收标准)

---

## 1. 需求概述

### 1.1 背景

v0.6.0 发布后，根据用户反馈，需要增强以下功能：
1. Status 颜色改为粗体显示，更醒目
2. CP 过滤功能
3. 备份恢复支持自定义路径

### 1.2 目标版本

| 版本 | 功能 | 状态 |
|------|------|------|
| v0.6.0 | 批量修改、DV Milestone、CP Priority 等 | ✅ 已发布 |
| **v0.6.1** | **Status 粗体、CP 过滤、备份路径** | **开发中** |
| v0.6.2 | CP 详情下拉、TC 过滤 | 计划中 |

### 1.3 需求清单

| # | 功能 | 优先级 | 预估时间 | 状态 |
|---|------|--------|----------|------|
| #1 | Status 颜色粗体显示 | P0 | 1h | ✅ 完成 |
| #9 | CP 过滤功能 | P0 | 6h | ✅ 完成 |
| FEAT-002 | 备份恢复自定义路径 | P1 | 4h | ✅ 完成 |

---

## 2. 需求详情

### 2.1 需求 1: Status 颜色粗体显示

#### 2.1.1 功能概述

**功能名称**: Test Case Status 颜色加粗

**背景/原因**:
- v0.6.0 已实现 Status 颜色显示
- 用户反馈颜色不够醒目，需要加粗显示

#### 2.1.2 实现方案

修改 `index.html` 中的 CSS 样式：

```css
/* v0.6.1 样式 - 加粗 */
.status-OPEN { background: #e3f2fd; color: #1976d2; font-weight: 600; }
.status-CODED { background: #fff3e0; color: #f57c00; font-weight: 600; }
.status-FAIL { background: #ffebee; color: #d32f2f; font-weight: 600; }
.status-PASS { background: #e8f5e9; color: #388e3c; font-weight: 600; }
.status-REMOVED { background: #f5f5f5; color: #9e9e9e; font-weight: 600; text-decoration: line-through; }
```

#### 2.1.3 验收标准

- [x] OPEN 状态显示灰色粗体
- [x] CODED 状态显示蓝色粗体
- [x] FAIL 状态显示红色粗体
- [x] PASS 状态显示绿色粗体
- [x] REMOVED 状态显示灰色粗体删除线

---

### 2.2 需求 9: CP 过滤功能

#### 2.2.1 功能概述

**功能名称**: Cover Point 过滤功能

**背景/原因**:
- 当前 CP 页面过滤功能有限
- 需要支持 Feature 和 Priority 过滤

#### 2.2.2 功能详情

##### 2.2.2.1 支持过滤的字段

| 字段 | 过滤类型 |
|------|----------|
| Feature | 下拉多选 |
| Priority | 下拉多选 |

##### 2.2.2.2 界面描述

**过滤器面板**:
```
过滤条件:
[全部 Feature ▼]    [全部 Priority ▼]

[应用过滤] [重置]
```

##### 2.2.2.3 API 修改

`GET /api/cp` 增加过滤参数：

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `project_id` | int | 项目 ID（必填） | `?project_id=1` |
| `feature` | string | Feature 过滤（支持多值，逗号分隔） | `?feature=FeatureA,FeatureB` |
| `priority` | string | Priority 过滤（支持多值） | `?priority=P0,P1` |

**请求示例**:
```
# 获取所有 CP
GET /api/cp?project_id=1

# 按 Feature 过滤
GET /api/cp?project_id=1&feature=FeatureA

# 按 Priority 过滤
GET /api/cp?project_id=1&priority=P0

# 组合过滤
GET /api/cp?project_id=1&feature=FeatureA,FeatureB&priority=P0,P1
```

**SQL 查询逻辑**:
```python
query = 'SELECT * FROM cover_point WHERE 1=1'
params = []

if feature_filter:
    features = [f.strip() for f in feature_filter.split(',')]
    placeholders = ','.join(['?'] * len(features))
    query += f' AND feature IN ({placeholders})'
    params.extend(features)

if priority_filter:
    priorities = [p.strip() for p in priority_filter.split(',')]
    placeholders = ','.join(['?'] * len(priorities))
    query += f' AND priority IN ({placeholders})'
    params.extend(priorities)
```

#### 2.2.3 验收标准

- [x] 支持按 Feature 过滤
- [x] 支持按 Priority 过滤
- [x] 支持组合过滤
- [x] 支持重置过滤条件
- [x] Feature 下拉框自动填充当前项目的 Feature 选项

---

### 2.3 FEAT-002: 备份恢复自定义路径

#### 2.3.1 功能概述

**功能名称**: 备份恢复自定义文件路径

**背景/原因**:
- 当前备份恢复功能只能搜索默认 `archives/` 目录
- 用户无法选择其他位置的备份文件

#### 2.3.2 功能详情

##### 2.3.2.1 界面修改

**恢复弹窗增加**:
- "选择文件" 按钮（`<input type="file">`）
- 文件选择对话框（只接受 JSON 文件）
- "上传恢复" 按钮

##### 2.3.2.2 新增 API

`POST /api/projects/restore/upload` - 上传备份文件恢复

**请求**: `multipart/form-data`
```
POST /api/projects/restore/upload
Content-Type: multipart/form-data

Body: file=@backup.json
```

**请求参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | file | JSON 格式的备份文件 |

**成功响应**:
```json
{
  "success": true,
  "project": {
    "id": 10,
    "name": "Restored_Project",
    "created_at": "2026-02-09 12:00:00"
  }
}
```

**错误响应**:
```json
{
  "error": "项目 \"xxx\" 已存在，无法恢复"
}
```

##### 2.3.2.3 保留功能

保留现有 `POST /api/projects/restore` 按文件名恢复的功能。

#### 2.3.3 验收标准

- [x] 恢复弹窗显示"选择文件"按钮
- [x] 支持本地 JSON 文件选择
- [x] 上传后自动恢复项目
- [x] 保留按文件名恢复的方式

---

## 3. API 接口

### 3.1 Cover Points API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/cp?project_id=1&feature=...&priority=...` | 获取 CP 列表（支持过滤） |
| GET | `/api/cp/{id}` | 获取 CP 详情（需 project_id） |
| POST | `/api/cp` | 创建 CP |
| PUT | `/api/cp/{id}` | 更新 CP（需 project_id） |
| DELETE | `/api/cp/{id}` | 删除 CP（需 project_id） |
| POST | `/api/cp/batch/priority` | 批量更新 Priority（需 project_id） |

### 3.2 备份恢复 API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/projects/{id}/archive` | 备份项目 |
| GET | `/api/projects/archive/list` | 获取归档列表 |
| POST | `/api/projects/restore` | 按文件名恢复 |
| **POST** | **`/api/projects/restore/upload`** | **上传文件恢复（v0.6.1）** |
| DELETE | `/api/projects/{id}` | 删除项目 |

---

## 4. 界面设计

### 4.1 CP 过滤下拉框

```html
<!-- Feature 过滤下拉框 -->
<select id="cpFeatureFilter" onchange="filterCPByFeature()">
  <option value="">全部 Feature</option>
  <!-- 自动填充 -->
</select>

<!-- Priority 过滤下拉框 -->
<select id="cpPriorityFilter" onchange="filterCPByPriority()">
  <option value="">全部 Priority</option>
  <option value="P0">P0</option>
  <option value="P1">P1</option>
  <option value="P2">P2</option>
</select>
```

### 4.2 备份恢复弹窗

```html
<div class="form-group">
  <label>从备份恢复</label>
  <div style="display: flex; gap: 10px; margin-bottom: 10px;">
    <input type="file" id="restoreFile" accept=".json" style="flex: 1;">
    <button class="btn" onclick="uploadAndRestore()">上传恢复</button>
  </div>
  <div id="uploadStatus"></div>
</div>
```

---

## 5. 验收标准清单

### 需求 1: Status 粗体
- [x] OPEN 状态显示灰色粗体
- [x] CODED 状态显示蓝色粗体
- [x] FAIL 状态显示红色粗体
- [x] PASS 状态显示绿色粗体
- [x] REMOVED 状态显示灰色粗体删除线

### 需求 9: CP 过滤
- [x] Feature 过滤
- [x] Priority 过滤
- [x] 组合过滤
- [x] 重置功能
- [x] Feature 下拉框自动填充

### FEAT-002: 备份路径
- [x] 选择文件按钮
- [x] 文件上传恢复
- [x] 保留文件名恢复

---

## 6. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.6.1 | 2026-02-09 | 创建规格书 |
