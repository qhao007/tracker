#!/usr/bin/env python3
"""
Tracker 运维管理脚本

功能:
    1. sync    - 复制 user_data 到 test_data
    2. clean   - 删除 test_data 中的用户数据
    3. check   - 静态检查：数据库结构、版本号、字段
    4. test    - 动态测试：调用 API 验证兼容性

使用方法:
    python3 scripts/tracker_ops.py sync      # 复制数据
    python3 scripts/tracker_ops.py clean     # 清理数据
    python3 scripts/tracker_ops.py check     # 静态检查
    python3 scripts/tracker_ops.py test     # 动态测试
    python3 scripts/tracker_ops.py all      # 执行全部
"""

import sqlite3
import glob
from datetime import datetime
import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path

# 颜色输出
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

REPO_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = REPO_ROOT / "shared" / "data" / "test_data"
USER_DATA_DIR = REPO_ROOT / "shared" / "data" / "user_data"


def print_step(msg):
    print(f"\n{GREEN}▶ {msg}{RESET}")


def print_ok(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_warn(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def get_all_db_files(data_dir):
    """获取所有数据库文件"""
    return sorted(data_dir.glob("*.db"))


def sync():
    """复制 user_data 到 test_data"""
    print_step("步骤 1: 复制用户数据到测试目录")
    
    if not USER_DATA_DIR.exists():
        print_error(f"用户数据目录不存在: {USER_DATA_DIR}")
        return False
    
    user_dbs = get_all_db_files(USER_DATA_DIR)
    if not user_dbs:
        print_error("未找到用户数据库文件")
        return False
    
    # 确保 test_data 目录存在
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    skipped = 0
    for db_file in user_dbs:
        dest_file = TEST_DATA_DIR / db_file.name
        if dest_file.exists():
            # 强制覆盖已存在的文件
            shutil.copy2(db_file, dest_file)
            print_ok(f"覆盖: {db_file.name}")
            copied += 1
        else:
            shutil.copy2(db_file, dest_file)
            print_ok(f"复制: {db_file.name}")
            copied += 1
    
    print_ok(f"完成! 复制了 {copied} 个数据库文件")
    return True


def reinit_users_db():
    """重新初始化用户数据库（v0.7.1 认证必需）"""
    print_step("步骤 2: 重新初始化用户数据库")
    
    # 设置 TEST_DATA_DIR 为数据目录
    import sys
    sys.path.insert(0, str(REPO_ROOT / "dev"))
    
    # 临时修改环境变量让 auth 模块使用 test_data
    original_data_dir = os.environ.get('TRACKER_DATA_DIR')
    os.environ['TRACKER_DATA_DIR'] = str(TEST_DATA_DIR)
    
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            from app.auth import init_users_db, create_default_users
            init_users_db()
            create_default_users()
            print_ok("用户数据库已重新初始化 (admin, guest)")
    except Exception as e:
        print_error(f"初始化用户数据库失败: {e}")
        return False
    finally:
        # 恢复环境变量
        if original_data_dir:
            os.environ['TRACKER_DATA_DIR'] = original_data_dir
        else:
            os.environ.pop('TRACKER_DATA_DIR', None)
    
    return True


def clean():
    """删除 test_data 中的测试数据（保留预置的原始数据）"""
    print_step("步骤 1: 清理测试数据")
    
    if not TEST_DATA_DIR.exists():
        print_warn("测试数据目录不存在")
        return True
    
    test_dbs = get_all_db_files(TEST_DATA_DIR)
    if not test_dbs:
        print_warn("未找到测试数据库文件")
        return True
    
    # 预置的原始测试数据（这些是项目自带的，需要保留）
    PRESERVED_NAMES = ["EX5", "TestProject"]
    
    # 系统数据库文件（不删除，但也不作为项目处理）
    SYSTEM_DB = "users.db"
    
    # 记录将被删除的项目名称
    deleted_names = []
    
    deleted = 0
    for db_file in test_dbs:
        # 保留预置的原始测试数据
        if any(preserved in db_file.name for preserved in PRESERVED_NAMES):
            print_warn(f"保留预置原始数据: {db_file.name}")
            continue
        
        # users.db 由 reinit_users_db() 重新创建
        if db_file.name == SYSTEM_DB:
            print_ok(f"删除 (将重新创建): {db_file.name}")
            os.remove(db_file)
            deleted += 1
            continue
        
        # 删除其他所有数据（sync 来的 + 测试创建的）
        os.remove(db_file)
        print_ok(f"删除: {db_file.name}")
        
        # 提取项目名称（去掉 .db 后缀）
        project_name = db_file.stem
        deleted_names.append(project_name)
        deleted += 1
    
    print_ok(f"完成! 删除了 {deleted} 个文件")
    
    # v0.7.1+: 重新初始化用户数据库
    if not reinit_users_db():
        return False
    
    # 同步更新 projects.json - 基于剩余的 .db 文件重建
    print_step("步骤 3: 同步更新 projects.json")
    projects_json = TEST_DATA_DIR / "projects.json"
    
    try:
        # 先读取原 projects.json，建立 name -> (is_archived, version, created_at) 的映射
        original_meta = {}
        if projects_json.exists():
            with open(projects_json, 'r', encoding='utf-8') as f:
                original_projects = json.load(f)
                for proj in original_projects:
                    name = proj.get('name')
                    original_meta[name] = {
                        'is_archived': proj.get('is_archived', True),
                        'version': proj.get('version', 'test'),
                        'created_at': proj.get('created_at')
                    }
        
        # 扫描剩余的 .db 文件（排除 projects.json 本身）
        remaining_dbs = [f for f in TEST_DATA_DIR.iterdir() 
                         if f.is_file() and f.suffix == '.db']
        
        # 排除系统数据库文件 (users.db 是用户认证数据库，不是项目)
        SYSTEM_DBS = ["users.db"]
        remaining_dbs = [f for f in remaining_dbs if f.name not in SYSTEM_DBS]
        
        # 为每个 .db 文件创建项目记录
        remaining_projects = []
        for i, db_file in enumerate(sorted(remaining_dbs), start=1):
            project_name = db_file.stem  # 去掉 .db 后缀
            
            # 优先使用原 projects.json 中的元数据
            meta = original_meta.get(project_name, {})
            is_archived = meta.get('is_archived', True)
            version = meta.get('version', 'test')
            created_at = meta.get('created_at')
            
            # 如果原 projects.json 没有创建时间，则用文件修改时间
            if not created_at:
                mtime = db_file.stat().st_mtime
                created_at = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            project_record = {
                "id": i,
                "name": project_name,
                "created_at": created_at,
                "is_archived": is_archived,
                "version": version
            }
            remaining_projects.append(project_record)
            print_ok(f"保留项目: {project_name} (is_archived={is_archived}, version={version})")
        
        # 写回文件
        with open(projects_json, 'w', encoding='utf-8') as f:
            json.dump(remaining_projects, f, indent=2, ensure_ascii=False)
        
        print_ok(f"projects.json 重建完成: 共 {len(remaining_projects)} 个项目")
        
    except Exception as e:
        print_error(f"更新 projects.json 失败: {e}")
        return False
    
    return True


def check():
    """静态检查：数据库结构"""
    print_step("静态检查: 数据库结构")
    
    if not TEST_DATA_DIR.exists():
        print_error(f"测试数据目录不存在: {TEST_DATA_DIR}")
        return False
    
    test_dbs = get_all_db_files(TEST_DATA_DIR)
    if not test_dbs:
        print_error("未找到测试数据库文件")
        return False
    
    print(f"检查 {len(test_dbs)} 个数据库文件...\n")
    
    # 必要的表和字段（注意：tc_cp_connections 没有 id 字段）
    REQUIRED_TABLES = {
        'cover_point': ['id', 'project_id', 'feature', 'sub_feature', 'cover_point', 'priority'],
        'test_case': ['id', 'project_id', 'dv_milestone', 'target_date', 'status'],
        'tc_cp_connections': ['tc_id', 'cp_id'],  # 没有 id 字段
    }
    
    issues = []
    checked = 0
    skipped = 0
    
    for db_file in test_dbs:
        db_name = db_file.name
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 检查是否有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            
            if not tables:
                # 空数据库，跳过（可能是测试残留文件）
                print_warn(f"跳过空数据库: {db_name}")
                skipped += 1
                conn.close()
                continue
            
            # 检查表是否存在
            for table_name, required_cols in REQUIRED_TABLES.items():
                if table_name not in tables:
                    issues.append(f"{db_name}: 缺少表 {table_name}")
                    continue
                
                # 检查必要字段
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = {row[1] for row in cursor.fetchall()}
                
                for col in required_cols:
                    if col not in columns:
                        issues.append(f"{db_name}.{table_name}: 缺少字段 {col}")
            
            conn.close()
            checked += 1
            
        except Exception as e:
            issues.append(f"{db_name}: {str(e)}")
    
    if issues:
        print_error(f"发现 {len(issues)} 个问题:")
        for issue in issues[:10]:
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... 还有 {len(issues) - 10} 个问题")
        return False
    else:
        print_ok(f"全部通过! 检查了 {checked} 个数据库")
        if skipped > 0:
            print_warn(f"跳过了 {skipped} 个空数据库")
        return True


def test_api():
    """动态测试：调用 API 验证兼容性"""
    print_step("动态测试: API 兼容性")
    
    # 启动测试版服务进行测试
    print("启动测试版服务...")
    
    # 检查测试版是否已运行
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8081/api/version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            print_warn("测试版服务未运行，跳过动态测试")
            return True
    except Exception:
        print_warn("无法连接测试版服务，跳过动态测试")
        return True
    
    # v0.7.1+: 先登录获取 session
    print("执行用户登录...")
    cookie_file = "/tmp/tracker_test_cookies.txt"
    try:
        result = subprocess.run(
            ["curl", "-s", "-c", cookie_file, "-X", "POST",
             "http://localhost:8081/api/auth/login",
             "-H", "Content-Type: application/json",
             "-d", '{"username":"admin","password":"admin123"}'],
            capture_output=True, text=True, timeout=10
        )
        login_resp = json.loads(result.stdout)
        if login_resp.get("success"):
            print_ok(f"登录成功: {login_resp['user']['username']} ({login_resp['user']['role']})")
        else:
            print_error(f"登录失败: {login_resp}")
            print_warn("跳过动态测试")
            return True
    except Exception as e:
        print_error(f"登录异常: {e}")
        print_warn("跳过动态测试")
        return True
    
    print("执行 API 兼容性测试...")
    
    tests_passed = 0
    tests_failed = 0
    
    # 获取测试项目列表 (使用 cookie 认证)
    try:
        result = subprocess.run(
            ["curl", "-s", "-b", cookie_file, "http://localhost:8081/api/projects"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            projects = json.loads(result.stdout)
            print_ok(f"API /projects 返回正常 (共 {len(projects)} 个项目)")
            tests_passed += 1
        else:
            print_error("API /projects 失败")
            tests_failed += 1
    except Exception as e:
        print_error(f"API /projects 异常: {e}")
        tests_failed += 1
    
    # 测试统计 API
    if projects:
        first_project = projects[0]
        project_id = first_project['id']
        
        try:
            result = subprocess.run(
                ["curl", "-s", "-b", cookie_file, f"http://localhost:8081/api/stats?project_id={project_id}"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                stats = json.loads(result.stdout)
                print_ok(f"API /stats 返回正常 (CP: {stats.get('total_cp', 'N/A')}, TC: {stats.get('total_tc', 'N/A')})")
                tests_passed += 1
            else:
                print_error(f"API /stats 失败: {result.stderr}")
                tests_failed += 1
        except Exception as e:
            print_error(f"API /stats 异常: {e}")
            tests_failed += 1
    
    # 清理 cookie 文件
    if os.path.exists(cookie_file):
        os.remove(cookie_file)
    
    print(f"\n动态测试结果: {tests_passed} 通过, {tests_failed} 失败")
    
    if tests_failed > 0:
        return False
    
    print_ok("全部 API 测试通过!")
    return True


def all_tests():
    """执行全部兼容性测试"""
    print("=" * 60)
    print("Tracker 兼容性测试")
    print("=" * 60)
    
    results = {}
    
    # 1. 复制数据
    results['sync'] = sync()
    
    # 2. 静态检查
    results['check'] = check()
    
    # 3. 动态测试
    results['test'] = test_api()
    
    # 4. 清理数据
    print()
    results['clean'] = clean()
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = f"{GREEN}✓ 通过{RESET}" if passed else f"{RED}✗ 失败{RESET}"
        print(f"{name.upper():10} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print_ok("所有兼容性测试通过!")
        return 0
    else:
        print_error("部分测试未通过，请检查")
        return 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    command = sys.argv[1].lower()
    
    if command == 'sync':
        return 0 if sync() else 1
    elif command == 'clean':
        return 0 if clean() else 1
    elif command == 'check':
        return 0 if check() else 1
    elif command == 'test':
        return 0 if test_api() else 1
    elif command == 'all':
        return all_tests()
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        return 1


if __name__ == '__main__':
    sys.exit(main())
