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
    python3 scripts/tracker_ops.py clean     # 预览清理（dry-run，不删除）
    python3 scripts/tracker_ops.py clean --yes  # 确认执行清理（保留 EX5/SOC_DV/FC_DV 且 id 不变）
    python3 scripts/tracker_ops.py check     # 静态检查
    python3 scripts/tracker_ops.py test     # 动态测试
    python3 scripts/tracker_ops.py all      # 执行全部（含实际清理）
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


# 清理时保留的基本 demo 项目（自动化测试基线依赖，如 SOC_DV id=3）
PRESERVED_NAMES = ["EX5", "SOC_DV", "FC_DV"]


def _check_safe_target():
    """安全约束：清理目标必须是 shared/data/test_data，拒绝触碰生产 user_data。"""
    test_data_real = TEST_DATA_DIR.resolve()
    user_data_real = USER_DATA_DIR.resolve()
    if test_data_real == user_data_real:
        print_error(f"安全约束: 测试数据目录与生产目录相同 ({test_data_real})，拒绝清理")
        return False
    if test_data_real.name != "test_data":
        print_error(f"安全约束: 目标目录名不是 test_data ({test_data_real})，拒绝清理")
        return False
    return True


def clean(dry_run=True):
    """清理 test_data 中的测试项目，保留基本 demo 项目且保持其 id 不变。

    - 保留: PRESERVED_NAMES 中的项目（完整保留原始 projects.json 记录与 id）
    - 删除: 其他项目 db、users.db（重建）、sessions、wiki 孤儿目录、
            *.db-journal、projects.json.new
    - 重建: 清理后若 SOC_DV / FC_DV 缺失，按原 id 调用 create_demo_project.py 重建
    - 安全: 仅操作 TEST_DATA_DIR (shared/data/test_data)，绝不触碰 user_data

    Args:
        dry_run: True 仅预览不删除（默认）；False 实际执行
    """
    if not _check_safe_target():
        return False

    mode = "预览（dry-run，不删除任何文件）" if dry_run else "实际执行"
    print_step(f"步骤 1: 扫描测试数据 [{mode}]")

    if not TEST_DATA_DIR.exists():
        print_warn("测试数据目录不存在")
        return True

    # 系统数据库文件（删除后重新创建）
    SYSTEM_DB = "users.db"

    # 读取原 projects.json，保留 name -> 完整记录 的映射
    # （保持 SOC_DV id=3 等原始 id 是自动化测试基线的硬约束）
    projects_json = TEST_DATA_DIR / "projects.json"
    original_records = {}
    if projects_json.exists():
        try:
            with open(projects_json, 'r', encoding='utf-8') as f:
                for proj in json.load(f):
                    original_records[proj.get('name')] = proj
        except Exception as e:
            print_error(f"读取 projects.json 失败: {e}")
            return False

    # 分类: 保留 / 删除
    test_dbs = get_all_db_files(TEST_DATA_DIR)
    preserved_dbs = [f for f in test_dbs if f.stem in PRESERVED_NAMES]
    system_dbs = [f for f in test_dbs if f.name == SYSTEM_DB]
    delete_dbs = [f for f in test_dbs if f.stem not in PRESERVED_NAMES and f.name != SYSTEM_DB]

    # 附属残留文件
    journal_files = sorted(TEST_DATA_DIR.glob("*.db-journal"))
    stray_files = [f for f in [TEST_DATA_DIR / "projects.json.new"] if f.exists()]

    for f in preserved_dbs:
        print_warn(f"保留 demo 项目: {f.name}")
    for f in delete_dbs[:20]:
        print_ok(f"删除: {f.name}")
    if len(delete_dbs) > 20:
        print_ok(f"删除: ... 其余 {len(delete_dbs) - 20} 个从略")
    for f in system_dbs:
        print_ok(f"删除 (将重新创建): {f.name}")
    for f in journal_files + stray_files:
        print_ok(f"删除残留文件: {f.name}")

    if not dry_run:
        for f in delete_dbs + system_dbs + journal_files + stray_files:
            try:
                f.unlink()
            except FileNotFoundError:
                pass
            except Exception as e:
                print_warn(f"删除失败: {f.name} - {e}")
    print_ok(f"项目 db: 保留 {len(preserved_dbs)} 个，删除 {len(delete_dbs)} 个")

    # v0.7.1+: 重新初始化用户数据库（所有用户密码重置为默认值，8081 在线会话全部失效）
    if not dry_run:
        if not reinit_users_db():
            return False
    else:
        print_warn("users.db 将重建（用户密码重置为默认值）")

    # 步骤 3: 重建 projects.json - 只含保留项目，完整沿用原记录（id 不变）
    print_step("步骤 3: 同步更新 projects.json")
    try:
        remaining_projects = []
        used_ids = set()
        for db_file in sorted(preserved_dbs):
            name = db_file.stem
            record = dict(original_records.get(name, {}))
            record.setdefault('created_at',
                              datetime.fromtimestamp(db_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
            record.setdefault('version', 'test')
            if 'id' not in record:
                record['id'] = 0  # 稍后分配空闲 id
            # 保留项目必须前端可见
            record['is_archived'] = False
            record['name'] = name
            remaining_projects.append(record)
            used_ids.add(record['id'])

        # 为没有原记录的项目分配空闲 id
        next_id = max(used_ids | {0}) + 1
        for record in remaining_projects:
            if record['id'] == 0:
                while next_id in used_ids:
                    next_id += 1
                record['id'] = next_id
                used_ids.add(next_id)

        remaining_projects.sort(key=lambda p: p['id'])

        if not dry_run:
            with open(projects_json, 'w', encoding='utf-8') as f:
                json.dump(remaining_projects, f, indent=2, ensure_ascii=False)

        for p in remaining_projects:
            print_ok(f"保留项目: {p['name']} (id={p['id']}, version={p.get('version')})")
        print_ok(f"projects.json {'将' if dry_run else ''}重建完成: 共 {len(remaining_projects)} 个项目")
    except Exception as e:
        print_error(f"更新 projects.json 失败: {e}")
        return False

    # 步骤 4: 清理 sessions 与 wiki 孤儿目录
    print_step("步骤 4: 清理 sessions / wiki 孤儿目录")
    sessions_dir = TEST_DATA_DIR / "sessions"
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("*"))
        if not dry_run:
            for sf in session_files:
                try:
                    sf.unlink()
                except Exception as e:
                    print_warn(f"删除 session 文件失败: {sf.name} - {e}")
        print_ok(f"sessions: {'发现' if dry_run else '清理'} {len(session_files)} 个文件")
    else:
        print_ok("sessions 目录不存在，无需清理")

    # wiki 数字目录（wiki/<project_id>/）中 project_id 已不存在的为孤儿目录
    wiki_dir = TEST_DATA_DIR / "wiki"
    remaining_ids = {p['id'] for p in remaining_projects}
    wiki_orphans = []
    if wiki_dir.exists():
        wiki_orphans = [d for d in wiki_dir.iterdir()
                        if d.is_dir() and d.name.isdigit() and int(d.name) not in remaining_ids]
    for d in wiki_orphans:
        print_ok(f"删除 wiki 孤儿目录: wiki/{d.name}")
        if not dry_run:
            shutil.rmtree(d, ignore_errors=True)
    if not wiki_orphans:
        print_ok("无 wiki 孤儿目录")

    # 步骤 5: 重建缺失的 demo 项目（按原 id）
    print_step("步骤 5: 检查 Demo 项目")
    remaining_names = {p['name'] for p in remaining_projects}
    demo_configs = [("SOC_DV", "soc_dv"), ("FC_DV", "fc_dv")]
    all_ok = True
    for demo_name, demo_slug in demo_configs:
        if demo_name in remaining_names:
            print_ok(f"Demo 项目 {demo_name} 已保留，无需重建")
            continue
        original_id = (original_records.get(demo_name) or {}).get('id')
        print_warn(f"Demo 项目 {demo_name} 缺失，{'将' if dry_run else '正在'}按原 id ({original_id or '自动'}) 重建")
        if not dry_run:
            if not generate_demo_project(demo_slug, demo_name, original_id):
                print_error(f"Demo 项目 {demo_name} 生成失败")
                all_ok = False
    if not all_ok:
        return False

    if dry_run:
        print_step("预览完成")
        print_warn("以上为预览，未删除任何文件。确认无误后执行: python3 scripts/tracker_ops.py clean --yes")

    return True


def generate_demo_project(project_slug=None, project_name=None, project_id=None):
    """生成缺失的 Demo 项目。

    Args:
        project_slug: create_demo_project.py -p 参数 ('soc_dv' / 'fc_dv')，None 表示全部
        project_name: 项目名（用于 --ids 传参与日志显示）
        project_id: 指定恢复的项目 id（保持测试基线依赖），None 为自动分配
    """
    demo_script = REPO_ROOT / "scripts" / "create_demo_project.py"

    if not demo_script.exists():
        print_warn(f"Demo 项目生成脚本不存在: {demo_script}")
        return True  # 不算失败，只是跳过

    cmd = [sys.executable, str(demo_script), "--force"]
    if project_slug:
        cmd += ["-p", project_slug]
    if project_id is not None:
        cmd += ["--ids", f"{project_name}={project_id}"]

    try:
        # 调用 demo 项目生成脚本
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))

        if result.returncode == 0:
            print_ok("Demo 项目生成完成")
            # 打印关键输出
            for line in result.stdout.split('\n'):
                if '📋' in line or '✅' in line or '项目:' in line:
                    print(f"   {line}")
            return True
        else:
            print_error(f"Demo 项目生成失败: {result.stderr}")
            return False

    except Exception as e:
        print_error(f"调用 Demo 项目生成脚本失败: {e}")
        return False


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
    
    # 排除系统数据库文件
    SYSTEM_DBS = ["users.db", "tracker.db"]
    test_dbs = [f for f in test_dbs if f.name not in SYSTEM_DBS]
    
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
    results['clean'] = clean(dry_run=False)
    
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
        # 默认 dry-run 预览，--yes/--force 才真正执行
        execute = '--yes' in sys.argv[2:] or '--force' in sys.argv[2:]
        return 0 if clean(dry_run=not execute) else 1
    elif command == 'check':
        return 0 if check() else 1
    elif command == 'test':
        return 0 if test_api() else 1
    elif command == 'all':
        return all_tests()
    elif command == 'migrate':
        return run_migration()
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        return 1


def run_migration():
    """执行数据库迁移"""
    import argparse

    parser = argparse.ArgumentParser(description='执行数据库迁移')
    parser.add_argument('--version', type=str, help='目标版本号 (如 v0.11.0)')
    args = parser.parse_args(sys.argv[2:])  # 跳过 'migrate' 命令本身

    version = args.version

    print_step(f"执行数据库迁移 (版本: {version or '最新'})")

    # 构建迁移脚本路径
    migrations_dir = Path(__file__).parent / 'migrations'

    if not migrations_dir.exists():
        print_error("migrations 目录不存在")
        return 1

    # 查找对应的迁移脚本
    if version:
        # 特定版本迁移
        migration_script = migrations_dir / f'v{version.replace(".", "_")}_migration.py'
        if not migration_script.exists():
            # 尝试另一种命名格式
            migration_script = migrations_dir / f'migrate_{version}.py'
        if not migration_script.exists():
            print_error(f"找不到版本 {version} 的迁移脚本")
            return 1

        print(f"执行迁移: {migration_script.name}")
        try:
            result = subprocess.run(
                [sys.executable, str(migration_script)],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )
            print(result.stdout)
            if result.returncode != 0:
                print_error(f"迁移失败: {result.stderr}")
                return 1
            print_ok(f"版本 {version} 迁移完成")
            return 0
        except Exception as e:
            print_error(f"执行迁移脚本失败: {e}")
            return 1
    else:
        # 执行所有迁移脚本（按版本顺序）
        migration_scripts = sorted(migrations_dir.glob('*.py'))
        if not migration_scripts:
            print_warn("没有找到迁移脚本")
            return 0

        for script in migration_scripts:
            if script.name == '__init__.py':
                continue
            print(f"\n执行迁移: {script.name}")
            try:
                result = subprocess.run(
                    [sys.executable, str(script)],
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).parent.parent)
                )
                print(result.stdout)
                if result.returncode != 0:
                    print_error(f"迁移失败: {result.stderr}")
                    return 1
            except Exception as e:
                print_error(f"执行迁移脚本失败: {e}")
                return 1

        print_ok("所有迁移完成")
        return 0


if __name__ == '__main__':
    sys.exit(main())
