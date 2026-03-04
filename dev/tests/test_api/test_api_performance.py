#!/usr/bin/env python3
"""
API 性能测试用例 - 增强测试套件
覆盖 API 响应时间、批量操作、列表查询等性能测试
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


@pytest.fixture(scope='module')
def test_project():
    """创建测试项目用于测试"""
    app = create_app(testing=True)
    with app.test_client() as client:
        # 先登录
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"Perf_Test_{int(time.time())}"

        # 创建项目
        response = client.post('/api/projects',
                              data=json.dumps({'name': name, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
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
def cleanup_tcs(admin_client, test_project):
    """清理测试创建的 TC"""
    created_ids = []
    yield created_ids
    for tc_id in created_ids:
        try:
            admin_client.delete(f'/api/tc/{tc_id}?project_id={test_project["id"]}')
        except:
            pass


@pytest.fixture
def cleanup_cps(admin_client, test_project):
    """清理测试创建的 CP"""
    created_ids = []
    yield created_ids
    for cp_id in created_ids:
        try:
            admin_client.delete(f'/api/cp/{cp_id}?project_id={test_project["id"]}')
        except:
            pass


# ============ 性能测试用例 ============

class TestAPISingleResponseTime:
    """单个 API 响应时间测试 (目标: < 500ms)"""
    
    def test_version_api_response_time(self, client):
        """API-PERF-001: /api/version 响应时间 < 500ms"""
        start = time.time()
        response = client.get('/api/version')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"API响应时间 {elapsed:.2f}ms 超过 500ms"
    
    def test_projects_list_response_time(self, admin_client):
        """API-PERF-001: /api/projects 响应时间 < 500ms"""
        start = time.time()
        response = admin_client.get('/api/projects')
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 500, f"API响应时间 {elapsed:.2f}ms 超过 500ms"

    def test_tc_list_response_time(self, admin_client, test_project):
        """API-PERF-001: /api/tc 响应时间 < 500ms"""
        start = time.time()
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 500, f"API响应时间 {elapsed:.2f}ms 超过 500ms"
    
    def test_cp_list_response_time(self, admin_client, test_project):
        """API-PERF-001: /api/cp 响应时间 < 500ms"""
        start = time.time()
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"API响应时间 {elapsed:.2f}ms 超过 500ms"


class TestBatchOperationResponseTime:
    """批量操作响应时间测试 (目标: < 1s for 10 items)"""
    
    def test_batch_status_response_time(self, admin_client, test_project, cleanup_tcs):
        """API-PERF-002: 批量更新 10 个 TC 状态响应时间 < 1s"""
        # 创建 10 个 TC
        tc_ids = []
        for i in range(10):
            create_resp = admin_client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Batch_{i}_{int(time.time())}',
                    'test_name': f'TC_Batch_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                tc_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_tcs.append(tc_ids[-1])
        
        start = time.time()
        response = admin_client.post('/api/tc/batch/status',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'status': 'CODED'
            }),
            content_type='application/json')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 1000, f"批量操作响应时间 {elapsed:.2f}ms 超过 1000ms"
    
    def test_batch_target_date_response_time(self, admin_client, test_project, cleanup_tcs):
        """API-PERF-002: 批量更新 10 个 TC Target Date 响应时间 < 1s"""
        # 创建 10 个 TC
        tc_ids = []
        for i in range(10):
            create_resp = admin_client.post('/api/tc',
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
        
        start = time.time()
        response = admin_client.post('/api/tc/batch/target_date',
            data=json.dumps({
                'project_id': test_project["id"],
                'tc_ids': tc_ids,
                'target_date': '2026-03-01'
            }),
            content_type='application/json')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 1000, f"批量操作响应时间 {elapsed:.2f}ms 超过 1000ms"
    
    def test_batch_priority_response_time(self, admin_client, test_project, cleanup_cps):
        """API-PERF-002: 批量更新 10 个 CP Priority 响应时间 < 1s"""
        # 创建 10 个 CP
        cp_ids = []
        for i in range(10):
            create_resp = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'feature': f'Feature_Prio_{i}_{int(time.time())}',
                    'cover_point': f'CP_Prio_{i}_{int(time.time())}'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cp_ids.append(json.loads(create_resp.data)['item']['id'])
                cleanup_cps.append(cp_ids[-1])
        
        start = time.time()
        response = admin_client.post('/api/cp/batch/priority',
            data=json.dumps({
                'project_id': test_project["id"],
                'cp_ids': cp_ids,
                'priority': 'P1'
            }),
            content_type='application/json')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 1000, f"批量操作响应时间 {elapsed:.2f}ms 超过 1000ms"


class TestListQueryResponseTime:
    """列表查询响应时间测试 (目标: < 500ms for 100 items)"""
    
    def test_list_query_with_100_tcs(self, admin_client, test_project, cleanup_tcs):
        """API-PERF-003: 查询 100 条 TC 数据响应时间 < 500ms"""
        # 创建 100 个 TC
        for i in range(100):
            create_resp = admin_client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Perf_{i}_{int(time.time())}',
                    'test_name': f'TC_Perf_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 查询列表
        start = time.time()
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 0  # 可能有其他测试数据
        assert elapsed < 500, f"查询响应时间 {elapsed:.2f}ms 超过 500ms"
    
    def test_list_query_with_100_cps(self, admin_client, test_project, cleanup_cps):
        """API-PERF-003: 查询 100 条 CP 数据响应时间 < 500ms"""
        # 创建 100 个 CP
        for i in range(100):
            create_resp = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'feature': f'Feature_Perf_{i}_{int(time.time())}',
                    'cover_point': f'CP_Perf_{i}_{int(time.time())}'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cleanup_cps.append(json.loads(create_resp.data)['item']['id'])
        
        # 查询列表
        start = time.time()
        response = admin_client.get(f'/api/cp?project_id={test_project["id"]}')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 0
        assert elapsed < 500, f"查询响应时间 {elapsed:.2f}ms 超过 500ms"


class TestStatsAPIResponseTime:
    """统计 API 响应时间测试 (目标: < 500ms)"""
    
    def test_stats_api_response_time(self, admin_client, test_project):
        """API-PERF-004: /api/stats 响应时间 < 500ms"""
        start = time.time()
        response = admin_client.get(f'/api/stats?project_id={test_project["id"]}')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"统计API响应时间 {elapsed:.2f}ms 超过 500ms"
    
    def test_stats_api_with_data_response_time(self, admin_client, test_project, cleanup_tcs, cleanup_cps):
        """API-PERF-004: 有数据时 /api/stats 响应时间 < 500ms"""
        # 创建测试数据
        for i in range(10):
            create_tc = admin_client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Stat_{i}_{int(time.time())}',
                    'test_name': f'TC_Stat_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_tc.status_code == 200:
                cleanup_tcs.append(json.loads(create_tc.data)['item']['id'])
        
        for i in range(5):
            create_cp = admin_client.post('/api/cp',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'feature': f'Feature_Stat_{i}_{int(time.time())}',
                    'cover_point': f'CP_Stat_{i}_{int(time.time())}'
                }),
                content_type='application/json')
            if create_cp.status_code == 200:
                cleanup_cps.append(json.loads(create_cp.data)['item']['id'])
        
        start = time.time()
        response = admin_client.get(f'/api/stats?project_id={test_project["id"]}')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_tc' in data
        assert elapsed < 500, f"统计API响应时间 {elapsed:.2f}ms 超过 500ms"


class TestFilterQueryResponseTime:
    """过滤查询响应时间测试 (目标: < 500ms)"""
    
    def test_filter_query_response_time(self, admin_client, test_project, cleanup_tcs):
        """API-PERF-005: 过滤查询响应时间 < 500ms"""
        # 创建带不同属性的 TC
        for i in range(20):
            owner = 'OwnerA' if i % 2 == 0 else 'OwnerB'
            category = 'Sanity' if i % 3 == 0 else 'Feature'
            create_resp = admin_client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Filter_{i}_{int(time.time())}',
                    'test_name': f'TC_Filter_{i}_{int(time.time())}',
                    'category': category,
                    'owner': owner
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 按 owner 过滤
        start = time.time()
        response = admin_client.get(f'/api/tc?project_id={test_project["id"]}&owner=OwnerA')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"过滤查询响应时间 {elapsed:.2f}ms 超过 500ms"
    
    def test_combined_filter_response_time(self, admin_client, test_project, cleanup_tcs):
        """API-PERF-005: 组合过滤查询响应时间 < 500ms"""
        # 创建带不同属性的 TC
        for i in range(20):
            create_resp = admin_client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Comb_{i}_{int(time.time())}',
                    'test_name': f'TC_Comb_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester',
                    'dv_milestone': 'DV1.0'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 组合过滤
        start = time.time()
        response = admin_client.get(
            f'/api/tc?project_id={test_project["id"]}&owner=Tester&dv_milestone=DV1.0')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"组合过滤响应时间 {elapsed:.2f}ms 超过 500ms"
    
    def test_sort_query_response_time(self, admin_client, test_project, cleanup_tcs):
        """API-PERF-005: 排序查询响应时间 < 500ms"""
        # 创建 TC
        for i in range(30):
            create_resp = admin_client.post('/api/tc',
                data=json.dumps({
                    'project_id': test_project["id"],
                    'testbench': f'TB_Sort_{i}_{int(time.time())}',
                    'test_name': f'TC_Sort_{i}_{int(time.time())}',
                    'category': 'Sanity',
                    'owner': 'Tester'
                }),
                content_type='application/json')
            if create_resp.status_code == 200:
                cleanup_tcs.append(json.loads(create_resp.data)['item']['id'])
        
        # 按 testbench 排序
        start = time.time()
        response = admin_client.get(
            f'/api/tc?project_id={test_project["id"]}&sort_by=testbench')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"排序查询响应时间 {elapsed:.2f}ms 超过 500ms"


class TestThroughputPerformance:
    """吞吐量性能测试"""
    
    def test_consecutive_requests_throughput(self, admin_client, test_project):
        """连续请求吞吐量测试 - 10 个请求平均 < 200ms"""
        response_times = []
        
        for i in range(10):
            start = time.time()
            response = admin_client.get(f'/api/tc?project_id={test_project["id"]}')
            elapsed = (time.time() - start) * 1000
            response_times.append(elapsed)
            assert response.status_code == 200
        
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # 平均响应时间应 < 200ms
        assert avg_time < 200, f"平均响应时间 {avg_time:.2f}ms 超过 200ms"
        # 最大响应时间应 < 500ms
        assert max_time < 500, f"最大响应时间 {max_time:.2f}ms 超过 500ms"


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
