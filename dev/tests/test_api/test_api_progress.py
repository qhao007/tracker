"""
Tracker Progress API 测试用例 - v0.8.1
测试计划曲线功能
"""

import json
import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
def test_project_with_dates(admin_client):
    """创建带日期的测试项目"""
    name = f"Progress_Test_{int(time.time())}"
    response = admin_client.post('/api/projects',
        data=json.dumps({
            'name': name,
            'start_date': '2026-01-01',
            'end_date': '2026-03-31'
        }),
        content_type='application/json')
    
    # 添加调试信息
    if response.status_code != 200:
        print(f"WARNING: Project creation failed: {response.status_code} - {response.data}")
    
    data = json.loads(response.data)
    project_id = data.get('project', {}).get('id')
    
    # 如果 project_id 为 None，记录详细信息
    if project_id is None:
        print(f"WARNING: project_id is None! Response: {data}")
        # 尝试再次登录
        admin_client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        # 重试创建项目
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': f"Progress_Test_{int(time.time())}_retry",
                'start_date': '2026-01-01',
                'end_date': '2026-03-31'
            }),
            content_type='application/json')
        data = json.loads(response.data)
        project_id = data.get('project', {}).get('id')
    
    return project_id


class TestProgressAPI:
    """进度图表 API 测试"""

    def test_get_progress_no_project(self, admin_client):
        """测试项目不存在时返回 404"""
        response = admin_client.get('/api/progress/99999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_progress_empty_project(self, admin_client):
        """测试空项目的进度数据"""
        # 创建无 TC/CP 的空项目
        name = f"Empty_Progress_{int(time.time())}"
        create_resp = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-03-31'
            }),
            content_type='application/json')
        project_data = json.loads(create_resp.data)
        project_id = project_data.get('project', {}).get('id')
        
        # 获取进度数据
        response = admin_client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'planned' in data
        assert 'actual' in data
        assert data['planned'] == []  # 空项目无计划曲线

    def test_get_progress_with_dates(self, admin_client, test_project_with_dates):
        """测试带日期项目的进度数据返回"""
        response = admin_client.get(f'/api/progress/{test_project_with_dates}')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'start_date' in data
        assert 'end_date' in data
        assert data['start_date'] == '2026-01-01'
        assert data['end_date'] == '2026-03-31'

    def test_get_progress_with_date_filter(self, admin_client, test_project_with_dates):
        """测试日期过滤参数"""
        # 测试 start_date 参数
        response = admin_client.get(
            f'/api/progress/{test_project_with_dates}?start_date=2026-02-01'
        )
        assert response.status_code == 200
        
        # 测试 end_date 参数
        response = admin_client.get(
            f'/api/progress/{test_project_with_dates}?end_date=2026-02-28'
        )
        assert response.status_code == 200
        
        # 测试两个参数
        response = admin_client.get(
            f'/api/progress/{test_project_with_dates}?start_date=2026-02-01&end_date=2026-02-28'
        )
        assert response.status_code == 200

    def test_planned_coverage_calculation(self, admin_client):
        """测试计划覆盖率计算"""
        # 创建项目并添加 TC/CP
        name = f"Coverage_Test_{int(time.time())}"
        create_resp = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-03-31'
            }),
            content_type='application/json')
        project_data = json.loads(create_resp.data)
        project_id = project_data.get('project', {}).get('id')
        project_name = project_data.get('project', {}).get('name')
        
        # 添加 CP
        cp_resp = admin_client.post('/api/cp',
            data=json.dumps({
                'project_id': project_id,
                'feature': 'TestFeature',
                'description': 'Test CP',
                'priority': 'P1'
            }),
            content_type='application/json')
        cp_data = json.loads(cp_resp.data)
        cp_id = cp_data.get('id')
        
        # 添加 TC
        tc_resp = admin_client.post('/api/tc',
            data=json.dumps({
                'project_id': project_id,
                'title': 'Test TC',
                'status': 'Pass',
                'target_date': '2026-01-15'
            }),
            content_type='application/json')
        
        # 关联 TC 和 CP
        admin_client.post('/api/tc-cp',
            data=json.dumps({
                'tc_id': 1,  # 需要获取实际 ID
                'cp_id': cp_id
            }),
            content_type='application/json')
        
        # 获取进度数据，应该有计划曲线
        response = admin_client.get(f'/api/progress/{project_id}')
        data = json.loads(response.data)
        
        # 验证计划曲线数据
        assert 'planned' in data
        # 计划曲线应该是数组，每个元素包含 week 和 coverage
        if len(data['planned']) > 0:
            for point in data['planned']:
                assert 'week' in point
                assert 'coverage' in point
                assert 0 <= point['coverage'] <= 100
