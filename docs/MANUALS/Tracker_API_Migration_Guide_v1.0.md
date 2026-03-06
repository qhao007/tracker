# Tracker 管理员后台项目创建/迁移指导手册

> **版本**: v1.0  
> **适用版本**: Tracker v0.9.0+  
> **创建日期**: 2026-03-05  
> **文档类型**: 操作指南

---

## 目录

1. [概述](#1-概述)
2. [环境准备](#2-环境准备)
3. [API基础 - 项目管理](#3-api基础---项目管理)
4. [Cover Point 导入](#4-cover-point-导入)
5. [Test Case 导入](#5-test-case-导入)
6. [批量操作与脚本](#6-批量操作与脚本)
7. [CSV标准模板](#7-csv标准模板)
8. [迁移验证](#8-迁移验证)
9. [附录](#9-附录)

---

## 1. 概述

### 1.1 目的

本文档指导管理员如何通过 Tracker API 在后台创建项目，并将外部跟踪的芯片验证数据（Excel/CSV）迁移到 Tracker 系统。

### 1.2 适用范围

- **场景一**：新建项目 - 通过 API 创建空白项目
- **场景二**：数据迁移 - 将现有 Excel 跟踪数据迁移到 Tracker
- **场景三**：批量导入 - 使用 CSV 模板批量创建 CP/TC 数据

### 1.3 前置条件

| 条件 | 说明 |
|------|------|
| Tracker 服务运行中 | 8080 (生产) 或 8081 (测试) |
| 管理员账户 | 拥有项目创建、用户管理权限 |
| 迁移数据 | 已整理为标准格式的 CSV 文件 |

### 1.4 迁移流程概览

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. 创建项目    │ ──▶ │  2. 导入 CP     │ ──▶ │  3. 导入 TC     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  6. 数据验证    │ ◀─── │  5. 关联 CP    │ ◀─── │  4. 批量导入    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

### 1.5 标准迁移流程（必须严格遵守）

```
┌─────────────────────────────────────────────────────────────────────┐
│                        标准迁移流程                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐                                                  │
│   │  步骤 1      │   迁移外部数据到测试环境（test_data）              │
│   │  数据迁移    │   - 使用 API 在 8081 端口创建项目                  │
│   │              │   - 导入 CP/TC 数据                                │
│   │              │   - 执行自检脚本验证迁移正确性                      │
│   └──────┬───────┘                                                  │
│          │ 自检通过                                                  │
│          ▼                                                          │
│   ┌──────────────┐                                                  │
│   │  步骤 2      │   通知系统管理员验证                                │
│   │  管理员验证  │   - 管理员登录测试环境 (8081)                      │
│   │              │   - 检查 CP/TC 数据完整性                         │
│   │              │   - 如有问题 → 返回步骤 1                          │
│   └──────┬───────┘                                                  │
│          │ 验证通过                                                  │
│          ▼                                                          │
│   ┌──────────────┐                                                  │
│   │  步骤 3      │   管理员部署到生产环境                            │
│   │  生产部署    │   - 参考《测试到生产部署指南》                     │
│   │              │   - 将项目从 test_data 复制到 user_data           │
│   │              │   - 验证生产环境正常工作                           │
│   └──────────────┘                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**详细说明**：

| 步骤 | 操作 | 负责人 | 说明 |
|------|------|--------|------|
| 步骤 1 | 数据迁移到测试环境 | AI/管理员 | 使用 API 在 8081 端口操作 test_data |
| 步骤 1.1 | 自检 | AI | 运行验证脚本确保迁移正确 |
| 步骤 2 | 管理员验证 | 人类管理员 | 登录 8081 检查数据完整性 |
| 步骤 2.1 | 问题处理 | AI/管理员 | 如有问题，返回步骤 1 重新迁移 |
| 步骤 3 | 生产部署 | 人类管理员 | 使用部署脚本迁移到生产 |

> ⚠️ **关键原则**：
> - 测试环境 (8081) 和生产环境 (8080) **完全隔离**
> - **严禁**直接操作生产环境 (8080)
> - 所有迁移操作必须在测试环境完成并验证通过后，才能部署到生产

---

## 2. 环境准备

### 2.1 服务地址

| 环境 | 地址 | 说明 |
|------|------|------|
| 生产 | `http://localhost:8080` | 使用 user_data |
| 测试 | `http://localhost:8081` | 使用 test_data |

本文档以测试环境为例，生产环境只需更换端口。

### 2.2 认证获取

Tracker 使用 Session-based 认证，需要先登录获取 Cookie。

**登录 API**:
```bash
curl -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  -c cookies.txt  # 保存 Cookie 到文件
```

**成功响应**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "is_active": 1
  }
}
```

**后续请求**: 使用保存的 Cookie 进行认证
```bash
curl http://localhost:8081/api/projects \
  -b cookies.txt  # 读取 Cookie
```

### 2.3 工具准备

推荐使用以下工具：

| 工具 | 用途 | 安装 |
|------|------|------|
| curl | 命令行 HTTP 请求 | 系统自带 |
| Python + requests | 脚本化批量操作 | `pip install requests` |
| Postman | API 调试 | 官网下载 |

### 2.4 Cookie 管理脚本

创建 `login.py` 简化认证流程：

```python
#!/usr/bin/env python3
"""Tracker API 认证辅助脚本"""
import requests

BASE_URL = "http://localhost:8081"
COOKIE_FILE = "cookies.txt"

def login(username="admin", password="admin123"):
    """登录并保存 Cookie"""
    session = requests.Session()
    resp = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    if resp.json().get("success"):
        # 保存 Cookie 到文件
        with open(COOKIE_FILE, "w") as f:
            for cookie in session.cookies:
                f.write(f"{cookie.name}\t{cookie.value}\n")
        print(f"✅ 登录成功: {username}")
        return session
    else:
        print(f"❌ 登录失败: {resp.json()}")
        return None

def load_session():
    """从文件加载会话"""
    session = requests.Session()
    try:
        with open(COOKIE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    session.cookies.set(parts[0], parts[1])
        return session
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    import sys
    user = sys.argv[1] if len(sys.argv) > 1 else "admin"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    login(user, pwd)
```

---

## 3. API基础 - 项目管理

### 3.1 项目列表查询

**API**: `GET /api/projects`

```bash
curl http://localhost:8081/api/projects -b cookies.txt
```

**响应**:
```json
[
  {
    "id": 1,
    "name": "Demo_Project",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "created_at": "2026-02-01 10:00:00",
    "is_archived": false
  }
]
```

### 3.2 创建新项目

**API**: `POST /api/projects`

**必填字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 项目名称 |
| start_date | string | 开始日期 (YYYY-MM-DD) |
| end_date | string | 结束日期 (YYYY-MM-DD) |

**可选字段**:
| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| create_test_user | boolean | false | 是否创建测试用户 |

**请求示例**:
```bash
curl -X POST http://localhost:8081/api/projects \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Chip_A_Verification",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "create_test_user": true
  }'
```

**成功响应**:
```json
{
  "success": true,
  "project": {
    "id": 5,
    "name": "Chip_A_Verification",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31"
  },
  "test_user": {
    "username": "test_user_chip_a_verification",
    "password": "test_user123",
    "role": "user"
  }
}
```

**注意事项**:
- 项目名称必须唯一
- 日期格式必须为 `YYYY-MM-DD`
- 创建项目时会自动初始化数据库

### 3.3 获取项目详情

**API**: `GET /api/projects/{id}`

```bash
curl http://localhost:8081/api/projects/5 -b cookies.txt
```

### 3.4 更新项目信息

**API**: `PUT /api/projects/{id}`

```bash
curl -X PUT http://localhost:8081/api/projects/5 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "end_date": "2027-06-30"
  }'
```

### 3.5 删除项目（⚠️ 严禁使用）

**API**: `DELETE /api/projects/{id}`

```bash
curl -X DELETE http://localhost:8081/api/projects/5 -b cookies.txt
```

> 🚫 **【严禁使用】** 此 API **禁止在迁移流程中使用**！
>
> **原因**：
> - 删除项目会同时删除所有关联的 CP 和 TC 数据，**此操作不可恢复**
> - 误删会导致历史验证数据永久丢失
>
> **正确处理方式**：
> - 如需删除有问题的测试项目，请**通知人类管理员**来处理
> - 管理员确认后，由管理员手动执行删除操作
> - 生产环境的项目**绝对禁止**通过 API 删除

---

## 4. Cover Point 导入

### 4.1 CP 数据结构

**必填字段**:
| 字段 | 说明 |
|------|------|
| feature | Feature 名称 |
| cover_point | Cover Point 名称 |

**可选字段**:
| 字段 | 说明 |
|------|------|
| sub_feature | Sub-Feature 名称 |
| cover_point_details | 详细说明 |
| priority | 优先级 (P0/P1/P2，默认 P0) |
| comments | 备注 |

### 4.2 单个 CP 创建

**API**: `POST /api/cp`

```bash
curl -X POST http://localhost:8081/api/cp \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "feature": "Clock",
    "sub_feature": "PLL",
    "cover_point": "CP_CLK_PLL_LOCK",
    "cover_point_details": "PLL 锁定检查点",
    "priority": "P0",
    "comments": "关键路径"
  }'
```

### 4.3 批量导入 CP

Tracker 内置了 CSV/Excel 导入功能，推荐使用此方式。

**API**: `POST /api/import`

**请求体**:
```json
{
  "project_id": 5,
  "type": "cp",
  "file_data": "<base64编码的CSV内容>"
}
```

**Python 批量导入脚本**:

```python
#!/usr/bin/env python3
"""CP 批量导入脚本"""
import base64
import csv
import io
import requests

BASE_URL = "http://localhost:8081"

def import_cp_batch(project_id, csv_file, cookies):
    """批量导入 CP"""
    # 读取 CSV 文件
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_content = f.read()
    
    # Base64 编码
    file_data = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    
    # 发送请求
    resp = requests.post(
        f"{BASE_URL}/api/import",
        json={
            "project_id": project_id,
            "type": "cp",
            "file_data": file_data
        },
        cookies=cookies
    )
    
    result = resp.json()
    print(f"导入结果: {result}")
    return result

if __name__ == "__main__":
    import json
    
    # 加载会话
    with open("cookies.txt", "r") as f:
        cookies = {}
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                cookies[parts[0]] = parts[1]
    
    # 执行导入
    result = import_cp_batch(5, "cp_template.csv", cookies)
    print(f"成功: {result.get('imported')}, 失败: {result.get('failed')}")
```

### 4.4 CSV 格式要求

CP 导入的 CSV 格式：

```csv
Feature,Sub-Feature,Cover Point,Cover Point Details,Comments
Clock,PLL,CP_CLK_PLL_LOCK,PLL锁定检查点,关键路径
Clock,PLL,CP_CLK_PLL_BYPASS,PLL旁路检查点,
Clock,DMA,CP_CLK_DMA_ENABLE,DMA时钟门控,
```

| 列序 | 字段 | 必填 | 说明 |
|------|------|------|------|
| 1 | Feature | ✅ | Feature 名称 |
| 2 | Sub-Feature | ❌ | Sub-Feature 名称 |
| 3 | Cover Point | ✅ | CP 名称（唯一） |
| 4 | Cover Point Details | ❌ | 详细说明 |
| 5 | Comments | ❌ | 备注 |

### 4.5 获取 CP 列表

**API**: `GET /api/cp?project_id={id}`

```bash
curl "http://localhost:8081/api/cp?project_id=5" -b cookies.txt
```

**响应**:
```json
[
  {
    "id": 1,
    "project_id": 5,
    "feature": "Clock",
    "sub_feature": "PLL",
    "cover_point": "CP_CLK_PLL_LOCK",
    "cover_point_details": "PLL锁定检查点",
    "priority": "P0",
    "coverage": 0,
    "coverage_detail": "0/0",
    "created_at": "2026-03-05 10:00:00"
  }
]
```

---

## 5. Test Case 导入

### 5.1 TC 数据结构

**必填字段**:
| 字段 | 说明 |
|------|------|
| testbench | TestBench 名称 |
| test_name | Test Case 名称 |

**可选字段**:
| 字段 | 说明 |
|------|------|
| category | 类别 (如 Sanity/Regression) |
| owner | 负责人 |
| scenario_details | 场景描述 |
| checker_details | 检查器描述 |
| coverage_details | 覆盖率描述 |
| target_date | 目标日期 (YYYY-MM-DD) |
| dv_milestone | DV 里程碑 (如 DV0.5/DV1.0) |
| status | 状态 (默认 OPEN) |
| connections | 关联的 CP ID 列表 |

### 5.2 单个 TC 创建

**API**: `POST /api/tc`

```bash
curl -X POST http://localhost:8081/api/tc \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "testbench": "TB_CLOCK",
    "category": "Sanity",
    "owner": "TestEng1",
    "test_name": "TC_CLK_PLL_LOCK_001",
    "scenario_details": "验证 PLL 锁定功能",
    "target_date": "2026-03-31",
    "dv_milestone": "DV0.5",
    "connections": [1]
  }'
```

> **重要**: `connections` 字段用于关联 CP，值为 CP 的 ID 列表。

### 5.3 批量导入 TC

**API**: `POST /api/import` (type: "tc")

**Python 批量导入脚本**:

```python
#!/usr/bin/env python3
"""TC 批量导入脚本"""
import base64
import requests

BASE_URL = "http://localhost:8081"

def import_tc_batch(project_id, csv_file, cookies):
    """批量导入 TC"""
    with open(csv_file, "r", encoding="utf-8") as f:
        csv_content = f.read()
    
    file_data = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    
    resp = requests.post(
        f"{BASE_URL}/api/import",
        json={
            "project_id": project_id,
            "type": "tc",
            "file_data": file_data
        },
        cookies=cookies
    )
    
    return resp.json()

if __name__ == "__main__":
    with open("cookies.txt", "r") as f:
        cookies = {}
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                cookies[parts[0]] = parts[1]
    
    result = import_tc_batch(5, "tc_template.csv", cookies)
    print(f"成功: {result.get('imported')}, 失败: {result.get('failed')}")
```

### 5.4 CSV 格式要求

TC 导入的 CSV 格式：

```csv
TestBench,Category,Owner,Test Name,Scenario Details,Checker Details,Coverage Details,Comments,Target Date,DV Milestone,Status
TB_CLOCK,Sanity,TestEng1,TC_CLK_PLL_LOCK_001,验证PLL锁定功能,检查lock信号,覆盖率到100%,,2026-03-31,DV0.5,OPEN
TB_CLOCK,Sanity,TestEng1,TC_CLK_PLL_BYPASS_001,验证PLL旁路功能,检查bypass信号,,,2026-04-15,DV0.5,OPEN
TB_DMA,Regression,TestEng2,TC_DMA_TRANSFER_001,验证DMA传输,检查数据完整性,,,2026-05-01,DV1.0,CODED
```

| 列序 | 字段 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| 1 | TestBench | ✅ | - | 测试台名称 |
| 2 | Category | ❌ | (空) | 类别 |
| 3 | Owner | ❌ | (空) | 负责人 |
| 4 | Test Name | ✅ | - | TC 名称（唯一） |
| 5 | Scenario Details | ❌ | (空) | 场景描述 |
| 6 | Checker Details | ❌ | (空) | 检查器描述 |
| 7 | Coverage Details | ❌ | (空) | 覆盖率描述 |
| 8 | Comments | ❌ | (空) | 备注 |
| 9 | Target Date | ❌ | (空) | 目标日期 |
| 10 | DV Milestone | ❌ | (空) | DV 里程碑 |
| 11 | Status | ❌ | OPEN | 状态 |

### 5.5 TC 状态更新

**API**: `POST /api/tc/{id}/status`

```bash
curl -X POST http://localhost:8081/api/tc/1/status \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "status": "PASS"
  }'
```

**状态值**: `OPEN` | `CODED` | `PASS` | `FAIL` | `REMOVED`

> **注意**: 更新状态时，系统会自动记录日期（CODED → coded_date, PASS → pass_date 等）

### 5.6 TC 关联 CP

在创建 TC 时通过 `connections` 字段关联，或单独更新：

**API**: `PUT /api/tc/{id}`

```bash
curl -X PUT http://localhost:8081/api/tc/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "connections": [1, 2, 3]
  }'
```

### 5.7 获取 TC 列表

**API**: `GET /api/tc?project_id={id}`

```bash
curl "http://localhost:8081/api/tc?project_id=5" -b cookies.txt
```

**过滤参数**:
| 参数 | 说明 | 示例 |
|------|------|------|
| status | 按状态过滤 | `?status=PASS` |
| dv_milestone | 按里程碑过滤 | `?dv_milestone=DV1.0` |
| owner | 按负责人过滤 | `?owner=TestEng1` |
| category | 按类别过滤 | `?category=Sanity` |

---

## 6. 批量操作与脚本

### 6.1 批量更新 TC 状态

**API**: `POST /api/tc/batch/status`

```bash
curl -X POST http://localhost:8081/api/tc/batch/status \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "tc_ids": [1, 2, 3],
    "status": "PASS"
  }'
```

### 6.2 批量更新 Target Date

**API**: `POST /api/tc/batch/target_date`

```bash
curl -X POST http://localhost:8081/api/tc/batch/target_date \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "tc_ids": [1, 2, 3],
    "target_date": "2026-06-30"
  }'
```

### 6.3 批量更新 Priority

**API**: `POST /api/cp/batch/priority`

```bash
curl -X POST http://localhost:8081/api/cp/batch/priority \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "cp_ids": [1, 2, 3],
    "priority": "P1"
  }'
```

### 6.4 一键迁移脚本

以下是一个完整的数据迁移脚本示例：

```python
#!/usr/bin/env python3
"""
Tracker 数据迁移脚本
功能: 从 CSV 文件批量迁移 CP 和 TC 数据到 Tracker
"""
import base64
import json
import sys
import requests

# ============ 配置 ============
BASE_URL = "http://localhost:8081"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
PROJECT_NAME = "Chip_A_Verification"
START_DATE = "2026-01-01"
END_DATE = "2026-12-31"
# ==============================

class TrackerMigration:
    def __init__(self):
        self.session = None
        self.project_id = None
    
    def login(self, username, password):
        """登录"""
        self.session = requests.Session()
        resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password}
        )
        if resp.json().get("success"):
            print(f"✅ 登录成功: {username}")
            return True
        print(f"❌ 登录失败: {resp.json()}")
        return False
    
    def create_project(self, name, start_date, end_date):
        """创建项目"""
        resp = self.session.post(
            f"{BASE_URL}/api/projects",
            json={
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "create_test_user": True
            }
        )
        result = resp.json()
        if result.get("success"):
            self.project_id = result["project"]["id"]
            print(f"✅ 项目创建成功: {name} (ID: {self.project_id})")
            if result.get("test_user"):
                tu = result["test_user"]
                print(f"   测试用户: {tu['username']} / {tu['password']}")
            return True
        print(f"❌ 项目创建失败: {result.get('error')}")
        return False
    
    def import_csv(self, import_type, csv_file):
        """导入 CSV"""
        with open(csv_file, "r", encoding="utf-8") as f:
            csv_content = f.read()
        
        file_data = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
        
        resp = self.session.post(
            f"{BASE_URL}/api/import",
            json={
                "project_id": self.project_id,
                "type": import_type,
                "file_data": file_data
            }
        )
        
        result = resp.json()
        imported = result.get("imported", 0)
        failed = result.get("failed", 0)
        errors = result.get("errors", [])
        
        print(f"📊 {import_type.upper()} 导入结果: 成功 {imported}, 失败 {failed}")
        if errors:
            for err in errors[:5]:  # 只显示前5个错误
                print(f"   - {err}")
            if len(errors) > 5:
                print(f"   ... 共 {len(errors)} 个错误")
        
        return imported > 0
    
    def verify_stats(self):
        """验证统计数据"""
        resp = self.session.get(
            f"{BASE_URL}/api/stats",
            params={"project_id": self.project_id}
        )
        stats = resp.json()
        print(f"\n📈 项目统计:")
        print(f"   CP 总数: {stats.get('total_cp')}")
        print(f"   TC 总数: {stats.get('total_tc')}")
        print(f"   通过率: {stats.get('pass_rate')}")
        print(f"   覆盖率: {stats.get('coverage')}")
        return stats
    
    def run(self, cp_csv, tc_csv):
        """执行迁移"""
        # 1. 登录
        if not self.login(ADMIN_USER, ADMIN_PASS):
            return False
        
        # 2. 创建项目
        if not self.create_project(PROJECT_NAME, START_DATE, END_DATE):
            return False
        
        # 3. 导入 CP
        if cp_csv:
            print(f"\n📥 开始导入 CP: {cp_csv}")
            self.import_csv("cp", cp_csv)
        
        # 4. 导入 TC
        if tc_csv:
            print(f"\n📥 开始导入 TC: {tc_csv}")
            self.import_csv("tc", tc_csv)
        
        # 5. 验证统计
        self.verify_stats()
        
        print(f"\n✅ 迁移完成!")
        return True

if __name__ == "__main__":
    migration = TrackerMigration()
    
    # 从命令行参数获取 CSV 文件
    cp_file = sys.argv[1] if len(sys.argv) > 1 else "cp_template.csv"
    tc_file = sys.argv[2] if len(sys.argv) > 2 else "tc_template.csv"
    
    migration.run(cp_file, tc_file)
```

**使用方法**:
```bash
python3 migrate.py cp_data.csv tc_data.csv
```

---

## 7. CSV标准模板

### 7.1 项目模板

项目通过 API 创建，CSV 仅用于记录参考：

```csv
Project Name,Start Date,End Date,Description
Chip_A_Verification,2026-01-01,2026-12-31,芯片A验证项目
```

### 7.2 CP 导入模板

**文件**: `cp_template.csv`

```csv
Feature,Sub-Feature,Cover Point,Cover Point Details,Comments
Clock,PLL,CP_CLK_PLL_LOCK,PLL锁定检查点,关键时序路径
Clock,PLL,CP_CLK_PLL_BYPASS,PLL旁路模式检查,
Clock,DMA,CP_CLK_DMA_ACTIVE,DMA活跃时钟检查,
Reset,PowerOn,CP_RST_POR,上电复位检查,
Reset,PowerOn,CP_RST_WDT,看门狗复位检查,
Interface,UART,CP_UART_TX_READY,UART发送就绪检查,
Interface,UART,CP_UART_RX_READY,UART接收就绪检查,
Interface,SPI,CP_SPI_MOSI,spi数据发送检查,
Memory,SRAM,CP_MEM_SRAM_READ,SRAM读操作检查,
Memory,SRAM,CP_MEM_SRAM_WRITE,SRAM写操作检查,
```

### 7.3 TC 导入模板

**文件**: `tc_template.csv`

```csv
TestBench,Category,Owner,Test Name,Scenario Details,Checker Details,Coverage Details,Comments,Target Date,DV Milestone,Status
TB_CLOCK,Sanity,TestEng1,TC_CLK_PLL_LOCK_001,验证PLL锁定功能,检查lock信号稳定,覆盖率100%,关键测试,2026-03-31,DV0.5,OPEN
TB_CLOCK,Sanity,TestEng1,TC_CLK_PLL_LOCK_002,验证PLL失锁恢复,检查失锁后恢复,覆盖率90%,,2026-04-15,DV0.5,OPEN
TB_CLOCK,Regression,TestEng1,TC_CLK_PLL_BYPASS_001,验证PLL旁路模式,检查旁路切换,覆盖率80%,,2026-04-30,DV0.5,CODED
TB_RESET,Sanity,TestEng2,TC_RST_POR_001,验证上电复位,检查复位信号,覆盖率100%,,2026-03-15,DV0.5,PASS
TB_RESET,Regression,TestEng2,TC_RST_WDT_001,验证看门狗复位,检查超时复位,覆盖率85%,,2026-04-20,DV1.0,OPEN
TB_UART,Integration,TestEng3,TC_UART_TX_001,验证UART发送,检查数据发送正确性,覆盖率95%,,2026-05-01,DV1.0,OPEN
TB_UART,Integration,TestEng3,TC_UART_RX_001,验证UART接收,检查数据接收正确性,覆盖率95%,,2026-05-01,DV1.0,OPEN
TB_DMA,Sanity,TestEng4,TC_DMA_MEM2MEM_001,验证DMA内存传输,检查数据完整性,覆盖率100%,,2026-05-15,DV1.0,OPEN
TB_SRAM,Regression,TestEng4,TC_SRAM_READ_001,验证SRAM读操作,检查读数据正确性,覆盖率90%,,2026-06-01,DV1.0,OPEN
TB_SRAM,Regression,TestEng4,TC_SRAM_WRITE_001,验证SRAM写操作,检查写数据正确性,覆盖率90%,,2026-06-01,DV1.0,OPEN
```

### 7.4 模板下载 API

也可以通过 API 下载官方模板：

```bash
# 下载 CP 模板
curl "http://localhost:8081/api/import/template?type=cp" \
  -b cookies.txt \
  -o cp_template.xlsx

# 下载 TC 模板  
curl "http://localhost:8081/api/import/template?type=tc" \
  -b cookies.txt \
  -o tc_template.xlsx
```

---

## 8. 迁移验证

### 8.1 统计数据校验

**API**: `GET /api/stats?project_id={id}`

```bash
curl "http://localhost:8081/api/stats?project_id=5" -b cookies.txt
```

**响应**:
```json
{
  "total_cp": 10,
  "total_tc": 20,
  "open_tc": 8,
  "coded_tc": 5,
  "fail_tc": 2,
  "pass_tc": 5,
  "pass_rate": "25.0%",
  "coverage": "45.5%"
}
```

### 8.2 数据完整性检查脚本

```python
#!/usr/bin/env python3
"""数据校验脚本"""
import requests

BASE_URL = "http://localhost:8081"

def verify_migration(project_id, expected_cp, expected_tc):
    """验证迁移结果"""
    session = requests.Session()
    with open("cookies.txt", "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                session.cookies.set(parts[0], parts[1])
    
    # 获取统计数据
    stats = session.get(
        f"{BASE_URL}/api/stats",
        params={"project_id": project_id}
    ).json()
    
    # 获取 CP 列表
    cps = session.get(
        f"{BASE_URL}/api/cp",
        params={"project_id": project_id}
    ).json()
    
    # 获取 TC 列表
    tcs = session.get(
        f"{BASE_URL}/api/tc",
        params={"project_id": project_id}
    ).json()
    
    print("=" * 50)
    print("📊 迁移验证报告")
    print("=" * 50)
    print(f"项目 ID: {project_id}")
    print("-" * 50)
    
    # CP 验证
    cp_match = stats["total_cp"] == expected_cp
    print(f"CP 数量: {stats['total_cp']} / 预期 {expected_cp} {'✅' if cp_match else '❌'}")
    
    # TC 验证
    tc_match = stats["total_tc"] == expected_tc
    print(f"TC 数量: {stats['total_tc']} / 预期 {expected_tc} {'✅' if tc_match else '❌'}")
    
    print("-" * 50)
    print(f"通过率: {stats['pass_rate']}")
    print(f"覆盖率: {stats['coverage']}")
    print("-" * 50)
    
    # 检查未关联 TC
    unconnected = [t for t in tcs if not t.get("connected_cps")]
    if unconnected:
        print(f"⚠️  未关联 CP 的 TC: {len(unconnected)} 个")
        for t in unconnected[:5]:
            print(f"   - {t['test_name']}")
    
    print("=" * 50)
    
    return cp_match and tc_match

if __name__ == "__main__":
    import sys
    pid = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    ecp = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    etc = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    verify_migration(pid, ecp, etc)
```

**使用方法**:
```bash
python3 verify.py 5 10 20
```

### 8.3 常见校验问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| CP 数量不匹配 | CSV 中有重复 Cover Point | 检查 CSV 去重 |
| TC 数量不匹配 | CSV 中有重复 Test Name | 检查 CSV 去重 |
| 未关联 CP | TC 创建时未指定 connections | 使用 PUT /api/tc 更新关联 |
| 覆盖率显示 0/0 | TC 状态非 PASS | 更新 TC 状态为 PASS |

---

## 9. 附录

### 9.1 完整 curl 示例

```bash
#!/bin/bash
# Tracker API 完整示例

BASE_URL="http://localhost:8081"
COOKIE_FILE="cookies.txt"

# 1. 登录
echo "1. 登录..."
curl -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c $COOKIE_FILE

# 2. 创建项目
echo -e "\n2. 创建项目..."
curl -X POST "$BASE_URL/api/projects" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d '{
    "name":"My_Project",
    "start_date":"2026-01-01",
    "end_date":"2026-12-31"
  }'

# 3. 导入 CP
echo -e "\n3. 导入 CP..."
PROJECT_ID=6  # 替换为实际项目 ID
BASE64_CP=$(base64 -w0 cp_template.csv)
curl -X POST "$BASE_URL/api/import" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d "{\"project_id\":$PROJECT_ID,\"type\":\"cp\",\"file_data\":\"$BASE64_CP\"}"

# 4. 导入 TC
echo -e "\n4. 导入 TC..."
BASE64_TC=$(base64 -w0 tc_template.csv)
curl -X POST "$BASE_URL/api/import" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d "{\"project_id\":$PROJECT_ID,\"type\":\"tc\",\"file_data\":\"$BASE64_TC\"}"

# 5. 查询统计
echo -e "\n5. 查询统计..."
curl "$BASE_URL/api/stats?project_id=$PROJECT_ID" -b $COOKIE_FILE

# 6. 登出
echo -e "\n6. 登出..."
curl -X POST "$BASE_URL/api/auth/logout" -b $COOKIE_FILE
```

### 9.2 错误码说明

| 错误码 | 说明 | 常见原因 |
|--------|------|----------|
| 400 | 请求参数错误 | 缺少必填字段、日期格式错误 |
| 401 | 未授权 | 未登录或 Cookie 过期 |
| 403 | 权限不足 | 非管理员操作需要管理员权限的 API |
| 404 | 资源不存在 | 项目/CP/TC ID 不存在 |
| 409 | 冲突 | 项目名称重复、CP/TC 名称重复 |

### 9.3 字段映射表

#### Excel/CSV → Tracker API 字段映射

| Excel/CSV 列 | API 字段 | 必填 | 说明 |
|--------------|----------|------|------|
| Feature | feature | ✅ | Feature 名称 |
| Cover Point | cover_point | ✅ | CP 名称 |
| TestBench | testbench | ✅ | 测试台名称 |
| Test Name | test_name | ✅ | TC 名称 |

---

*文档版本: v1.0*
*最后更新: 2026-03-05*
