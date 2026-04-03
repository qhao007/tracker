#!/usr/bin/env python3
"""
Tracker Dashboard API 测试用例 - v0.11.0
测试 GET /api/dashboard/stats 接口
"""

import json
import pytest
import sys
import os
import time

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

# 使用已存在的测试项目 ID
TEST_PROJECT_ID = 5  # SOC_DV 项目


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


# ============ Dashboard API 测试 ============

class TestDashboardStatsAPI:
    """Dashboard Stats API 测试 (v0.11.0)"""

    def test_api_dash_001_get_dashboard_stats_returns_correct_structure(self, admin_client):
        """API-DASH-001: GET /api/dashboard/stats 返回正确数据结构"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data

        # 验证顶层结构
        dashboard_data = data['data']
        assert 'overview' in dashboard_data
        assert 'by_feature' in dashboard_data
        assert 'by_priority' in dashboard_data
        assert 'trend' in dashboard_data
        assert 'top_uncovered' in dashboard_data
        assert 'recent_activity' in dashboard_data

    def test_api_dash_002_overview_total_cp_count(self, admin_client):
        """API-DASH-002: overview.total_cp 正确统计项目 CP 总数"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 total_cp 存在且为非负整数
        assert 'total_cp' in overview
        assert isinstance(overview['total_cp'], int)
        assert overview['total_cp'] >= 0

    def test_api_dash_003_overview_covered_cp_count(self, admin_client):
        """API-DASH-003: overview.covered_cp 正确统计已覆盖 CP (有 PASS TC)"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 covered_cp 存在且为非负整数
        assert 'covered_cp' in overview
        assert isinstance(overview['covered_cp'], int)
        assert overview['covered_cp'] >= 0

        # covered_cp 不应超过 total_cp
        assert overview['covered_cp'] <= overview['total_cp']

    def test_api_dash_004_overview_unlinked_cp_count(self, admin_client):
        """API-DASH-004: overview.unlinked_cp 正确统计未关联 CP"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 unlinked_cp 存在且为非负整数
        assert 'unlinked_cp' in overview
        assert isinstance(overview['unlinked_cp'], int)
        assert overview['unlinked_cp'] >= 0

    def test_api_dash_005_overview_coverage_rate_calculation(self, admin_client):
        """API-DASH-005: overview.coverage_rate 正确计算覆盖率百分比"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        overview = data['data']['overview']

        # 验证 coverage_rate 存在且格式正确
        assert 'coverage_rate' in overview
        assert isinstance(overview['coverage_rate'], (int, float))
        assert overview['coverage_rate'] >= 0
        assert overview['coverage_rate'] <= 100

        # 验证覆盖率计算逻辑: covered_cp / total_cp * 100
        if overview['total_cp'] > 0:
            expected_rate = round((overview['covered_cp'] / overview['total_cp']) * 100, 1)
            assert overview['coverage_rate'] == expected_rate

    def test_api_dash_006_by_feature_grouping(self, admin_client):
        """API-DASH-006: by_feature 按 feature 分组统计正确"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        by_feature = data['data']['by_feature']

        # 验证 by_feature 是数组
        assert isinstance(by_feature, list)

        # 每个 feature 条目应包含必要字段
        for item in by_feature:
            assert 'feature' in item
            assert 'total' in item
            assert 'covered' in item
            assert 'rate' in item
            assert isinstance(item['total'], int)
            assert isinstance(item['covered'], int)
            assert isinstance(item['rate'], (int, float))
            assert item['total'] >= 0
            assert item['covered'] >= 0
            assert item['covered'] <= item['total']
            assert 0 <= item['rate'] <= 100

    def test_api_dash_007_by_priority_grouping(self, admin_client):
        """API-DASH-007: by_priority 按 priority 分组统计正确"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        by_priority = data['data']['by_priority']

        # 验证 by_priority 包含 P0, P1, P2
        assert 'P0' in by_priority
        assert 'P1' in by_priority
        assert 'P2' in by_priority

        # 每个 priority 条目应包含必要字段
        for p in ['P0', 'P1', 'P2']:
            item = by_priority[p]
            assert 'total' in item
            assert 'covered' in item
            assert 'rate' in item
            assert isinstance(item['total'], int)
            assert isinstance(item['covered'], int)
            assert isinstance(item['rate'], (int, float))
            assert item['total'] >= 0
            assert item['covered'] >= 0
            assert item['covered'] <= item['total']
            assert 0 <= item['rate'] <= 100

    def test_api_dash_008_trend_data_format(self, admin_client):
        """API-DASH-008: trend 返回最近7天的覆盖率数据"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        trend = data['data']['trend']

        # 验证 trend 是数组
        assert isinstance(trend, list)

        # trend 最多7天数据
        assert len(trend) <= 7

        # 每个 trend 条目应包含必要字段
        for item in trend:
            assert 'date' in item
            assert 'rate' in item
            assert isinstance(item['rate'], (int, float))
            assert item['rate'] >= 0
            assert item['rate'] <= 100

    def test_api_dash_009_top_uncovered_ordering(self, admin_client):
        """API-DASH-009: top_uncovered 返回按 priority 排序的未覆盖 CP"""
        response = admin_client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        top_uncovered = data['data']['top_uncovered']

        # 验证 top_uncovered 是数组
        assert isinstance(top_uncovered, list)

        # 最多5条
        assert len(top_uncovered) <= 5

        # 每个条目应包含必要字段
        for item in top_uncovered:
            assert 'id' in item
            assert 'name' in item
            assert 'priority' in item
            assert 'feature' in item
            assert item['priority'] in ['P0', 'P1', 'P2']

    def test_api_dash_010_unauthorized_access(self, client):
        """API-DASH-010: 未登录访问返回 401"""
        response = client.get(f'/api/dashboard/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 401

    def test_api_dash_011_nonexistent_project(self, admin_client):
        """API-DASH-011: project_id 不存在返回 404"""
        # 使用一个大概率不存在的项目 ID
        response = admin_client.get('/api/dashboard/stats?project_id=99999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
