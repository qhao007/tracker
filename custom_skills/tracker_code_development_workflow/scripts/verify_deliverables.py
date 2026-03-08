#!/usr/bin/env python3
"""
Tracker 代码开发工作流 - 交付物验证脚本

检查各阶段交付物是否完整：
- API测试文件
- UI测试文件
- 测试报告
- Bug记录
"""

import os
import sys
import json
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path("/projects/management/tracker")
DEV_DIR = PROJECT_ROOT / "dev"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORTS_DIR = DOCS_DIR / "REPORTS"
BUGLOG_DIR = DOCS_DIR / "BUGLOG"


def check_api_tests(version):
    """检查API测试文件"""
    print(f"\n{'='*60}")
    print(f"检查 API 测试文件 (v{version})")
    print(f"{'='*60}")

    test_dir = DEV_DIR / "tests" / "test_api"
    if not test_dir.exists():
        print(f"❌ API测试目录不存在: {test_dir}")
        return False

    test_files = list(test_dir.glob("test_api_*.py"))
    print(f"✅ 找到 {len(test_files)} 个API测试文件:")

    for f in sorted(test_files):
        print(f"   - {f.name}")

    return len(test_files) > 0


def check_ui_tests(version):
    """检查UI测试文件"""
    print(f"\n{'='*60}")
    print(f"检查 UI 测试文件 (v{version})")
    print(f"{'='*60}")

    test_dir = DEV_DIR / "tests" / "test_ui" / "specs" / "integration"
    if not test_dir.exists():
        print(f"❌ UI测试目录不存在: {test_dir}")
        return False

    test_files = list(test_dir.glob("*.spec.ts"))
    print(f"✅ 找到 {len(test_files)} 个UI测试文件:")

    for f in sorted(test_files):
        print(f"   - {f.name}")

    return len(test_files) > 0


def check_test_report(version):
    """检查测试报告"""
    print(f"\n{'='*60}")
    print(f"检查测试报告 (v{version})")
    print(f"{'='*60}")

    if not REPORTS_DIR.exists():
        print(f"❌ 报告目录不存在: {REPORTS_DIR}")
        return False

    # 查找版本相关的报告
    report_files = list(REPORTS_DIR.glob(f"TEST_REPORT_v{version}_*.md"))

    if not report_files:
        print(f"❌ 未找到 v{version} 的测试报告")
        return False

    print(f"✅ 找到 {len(report_files)} 个测试报告:")
    for f in sorted(report_files):
        print(f"   - {f.name}")

    return True


def check_buglog():
    """检查Bug记录"""
    print(f"\n{'='*60}")
    print(f"检查 Bug 记录")
    print(f"{'='*60}")

    buglog_file = BUGLOG_DIR / "tracker_BUG_RECORD.md"
    if not buglog_file.exists():
        print(f"❌ Bug记录文件不存在: {buglog_file}")
        return False

    # 统计Bug数量
    with open(buglog_file, 'r') as f:
        content = f.read()
        bug_count = content.count("### BUG-")

    print(f"✅ Bug记录文件存在，包含 {bug_count} 个Bug记录")
    return True


def run_pytest_tests():
    """运行API测试"""
    print(f"\n{'='*60}")
    print(f"运行 API 测试")
    print(f"{'='*60}")

    os.chdir(DEV_DIR)
    result = os.system("PYTHONPATH=. pytest tests/test_api/ -v --tb=short 2>&1 | head -50")

    return result == 0


def run_playwright_tests():
    """运行Playwright测试"""
    print(f"\n{'='*60}")
    print(f"运行 UI 测试")
    print(f"{'='*60}")

    os.chdir(DEV_DIR)
    result = os.system("npx playwright test tests/test_ui/specs/integration/ --project=firefox 2>&1 | head -50")

    return result == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="验证Tracker开发工作流交付物")
    parser.add_argument("--version", "-v", required=True, help="版本号，如 0.9.1")
    parser.add_argument("--api", action="store_true", help="运行API测试")
    parser.add_argument("--ui", action="store_true", help="运行UI测试")
    parser.add_argument("--all", action="store_true", help="检查所有交付物")

    args = parser.parse_args()

    print(f"\n🔍 Tracker v{args.version} 开发交付物验证")
    print(f"项目根目录: {PROJECT_ROOT}")

    results = {}

    # 基础交付物检查
    results["api_tests"] = check_api_tests(args.version)
    results["ui_tests"] = check_ui_tests(args.version)
    results["test_report"] = check_test_report(args.version)
    results["buglog"] = check_buglog()

    # 可选测试执行
    if args.api:
        results["api_run"] = run_pytest_tests()

    if args.ui:
        results["ui_run"] = run_playwright_tests()

    # 总结
    print(f"\n{'='*60}")
    print(f"验证总结")
    print(f"{'='*60}")

    for key, value in results.items():
        status = "✅ 通过" if value else "❌ 失败"
        print(f"{key}: {status}")

    all_passed = all(results.values())
    print(f"\n{'='*60}")
    if all_passed:
        print(f"🎉 所有检查通过!")
    else:
        print(f"⚠️ 部分检查失败，请查看上述详情")
    print(f"{'='*60}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
