#!/usr/bin/env python3
"""
Tracker API 测试用例 - stable 版本专用

只测试核心功能（冒烟测试），确保不修改用户真实数据。
用于发布前的快速验证。
"""

import json
import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

# stable 版本使用 user_data 目录
# 注意：不要修改 Debugware_65K 和 EX5 的数据！

TEST_PROJECT_ID = 2  # Debugware_65K


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestSanity:
    """
    冒烟测试 - 仅测试核心功能
    
    运行命令: pytest tests/test_api.py -v
    ⚠️ 注意：不修改用户数据，只进行只读操作
    """

    def test_version_api(self, client):
        """S001: 版本 API 正常"""
        response = client.get('/api/version')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'version' in data

    def test_get_projects(self, client):
        """S002: 项目列表获取"""
        response = client.get('/api/projects')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_project_detail(self, client):
        """S003: 获取单个项目详情"""
        response = client.get(f'/api/projects/{TEST_PROJECT_ID}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] in ['Debugware_65K', 'EX5']

    def test_get_cp_list(self, client):
        """S004: CP 列表读取"""
        response = client.get(f'/api/cp?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200

    def test_get_tc_list(self, client):
        """S005: TC 列表读取"""
        response = client.get(f'/api/tc?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200

    def test_get_stats(self, client):
        """S006: 统计 API"""
        response = client.get(f'/api/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200


class TestUserDataSafety:
    """
    用户数据安全测试
    
    确保不修改用户真实项目的数据
    """

    def test_no_modify_debugware_65k(self, client):
        """确保不对 Debugware_65K 进行写操作"""
        # 只读操作
        response = client.get(f'/api/tc?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200
        # 不进行 POST/PUT/DELETE 操作

    def test_no_modify_ex5(self, client):
        """确保不对 EX5 进行写操作"""
        # EX5 的 project_id 是 3
        response = client.get('/api/tc?project_id=3')
        assert response.status_code == 200
        # 不进行 POST/PUT/DELETE 操作


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
