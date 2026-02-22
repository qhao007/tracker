# Tracker v0.7.0 详细规格

> **版本**: v0.7.0 | **更新日期**: 2026-02-16 | **状态**: 🔄 开发中

---

## 目录

1. [需求清单](#1-需求清单)
2. [需求 10: 导入功能](#2-需求-10-导入功能)
3. [需求 11: 导出功能](#3-需求-11-导出功能)
4. [ISSUE-001 修复](#4-issue-001-修复)
5. [TS 类型修复](#5-ts-类型修复)
6. [API 接口](#6-api-接口)
7. [验收标准](#7-验收标准)

---

## 1. 需求清单

| # | 功能 | 优先级 | 预估时间 | 状态 |
|---|------|--------|----------|------|
| #10 | 导入功能 (CP/TC) | P1 | 20h | 🔄 开发中 |
| #11 | 导出功能 (CP/TC) | P1 | 13h | 🔄 开发中 |
| #ISSUE-001 | 项目选择框宽度修复 | P3 | 0.5h | ✅ 已完成 |
| - | TS 类型修复 | Tech Debt | - | ✅ 主代码已完成 |

**总预估时间**: 33.5h (~5天)

---

## 2. 需求 10: 导入功能

### 2.1 功能概述

支持从 Excel (.xlsx) 或 CSV 文件批量导入 Cover Points 和 Test Cases，减少手动录入工作量。

### 2.2 界面设计

#### 2.2.1 按钮位置

| 页面 | 工具栏位置 |
|------|------------|
| CP 页面 | 右侧 [+ 添加 CP] 旁边 |
| TC 页面 | 右侧 [+ 添加 TC] 旁边 |

#### 2.2.2 按钮文字

- CP 导入按钮: `[导入 CP]`
- TC 导入按钮: `[导入 TC]`

#### 2.2.3 导入对话框

```
+------------------------------------------+
|  导入 Cover Points                       |
+------------------------------------------+
|  [选择文件] 未选择任何文件                  |
|  支持格式: .xlsx, .csv                    |
|                                          |
|  [下载导入模板]                           |
+------------------------------------------+
|              [取消]  [导入]               |
+------------------------------------------+
```

### 2.3 导入模板字段

#### CP 导入模板

| Excel 列名 | 数据库字段 | 必填 | 说明 |
|------------|------------|------|------|
| Feature | feature | ✅ | 功能领域 |
| Sub-Feature | sub_feature | - | 子功能 |
| Cover Point | cover_point | ✅ | 覆盖点 |
| Cover Point Details | cover_point_details | - | 详细描述 |
| Comments | comments | - | 备注 |

#### TC 导入模板

| Excel 列名 | 数据库字段 | 必填 | 说明 |
|------------|------------|------|------|
| TestBench | testbench | ✅ | 测试台 |
| Category | category | - | 类别 |
| Owner | owner | - | 负责人 |
| Test Name | test_name | ✅ | 测试名称 |
| Scenario Details | scenario_details | - | 场景详情 |
| Checker Details | checker_details | - | 检查详情 |
| Coverage Details | coverage_details | - | 覆盖率详情 |
| Comments | comments | - | 备注 |

### 2.4 操作流程

```
1. 用户点击 [导入 CP] 或 [导入 TC]
2. 弹出导入对话框
3. 用户可点击 [下载模板] 获取 Excel 模板
4. 用户点击 [选择文件] 上传 .xlsx 或 .csv
5. 系统解析文件并进行预检查:
   - 必填字段检查
   - 重名检查（同一项目内）
   - 字段格式校验
6. 如果预检查失败:
   - 显示错误信息
   - 用户可重新选择文件
7. 如果预检查通过:
   - 显示预览数据（可选）
   - 用户点击 [导入] 确认
8. 系统执行导入（事务保护）
9. 显示导入结果:
   - 成功导入数量
   - 失败数量及原因（如有）
10. 关闭对话框，刷新列表
```

### 2.5 导入校验规则

| 规则 | 说明 | 处理方式 |
|------|------|----------|
| 必填字段 | feature, cover_point (CP) / testbench, test_name (TC) | 缺失则失败 |
| 重名检查 | 同一项目内 CP.cover_point 或 TC.test_name 重复 | 跳过或询问用户 |
| 项目归属 | 导入数据关联到当前选中的项目 | 自动设置 |
| 事务保护 | 导入失败时回滚所有更改 | 原子性操作 |

### 2.6 导出模板

导出数据使用相同的字段格式，方便用户编辑后重新导入。

---

## 3. 需求 11: 导出功能

### 3.1 功能概述

将当前项目中的 Cover Points 或 Test Cases 列表导出为 Excel (.xlsx) 或 CSV 文件。

### 3.2 界面设计

#### 3.2.1 按钮位置

| 页面 | 工具栏位置 |
|------|------------|
| CP 页面 | 右侧 [导入 CP] 旁边 |
| TC 页面 | 右侧 [导入 TC] 旁边 |

#### 3.2.2 按钮文字

- CP 导出按钮: `[导出 CP]`
- TC 导出按钮: `[导出 TC]`

#### 3.2.3 导出对话框

```
+------------------------------------------+
|  导出 Cover Points                       |
+------------------------------------------+
|  导出格式:  (o) Excel (.xlsx)             |
|            ( ) CSV (.csv)                |
|                                          |
|  当前项目: TestProject                   |
|  记录数量: 45                            |
+------------------------------------------+
|              [取消]  [导出]               |
+------------------------------------------+
```

### 3.3 导出字段

#### CP 导出字段

| Excel 列名 | 数据库字段 |
|------------|------------|
| Feature | feature |
| Sub-Feature | sub_feature |
| Cover Point | cover_point |
| Cover Point Details | cover_point_details |
| Priority | priority |
| Comments | comments |
| Created At | created_at |

#### TC 导出字段

| Excel 列名 | 数据库字段 |
|------------|------------|
| ID | id |
| DV Milestone | dv_milestone |
| TestBench | testbench |
| Category | category |
| Owner | owner |
| Test Name | test_name |
| Scenario Details | scenario_details |
| Checker Details | checker_details |
| Coverage Details | coverage_details |
| Status | status |
| Comments | comments |
| Created At | created_at |
| Coded Date | coded_date |
| Fail Date | fail_date |
| Pass Date | pass_date |
| Removed Date | removed_date |
| Target Date | target_date |

### 3.4 操作流程

```
1. 用户点击 [导出 CP] 或 [导出 TC]
2. 弹出导出对话框，显示格式选项
3. 用户选择格式（默认 Excel）
4. 用户点击 [导出]
5. 系统生成文件并触发浏览器下载
6. 文件名格式: {项目名}_{CP/TC}_{日期}.xlsx
   示例: TestProject_CP_20260215.xlsx
```

### 3.5 导出范围

- 导出当前项目的全部 CP/TC
- 不受过滤器影响（导出完整列表）
- 后续版本可考虑支持过滤导出

---

## 4. ISSUE-001 修复

### 4.1 问题描述

项目选择框宽度不固定，导致不同项目名称长度时显示宽度不一致。

### 4.2 修复方案

给 `.project-selector` 添加固定宽度：

```css
.project-selector {
    width: 200px;
}
```

### 4.3 验收标准

- [ ] 项目选择框宽度固定为 200px
- [ ] 不同项目名称长度时显示宽度一致
- [ ] 界面布局不因项目名称长度而改变

---

## 5. TS 类型修复

### 5.1 修复任务清单

| # | 任务 | 错误数量 | 预估时间 |
|---|------|----------|----------|
| 1 | `npm install -D @types/node` | 5 个错误 | 5min |
| 2 | 修复 TS7006 (隐式 any) | 7 个错误 | 1h |
| 3 | 修复 TS2353 (fixture 类型) | 7 个错误 | 1h |
| 4 | 修复 TS18047 (可选链) | 4 个错误 | 30min |

### 5.2 TS7006 修复

**问题**: 缺少类型标注的隐式 any 变量

**修复方法**: 添加明确的类型标注

```typescript
// 修复前
const items = getItems();

// 修复后
const items: string[] = getItems();
```

### 5.3 TS2353 修复

**问题**: fixture 类型定义问题

**修复方法**: 检查 fixture 类型定义是否正确，可能需要添加类型守卫或调整类型

### 5.4 TS18047 修复

**问题**: 使用可选链访问可能为 undefined 的属性

**修复方法**: 添加可选链操作符

```typescript
// 修复前
const value = obj.nested.prop;

// 修复后
const value = obj?.nested?.prop;
```

---

## 6. API 接口

### 6.1 导入 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/import/template?type=cp\|tc` | 下载导入模板 |
| POST | `/api/import` | 执行导入 |

#### GET /api/import/template?type=cp

**响应**: 文件下载 (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

#### POST /api/import

**请求体**:
```json
{
  "project_id": 1,
  "type": "cp",
  "file_data": "base64编码的Excel文件内容"
}
```

**响应**:
```json
{
  "success": true,
  "imported": 10,
  "failed": 0,
  "errors": []
}
```

### 6.2 导出 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/export?project_id=1&type=cp\|tc&format=xlsx\|csv` | 导出数据 |

#### GET /api/export

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | ✅ | 项目 ID |
| type | string | ✅ | cp 或 tc |
| format | string | ✅ | xlsx 或 csv |

**响应**: 文件下载

---

## 7. 验收标准

### 7.1 导入功能

- [x] CP 页面显示 [导入 CP] 按钮
- [x] TC 页面显示 [导入 TC] 按钮
- [x] 点击按钮弹出导入对话框
- [x] 提供下载 CP 模板功能
- [x] 提供下载 TC 模板功能
- [x] 支持 Excel (.xlsx) 文件上传
- [x] 支持 CSV 文件上传
- [ ] 必填字段缺失时显示错误提示
- [x] 重名检测功能正常
- [x] 导入失败时回滚事务
- [x] 导入成功后显示成功数量
- [x] 导入成功后刷新列表

### 7.2 导出功能

- [x] CP 页面显示 [导出 CP] 按钮
- [x] TC 页面显示 [导出 TC] 按钮
- [x] 点击按钮弹出导出对话框
- [x] 支持选择 Excel 格式
- [x] 支持选择 CSV 格式
- [x] 导出的 Excel 格式正确可读
- [x] 导出的 CSV 编码正确
- [x] 文件名包含项目名和日期

### 7.3 ISSUE-001 修复

- [x] 项目选择框宽度固定为 200px
- [x] 不同项目名称长度时显示宽度一致

### 7.4 TS 类型修复

- [x] 运行 `npx tsc --noEmit` 无 @types/node 相关错误
- [x] 无 TS7006 错误 (主应用代码)
- [x] 无 TS2353 错误 (主应用代码)
- [x] 无 TS18047 错误 (主应用代码)

---

**相关文档**:
- 总体规格: `SPECIFICATIONS/tracker_OVERALL_SPECS.md`
- Bug 追踪: `../BUGLOG/tracker_BUG_RECORD.md`
- 需求来源: `/projects/management/feedbacks/reviewed/tracker_FEATURE_REQUESTS_v0.6.0_20260207.md`
