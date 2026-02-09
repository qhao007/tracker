#!/usr/bin/env python3
"""
Tracker 冒烟测试 - 无浏览器版

目的：验证开发版服务是否正常运行
无需 Playwright 浏览器，纯 HTTP API 测试

运行命令:
    python3 scripts/smoke_test.py
"""

import sys
import json
import time

BASE_URL = 'http://localhost:8081'

def test_api(endpoint, method='GET', data=None):
    """测试 API 接口"""
    import urllib.request
    import urllib.error

    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}

    try:
        if method == 'GET':
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode()
                # 尝试解析 JSON，如果失败则只返回状态
                try:
                    return True, json.loads(content)
                except:
                    return True, {'status_code': resp.status, 'content_type': resp.headers.get('Content-Type', '')}
        elif method == 'POST':
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as resp:
                return True, json.loads(resp.read().decode())
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Tracker v0.6.0 冒烟测试")
    print("=" * 60)
    print()

    tests = [
        ("HTTP 服务响应", lambda: test_api('/')),
        ("API 版本信息", lambda: test_api('/api/version')),
        ("项目列表", lambda: test_api('/api/projects')),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        success, result = test_func()
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"[{status}] {name}")

        if not success:
            print(f"       错误: {result}")
            failed += 1
        elif isinstance(result, dict) and 'version' in result:
            print(f"       版本: {result.get('version')} ({result.get('version_type')})")
            passed += 1
        elif isinstance(result, list):
            print(f"       项目数: {len(result)}")
            passed += 1
        else:
            passed += 1

        # 短暂延迟，避免请求过快
        time.sleep(0.1)

    # 如果有项目，测试项目详情
    print()
    print("-" * 60)
    print("项目数据测试:")

    success, projects = test_api('/api/projects')
    if success and projects:
        # 使用第一个项目测试
        project = projects[0]
        project_id = project['id']
        project_name = project['name']
        print(f"  使用项目: {project_name} (ID={project_id})")

        tests_project = [
            ("CP 列表", lambda: test_api(f'/api/cp?project_id={project_id}')),
            ("TC 列表", lambda: test_api(f'/api/tc?project_id={project_id}')),
            ("统计数据", lambda: test_api(f'/api/stats?project_id={project_id}')),
        ]

        for name, test_func in tests_project:
            success, result = test_func()
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  [{status}] {name}")

            if not success:
                print(f"         错误: {result}")
                failed += 1
            else:
                passed += 1

            time.sleep(0.1)

    print()
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
