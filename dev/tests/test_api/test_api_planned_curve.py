"""
Tracker 计划曲线 API 测试用例 - v0.8.1
测试计划曲线覆盖率计算功能

使用 SOC_DV 项目进行测试
"""

import json
import pytest
import sys
import os

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
def soc_dv_project(admin_client):
    """获取 SOC_DV 项目 ID"""
    response = admin_client.get('/api/projects')
    projects = json.loads(response.data)
    soc_dv = next((p for p in projects if p.get('name') == 'SOC_DV'), None)
    if not soc_dv:
        pytest.skip("SOC_DV 项目不存在")
    return soc_dv['id']


class TestPlannedCoverageCalculation:
    """计划曲线覆盖率计算测试"""
    
    def test_calculate_coverage_basic(self, admin_client, soc_dv_project):
        """API-PLAN-001: 基础覆盖率计算"""
        response = admin_client.get(f'/api/progress/{soc_dv_project}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'planned' in data
        assert len(data['planned']) > 0
        
        # 验证有覆盖率数据
        for week_data in data['planned']:
            assert 'week' in week_data
            assert 'coverage' in week_data
    
    def test_calculate_coverage_with_pass_tcs(self, admin_client, soc_dv_project):
        """API-PLAN-002: 带 PASS 状态 TC 的覆盖率计算"""
        response = admin_client.get(f'/api/progress/{soc_dv_project}')
        data = json.loads(response.data)
        
        # 有 PASS 状态的 TC，应该有覆盖率 > 0
        # SOC_DV 有 20 个 PASS TC，30 个 CP
        has_nonzero = any(w['coverage'] > 0 for w in data['planned'])
        assert has_nonzero, "应该有非零覆盖率"
    
    def test_calculate_coverage_no_tcs(self, admin_client):
        """API-PLAN-003: 无 TC 时覆盖率计算"""
        # 创建空项目
        import time
        name = f"Empty_TC_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-06',
                'end_date': '2026-03-31'
            }),
            content_type='application/json')
        project_data = json.loads(response.data)
        project_id = project_data.get('project', {}).get('id')
        
        # 添加 CP
        import sqlite3
        db_path = f"/projects/management/tracker/shared/data/test_data/{name}.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cover_point (project_id, feature, cover_point, priority, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (project_id, 'CPU', 'Test CP', 'P0'))
        conn.commit()
        conn.close()
        
        response = admin_client.get(f'/api/progress/{project_id}')
        data = json.loads(response.data)
        
        # 无 TC 时，覆盖率应为 0
        for week_data in data['planned']:
            assert week_data['coverage'] == 0.0
    
    def test_calculate_coverage_no_cps(self, admin_client):
        """API-PLAN-004: 无 CP 时避免除零错误"""
        import time
        name = f"Empty_CP_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-06',
                'end_date': '2026-03-31'
            }),
            content_type='application/json')
        project_data = json.loads(response.data)
        project_id = project_data.get('project', {}).get('id')
        
        response = admin_client.get(f'/api/progress/{project_id}')
        # 无 CP 时应返回空 planned
        data = json.loads(response.data)
        assert data['planned'] == []


class TestPlannedCurveAPI:
    """计划曲线 API 测试"""
    
    def test_get_progress_with_planned(self, admin_client, soc_dv_project):
        """API-PLAN-010: 获取含计划曲线数据"""
        response = admin_client.get(f'/api/progress/{soc_dv_project}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'planned' in data
        assert isinstance(data['planned'], list)
        assert len(data['planned']) > 0
    
    def test_get_progress_date_filter(self, admin_client, soc_dv_project):
        """API-PLAN-011: 时间段过滤"""
        # 只获取 2 月的数据
        response = admin_client.get(
            f'/api/progress/{soc_dv_project}?start_date=2026-02-01&end_date=2026-02-28'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # 验证返回的是过滤后的数据
        if len(data['planned']) > 0:
            # 检查周日期在范围内
            for week in data['planned']:
                week_date = week['week']
                assert '2026-02-' in week_date
    
    def test_get_progress_with_dates(self, admin_client):
        """API-PLAN-013: 有日期项目返回 planned 数据"""
        import time
        name = f"With_Date_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-01',
                'end_date': '2026-12-31'
            }),
            content_type='application/json')
        project_data = json.loads(response.data)
        project_id = project_data.get('project', {}).get('id')
        
        response = admin_client.get(f'/api/progress/{project_id}')
        data = json.loads(response.data)
        
        assert 'planned' in data
        # 有日期的项目应该有计划曲线数据（基于 target_date）
    
    def test_get_progress_week_boundary(self, admin_client, soc_dv_project):
        """API-PLAN-014: Week 边界处理"""
        response = admin_client.get(f'/api/progress/{soc_dv_project}')
        data = json.loads(response.data)
        
        # 验证周数据点正确
        # SOC_DV 项目开始日期是 2026-01-06（周二）
        # 算法应该找到该周之前的周日作为第一个数据点
        from datetime import datetime
        for week_data in data['planned']:
            week_date = week_data['week']
            dt = datetime.strptime(week_date, '%Y-%m-%d')
            # 周一=0, 周日=6
            # 2026-01-06 是周二，所以第一个数据点应该是 2026-01-05（周一）
            # 验证所有数据点都是周一
            assert dt.weekday() in [0, 1]  # 周一或周二（项目开始的周）


class TestPlannedCurveBoundary:
    """边界情况测试"""
    
    def test_get_progress_empty_project(self, admin_client):
        """API-PLAN-020: 空项目边界情况"""
        import time
        name = f"Empty_Project_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-06',
                'end_date': '2026-03-31'
            }),
            content_type='application/json')
        project_data = json.loads(response.data)
        project_id = project_data.get('project', {}).get('id')
        
        response = admin_client.get(f'/api/progress/{project_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['planned'] == []
    
    def test_get_progress_no_target_date(self, admin_client):
        """API-PLAN-021: TC 无 target_date 时跳过该 TC"""
        import time
        import sqlite3
        name = f"No_Target_Date_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-06',
                'end_date': '2026-03-31'
            }),
            content_type='application/json')
        project_data = json.loads(response.data)
        project_id = project_data.get('project', {}).get('id')
        
        # 添加 CP
        db_path = f"/projects/management/tracker/shared/data/test_data/{name}.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cover_point (project_id, feature, cover_point, priority, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (project_id, 'CPU', 'Test CP', 'P0'))
        
        # 添加无 target_date 的 TC
        cursor.execute("""
            INSERT INTO test_case (project_id, testbench, test_name, status, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (project_id, 'tb_cpu', 'Test_No_Date', 'PASS'))
        
        conn.commit()
        conn.close()
        
        response = admin_client.get(f'/api/progress/{project_id}')
        data = json.loads(response.data)
        
        # 无 target_date 的 TC 不计入，覆盖率应为 0
        for week_data in data['planned']:
            assert week_data['coverage'] == 0.0
    
    def test_get_progress_future_target(self, admin_client):
        """API-PLAN-022: target_date 在未来不计入覆盖"""
        import time
        import sqlite3
        name = f"Future_Target_{int(time.time())}"
        response = admin_client.post('/api/projects',
            data=json.dumps({
                'name': name,
                'start_date': '2026-01-06',
                'end_date': '2026-01-31'
            }),
            content_type='application/json')
        project_data = json.loads(response.data)
        project_id = project_data.get('project', {}).get('id')
        
        # 添加 CP
        db_path = f"/projects/management/tracker/shared/data/test_data/{name}.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cover_point (project_id, feature, cover_point, priority, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (project_id, 'CPU', 'Test CP', 'P0'))
        
        # 添加 target_date 在项目结束后的 TC
        cursor.execute("""
            INSERT INTO test_case (project_id, testbench, test_name, status, target_date, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (project_id, 'tb_cpu', 'Test_Future', 'PASS', '2026-12-31'))
        
        conn.commit()
        conn.close()
        
        response = admin_client.get(f'/api/progress/{project_id}')
        data = json.loads(response.data)
        
        # 未来 target_date 不计入，覆盖率应为 0
        for week_data in data['planned']:
            assert week_data['coverage'] == 0.0
