# Tracker v0.6.2 第三阶段规格书

> **版本**: v0.6.2 | **创建日期**: 2026-02-10 | **状态**: ✅ 已完成

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

v0.6.1 发布后，继续增强以下功能：
1. CP 详情下拉 - 点击详情按钮查看 CP 完整信息和关联 TC
2. TC 过滤 - 支持多字段过滤 Test Cases 列表

### 1.2 目标版本

| 版本 | 功能 | 状态 |
|------|------|------|
| v0.6.0 | 批量修改、DV Milestone、CP Priority 等 | ✅ 已发布 |
| v0.6.1 | Status 粗体、CP 过滤、备份路径 | ✅ 已发布 |
| **v0.6.2** | **CP 详情下拉、TC 过滤** | **开发中** |

### 1.3 需求清单

| # | 功能 | 优先级 | 预估时间 | 状态 |
|---|------|--------|----------|------|
| #7 | CP 详情下拉 | P0 | 4h | ✅ 已完成 |
| #8 | TC 过滤 | P0 | 8h | ✅ 已完成 |

---

## 2. 需求详情

### 2.1 需求 7: CP 详情下拉

#### 2.1.1 功能概述

**功能名称**: Cover Point 详情展开

**背景/原因**:
- 当前 CP 列表只显示有限字段
- 用户需要查看 CP 的完整信息（备注、关联 TC 等）
- 需要支持展开/收起详情

#### 2.1.2 功能详情

##### 2.1.2.1 界面行为

| 行为 | 说明 |
|------|------|
| 点击详情按钮 | 展开/收起 CP 详情（按钮位于操作栏） |
| 详情内容 | 显示 CP 备注信息 + 关联 TC 列表 |

##### 2.1.2.2 详情内容

**只显示 CP 列表中没有的字段：**

| 字段 | 说明 |
|------|------|
| cover_point_details | 详细信息（备注、说明等） |
| comments | 附加评论 |

**不重复显示的字段**（已在列表中显示）：
- id, testbench, block, feature, priority, status, owner, coverage

##### 2.1.2.3 关联 TC 列表

只显示以下三个字段：

```
┌─────────────────────────────────────────┐
│ ID  │ Test Name │ Status              │
├─────┼───────────┼─────────────────────┤
│ TC1 │ TC_Name1  │ PASS                │
│ TC2 │ TC_Name2  │ CODED               │
└─────────────────────────────────────────┘
```

#### 2.1.3 实现方案

**前端实现**:
- 操作栏添加"详情"按钮
- 点击展开详情面板
- 异步加载关联 TC 列表

**后端 API**:
- `GET /api/cp/{id}/tcs` - 获取 CP 关联的 TC 列表

#### 2.1.4 验收标准

- [x] 操作栏显示"详情"按钮
- [x] 点击详情按钮展开详情面板
- [x] 详情面板显示 cover_point_details 字段
- [x] 详情面板显示 comments 字段
- [x] 详情面板显示关联 TC 列表
- [x] 关联 TC 列表只显示 ID、Test Name、Status
- [x] 再次点击收起详情
- [x] 按钮文字切换为"收起详情"/"详情"
- [x] API `GET /api/cp/{id}/tcs` 返回关联 TC 列表（只含 ID, test_name, status）

---

### 2.2 需求 8: TC 过滤

#### 2.2.1 功能概述

**功能名称**: Test Cases 多字段过滤

**背景/原因**:
- 当前 TC 列表缺少过滤功能
- 用户需要按 Status、DV Milestone、Priority 等字段过滤
- 需要支持多字段组合过滤

#### 2.2.2 功能详情

##### 2.2.2.1 支持过滤的字段

| 字段 | 过滤类型 | 选项 |
|------|----------|------|
| Status | 下拉多选 | OPEN, CODED, FAIL, PASS, REMOVED |
| DV Milestone | 下拉多选 | DV1.0, DV2.0, DV3.0, DV4.0, DV5.0 |
| Priority | 下拉单选 | P0, P1, P2 |
| Owner | 下拉单选 | 所有 Owner（动态填充） |
| Category | 下拉单选 | 所有 Category（动态填充） |

##### 2.2.2.2 过滤逻辑

```
过滤规则:
- 多选字段: OR 逻辑 (例: Status=PASS OR CODED)
- 多字段组合: AND 逻辑 (例: Status=PASS AND DV Milestone=DV1.0)
- 无选择: 显示所有
```

##### 2.2.2.3 API 修改

`GET /api/tc` 增加过滤参数：

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `project_id` | int | 项目 ID（必填） | `?project_id=1` |
| `status` | string | Status 过滤（多值，逗号分隔） | `?status=PASS,CODED` |
| `dv_milestone` | string | DV Milestone 过滤（多值） | `?dv_milestone=DV1.0,DV2.0` |
| `priority` | string | Priority 过滤（多值） | `?priority=P0,P1` |
| `owner` | string | Owner 过滤 | `?owner=TestEng1` |
| `category` | string | Category 过滤 | `?category=Sanity` |

**请求示例**:
```
# 获取所有 TC
GET /api/tc?project_id=1

# 按 Status 过滤
GET /api/tc?project_id=1&status=PASS,CODED

# 组合过滤
GET /api/tc?project_id=1&status=PASS&dv_milestone=DV1.0&priority=P0
```

#### 2.2.3 界面设计

##### 2.2.3.1 过滤面板

- 显示在 TC 列表上方
- 包含 Status、DV Milestone、Priority、Owner、Category 下拉框
- 支持多选过滤
- 显示过滤后的记录数量（格式：显示 X/Y 条）
- 重置按钮

#### 2.2.4 验收标准

- [x] 过滤面板显示在 TC 列表上方
- [x] 支持 Status 多选过滤
- [x] 支持 DV Milestone 多选过滤
- [x] 支持 Priority 单选过滤
- [x] 支持 Owner 过滤（动态填充选项）
- [x] 支持 Category 过滤（动态填充选项）
- [x] 支持组合过滤
- [x] 显示过滤后的记录数量
- [x] 支持重置过滤条件
- [x] API `GET /api/tc` 支持所有过滤参数

---

## 3. API 接口

### 3.1 Cover Points API

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/cp?project_id=1&feature=...&priority=...` | 获取 CP 列表（支持过滤） | ✅ 已实现 |
| GET | `/api/cp/{id}` | 获取 CP 详情 | ✅ 已实现 |
| **GET** | **`/api/cp/{id}/tcs`** | **获取 CP 关联的 TC 列表（v0.6.2）** | ✅ 已实现 |
| POST | `/api/cp` | 创建 CP | ✅ 已实现 |
| PUT | `/api/cp/{id}` | 更新 CP | ✅ 已实现 |
| DELETE | `/api/cp/{id}` | 删除 CP | ✅ 已实现 |
| POST | `/api/cp/batch/priority` | 批量更新 Priority | ✅ 已实现 |

### 3.2 Test Cases API

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| **GET** | **`/api/tc?project_id=1&status=...&dv_milestone=...`** | **获取 TC 列表（支持过滤，v0.6.2）** | ✅ 已实现 |
| GET | `/api/tc/{id}` | 获取 TC 详情 | ✅ 已实现 |
| POST | `/api/tc` | 创建 TC | ✅ 已实现 |
| PUT | `/api/tc/{id}` | 更新 TC | ✅ 已实现 |
| DELETE | `/api/tc/{id}` | 删除 TC | ✅ 已实现 |
| POST | `/api/tc/{id}/status` | 更新状态 | ✅ 已实现 |
| POST | `/api/tc/batch/status` | 批量更新状态 | ✅ 已实现 |
| POST | `/api/tc/batch/target_date` | 批量修改 Target Date | ✅ 已实现 |
| POST | `/api/tc/batch/dv_milestone` | 批量修改 DV Milestone | ✅ 已实现 |

### 3.3 API 响应示例

#### 3.3.1 CP 关联 TC 列表

**GET** `/api/cp/{id}/tcs`

```json
{
  "cp_id": 1,
  "connected_tcs": [
    {
      "id": 10,
      "test_name": "TC_复位测试_001",
      "status": "PASS"
    },
    {
      "id": 15,
      "test_name": "TC_时钟测试_002",
      "status": "CODED"
    }
  ]
}
```

#### 3.3.2 TC 列表（支持过滤）

**GET** `/api/tc?project_id=1&status=PASS,CODED&dv_milestone=DV1.0`

```json
[
  {
    "id": 10,
    "project_id": 1,
    "dv_milestone": "DV1.0",
    "testbench": "TB01",
    "category": "Sanity",
    "priority": "P0",
    "owner": "TestEng1",
    "test_name": "TC_复位测试_001",
    "status": "PASS",
    "target_date": "2026-02-15",
    "connected_cps": [1, 2]
  }
]
```

---

## 4. 界面设计

### 4.1 CP 详情按钮和展开

```
┌─────────────────────────────────────────────────────────────────────┐
│ Cover Points                  [+ 添加 CP] [📊 导出] [💾] [详情 ▼]    │
├─────────────────────────────────────────────────────────────────────┤
│  ID  │ TestBench │ Block │ Feature │ Priority │ Coverage │ 操作    │
├──────┼───────────┼───────┼─────────┼──────────┼──────────┼─────────┤
│  1   │   TB01    │  CPU  │ FeatureA │    P0    │   100%   │ [详情]  │
├──────┼───────────┼───────┼─────────┼──────────┼──────────┼─────────┤
│                                                                    │
│  Cover Point 详细信息: CPU 复位功能覆盖率                            │
│  Comments: 需要补充更多的边界条件测试                                │
│                                                                    │
│  关联的 Test Cases:                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ID      │ Test Name                    │ Status            │   │
│  ├─────────┼──────────────────────────────┼───────────────────┤   │
│  │ TC_001  │ TC_复位测试_001              │ PASS              │   │
│  │ TC_002  │ TC_时钟测试_002              │ CODED             │   │
│  └─────────────────────────────────────────────────────────────┘   │
├──────┼───────────┼───────┼─────────┼──────────┼──────────┼─────────┤
│  2   │   TB02    │  CPU  │ FeatureB │    P1    │    50%   │ [详情]  │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 TC 过滤面板

```
┌─────────────────────────────────────────────────────────────┐
│ Test Cases                      [+ 添加 TC]  [📊 导出]     │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [DV Milestone ▼]  [Status ▼]  [Priority ▼]  [Owner ▼] │ │
│ │ 显示 8/15 条                                             │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ID  │ TestBench │ Category │ Priority │ Status │ Target  │
├──────┼───────────┼──────────┼──────────┼────────┼─────────┤
│  1   │   TB01    │  Sanity  │    P0    │  PASS  │02-15   │
│  2   │   TB02    │ Feature  │    P0    │  CODED │02-20   │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 验收标准清单

### 需求 7: CP 详情下拉

- [x] 操作栏显示"详情"按钮（位于 [+ 添加 CP] [📊 导出] [💾] 右侧）
- [x] 点击详情按钮展开详情面板
- [x] 详情面板显示 cover_point_details 字段
- [x] 详情面板显示 comments 字段
- [x] 详情面板显示关联 TC 列表
- [x] 关联 TC 列表只显示 ID、Test Name、Status
- [x] 再次点击收起详情
- [x] 按钮文字切换为"收起详情"/"详情"
- [x] API `GET /api/cp/{id}/tcs` 返回关联 TC 列表（只含 ID, test_name, status）
- [x] **BUG-027 修复**: 展开所有 CP 详情时正确加载 TC 数据
- [x] **BUG-030 修复**: CP 详情关联 TC 显示错误（API 传递 project_id 参数）
- [x] **BUG-036 修复**: projectSelector ID 拼写错误导致加载失败

### 需求 8: TC 过滤

- [x] 过滤面板显示在 TC 列表上方
- [x] 支持 Status 单选过滤（多选改为单选，体验更好）
- [x] 支持 DV Milestone 单选过滤（多选改为单选）
- [x] ~~支持 Priority 单选过滤~~（TC 没有 priority 字段，已移除）
- [x] 支持 Owner 过滤（动态填充选项）
- [x] 支持 Category 过滤（动态填充选项）
- [x] 支持组合过滤
- [x] 显示过滤后的记录数量
- [x] 支持重置过滤条件
- [x] API `GET /api/tc` 支持所有过滤参数
- [x] **BUG-031 修复**: 移除 TC Priority 过滤选项
- [x] **BUG-032 修复**: Owner/Category 过滤选项动态加载
- [x] **BUG-033 修复**: Status/DV Milestone 改为单选下拉框
- [x] **BUG-034 修复**: Status/DV Milestone 添加"全部"选项
- [x] **BUG-035 修复**: DV Milestone 过滤选项动态加载

---

## 6. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.6.2 | 2026-02-10 | 创建第三阶段规格书 |
| v0.6.2 | 2026-02-10 | 去掉动画效果；按钮移至操作栏；简化详情内容 |
| v0.6.2 | 2026-02-10 | #7 CP 详情下拉功能完成 |
| v0.6.2 | 2026-02-10 | #8 TC 过滤功能完成 |
| **v0.6.2** | **2026-02-10** | **#7 #8 功能完成，BUG-027~036 全部修复** |
