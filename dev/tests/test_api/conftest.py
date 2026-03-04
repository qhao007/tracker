"""
API 测试配置 - 自动清理 session 文件 + 不稳定测试检测
"""
import os
import glob
import pytest


@pytest.fixture(autouse=True)
def cleanup_test_sessions():
    """每个测试前后清理 session 文件"""
    # 测试开始前清理
    session_dir = '/projects/management/tracker/dev/data/sessions'
    if os.path.exists(session_dir):
        for f in glob.glob(f'{session_dir}/*'):
            try:
                os.remove(f)
            except Exception:
                pass
    
    yield
    
    # 测试结束后清理
    if os.path.exists(session_dir):
        for f in glob.glob(f'{session_dir}/*'):
            try:
                os.remove(f)
            except Exception:
                pass


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """在测试报告中标记不稳定的测试为错误"""
    # 检查是否有 rerun
    rerun_info = terminalreporter.stats.get('rerun', [])
    if rerun_info:
        # 获取重试的测试名称
        seen_tests = set()
        for report in rerun_info:
            test_name = report.nodeid
            if test_name not in seen_tests:
                seen_tests.add(test_name)
        
        # 将不稳定测试添加到 failed 统计
        if seen_tests:
            terminalreporter.write_sep("=", "🔴 UNSTABLE TESTS - NEEDS FIX", red=True, bold=True)
            terminalreporter.write_line("")
            
            for test_name in sorted(seen_tests):
                terminalreporter.write_line(f"  ❌ {test_name}", red=True)
            
            terminalreporter.write_line("")
            terminalreporter.write_line("💡 These tests passed after retry but MUST BE FIXED!", red=True)
            terminalreporter.write_line("📝 Fix the root cause - do not rely on retries")
            terminalreporter.write_line("")
            
            # 强制设置退出码为失败
            terminalreporter._sessionexitstatus = 1
