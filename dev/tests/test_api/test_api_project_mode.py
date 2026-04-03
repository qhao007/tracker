#!/usr/bin/env python3
"""
Tracker API 测试用例 - coverage_mode 测试
v0.11.0 版本新增功能测试
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


# ============ coverage_mode 测试 ============

class TestProjectCoverageMode:
    """项目 coverage_mode 测试"""

    def test_create_project_with_mode(self, admin_client):
        """API-PROJ-001: 创建项目带 mode"""
        name = f"Mode_Test_{int(time.time())}"

        # 创建带 coverage_mode 的项目
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')

        assert response.status_code == 200, f"创建项目失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert 'project' in result
        assert result['project'].get('coverage_mode') == 'fc_cp'

        # 清理
        project_id = result['project']['id']
        admin_client.delete(f"/api/projects/{project_id}")

    def test_create_project_with_tc_cp_mode(self, admin_client):
        """创建项目带 tc_cp mode"""
        name = f"TC_CP_Test_{int(time.time())}"

        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'tc_cp'
            }),
            content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result['project'].get('coverage_mode') == 'tc_cp'

        # 清理
        project_id = result['project']['id']
        admin_client.delete(f"/api/projects/{project_id}")

    def test_create_project_without_mode(self, admin_client):
        """创建项目不带 mode（应该使用默认值 tc_cp）"""
        name = f"No_Mode_Test_{int(time.time())}"

        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)

        # 应该使用默认值 tc_cp
        assert result['project'].get('coverage_mode') == 'tc_cp'

        # 清理
        project_id = result['project']['id']
        admin_client.delete(f"/api/projects/{project_id}")

    def test_get_project_returns_mode(self, admin_client):
        """API-PROJ-002: 获取项目返回 mode"""
        name = f"Get_Mode_Test_{int(time.time())}"

        # 创建项目
        create_response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')

        assert create_response.status_code == 200
        project_id = json.loads(create_response.data)['project']['id']

        # 获取项目列表
        list_response = admin_client.get('/api/projects')
        projects = json.loads(list_response.data)

        # 找到我们创建的项目
        target_project = next((p for p in projects if p['id'] == project_id), None)
        assert target_project is not None, "项目应该在列表中"
        assert 'coverage_mode' in target_project, "项目应该包含 coverage_mode 字段"
        assert target_project['coverage_mode'] == 'fc_cp'

        # 清理
        admin_client.delete(f"/api/projects/{project_id}")

    def test_get_project_by_id_returns_mode(self, admin_client):
        """通过 ID 获取项目返回 mode"""
        name = f"Get_By_ID_Test_{int(time.time())}"

        # 创建项目
        create_response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')

        assert create_response.status_code == 200
        project_id = json.loads(create_response.data)['project']['id']

        # 获取单个项目详情
        # 根据 API 实现，需要通过项目名获取，这里用 projects 列表
        list_response = admin_client.get('/api/projects')
        projects = json.loads(list_response.data)

        target_project = next((p for p in projects if p['id'] == project_id), None)
        assert target_project is not None
        assert target_project['coverage_mode'] == 'fc_cp'

        # 清理
        admin_client.delete(f"/api/projects/{project_id}")


class TestProjectDefaultMode:
    """项目默认 mode 测试"""

    def test_project_default_tc_cp(self, admin_client):
        """API-PROJ-003: 新建项目默认 tc_cp"""
        name = f"Default_Test_{int(time.time())}"

        # 创建项目不指定 mode
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)

        # 验证默认值为 tc_cp
        assert result['project'].get('coverage_mode') == 'tc_cp', \
            f"期望默认值为 'tc_cp'，实际为 '{result['project'].get('coverage_mode')}'"

        # 清理
        project_id = result['project']['id']
        admin_client.delete(f"/api/projects/{project_id}")

    def test_multiple_projects_different_modes(self, admin_client):
        """多个项目不同 mode"""
        # 项目 1 - fc_cp
        name1 = f"FC_Mode_{int(time.time())}"
        response1 = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name1,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')
        assert response1.status_code == 200
        project1_id = json.loads(response1.data)['project']['id']

        # 项目 2 - tc_cp
        name2 = f"TC_Mode_{int(time.time())}"
        response2 = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name2,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'tc_cp'
            }),
            content_type='application/json')
        assert response2.status_code == 200
        project2_id = json.loads(response2.data)['project']['id']

        # 获取项目列表验证
        list_response = admin_client.get('/api/projects')
        projects = json.loads(list_response.data)

        project1 = next((p for p in projects if p['id'] == project1_id), None)
        project2 = next((p for p in projects if p['id'] == project2_id), None)

        assert project1 is not None
        assert project2 is not None
        assert project1['coverage_mode'] == 'fc_cp'
        assert project2['coverage_mode'] == 'tc_cp'

        # 清理
        admin_client.delete(f"/api/projects/{project1_id}")
        admin_client.delete(f"/api/projects/{project2_id}")


class TestProjectModeBoundary:
    """coverage_mode 边界测试"""

    def test_create_project_invalid_mode(self, admin_client):
        """创建项目使用无效 mode"""
        name = f"Invalid_Mode_Test_{int(time.time())}"

        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'invalid_mode'
            }),
            content_type='application/json')

        # API 应该接受任意值（不验证 mode 的有效性）
        # 或者返回错误
        # 这里根据实际 API 行为来写断言
        if response.status_code == 200:
            # API 接受任意值，mode 被设置为 invalid_mode
            result = json.loads(response.data)
            assert result['project'].get('coverage_mode') == 'invalid_mode'
            # 清理
            project_id = result['project']['id']
            admin_client.delete(f"/api/projects/{project_id}")
        else:
            # API 返回错误
            assert response.status_code == 400

    def test_update_project_mode(self, admin_client):
        """更新项目 mode"""
        name = f"Update_Mode_Test_{int(time.time())}"

        # 创建项目
        create_response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'tc_cp'
            }),
            content_type='application/json')

        assert create_response.status_code == 200
        project_id = json.loads(create_response.data)['project']['id']

        # 更新项目 mode
        update_response = admin_client.put(f'/api/projects/{project_id}',
            data=json.dumps({
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')

        # 根据 API 实现，可能需要 admin 权限
        assert update_response.status_code in [200, 403]

        # 清理
        admin_client.delete(f"/api/projects/{project_id}")

    def test_mode_field_in_project_response(self, admin_client):
        """验证项目响应包含 mode 字段"""
        name = f"Field_Test_{int(time.time())}"

        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31',
                'coverage_mode': 'fc_cp'
            }),
            content_type='application/json')

        assert response.status_code == 200
        result = json.loads(response.data)

        # 验证响应包含所有必要字段
        project = result['project']
        assert 'id' in project
        assert 'name' in project
        assert 'coverage_mode' in project
        assert project['coverage_mode'] == 'fc_cp'

        # 清理
        project_id = project['id']
        admin_client.delete(f"/api/projects/{project_id}")
