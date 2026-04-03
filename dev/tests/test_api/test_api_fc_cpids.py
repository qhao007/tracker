#!/usr/bin/env python3
"""
Tracker API 测试用例 - FC cp_ids 字段测试
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
def fc_cp_project(admin_client):
    """创建 FC-CP 模式的测试项目"""
    name = f"FC_CPIDS_Test_{int(time.time())}"

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


@pytest.fixture
def test_cps(admin_client, fc_cp_project):
    """创建测试 CP 数据"""
    cps = []
    for i in range(3):
        response = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'feature': f'Feature_{i}',
                'sub_feature': f'SubFeature_{i}',
                'cover_point': f'CP_Test_{i}',
                'cover_point_details': f'Details {i}',
                'priority': 'P1'
            }),
            content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            cp_id = data.get('item', {}).get('id')
            if cp_id:
                cps.append(cp_id)

    yield cps

    # 清理
    for cp_id in cps:
        try:
            admin_client.delete(f'/api/cp/{cp_id}?project_id={fc_cp_project["id"]}')
        except:
            pass


@pytest.fixture
def test_fc(admin_client, fc_cp_project):
    """创建测试 FC 数据"""
    csv_data = [
        ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
        ["CG_CPIDS", "CP_CPIDS", "cover", "bin_test", "1", "50.0", "ready", "Test FC"]
    ]

    response = admin_client.post(f'/api/fc/import?project_id={fc_cp_project["id"]}',
        data=json.dumps({'csv_data': csv_data}),
        content_type='application/json')

    if response.status_code == 200:
        # 获取导入的 FC 列表
        fc_list_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_list_response.data)

        if fc_list:
            fc = fc_list[0]
            yield {'id': fc['id'], 'project_id': fc_cp_project["id"]}
        else:
            pytest.skip("无法创建测试 FC")
    else:
        pytest.skip("无法创建测试 FC")


# ============ FC cp_ids 测试 ============

class TestFCCpIds:
    """FC cp_ids 字段测试"""

    def test_fc_no_associated_cp(self, admin_client, fc_cp_project, test_fc):
        """API-FC-CPIDS-001: 无关联CP返回空数组"""
        response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')

        assert response.status_code == 200, f"获取 FC 列表失败: {response.data}"
        fc_list = json.loads(response.data)

        # 找到我们的测试 FC
        target_fc = next((fc for fc in fc_list if fc['id'] == test_fc['id']), None)
        assert target_fc is not None, "测试 FC 应该存在"
        assert 'cp_ids' in target_fc, "FC 应该包含 cp_ids 字段"
        assert target_fc['cp_ids'] == [], "无关联 CP 应该返回空数组"

    def test_fc_single_associated_cp(self, admin_client, fc_cp_project, test_fc, test_cps):
        """API-FC-CPIDS-002: 单个关联CP"""
        if len(test_cps) < 1:
            pytest.skip("需要至少一个 CP")

        cp_id = test_cps[0]

        # 关联 FC 和 CP
        response = admin_client.post('/api/fc-cp-association',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'fc_id': test_fc['id'],
                'cp_id': cp_id
            }),
            content_type='application/json')

        assert response.status_code in [200, 201], f"关联 FC-CP 失败: {response.data}"

        # 验证 cp_ids
        fc_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_response.data)
        target_fc = next((fc for fc in fc_list if fc['id'] == test_fc['id']), None)

        assert target_fc is not None
        assert 'cp_ids' in target_fc
        assert cp_id in target_fc['cp_ids'], f"CP ID {cp_id} 应该在 cp_ids 中"

    def test_fc_multiple_associated_cp(self, admin_client, fc_cp_project, test_fc, test_cps):
        """API-FC-CPIDS-003: 多个关联CP"""
        if len(test_cps) < 3:
            pytest.skip("需要至少三个 CP")

        # 关联 FC 和多个 CP (使用第0,1,2个)
        for cp_id in test_cps[:3]:
            response = admin_client.post('/api/fc-cp-association',
                data=json.dumps({
                    'project_id': fc_cp_project['id'],
                    'fc_id': test_fc['id'],
                    'cp_id': cp_id
                }),
                content_type='application/json')

            assert response.status_code in [200, 201], f"关联 FC-CP 失败: {response.data}"

        # 验证 cp_ids 按顺序返回
        fc_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_response.data)
        target_fc = next((fc for fc in fc_list if fc['id'] == test_fc['id']), None)

        assert target_fc is not None
        assert 'cp_ids' in target_fc
        # 应该包含所有关联的 CP IDs
        for cp_id in test_cps[:3]:
            assert cp_id in target_fc['cp_ids'], f"CP ID {cp_id} 应该在 cp_ids 中"
