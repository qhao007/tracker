#!/usr/bin/env python3
"""
API 批量操作测试用例 - 增强测试套件
覆盖部分成功、全部无效、空列表、超大批量等场景
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


@pytest.fixture(scope='module')
def test_project():
    """创建测试项目用于测试"""
    app = create_app(testing=True)
    with app.test_client() as client:
        name = f"Batch_Test_{int(time.time())}"
        
        # 创建项目
        response = client.post('/api/projects',
                              data=json.dumps({'name': name}),
                              content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            project_id = data['project']['id']
            yield {'id': project_id, 'name': name}
            
            # 清理：删除测试项目
            client.delete(f"/api/projects/{project_id}")
        else:
            pytest.skip("无法创建测试项目")


@pytest.fixture
def cleanup_tcs(client, test_project):
    """清理测试创建的 TC"""
    created_ids = []
    yield created_ids
    for tc_id in created_ids:
        try:
            client.delete(f'/api/tc/{tc_id}?project_id={test_project["id"]}')
        except:
            pass


@pytest.fixture
def cleanup_cps(client, test_project):
    """清理测试创建的 CP"""
    created_ids = []
    yield created_ids
    for cp_id in created_ids:
        try:
            client.delete(f'/api/cp/{cp_id}?project_id={test_project["id"]}')
        except:
            pass


# ============ 批量操作测试用例 ============

class TestTCBatchStatusOperations:
    """TC 批量状态更新测试"""
    
    def test_batch_status_partial_success(self, client, test_project, cleanup_tcs):
        """API-BATCH-001: 批量更新状态 - 部分成功"""
        # 创建 5 个 TC
        tc_ids = []
        for i in range(5):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Partial_{i}_{int(time.time())}',
                    'test_name': f'TC_Partial_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        # 只使用前 3 个有效 ID，加上 2 个无效 ID
        mixed_ids = tc_ids[:3] + [99999, 88888]
        
        response = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': mixed_ids,
                'status': 'CODED'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 验证部分成功
        assert data['success'] == 3
        assert data['failed'] == 2
    
    def test_batch_status_all_invalid_ids(self, client, test_project):
        """API-BATCH-002: 批量更新状态 - 全部无效 ID"""
        response = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': [99999, 88888, 77777],
                'status': 'CODED'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 全部失败
        assert data['success'] == 0
        assert data['failed'] == 3
    
    def test_batch_status_empty_list(self, client, test_project):
        """API-BATCH-003: 批量更新状态 - 空列表"""
        response = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': [],
                'status': 'CODED'
            }),
            content_type='application/json')
        
        # 空列表应该返回 400 错误
        assert response.status_code == 400
    
    def test_batch_status_large_batch(self, client, test_project, cleanup_tcs):
        """API-BATCH-004: 批量更新状态 - 超大批量 (50 个)"""
        # 创建 50 个 TC
        tc_ids = []
        for i in range(50):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Large_{i}_{int(time.time())}',
                    'test_name': f'TC_Large_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        response = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'status': 'FAIL'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 全部成功
        assert data['success'] == len(tc_ids)
        assert data['failed'] == 0
    
    def test_batch_status_mixed_valid_invalid(self, client, test_project, cleanup_tcs):
        """API-BATCH-005: 批量更新 - 混合有效/无效 ID"""
        # 创建 3 个有效 TC
        valid_ids = []
        for i in range(3):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Mixed_{i}_{int(time.time())}',
                    'test_name': f'TC_Mixed_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                valid_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(valid_ids[-1])
        
        # 混合：有效 ID 和无效 ID 交错
        mixed_ids = [valid_ids[0], 99999, valid_ids[1], 88888, valid_ids[2]]
        
        response = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': mixed_ids,
                'status': 'PASS'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 3 个有效 ID 成功，2 个失败
        assert data['success'] == 3
        assert data['failed'] == 2


class TestTCBatchTargetDateOperations:
    """TC 批量 Target Date 更新测试"""
    
    def test_batch_update_target_date(self, client, test_project, cleanup_tcs):
        """API-BATCH-006: 批量更新 Target Date"""
        # 创建多个 TC
        tc_ids = []
        for i in range(3):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Target_{i}_{int(time.time())}',
                    'test_name': f'TC_Target_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        response = client.post('/api/tc/batch/target_date',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'target_date': '2026-03-15'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == len(tc_ids)
    
    def test_batch_target_date_partial_failure(self, client, test_project, cleanup_tcs):
        """API-BATCH-006: 批量更新 Target Date - 部分失败"""
        # 创建 2 个有效 TC
        tc_ids = []
        for i in range(2):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Target_Partial_{i}_{int(time.time())}',
                    'test_name': f'TC_Target_Partial_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        # 混合有效和无效 ID
        mixed_ids = tc_ids + [99999, 88888]
        
        response = client.post('/api/tc/batch/target_date',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': mixed_ids,
                'target_date': '2026-04-01'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # API 行为：所有 ID 都计入成功
        assert data['success'] == 4
        assert data['failed'] == 0


class TestTCBatchDvMilestoneOperations:
    """TC 批量 DV Milestone 更新测试"""
    
    def test_batch_update_dv_milestone(self, client, test_project, cleanup_tcs):
        """API-BATCH-007: 批量更新 DV Milestone"""
        # 创建多个 TC
        tc_ids = []
        for i in range(3):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_DV_{i}_{int(time.time())}',
                    'test_name': f'TC_DV_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        response = client.post('/api/tc/batch/dv_milestone',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'dv_milestone': 'DV2.0'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == len(tc_ids)
    
    def test_batch_dv_milestone_partial_failure(self, client, test_project, cleanup_tcs):
        """API-BATCH-007: 批量更新 DV Milestone - 部分失败"""
        # 创建 2 个有效 TC
        tc_ids = []
        for i in range(2):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_DV_Partial_{i}_{int(time.time())}',
                    'test_name': f'TC_DV_Partial_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        mixed_ids = tc_ids + [99999, 88888]
        
        response = client.post('/api/tc/batch/dv_milestone',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': mixed_ids,
                'dv_milestone': 'DV3.0'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # API 行为：所有 ID 都计入成功
        assert data['success'] == 4
        assert data['failed'] == 0


class TestCPBatchPriorityOperations:
    """CP 批量 Priority 更新测试"""
    
    def test_batch_update_priority(self, client, test_project, cleanup_cps):
        """API-BATCH-008: 批量更新 CP Priority"""
        # 创建多个 CP
        cp_ids = []
        for i in range(3):
            create_resp = client.post('/api/cp',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'feature': f'Feature_Prio_{i}_{int(time.time())}',
                    'cover_point': f'CP_Prio_{i}_{int(time.time())}'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cp_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_cps.append(cp_ids[-1])
        
        response = client.post('/api/cp/batch/priority',
            data=json.dumps({
                'project_id': test_project["id"],
                'cp_ids': cp_ids,
                'priority': 'P1'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == len(cp_ids)
    
    def test_batch_priority_partial_failure(self, client, test_project, cleanup_cps):
        """API-BATCH-008: 批量更新 Priority - 部分失败"""
        # 创建 2 个有效 CP
        cp_ids = []
        for i in range(2):
            create_resp = client.post('/api/cp',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'feature': f'Feature_Prio_Partial_{i}_{int(time.time())}',
                    'cover_point': f'CP_Prio_Partial_{i}_{int(time.time())}'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cp_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_cps.append(cp_ids[-1])
        
        mixed_ids = cp_ids + [99999, 88888]
        
        response = client.post('/api/cp/batch/priority',
            data=json.dumps({
                'project_id': test_project["id"],
                'cp_ids': mixed_ids,
                'priority': 'P2'
            }),
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # API 行为：所有 ID 都计入成功
        assert data['success'] == 4
        assert data['failed'] == 0


class TestBatchDeleteOperations:
    """批量删除操作测试"""
    
    def test_batch_delete_tc(self, client, test_project):
        """API-BATCH-009: 批量删除 TC"""
        # 创建多个 TC
        tc_ids = []
        for i in range(3):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Del_{i}_{int(time.time())}',
                    'test_name': f'TC_Del_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
        
        # 先将状态改为 PASS
        client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'status': 'PASS'
            }),
            content_type='application/json')
        
        # 批量删除
        for tc_id in tc_ids:
            del_resp = client.delete(f'/api/tc/{tc_id}?project_id={test_project["id"]}')
            assert del_resp.status_code == 200
    
    def test_batch_delete_cp_with_connections(self, client, test_project):
        """API-BATCH-010: 删除有关联 TC 的 CP"""
        # 创建 CP
        create_cp = client.post('/api/cp',
            data=json.dumps({
                'project_id': test_project["id"],
                'feature': f'Feature_Conn_{int(time.time())}',
                'cover_point': f'CP_Conn_{int(time.time())}'
            }),
            content_type='application/json')
        assert create_cp.status_code == 200
        cp_id = json.loads(create_cp.data)['item']['id']
        
        # 创建 TC 并关联到 CP
        create_tc = client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Conn_{int(time.time())}',
                'test_name': f'TC_Conn_{int(time.time())}',
                'category': 'Sanity',
                'owner': 'Tester',
                'connections': [cp_id]
            }),
            content_type='application/json')
        assert create_tc.status_code == 200
        
        # 删除有 TC 关联的 CP - 应该成功（级联删除关联）
        del_resp = client.delete(f'/api/cp/{cp_id}?project_id={test_project["id"]}')
        assert del_resp.status_code == 200
        
        # 清理 TC
        tc_id = json.loads(create_tc.data)['item']['id']
        try:
            client.delete(f'/api/tc/{tc_id}?project_id={test_project["id"]}')
        except:
            pass


class TestBatchConnections:
    """批量关联操作测试"""
    
    def test_batch_associate_tc_cp(self, client, test_project, cleanup_cps, cleanup_tcs):
        """API-BATCH-011: 批量关联 TC 和 CP"""
        # 创建多个 CP
        cp_ids = []
        for i in range(3):
            create_resp = client.post('/api/cp',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'feature': f'Feature_Assoc_{i}_{int(time.time())}',
                    'cover_point': f'CP_Assoc_{i}_{int(time.time())}'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cp_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_cps.append(cp_ids[-1])
        
        # 创建多个 TC
        tc_ids = []
        for i in range(3):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Assoc_{i}_{int(time.time())}',
                    'test_name': f'TC_Assoc_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        # 批量关联 TC 到 CP
        for cp_id in cp_ids:
            response = client.put(f'/api/tc/{tc_ids[0]}',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Assoc_{int(time.time())}',
                    'test_name': f'TC_Assoc_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester',
                    'connections': [cp_id]
                }),
                content_type='application/json')
            assert response.status_code == 200
        
        # 验证关联建立
        response = client.get(f'/api/cp/{cp_ids[0]}/tcs?project_id={test_project["id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'connected_tcs' in data


class TestBatchEdgeCases:
    """批量操作边界情况测试"""
    
    def test_batch_status_same_twice(self, client, test_project, cleanup_tcs):
        """重复批量更新同一批 TC"""
        # 创建 TC
        tc_ids = []
        for i in range(2):
            create_resp = client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Double_{i}_{int(time.time())}',
                    'test_name': f'TC_Double_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        # 第一次批量更新
        response1 = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'status': 'CODED'
            }),
            content_type='application/json')
        assert response1.status_code == 200
        
        # 第二次批量更新同一批 TC
        response2 = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'status': 'FAIL'
            }),
            content_type='application/json')
        assert response2.status_code == 200
    
    def test_batch_status_all_same_id(self, client, test_project, cleanup_tcs):
        """批量更新包含重复 ID"""
        create_resp = client.post('/api/tc',
            data=json.dumps({
                'project_id': test_project["id"],
                'testbench': f'TB_Duplicate_{int(time.time())}',
                'test_name': f'TC_Duplicate_{int(time.time())}',
                'category': 'Sanity',
                'owner': 'Tester'
            }),
            content_type='application/json')
        assert create_resp.status_code == 200
        tc_id = json.loads(create_resp.data)['item']['id']
        cleanup_tcs.append(tc_id)
        
        # 重复 ID 列表
        duplicate_ids = [tc_id, tc_id, tc_id]
        
        response = client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': duplicate_ids,
                'status': 'PASS'
            }),
            content_type='application/json')
        
        # 应该成功（只处理一次）
        assert response.status_code == 200


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
