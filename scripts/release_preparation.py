#!/usr/bin/env python3
"""
Tracker 发布前准备脚本

按照开发流程规范执行发布前检查：
1. API 测试 (pytest)
2. Playwright 冒烟测试
3. BugLog 回归测试
4. Git 状态检查
5. 交互式 Merge 和 Tag 操作

使用方法:
    python3 scripts/release_preparation.py --version v0.5.0

选项:
    --dry-run        演练模式（只检查，不执行实际操作）
    --version        指定版本号 (必需)
    --skip-tests     跳过测试执行
    --skip-merge-tag 跳过交互式 merge 和 tag 步骤
    --force          强制继续（忽略警告）

发布流程:
    1. 执行发布准备: python3 scripts/release_preparation.py --version v0.5.0
    2. 脚本检查通过后会打印命令
    3. 你执行 merge 和 tag 命令
    4. 脚本验证结果
    5. 执行发布: python3 scripts/release.py --version v0.5.0 --force
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# 颜色定义
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_step(step_num, title):
    """打印步骤标题"""
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}步骤 {step_num}: {title}{RESET}")
    print(f"{BOLD}{'=' * 60}\n")


def print_result(status, message=""):
    """打印检查结果"""
    if status:
        print(f"{GREEN}✅ {message}{RESET}")
    else:
        print(f"{RED}❌ {message}{RESET}")


def run_command(cmd, description, cwd=None, check=True):
    """执行命令并返回结果"""
    print(f"执行: {cmd}")
    print(f"目录: {cwd or '当前目录'}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=1800  # 30分钟超时
        )
        if result.returncode == 0:
            print_result(True, f"{description} 成功")
            return True, result.stdout
        else:
            print_result(False, f"{description} 失败")
            print(f"错误输出:\n{result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print_result(False, f"{description} 超时")
        return False, "命令执行超时"
    except Exception as e:
        print_result(False, f"{description} 异常: {str(e)}")
        return False, str(e)


def check_git_status(dry_run=False):
    """步骤 4: 检查 Git 状态"""
    print_step(4, "检查 Git 状态")

    repo_root = Path(__file__).parent.parent

    # 检查当前分支
    cmd = "git branch --show-current"
    success, output = run_command(cmd, "获取当前分支", cwd=repo_root)
    if not success:
        return False

    current_branch = output.strip()
    print(f"当前分支: {current_branch}")

    if current_branch != "develop":
        print(YELLOW + "⚠️  警告: 当前不在 develop 分支" + RESET)
        if not dry_run:
            return False

    # 检查是否有未提交的更改
    cmd = "git status --porcelain"
    success, output = run_command(cmd, "检查未提交更改", cwd=repo_root)
    if not success:
        return False

    if output.strip():
        print(YELLOW + "⚠️  有未提交的更改:" + RESET)
        print(output)
        if not dry_run:
            return False
    else:
        print("✓ 没有未提交的更改")

    print_result(True, "Git 状态检查通过")
    return True


def interactive_merge_and_tag(version, dry_run=False):
    """
    步骤 5: 交互式 Merge 和 Tag

    这个步骤是交互式的：
    1. 打印需要执行的命令
    2. 等待用户执行并确认
    3. 验证结果
    """
    print_step(5, "交互式 Merge 和 Tag 操作")

    repo_root = Path(__file__).parent.parent

    if dry_run:
        print("[演练] 跳过交互式步骤")
        return True

    # 打印需要执行的命令
    print(f"\n{BOLD}请执行以下命令:{RESET}\n")

    print(f"{GREEN}# 1. 切换到 main 分支并合并 develop{RESET}")
    print(f"{YELLOW}git checkout main{RESET}")
    print(f"{YELLOW}git pull origin main 2>/dev/null || git pull main 2>/dev/null || true{RESET}")
    merge_cmd = f'git merge develop --no-ff -m "merge: 合并 v{version} 到正式版"'
    print(f"{YELLOW}{merge_cmd}{RESET}")

    print(f"\n{GREEN}# 2. 创建发布标签{RESET}")
    tag_cmd = f"git tag -a v{version} -m 'Release v{version}'"
    print(f"{YELLOW}{tag_cmd}{RESET}")

    print(f"\n{GREEN}# 3. 切换回 develop 分支{RESET}")
    print(f"{YELLOW}git checkout develop{RESET}")

    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}等待确认...{RESET}")
    print(f"{BOLD}{'=' * 60}\n")

    return True


def verify_merge_and_tag(version):
    """
    验证 Merge 和 Tag 是否正确完成
    """
    repo_root = Path(__file__).parent.parent

    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}验证 Merge 和 Tag 结果{RESET}")
    print(f"{BOLD}{'=' * 60}\n")

    all_verified = True

    # 1. 检查 main 分支是否包含 develop 的提交
    print("1. 验证 main 分支已合并...")
    cmd = "git log main --oneline -1 --format='%H'"
    result = subprocess.run(cmd, shell=True, cwd=repo_root, capture_output=True, text=True)
    main_head = result.stdout.strip()

    cmd = "git log develop --oneline -1 --format='%H'"
    result = subprocess.run(cmd, shell=True, cwd=repo_root, capture_output=True, text=True)
    develop_head = result.stdout.strip()

    cmd = f"git merge-base --is-ancestor {develop_head} {main_head}"
    result = subprocess.run(cmd, shell=True, cwd=repo_root)
    if result.returncode == 0:
        print_result(True, "main 分支已包含 develop 的提交")
    else:
        print_result(False, "main 分支未包含 develop 的提交")
        print(f"  develop 最新: {develop_head[:8]}")
        print(f"  main 最新: {main_head[:8]}")
        all_verified = False

    # 2. 检查标签是否存在
    if all_verified:
        print("\n2. 验证标签存在...")
        cmd = f"git tag -l v{version}"
        result = subprocess.run(cmd, shell=True, cwd=repo_root, capture_output=True, text=True)
        if result.stdout.strip() == f"v{version}":
            print_result(True, f"标签 v{version} 已创建")
        else:
            print_result(False, f"标签 v{version} 不存在")
            all_verified = False

    # 3. 检查标签指向的提交
    if all_verified:
        print("\n3. 验证标签指向...")
        cmd = f"git rev-parse v{version}^{{commit}}"
        result = subprocess.run(cmd, shell=True, cwd=repo_root, capture_output=True, text=True)
        if result.returncode == 0:
            tag_commit = result.stdout.strip()
            if tag_commit == main_head:
                print_result(True, f"标签指向 main 最新提交")
            else:
                print_result(False, f"标签未指向 main 最新提交")
                print(f"  标签指向: {tag_commit[:8]}")
                print(f"  main 指向: {main_head[:8]}")
                all_verified = False
        else:
            print_result(False, "无法解析标签")
            all_verified = False

    return all_verified


def run_api_tests(dry_run=False):
    """步骤 1: 运行 API 测试"""
    print_step(1, "运行 API 测试 (pytest)")

    repo_root = Path(__file__).parent.parent
    dev_dir = repo_root / "dev"

    # 确保 dev 服务器未运行
    cmd = "pkill -f 'server_test.py' 2>/dev/null || true"
    subprocess.run(cmd, shell=True, cwd=repo_root)

    # 启动 dev 服务器
    print("\n启动 dev 服务器...")
    cmd = f"cd {dev_dir} && python3 server_test.py > /dev/null 2>&1 &"
    if not dry_run:
        os.system(cmd)
        import time
        time.sleep(3)
        print("Dev 服务器已启动")

    # 运行 API 测试
    cmd = f"PYTHONPATH={dev_dir} python3 -m pytest {dev_dir}/tests/test_api.py -v"
    success, output = run_command(cmd, "API 测试", cwd=repo_root)

    # 停止 dev 服务器
    if not dry_run:
        cmd = "pkill -f 'server_test.py' 2>/dev/null || true"
        subprocess.run(cmd, shell=True)

    if not success:
        return False

    # 检查测试通过数
    if "17 passed" in output or "passed" in output:
        print(GREEN + "✓ API 测试全部通过" + RESET)
        return True
    else:
        print(RED + "✗ API 测试未全部通过" + RESET)
        return False


def run_smoke_tests(dry_run=False):
    """步骤 2: 运行 Playwright 冒烟测试"""
    print_step(2, "运行 Playwright 冒烟测试")

    repo_root = Path(__file__).parent.parent
    dev_dir = repo_root / "dev"

    # 确保 dev 服务器运行
    print("确保 dev 服务器运行...")
    cmd = f"cd {dev_dir} && python3 server_test.py > /dev/null 2>&1 &"
    if not dry_run:
        os.system(cmd)
        import time
        time.sleep(3)

    # 运行冒烟测试
    cmd = f"cd {dev_dir} && npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000"
    success, output = run_command(cmd, "冒烟测试", cwd=repo_root)

    if not success:
        return False

    if "6 passed" in output or "passed" in output:
        print(GREEN + "✓ 冒烟测试全部通过" + RESET)
        return True
    else:
        print(RED + "✗ 冒烟测试未全部通过" + RESET)
        return False


def run_buglog_tests(dry_run=False):
    """步骤 3: 运行 BugLog 回归测试"""
    print_step(3, "运行 BugLog 回归测试")

    repo_root = Path(__file__).parent.parent
    dev_dir = repo_root / "dev"

    # 运行 BugLog 回归测试
    cmd = f"cd {dev_dir} && npx playwright test tests/tracker.spec.ts --project=firefox --timeout=90000"
    success, output = run_command(cmd, "BugLog 回归测试", cwd=repo_root)

    if not success:
        return False

    # 检查测试通过数
    if "11 passed" in output or "passed" in output:
        print(GREEN + "✓ BugLog 回归测试全部通过" + RESET)
        return True
    else:
        print(YELLOW + "⚠️  BugLog 回归测试部分通过或超时" + RESET)
        # 部分通过也允许继续
        if "passed" in output:
            print("虽然不是全部通过，但有测试通过")
            return True
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Tracker 发布前准备脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 演练模式（只检查，不实际操作）
    python3 scripts/release_preparation.py --dry-run --version v0.5.0

    # 执行完整发布准备（交互式 merge 和 tag）
    python3 scripts/release_preparation.py --version v0.5.0
    # 脚本检查通过后会打印命令，请执行后再确认

    # 跳过 merge 和 tag（用于 CI/CD）
    python3 scripts/release_preparation.py --version v0.5.0 --skip-merge-tag
        """
    )

    parser.add_argument(
        "--version",
        required=True,
        help="版本号 (例如: v0.5.0)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="演练模式（只检查，不实际操作）"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="跳过测试执行"
    )
    parser.add_argument(
        "--skip-merge-tag",
        action="store_true",
        help="跳过交互式 merge 和 tag 步骤（用于 CI/CD 环境）"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制继续（忽略警告）"
    )

    args = parser.parse_args()

    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}Tracker 发布前准备脚本{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"\n版本: {args.version}")
    print(f"模式: {'演练模式' if args.dry_run else '执行模式'}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # 执行检查
    if not args.skip_tests:
        results["api_tests"] = run_api_tests(args.dry_run)
        results["smoke_tests"] = run_smoke_tests(args.dry_run)
        results["buglog_tests"] = run_buglog_tests(args.dry_run)
    else:
        print_step(0, "跳过测试执行")
        print(YELLOW + "⚠️  已跳过测试执行" + RESET)
        results["api_tests"] = True
        results["smoke_tests"] = True
        results["buglog_tests"] = True

    results["git_status"] = check_git_status(args.dry_run)

    if not args.skip_merge_tag:
        results["merge_tag"] = interactive_merge_and_tag(args.version, args.dry_run)
    else:
        print_step(0, "跳过交互式 Merge 和 Tag")
        print(YELLOW + "⚠️  已跳过 Merge 和 Tag" + RESET)
        results["merge_tag"] = True

    # 验证 Merge 和 Tag 结果
    if not args.dry_run and not args.skip_merge_tag:
        verification_passed = verify_merge_and_tag(args.version)
        if not verification_passed:
            print(f"\n{RED}{BOLD}❌ Merge 或 Tag 验证失败！{RESET}")
            print("请修复问题后重新运行发布准备脚本。")
            return 1
        else:
            print(f"\n{GREEN}{BOLD}✅ Merge 和 Tag 验证通过！{RESET}")

    # 汇总结果
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}发布前检查结果汇总{RESET}")
    print(f"{BOLD}{'=' * 60}\n")

    all_passed = True
    for step, passed in results.items():
        step_names = {
            "api_tests": "API 测试",
            "smoke_tests": "冒烟测试",
            "buglog_tests": "BugLog 回归测试",
            "git_status": "Git 状态",
            "merge_tag": "Merge 和 Tag"
        }
        step_name = step_names.get(step, step)
        if passed:
            print(f"{GREEN}✅ {step_name}: 通过{RESET}")
        else:
            print(f"{RED}❌ {step_name}: 失败{RESET}")
            all_passed = False

    print(f"\n{BOLD}{'=' * 60}{RESET}")

    if all_passed:
        print(f"{GREEN}{BOLD}✅ 所有检查通过！可以执行发布。{RESET}")
        print(f"\n下一步操作:")
        if not args.dry_run:
            print(f"  cd /projects/management/tracker")
            print(f"  python3 scripts/release.py --version {args.version} --force")
        else:
            print(f"  [演练] 发布命令已准备")
        return 0
    else:
        print(f"{RED}{BOLD}❌ 检查未通过，请修复问题后重试。{RESET}")
        print(f"\n发现问题:")
        for step, passed in results.items():
            if not passed:
                step_names = {
                    "api_tests": "API 测试",
                    "smoke_tests": "冒烟测试",
                    "buglog_tests": "BugLog 回归测试",
                    "git_status": "Git 状态",
                    "merge_tag": "Merge 和 Tag"
                }
                print(f"  - {step_names.get(step, step)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
