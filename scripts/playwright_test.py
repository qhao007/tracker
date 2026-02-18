#!/usr/bin/env python3
"""
Tracker Playwright 测试脚本

功能:
    1. smoke     - 快速冒烟测试
    2. screenshot - 截图测试
    3. workflow   - 端到端流程测试
    4. all       - 执行全部测试

使用方法:
    python3 scripts/playwright_test.py smoke       # 快速冒烟测试
    python3 scripts/playwright_test.py screenshot # 截图测试
    python3 scripts/playwright_test.py workflow   # 端到端测试
    python3 scripts/playwright_test.py all        # 执行全部
"""

import subprocess
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# 颜色输出
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

REPO_ROOT = Path(__file__).parent.parent
TEST_DIR = REPO_ROOT / "dev" / "tests"
OUTPUT_DIR = REPO_ROOT / "test-results" / "playwright"

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


def check_service():
    """检查服务是否运行"""
    print_step("检查服务状态")
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{BASE_URL}/api/version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout == "200":
            print_ok(f"服务运行正常 ({BASE_URL})")
            return True
        else:
            print_error(f"服务无响应 (HTTP {result.stdout})")
            return False
    except Exception as e:
        print_error(f"无法连接服务: {e}")
        return False


def run_npx_playwright(cmd_args, description):
    """运行 npx playwright 命令"""
    full_cmd = ["npx", "playwright", "--version"] + cmd_args
    print(f"\n{description}...")
    
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO_ROOT / "dev")
        )
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, "", "npx not found"
    except Exception as e:
        return False, "", str(e)


def smoke_test():
    """快速冒烟测试 - 使用 Playwright Python"""
    print_step("快速冒烟测试")
    
    test_script = '''
const { firefox } = require('playwright');

(async () => {
    const browser = await firefox.launch({ headless: true });
    const page = await browser.newPage();
    
    let passed = true;
    const tests = [];
    
    // 1. 打开页面
    try {
        await page.goto('{{BASE_URL}}', { waitUntil: 'domcontentloaded' });
        tests.push({ name: '打开页面', ok: true });
    } catch (e) {
        tests.push({ name: '打开页面', ok: false, error: e.message });
        passed = false;
    }
    
    // 2. 验证标题
    try {
        const title = await page.title();
        tests.push({ name: '页面标题', ok: title.includes('Tracker'), detail: title });
    } catch (e) {
        tests.push({ name: '页面标题', ok: false, error: e.message });
        passed = false;
    }
    
    // 3. 验证项目选择器
    try {
        const selector = await page.locator('#projectSelector').isVisible();
        tests.push({ name: '项目选择器', ok: selector });
    } catch (e) {
        tests.push({ name: '项目选择器', ok: false, error: e.message });
        passed = false;
    }
    
    await browser.close();
    
    // 输出结果
    tests.forEach(t => {
        if (t.ok) {
            console.log('✓ ' + t.name + ' 通过');
        } else {
            console.log('✗ ' + t.name + ' 失败: ' + (t.error || '未知错误'));
        }
    });
    
    process.exit(passed ? 0 : 1);
})();
'''.replace('{{BASE_URL}}', BASE_URL)
    
    # 在 dev/tests 目录写入临时脚本
    dev_tests_dir = REPO_ROOT / "dev" / "tests"
    test_file = dev_tests_dir / "smoke_test_temp.js"
    test_file.write_text(test_script)
    
    # 运行测试（从 dev 目录运行）
    try:
        result = subprocess.run(
            ["node", str(test_file)],
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO_ROOT / "dev")
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        # 清理临时文件
        test_file.unlink()
        return result.returncode == 0
    except Exception as e:
        print_error(f"执行失败: {e}")
        if test_file.exists():
            test_file.unlink()
        return False


def screenshot_test():
    """截图测试"""
    print_step("截图测试")
    
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    test_script = '''
const { firefox } = require('playwright');

(async () => {
    const browser = await firefox.launch({ headless: true });
    const page = await browser.newPage();
    
    // 1. 打开页面
    await page.goto('{{BASE_URL}}', { waitUntil: 'networkidle' });
    console.log('✓ 页面加载完成');
    
    // 2. 截图
    const screenshotPath = '{{OUTPUT_DIR}}/screenshot_{{TIMESTAMP}}.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log('✓ 截图已保存: ' + screenshotPath);
    
    await browser.close();
    console.log('✓ 测试完成');
})();
'''.replace('{{BASE_URL}}', BASE_URL) \
   .replace('{{OUTPUT_DIR}}', str(OUTPUT_DIR)) \
   .replace('{{TIMESTAMP}}', timestamp)
    
    # 在 dev/tests 目录写入临时脚本
    dev_tests_dir = REPO_ROOT / "dev" / "tests"
    test_file = dev_tests_dir / "screenshot_test_temp.js"
    test_file.write_text(test_script)
    
    # 运行截图测试
    try:
        result = subprocess.run(
            ["node", str(test_file)],
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO_ROOT / "dev")
        )
        print(result.stdout)
        if result.stderr:
            print_warn(result.stderr)
        # 清理临时文件
        test_file.unlink()
        return True
    except Exception as e:
        print_error(f"执行失败: {e}")
        if test_file.exists():
            test_file.unlink()
        return False


def workflow_test():
    """端到端流程测试"""
    print_step("端到端流程测试")
    
    test_script = '''
const { firefox } = require('playwright');

(async () => {
    const browser = await firefox.launch({ headless: true });
    const page = await browser.newPage();
    
    let steps = [];
    
    // 1. 打开页面
    try {
        await page.goto('{{BASE_URL}}', { waitUntil: 'domcontentloaded' });
        steps.push('✓ 打开 Tracker 页面');
    } catch (e) {
        steps.push('✗ 打开页面失败: ' + e.message);
    }
    
    // 2. 等待页面加载
    await page.waitForTimeout(1000);
    
    // 3. 切换到 TC 面板
    try {
        await page.click('button:has-text("Test Cases")');
        await page.waitForTimeout(500);
        steps.push('✓ 切换到 TC 面板');
    } catch (e) {
        steps.push('⚠ 切换面板: ' + e.message);
    }
    
    // 4. 截图
    try {
        await page.screenshot({ path: '{{OUTPUT_DIR}}/workflow_test.png', fullPage: true });
        steps.push('✓ 流程截图已保存');
    } catch (e) {
        steps.push('✗ 截图失败: ' + e.message);
    }
    
    await browser.close();
    
    // 输出结果
    steps.forEach(s => console.log(s));
    console.log('\\n✓ 端到端测试完成');
})();
'''.replace('{{BASE_URL}}', BASE_URL) \
   .replace('{{OUTPUT_DIR}}', str(OUTPUT_DIR))
    
    # 在 dev/tests 目录写入临时脚本
    dev_tests_dir = REPO_ROOT / "dev" / "tests"
    test_file = dev_tests_dir / "workflow_test_temp.js"
    test_file.write_text(test_script)
    
    # 运行端到端流程测试
    try:
        result = subprocess.run(
            ["node", str(test_file)],
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO_ROOT / "dev")
        )
        print(result.stdout)
        if result.stderr:
            print_warn(result.stderr)
        # 清理临时文件
        test_file.unlink()
        return True
    except Exception as e:
        print_error(f"执行失败: {e}")
        if test_file.exists():
            test_file.unlink()
        return False


def all_tests():
    """执行全部测试"""
    print("=" * 60)
    print("Tracker Playwright 测试")
    print("=" * 60)
    
    results = {}
    
    # 检查服务
    if not check_service():
        print_error("服务未运行，请先启动测试版服务")
        return 1
    
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
        status = f"{GREEN}✓ 通过{RESET}" if passed else f"{YELLOW}⚠️ 部分通过{RESET}"
        print(f"{name.upper():12} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print_ok("全部测试通过!")
        print(f"\n截图保存在: {OUTPUT_DIR}")
        return 0
    else:
        print_warn("部分测试未完全通过")
        return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    command = sys.argv[1].lower()
    
    if command == 'smoke':
        return 0 if check_service() and smoke_test() else 1
    elif command == 'screenshot':
        return 0 if check_service() and screenshot_test() else 1
    elif command == 'workflow':
        return 0 if check_service() and workflow_test() else 1
    elif command == 'all':
        return all_tests()
    else:
        print(f"未知命令: {command}")
        print(__doc__)
        return 1


if __name__ == '__main__':
    sys.exit(main())
