# Tracker 项目重命名指导手册

> **版本**: v1.0
> **适用版本**: Tracker v0.9.0+
> **创建日期**: 2026-03-09
> **文档类型**: 操作指南

---

## 目录

1. [概述](#1-概述)
2. [项目名称依赖分析](#2-项目名称依赖分析)
3. [手动重命名步骤](#3-手动重命名步骤)
4. [自动化重命名脚本](#4-自动化重命名脚本)
5. [验证与回滚](#5-验证与回滚)
6. [附录](#6-附录)

---

## 1. 概述

### 1.1 目的

本文档指导管理员如何安全地修改 Tracker 系统中的项目名称。

### 1.2 适用范围

- **场景一**：项目命名规范调整
- **场景二**：项目阶段变更需更新名称
- **场景三**：纠正项目名称拼写错误

### 1.3 前置条件

| 条件 | 说明 |
|------|------|
| 管理员权限 | 拥有服务器文件系统访问权限 |
| 项目存在 | 目标项目在系统中已存在 |
| 新名称唯一 | 新项目名称不能与现有项目重复 |

### 1.4 重要原则（严禁操作）

> **关键原则 - 必须严格遵守**：

| 操作 | 允许 | 说明 |
|------|------|------|
| 备份数据 | ✅ 允许 | 操作前必须备份 |
| 重命名数据库文件 | ✅ 允许 | 与项目名称同步修改 |
| 更新 projects.json | ✅ 允许 | 仅修改 name 字段 |
| 删除备份数据 | ❌ **严禁** | 备份数据是回滚依据 |
| 跳过备份步骤 | ❌ **严禁** | 必须先备份再操作 |

> **违反原则的后果**：可能导致数据无法访问或永久丢失！

---

## 2. 项目名称依赖分析

### 2.1 项目名称在系统中的作用

| 组件 | 是否依赖项目名称 | 依赖方式 |
|------|-----------------|---------|
| projects.json | 是 | 存储项目元数据的 `name` 字段 |
| 数据库文件名 | 是 | 文件名格式为 `{project_name}.db` |
| 数据库内部数据 | 否 | 内部仅使用 `project_id` |
| 归档文件 | 部分 | 历史归档保留原名，不影响当前系统 |
| Session 文件 | 否 | 不包含项目信息 |
| API 通信 | 否 | API 使用 `project_id` 作为参数 |
| 前端显示 | 是 | 显示项目名称给用户 |

### 2.2 数据库连接机制

Tracker 系统通过以下方式定位项目数据库：

```python
# api.py 中的数据库路径获取函数
def get_db_path(project_name):
    safe_name = project_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    return os.path.join(current_app.config["DATA_DIR"], f"{safe_name}.db")
```

**关键发现**：
- 项目名称直接决定数据库文件名
- 重命名项目必须同步重命名数据库文件
- 否则系统无法找到数据库，导致项目无法访问

### 2.3 重命名影响范围

```
重命名前:
├── projects.json        → "name": "Old_Name"
└── Old_Name.db          → 数据库文件

重命名后:
├── projects.json        → "name": "New_Name"  (需更新)
└── New_Name.db          → 数据库文件 (需重命名)
```

---

## 3. 手动重命名步骤

### 3.1 步骤 1：确认项目信息

```bash
# 登录测试环境
curl -X POST http://localhost:8081/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c /tmp/cookies.txt

# 获取项目列表，确认项目 ID
curl http://localhost:8081/api/projects -b /tmp/cookies.txt | python3 -m json.tool

# 获取项目统计，确认数据量
curl "http://localhost:8081/api/stats?project_id=<项目ID>" -b /tmp/cookies.txt
```

记录以下信息：
- 项目名称 (name)
- 项目 ID (id)
- CP/TC 数量

### 3.2 步骤 2：检查新名称是否可用

```bash
# 设置变量
OLD_NAME="Old_Project_Name"
NEW_NAME="New_Project_Name"
DATA_DIR="/projects/management/tracker/shared/data/test_data"  # 或 user_data

# 检查 projects.json 中是否已有同名项目
grep "\"$NEW_NAME\"" $DATA_DIR/projects.json && echo "名称已存在!" || echo "名称可用"

# 检查是否已有同名数据库文件
ls $DATA_DIR/${NEW_NAME}.db 2>/dev/null && echo "数据库文件已存在!" || echo "文件名可用"
```

### 3.3 步骤 3：备份当前数据

```bash
# 创建备份目录
BACKUP_DIR="/projects/management/tracker/shared/data/backups/rename_${OLD_NAME}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份 projects.json
cp $DATA_DIR/projects.json "$BACKUP_DIR/"

# 备份项目数据库
cp $DATA_DIR/${OLD_NAME}.db "$BACKUP_DIR/"

echo "备份完成: $BACKUP_DIR"
ls -la "$BACKUP_DIR"
```

### 3.4 步骤 4：重命名数据库文件

```bash
# 重命名数据库文件
mv $DATA_DIR/${OLD_NAME}.db $DATA_DIR/${NEW_NAME}.db

# 验证
ls -la $DATA_DIR/${NEW_NAME}.db
```

### 3.5 步骤 5：更新 projects.json

```bash
# 查看当前项目配置
grep -B2 -A6 "\"$OLD_NAME\"" $DATA_DIR/projects.json

# 使用 sed 替换项目名称
sed -i "s/\"name\": \"$OLD_NAME\"/\"name\": \"$NEW_NAME\"/g" $DATA_DIR/projects.json

# 验证修改结果
grep -B2 -A6 "\"$NEW_NAME\"" $DATA_DIR/projects.json
```

### 3.6 步骤 6：验证重命名结果

```bash
# 通过 API 验证项目可访问
curl "http://localhost:8081/api/stats?project_id=<项目ID>" -b /tmp/cookies.txt

# 验证 CP 数据
curl "http://localhost:8081/api/cp?project_id=<项目ID>" -b /tmp/cookies.txt | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'CP 数量: {len(data)}')"

# 验证 TC 数据
curl "http://localhost:8081/api/tc?project_id=<项目ID>" -b /tmp/cookies.txt | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'TC 数量: {len(data)}')"
```

---

## 4. 自动化重命名脚本

### 4.1 一键重命名脚本

创建 `rename_project.py`：

```python
#!/usr/bin/env python3
"""
项目重命名脚本
功能: 安全地修改 Tracker 项目名称

⚠️ 重要约束:
- 仅执行重命名操作，不允许删除
- 必须先备份再操作
- 成功/失败都需要通知管理员
"""
import argparse
import json
import os
import shutil
from datetime import datetime

# ============ 配置 ============
TEST_DATA_DIR = "/projects/management/tracker/shared/data/test_data"
USER_DATA_DIR = "/projects/management/tracker/shared/data/user_data"
BACKUP_DIR = "/projects/management/tracker/shared/data/backups"

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

def get_project_info(data_dir, project_name):
    """获取项目信息"""
    projects_file = os.path.join(data_dir, "projects.json")

    if not os.path.exists(projects_file):
        print_error("projects.json 不存在")
        return None

    with open(projects_file, "r") as f:
        projects = json.load(f)

    for p in projects:
        if p["name"] == project_name:
            return p

    return None

def check_new_name_available(data_dir, new_name):
    """检查新名称是否可用"""
    projects_file = os.path.join(data_dir, "projects.json")

    # 检查 projects.json
    with open(projects_file, "r") as f:
        projects = json.load(f)

    for p in projects:
        if p["name"] == new_name:
            return False, f"项目名称 '{new_name}' 已存在于 projects.json"

    # 检查数据库文件
    db_path = os.path.join(data_dir, f"{new_name}.db")
    if os.path.exists(db_path):
        return False, f"数据库文件 '{new_name}.db' 已存在"

    return True, "名称可用"

def backup_data(data_dir, old_name):
    """备份数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"rename_{old_name}_{timestamp}")

    os.makedirs(backup_path, exist_ok=True)

    # 备份 projects.json
    src = os.path.join(data_dir, "projects.json")
    if os.path.exists(src):
        shutil.copy2(src, backup_path)
        print_ok(f"已备份 projects.json")

    # 备份数据库文件
    db_src = os.path.join(data_dir, f"{old_name}.db")
    if os.path.exists(db_src):
        shutil.copy2(db_src, backup_path)
        print_ok(f"已备份 {old_name}.db")

    print_ok(f"备份目录: {backup_path}")
    return backup_path

def rename_project(old_name, new_name, env="test"):
    """重命名项目"""
    print_step(f"开始重命名项目: {old_name} → {new_name}")

    # 确定数据目录
    data_dir = TEST_DATA_DIR if env == "test" else USER_DATA_DIR
    env_name = "测试环境" if env == "test" else "生产环境"

    print(f"\n环境: {env_name}")
    print(f"数据目录: {data_dir}")

    try:
        # 1. 检查原项目是否存在
        print("\n📋 步骤 1: 检查原项目...")
        project_info = get_project_info(data_dir, old_name)

        if not project_info:
            error_msg = f"项目 '{old_name}' 不存在"
            print_error(error_msg)
            send_feishu_notification("项目重命名失败",
                f"**原名称**: {old_name}\n**新名称**: {new_name}\n**错误**: {error_msg}",
                is_success=False)
            return False

        print_ok(f"找到项目: ID={project_info['id']}")

        # 检查数据库文件
        old_db_path = os.path.join(data_dir, f"{old_name}.db")
        if not os.path.exists(old_db_path):
            error_msg = f"数据库文件 '{old_name}.db' 不存在"
            print_error(error_msg)
            send_feishu_notification("项目重命名失败",
                f"**原名称**: {old_name}\n**新名称**: {new_name}\n**错误**: {error_msg}",
                is_success=False)
            return False

        print_ok(f"数据库文件存在: {old_db_path}")

        # 2. 检查新名称是否可用
        print("\n📋 步骤 2: 检查新名称...")
        available, msg = check_new_name_available(data_dir, new_name)

        if not available:
            print_error(msg)
            send_feishu_notification("项目重命名失败",
                f"**原名称**: {old_name}\n**新名称**: {new_name}\n**错误**: {msg}",
                is_success=False)
            return False

        print_ok(msg)

        # 3. 备份数据
        print("\n📋 步骤 3: 备份数据...")
        backup_path = backup_data(data_dir, old_name)

        # 4. 重命名数据库文件
        print("\n📋 步骤 4: 重命名数据库文件...")
        new_db_path = os.path.join(data_dir, f"{new_name}.db")
        shutil.move(old_db_path, new_db_path)
        print_ok(f"数据库文件已重命名: {new_db_path}")

        # 5. 更新 projects.json
        print("\n📋 步骤 5: 更新 projects.json...")
        projects_file = os.path.join(data_dir, "projects.json")

        with open(projects_file, "r") as f:
            projects = json.load(f)

        for p in projects:
            if p["name"] == old_name:
                p["name"] = new_name
                break

        with open(projects_file, "w") as f:
            json.dump(projects, f, indent=2)

        print_ok(f"projects.json 已更新")

        # 6. 发送成功通知
        print("\n📋 步骤 6: 发送通知...")
        send_feishu_notification("项目重命名成功",
            f"**原名称**: {old_name}\n**新名称**: {new_name}\n**项目ID**: {project_info['id']}\n**环境**: {env_name}\n\n### 操作详情\n1. 备份数据到 {backup_path}\n2. 重命名数据库文件\n3. 更新 projects.json",
            is_success=True)

        print_step("重命名完成!")
        print(f"\n项目 '{old_name}' 已重命名为 '{new_name}'")

        return True

    except Exception as e:
        error_msg = f"重命名过程异常: {str(e)}"
        print_error(error_msg)
        send_feishu_notification("项目重命名失败",
            f"**原名称**: {old_name}\n**新名称**: {new_name}\n**错误**: {error_msg}",
            is_success=False)
        return False

def list_projects(env="test"):
    """列出项目"""
    data_dir = TEST_DATA_DIR if env == "test" else USER_DATA_DIR
    projects_file = os.path.join(data_dir, "projects.json")

    print_step(f"项目列表 ({'测试环境' if env == 'test' else '生产环境'})")

    if not os.path.exists(projects_file):
        print_error("projects.json 不存在")
        return

    with open(projects_file, "r") as f:
        projects = json.load(f)

    active_projects = [p for p in projects if not p.get("is_archived", False)]

    print(f"\n{'名称':<40} {'ID':<5} {'创建时间':<20}")
    print("-" * 70)
    for p in active_projects:
        print(f"{p['name']:<40} {p['id']:<5} {p.get('created_at', ''):<20}")

def main():
    parser = argparse.ArgumentParser(description="Tracker 项目重命名工具")
    parser.add_argument("--list", "-l", action="store_true", help="列出项目")
    parser.add_argument("--old", "-o", type=str, help="原项目名称")
    parser.add_argument("--new", "-n", type=str, help="新项目名称")
    parser.add_argument("--env", "-e", type=str, default="test", choices=["test", "prod"],
                        help="环境: test(测试) 或 prod(生产)")

    args = parser.parse_args()

    if args.list:
        list_projects(args.env)
    elif args.old and args.new:
        rename_project(args.old, args.new, args.env)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python3 rename_project.py --list                      # 列出测试环境项目")
        print("  python3 rename_project.py --list --env prod           # 列出生产环境项目")
        print("  python3 rename_project.py --old 'OldName' --new 'NewName'  # 测试环境重命名")
        print("  python3 rename_project.py --old 'OldName' --new 'NewName' --env prod  # 生产环境重命名")

if __name__ == "__main__":
    main()
```

### 4.2 使用方法

```bash
# 1. 列出测试环境项目
python3 rename_project.py --list

# 2. 列出生产环境项目
python3 rename_project.py --list --env prod

# 3. 测试环境重命名
python3 rename_project.py --old "EX1_ValChar" --new "EX1_Validation"

# 4. 生产环境重命名（谨慎操作）
python3 rename_project.py --old "EX1_ValChar" --new "EX1_Validation" --env prod
```

---

## 5. 验证与回滚

### 5.1 验证清单

重命名完成后，请执行以下验证：

| 检查项 | 验证方式 | 预期结果 |
|--------|---------|---------|
| 项目列表显示 | API 查询或前端查看 | 显示新名称 |
| CP 数据完整 | `/api/cp?project_id=<id>` | 数量与重命名前一致 |
| TC 数据完整 | `/api/tc?project_id=<id>` | 数量与重命名前一致 |
| 统计数据正确 | `/api/stats?project_id=<id>` | 数据正常显示 |

### 5.2 回滚方法

如果重命名后发现问题，可以从备份恢复：

```bash
# 设置变量
OLD_NAME="New_Name"           # 当前（错误的）名称
ORIGINAL_NAME="Original_Name" # 原始名称
BACKUP_DIR="/path/to/backup"  # 备份目录
DATA_DIR="/projects/management/tracker/shared/data/test_data"

# 1. 删除当前的（错误）数据库文件
rm $DATA_DIR/${OLD_NAME}.db

# 2. 从备份恢复原始数据库
cp $BACKUP_DIR/${ORIGINAL_NAME}.db $DATA_DIR/

# 3. 从备份恢复 projects.json
cp $BACKUP_DIR/projects.json $DATA_DIR/

echo "回滚完成"
```

> **注意**: 回滚操作需要管理员确认后执行。

---

## 6. 附录

### 6.1 常见问题

**Q1: 重命名后项目无法访问，显示 "数据库不存在"**

原因: 数据库文件名与 projects.json 中的名称不匹配。

解决:
```bash
# 检查数据库文件名
ls $DATA_DIR/*.db

# 检查 projects.json 中的名称
grep "name" $DATA_DIR/projects.json

# 确保两者一致
```

**Q2: 新名称已存在，无法重命名**

解决: 选择其他唯一的项目名称，或先删除/归档同名项目。

**Q3: 备份目录在哪里？**

默认备份目录: `/projects/management/tracker/shared/data/backups/`

### 6.2 相关文档

| 文档 | 说明 |
|------|------|
| Tracker_Test_to_Production_Guide_v1.0.md | 测试到生产部署指南 |
| Tracker_API_Migration_Guide_v1.0.md | API 项目创建迁移指南 |

### 6.3 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-03-09 | 初始版本 |

---

*文档版本: v1.0*
*最后更新: 2026-03-09*
*署名: Claude Code*
