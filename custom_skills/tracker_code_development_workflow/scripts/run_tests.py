#!/usr/bin/env python3
"""
Tracker 代码开发工作流 - 统一测试执行脚本

提供统一的测试入口，支持：
- 前端检查
- API测试
- UI冒烟测试
- UI集成测试
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"执行: {cmd}\n")

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd="/projects/management/tracker/dev"
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tracker统一测试入口")
    parser.add_argument("--frontend", "-f", action="store_true", help="运行前端检查")
    parser.add_argument("--api", "-a", action="store_true", help="运行API测试")
    parser.add_argument("--smoke", "-s", action="store_true", help="运行UI冒烟测试")
    parser.add_argument("--integration", "-i", action="store_true", help="运行UI集成测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")

    args = parser.parse_args()

    if not any([args.frontend, args.api, args.smoke, args.integration, args.all]):
        parser.print_help()
        print("\n请至少选择一个测试类型，或使用 --all 运行所有测试")
        return 1

    os.chdir("/projects/management/tracker/dev")

    results = {}

    if args.frontend or args.all:
        results["frontend"] = run_command(
            "bash check_frontent.sh",
            "前端检查 (check_frontent.sh)"
        )

    if args.api or args.all:
        results["api"] = run_command(
            "PYTHONPATH=. pytest tests/test_api/ -v",
            "API测试 (pytest)"
        )

    if args.smoke or args.all:
        results["smoke"] = run_command(
            "npx playwright test tests/test_ui/specs/smoke/ --project=firefox",
            "UI冒烟测试 (Playwright)"
        )

    if args.integration or args.all:
        results["integration"] = run_command(
            "npx playwright test tests/test_ui/specs/integration/ --project=firefox",
            "UI集成测试 (Playwright)"
        )

    # 总结
    print(f"\n{'='*60}")
    print(f"测试总结")
    print(f"{'='*60}")

    for key, value in results.items():
        status = "✅ 通过" if value else "❌ 失败"
        print(f"{key}: {status}")

    all_passed = all(results.values())
    print(f"\n{'='*60}")
    if all_passed:
        print(f"🎉 所有测试通过!")
    else:
        print(f"⚠️ 部分测试失败")
    print(f"{'='*60}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
