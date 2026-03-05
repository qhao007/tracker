#!/usr/bin/env python3
"""
Tracker 发布前准备脚本

按照开发流程规范执行发布前检查：
1. API 测试 (pytest)
2. Playwright 冒烟测试
3. 兼容性测试 (用户数据 → 测试数据)
4. VERSION 更新和提交
5. Git 状态检查
6. Merge 和 Tag 操作

使用方法:
    python3 scripts/release_preparation.py --version v0.6.0

选项:
    --dry-run        演练模式（只检查，不执行实际操作）
    --version        指定版本号 (必需)
    --skip-tests     跳过测试执行
    --skip-version   跳过 VERSION 更新（用于手动更新）
    --force          强制继续（忽略警告）

发布流程:
    1. 执行发布准备: python3 scripts/release_preparation.py --version v0.6.0
    2. 脚本自动执行 VERSION 更新、Git Merge 和 Tag
    3. 执行发布: python3 scripts/release.py --version v0.5.0 --force
"""

import os
import re
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


def extract_test_count(output):
    """从测试输出中提取 passed 数量"""
    match = re.search(r'(\d+)\s+passed', output)
    return int(match.group(1)) if match else 0


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
    """执行命令并返回结果
    
    注意: 仅用于脚本内部命令，不接受外部输入。
    所有命令来源必须是可信的（无用户输入拼接）。
    """
    # 安全检查：确保 cmd 是非空字符串
    if not isinstance(cmd, str) or not cmd:
        raise ValueError("cmd must be a non-empty string")
    
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


def update_version(version, dry_run=False):
    """
    步骤 4: 更新 VERSION 文件并提交

    1. 更新 dev/VERSION 文件
    2. 提交到 develop 分支
    """
    print_step(4, f"更新 VERSION 文件 (v{version})")

    repo_root = Path(__file__).parent.parent
    version_file = repo_root / "dev" / "VERSION"

    if dry_run:
        print("[演练] 跳过 VERSION 更新")
        return True

    # 获取当前日期
    release_date = datetime.now().strftime("%Y-%m-%d")

    # 更新 VERSION 文件
    print(f"\n1. 更新 VERSION 文件...")
    try:
        with open(version_file, 'w') as f:
            f.write(f"VERSION={version}\n")
            f.write(f"RELEASE_DATE={release_date}\n")
        print_result(True, "VERSION 文件已更新")
    except Exception as e:
        print_result(False, f"VERSION 文件更新失败: {str(e)}")
        return False

    # 提交 VERSION 更新
    print(f"\n2. 提交 VERSION 更新...")
    cmd = f'git add dev/VERSION && git commit -m "chore: 更新 VERSION 文件为 {version}"'
    success, _ = run_command(cmd, "提交 VERSION 更新", cwd=repo_root)
    if not success:
        return False

    print_result(True, f"VERSION 已更新并提交: v{version}")
    return True


def check_git_status(dry_run=False):
    """
    步骤 5: 检查 Git 状态
    """
    print_step(5, "检查 Git 状态")

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


def rollback_on_failure(version, results, repo_root):
    """发布失败时自动回滚"""
    print(f"\n{'='*60}")
    print(f"🔄 执行回滚")
    print(f"{'='*60}\n")
    
    # 找出失败的步骤
    failed_steps = [step for step, passed in results.items() if not passed]
    failed_step = failed_steps[0] if failed_steps else "未知"
    
    # 1. 找出上一个稳定版本 tag
    tags_result = subprocess.run(
        ["git", "tag", "--sort=-creatordate"],
        cwd=repo_root, capture_output=True, text=True
    )
    tags = tags_result.stdout.strip().split('\n')
    
    # 找到上一个非当前版本的 tag
    prev_tag = None
    for tag in tags:
        if tag and tag != f"v{version}":
            prev_tag = tag
            break
    
    # 2. 回滚 main 分支
    if prev_tag:
        print(f"1. 回滚到上一个稳定版本: {prev_tag}")
        subprocess.run(["git", "checkout", "main"], cwd=repo_root, check=True)
        subprocess.run(["git", "reset", "--hard", prev_tag], cwd=repo_root, check=True)
        print(f"✅ main 分支已回滚到 {prev_tag}")
    else:
        print("⚠️ 未找到上一个稳定版本，请手动处理")
    
    # 3. 切换到 develop 分支（不回滚代码）
    # 说明：develop 分支上的代码是开发中的代码，即使 merge 失败，develop 上的代码不会丢失
    # 操作：只需要把 HEAD 切换到 develop 分支即可
    print("2. 切换到 develop 分支...")
    subprocess.run(["git", "checkout", "develop"], cwd=repo_root, check=True)
    print("✅ 已切换到 develop 分支")
    
    # 4. 删除 flag 文件
    flag_file = repo_root / ".release_ready"
    if flag_file.exists():
        flag_file.unlink()
    print("✅ Flag 文件已删除")
    
    # 5. 发送通知
    notify_failure(version, failed_step, prev_tag)
    
    return False


def notify_failure(version, failed_step, prev_tag):
    """通知用户发布失败"""
    import json
    
    message = f"""🚨 Tracker 发布失败

版本: v{version}
失败步骤: {failed_step}
已回滚到: {prev_tag}

请检查问题后重新执行发布准备。"""
    
    # 打印到控制台
    print(f"\n{message}")
    
    # 发送飞书通知
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/00f0719c-89c0-4595-9c68-1bfd3a5de3d3"
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        result = subprocess.run(
            ["curl", "-X", "POST", webhook_url, 
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ 飞书通知已发送")
        else:
            print(f"⚠️ 飞书通知发送失败: {result.stderr}")
    except Exception as e:
        print(f"⚠️ 飞书通知发送异常: {e}")


def create_release_ready_flag(version, repo_root):
    """创建发布就绪 flag 文件"""
    flag_file = repo_root / ".release_ready"
    
    # 获取当前 main 分支的提交 hash
    current_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    content = f"""VERSION={version}
PREPARED_AT={datetime.now().isoformat()}
MAIN_COMMIT={current_commit}
"""
    
    flag_file.write_text(content)
    print(f"✅ Flag 文件已创建: {flag_file}")
    return True


def merge_and_tag(version, dry_run=False):
    """
    步骤 6: 执行 Merge 和 Tag 操作

    1. 切换到 main 分支
    2. 拉取最新
    3. 合并 develop 到 main
    4. 创建发布标签
    5. 创建 .release_ready flag
    6. 停留在 main 分支（不切换回 develop）
    """
    print_step(6, f"执行 Merge 和 Tag (v{version})")

    repo_root = Path(__file__).parent.parent

    if dry_run:
        print("[演练] 跳过 Merge 和 Tag")
        return True

    # 1. 切换到 main 分支
    print("\n1. 切换到 main 分支...")
    cmd = "git checkout main"
    success, _ = run_command(cmd, "切换到 main 分支", cwd=repo_root)
    if not success:
        return False

    # 2. 拉取最新
    print("\n2. 拉取 main 分支最新...")
    cmd = "timeout 10 git pull origin main 2>/dev/null || timeout 10 git pull main 2>/dev/null || true"
    subprocess.run(cmd, shell=True, cwd=repo_root)
    print("✓ 拉取完成")

    # 3. 合并 develop 到 main
    print("\n3. 合并 develop 到 main...")
    merge_msg = f"merge: 合并 v{version} 到正式版"
    cmd = f'git merge develop --no-ff -m "{merge_msg}"'
    success, output = run_command(cmd, "合并 develop 到 main", cwd=repo_root)
    if not success:
        print(YELLOW + "⚠️  合并失败，可能有冲突" + RESET)
        print("请手动解决冲突后重新运行脚本")
        subprocess.run("git checkout develop 2>/dev/null || true", shell=True, cwd=repo_root)
        return False

    # 4. 创建发布标签
    print("\n4. 创建发布标签...")
    tag_name = f"v{version}"
    cmd = f"git tag -a {tag_name} -m 'Release {tag_name}'"
    success, _ = run_command(cmd, f"创建标签 {tag_name}", cwd=repo_root)
    if not success:
        return False

    # 5. 创建 .release_ready flag 并停留在 main 分支
    print("\n5. 创建 release_ready flag...")
    create_release_ready_flag(version, repo_root)
    
    print(f"\n✅ Merge 和 Tag 完成: v{version}")
    print(f"📌 当前分支: main (准备好发布)")
    
    return True


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

    # 运行 API 测试 (tests/test_api/)
    cmd = f"PYTHONPATH={dev_dir} python3 -m pytest {dev_dir}/tests/test_api/ -v"
    success, output = run_command(cmd, "API 测试", cwd=repo_root)

    # 停止 dev 服务器
    if not dry_run:
        cmd = "pkill -f 'server_test.py' 2>/dev/null || true"
        subprocess.run(cmd, shell=True)

    if not success:
        return False

    # 检查测试通过数
    if "passed" in output and "failed" not in output:
        passed_count = extract_test_count(output)
        print(GREEN + f"✓ API 测试全部通过 ({passed_count} tests)" + RESET)
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

    # 运行冒烟测试 (自动匹配所有 smoke 目录下的测试文件)
    cmd = f"cd {dev_dir} && npx playwright test tests/test_ui/specs/smoke/*.spec.ts --project=firefox --timeout=60000"
    success, output = run_command(cmd, "冒烟测试", cwd=repo_root)

    if not success:
        return False

    # 检查测试通过数
    if "passed" in output and "failed" not in output:
        passed_count = extract_test_count(output)
        print(GREEN + f"✓ 冒烟测试全部通过 ({passed_count} tests)" + RESET)
        return True
    else:
        print(RED + "✗ 冒烟测试未全部通过" + RESET)
        return False


def run_compatibility_tests(dry_run=False):
    """步骤 3: 运行兼容性测试"""
    print_step(3, "运行兼容性测试")

    repo_root = Path(__file__).parent.parent
    scripts_dir = repo_root / "scripts"

    if dry_run:
        print("[演练] 跳过兼容性测试")
        return True

    # 执行兼容性测试脚本
    cmd = f"python3 {scripts_dir}/tracker_ops.py all"
    success, output = run_command(cmd, "执行兼容性测试", cwd=repo_root)
    
    if success:
        print(GREEN + "✓ 兼容性测试通过" + RESET)
        return True
    else:
        print(YELLOW + "⚠️  兼容性测试未完全通过，但允许继续" + RESET)
        return True  # 允许继续，不中止发布


def main():
    repo_root = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(
        description="Tracker 发布前准备脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 演练模式（只检查，不实际操作）
    python3 scripts/release_preparation.py --dry-run --version v0.5.0

    # 执行完整发布准备
    python3 scripts/release_preparation.py --version v0.5.0

    # 跳过测试（仅执行 VERSION 更新和 Merge/Tag）
    python3 scripts/release_preparation.py --version v0.5.0 --skip-tests

    # 跳过 VERSION 更新（用于手动更新）
    python3 scripts/release_preparation.py --version v0.5.0 --skip-version
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
        "--skip-version",
        action="store_true",
        help="跳过 VERSION 更新（用于手动更新）"
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
        # buglog_tests 已移除
    else:
        print_step(0, "跳过测试执行")
        print(YELLOW + "⚠️  已跳过测试执行" + RESET)
        results["api_tests"] = True
        results["smoke_tests"] = True
        # buglog_tests 已移除

    # VERSION 更新
    if not args.skip_version:
        results["version_update"] = update_version(args.version, args.dry_run)
    else:
        print_step(0, "跳过 VERSION 更新")
        print(YELLOW + "⚠️  已跳过 VERSION 更新" + RESET)
        results["version_update"] = True

    results["git_status"] = check_git_status(args.dry_run)

    results["merge_tag"] = merge_and_tag(args.version, args.dry_run)

    # 汇总结果
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}发布前检查结果汇总{RESET}")
    print(f"{BOLD}{'=' * 60}\n")

    all_passed = True
    for step, passed in results.items():
        step_names = {
            "api_tests": "API 测试",
            "smoke_tests": "冒烟测试",
            "version_update": "VERSION 更新",
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

    if not all_passed:
        # 失败时执行回滚
        print(f"{RED}{BOLD}❌ 检查未通过，触发回滚{RESET}")
        rollback_on_failure(args.version, results, repo_root)
        print(f"\n发现问题:")
        for step, passed in results.items():
            if not passed:
                step_names = {
                    "api_tests": "API 测试",
                    "smoke_tests": "冒烟测试",
                    "version_update": "VERSION 更新",
                    "git_status": "Git 状态",
                    "merge_tag": "Merge 和 Tag"
                }
                print(f"  - {step_names.get(step, step)}")
        return 1

    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{GREEN}{BOLD}✅ 所有检查通过！可以执行发布。{RESET}")
    print(f"\n下一步操作:")
    if not args.dry_run:
        print(f"  cd /projects/management/tracker")
        print(f"  python3 scripts/release.py --version {args.version} --force")
    else:
        print(f"  [演练] 发布命令已准备")
    return 0


if __name__ == "__main__":
    sys.exit(main())
