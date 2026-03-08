"""
用户反馈 API 测试 - v0.9.1
测试 POST /api/feedback 接口
"""
import json
import pytest
import sys
import os
import glob
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def admin_client(client):
    """管理员登录会话"""
    client.post('/api/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json')
    return client


class TestFeedbackAPI:
    """反馈 API 测试"""

    def test_submit_feedback_success(self, admin_client):
        """API-FB-001: 提交反馈接口 - 成功"""
        response = admin_client.post('/api/feedback',
            data=json.dumps({
                'type': 'bug',
                'title': '测试反馈标题',
                'description': '这是一个测试反馈描述'
            }),
            content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['message'] == '反馈提交成功'
        assert 'data' in data
        assert data['data']['type'] == 'bug'
        assert data['data']['title'] == '测试反馈标题'
        assert data['data']['user'] == 'admin'

    def test_submit_feedback_unauthenticated(self, client):
        """API-FB-002: 提交反馈接口 - 未登录"""
        response = client.post('/api/feedback',
            data=json.dumps({
                'type': 'bug',
                'title': '测试反馈标题',
                'description': '这是一个测试反馈描述'
            }),
            content_type='application/json')

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_submit_feedback_missing_type(self, admin_client):
        """API-FB-003: 提交反馈接口 - 缺少类型"""
        response = admin_client.post('/api/feedback',
            data=json.dumps({
                'title': '测试反馈标题',
                'description': '这是一个测试反馈描述'
            }),
            content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_submit_feedback_invalid_type(self, admin_client):
        """API-FB-003: 提交反馈接口 - 无效类型"""
        response = admin_client.post('/api/feedback',
            data=json.dumps({
                'type': 'invalid_type',
                'title': '测试反馈标题',
                'description': '这是一个测试反馈描述'
            }),
            content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_submit_feedback_missing_title(self, admin_client):
        """API-FB-003: 提交反馈接口 - 缺少标题"""
        response = admin_client.post('/api/feedback',
            data=json.dumps({
                'type': 'bug',
                'description': '这是一个测试反馈描述'
            }),
            content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_submit_feedback_missing_description(self, admin_client):
        """API-FB-003: 提交反馈接口 - 缺少描述"""
        response = admin_client.post('/api/feedback',
            data=json.dumps({
                'type': 'bug',
                'title': '测试反馈标题'
            }),
            content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_submit_feedback_empty_body(self, admin_client):
        """API-FB-003: 提交反馈接口 - 空请求体"""
        response = admin_client.post('/api/feedback',
            data=json.dumps({}),
            content_type='application/json')

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_submit_feedback_all_types(self, admin_client):
        """测试所有反馈类型"""
        for feedback_type in ['bug', 'feature', 'optimization']:
            response = admin_client.post('/api/feedback',
                data=json.dumps({
                    'type': feedback_type,
                    'title': f'测试{feedback_type}类型',
                    'description': f'这是{feedback_type}类型的测试反馈'
                }),
                content_type='application/json')

            assert response.status_code == 200
            data = response.get_json()
            assert data['data']['type'] == feedback_type

    def test_feedback_file_created(self, admin_client):
        """API-COV-002: 验证反馈提交后文件正确生成"""
        import glob
        from pathlib import Path

        # 测试模式下 DATA_DIR 是 dev/data
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_dir = os.path.dirname(base_dir)  # 回到 dev 目录
        feedback_dir = Path(base_dir) / 'data' / 'feedbacks'

        if feedback_dir.exists():
            files_before = set(glob.glob(str(feedback_dir / 'FEEDBACK_*.json')))
        else:
            files_before = set()

        # 提交反馈
        response = admin_client.post('/api/feedback',
            data=json.dumps({
                'type': 'bug',
                'title': '文件生成测试',
                'description': '验证文件是否实际生成'
            }),
            content_type='application/json')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

        # 验证文件已生成
        files_after = set(glob.glob(str(feedback_dir / 'FEEDBACK_*.json')))
        new_files = files_after - files_before

        assert len(new_files) > 0, "反馈文件未生成"

        # 验证最新文件内容
        latest_file = max(new_files, key=lambda p: Path(p).stat().st_mtime)
        with open(latest_file) as f:
            file_data = json.load(f)

        assert file_data['type'] == 'bug'
        assert file_data['title'] == '文件生成测试'
        assert 'created_at' in file_data
