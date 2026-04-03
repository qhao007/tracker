#!/usr/bin/env python3
"""
Tracker API 测试用例 - Project fc_count 字段测试
v0.11.0 版本补充功能测试
"""

import json
import pytest
import sys
import os
import time

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


@pytest.fixture
def tc_cp_project(admin_client):
    """创建 TC-CP 模式的测试项目"""
    name = f"TC_CP_FCCount_Test_{int(time.time())}"

    response = admin_client.post('/api/projects',
        data=json.dumps({
            'name': name,
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'coverage_mode': 'tc_cp'
        }),
        content_type='application/json')

    if response.status_code == 200:
        data = json.loads(response.data)
        project_id = data['project']['id']
        yield {'id': project_id, 'name': name}

        # 清理
        admin_client.delete(f"/api/projects/{project_id}")
    else:
        pytest.skip("无法创建测试项目")


@pytest.fixture
def fc_cp_project(admin_client):
    """创建 FC-CP 模式的测试项目"""
    name = f"FC_CP_FCCount_Test_{int(time.time())}"

    response = admin_client.post('/api/projects',
        data=json.dumps({
            'name': name,
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'coverage_mode': 'fc_cp'
        }),
        content_type='application/json')

    if response.status_code == 200:
        data = json.loads(response.data)
        project_id = data['project']['id']
        yield {'id': project_id, 'name': name}

        # 清理
        admin_client.delete(f"/api/projects/{project_id}")
    else:
        pytest.skip("无法创建测试项目")


# ============ Project fc_count 测试 ============

class TestProjectFcCount:
    """Project fc_count 字段测试"""

    def test_tc_cp_mode_fc_count_zero(self, admin_client, tc_cp_project):
        """API-PROJ-FCCOUNT-001: TC-CP模式返回fc_count=0"""
        # 创建 TC-CP 模式项目后，添加一些 TC 数据（不是 FC）
        # TC-CP 模式项目不会有 FC 数据

        response = admin_client.get('/api/projects')
        projects = json.loads(response.data)

        target_project = next((p for p in projects if p['id'] == tc_cp_project['id']), None)
        assert target_project is not None, "项目应该存在"

        assert target_project.get('coverage_mode') == 'tc_cp'
        assert 'fc_count' in target_project, "项目应该包含 fc_count 字段"
        assert target_project.get('fc_count') == 0, "TC-CP 模式 fc_count 应该为 0"

    def test_fc_cp_mode_fc_count_actual(self, admin_client, fc_cp_project):
        """API-PROJ-FCCOUNT-002: FC-CP模式返回fc_count实际数量"""
        # 导入一些 FC 数据
        csv_data = [
            ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
            ["CG_FCount_1", "CP_FCount_1", "cover", "bin_1", "1", "50.0", "ready", "Test FC 1"],
            ["CG_FCount_2", "CP_FCount_2", "cover", "bin_2", "2", "60.0", "ready", "Test FC 2"],
            ["CG_FCount_3", "CP_FCount_3", "cover", "bin_3", "3", "70.0", "missing", "Test FC 3"]
        ]

        import_response = admin_client.post(f'/api/fc/import?project_id={fc_cp_project["id"]}',
            data=json.dumps({'csv_data': csv_data}),
            content_type='application/json')

        assert import_response.status_code == 200, f"导入 FC 失败: {import_response.data}"

        # 验证 fc_count
        response = admin_client.get('/api/projects')
        projects = json.loads(response.data)

        target_project = next((p for p in projects if p['id'] == fc_cp_project['id']), None)
        assert target_project is not None, "项目应该存在"

        assert target_project.get('coverage_mode') == 'fc_cp'
        assert 'fc_count' in target_project, "项目应该包含 fc_count 字段"
        assert target_project.get('fc_count') == 3, f"FC-CP 模式应该有 3 个 FC，实际 {target_project.get('fc_count')}"

    def test_projects_list_includes_fc_count(self, admin_client, fc_cp_project):
        """API-PROJ-FCCOUNT-003: 返回值包含coverage_mode和fc_count"""
        response = admin_client.get('/api/projects')
        projects = json.loads(response.data)

        assert response.status_code == 200, f"获取项目列表失败: {response.data}"

        target_project = next((p for p in projects if p['id'] == fc_cp_project['id']), None)
        assert target_project is not None, "项目应该存在"

        # 验证包含所有必要字段
        assert 'coverage_mode' in target_project, "项目应该包含 coverage_mode 字段"
        assert 'fc_count' in target_project, "项目应该包含 fc_count 字段"
        assert 'cp_count' in target_project, "项目应该包含 cp_count 字段"
        assert 'tc_count' in target_project, "项目应该包含 tc_count 字段"

        # 验证 coverage_mode 值为 fc_cp
        assert target_project['coverage_mode'] == 'fc_cp'
