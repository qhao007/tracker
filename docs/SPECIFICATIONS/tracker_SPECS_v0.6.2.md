# Tracker v0.6.2 详细规格

> **版本**: v0.6.2 | **更新日期**: 2026-02-11 | **状态**: ✅ 已完成

---

## 目录

1. [需求清单](#1-需求清单)
2. [需求 7: CP 详情下拉](#2-需求-7-cp-详情下拉)
3. [需求 8: TC 过滤](#3-需求-8-tc-过滤)
4. [API 接口](#4-api-接口)
5. [Bug 修复](#5-bug-修复)
6. [验收标准](#6-验收标准)

---

## 1. 需求清单

| # | 功能 | 优先级 | 状态 |
|---|------|--------|------|
| #7 | CP 详情下拉 | P0 | ✅ 完成 |
| #8 | TC 过滤 | P0 | ✅ 完成 |

---

## 2. 需求 7: CP 详情下拉

### 2.1 功能概述

点击 CP 行的"详情"按钮，展开查看完整信息和关联 TC 列表。

### 2.2 界面行为

| 行为 | 说明 |
|------|------|
| 点击"详情"按钮 | 展开详情面板 |
| 再次点击 | 收起详情面板 |
| 按钮文字 | "详情" ↔ "收起详情" |

### 2.3 详情内容

| 字段 | 说明 |
|------|------|
| cover_point_details | 详细信息 |
| comments | 附加评论 |
| 关联 TC 列表 | ID / Test Name / Status |

### 2.4 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/cp/{id}/tcs` | 获取关联 TC 列表 |

**响应示例**:
```json
{
  "cp_id": 1,
  "connected_tcs": [
    {"id": 10, "test_name": "TC_复位测试", "status": "PASS"}
  ]
}
```

### 2.5 验收标准

- [x] 操作栏显示"详情"按钮
- [x] 点击展开详情面板
- [x] 显示 cover_point_details 和 comments
- [x] 显示关联 TC 列表
- [x] 再次点击收起
- [x] 按钮文字切换

---

## 3. 需求 8: TC 过滤

### 3.1 功能概述

在 TC 列表上方显示过滤面板，支持多字段过滤。

### 3.2 支持的过滤字段

| 字段 | 类型 | 说明 |
|------|------|------|
| Status | 单选 | OPEN/CODED/FAIL/PASS/REMOVED |
| DV Milestone | 单选 | DV1.0/DV2.0... |
| Owner | 单选 | 动态填充 |
| Category | 单选 | 动态填充 |

### 3.3 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/tc?project_id=1&status=PASS&dv_milestone=DV1.0` | 过滤 TC |

### 3.4 验收标准

- [x] 过滤面板显示在 TC 列表上方
- [x] Status 单选过滤
- [x] DV Milestone 单选过滤
- [x] Owner 动态过滤
- [x] Category 动态过滤
- [x] 显示过滤后记录数量
- [x] 支持重置过滤

---

## 4. API 接口

### 4.1 Cover Points API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/cp?project_id=1&feature=...&priority=...` | CP 列表（支持过滤） |
| GET | `/api/cp/{id}` | CP 详情 |
| **GET** | **`/api/cp/{id}/tcs`** | **关联 TC 列表（新增）** |
| POST | `/api/cp` | 创建 CP |
| PUT | `/api/cp/{id}` | 更新 CP |
| DELETE | `/api/cp/{id}` | 删除 CP |

### 4.2 Test Cases API

| 方法 | 路径 | 功能 |
|------|------|------|
| **GET** | **`/api/tc?project_id=1&status=...`** | **TC 列表（支持过滤）** |
| GET | `/api/tc/{id}` | TC 详情 |
| POST | `/api/tc` | 创建 TC |
| PUT | `/api/tc/{id}` | 更新 TC |
| DELETE | `/api/tc/{id}` | 删除 TC |
| POST | `/api/tc/{id}/status` | 更新状态 |
| POST | `/api/tc/batch/status` | 批量更新状态 |

### 4.3 TC 过滤参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `project_id` | int | 项目 ID（必填） |
| `status` | string | Status 过滤 |
| `dv_milestone` | string | DV Milestone 过滤 |
| `owner` | string | Owner 过滤 |
| `category` | string | Category 过滤 |

---

## 5. Bug 修复

### 5.1 v0.6.2 Bug 汇总

| Bug ID | 问题 | 修复内容 |
|--------|------|----------|
| BUG-027 | 展开所有 CP 详情时 TC 数据不加载 | 添加 loadCPTcConnections() 调用 |
| BUG-028 | TC 过滤重置后列表不刷新 | 末尾添加 renderTC() |
| BUG-029 | TC 过滤重置代码无效 | 删除无效代码 |
| BUG-030 | CP 详情关联 TC 显示错误 | API 添加 project_id 参数 |
| BUG-031 | TC Priority 过滤不需要 | 移除 Priority 过滤 |
| BUG-032 | Owner/Category 过滤选项不动态加载 | 添加 loadTCFilterOptions() |
| BUG-033 | Status/DV Milestone 需要单选 | 多选改为单选 |
| BUG-034 | Status/DV Milestone 缺少全部选项 | 添加"全部"选项 |
| BUG-035 | DV Milestone 过滤选项不动态加载 | 动态加载选项 |
| BUG-036 | projectSelector ID 拼写错误 | projectSelect → projectSelector |
| BUG-037 | TC 列表 API 读取不存在的 priority 字段 | 移除 priority 字段 |
| BUG-038 | toggleTCDetails 函数未定义 | 统一函数命名 |
| BUG-039 | getElementById 缺少前缀 | 添加 'tc-details-' 前缀 |
| BUG-040 | TC 详情缺少 Scenario 字段 | 添加 scenario_details 显示 |

---

## 6. 验收标准清单

### 需求 7: CP 详情下拉

- [x] 操作栏显示"详情"按钮
- [x] 点击详情按钮展开详情面板
- [x] 详情面板显示 cover_point_details
- [x] 详情面板显示 comments
- [x] 详情面板显示关联 TC 列表
- [x] 关联 TC 列表只显示 ID/Test Name/Status
- [x] 再次点击收起详情
- [x] 按钮文字切换
- [x] API GET /api/cp/{id}/tcs 正常返回

### 需求 8: TC 过滤

- [x] 过滤面板显示在 TC 列表上方
- [x] Status 单选过滤
- [x] DV Milestone 单选过滤
- [x] Owner 过滤（动态填充选项）
- [x] Category 过滤（动态填充选项）
- [x] 支持组合过滤
- [x] 显示过滤后记录数量
- [x] 支持重置过滤条件
- [x] API GET /api/tc 支持所有过滤参数

---

**相关文档**:
- 总体规格: `SPECIFICATIONS/tracker_OVERALL_SPECS.md`
- Bug 追踪: `../BUGLOG/tracker_BUG_RECORD.md`
