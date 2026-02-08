# 芯片验证 Tracker v0.6.0 总体规格书

> **版本**: v0.6.0 | **更新日期**: 2026-02-08 | **状态**: 正式发布

---

## 目录

1. [需求分析](#1-需求分析)
2. [实现方案](#2-实现方案)
3. [功能规格](#3-功能规格)
4. [API 接口](#4-api-接口)
5. [数据库设计](#5-数据库设计)
6. [版本管理](#6-版本管理)
7. [测试计划](#7-测试计划)
8. [部署说明](#8-部署说明)
9. [版本历史](#9-版本历史)

---

## 1. 需求分析

### 1.1 背景

芯片验证团队需要管理 Cover Points（覆盖点）与 Test Cases（测试用例）的关联关系，跟踪验证进度和覆盖率。团队成员需要多人协作，实时共享数据。

### 1.2 核心目标

- 提供可视化的 Cover Points 管理界面
- 支持 Test Cases 的创建、编辑、状态跟踪
- 自动计算 Cover Points 的完成进度和整体覆盖率
- 支持多人协作，数据实时同步到服务器
- **支持多项目（Project）管理**
- **支持测试版本和正式版本分离**

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 多项目（Project）管理 | 与外部 CI/CD 系统集成 |
| Cover Points 的增删改查 | 自动化测试执行引擎 |
| Test Cases 的增删改查 | 芯片仿真功能 |
| TC 与 CP 的多对多关联管理 | 用户权限管理 |
| 状态跟踪（OPEN/CODED/FAIL/PASS） | |
| 项目备份/恢复（Archive） | |
| 测试版本和正式版本分离 | |
| 进度/覆盖率统计面板 | |
| 数据持久化到 SQLite 数据库 | |
| systemd 正式版部署 | |

### 1.4 v0.6.0 重大变更

**v0.6.0 第一阶段功能增强：**

- **Status 日期记录**: CODED/FAIL/PASS/REMOVED 状态变更时自动记录日期
- **Target Date 字段**: 支持设置测试预期完成日期
- **REMOVED 状态**: 新增已移除测试用例状态，统计时自动排除
- **批量修改功能**: 支持批量更新状态、Target Date、DV Milestone
- **DV Milestone 字段**: 跟踪测试用例所属的 DV 里程碑版本
- **CP Priority 字段**: 支持 Cover Point 优先级标记 (P0/P1/P2)

---

## 2. 实现方案

### 2.1 目录结构

```
/projects/management/tracker/              ← Git 仓库（只维护 dev/）
├── dev/                                  ← 开发版代码（Git 分支: develop）
│   ├── server.py                        # 开发启动脚本 (:8081)
│   ├── server_test.py      # 旧启动脚本（已弃用）
│   ├── start_server_test.sh     # 新启动脚本 (gunicorn)
│   ├── app/                             # Flask 应用
│   ├── index.html                       # 前端页面
│   ├── data → ../shared/data/test_data  # 测试数据
│   ├── tests/                           # 测试用例
│   └── docs/                            # 文档
│
├── shared/                              # 共享数据（不纳入 Git）
│   └── data/
│       ├── user_data/                   # 用户真实数据（正式版使用）
│       │   ├── projects.json
│       │   ├── Debugware_65K.db
│       │   └── EX5.db
│       │
│       └── test_data/                    # 测试数据（开发版使用）
│           ├── projects.json
│           └── *.db
│
└── scripts/                             # 工具脚本
    ├── release.py                      # 版本发布脚本
    ├── migrate_v02_to_v03.py            # v0.2 → v0.3 迁移
    ├── compat_check.py                  # 兼容性检查
    └── data_manager.py                  # 数据管理工具

/release/tracker/                         ← 发布目录（由 release.py 生成，不纳入 Git）
├── v0.3.1/                             ← 历史版本
├── v0.3.2/                             ← 当前版本
├── current → v0.3.2                    ← 软链接指向当前版本
└── RELEASE_NOTES.md                     ← 发布报告
```

### 2.2 数据隔离原则

| 原则 | 说明 |
|------|------|
| **用户数据独立** | `user_data/` 存储用户真实数据，独立于代码 |
| **测试数据隔离** | `test_data/` 存储测试数据，与用户数据完全隔离 |
| **dev 使用 test_data** | 开发测试操作 test_data，不影响用户数据 |
| **发布目录独立** | `/release/tracker/v{version}/` 存放发布版本，不纳入 Git |
| **current 软链接** | `/release/tracker/current` 指向当前运行版本 |
| **版本发布** | 发布到 `/release/tracker/v{version}`，切换软链接更新版本 |
| **数据库版本** | 每个数据库包含版本号，支持自动迁移 |

### 2.3 多版本架构

```
                            ┌─────────────────────────┐
                            │       systemd 服务      │
                            │  /release/tracker/current → v{version}/
                            └─────────────────────────┘
                                              │
              ┌─────────────────────────────────┼─────────────────────────────────┐
              │                                 │                                 │
              ▼                                 ▼                                 ▼
      ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
      │  发布版       │               │  开发版       │               │  共享数据     │
      │ /release/    │               │  dev/        │               │  shared/     │
      │ tracker/     │               │  :8081       │               │  data/       │
      │ current/     │               │  (Git)       │               │              │
      └───────────────┘               └───────────────┘               └───────────────┘
              │                                 │                                 │
              ▼                                 ▼                                 ▼
      ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
      │ user_data/    │               │ test_data/   │               │ backups/     │
      │ (用户真实数据) │               │ (测试数据)   │               │ (原始备份)   │
      └───────────────┘               └───────────────┘               └───────────────┘
```

### 2.4 数据兼容性测试

如需测试用户数据与 dev 版本的兼容性：

```bash
# 1. 同步用户项目到测试目录（复制一份）
python3 scripts/data_manager.py sync

# 2. 在 dev 版本中测试复制的用户数据
# 访问 http://localhost:8081
# 切换到复制的用户项目进行测试

# 3. 测试完成后清理（删除复制的用户项目）
python3 scripts/data_manager.py clean
```

### 2.5 端口配置

| 版本 | 端口 | 数据目录 | 启动命令 |
|------|------|----------|----------|
| 正式版 | 8080 | user_data | `cd stable && python3 server.py` |
| 测试版 | 8081 | test_data | `cd dev && bash start_server_test.sh` |

---

## 3. 功能规格

### 3.1 功能列表

| 编号 | 功能 | 描述 | 优先级 |
|------|------|------|--------|
| F001 | **项目管理** | 创建、加载、切换项目 | P0 |
| F002 | **代码隔离** | stable/ 和 dev/ 目录分离 | P0 |
| F003 | **数据共享** | shared/data/ 集中存储 | P0 |
| F004 | **Cover Points 管理** | 按字段结构管理 CP | P0 |
| F005 | **Test Cases 管理** | 按字段结构管理 TC | P0 |
| F006 | **关联管理** | TC 关联 CP（多对多关系） | P0 |
| F007 | **状态跟踪** | OPEN → CODED → FAIL → PASS | P0 |
| F008 | **版本迁移** | 数据库版本号 + 自动迁移 | P0 |
| F009 | **排序过滤** | 按字段排序和过滤 TC | P1 |
| F010 | **完成日期** | 显示 TC 完成日期 | P1 |
| F011 | **进度统计** | 自动计算 CP 完成进度 | P1 |
| F012 | **覆盖率计算** | 整体覆盖率百分比显示 | P1 |
| F013 | **项目备份** | 导出项目 Archive | P1 |
| F014 | **项目恢复** | 从 Archive 导入恢复 | P1 |
| F015 | **版本管理** | 测试版/正式版分离 | P1 |
| F016 | **发布脚本** | 一键发布到正式版 | P1 |
| F017 | **兼容性检查** | 启动时自动检查 | P1 |
| F018 | **界面优化** | Excel 风格，紧凑显示 | P2 |
| F019 | **systemd 部署** | 正式版 24/7 运行 | P1 |
| **F020** | **Status 日期记录** | 状态变更时自动记录日期 | P0 |
| **F021** | **Target Date 字段** | 设置测试预期完成日期 | P0 |
| **F022** | **REMOVED 状态** | 已移除测试用例状态 | P0 |
| **F023** | **批量修改功能** | 批量更新状态/日期/里程碑 | P0 |
| **F024** | **DV Milestone 字段** | 跟踪 DV 里程碑版本 | P0 |
| **F025** | **CP Priority 字段** | Cover Point 优先级标记 | P0 |

### 3.2 Cover Point 字段

| 字段 | 说明 | 必填 |
|------|------|------|
| Feature | 功能模块 | ✅ |
| Sub-Feature | 子功能模块 | ✅ |
| Cover Point | 覆盖点名称 | ✅ **(首要)** |
| Cover Point Details | 覆盖点详情 | ✅ |
| **Priority** | 优先级 (P0/P1/P2) | ✅ |
| Comments | 备注 | ❌ |

### 3.3 Test Case 字段

| 字段 | 说明 | 必填 |
|------|------|------|
| TestBench | 测试台 | ✅ |
| Category | 类别 | ✅ |
| Owner | 负责人 | ✅ |
| Test Name | 测试名称 | ✅ **(首要)** |
| Scenario Details | 场景详情 | ✅ |
| Checker Details | 检查器详情 | ❌ (可隐藏) |
| Coverage Details | 覆盖详情 | ❌ (可隐藏) |
| Comments | 备注 | ❌ (可隐藏) |
| Status | 状态 | 系统字段 |
| DV Milestone | DV 里程碑版本 | 系统字段 |
| Target Date | 目标完成日期 | 系统字段 |
| Status Date | 状态变更日期 | 系统字段 |
| **coded_date** | CODED 状态日期 | 系统字段 |
| **fail_date** | FAIL 状态日期 | 系统字段 |
| **pass_date** | PASS 状态日期 | 系统字段 |
| **removed_date** | REMOVED 状态日期 | 系统字段 |

### 3.3 Cover Point 覆盖率计算规则

> **v0.3.1 新增功能**

每个 Cover Point 显示覆盖率百分比，基于关联的 Test Cases 状态计算：

| 关联 TC 状态 | 覆盖率 |
|-------------|--------|
| 全部 PASS | **100%** ✅ |
| 无关联 TC | **0%** （显示 0/0） |
| 部分 PASS | **PASS 数量 / 关联总数 × 100%** |

**计算逻辑：**

```python
# 获取 CP 关联的所有 TC
cursor.execute('''
    SELECT tc.status FROM test_case tc
    INNER JOIN tc_cp_connections tcc ON tc.id = tcc.tc_id
    WHERE tcc.cp_id = ?
''', (cp_id,))

connected_tcs = cursor.fetchall()
total = len(connected_tcs)
passed = sum(1 for tc in connected_tcs if tc['status'] == 'PASS')

coverage = round(passed / total * 100, 1) if total > 0 else 0.0
```

**前端显示示例：**

| 状态 | 覆盖率显示 |
|------|-----------|
| 100% | 🟢 100% (3/3) |
| 部分 | 🟡 66.7% (2/3) |
| 0% | ⚪ 0% (0/3) |
| 无关联 | ⚪ 0% (0/0) |

**API 返回字段：**

```json
{
  "id": 1,
  "feature": "...",
  "cover_point": "...",
  "coverage": 100.0,
  "coverage_detail": "3/3"
}
```

### 3.4 状态定义

| 状态 | 说明 | 计入统计 |
|------|------|----------|
| OPEN | 待开发/待执行 | ✅ |
| CODED | 已开发完成 | ✅ |
| FAIL | 测试失败 | ✅ |
| PASS | 测试通过 | ✅ |
| REMOVED | 已移除/废弃 | ❌ |

**REMOVED 状态特殊规则**:
- 不计入 Total 统计
- 不计入 Pass Rate 计算
- 状态变更时自动清除与 CP 的关联
- 可转移回 CODED 状态

---

## 4. API 接口

### 4.1 版本管理

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/version` | 获取版本信息 |

### 4.2 项目管理

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| **GET** | **`/api/projects/{id}`** | **获取项目详情** |
| POST | `/api/projects` | 创建新项目 |
| POST | `/api/projects/{id}/archive` | 备份项目 |
| GET | `/api/projects/archive/list` | 获取归档列表 |
| POST | `/api/projects/restore` | 从归档恢复 |
| DELETE | `/api/projects/{id}` | 删除项目 |

### 4.3 Cover Points

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/cp` | 获取 CP 列表（**含覆盖率 + Priority**） |
| **GET** | **`/api/cp/{id}`** | **获取 CP 详情（需 project_id）** |
| POST | `/api/cp` | 创建 CP |
| PUT | `/api/cp/{id}` | 更新 CP（**需 project_id**） |
| DELETE | `/api/cp/{id}` | 删除 CP（需 project_id） |
| **POST** | **`/api/cp/batch/priority`** | **批量更新 Priority（需 project_id）** |

**API 参数说明**:
- **GET /api/cp**: 通过查询参数传递 `project_id`，例如: `/api/cp?project_id=1`
- **GET /api/cp/{id}**: 通过查询参数传递 `project_id`，例如: `/api/cp/1?project_id=1`
- **POST /api/cp**: 在请求体中传递 `project_id`
- **PUT /api/cp/{id}**: 在请求体中必须包含 `project_id`
- **DELETE /api/cp/{id}**: 通过查询参数传递 `project_id`，例如: `/api/cp/1?project_id=1`

**PUT /api/cp/{id} 请求体**:
```json
{
    "project_id": 1,
    "feature": "Feature A",
    "sub_feature": "SubFeature A",
    "cover_point": "CP_A",
    "cover_point_details": "Details",
    "priority": "P0",
    "comments": ""
}
```

**DELETE /api/cp/{id} 请求示例**:
```
DELETE /api/cp/1?project_id=1
```

**GET /api/cp 返回字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | CP ID |
| project_id | int | 项目 ID |
| feature | string | Feature |
| sub_feature | string | Sub-Feature |
| cover_point | string | Cover Point |
| cover_point_details | string | 详情 |
| comments | string | 备注 |
| created_at | string | 创建时间 |
| **priority** | string | **优先级 (P0/P1/P2)** |
| **coverage** | float | **覆盖率百分比 (0-100)** |
| **coverage_detail** | string | **详情格式: "PASS/总数"** |

### 4.4 Test Cases

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/tc` | 获取 TC 列表（**含日期/DV Milestone**） |
| **GET** | **`/api/tc/{id}`** | **获取 TC 详情（需 project_id）** |
| POST | `/api/tc` | 创建 TC |
| PUT | `/api/tc/{id}` | 更新 TC 信息（**不含状态**，需 project_id） |
| DELETE | `/api/tc/{id}` | 删除 TC（需 project_id） |
| POST | `/api/tc/{id}/status` | 更新状态（**含日期自动记录**，需 project_id） |
| POST | `/api/tc/batch/status` | 批量更新状态（需 project_id） |
| POST | `/api/tc/batch/target_date` | 批量更新 Target Date（需 project_id） |
| POST | `/api/tc/batch/dv_milestone` | 批量更新 DV Milestone（需 project_id） |

**API 参数说明**:
- **GET /api/tc**: 通过查询参数传递 `project_id`，例如: `/api/tc?project_id=1`
- **GET /api/tc/{id}**: 通过查询参数传递 `project_id`，例如: `/api/tc/1?project_id=1`
- **POST /api/tc**: 在请求体中传递 `project_id`
- **PUT /api/tc/{id}**: 在请求体中必须包含 `project_id`，**不能用于更新状态**
- **DELETE /api/tc/{id}**: 通过查询参数传递 `project_id`，例如: `/api/tc/1?project_id=1`
- **POST /api/tc/{id}/status**: 在请求体中必须包含 `project_id` 和 `status`

**PUT /api/tc/{id} 请求体**:
```json
{
    "project_id": 1,
    "testbench": "TB_A",
    "category": "Category",
    "owner": "Owner",
    "test_name": "TC_A",
    "scenario_details": "Scenario",
    "target_date": "2026-02-15",
    "dv_milestone": "DV0.5",
    "checker_details": "",
    "coverage_details": "",
    "comments": "",
    "connections": [1, 2, 3]
}
```
> **注意**: `connections` 字段用于设置 TC 关联的 CP ID 列表。调用时会覆盖原有的关联关系。

**POST /api/tc/{id}/status 请求体**:
```json
{
    "project_id": 1,
    "status": "PASS"
}
```

**DELETE /api/tc/{id} 请求示例**:
```
DELETE /api/tc/1?project_id=1
```

**GET /api/tc 返回字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | TC ID |
| project_id | int | 项目 ID |
| dv_milestone | string | DV 里程碑 |
| testbench | string | 测试台 |
| category | string | 类别 |
| owner | string | 负责人 |
| test_name | string | 测试名称 |
| status | string | 状态 |
| **target_date** | string | **目标完成日期** |
| **coded_date** | string | **CODED 日期** |
| **fail_date** | string | **FAIL 日期** |
| **pass_date** | string | **PASS 日期** |
| **removed_date** | string | **REMOVED 日期** |

### 4.5 统计

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/stats` | 获取统计数据（**排除 REMOVED**） |

**统计规则**：
- REMOVED 状态的 TC 不计入 Total
- REMOVED 状态的 TC 不计入 Pass Rate 计算

---

### 4.6 API 使用说明

#### 4.6.1 为什么需要 project_id？

Tracker 使用**独立数据库架构**，每个项目拥有独立的 `.db` 文件。因此，所有涉及项目数据的 API 操作都需要知道操作的是哪个项目的数据。

**project_id 传递方式**:
| API 类型 | 传递方式 | 示例 |
|----------|----------|------|
| GET (列表) | 查询参数 | `GET /api/tc?project_id=1` |
| POST (创建) | 请求体 JSON | `{"project_id": 1, ...}` |
| PUT (更新) | 请求体 JSON | `{"project_id": 1, ...}` |
| DELETE | 查询参数 | `DELETE /api/tc/1?project_id=1` |

#### 4.6.2 错误处理

| 状态码 | 含义 | 常见原因 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 缺少 project_id、参数格式错误 |
| 404 | 资源不存在 | 项目不存在、CP/TC ID 不存在 |
| 500 | 服务器错误 | 数据库错误 |

**常见错误响应**:
```json
// 缺少 project_id
{"error": "需要指定项目"}

// 项目不存在
{"error": "项目不存在"}

// CP/TC 不存在
{"error": "Cover Point 不存在"}

/**
 * Test Case 不存在
{"error": "Test Case 不存在"}
```

---

## 5. 数据库设计

### 5.1 数据库结构

每个项目拥有独立的 SQLite 数据库文件 (`*.db`)：

```
{项目名}.db
├── cover_point           # Cover Points 表 (v0.6.0+ 含 priority)
├── test_case            # Test Cases 表 (v0.6.0+ 含新字段)
├── tc_cp_connections    # TC-CP 关联表
└── tracker_version      # 版本表 (v0.3+)
```

### 5.2 版本表

**tracker_version 表：**

```sql
CREATE TABLE tracker_version (
    version TEXT PRIMARY KEY,
    created_at TEXT,
    migrated_at TEXT
);
```

### 5.3 v0.6.0 字段变更

#### Test Case 表新增字段 (v0.6.0)

```sql
-- DV Milestone 字段
ALTER TABLE test_case ADD COLUMN dv_milestone VARCHAR(10) DEFAULT NULL;

-- Target Date 字段
ALTER TABLE test_case ADD COLUMN target_date DATE DEFAULT NULL;

-- Status 日期字段
ALTER TABLE test_case ADD COLUMN coded_date DATE DEFAULT NULL;
ALTER TABLE test_case ADD COLUMN fail_date DATE DEFAULT NULL;
ALTER TABLE test_case ADD COLUMN pass_date DATE DEFAULT NULL;
ALTER TABLE test_case ADD COLUMN removed_date DATE DEFAULT NULL;
```

#### Cover Point 表新增字段 (v0.6.0)

```sql
-- Priority 字段
ALTER TABLE cover_point ADD COLUMN priority VARCHAR(3) DEFAULT 'P0';
```

#### 数据迁移 (v0.6.0)

```sql
-- 为已有数据填充日期
UPDATE test_case SET pass_date = updated_at WHERE status = 'PASS';
UPDATE test_case SET coded_date = updated_at WHERE status = 'CODED';
UPDATE test_case SET fail_date = updated_at WHERE status = 'FAIL';

-- DV Milestone 默认值
UPDATE test_case SET dv_milestone = 'DV1.0' WHERE dv_milestone IS NULL;

-- CP Priority 默认值
UPDATE cover_point SET priority = 'P0' WHERE priority IS NULL;
```

### 5.4 v0.2 到 v0.3 迁移

现有用户需要执行迁移：

```bash
# 1. 检查兼容性
python3 scripts/compat_check.py shared/data/

# 2. 执行迁移
python3 scripts/migrate_v02_to_v03.py --source data/tracker.db --target shared/data/

# 3. 验证
python3 scripts/compat_check.py shared/data/
```

---

## 6. 版本管理

### 6.1 Git 分支策略

#### 6.1.1 分支结构

```
main (稳定代码，对应 /release/tracker/current)
│
├── develop (开发分支，存放 dev/ 代码)
│   ├── feature/* (功能开发分支，源自 develop，合并回 develop)
│   ├── release/* (发布分支，源自 develop，合并回 main 和 develop)
│   └── hotfix/* (紧急修复分支，源自 main，合并回 main 和 develop)
│
└── tags (在 main 分支上创建)
    ├── v0.3.0
    ├── v0.3.1
    └── v0.3.2

/release/tracker/                         ← 发布目录（由 release.py 生成）
├── v0.3.1/                               ← 历史版本
├── v0.3.2/                               ← 当前版本
└── current → v0.3.2/                    ← 软链接指向当前运行版本
```

#### 6.1.2 分支说明

| 分支 | 命名规则 | 来源 | 合并到 | 用途 |
|------|----------|------|--------|------|
| **main** | `main` | - | - | 生产环境代码（Git） |
| **develop** | `develop` | main | - | 开发主分支（存放 dev/ 代码） |
| **feature** | `feature/xxx` | develop | develop | 新功能开发 |
| **release** | `release/v0.x.x` | develop | main + develop | 发布准备 |
| **hotfix** | `hotfix/v0.x.x` | main | main + develop | 紧急修复 |

**发布目录（由 release.py 生成，不纳入 Git）：**

| 目录 | 说明 |
|------|------|
| `/release/tracker/v{version}/` | 发布版本目录 |
| `/release/tracker/current` | 软链接，指向当前运行版本 |

**说明：**
- Git 仓库只维护 `dev/` 代码
- 发布时由 `release.py` 生成到 `/release/tracker/v{version}/`
- systemd 服务指向 `/release/tracker/current`

#### 6.1.3 工作流程

**日常开发（dev 版本）：**
```bash
# 创建功能分支
git checkout develop
git checkout -b feature/user-auth

# 开发完成，合并回 develop
git checkout develop
git merge feature/user-auth --no-ff -m "feat: 添加用户认证功能"
git branch -d feature/user-auth
```

**版本发布：**
```bash
# 创建发布分支
git checkout develop
git checkout -b release/v0.3.3

# 测试完成后合并：
git checkout main
git merge release/v0.3.3 --no-ff -m "release: v0.3.3"
git tag -a v0.3.3 -m "Release v0.3.3"

git checkout develop
git merge release/v0.3.3 --no-ff

git branch -d release/v0.3.3
```

**Hotfix 紧急修复（用户反馈后）：**
```bash
# 场景：正式版发现紧急 bug
git checkout main
git checkout -b hotfix/v0.3.2-urgent

# 修复 bug
git add .
git commit -m "hotfix: 修复项目切换数据丢失问题"

# 合并到 main（立即发布）
git checkout main
git merge hotfix/v0.3.2-urgent --no-ff -m "hotfix: v0.3.2-urgent"
git tag -a v0.3.2 -m "Hotfix v0.3.2"

# 同步到 develop（保持一致）
git checkout develop
git merge hotfix/v0.3.2-urgent --no-ff

git branch -d hotfix/v0.3.2-urgent
```

#### 6.1.4 .gitignore 配置

```bash
# /projects/management/tracker/.gitignore

# 数据目录（不版本控制）
shared/data/
user_data/
test_data/
*.db

# 测试输出
test-results/
playwright-report/
htmlcov/

# Python
__pycache__/
*.pyc
.pytest_cache/
.coverage

# IDE
.vscode/
.idea/

# 系统文件
.DS_Store
```

---

### 6.2 发布流程

```
日常开发 → 功能测试 → 创建发布分支 → 集成测试 → 合并到 main → 打标签 → 执行 release.py → 切换软链接 → 重启服务
```

**自动完成以下步骤：**

1. **代码检查** - 测试是否全部通过
2. **版本号更新** - 更新版本文件中的版本号
3. **兼容性检查** - 检查用户数据库版本，如需迁移则执行迁移脚本
4. **创建发布版本** - 复制 dev/ 代码到 `/release/tracker/v{version}/`
5. **配置数据链接** - 创建 `data → ../../shared/data/user_data` 符号链接
6. **切换 current 软链接** - `/release/tracker/current` 指向新版本
7. **更新 systemd** - 服务配置指向新目录
8. **重启服务** - 自动重启 tracker 服务
9. **生成发布报告** - 创建 `/release/tracker/v{version}/RELEASE_NOTES.md`

---

### 6.3 发布命令

```bash
cd /projects/management/tracker

# 演练模式（不实际执行）
python3 scripts/release.py --dry-run

# 实际发布
python3 scripts/release.py --version v0.3.3 --migrate --force

# 回滚（切换到上一版本）
python3 scripts/release.py --rollback --force
```

**发布目录：**
```
/release/tracker/
├── v0.3.1/
├── v0.3.2/
└── current → v0.3.2  ← systemd 指向这里
```

---

### 6.4 发布流程详解

```
1. 检查数据目录结构
   └── 验证 user_data 和 test_data 存在

2. 创建发布版本
   └── /release/tracker/v{version}/（从 dev/ 复制，不包括 data、tests）

3. 配置数据符号链接
   └── /release/tracker/v{version}/data → ../../shared/data/user_data

4. 切换 current 软链接
   └── /release/tracker/current → /release/tracker/v{version}/

5. 更新 systemd 服务
   └── /etc/systemd/system/tracker.service

6. 重启服务
   └── sudo systemctl restart tracker

7. 验证服务状态
   └── 检查服务是否正常运行
```

**发布后访问：** http://10.0.0.8:8080

**发布目录结构：**
```
/release/tracker/
├── v0.3.1/              ← 历史版本
│   ├── server.py
│   ├── app/
│   ├── index.html
│   ├── data → ../../shared/data/user_data
│   └── RELEASE_NOTES.md
│
├── v0.3.2/              ← 当前版本
│   └── ...
│
└── current → v0.3.2/    ← 软链接，systemd 指向这里
```

---

### 6.5 发布摘要模板

发布脚本会自动生成 `/release/tracker/v{version}/RELEASE_NOTES.md`，包含以下内容：

```markdown
# Tracker v{版本号} 发布报告

> **版本**: {版本号} | **发布日期**: {日期} | **发布时间**: {时间}

---

## 发布摘要

| 项目 | 状态 |
|------|------|
| 版本 | {版本号} |
| 源版本 | dev |
| 目标版本 | stable |
| 兼容性检查 | ✅ 全部通过 |
| 代码发布 | ✅ dev → stable |

---

## 数据目录结构

```
shared/data/
├── user_data/       # 正式版数据 (stable 使用)
│   └── 2 个项目数据库
│
└── test_data/      # 测试数据 (dev 使用)
    └── 测试项目数据库
```

---

## 数据统计

| 指标 | 值 |
|------|-----|
| 用户项目数量 | 2 |
| 数据库文件 | 2 个 |

---

## 访问地址

| 环境 | 地址 | 端口 |
|------|------|------|
| 内网 | http://10.0.0.8 | 8080 |
| 外网 | http://外网IP | 8080 |

---

## 服务管理

```bash
# 重启服务（发布后需要）
sudo systemctl restart tracker

# 查看状态
sudo systemctl status tracker

# 查看日志
journalctl -u tracker -f
```

---

## 版本回滚

如需回滚到上一版本：

```bash
cd /projects/management/tracker
python3 scripts/release.py --rollback --force
```

**注意：** 回滚只恢复代码文件，用户数据不会改变。

---

## 备份位置

发布前已自动备份：

```
stable/backup_YYYYMMDD_HHMMSS
```

---

**文档生成时间**: {日期} {时间}
```

---

### 6.6 回滚方案

如果新版本有问题，执行回滚（切换软链接）：

```bash
cd /projects/management/tracker
python3 scripts/release.py --rollback --force
```

**回滚过程：**

1. 查找可用的历史版本
2. 切换 `current` 软链接到上一版本
3. 更新 systemd 服务配置
4. 重启 tracker 服务
5. 验证服务状态

**手动回滚（如果需要）：**

```bash
# 查看可用版本
ls -la /release/tracker/

# 切换到指定版本
sudo rm /release/tracker/current
sudo ln -s /release/tracker/v0.3.1 /release/tracker/current
sudo systemctl restart tracker
```

**⚠️ 注意：**
- 用户数据（user_data）独立存储，**不会改变**，无需回滚
- 回滚只是切换软链接，非常快速
- 历史版本目录保留，可以随时回滚

---

## 7. 测试计划

### 7.1 测试类型

| 测试类型 | 覆盖范围 | 通过标准 |
|----------|----------|----------|
| 单元测试 | API 接口、独立数据库 | 全部通过 |
| 集成测试 | 项目 + CP + TC 关联 | 全部通过 |
| 版本迁移 | v0.2 → v0.3 数据迁移 | 数据完整 |
| 手动测试 | 前端交互、界面显示 | 用户验收 |

### 7.2 目录结构测试

| ID | 测试项 | 预期结果 | 状态 |
|----|--------|----------|------|
| T001 | stable/data 是符号链接 | 指向 shared/data | ✅ |
| T002 | dev/data 是符号链接 | 指向 shared/data | ✅ |
| T003 | shared/data/ 独立存在 | 不随代码发布改变 | ✅ |
| T004 | stable/ 代码可独立启动 | 访问 http://localhost:8080 | ✅ |
| T005 | dev/ 代码可独立启动 | 访问 http://localhost:8081 | ✅ |

### 7.3 API 测试用例

| ID | API | 测试步骤 | 预期结果 |
|----|-----|----------|----------|
| A001 | GET /api/version | 获取版本信息 | 返回版本信息 |
| A002 | POST /api/projects | 创建项目 | 项目创建成功，生成独立 .db |
| A003 | GET /api/projects | 获取项目列表 | 返回所有项目 |
| A004 | POST /api/cp | 创建 CP | CP 创建成功 |
| A005 | GET /api/cp | 获取 CP 列表 | 返回 CP 列表 |
| A006 | POST /api/tc | 创建 TC（默认 OPEN） | TC 创建成功 |
| A007 | POST /api/tc/{id}/status | 更新状态 | 状态切换，完成日期更新 |
| A008 | GET /api/stats | 获取统计 | 返回统计数据 |

### 7.4 版本迁移测试

| ID | 测试项 | 预期结果 |
|----|--------|----------|
| M001 | 加载 v0.2 数据 | 正确读取 project, cp, tc 表 |
| M002 | 生成独立数据库 | 每个项目一个 .db 文件 |
| M003 | 创建 projects.json | 项目列表正确 |
| M004 | 数据完整性 | CP, TC 数量一致 |
| M005 | 关联关系 | tc_cp_connections 正确 |

### 7.5 发布流程测试

| ID | 测试项 | 预期结果 |
|----|--------|----------|
| R001 | 代码复制 | stable/ 代码被更新 |
| R002 | 数据保留 | shared/data/ 不变 |
| R003 | 符号链接 | stable/data 指向 shared/data |
| R004 | 回滚功能 | 可恢复到上一版本 |

---

## 8. 部署说明

### 8.1 快速开始

**启动正式版：**

```bash
cd /projects/management/tracker/stable
python3 server.py
# 访问 http://localhost:8080
```

**启动测试版：**

```bash
cd /projects/management/tracker/dev
bash start_server_test.sh
# 访问 http://localhost:8081
```

### 8.2 技术栈

| 层级 | 技术 | 版本要求 |
|------|------|----------|
| 前端 | HTML5 + Vanilla JavaScript | ES6+ |
| 后端 | Python Flask | 最新 |
| 数据库 | SQLite | 3.x |
| 部署 | systemd（正式版） | - |
| 测试 | pytest | - |

### 8.3 systemd 部署（正式版）

**说明：** systemd 服务指向 `/release/tracker/current`，由 `release.py` 自动更新配置。

```ini
# /etc/systemd/system/tracker.service
# （由 release.py 自动生成，无需手动配置）

[Unit]
Description=Chip Verification Tracker v0.3
After=network.target

[Service]
User=root
WorkingDirectory=/release/tracker/current
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/tracker.log
StandardError=append:/var/log/tracker.error.log

[Install]
WantedBy=multi-user.target
```

**常用命令：**

```bash
# 查看状态
sudo systemctl status tracker

# 重启服务
sudo systemctl restart tracker

# 查看日志
journalctl -u tracker -f
```

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.1 | 2026-02-03 | 初始版本：基础 CRUD + JSON 存储 |
| v0.2 | 2026-02-03 | **重大更新**：多项目、新字段结构、备份恢复 |
| v0.3 | 2026-02-04 | **架构重构**：代码隔离、数据共享、版本迁移 |
| v0.3.1 | 2026-02-04 | **数据隔离**：user_data/test_data 分离，测试不碰用户数据 |
| v0.4 | 2026-02-05 | **简化架构**：Git 只维护 dev/，发布到 /release/tracker/ |
| v0.5.0 | 2026-02-06 | **功能增强**：界面优化、测试报告、发布准备脚本 |
| v0.5.1 | 2026-02-07 | **Bug 修复**：API 和界面问题修复 |
| **v0.6.0** | **2026-02-08** | **第一阶段功能增强**：Status 日期、Target Date、REMOVED、批量修改、DV Milestone、CP Priority |

### v0.6.0 详细变更

1. **Status 日期记录**：
   - CODED/FAIL/PASS/REMOVED 状态变更时自动记录日期
   - OPEN 状态不记录日期
   - PASS → 其他状态有二次确认提示

2. **Target Date 字段**：
   - TC 表格显示 Target Date 列
   - 支持单个和批量修改 Target Date

3. **REMOVED 状态**：
   - Status 下拉框新增 REMOVED 选项
   - REMOVED 状态的 TC 显示删除线样式
   - REMOVED 不计入 Total 和 Pass Rate 统计
   - REMOVED 时自动清除与 CP 的关联

4. **批量修改功能**：
   - TC 表格显示复选框列
   - 支持批量更新状态、Target Date、DV Milestone
   - 支持全选/取消全选

5. **DV Milestone 字段**：
   - TC 表格显示 DV Milestone 列
   - 支持选择 DV0.3/DV0.5/DV0.7/DV1.0
   - 默认值 DV1.0

6. **CP Priority 字段**：
   - CP 表格显示 Priority 列
   - 支持选择 P0/P1/P2
   - 默认值 P0

### v0.5.x 详细变更

1. **Git 仓库简化**：
   - 只维护 `dev/` 代码，移除 `stable/` 追踪
   - 发布目录 `/release/tracker/v{version}/` 由 `release.py` 生成

2. **发布目录独立**：
   - `/release/tracker/v{version}/`：历史版本目录
   - `/release/tracker/current`：软链接指向当前运行版本
   - systemd 服务指向 `current`

3. **发布流程改进**：
   - 一键发布到独立目录
   - 软链接切换版本，无需覆盖
   - 快速回滚（切换软链接）
   - 用户数据与测试数据物理隔离，互不影响

3. **数据管理工具**（scripts/data_manager.py）：
   - `sync`：同步用户数据到测试目录（用于兼容性测试）
   - `clean`：清理测试数据
   - `create`：创建测试项目

4. **CP 覆盖率计算**（v0.3.1 新增）：
   - 每个 Cover Point 显示覆盖率百分比
   - 基于关联 TC 的 PASS 状态计算
   - 全部 PASS = 100%，无关联 = 0%，部分 = PASS/总数
   - API 返回 `coverage` 和 `coverage_detail` 字段

### v0.3 详细变更

1. **代码隔离**：stable/ 和 dev/ 目录完全独立
2. **数据共享**：shared/data/ 集中存储用户数据
3. **版本迁移**：支持 v0.2 到 v0.3 自动迁移
4. **发布流程**：一键发布脚本，支持回滚
5. **兼容性检查**：启动时自动检查数据库版本

---

## 附录

### A. 文件结构

```
/projects/management/tracker/
├── stable/                   # 正式版
│   ├── server.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── index.html
│   └── data → ../shared/data/user_data
│
├── dev/                     # 测试版
│   ├── server.py
│   ├── server_test.py      # 原启动脚本（已弃用）
│   ├── start_server_test.sh     # 新启动脚本 (gunicorn)
│   ├── app/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── index.html
│   ├── tests/
│   │   ├── test_api.py      # 完整 API 测试
│   │   └── test_sanity.py   # 冒烟测试
│   └── data → ../shared/data/test_data
│
├── shared/                  # 共享数据
│   └── data/
│       ├── user_data/       # 用户真实数据
│       │   ├── projects.json
│       │   ├── Debugware_65K.db
│       │   └── EX5.db
│       │
│       ├── test_data/       # 测试数据
│       │   ├── projects.json
│       │   └── *.db        # 测试项目
│       │
│       └── tracker_backup_*.db  # v0.2 原始备份
│
└── scripts/                 # 工具脚本
    ├── release.py           # 版本发布
    ├── migrate_v02_to_v03.py  # v0.2 → v0.3 迁移
    ├── compat_check.py      # 兼容性检查
    └── data_manager.py      # 数据管理（sync/clean）
```

### B. 风险评估

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 迁移失败 | 数据丢失 | 自动备份原数据 |
| 符号链接损坏 | 数据不可访问 | 发布前验证链接 |
| 版本冲突 | 启动失败 | 版本检查 + 错误提示 |
| 端口冲突 | 服务无法启动 | 使用不同端口 (8080/8081) |

### C. 常见问题

**Q: 如何升级到 v0.3？**

A: 执行迁移脚本：
```bash
python3 scripts/migrate_v02_to_v03.py --source data/tracker.db --target shared/data/
```

**Q: 版本发布会丢失数据吗？**

A: 不会。数据存储在 `shared/data/`，独立于代码目录。

**Q: 如何回滚到上一版本？**

A: 执行回滚命令：
```bash
python3 scripts/release.py --rollback --force
```
