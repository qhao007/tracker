#!/usr/bin/env python3
"""
Tracker 冒烟测试 - stable 版本专用

仅测试核心功能，确保从 dev 迁移到 stable 时无回归。
⚠️ 注意：此测试只使用 user_data 中的数据，不修改用户真实项目！

运行命令: PYTHONPATH=. pytest tests/test_sanity.py -v
"""

import json
import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app

# stable 版本使用 user_data 目录
# Debugware_65K 的 project_id 是 2
TEST_PROJECT_ID = 2


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
    
    运行命令: PYTHONPATH=. pytest tests/test_sanity.py -v
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

    def test_get_cp_list(self, client):
        """S003: CP 列表读取"""
        response = client.get(f'/api/cp?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200

    def test_get_tc_list(self, client):
        """S004: TC 列表读取"""
        response = client.get(f'/api/tc?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200

    def test_get_stats(self, client):
        """S005: 统计 API"""
        response = client.get(f'/api/stats?project_id={TEST_PROJECT_ID}')
        assert response.status_code == 200


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
