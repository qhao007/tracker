# Tracker 测试到生产部署指南

> **版本**: v1.1  
> **适用版本**: Tracker v0.9.0+ (v0.11.0+ 新增 FC/Dashboard 验收)  
> **创建日期**: 2026-03-05  
> **更新日期**: 2026-04-03  
> **文档类型**: 操作指南

---

## 目录

1. [概述](#1-概述)
2. [环境说明](#2-环境说明)
3. [部署流程](#3-部署流程)
4. [手动部署步骤](#4-手动部署步骤)
5. [自动化部署脚本](#5-自动化部署脚本)
6. [飞书通知配置](#6-飞书通知配置)
7. [附录](#7-附录)

---

## 1. 概述

### 1.1 目的

本文档指导管理员如何将经过验证的测试项目（位于 `test_data` 目录）部署到生产环境（`user_data` 目录）。

### 1.2 适用范围

- **场景一**：迁移验证通过的项目到生产环境
- **场景二**：复制特定项目数据到生产环境
- **场景三**：批量部署多个已验证的项目

### 1.3 前置条件

| 条件 | 说明 |
|------|------|
| 测试项目已验证通过 | 参考《Tracker_API_项目创建迁移指南》完成验证 |
| 管理员权限 | 拥有服务器文件系统访问权限 |
| 生产环境可访问 | 能够访问 `/projects/management/tracker/shared/data/` |
| 飞书机器人配置 | 已配置飞书 webhook 接收通知 |

### 1.4 重要原则（🚫 严禁操作）

> ⚠️ **关键原则 - 必须严格遵守**：

| 操作 | 允许 | 说明 |
|------|------|------|
| 删除 test_data 数据 | ❌ **严禁** | 测试数据是验证依据，严禁删除 |
| 删除 user_data 数据 | ❌ **严禁** | 生产数据是红线，严禁删除 |
| 回滚操作 | ❌ **严禁** | 如需回滚，通知人类管理员处理 |
| 重启生产服务 | ❌ **严禁** | 如需重启，通过飞书通知管理员 |
| 复制/添加数据 | ✅ 允许 | 仅允许复制和添加操作 |

> **违反原则的后果**：可能导致数据永久丢失，系统不可用！

---

## 2. 环境说明

### 2.1 目录结构

```
/projects/management/tracker/shared/data/
├── test_data/              # 测试环境数据（只读操作）
│   ├── projects.json       # 项目列表配置文件
│   ├── *.db               # 项目数据库文件
│   └── sessions/          # 测试会话数据
│
└── user_data/              # 生产环境数据（只添加/复制）
    ├── projects.json       # 项目列表配置文件
    ├── *.db               # 项目数据库文件
    └── sessions/          # 生产会话数据
```

### 2.2 服务端口

| 环境 | 端口 | 数据目录 | 用途 |
|------|------|----------|------|
| 测试 | 8081 | test_data | 开发/验证 |
| 生产 | 8080 | user_data | 正式使用 |

---

## 3. 部署流程

### 3.1 标准部署流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                     测试到生产部署流程                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐                                                  │
│   │  步骤 1      │   确认测试项目验证通过                            │
│   │  验证确认    │   - 数据完整性检查通过                           │
│   │              │   - 管理员已在测试环境确认                         │
│   └──────┬───────┘                                                  │
│          │ 确认通过                                                  │
│          ▼                                                          │
│   ┌──────────────┐                                                  │
│   │  步骤 2      │   备份当前生产数据（仅复制，不删除）             │
│   │  数据备份    │   - 复制 projects.json 到备份目录                 │
│   │              │   - 复制即将覆盖的 db 文件                        │
│   └──────┬───────┘                                                  │
│          │ 备份完成                                                  │
│          ▼                                                          │
│   ┌──────────────┐                                                  │
│   │  步骤 3      │   执行部署脚本（仅添加/复制）                     │
│   │  执行部署    │   - 复制项目数据库到 user_data                   │
│   │              │   - 更新 projects.json（仅添加）                  │
│   └──────┬───────┘                                                  │
│          │ 部署完成                                                  │
│          ▼                                                          │
│   ┌──────────────┐                                                  │
│   │  步骤 4      │   飞书通知管理员                                 │
│   │  通知验证    │   - 发送部署结果到飞书群                         │
│   │              │   - 管理员登录验证                               │
│   └──────────────┘                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 关键约束

| 约束类型 | 说明 |
|----------|------|
| 只读测试数据 | 只能从 test_data 读取，不能删除 |
| 只写生产数据 | 只能添加到 user_data，不能删除现有数据 |
| 不重启服务 | 部署后不重启服务，由系统自动加载新数据 |
| 通知必达 | 部署成功/失败都必须通知管理员 |

---

## 4. 手动部署步骤

### 4.1 步骤 1：确认测试项目信息

在测试环境 (8081) 查询项目信息：

```bash
# 登录测试环境
curl -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c test_cookies.txt

# 获取项目列表
curl http://localhost:8081/api/projects -b test_cookies.txt

# 获取项目统计
curl "http://localhost:8081/api/stats?project_id=5" -b test_cookies.txt
```

记录以下信息：
- 项目名称 (name)
- 项目 ID (id)
- 开始/结束日期

### 4.2 步骤 2：查找测试项目数据库

```bash
# 列出测试数据目录中的数据库文件
ls -la /projects/management/tracker/shared/data/test_data/*.db

# 查找特定项目的数据库
ls -la /projects/management/tracker/shared/data/test_data/ | grep "项目名称"
```

> **注意**: 项目数据库文件名格式为 `{项目名称}.db`

### 4.3 步骤 3：备份当前生产数据（仅复制）

```bash
# 创建备份目录（只复制，不删除）
BACKUP_DIR="/projects/management/tracker/shared/data/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 仅复制 projects.json
cp /projects/management/tracker/shared/data/user_data/projects.json "$BACKUP_DIR/"

# 仅复制现有项目数据库（不删除）
cp /projects/management/tracker/shared/data/user_data/*.db "$BACKUP_DIR/" 2>/dev/null || true

echo "备份完成: $BACKUP_DIR"
```

> **注意**: 备份操作仅复制文件，不执行任何删除

### 4.4 步骤 4：复制项目数据库到生产环境

```bash
# 假设要迁移的项目名称为 "Chip_A_Verification"

# 复制数据库文件（仅添加，不覆盖）
cp /projects/management/tracker/shared/data/test_data/Chip_A_Verification.db \
   /projects/management/tracker/shared/data/user_data/

echo "数据库文件复制完成"
```

> **注意**: 如果文件已存在，脚本会报错，需要通知管理员处理

### 4.5 步骤 5：更新生产 projects.json（仅添加）

```bash
# 读取测试环境的 projects.json
TEST_PROJECTS="/projects/management/tracker/shared/data/test_data/projects.json"
USER_PROJECTS="/projects/management/tracker/shared/data/user_data/projects.json"

# 查看测试环境中的项目
cat "$TEST_PROJECTS" | python3 -m json.tool

# 手动将项目添加到生产环境（仅添加，不修改现有数据）
# 需要添加整个项目对象到数组中
```

> ⚠️ **手动操作风险较高，建议使用自动化脚本**

### 4.6 步骤 6：v0.11.0+ 功能验收（可选）

部署 v0.11.0+ 版本后，建议验证以下新功能：

#### FC Tab 页面验证

如果项目包含 FC（Functional Coverage）数据，验证以下功能：

| 检查项 | 操作 | 预期结果 |
|--------|------|----------|
| FC Tab 可见 | 切换到 FC Tab | 页面正常显示 |
| FC 数据加载 | 查看 FC 列表 | 显示 covergroup/coverpoint/bin 信息 |
| FC 筛选 | 使用筛选器 | 列表按条件过滤 |
| FC 导入/导出 | 测试 CSV 导入导出 | 功能正常 |

**覆盖率模式切换**（如项目需要）：
- 项目设置中可切换 `coverage_mode`（`tc_cp` / `fc_cp`）
- 切换后进度图表显示对应模式的覆盖率

#### Dashboard 页面验证

| 检查项 | 操作 | 预期结果 |
|--------|------|----------|
| Dashboard Tab 可见 | 切换到 Dashboard Tab | 页面正常显示 |
| 概览卡片 | 查看 4 项指标 | 显示总 CP/已覆盖/覆盖率/未关联 |
| Feature 分布图 | 查看横向柱状图 | 显示各 Feature 覆盖率 |
| Priority 分布 | 查看优先级卡片 | 显示 P0/P1/P2/P3 覆盖率 |
| 覆盖率趋势图 | 查看折线图 | 显示历史趋势（如有快照数据） |
| Top 5 未覆盖 | 查看列表 | 显示覆盖率最低的 CP |

#### 已知问题（BUG-128）

> ⚠️ **FC-CP 覆盖率计算存在已知问题**：在 `fc_cp` 覆盖率模式下，CP 覆盖率计算可能不准确。这是 v0.11.0 的已知问题，将在 v0.11.1 中修复。

如发现问题，请在项目设置中切换回 `tc_cp` 模式作为临时解决方案。

---

## 5. 自动化部署脚本

### 5.1 飞书通知配置

脚本需要配置飞书 webhook，用于发送部署通知。

**飞书机器人配置**:
```bash
# 在脚本开头配置
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID"
```

### 5.2 一键部署脚本

创建 `deploy_to_production.py`：

```python
#!/usr/bin/env python3
"""
测试到生产部署脚本
功能: 将指定项目从测试环境部署到生产环境

⚠️ 重要约束:
- 仅执行添加/复制操作，不允许任何删除
- 不重启生产服务
- 成功/失败都需要通过飞书通知管理员
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

# ============ 配置 ============
TEST_DATA_DIR = "/projects/management/tracker/shared/data/test_data"
USER_DATA_DIR = "/projects/management/tracker/shared/data/user_data"
BACKUP_DIR = "/projects/management/tracker/shared/data/backups"

# 飞书 webhook 配置
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3"
# ==============================

def print_step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")

def print_ok(msg):
    print(f"✅ {msg}")

def print_warn(msg):
    print(f"⚠️  {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def send_feishu_notification(title, content, is_success=True):
    """发送飞书通知"""
    import requests
    
    # 颜色: 绿色成功, 红色失败
    color = "#00C471" if is_success else "#F5222D"
    
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🚨 {title}"
                },
                "template": color
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                }
            ]
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print_ok("飞书通知已发送")
            return True
        else:
            print_warn(f"飞书通知发送失败: {response.status_code}")
            return False
    except Exception as e:
        print_warn(f"飞书通知发送异常: {e}")
        return False

def notify_admin_success(project_name, project_info):
    """通知管理员部署成功"""
    content = f"""
## ✅ 项目部署成功

**项目名称**: {project_name}
**项目ID**: {project_info.get('id', 'N/A')}
**开始日期**: {project_info.get('start_date', 'N/A')}
**结束日期**: {project_info.get('end_date', 'N/A')}

### 下一步
请登录生产环境 (http://localhost:8080) 验证项目数据正确性。

---
⚠️ 如有问题，**请勿自行处理**，请联系系统管理员。
"""
    send_feishu_notification("项目部署成功", content, is_success=True)

def notify_admin_failure(project_name, error_message):
    """通知管理员部署失败"""
    content = f"""
## ❌ 项目部署失败

**项目名称**: {project_name}
**错误信息**: {error_message}

### 解决方案
请检查测试环境项目是否存在，然后重试。

---
⚠️ 如持续失败，请联系系统管理员处理。
"""
    send_feishu_notification("项目部署失败", content, is_success=False)

def notify_admin_rollback_needed(project_name, reason):
    """通知管理员需要回滚"""
    content = f"""
## ⚠️ 需要管理员介入

**项目名称**: {project_name}
**原因**: {reason}

### 需要管理员操作
1. 检查生产环境数据是否正确
2. 如需回滚，请手动执行
3. 如需重启服务，请手动执行

---
🚫 **警告**: 回滚/重启操作必须由管理员执行！
"""
    send_feishu_notification("需要管理员介入", content, is_success=False)

def get_project_db_path(data_dir, project_name):
    """查找项目数据库文件路径"""
    # 尝试多种可能的文件名格式
    possible_names = [
        f"{project_name}.db",
        f"{project_name.replace(' ', '_')}.db",
        f"{project_name.lower()}.db"
    ]
    
    for name in possible_names:
        path = os.path.join(data_dir, name)
        if os.path.exists(path):
            return path
    
    # 如果没找到，列出所有 db 文件供用户选择
    print_warn(f"未找到项目 '{project_name}' 的数据库文件")
    print("测试环境中的数据库文件:")
    for f in sorted(os.listdir(data_dir)):
        if f.endswith('.db') and not f.startswith('users'):
            print(f"  - {f}")
    return None

def list_test_projects():
    """列出测试环境中的项目"""
    projects_file = os.path.join(TEST_DATA_DIR, "projects.json")
    if not os.path.exists(projects_file):
        print_error("测试环境 projects.json 不存在")
        return []
    
    with open(projects_file, "r") as f:
        projects = json.load(f)
    
    # 过滤出未归档的项目
    active_projects = [p for p in projects if not p.get("is_archived", False)]
    return active_projects

def backup_production():
    """备份当前生产数据（仅复制，不删除）"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"pre_deploy_{timestamp}")
    
    os.makedirs(backup_path, exist_ok=True)
    
    # 仅复制 projects.json
    src = os.path.join(USER_DATA_DIR, "projects.json")
    if os.path.exists(src):
        shutil.copy2(src, backup_path)
        print_ok(f"已备份 projects.json")
    
    # 仅复制所有项目数据库（不删除任何文件）
    for f in os.listdir(USER_DATA_DIR):
        if f.endswith('.db'):
            shutil.copy2(os.path.join(USER_DATA_DIR, f), backup_path)
    
    print_ok(f"已备份到: {backup_path}")
    return backup_path

def add_project_to_production(project_name, project_info):
    """添加项目到生产 projects.json（仅添加，不修改现有数据）"""
    projects_file = os.path.join(USER_DATA_DIR, "projects.json")
    
    # 读取现有项目
    if os.path.exists(projects_file):
        with open(projects_file, "r") as f:
            projects = json.load(f)
    else:
        projects = []
    
    # 检查项目是否已存在
    for p in projects:
        if p["name"] == project_name:
            print_warn(f"项目 '{project_name}' 已存在于生产环境")
            return False
    
    # 添加新项目
    # 生成新的项目 ID
    new_id = max([p.get("id", 0) for p in projects], default=0) + 1
    
    new_project = {
        "id": new_id,
        "name": project_name,
        "created_at": project_info.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "is_archived": False,
        "version": "stable",
        "start_date": project_info.get("start_date", ""),
        "end_date": project_info.get("end_date", "")
    }
    
    projects.append(new_project)
    
    # 写入文件
    with open(projects_file, "w") as f:
        json.dump(projects, f, indent=2)
    
    print_ok(f"已添加项目到生产环境 (ID: {new_id})")
    return True

def deploy_project(project_name):
    """部署项目到生产环境"""
    
    print_step(f"开始部署项目: {project_name}")
    
    try:
        # 1. 查找测试项目信息
        print("\n📋 步骤 1: 检查测试项目...")
        projects = list_test_projects()
        project_info = None
        for p in projects:
            if p["name"] == project_name:
                project_info = p
                break
        
        if not project_info:
            error_msg = f"测试环境中未找到项目: {project_name}"
            print_error(error_msg)
            print("\n测试环境中的项目:")
            for p in projects:
                print(f"  - {p['name']} (ID: {p['id']})")
            notify_admin_failure(project_name, error_msg)
            return False
        
        print_ok(f"找到测试项目: {project_info['name']}")
        
        # 2. 查找项目数据库
        print("\n📋 步骤 2: 查找项目数据库...")
        db_path = get_project_db_path(TEST_DATA_DIR, project_name)
        if not db_path:
            error_msg = "项目数据库文件不存在"
            print_error(error_msg)
            notify_admin_failure(project_name, error_msg)
            return False
        
        print_ok(f"找到数据库: {db_path}")
        
        # 3. 检查目标文件是否已存在（防止覆盖）
        dest_db_path = os.path.join(USER_DATA_DIR, f"{project_name}.db")
        if os.path.exists(dest_db_path):
            error_msg = f"生产环境已存在同名数据库: {dest_db_path}"
            print_error(error_msg)
            # 通知管理员处理
            notify_admin_rollback_needed(project_name, "生产环境已存在同名数据库文件")
            return False
        
        # 4. 备份生产数据（仅复制）
        print("\n📋 步骤 3: 备份生产数据...")
        backup_path = backup_production()
        
        # 5. 复制数据库文件到生产环境（仅添加）
        print("\n📋 步骤 4: 复制数据库到生产环境...")
        shutil.copy2(db_path, dest_db_path)
        print_ok(f"已复制数据库到: {dest_db_path}")
        
        # 6. 更新 projects.json（仅添加）
        print("\n📋 步骤 5: 更新生产项目列表...")
        if not add_project_to_production(project_name, project_info):
            error_msg = "添加项目到生产列表失败"
            print_error(error_msg)
            notify_admin_failure(project_name, error_msg)
            return False
        
        # 7. 通知管理员部署成功
        print("\n📋 步骤 6: 发送通知...")
        notify_admin_success(project_name, project_info)
        
        print_step("部署完成!")
        print(f"\n项目 '{project_name}' 已部署到生产环境")
        print(f"请访问 http://localhost:8080 验证")
        
        return True
        
    except Exception as e:
        error_msg = f"部署过程异常: {str(e)}"
        print_error(error_msg)
        notify_admin_failure(project_name, error_msg)
        return False

def list_projects():
    """列出可部署的项目"""
    print_step("测试环境中的项目")
    projects = list_test_projects()
    
    if not projects:
        print("没有可部署的项目")
        return
    
    print(f"\n{'名称':<40} {'ID':<5} {'创建时间':<20}")
    print("-" * 70)
    for p in projects:
        print(f"{p['name']:<40} {p['id']:<5} {p.get('created_at', ''):<20}")

def test_notification():
    """测试飞书通知"""
    content = """
## 🧪 飞书通知测试

这是一条测试消息，用于验证飞书机器人配置是否正确。

---
如果收到此消息，说明配置成功。
"""
    send_feishu_notification("飞书通知测试", content, is_success=True)

def main():
    parser = argparse.ArgumentParser(description="测试到生产部署工具")
    parser.add_argument("--list", "-l", action="store_true", help="列出可部署的项目")
    parser.add_argument("--project", "-p", type=str, help="项目名称")
    parser.add_argument("--test-notify", "-t", action="store_true", help="测试飞书通知")
    
    args = parser.parse_args()
    
    if args.test_notify:
        test_notification()
    elif args.list:
        list_projects()
    elif args.project:
        deploy_project(args.project)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python3 deploy_to_production.py --list              # 列出可部署项目")
        print("  python3 deploy_to_production.py --project '项目名'  # 部署项目")
        print("  python3 deploy_to_production.py --test-notify       # 测试飞书通知")

if __name__ == "__main__":
    main()
```

### 5.3 使用方法

```bash
# 1. 首先查看可部署的项目列表
python3 deploy_to_production.py --list

# 2. 执行部署（会自动通知管理员）
python3 deploy_to_production.py --project "Chip_A_Verification"

# 3. 测试飞书通知
python3 deploy_to_production.py --test-notify
```

---

## 6. 飞书通知配置

### 6.1 通知类型

| 事件 | 通知类型 | 颜色 |
|------|----------|------|
| 部署成功 | ✅ 项目部署成功 | 绿色 |
| 部署失败 | ❌ 项目部署失败 | 红色 |
| 需要介入 | ⚠️ 需要管理员介入 | 红色 |

### 6.2 通知内容示例

**部署成功**:
```
🚨 项目部署成功

项目名称: Chip_A_Verification
项目ID: 5
开始日期: 2026-01-01
结束日期: 2026-12-31

下一步
请登录生产环境 (http://localhost:8080) 验证项目数据正确性。

---
⚠️ 如有问题，请勿自行处理，请联系系统管理员。
```

**部署失败**:
```
🚨 项目部署失败

项目名称: Chip_A_Verification
错误信息: 项目数据库文件不存在

解决方案
请检查测试环境项目是否存在，然后重试。

---
⚠️ 如持续失败，请联系系统管理员处理。
```

---

## 7. 附录

### 7.1 飞书 webhook 配置

**当前配置的 webhook**:
```bash
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3"
```

**获取新的 webhook**:
1. 打开飞书群聊设置
2. 添加群机器人
3. 选择"自定义机器人"
4. 获取 Webhook 地址

### 7.2 curl 发送飞书消息示例

```bash
# 发送文本消息
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "项目 Chip_A_Verification 部署成功！"
    }
  }'

# 发送富文本卡片消息
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": {
          "tag": "plain_text",
          "content": "🚨 项目部署成功"
        },
        "template": "green"
      },
      "elements": [
        {
          "tag": "markdown",
          "content": "**项目名称**: Chip_A_Verification\n**项目ID**: 5"
        },
        {
          "tag": "div",
          "text": {
            "tag": "plain_text",
            "content": "⏰ 时间: 2026-03-05 14:00:00"
          }
        }
      ]
    }
  }'
```

### 7.3 Python 发送飞书消息示例

```python
import requests
import json

# Webhook 地址
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3"

# 发送文本消息
def send_text(message):
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    return response.json()

# 发送卡片消息
def send_card(title, content, is_success=True):
    color = "#00C471" if is_success else "#F5222D"
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🚨 {title}"
                },
                "template": color
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 发送文本
    send_text("项目部署成功！")
    
    # 发送卡片
    send_card(
        "项目部署成功",
        "**项目名称**: Chip_A_Verification\n**项目ID**: 5",
        is_success=True
    )
```

### 7.4 完整部署流程命令示例

```bash
# 完整部署流程

# 1. 列出可部署项目
python3 deploy_to_production.py --list

# 2. 执行部署（会自动通知）
python3 deploy_to_production.py --project "Chip_A_Verification"

# 3. 等待飞书通知，确认部署结果

# 4. 验证部署
curl http://localhost:8080/api/projects
```

---

### 7.5 ⚠️ 绝对禁止操作清单

| 操作 | 命令 | 后果 |
|------|------|------|
| ❌ 删除测试数据 | `rm test_data/*.db` | 丢失验证数据 |
| ❌ 删除生产数据 | `rm user_data/*.db` | 丢失生产数据 |
| ❌ 回滚操作 | 任何恢复旧版本的操作 | 数据不一致 |
| ❌ 重启服务 | `pkill`, `systemctl restart` | 服务中断 |

> **如需执行上述操作，必须通知管理员，由管理员亲自执行！**

---

*文档版本: v1.1*
*最后更新: 2026-04-03*
