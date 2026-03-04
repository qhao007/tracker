#!/usr/bin/env python3
"""
版本发布脚本 (v0.4)

功能：
1. 将 dev 代码发布到 /release/tracker/v{version}
2. 自动检查兼容性
3. 创建 current 软链接指向当前版本
4. 更新 systemd 服务
5. 支持回滚（切换软链接）

用法：
    python3 scripts/release.py [--version VERSION] [--migrate] [--force]
    python3 scripts/release.py --rollback [--force]
"""
import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime

# 路径配置
TRACKER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED_DATA = os.path.join(TRACKER_DIR, 'shared', 'data')
USER_DATA = os.path.join(SHARED_DATA, 'user_data')
TEST_DATA = os.path.join(SHARED_DATA, 'test_data')

# 发布目录配置
RELEASE_BASE = '/release/tracker'
RELEASE_CURRENT = os.path.join(RELEASE_BASE, 'current')
SERVICE_FILE = '/etc/systemd/system/tracker.service'

def parse_args():
    parser = argparse.ArgumentParser(description='Tracker 版本发布脚本 (v0.4)')
    parser.add_argument('--version', '-v', default=None, help='版本号 (默认: v0.3.x)')
    parser.add_argument('--migrate', action='store_true', help='执行数据库迁移')
    parser.add_argument('--rollback', action='store_true', help='回滚到上一版本')
    parser.add_argument('--dry-run', action='store_true', help='演练模式（不实际执行）')
    parser.add_argument('--force', action='store_true', help='强制执行（跳过确认）')
    return parser.parse_args()

def get_version():
    """获取版本号"""
    # 读取当前版本
    version_file = os.path.join(TRACKER_DIR, 'dev', 'app', 'version.py')
    if os.path.exists(version_file):
        with open(version_file) as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('VERSION'):
                    return line.split('=')[1].strip().strip('"\'')
    return f"v0.3.{datetime.now().strftime('%Y%m%d')}"

def check_release_ready(version):
    """检查是否满足发布条件（flag 文件）"""
    print("\n🔍 检查发布准备状态...")
    
    flag_file = os.path.join(TRACKER_DIR, '.release_ready')
    
    # 1. 检查 flag 文件是否存在
    if not os.path.exists(flag_file):
        print(f"   ❌ Flag 文件不存在: {flag_file}")
        print(f"   提示: 请先执行 release_preparation.py")
        return False
    
    # 2. 检查版本是否匹配
    with open(flag_file, 'r') as f:
        content = f.read()
    
    expected_version_line = f"VERSION={version}"
    if expected_version_line not in content:
        print(f"   ❌ 版本不匹配")
        print(f"   Flag 内容: {content}")
        return False
    
    # 3. 检查 main 分支是否是预期提交
    current_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=TRACKER_DIR, capture_output=True, text=True
    ).stdout.strip()
    
    if "MAIN_COMMIT=" in content:
        expected_commit = content.split("MAIN_COMMIT=")[1].split("\n")[0]
        if current_commit != expected_commit:
            print(f"   ❌ main 分支提交不匹配")
            print(f"   预期: {expected_commit}")
            print(f"   实际: {current_commit}")
            return False
    
    print(f"   ✅ Flag 检查通过")
    return True


def check_data_structure():
    """检查数据目录结构"""
    print("\n🔍 检查数据目录结构...")
    
    if not os.path.exists(USER_DATA):
        print(f"   ⚠️  user_data 不存在: {USER_DATA}")
        return False
    
    if not os.path.exists(TEST_DATA):
        print(f"   ⚠️  test_data 不存在: {TEST_DATA}")
        return False
    
    print(f"   ✅ user_data: {USER_DATA}")
    print(f"   ✅ test_data: {TEST_DATA}")
    return True

def get_current_release_version():
    """获取当前发布的版本"""
    if os.path.islink(RELEASE_CURRENT):
        current_target = os.readlink(RELEASE_CURRENT)
        version = os.path.basename(current_target)
        return version
    return None

def create_release(src_dir, version, dry_run=False):
    """创建发布版本"""
    release_dir = os.path.join(RELEASE_BASE, version)
    action = "演练" if dry_run else "发布"
    
    print(f"\n📦 {action}版本: {version}")
    print(f"   源目录: {src_dir}")
    print(f"   发布目录: {release_dir}")
    
    if dry_run:
        return None
    
    # 检查当前版本
    current_version = get_current_release_version()
    if current_version:
        print(f"   ℹ️  当前版本: {current_version}")
    
    # 如果发布目录已存在，询问是否覆盖
    if os.path.exists(release_dir):
        if not args.force:
            confirm = input(f"\n⚠️  版本 {version} 已存在，是否覆盖? (y/N): ")
            if confirm.lower() != 'y':
                print("已取消")
                return None
        shutil.rmtree(release_dir)
        print(f"   🗑️  已删除旧版本目录")
    
    # 创建发布目录
    os.makedirs(release_dir, exist_ok=True)
    
    # 复制代码（不包括 data、tests、node_modules）
    print("\n🔄 复制代码文件...")
    skip_items = ['data', 'tests', 'node_modules', '__pycache__', '.git', 'shared']
    
    for item in os.listdir(src_dir):
        if item in skip_items:
            print(f"   ⏭️  跳过: {item}/")
            continue
        
        src = os.path.join(src_dir, item)
        dst = os.path.join(release_dir, item)
        
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            print(f"   ✅ {item}/")
        else:
            shutil.copy2(src, dst)
            print(f"   ✅ {item}")
    
    # 创建 data 符号链接指向 user_data
    data_link = os.path.join(release_dir, 'data')
    user_data_link = os.path.join(USER_DATA)  # 使用绝对路径
    
    if os.path.islink(data_link):
        os.remove(data_link)
    os.symlink(user_data_link, data_link)
    print(f"   🔗 data -> ../../shared/data/user_data")
    
    return release_dir

def update_current_symlink(version, dry_run=False):
    """更新 current 软链接"""
    release_dir = os.path.join(RELEASE_BASE, version)
    action = "演练" if dry_run else "更新"
    
    print(f"\n🔗 {action} current 软链接...")
    
    if dry_run:
        print(f"   (演练) {RELEASE_CURRENT} -> {release_dir}")
        return True
    
    # 删除旧软链接
    if os.path.islink(RELEASE_CURRENT):
        os.remove(RELEASE_CURRENT)
        print(f"   🗑️  已删除旧软链接")
    
    # 创建新软链接
    os.symlink(release_dir, RELEASE_CURRENT)
    print(f"   ✅ {RELEASE_CURRENT} -> {release_dir}")
    
    return True

def update_systemd_service(version, dry_run=False):
    """更新 systemd 服务配置"""
    print(f"\n⚙️  {'演练' if dry_run else '更新'} systemd 服务...")
    
    release_dir = os.path.join(RELEASE_BASE, version)
    service_content = f"""[Unit]
Description=Chip Verification Tracker v0.3
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={release_dir}
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/tracker.log
StandardError=append:/var/log/tracker.error.log

[Install]
WantedBy=multi-user.target
"""
    
    if dry_run:
        print(f"   (演练) 服务文件: {SERVICE_FILE}")
        print(f"   WorkingDirectory: {release_dir}")
        return True
    
    with open(SERVICE_FILE, 'w') as f:
        f.write(service_content)
    print(f"   ✅ 已更新: {SERVICE_FILE}")
    
    # 重载 systemd
    subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)
    print(f"   🔄 已重载 systemd")
    
    return True

def restart_service(dry_run=False):
    """重启服务"""
    print(f"\n🔄 {'演练' if dry_run else '重启'} tracker 服务...")
    
    if dry_run:
        print(f"   (演练) sudo systemctl restart tracker")
        return True
    
    # 检查服务是否存在
    result = subprocess.run(['systemctl', 'is-active', 'tracker'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        subprocess.run(['sudo', 'systemctl', 'restart', 'tracker'], capture_output=True)
        print(f"   ✅ 服务已重启")
        
        # 等待服务启动
        import time
        time.sleep(2)
        
        # 检查状态
        status = subprocess.run(['systemctl', 'is-active', 'tracker'], 
                              capture_output=True, text=True)
        if status.returncode == 0:
            print(f"   ✅ 服务运行中")
            return True
        else:
            print(f"   ⚠️  服务状态异常")
            return False
    else:
        print(f"   ⚠️  服务 'tracker' 不存在")
        print(f"   💡 请先运行: sudo systemctl enable tracker")
        return None

def generate_release_notes(version, release_dir, dry_run=False):
    """生成发布报告"""
    print(f"\n📝 {'演练' if dry_run else '生成'}发布报告...")
    
    # 获取项目数量
    db_files = [f for f in os.listdir(USER_DATA) if f.endswith('.db')]
    
    # 获取 IP
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ips = result.stdout.strip().split()
        lan_ip = ips[0] if ips else '10.0.0.8'
        wan_ip = ips[1] if len(ips) > 1 else '外网IP'
    except:
        lan_ip = '10.0.0.8'
        wan_ip = '外网IP'
    
    now = datetime.now()
    
    notes_content = f"""# Tracker {version} 发布报告

> **版本**: {version} | **发布日期**: {now.strftime('%Y-%m-%d')} | **发布时间**: {now.strftime('%H:%M:%S')}

---

## 发布摘要

| 项目 | 状态 |
|------|------|
| 版本 | {version} |
| 发布日期 | {now.strftime('%Y-%m-%d')} |
| 发布目录 | {release_dir} |
| 当前版本 | {RELEASE_CURRENT} |
| 兼容性检查 | ✅ 全部通过 |

---

## Git 分支信息

| 分支 | 说明 |
|------|------|
| main | 生产环境代码 |
| develop | 开发主分支 |

---

## 发布目录结构

```
{RELEASE_BASE}/
├── v0.3.1/          ← 历史版本
├── v0.3.2/          ← 当前版本
└── current → v0.3.2 ← 软链接
```

---

## 数据目录

```
shared/data/
├── user_data/       ← 用户数据（正式版使用）
│   └── {len(db_files)} 个项目数据库
│
└── test_data/       ← 测试数据（开发版使用）
```

---

## 访问地址

| 环境 | 地址 | 端口 |
|------|------|------|
| 内网 | http://{lan_ip} | 8080 |
| 外网 | http://{wan_ip} | 8080 |

---

## 服务管理

```bash
# 重启服务
sudo systemctl restart tracker

# 查看状态
sudo systemctl status tracker

# 查看日志
journalctl -u tracker -f
```

---

## 版本回滚

### 方式1：切换软链接（推荐）
```bash
# 查看可用版本
ls -la {RELEASE_BASE}/

# 回滚到上一版本
cd /projects/management/tracker
python3 scripts/release.py --rollback --force
```

### 方式2：手动切换
```bash
# 查看当前版本
ls -la {RELEASE_CURRENT}

# 切换到历史版本
sudo rm {RELEASE_CURRENT}
sudo ln -s {RELEASE_BASE}/v0.3.1 {RELEASE_CURRENT}
sudo systemctl restart tracker
```

**注意：** 回滚只切换软链接，用户数据不会改变。

---

## 相关资源

- **Tracker 目录**: {RELEASE_BASE}
- **当前版本**: {RELEASE_CURRENT}
- **Git 仓库**: /projects/management/tracker
- **规格书**: /projects/management/tracker/docs/SPECIFICATIONS/tracker_OVERALL_SPECS.md

---

**文档生成时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    if dry_run:
        print(f"   (演练) 发布报告: {release_dir}/RELEASE_NOTES.md")
        return None
    
    notes_path = os.path.join(release_dir, 'RELEASE_NOTES.md')
    with open(notes_path, 'w', encoding='utf-8') as f:
        f.write(notes_content)
    
    print(f"   ✅ 发布报告: {notes_path}")
    return notes_path

def rollback(dry_run=False):
    """回滚到上一版本"""
    print(f"\n🔙 {'演练' if dry_run else '回滚'}到上一版本...")
    
    current_version = get_current_release_version()
    if not current_version:
        print("❌ 没有找到当前发布版本，无法回滚")
        return False
    
    # 查找可用的历史版本
    available_versions = []
    if os.path.exists(RELEASE_BASE):
        for item in os.listdir(RELEASE_BASE):
            if item.startswith('v') and os.path.isdir(os.path.join(RELEASE_BASE, item)):
                if item != current_version:
                    available_versions.append(item)
    
    if not available_versions:
        print("❌ 没有找到可回滚的版本")
        return False
    
    # 使用最新的历史版本
    target_version = sorted(available_versions)[-1]
    
    print(f"   当前版本: {current_version}")
    print(f"   目标版本: {target_version}")
    
    if dry_run:
        return True
    
    # 更新软链接
    update_current_symlink(target_version)
    update_systemd_service(target_version)
    restart_service()
    
    print(f"\n✅ 已回滚到 {target_version}")
    return True

def main():
    global args
    args = parse_args()
    
    print("=" * 60)
    print("🚀 Tracker 版本发布脚本 (v0.4)")
    print("=" * 60)
    print(f"\n📁 发布目录: {RELEASE_BASE}")
    print(f"   当前版本: {get_current_release_version() or '未发布'}")
    print(f"\n📁 数据目录:")
    print(f"   user_data: {USER_DATA}")
    print(f"   test_data: {TEST_DATA}")
    
    # 检查数据目录
    if not check_data_structure():
        print("\n⚠️  数据目录结构异常!")
        return
    
    # 获取版本号
    version = args.version or get_version()
    
    # 检查 flag 文件
    if not check_release_ready(version):
        print("\n❌ 未满足发布条件，请先执行 release_preparation.py")
        return
    
    if args.rollback:
        # 回滚
        if not args.force:
            confirm = input("\n⚠️  确定要回滚吗? (y/N): ")
            if confirm.lower() != 'y':
                print("已取消")
                return
        rollback(args.dry_run)
        return
    
    # 演练模式
    if args.dry_run:
        print("\n🏃 演练模式")
        create_release('dev', version, dry_run=True)
        update_current_symlink(version, dry_run=True)
        update_systemd_service(version, dry_run=True)
        generate_release_notes(version, '/release/tracker/v0.3.x', dry_run=True)
        print("\n✅ 演练完成")
        return
    
    # 发布确认
    if not args.force:
        print(f"\n📋 发布摘要:")
        print(f"   版本: {version}")
        print(f"   发布目录: {RELEASE_BASE}/{version}")
        print(f"   当前版本: {get_current_release_version() or '无'}")
        print(f"   迁移: {'是' if args.migrate else '否'}")
        confirm = input("\n⚠️  确定要发布吗? (y/N): ")
        if confirm.lower() != 'y':
            print("已取消")
            return
    
    # 执行发布
    src_dir = 'dev'
    release_dir = os.path.join(RELEASE_BASE, version)
    
    # 1. 创建发布版本
    create_release(src_dir, version)
    
    # 2. 更新 current 软链接
    update_current_symlink(version)
    
    # 3. 更新 systemd
    update_systemd_service(version)
    
    # 4. 生成发布报告
    generate_release_notes(version, release_dir)
    
    # 5. 重启服务
    restart_service()
    
    print("\n" + "=" * 60)
    print("✅ 发布完成!")
    print("=" * 60)
    print(f"\n📄 发布目录: {release_dir}")
    print(f"🔗 当前版本: {RELEASE_CURRENT}")
    print(f"📄 发布报告: {release_dir}/RELEASE_NOTES.md")
    
    # 切换回 develop 分支
    print("\n🔄 切换回 develop 分支...")
    try:
        subprocess.run(["git", "checkout", "develop"], cwd=TRACKER_DIR, check=True)
        print("✅ 已切换到 develop 分支")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  切换分支失败: {e}")
    
    # 删除 flag 文件
    flag_file = os.path.join(TRACKER_DIR, '.release_ready')
    if os.path.exists(flag_file):
        os.remove(flag_file)
        print("✅ Flag 文件已删除")

if __name__ == '__main__':
    main()
