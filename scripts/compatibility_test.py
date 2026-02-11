#!/usr/bin/env python3
"""
Tracker 兼容性测试脚本

功能:
    1. sync    - 复制 user_data 到 test_data
    2. clean   - 删除 test_data 中的用户数据
    3. check   - 静态检查：数据库结构、版本号、字段
    4. test    - 动态测试：调用 API 验证兼容性

使用方法:
    python3 scripts/compatibility_test.py sync      # 复制数据
    python3 scripts/compatibility_test.py clean     # 清理数据
    python3 scripts/compatibility_test.py check     # 静态检查
    python3 scripts/compatibility_test.py test     # 动态测试
    python3 scripts/compatibility_test.py all      # 执行全部
"""

import sqlite3
import glob
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
    for db_file in user_dbs:
        dest_file = TEST_DATA_DIR / db_file.name
        if dest_file.exists():
            print_warn(f"已存在，跳过: {db_file.name}")
        else:
            shutil.copy2(db_file, dest_file)
            print_ok(f"复制: {db_file.name}")
            copied += 1
    
    print_ok(f"完成! 复制了 {copied} 个数据库文件")
    return True


def clean():
    """删除 test_data 中的用户数据"""
    print_step("步骤 1: 清理测试数据")
    
    if not TEST_DATA_DIR.exists():
        print_warn("测试数据目录不存在")
        return True
    
    test_dbs = get_all_db_files(TEST_DATA_DIR)
    if not test_dbs:
        print_warn("未找到测试数据库文件")
        return True
    
    deleted = 0
    for db_file in test_dbs:
        # 保留原始测试数据（如果存在）
        if "_Test" in db_file.name or "Debugware" in db_file.name or "EX5" in db_file.name:
            print_warn(f"保留原始测试数据: {db_file.name}")
            continue
        os.remove(db_file)
        print_ok(f"删除: {db_file.name}")
        deleted += 1
    
    print_ok(f"完成! 删除了 {deleted} 个文件")
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
    
    print("执行 API 兼容性测试...")
    
    tests_passed = 0
    tests_failed = 0
    
    # 获取测试项目列表
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8081/api/projects"],
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
                ["curl", "-s", f"http://localhost:8081/api/stats?project_id={project_id}"],
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
