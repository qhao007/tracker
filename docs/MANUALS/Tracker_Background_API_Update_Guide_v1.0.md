# Tracker 后台 API 批量更新指南

> **版本**: v1.0  
> **适用版本**: Tracker v0.11.0+  
> **创建日期**: 2026-04-06  
> **文档类型**: 操作指南

---

## 目录

1. [概述](#1-概述)
2. [认证方式](#2-认证方式)
3. [更新 FC 覆盖率数据](#3-更新-fc-覆盖率数据)
4. [更新 TC 状态](#4-更新-tc-状态)
5. [自动化脚本](#5-自动化脚本)
6. [常见问题](#6-常见问题)

---

## 1. 概述

### 1.1 目的

本文档介绍如何通过 Tracker API 在后台自动更新：
- **FC Items**：Functional Coverage 的 coverage_pct 和 status
- **TC 状态**：Test Case 的执行状态（OPEN/CODED/FAIL/PASS/REMOVED）

### 1.2 适用场景

| 场景 | 说明 |
|------|------|
| CI/CD 集成 | 仿真完成后自动更新 FC coverage_pct |
| 覆盖率收集 | 从覆盖率工具导出数据后批量更新 |
| 测试结果同步 | 回归测试完成后批量更新 TC 状态 |
| 定时任务 | 定期抓取外部数据源更新 Tracker |

### 1.3 前置条件

| 条件 | 说明 |
|------|------|
| Tracker 服务运行中 | 8080 (生产) 或 8081 (测试) |
| 有效会话 Cookie | 通过登录获取的 session cookie |
| 项目为 FC-CP 模式 | 更新 FC 需要 `coverage_mode = fc_cp` |

### 1.4 可用 API 端点

| 功能 | 方法 | 路径 |
|------|------|------|
| 批量更新 FC | `PUT` | `/api/fc/batch` |
| 单个 TC 状态更新 | `POST` | `/api/tc/<id>/status` |
| 批量 TC 状态更新 | `POST` | `/api/tc/batch/status` |
| 单个 TC 完整更新 | `PUT` | `/api/tc/<id>` |
| 获取 TC 列表 | `GET` | `/api/tc` |

---

## 2. 认证方式

### 2.1 Session Cookie 认证

后台 API 需要登录获取 session cookie。

**登录 API**: `POST /api/auth/login`

```bash
curl -X POST "http://localhost:8081/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}' \
  -c cookies.txt \
  -w "\n%{http_code}"
```

**响应示例**:
```json
{"success": true, "user": {"id": 1, "username": "admin", "role": "admin"}}
```

**保存 Cookie**: 使用 `-c cookies.txt` 保存 session cookie，后续请求使用 `-b cookies.txt` 读取。

### 2.2 Cookie 文件格式

```
# Netscape HTTP Cookie File
.domain.com	TRUE	/	FALSE	0	session	abc123...
```

### 2.3 登出

```bash
curl -X POST "http://localhost:8081/api/auth/logout" -b cookies.txt
```

---

## 3. 更新 FC 覆盖率数据

> **前提**: 项目 `coverage_mode` 必须为 `fc_cp`

### 3.1 批量更新 FC (PUT /api/fc/batch)

**功能**: 批量更新 FC items 的 `coverage_pct` 和 `status`

**请求体**:
```json
{
  "project_id": 5,
  "items": [
    {
      "id": 1,
      "coverage_pct": 98.5,
      "status": "ready"
    },
    {
      "id": 2,
      "coverage_pct": 85.0
    },
    {
      "id": 3,
      "status": "missing"
    }
  ]
}
```

**参数说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | ✅ | 项目 ID |
| items | array | ✅ | FC items 数组 |
| items[].id | int | ✅ | FC item ID |
| items[].coverage_pct | float | ❌ | 覆盖率 (0-100) |
| items[].status | string | ❌ | 状态 (missing/ready) |

**至少提供 `coverage_pct` 或 `status` 之一。**

**示例**:
```bash
curl -X PUT "http://localhost:8081/api/fc/batch" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "items": [
      {"id": 1, "coverage_pct": 98.5, "status": "ready"},
      {"id": 2, "coverage_pct": 85.0},
      {"id": 3, "status": "missing"}
    ]
  }'
```

**响应**:
```json
{
  "success": true,
  "updated": 3,
  "failed": 0,
  "errors": []
}
```

### 3.2 获取 FC 列表 (GET /api/fc)

获取项目所有 FC items，用于了解当前状态。

**示例**:
```bash
curl "http://localhost:8081/api/fc?project_id=5" -b cookies.txt
```

**响应**:
```json
{
  "success": true,
  "fc_items": [
    {
      "id": 1,
      "covergroup": "apb_protocol_cg",
      "coverpoint": "cp_addr_range",
      "bin_name": "addr_max",
      "coverage_pct": 95.0,
      "status": "ready"
    }
  ]
}
```

### 3.3 从 CSV 导入 FC 更新数据

外部覆盖率工具（如 Verdi、SimVision）导出的 CSV 可以转换为 API 调用。

**CSV 格式示例** (覆盖率工具导出):
```csv
covergroup,coverpoint,bin,coverage
apb_protocol_cg,cp_addr_range,addr_max,98.5
apb_protocol_cg,cp_addr_range,addr_mid,85.0
axi_protocol_cg,cp_burst_type,inc_burst,92.0
```

**Python 转换脚本**:
```python
#!/usr/bin/env python3
"""CSV 覆盖率数据转换为 FC batch update API 调用"""
import csv
import json
import requests
import sys

BASE_URL = "http://localhost:8081"
CSV_FILE = "coverage_data.csv"
PROJECT_ID = 5

def load_fc_mapping(project_id, cookies):
    """获取当前 FC 列表，建立 bin_name -> id 的映射"""
    resp = requests.get(f"{BASE_URL}/api/fc", params={"project_id": project_id}, cookies=cookies)
    data = resp.json()
    mapping = {}
    for fc in data.get("fc_items", []):
        key = f"{fc['covergroup']}::{fc['coverpoint']}::{fc['bin_name']}"
        mapping[key] = fc["id"]
    return mapping

def csv_to_api_data(csv_file, project_id, fc_mapping):
    """将 CSV 转换为 API 请求数据"""
    items = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['covergroup']}::{row['coverpoint']}::{row['bin']}"
            if key in fc_mapping:
                coverage = float(row.get("coverage", 0))
                status = "ready" if coverage >= 90 else "missing"
                items.append({
                    "id": fc_mapping[key],
                    "coverage_pct": coverage,
                    "status": status
                })
    return {"project_id": project_id, "items": items}

def batch_update(cookies, project_id, items):
    """调用 batch update API"""
    resp = requests.put(
        f"{BASE_URL}/api/fc/batch",
        json={"project_id": project_id, "items": items},
        cookies=cookies
    )
    return resp.json()

if __name__ == "__main__":
    # 加载 cookie
    cookies = {"session": open("session_cookie.txt").read().strip()}
    
    # 获取 FC 映射
    fc_mapping = load_fc_mapping(PROJECT_ID, cookies)
    print(f"Loaded {len(fc_mapping)} FC items")
    
    # 转换 CSV
    api_data = csv_to_api_data(CSV_FILE, PROJECT_ID, fc_mapping)
    print(f"Prepared {len(api_data['items'])} items for update")
    
    # 调用 API
    result = batch_update(cookies, PROJECT_ID, api_data["items"])
    print(f"Result: {result}")
```

---

## 4. 更新 TC 状态

### 4.1 单个 TC 状态更新 (POST /api/tc/<id>/status)

**路径**: `POST /api/tc/<tc_id>/status`

**请求体**:
```json
{
  "project_id": 5,
  "status": "PASS"
}
```

**有效状态值**: `OPEN`, `CODED`, `FAIL`, `PASS`, `REMOVED`

**示例**:
```bash
curl -X POST "http://localhost:8081/api/tc/123/status" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "status": "PASS"
  }'
```

**响应**:
```json
{
  "success": true,
  "status": "PASS",
  "need_confirm": false
}
```

**状态日期自动更新**:
| 状态 | 自动设置日期字段 |
|------|-----------------|
| CODED | coded_date |
| FAIL | fail_date |
| PASS | pass_date |
| REMOVED | removed_date |

### 4.2 批量 TC 状态更新 (POST /api/tc/batch/status)

**路径**: `POST /api/tc/batch/status`

**请求体**:
```json
{
  "project_id": 5,
  "tc_ids": [1, 2, 3, 4, 5],
  "status": "PASS"
}
```

**示例**:
```bash
curl -X POST "http://localhost:8081/api/tc/batch/status" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "project_id": 5,
    "tc_ids": [1, 2, 3, 4, 5],
    "status": "PASS"
  }'
```

**响应**:
```json
{
  "success": 5,
  "failed": 0
}
```

### 4.3 获取 TC 列表 (GET /api/tc)

获取项目 TC 列表，筛选特定状态的 TC。

**按状态筛选**:
```bash
curl "http://localhost:8081/api/tc?project_id=5&status=PASS" -b cookies.txt
```

**获取所有 TC**:
```bash
curl "http://localhost:8081/api/tc?project_id=5" -b cookies.txt
```

**Python 获取 TC 列表**:
```python
#!/usr/bin/env python3
"""获取 TC 列表并按状态分组"""
import requests

BASE_URL = "http://localhost:8081"
PROJECT_ID = 5

def get_tc_list(project_id, cookies, status=None):
    """获取 TC 列表"""
    params = {"project_id": project_id}
    if status:
        params["status"] = status
    
    resp = requests.get(f"{BASE_URL}/api/tc", params=params, cookies=cookies)
    data = resp.json()
    return data.get("test_cases", [])

def get_tc_summary(project_id, cookies):
    """获取 TC 状态汇总"""
    tc_list = get_tc_list(project_id, cookies)
    summary = {}
    for tc in tc_list:
        status = tc.get("status", "UNKNOWN")
        summary[status] = summary.get(status, 0) + 1
    return summary

if __name__ == "__main__":
    cookies = {"session": open("session_cookie.txt").read().strip()}
    
    # 获取汇总
    summary = get_tc_summary(PROJECT_ID, cookies)
    print(f"TC Summary: {summary}")
    
    # 获取所有 OPEN 的 TC
    open_tcs = get_tc_list(PROJECT_ID, cookies, status="OPEN")
    print(f"Open TCs: {len(open_tcs)}")
    for tc in open_tcs[:5]:
        print(f"  - {tc['id']}: {tc['test_name']}")
```

### 4.4 批量更新 TC 状态 (从外部测试系统)

**场景**: 外部测试系统（如 Jenkins、GitLab CI）运行回归测试后，需要将结果同步到 Tracker。

**CSV 格式** (测试系统导出):
```csv
test_name,result,duration
TC_SRAM_READ_001,PASS,120
TC_SRAM_READ_002,PASS,115
TC_SRAM_WRITE_001,FAIL,130
TC_SRAM_WRITE_002,PASS,125
```

**Python 批量更新脚本**:
```python
#!/usr/bin/env python3
"""从测试结果 CSV 批量更新 TC 状态"""
import csv
import requests
import sys

BASE_URL = "http://localhost:8081"
PROJECT_ID = 5

def get_tc_mapping(project_id, cookies):
    """建立 test_name -> id 的映射"""
    resp = requests.get(f"{BASE_URL}/api/tc", params={"project_id": project_id}, cookies=cookies)
    data = resp.json()
    mapping = {}
    for tc in data.get("test_cases", []):
        mapping[tc["test_name"]] = tc["id"]
    return mapping

def result_to_status(result):
    """测试结果映射到 TC 状态"""
    mapping = {
        "PASS": "PASS",
        "FAIL": "FAIL",
        "BLOCKED": "OPEN",
        "SKIPPED": "REMOVED"
    }
    return mapping.get(result.upper(), "OPEN")

def batch_update_tc_status(project_id, cookies, tc_ids, status):
    """批量更新 TC 状态"""
    resp = requests.post(
        f"{BASE_URL}/api/tc/batch/status",
        json={"project_id": project_id, "tc_ids": tc_ids, "status": status},
        cookies=cookies
    )
    return resp.json()

def process_test_results(csv_file, project_id, cookies):
    """处理测试结果 CSV"""
    # 获取 TC 映射
    tc_mapping = get_tc_mapping(project_id, cookies)
    
    # 按状态分组
    status_groups = {}
    
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_name = row["test_name"]
            result = row["result"]
            tc_status = result_to_status(result)
            
            if test_name in tc_mapping:
                if tc_status not in status_groups:
                    status_groups[tc_status] = []
                status_groups[tc_status].append(tc_mapping[test_name])
    
    # 批量更新
    for status, tc_ids in status_groups.items():
        result = batch_update_tc_status(project_id, cookies, tc_ids, status)
        print(f"Updated {result['success']} TCs to {status}")
        if result.get('failed', 0) > 0:
            print(f"  Failed: {result['failed']}")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "test_results.csv"
    cookies = {"session": open("session_cookie.txt").read().strip()}
    
    process_test_results(csv_file, PROJECT_ID, cookies)
```

---

## 5. 自动化脚本

### 5.1 完整自动化脚本

**场景**: 定时从覆盖率工具和测试系统获取数据，自动更新 Tracker。

```python
#!/usr/bin/env python3
"""
Tracker 自动更新脚本
- 定时从覆盖率工具更新 FC coverage_pct
- 定时从测试系统更新 TC 状态
"""
import os
import time
import requests
from datetime import datetime

BASE_URL = os.environ.get("TRACKER_URL", "http://localhost:8081")
COOKIE_FILE = "/path/to/cookies.txt"
PROJECT_ID = int(os.environ.get("TRACKER_PROJECT_ID", "5"))

def load_cookies():
    """加载 session cookie"""
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE) as f:
            session = f.read().strip()
            return {"session": session}
    return {}

def ensure_logged_in():
    """确保已登录"""
    cookies = load_cookies()
    # 测试是否有效
    resp = requests.get(f"{BASE_URL}/api/projects", cookies=cookies)
    if resp.status_code == 200:
        return cookies
    
    # 需要重新登录
    username = os.environ.get("TRACKER_USER", "admin")
    password = os.environ.get("TRACKER_PASS", "admin")
    
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    if resp.status_code == 200:
        # 保存 cookie
        cookies = resp.cookies
        with open(COOKIE_FILE, "w") as f:
            for name, value in cookies.items():
                if name == "session":
                    f.write(value)
        return cookies
    raise Exception("Login failed")

def update_fc_from_coverage_tool(cookies):
    """从覆盖率工具更新 FC"""
    # 示例：从文件读取覆盖率数据
    coverage_file = "/data/coverage/latest.csv"
    if not os.path.exists(coverage_file):
        print(f"Coverage file not found: {coverage_file}")
        return
    
    # 获取当前 FC 映射
    resp = requests.get(f"{BASE_URL}/api/fc", params={"project_id": PROJECT_ID}, cookies=cookies)
    fc_items = resp.json().get("fc_items", [])
    fc_mapping = {f"{fc['covergroup']}::{fc['coverpoint']}::{fc['bin_name']}": fc["id"] for fc in fc_items}
    
    # 解析覆盖率数据并准备更新
    import csv
    items = []
    with open(coverage_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['covergroup']}::{row['coverpoint']}::{row['bin']}"
            if key in fc_mapping:
                items.append({
                    "id": fc_mapping[key],
                    "coverage_pct": float(row.get("coverage", 0)),
                    "status": "ready" if float(row.get("coverage", 0)) >= 90 else "missing"
                })
    
    if not items:
        print("No FC items to update")
        return
    
    # 调用 batch update
    resp = requests.put(
        f"{BASE_URL}/api/fc/batch",
        json={"project_id": PROJECT_ID, "items": items},
        cookies=cookies
    )
    result = resp.json()
    print(f"FC Update: {result}")

def update_tc_from_test_system(cookies):
    """从测试系统更新 TC 状态"""
    test_results_file = "/data/test_results/latest.csv"
    if not os.path.exists(test_results_file):
        print(f"Test results file not found: {test_results_file}")
        return
    
    # 获取当前 TC 映射
    resp = requests.get(f"{BASE_URL}/api/tc", params={"project_id": PROJECT_ID}, cookies=cookies)
    tc_items = resp.json().get("test_cases", [])
    tc_mapping = {tc["test_name"]: tc["id"] for tc in tc_items}
    
    # 按状态分组
    status_groups = {}
    import csv
    with open(test_results_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_name = row["test_name"]
            result = row["result"].upper()
            status = "PASS" if result == "PASS" else ("FAIL" if result == "FAIL" else "OPEN")
            
            if test_name in tc_mapping:
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(tc_mapping[test_name])
    
    # 批量更新
    for status, tc_ids in status_groups.items():
        resp = requests.post(
            f"{BASE_URL}/api/tc/batch/status",
            json={"project_id": PROJECT_ID, "tc_ids": tc_ids, "status": status},
            cookies=cookies
        )
        result = resp.json()
        print(f"TC Update ({status}): {result}")

def main():
    print(f"[{datetime.now()}] Starting Tracker auto-update")
    
    cookies = ensure_logged_in()
    
    # 更新 FC
    update_fc_from_coverage_tool(cookies)
    
    # 更新 TC
    update_tc_from_test_system(cookies)
    
    print(f"[{datetime.now()}] Auto-update completed")

if __name__ == "__main__":
    main()
```

### 5.2 Crontab 配置

```bash
# 每天早上 8 点运行自动更新
0 8 * * * /usr/bin/python3 /opt/tracker/auto_update.py >> /var/log/tracker_auto_update.log 2>&1

# 每小时运行一次覆盖率同步（仅在 FC-CP 模式项目）
0 * * * * /usr/bin/python3 /opt/tracker/sync_coverage.py >> /var/log/tracker_coverage_sync.log 2>&1
```

### 5.3 CI/CD 集成示例 (GitLab CI)

```yaml
# .gitlab-ci.yml
coverage_sync:
  stage: deploy
  script:
    - python3 scripts/sync_coverage.py --project-id $TRACKER_PROJECT_ID
  environment:
    name: tracker-sync
  only:
    - tags
```

---

## 6. 常见问题

### Q1: 返回 "Not in FC-CP mode" 错误？

**原因**: 项目不是 FC-CP 模式，无法操作 FC 数据。

**解决方法**: 创建项目时指定 `coverage_mode: fc_cp`，或通过项目设置切换模式。

```bash
# 检查项目模式
curl "http://localhost:8081/api/projects/5" -b cookies.txt | jq '.coverage_mode'
```

### Q2: 批量更新时部分失败？

**响应示例**:
```json
{
  "success": false,
  "updated": 8,
  "failed": 2,
  "errors": [
    {"id": 5, "error": "FC item not found"},
    {"id": 10, "error": "Value must be between 0 and 100"}
  ]
}
```

**排查**: 检查 `errors` 数组，常见原因：
- ID 不存在
- coverage_pct 超出 0-100 范围
- status 值不是 missing/ready

### Q3: Session Cookie 过期？

**现象**: API 返回 401 Unauthorized

**解决方法**: 重新登录获取新 cookie

```python
def ensure_fresh_cookie():
    """确保 cookie 有效，失效则重新登录"""
    cookies = load_cookies()
    resp = requests.get(f"{BASE_URL}/api/projects", cookies=cookies)
    if resp.status_code != 200:
        return login()
    return cookies
```

### Q4: coverage_pct 更新后覆盖率没变化？

**可能原因**:
1. 项目是 TC-CP 模式，FC 数据不影响覆盖率计算
2. 缓存未刷新（刷新页面）

**检查项目模式**:
```bash
curl "http://localhost:8081/api/projects/5" -b cookies.txt | jq '{name, coverage_mode}'
```

### Q5: TC 状态更新后关联的 CP 覆盖率没变化？

**说明**: TC 状态变更后，需要重新计算覆盖率。如果 TC 关联了 CP，CP 的覆盖率会基于关联的 TC 状态重新计算。

**手动触发**: 访问项目页面，切换 Tab 触发重新渲染。

### Q6: 权限不足？

**现象**: API 返回 401 或 403

**原因**: 当前 session 用户权限不足

| 角色 | 可用操作 |
|------|----------|
| guest | 只读 |
| user | 更新 TC 状态 |
| admin | 所有操作 |

**解决方法**: 使用 admin 账户登录

---

## 附录

### A.1 完整 API 调用示例

```bash
#!/bin/bash
# Tracker API 完整调用示例

BASE_URL="http://localhost:8081"
COOKIE_FILE="cookies.txt"

# 1. 登录
echo "1. Logging in..."
curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  -c $COOKIE_FILE

# 2. 批量更新 FC
echo -e "\n2. Updating FC items..."
curl -s -X PUT "$BASE_URL/api/fc/batch" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d '{
    "project_id": 5,
    "items": [
      {"id": 1, "coverage_pct": 98.5, "status": "ready"},
      {"id": 2, "coverage_pct": 85.0}
    ]
  }'

# 3. 批量更新 TC 状态
echo -e "\n3. Updating TC status..."
curl -s -X POST "$BASE_URL/api/tc/batch/status" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d '{
    "project_id": 5,
    "tc_ids": [1, 2, 3],
    "status": "PASS"
  }'

# 4. 登出
echo -e "\n4. Logging out..."
curl -s -X POST "$BASE_URL/api/auth/logout" -b $COOKIE_FILE
```

### A.2 Python 依赖

```bash
pip install requests
```

### A.3 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| TRACKER_URL | Tracker 服务地址 | http://localhost:8081 |
| TRACKER_PROJECT_ID | 项目 ID | 5 |
| TRACKER_USER | 登录用户名 | admin |
| TRACKER_PASS | 登录密码 | admin |

---

*文档版本: v1.0*
*最后更新: 2026-04-06*
