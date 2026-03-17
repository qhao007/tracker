#!/usr/bin/env python3
"""
Tracker API 过滤功能测试用例 - CP 过滤测试
测试计划: TRACKER_TEST_PLAN_v0.9.2
覆盖 REQ-005 过滤功能
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
def test_project(admin_client):
    """创建测试项目用于测试"""
    name = f"FilterTest_{int(time.time())}"

    # 创建项目
    response = admin_client.post('/api/projects',
                          data=json.dumps({'name': name, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
                          content_type='application/json')

    if response.status_code == 200:
        data = json.loads(response.data)
        project_id = data['project']['id']
        yield {'id': project_id, 'name': name}

        # 清理：删除测试项目
        admin_client.delete(f"/api/projects/{project_id}")
    else:
        pytest.skip("无法创建测试项目")


class TestCPFilterAPI:
    """CP 过滤功能 API 测试 (REQ-005)"""

    def test_get_cp_with_filter_all(self, admin_client, test_project):
        """
        API-FILTER-001: 获取全部CP（默认）
        测试目标: 不传 filter 参数时返回所有 CP
        预期结果: 返回所有 CP
        """
        # 创建多个 CP
        cp_ids = []
        for i in range(3):
            resp = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'feature': f'Feature_All_{i}_{int(time.time())}',
                    'sub_feature': 'SubFeature',
                    'cover_point': f'CP_All_{i}_{int(time.time())}',
                    'cover_point_details': f'Test CP {i}',
                    'priority': 'P1'
                }),
                content_type='application/json')
            assert resp.status_code == 200
            cp_data = json.loads(resp.data)
            cp_ids.append(cp_data['item']['id'])

        # 获取全部 CP（不带 filter 参数）
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}')
        assert response.status_code == 200

        data = json.loads(response.data)
        # 验证返回了 CP 数据
        assert isinstance(data, list)
        # 验证我们创建的 CP 都在返回列表中
        returned_cp_ids = [cp['id'] for cp in data]
        for cp_id in cp_ids:
            assert cp_id in returned_cp_ids

    def test_get_cp_with_filter_unlinked(self, admin_client, test_project):
        """
        API-FILTER-002: 获取未关联CP
        测试目标: filter=unlinked 时只返回 linked=false 的 CP
        预期结果: 只返回未关联的 CP
        """
        # 创建一个未关联的 CP
        unlinked_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': f'Feature_Unlinked_{int(time.time())}',
                'sub_feature': 'SubFeature',
                'cover_point': f'CP_Unlinked_{int(time.time())}',
                'cover_point_details': 'Unlinked CP',
                'priority': 'P2'
            }),
            content_type='application/json')
        assert unlinked_resp.status_code == 200
        unlinked_cp_data = json.loads(unlinked_resp.data)
        unlinked_cp_id = unlinked_cp_data['item']['id']

        # 创建一个已关联的 CP（需要先创建 TC）
        linked_cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': f'Feature_Linked_{int(time.time())}',
                'sub_feature': 'SubFeature',
                'cover_point': f'CP_Linked_{int(time.time())}',
                'cover_point_details': 'Linked CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        assert linked_cp_resp.status_code == 200
        linked_cp_data = json.loads(linked_cp_resp.data)
        linked_cp_id = linked_cp_data['item']['id']

        # 创建 TC 并关联到 CP
        tc_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Linked_{int(time.time())}',
                'test_name': f'TC_Linked_{int(time.time())}',
                'category': 'Sanity',
                'owner': 'TestEng',
                'connections': [linked_cp_id]
            }),
            content_type='application/json')
        assert tc_resp.status_code == 200

        # 使用 filter=unlinked 获取未关联的 CP
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}&filter=unlinked')
        assert response.status_code == 200

        data = json.loads(response.data)
        # 验证返回的是未关联的 CP
        assert isinstance(data, list)
        # 验证 linked_cp_id 不在返回列表中（已关联）
        returned_cp_ids = [cp['id'] for cp in data]
        assert linked_cp_id not in returned_cp_ids
        # 验证未关联的 CP 在返回列表中且 linked=false
        for cp in data:
            if cp['id'] == unlinked_cp_id:
                assert cp['linked'] == False

    def test_get_cp_filter_with_project(self, admin_client):
        """
        API-FILTER-003: 指定项目过滤
        测试目标: 指定 project_id 参数时按项目过滤
        预期结果: 只返回指定项目的 CP
        """
        # 创建两个不同项目 - 使用不同的时间戳确保唯一性
        name1 = f"Project1_{int(time.time() * 1000000)}"
        name2 = f"Project2_{int(time.time() * 1000000) + 1}"

        resp1 = admin_client.post('/api/projects',
            data=json.dumps({'name': name1, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
            content_type='application/json')
        project1_id = json.loads(resp1.data)['project']['id']

        resp2 = admin_client.post('/api/projects',
            data=json.dumps({'name': name2, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
            content_type='application/json')
        project2_id = json.loads(resp2.data)['project']['id']

        try:
            # 为项目1创建 CP
            feature1 = f"Feature_Proj1_{int(time.time() * 1000000)}"
            cp1_resp = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': project1_id,
                    'feature': feature1,
                    'cover_point': f'CP_Proj1_{int(time.time() * 1000000)}',
                    'cover_point_details': 'Project 1 CP'
                }),
                content_type='application/json')
            assert cp1_resp.status_code == 200

            # 为项目2创建 CP
            feature2 = f"Feature_Proj2_{int(time.time() * 1000000)}"
            cp2_resp = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': project2_id,
                    'feature': feature2,
                    'cover_point': f'CP_Proj2_{int(time.time() * 1000000)}',
                    'cover_point_details': 'Project 2 CP'
                }),
                content_type='application/json')
            assert cp2_resp.status_code == 200

            # 只获取项目1的 CP
            response = admin_client.get(f'/api/cp?project_id={project1_id}')
            assert response.status_code == 200

            data = json.loads(response.data)
            # 验证只返回项目1的 CP - 通过检查 feature 字段
            assert isinstance(data, list)
            features = [cp['feature'] for cp in data]
            assert feature1 in features
            assert feature2 not in features
            # 验证返回的 CP 的 project_id 正确
            for cp in data:
                assert cp['project_id'] == project1_id

            # 只获取项目2的 CP
            response2 = admin_client.get(f'/api/cp?project_id={project2_id}')
            assert response2.status_code == 200

            data2 = json.loads(response2.data)
            features2 = [cp['feature'] for cp in data2]
            assert feature1 not in features2
            assert feature2 in features2
            # 验证返回的 CP 的 project_id 正确
            for cp in data2:
                assert cp['project_id'] == project2_id
        finally:
            # 清理项目
            admin_client.delete(f"/api/projects/{project1_id}")
            admin_client.delete(f"/api/projects/{project2_id}")

    def test_get_cp_filter_invalid(self, admin_client, test_project):
        """
        API-FILTER-004: 无效filter参数
        测试目标: 传入无效的 filter 参数时返回默认行为（全部）
        预期结果: 返回错误或默认全部
        """
        # 创建一个 CP
        cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': f'Feature_Invalid_{int(time.time())}',
                'sub_feature': 'SubFeature',
                'cover_point': f'CP_Invalid_{int(time.time())}',
                'cover_point_details': 'Test CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        assert cp_resp.status_code == 200
        cp_data = json.loads(cp_resp.data)
        cp_id = cp_data['item']['id']

        # 使用无效的 filter 参数（如 "invalid_value"）
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}&filter=invalid_value')
        assert response.status_code == 200

        data = json.loads(response.data)
        # 无效 filter 参数时应该返回默认行为（全部 CP）
        assert isinstance(data, list)
        # 验证我们创建的 CP 仍然在返回列表中
        returned_cp_ids = [cp['id'] for cp in data]
        assert cp_id in returned_cp_ids


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
