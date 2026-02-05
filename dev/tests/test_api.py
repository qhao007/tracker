#!/usr/bin/env python3
"""
Tracker API 测试用例 - dev 版本专用
完整测试套件，覆盖所有 API 端点
"""

import json
import pytest
import sys
import os
import time

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

# dev 版本使用 test_data 目录中的数据
TEST_PROJECT_ID = None  # 动态获取

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
        name = f"API_Test_{int(time.time())}"
        
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


# ============ 基础 API 测试 ============

class TestVersionAPI:
    """版本 API 测试"""
    
    def test_get_version(self, client):
        """GET /api/version"""
        response = client.get('/api/version')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'version' in data


# ============ 项目管理 API 测试 ============

class TestProjectsAPI:
    """项目 API 测试"""
    
    def test_get_projects(self, client):
        """GET /api/projects - 获取项目列表"""
        response = client.get('/api/projects')
        assert response.status_code == 200
    
    def test_create_project(self, client):
        """POST /api/projects - 创建项目"""
        name = f"Test_{int(time.time())}"
        response = client.post('/api/projects',
                              data=json.dumps({'name': name}),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # 清理
        client.delete(f"/api/projects/{data['project']['id']}")
    
    def test_create_duplicate_project(self, client):
        """POST /api/projects - 创建重复项目"""
        name = f"Dup_{int(time.time())}"
        # 先创建
        client.post('/api/projects',
                   data=json.dumps({'name': name}),
                   content_type='application/json')
        # 再次创建同名项目
        response = client.post('/api/projects',
                             data=json.dumps({'name': name}),
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_get_archive_list(self, client):
        """GET /api/projects/archive/list - 获取归档列表"""
        response = client.get('/api/projects/archive/list')
        assert response.status_code == 200


# ============ Cover Points API 测试 ============

class TestCoverPointsAPI:
    """Cover Points API 测试"""
    
    def test_get_cp_list(self, client, test_project):
        """GET /api/cp - 获取 CP 列表"""
        response = client.get(f'/api/cp?project_id={test_project["id"]}')
        assert response.status_code == 200
    
    def test_create_cp(self, client, test_project):
        """POST /api/cp - 创建 CP"""
        response = client.post('/api/cp',
                            data=json.dumps({
                                'project_id': test_project["id"],
                                'feature': f'Feature_{int(time.time())}',
                                'sub_feature': 'TestSub',
                                'cover_point': f'CP_{int(time.time())}',
                                'cover_point_details': 'Test Details'
                            }),
                            content_type='application/json')
        assert response.status_code == 200
    
    def test_update_cp(self, client, test_project):
        """PUT /api/cp/{id} - 更新 CP"""
        # 先创建
        create_resp = client.post('/api/cp',
                               data=json.dumps({
                                   'project_id': test_project["id"],
                                   'feature': f'Feature_{int(time.time())}',
                                   'sub_feature': 'Test',
                                   'cover_point': f'UpdateCP_{int(time.time())}',
                                   'cover_point_details': 'Test'
                               }),
                               content_type='application/json')
        if create_resp.status_code == 200:
            cp_id = json.loads(create_resp.data)['item']['id']
            # 更新
            update_resp = client.put(f'/api/cp/{cp_id}',
                                data=json.dumps({
                                    'project_id': test_project["id"],
                                    'feature': 'UpdatedFeature',
                                    'sub_feature': 'UpdatedSub',
                                    'cover_point': 'UpdatedCP',
                                    'cover_point_details': 'Updated Details'
                                }),
                                content_type='application/json')
            assert update_resp.status_code == 200
    
    def test_delete_cp(self, client, test_project):
        """DELETE /api/cp/{id} - 删除 CP"""
        # 先创建
        create_resp = client.post('/api/cp',
                               data=json.dumps({
                                   'project_id': test_project["id"],
                                   'feature': f'Feature_{int(time.time())}',
                                   'sub_feature': 'Test',
                                   'cover_point': f'DeleteCP_{int(time.time())}',
                                   'cover_point_details': 'Test'
                               }),
                               content_type='application/json')
        if create_resp.status_code == 200:
            cp_id = json.loads(create_resp.data)['item']['id']
            # 删除
            delete_resp = client.delete(f'/api/cp/{cp_id}?project_id={test_project["id"]}')
            assert delete_resp.status_code == 200


# ============ Test Cases API 测试 ============

class TestTestCasesAPI:
    """Test Cases API 测试"""
    
    def test_get_tc_list(self, client, test_project):
        """GET /api/tc - 获取 TC 列表"""
        response = client.get(f'/api/tc?project_id={test_project["id"]}')
        assert response.status_code == 200
    
    def test_create_tc(self, client, test_project):
        """POST /api/tc - 创建 TC"""
        response = client.post('/api/tc',
                            data=json.dumps({
                                'project_id': test_project["id"],
                                'testbench': f'TB_{int(time.time())}',
                                'category': 'Sanity',
                                'owner': 'Tester',
                                'test_name': f'TC_{int(time.time())}',
                                'scenario_details': 'Test scenario'
                            }),
                            content_type='application/json')
        assert response.status_code == 200
    
    def test_update_tc(self, client, test_project):
        """PUT /api/tc/{id} - 更新 TC"""
        # 先创建
        create_resp = client.post('/api/tc',
                              data=json.dumps({
                                  'project_id': test_project["id"],
                                  'testbench': f'TB_Upd_{int(time.time())}',
                                  'category': 'Sanity',
                                  'owner': 'Tester',
                                  'test_name': f'TC_Upd_{int(time.time())}',
                                  'scenario_details': 'Test'
                              }),
                              content_type='application/json')
        if create_resp.status_code == 200:
            tc_id = json.loads(create_resp.data)['item']['id']
            # 更新
            update_resp = client.put(f'/api/tc/{tc_id}',
                                data=json.dumps({
                                    'project_id': test_project["id"],
                                    'testbench': 'TB_Updated',
                                    'category': 'Updated',
                                    'owner': 'Updated',
                                    'test_name': 'UpdatedTC',
                                    'scenario_details': 'Updated'
                                }),
                                content_type='application/json')
            assert update_resp.status_code == 200
    
    def test_delete_tc(self, client, test_project):
        """DELETE /api/tc/{id} - 删除 TC"""
        # 先创建
        create_resp = client.post('/api/tc',
                              data=json.dumps({
                                  'project_id': test_project["id"],
                                  'testbench': f'TB_Del_{int(time.time())}',
                                  'category': 'Sanity',
                                  'owner': 'Tester',
                                  'test_name': f'TC_Del_{int(time.time())}',
                                  'scenario_details': 'Test'
                              }),
                              content_type='application/json')
        if create_resp.status_code == 200:
            tc_id = json.loads(create_resp.data)['item']['id']
            # 删除
            delete_resp = client.delete(f'/api/tc/{tc_id}?project_id={test_project["id"]}')
            assert delete_resp.status_code == 200
    
    def test_update_tc_status(self, client, test_project):
        """POST /api/tc/{id}/status - 更新状态"""
        # 先创建 TC
        create_resp = client.post('/api/tc',
                              data=json.dumps({
                                  'project_id': test_project["id"],
                                  'testbench': f'TB_Status_{int(time.time())}',
                                  'category': 'Sanity',
                                  'owner': 'Tester',
                                  'test_name': f'TC_Status_{int(time.time())}',
                                  'scenario_details': 'Test'
                              }),
                              content_type='application/json')
        if create_resp.status_code == 200:
            tc_id = json.loads(create_resp.data)['item']['id']
            
            # OPEN -> CODED
            resp1 = client.post(f'/api/tc/{tc_id}/status',
                              data=json.dumps({
                                  'project_id': test_project["id"],
                                  'status': 'CODED'
                              }),
                              content_type='application/json')
            assert resp1.status_code == 200
            
            # CODED -> FAIL
            resp2 = client.post(f'/api/tc/{tc_id}/status',
                              data=json.dumps({
                                  'project_id': test_project["id"],
                                  'status': 'FAIL'
                              }),
                              content_type='application/json')
            assert resp2.status_code == 200
            
            # FAIL -> PASS
            resp3 = client.post(f'/api/tc/{tc_id}/status',
                              data=json.dumps({
                                  'project_id': test_project["id"],
                                  'status': 'PASS'
                              }),
                              content_type='application/json')
            assert resp3.status_code == 200
    
    def test_tc_with_status_filter(self, client, test_project):
        """GET /api/tc?status=PASS - 状态过滤"""
        response = client.get(f'/api/tc?project_id={test_project["id"]}&status=PASS')
        assert response.status_code == 200
    
    def test_tc_with_sort(self, client, test_project):
        """GET /api/tc?sort_by=testbench - 排序"""
        response = client.get(f'/api/tc?project_id={test_project["id"]}&sort_by=testbench')
        assert response.status_code == 200


# ============ 统计 API 测试 ============

class TestStatsAPI:
    """统计 API 测试"""
    
    def test_get_stats(self, client, test_project):
        """GET /api/stats - 获取统计"""
        response = client.get(f'/api/stats?project_id={test_project["id"]}')
        assert response.status_code == 200


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
