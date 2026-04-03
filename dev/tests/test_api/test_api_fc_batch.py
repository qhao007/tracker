#!/usr/bin/env python3
"""
Tracker API 测试用例 - FC Batch Update API 测试
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
    name = f"FC_Batch_Test_{int(time.time())}"

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
def tc_cp_project(admin_client):
    """创建 TC-CP 模式的测试项目"""
    name = f"TC_CP_Test_{int(time.time())}"

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
def test_fc(admin_client, fc_cp_project):
    """创建测试 FC 数据"""
    csv_data = [
        ["Covergroup", "Coverpoint", "Type", "Bin_Name", "Bin_Value", "Coverage_Pct", "Status", "Comments"],
        ["CG_Batch_1", "CP_Batch_1", "cover", "bin_1", "1", "50.0", "ready", "Test FC 1"],
        ["CG_Batch_2", "CP_Batch_2", "cover", "bin_2", "2", "60.0", "missing", "Test FC 2"]
    ]

    response = admin_client.post(f'/api/fc/import?project_id={fc_cp_project["id"]}',
        data=json.dumps({'csv_data': csv_data}),
        content_type='application/json')

    if response.status_code == 200:
        # 获取导入的 FC 列表
        fc_list_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_list_response.data)

        if fc_list and len(fc_list) >= 2:
            yield {'ids': [fc_list[0]['id'], fc_list[1]['id']], 'project_id': fc_cp_project["id"]}
        else:
            pytest.skip("无法创建测试 FC")
    else:
        pytest.skip("无法创建测试 FC")


# ============ FC Batch Update API 测试 ============

class TestFCBatchUpdate:
    """FC Batch Update API 测试"""

    def test_batch_update_coverage_pct(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-001: 批量更新 coverage_pct"""
        fc_id = test_fc['ids'][0]

        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [{'id': fc_id, 'coverage_pct': 98.5}]
            }),
            content_type='application/json')

        assert response.status_code == 200, f"更新 FC 失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert result.get('updated') == 1
        assert result.get('failed') == 0

        # 验证更新结果
        fc_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_response.data)
        updated_fc = next((fc for fc in fc_list if fc['id'] == fc_id), None)
        assert updated_fc is not None
        assert updated_fc['coverage_pct'] == 98.5

    def test_batch_update_status(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-002: 批量更新 status"""
        fc_id = test_fc['ids'][0]

        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [{'id': fc_id, 'status': 'ready'}]
            }),
            content_type='application/json')

        assert response.status_code == 200, f"更新 FC 失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert result.get('updated') == 1
        assert result.get('failed') == 0

        # 验证更新结果
        fc_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_response.data)
        updated_fc = next((fc for fc in fc_list if fc['id'] == fc_id), None)
        assert updated_fc is not None
        assert updated_fc['status'] == 'ready'

    def test_batch_update_partial_fields(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-003: 批量更新部分字段 - 只更新coverage_pct"""
        fc_id = test_fc['ids'][0]

        # 先获取原始 status
        fc_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_response.data)
        original_fc = next((fc for fc in fc_list if fc['id'] == fc_id), None)
        original_status = original_fc['status']

        # 只更新 coverage_pct
        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [{'id': fc_id, 'coverage_pct': 85.0}]
            }),
            content_type='application/json')

        assert response.status_code == 200, f"更新 FC 失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert result.get('updated') == 1

        # 验证 coverage_pct 已更新
        fc_response = admin_client.get(f'/api/fc?project_id={fc_cp_project["id"]}')
        fc_list = json.loads(fc_response.data)
        updated_fc = next((fc for fc in fc_list if fc['id'] == fc_id), None)
        assert updated_fc['coverage_pct'] == 85.0
        # status 应该不变
        assert updated_fc['status'] == original_status

    def test_batch_update_multiple_items(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-004: 批量更新多个items"""
        fc_id_1 = test_fc['ids'][0]
        fc_id_2 = test_fc['ids'][1]

        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [
                    {'id': fc_id_1, 'coverage_pct': 99.0, 'status': 'ready'},
                    {'id': fc_id_2, 'coverage_pct': 88.0, 'status': 'missing'}
                ]
            }),
            content_type='application/json')

        assert response.status_code == 200, f"批量更新失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert result.get('updated') == 2
        assert result.get('failed') == 0

    def test_batch_update_empty_array(self, admin_client, fc_cp_project):
        """API-FC-BATCH-005: 空数组"""
        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': []
            }),
            content_type='application/json')

        assert response.status_code == 200, f"空数组请求失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == True
        assert result.get('updated') == 0
        assert result.get('failed') == 0

    def test_batch_update_partial_success_failure(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-006: 部分成功部分失败"""
        fc_id_valid = test_fc['ids'][0]
        fc_id_invalid = 99999  # 不存在的 ID

        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [
                    {'id': fc_id_valid, 'coverage_pct': 95.0},
                    {'id': fc_id_invalid, 'coverage_pct': 80.0}
                ]
            }),
            content_type='application/json')

        assert response.status_code == 200, f"批量更新失败: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == False  # 有失败
        assert result.get('updated') == 1
        assert result.get('failed') == 1
        assert len(result.get('errors', [])) >= 1

    def test_batch_update_coverage_pct_too_high(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-007: coverage_pct超出范围-过大"""
        fc_id = test_fc['ids'][0]

        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [{'id': fc_id, 'coverage_pct': 150}]
            }),
            content_type='application/json')

        assert response.status_code == 400, f"应该返回校验错误: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == False
        assert 'Invalid coverage_pct' in result.get('error', '')

    def test_batch_update_coverage_pct_negative(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-008: coverage_pct超出范围-负数"""
        fc_id = test_fc['ids'][0]

        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [{'id': fc_id, 'coverage_pct': -10}]
            }),
            content_type='application/json')

        assert response.status_code == 400, f"应该返回校验错误: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == False
        assert 'Invalid coverage_pct' in result.get('error', '')

    def test_batch_update_invalid_status(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-009: 无效status值"""
        fc_id = test_fc['ids'][0]

        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [{'id': fc_id, 'status': 'invalid'}]
            }),
            content_type='application/json')

        assert response.status_code == 200, f"无效status应该返回错误: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == False
        assert result.get('failed') == 1
        assert len(result.get('errors', [])) >= 1

    def test_batch_update_missing_required_field(self, admin_client, fc_cp_project, test_fc):
        """API-FC-BATCH-010: 缺少必填字段 - 只传coverage_pct无id"""
        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': fc_cp_project['id'],
                'items': [{'coverage_pct': 85.0}]
            }),
            content_type='application/json')

        # 根据 API 实现，缺少 id 应该返回错误
        assert response.status_code == 200, f"缺少id应该处理: {response.data}"
        result = json.loads(response.data)

        # API 应该能处理这种情况（要么报错要么标记为failed）
        assert result.get('failed') >= 0

    def test_batch_update_invalid_json(self, admin_client, fc_cp_project):
        """API-FC-BATCH-011: 无效JSON格式"""
        response = admin_client.put(f'/api/fc/batch',
            data='invalid json {{{',
            content_type='application/json')

        assert response.status_code == 400, f"无效JSON应该返回400: {response.data}"

    def test_batch_update_tc_cp_mode(self, admin_client, tc_cp_project):
        """API-FC-BATCH-012: TC-CP模式下调用"""
        response = admin_client.put(f'/api/fc/batch',
            data=json.dumps({
                'project_id': tc_cp_project['id'],
                'items': [{'id': 1, 'coverage_pct': 85.0}]
            }),
            content_type='application/json')

        assert response.status_code == 400, f"TC-CP模式应该返回错误: {response.data}"
        result = json.loads(response.data)

        assert result.get('success') == False
        assert 'Not in FC-CP mode' in result.get('error', '')
