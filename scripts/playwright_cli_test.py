#!/usr/bin/env python3
"""
Tracker Playwright CLI 测试脚本

使用 playwright-cli 命令行工具进行浏览器自动化测试

功能:
    1. smoke     - 快速冒烟测试
    2. screenshot - 截图测试
    3. workflow   - 端到端流程测试
    4. all       - 执行全部测试

使用方法:
    python3 scripts/playwright_cli_test.py smoke       # 快速冒烟测试
    python3 scripts/playwright_cli_test.py screenshot # 截图测试
    python3 scripts/playwright_cli_test.py workflow   # 端到端测试
    python3 scripts/playwright_cli_test.py all        # 执行全部
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# 颜色输出
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

REPO_ROOT = Path(__file__).parent.parent
TEST_RESULTS_DIR = REPO_ROOT / "test-results" / "playwright-cli"
OUTPUT_DIR = TEST_RESULTS_DIR
BASE_URL = "http://localhost:8081"


def print_step(msg):
    print(f"\n{GREEN}▶ {msg}{RESET}")


def print_ok(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_warn(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def ensure_output_dir():
    """确保输出目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_playwright_cli(args, description=None):
    """运行 playwright-cli 命令"""
    cmd = ["playwright-cli", "--browser=firefox"] + args
    if description:
        print_step(description)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT)
        )
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, "", "playwright-cli not found"
    except Exception as e:
        return False, "", str(e)


def cleanup_browser():
    """清理浏览器进程"""
    run_playwright_cli(["close"], "关闭浏览器")


def save_test_result(name, passed, details=""):
    """保存测试结果到 JSON 文件"""
    result_file = OUTPUT_DIR / f"{name}_result.json"
    result = {
        "test": name,
        "passed": passed,
        "timestamp": datetime.now().isoformat(),
        "details": details
    }
    result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result_file


def smoke_test():
    """快速冒烟测试"""
    print_step("快速冒烟测试")
    ensure_output_dir()

    tests = [
        ("打开页面", ["open", BASE_URL]),
        ("获取页面快照", ["snapshot"]),
        ("截图", ["screenshot"]),
    ]

    all_passed = True
    results = []

    for name, args in tests:
        passed, stdout, stderr = run_playwright_cli(args, name)
        results.append({"test": name, "passed": passed})
        if passed:
            print_ok(f"{name} 通过")
        else:
            print_error(f"{name} 失败: {stderr}")
            all_passed = False

    # 保存结果
    save_test_result("smoke", all_passed, json.dumps(results, indent=2))

    cleanup_browser()
    return all_passed


def screenshot_test():
    """截图测试"""
    print_step("截图测试")
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    tests = [
        ("首页截图", ["open", BASE_URL], f"screenshot_homepage_{timestamp}.png"),
        ("快照", ["snapshot"], None),
        ("TC面板截图", ["goto", f"{BASE_URL}#tc"], f"screenshot_tc_{timestamp}.png"),
    ]

    all_passed = True
    results = []

    for name, args, filename in tests:
        passed, stdout, stderr = run_playwright_cli(args, name)
        results.append({"test": name, "passed": passed})

        if passed:
            print_ok(f"{name} 通过")
            if filename:
                # 重命名最新的截图
                latest_png = max(OUTPUT_DIR.glob("page-*.png"), key=os.path.getmtime, default=None)
                if latest_png and latest_png.exists():
                    new_path = OUTPUT_DIR / filename
                    if new_path.exists():
                        new_path.unlink()
                    latest_png.rename(new_path)
                    print_ok(f"截图保存为: {filename}")
        else:
            print_error(f"{name} 失败: {stderr}")
            all_passed = False

    # 保存结果
    save_test_result("screenshot", all_passed, json.dumps(results, indent=2))

    cleanup_browser()
    return all_passed


def workflow_test():
    """端到端流程测试"""
    print_step("端到端流程测试")
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    steps = []

    # 1. 打开首页
    passed, stdout, stderr = run_playwright_cli(["open", BASE_URL], "打开 Tracker 首页")
    steps.append({"step": "打开首页", "passed": passed})
    if passed:
        print_ok("打开 Tracker 首页成功")
    else:
        print_error(f"打开首页失败: {stderr}")
        cleanup_browser()
        save_test_result("workflow", False, json.dumps(steps, indent=2))
        return False

    # 2. 获取页面快照
    passed, stdout, stderr = run_playwright_cli(["snapshot"], "获取页面快照")
    steps.append({"step": "获取页面快照", "passed": passed})
    if passed:
        print_ok("页面快照成功")
    else:
        print_warn(f"快照: {stderr}")

    # 3. 截图 - 首页
    passed, stdout, stderr = run_playwright_cli(["screenshot"], "首页截图")
    steps.append({"step": "首页截图", "passed": passed})
    if passed:
        print_ok("首页截图成功")
        # 重命名截图
        latest_png = max(OUTPUT_DIR.glob("page-*.png"), key=os.path.getmtime, default=None)
        if latest_png and latest_png.exists():
            latest_png.rename(OUTPUT_DIR / f"workflow_homepage_{timestamp}.png")

    # 4. 查看控制台日志
    passed, stdout, stderr = run_playwright_cli(["console"], "查看控制台")
    steps.append({"step": "查看控制台", "passed": passed})
    if passed:
        print_ok("控制台日志获取成功")
    else:
        print_warn(f"控制台: {stderr}")

    # 5. 截图 - 完整页面
    passed, stdout, stderr = run_playwright_cli(["screenshot"], "完整页面截图")
    steps.append({"step": "完整页面截图", "passed": passed})
    if passed:
        print_ok("完整页面截图成功")
        latest_png = max(OUTPUT_DIR.glob("page-*.png"), key=os.path.getmtime, default=None)
        if latest_png and latest_png.exists():
            latest_png.rename(OUTPUT_DIR / f"workflow_fullpage_{timestamp}.png")

    # 关闭浏览器
    cleanup_browser()

    # 保存结果
    all_passed = all(s["passed"] for s in steps)
    save_test_result("workflow", all_passed, json.dumps(steps, indent=2))

    return all_passed


def all_tests():
    """执行全部测试"""
    print("=" * 60)
    print("Tracker Playwright CLI 测试")
    print("=" * 60)

    results = {}

    ensure_output_dir()

    # 1. 冒烟测试
    print_step("1. 冒烟测试")
    results['smoke'] = smoke_test()

    # 2. 截图测试
    print_step("2. 截图测试")
    results['screenshot'] = screenshot_test()

    # 3. 流程测试
    print_step("3. 端到端流程测试")
    results['workflow'] = workflow_test()

    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = f"{GREEN}✓ 通过{RESET}" if passed else f"{YELLOW}⚠️ 失败{RESET}"
        print(f"{name.upper():12} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    # 保存汇总结果
    summary_file = OUTPUT_DIR / "test_summary.json"
    summary = {
        "timestamp": datetime.now().isoformat(),
        "all_passed": all_passed,
        "results": results
    }
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    if all_passed:
        print_ok("全部测试通过!")
        print(f"\n结果保存在: {OUTPUT_DIR}")
        return 0
    else:
        print_warn("部分测试失败")
        return 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1].lower()

    if command == 'smoke':
        return 0 if smoke_test() else 1
    elif command == 'screenshot':
        return 0 if screenshot_test() else 1
    elif command == 'workflow':
        return 0 if workflow_test() else 1
    elif command == 'all':
        return all_tests()
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        return 1


if __name__ == '__main__':
    sys.exit(main())
