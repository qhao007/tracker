"""
项目状态报告导出 API 测试 - v0.14.3

测试项目状态报告 Markdown 导出 API 的功能：
- 正常导出验证
- 报告内容完整性
- 权限控制
- 边界条件
- 数据一致性

运行命令:
    cd dev && PYTHONPATH=. pytest tests/test_api/test_api_report_export.py -v
"""

import json
import pytest
import sys
import os
import time
import re

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_client(client):
    """创建已登录的管理员客户端"""
    client.post('/api/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json')
    return client


@pytest.fixture(scope='module')
def empty_project():
    """创建空的测试项目（无 TC/CP）"""
    app = create_app(testing=True)
    with app.test_client() as client:
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"Empty_Report_Test_{int(time.time())}"

        response = client.post('/api/projects',
                              data=json.dumps({'name': name, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
                              content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            project_id = data['project']['id']
            yield {'id': project_id, 'name': name}

            client.delete(f"/api/projects/{project_id}")
        else:
            pytest.skip("无法创建空项目")


class TestReportExportBasic:
    """测试报告导出基本功能"""

    def test_export_report_success(self, admin_client):
        """API-REPORT-001: 正常导出 Markdown"""
        response = admin_client.get('/api/export/project/3/report')

        assert response.status_code == 200
        # mimetype 可能包含重复的 charset，使用 in 检查
        assert 'text/markdown' in response.content_type
        content = response.data.decode('utf-8')
        assert content.startswith('#')
        assert 'SOC_DV' in content

    def test_export_report_sections(self, admin_client):
        """API-REPORT-002: 报告 8 个章节齐全"""
        response = admin_client.get('/api/export/project/3/report')

        assert response.status_code == 200
        content = response.data.decode('utf-8')

        # 验证关键章节存在 (v0.14.3: 执行摘要拆分为 CP 概览 + TC 概览)
        assert 'CP 概览' in content, "缺少 CP 概览章节"
        assert 'TC 概览' in content, "缺少 TC 概览章节"
        assert 'CP 覆盖状态' in content, "缺少 CP 覆盖状态章节"
        assert 'TC 执行状态' in content, "缺少 TC 执行状态章节"
        assert 'Feature 覆盖矩阵' in content, "缺少 Feature 覆盖矩阵章节"
        assert 'Owner 工作分布' in content, "缺少 Owner 工作分布章节"
        assert '风险与待办' in content, "缺少风险与待办章节"
        assert '附录' in content, "缺少附录章节"

    def test_export_report_unauthenticated(self, client):
        """API-REPORT-003: 未登录访问"""
        response = client.get('/api/export/project/3/report')

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_export_report_nonexistent_project(self, admin_client):
        """API-REPORT-004: 项目不存在"""
        response = admin_client.get('/api/export/project/99999/report')

        assert response.status_code == 404
        data = response.get_json()
        assert data.get('code') == 'PROJECT_NOT_FOUND'

    def test_export_report_filename(self, admin_client):
        """API-REPORT-005: 文件名正确"""
        response = admin_client.get('/api/export/project/3/report')

        assert response.status_code == 200

        content_disp = response.headers.get('Content-Disposition', '')
        assert 'SOC_DV' in content_disp or 'attachment' in content_disp
        assert '.md' in content_disp


class TestReportExportDataConsistency:
    """测试报告数据一致性"""

    def test_export_report_data_matches_dashboard(self, admin_client):
        """API-REPORT-006: 数据一致性 - 报告 overview 数值与 dashboard 一致"""
        # 获取报告内容
        report_response = admin_client.get('/api/export/project/3/report')
        assert report_response.status_code == 200
        report_content = report_response.data.decode('utf-8')

        # 获取 dashboard 数据
        dashboard_response = admin_client.get('/api/dashboard/stats?project_id=3')
        assert dashboard_response.status_code == 200
        dashboard_data = json.loads(dashboard_response.data)['data']['overview']

        # 验证关键指标一致
        total_cp = dashboard_data['total_cp']
        covered_cp = dashboard_data['covered_cp']
        coverage_rate = dashboard_data['coverage_rate']
        tc_total = dashboard_data['tc_total']
        tc_pass = dashboard_data['tc_pass']
        tc_pass_rate = dashboard_data['tc_pass_rate']

        assert f"CP 总数 | {total_cp}" in report_content, \
            f"CP 总数不一致: dashboard={total_cp}"
        assert f"已覆盖 CP | {covered_cp}" in report_content, \
            f"已覆盖 CP 不一致: dashboard={covered_cp}"
        assert f"覆盖率 | {coverage_rate}%" in report_content, \
            f"覆盖率不一致: dashboard={coverage_rate}"
        assert f"TC 总数 | {tc_total}" in report_content, \
            f"TC 总数不一致: dashboard={tc_total}"
        assert f"TC PASS | {tc_pass}" in report_content, \
            f"TC PASS 不一致: dashboard={tc_pass}"
        assert f"TC 通过率 | {tc_pass_rate}%" in report_content, \
            f"TC 通过率不一致: dashboard={tc_pass_rate}"


class TestReportExportBoundary:
    """测试报告导出边界条件"""

    def test_export_empty_project(self, admin_client, empty_project):
        """API-REPORT-007: 空项目导出"""
        response = admin_client.get(f'/api/export/project/{empty_project["id"]}/report')

        assert response.status_code == 200
        content = response.data.decode('utf-8')

        # 验证包含 0 值，不报错
        assert 'CP 总数 | 0' in content, "空项目 CP 总数应为 0"
        assert 'TC 总数 | 0' in content, "空项目 TC 总数应为 0"
        assert '覆盖率 | 0%' in content, "空项目覆盖率应为 0%"
        # 验证所有章节仍然存在
        assert 'CP 概览' in content
        assert 'TC 概览' in content
        assert 'CP 覆盖状态' in content
        assert 'TC 执行状态' in content
        assert 'Feature 覆盖矩阵' in content
        assert 'Owner 工作分布' in content
        assert '风险与待办' in content
        assert '附录' in content
