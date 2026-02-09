# Tracker v0.6.1 第二阶段规格书

> **版本**: v0.6.1 | **创建日期**: 2026-02-09 | **状态**: 待开发

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
| **v0.6.1** | **Status 粗体、CP 过滤、备份路径** | **待开发** |
| v0.6.2 | CP 详情下拉、TC 过滤 | 计划中 |

---

## 2. 需求清单

| # | 功能 | 优先级 | 预估时间 | 状态 |
|---|------|--------|----------|------|
| #1 | Status 颜色粗体显示 | P0 | 1h | 待开发 |
| #9 | CP 过滤功能 | P0 | 6h | 待开发 |
| FEAT-002 | 备份恢复自定义路径 | P1 | 4h | 待开发 |

---

## 3. 需求详情

### 需求 1: Status 颜色粗体显示

#### 3.1 功能概述

**功能名称**: Test Case Status 颜色加粗

**背景/原因**:
- v0.6.0 已实现 Status 颜色显示
- 用户反馈颜色不够醒目，需要加粗显示

#### 3.2 实现方案

修改 `index.html` 中的 CSS 样式：

```css
/* 当前样式 */
.status-open { color: #6b7280; }
.status-coded { color: #3b82f6; }
.status-fail { color: #ef4444; }
.status-pass { color: #22c55e; }
.status-removed { color: #9ca3af; text-decoration: line-through; }

/* v0.6.1 样式 - 加粗 */
.status-open { color: #6b7280; font-weight: 600; }
.status-coded { color: #3b82f6; font-weight: 600; }
.status-fail { color: #ef4444; font-weight: 600; }
.status-pass { color: #22c55e; font-weight: 600; }
.status-removed { color: #9ca3af; font-weight: 600; text-decoration: line-through; }
```

#### 3.3 验收标准

- [ ] OPEN 状态显示灰色粗体
- [ ] CODED 状态显示蓝色粗体
- [ ] FAIL 状态显示红色粗体
- [ ] PASS 状态显示绿色粗体
- [ ] REMOVED 状态显示灰色粗体删除线

---

### 需求 9: CP 过滤功能

#### 3.4 功能概述

**功能名称**: Cover Point 过滤功能

**背景/原因**:
- 当前 CP 页面过滤功能有限
- 需要支持 Feature 和 Priority 过滤

#### 3.5 功能详情

##### 3.5.1 支持过滤的字段

| 字段 | 过滤类型 |
|------|----------|
| Feature | 下拉多选 |
| Priority | 下拉多选 |

##### 3.5.2 界面描述

**过滤器面板**:
```
过滤条件:
[Feature ▼]    [Priority ▼]

[应用过滤] [重置]
```

##### 3.5.3 API 修改

`GET /api/cp` 增加过滤参数：

| 参数 | 类型 | 说明 |
|------|------|------|
| `feature` | string | Feature 名称（支持多值，逗号分隔） |
| `priority` | string | Priority (P0/P1/P2，支持多值） |

**请求示例**:
```
GET /api/cp?project_id=1&feature=FeatureA,FeatureB&priority=P0,P1
```

**SQL 查询逻辑**:
```python
query = 'SELECT * FROM cover_point WHERE 1=1'
params = []

if feature_filter:
    placeholders = ','.join(['?'] * len(features))
    query += f' AND feature IN ({placeholders})'
    params.extend(features)

if priority_filter:
    placeholders = ','.join(['?'] * len(priorities))
    query += f' AND priority IN ({placeholders})'
    params.extend(priorities)
```

#### 3.6 验收标准

- [ ] 支持按 Feature 过滤
- [ ] 支持按 Priority 过滤
- [ ] 支持组合过滤
- [ ] 支持重置过滤条件

---

### FEAT-002: 备份恢复自定义路径

#### 3.7 功能概述

**功能名称**: 备份恢复自定义文件路径

**背景/原因**:
- 当前备份恢复功能只能搜索默认 `archives/` 目录
- 用户无法选择其他位置的备份文件

#### 3.8 功能详情

##### 3.8.1 界面修改

**恢复弹窗增加**:
- "选择文件" 按钮
- 文件选择对话框（JSON 文件）

##### 3.8.2 新增 API

`POST /api/projects/restore/upload` - 上传备份文件恢复

**请求**: `multipart/form-data`
```
file: [JSON 文件]
```

**响应**:
```json
{
  "success": true,
  "project": {
    "id": 1,
    "name": "Restored_Project"
  }
}
```

##### 3.8.3 保留功能

保留现有 `POST /api/projects/restore` 按文件名恢复的功能

#### 3.9 验收标准

- [ ] 恢复弹窗显示"选择文件"按钮
- [ ] 支持本地 JSON 文件选择
- [ ] 上传后自动恢复项目
- [ ] 保留按文件名恢复的方式

---

## 4. API 接口

### 4.1 CP 过滤 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/cp?project_id=1&feature=...&priority=...` | 获取 CP 列表（支持过滤） |

### 4.2 备份恢复 API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/projects/restore` | 按文件名恢复 |
| POST | `/api/projects/restore/upload` | 上传文件恢复 |

---

## 5. 验收标准清单

### 需求 1: Status 粗体
- [ ] OPEN 灰色粗体
- [ ] CODED 蓝色粗体
- [ ] FAIL 红色粗体
- [ ] PASS 绿色粗体
- [ ] REMOVED 灰色粗体删除线

### 需求 9: CP 过滤
- [ ] Feature 过滤
- [ ] Priority 过滤
- [ ] 组合过滤
- [ ] 重置功能

### FEAT-002: 备份路径
- [ ] 选择文件按钮
- [ ] 文件上传恢复
- [ ] 保留文件名恢复

---

## 6. 预估工作量

| 需求 | 任务 | 时间 |
|------|------|------|
| #1 | CSS 样式修改 | 1h |
| #9 | 后端过滤 API | 2h |
| #9 | 前端过滤 UI | 3h |
| #9 | 测试验证 | 1h |
| FEAT-002 | 上传 API | 2h |
| FEAT-002 | 前端上传 UI | 1.5h |
| FEAT-002 | 测试验证 | 0.5h |
| **总计** | | **11h** |

---

## 7. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.6.1 | 2026-02-09 | 创建规格书 |
