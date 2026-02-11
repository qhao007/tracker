# 芯片验证 Tracker 总体规格书

> **版本**: v0.6.2 | **更新日期**: 2026-02-11 | **状态**: ✅ 已完成

---

## 目录

1. [项目概述](#1-项目概述)
2. [功能规格](#2-功能规格)
3. [API 接口](#3-api-接口)
4. [数据库设计](#4-数据库设计)
5. [部署说明](#5-部署说明)
6. [版本历史](#6-版本历史)

---

## 1. 项目概述

### 1.1 背景

芯片验证团队需要管理 Cover Points（覆盖点）与 Test Cases（测试用例）的关联关系，跟踪验证进度和覆盖率。

### 1.2 核心功能

| 功能 | 说明 |
|------|------|
| 项目管理 | 多项目支持，独立数据库 |
| Cover Points | Feature/Sub-Feature/Priority 管理 |
| Test Cases | Status/DV Milestone/Target Date 跟踪 |
| 关联管理 | TC ↔ CP 多对多关联 |
| 统计面板 | Pass Rate / Coverage 计算 |
| 备份恢复 | 项目导出/导入 |

### 1.3 技术架构

```
前端: HTML5 + Vanilla JavaScript
后端: Python Flask
数据库: SQLite (每个项目独立 .db)
部署: systemd + gunicorn
```

### 1.4 版本演进

| 版本 | 日期 | 主要功能 |
|------|------|----------|
| v0.3 | 2026-02-04 | 代码隔离、数据共享 |
| v0.5.0 | 2026-02-06 | 界面优化、发布脚本 |
| v0.6.0 | 2026-02-08 | Status 日期、批量修改、DV Milestone |
| v0.6.1 | 2026-02-09 | Status 粗体、CP 过滤 |
| v0.6.2 | 2026-02-10 | CP 详情、TC 过滤 |

---

## 2. 功能规格

### 2.1 功能列表

| 编号 | 功能 | 描述 | 优先级 |
|------|------|------|--------|
| F001 | 项目管理 | 创建、加载、切换项目 | P0 |
| F002 | CP 管理 | Cover Points CRUD | P0 |
| F003 | TC 管理 | Test Cases CRUD | P0 |
| F004 | 关联管理 | TC ↔ CP 关联 | P0 |
| F005 | 状态跟踪 | OPEN→CODED→FAIL→PASS | P0 |
| F006 | CP 详情 | 展开查看详情和关联 TC | P0 |
| F007 | TC 过滤 | 多字段过滤 Test Cases | P0 |
| F008 | 统计面板 | Pass Rate / Coverage | P1 |
| F009 | 备份恢复 | 项目导出/导入 | P1 |

### 2.2 Cover Point 字段

| 字段 | 说明 |
|------|------|
| Feature | 功能模块 |
| Sub-Feature | 子功能模块 |
| Cover Point | 覆盖点名称 |
| Cover Point Details | 详情说明 |
| Priority | P0/P1/P2 |
| Comments | 备注 |

### 2.3 Test Case 字段

| 字段 | 说明 |
|------|------|
| TestBench | 测试台 |
| Category | 类别 |
| Owner | 负责人 |
| Test Name | 测试名称 |
| Scenario Details | 场景详情 |
| Status | OPEN/CODED/FAIL/PASS/REMOVED |
| DV Milestone | DV 里程碑 |
| Target Date | 目标日期 |
| Status Date | 状态变更日期 |

### 2.4 覆盖率计算

```
Coverage = 所有 CP 覆盖率 / CP 总数
每个 CP 覆盖率 = PASS 关联 TC / 关联 TC 总数 × 100%
```

---

## 3. API 接口

### 3.1 版本管理

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/version` | 获取版本信息 |

### 3.2 项目管理

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| POST | `/api/projects` | 创建项目 |
| POST | `/api/projects/{id}/archive` | 备份项目 |
| POST | `/api/projects/restore/upload` | 从文件恢复 |

### 3.3 Cover Points

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/cp` | 获取 CP 列表 |
| GET | `/api/cp/{id}` | 获取 CP 详情 |
| GET | `/api/cp/{id}/tcs` | 获取关联 TC |
| POST | `/api/cp` | 创建 CP |
| PUT | `/api/cp/{id}` | 更新 CP |
| DELETE | `/api/cp/{id}` | 删除 CP |

### 3.4 Test Cases

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/tc` | 获取 TC 列表 |
| GET | `/api/tc/{id}` | 获取 TC 详情 |
| POST | `/api/tc` | 创建 TC |
| PUT | `/api/tc/{id}` | 更新 TC |
| DELETE | `/api/tc/{id}` | 删除 TC |
| POST | `/api/tc/{id}/status` | 更新状态 |
| POST | `/api/tc/batch/status` | 批量更新状态 |

### 3.5 统计

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/stats` | 获取统计数据 |

---

## 4. 数据库设计

### 4.1 表结构

```
{项目名}.db
├── cover_point              # Cover Points 表
├── test_case               # Test Cases 表
├── tc_cp_connections       # 关联表
└── tracker_version         # 版本表
```

### 4.2 版本迁移

- 每个数据库包含 `tracker_version` 表
- 启动时自动检查版本兼容性
- 支持 v0.2 → v0.3 数据迁移

---

## 5. 部署说明

### 5.1 目录结构

```
/projects/management/tracker/
├── dev/                    # 开发版代码
│   ├── server.py           # 启动脚本 (:8081)
│   ├── app/
│   └── index.html
│
├── shared/                 # 共享数据
│   └── data/
│       ├── user_data/    # 用户数据
│       └── test_data/    # 测试数据
│
└── scripts/              # 工具脚本
    ├── release.py
    └── compat_check.py
```

### 5.2 服务管理

| 环境 | 端口 | 数据 |
|------|------|------|
| 正式版 | 8080 | user_data |
| 开发版 | 8081 | test_data |

### 5.3 systemd 部署

```bash
# 重启服务
sudo systemctl restart tracker

# 查看状态
sudo systemctl status tracker
```

---

## 6. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.1 | 2026-02-03 | 初始版本 |
| v0.2 | 2026-02-03 | 多项目支持 |
| v0.3 | 2026-02-04 | 架构重构 |
| v0.3.1 | 2026-02-04 | 数据隔离 |
| v0.4 | 2026-02-05 | 简化架构 |
| v0.5.0 | 2026-02-06 | 功能增强 |
| v0.5.1 | 2026-02-07 | Bug 修复 |
| v0.6.0 | 2026-02-08 | 第一阶段增强 |
| v0.6.1 | 2026-02-09 | 第二阶段增强 |
| **v0.6.2** | **2026-02-10** | **CP 详情、TC 过滤** |

### v0.6.2 详细变更

详见: [tracker_SPECS_v0.6.2.md](./tracker_SPECS_v0.6.2.md)

---

**详细规格**: 请参考 `SPECIFICATIONS/tracker_SPECS_v0.6.2.md`
**Bug 追踪**: 请参考 `BUGLOG/tracker_BUGLOG.md`
**测试计划**: 请参考 `DEVELOPMENT/TEST_PLAN.md`
