"""
导出材料包 API 测试 - v0.14.0

测试导出项目材料包 API 的功能：
- 权限控制测试
- 导出内容验证
- 边界条件测试
- 异常场景测试

运行命令:
    cd dev && PYTHONPATH=. pytest tests/test_api/test_export_package.py -v
"""

import json
import pytest
import sys
import os
import time
import zipfile
import io

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
def user_client(client):
    """创建已登录的普通用户客户端"""
    # 先尝试登录，如果失败则创建用户后重试
    response = client.post('/api/auth/login',
        data=json.dumps({'username': 'user', 'password': 'user123'}),
        content_type='application/json')
    if response.status_code == 401:
        # 用户不存在，先创建
        app = create_app(testing=True)
        with app.app_context():
            from app import auth
            auth.init_users_db()
            auth.create_user('user', 'user123', 'user')
        # 重试登录
        client.post('/api/auth/login',
            data=json.dumps({'username': 'user', 'password': 'user123'}),
            content_type='application/json')
    return client


@pytest.fixture
def guest_client(client):
    """创建已登录的访客客户端"""
    client.post('/api/auth/guest-login',
        data=json.dumps({}),
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

        name = f"Export_Test_{int(time.time())}"

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


@pytest.fixture(scope='module')
def empty_project():
    """创建空的测试项目（无 TC/CP）"""
    app = create_app(testing=True)
    with app.test_client() as client:
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"Empty_Export_Test_{int(time.time())}"

        response = client.post('/api/projects',
                              data=json.dumps({'name': name, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
                              content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            project_id = data['project']['id']
            yield {'id': project_id, 'name': name}

            client.delete(f"/api/projects/{project_id}")
        else:
            pytest.skip("无法创建空项目")


@pytest.fixture(scope='module')
def large_project():
    """创建大型测试项目（500+ TC）"""
    app = create_app(testing=True)
    with app.test_client() as client:
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"Large_Export_Test_{int(time.time())}"

        response = client.post('/api/projects',
                              data=json.dumps({'name': name, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
                              content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            project_id = data['project']['id']

            # 创建 500+ TC（分批创建以避免超时）
            batch_size = 50
            total_tc = 520
            for batch_start in range(0, total_tc, batch_size):
                batch_data = []
                for i in range(batch_start, min(batch_start + batch_size, total_tc)):
                    batch_data.append({
                        'project_id': project_id,
                        'testbench': f'TB_{i // batch_size}',
                        'test_name': f'Large_TC_{i}',
                        'dv_milestone': 'DV1.0',
                        'status': 'OPEN'
                    })

                # 批量创建 TC
                for tc_data in batch_data:
                    client.post('/api/tc', json=tc_data)

            yield {'id': project_id, 'name': name, 'tc_count': total_tc}

            # 清理
            client.delete(f"/api/projects/{project_id}")
        else:
            pytest.skip("无法创建大型项目")


@pytest.fixture(scope='module')
def project_with_special_chars():
    """创建名称含特殊字符的项目"""
    app = create_app(testing=True)
    with app.test_client() as client:
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        # 名称含空格和特殊字符
        name = f"Special@Test#Project_{int(time.time())}"

        response = client.post('/api/projects',
                              data=json.dumps({'name': name, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
                              content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            project_id = data['project']['id']
            yield {'id': project_id, 'name': name}

            client.delete(f"/api/projects/{project_id}")
        else:
            pytest.skip("无法创建特殊字符项目")


@pytest.fixture(scope='module')
def project_with_wiki():
    """创建有 Wiki 内容的项目"""
    app = create_app(testing=True)
    with app.test_client() as client:
        client.post('/api/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')

        name = f"Wiki_Export_Test_{int(time.time())}"

        response = client.post('/api/projects',
                              data=json.dumps({'name': name, 'start_date': '2026-01-01', 'end_date': '2026-12-31'}),
                              content_type='application/json')

        if response.status_code == 200:
            data = json.loads(response.data)
            project_id = data['project']['id']

            # 创建 Wiki 目录和文件 - 使用 app.config['DATA_DIR'] 确保路径正确
            wiki_base = os.path.join(app.config['DATA_DIR'], 'wiki')
            project_wiki_dir = os.path.join(wiki_base, str(project_id))
            pages_dir = os.path.join(project_wiki_dir, 'pages')
            os.makedirs(pages_dir, exist_ok=True)

            # 创建 Wiki 页面
            page_content = """<!DOCTYPE html>
<html>
<head><title>Test Page</title></head>
<body><h1>Test Wiki Page</h1><p>This is a test page.</p></body>
</html>"""
            with open(os.path.join(pages_dir, 'test_page.html'), 'w', encoding='utf-8') as f:
                f.write(page_content)

            # 创建 index.json
            index_data = {"pages": [{"slug": "test_page", "filename": "test_page.html"}]}
            with open(os.path.join(project_wiki_dir, 'index.json'), 'w', encoding='utf-8') as f:
                json.dump(index_data, f)

            # 创建 changes_index.json
            changes_data = {"changes": [{"date": "2026-05-12", "message": "Initial commit"}]}
            with open(os.path.join(project_wiki_dir, 'changes_index.json'), 'w', encoding='utf-8') as f:
                json.dump(changes_data, f)

            yield {'id': project_id, 'name': name}

            # 清理
            client.delete(f"/api/projects/{project_id}")

            # 清理 Wiki 目录
            import shutil
            if os.path.exists(project_wiki_dir):
                shutil.rmtree(project_wiki_dir)
        else:
            pytest.skip("无法创建 Wiki 项目")


def validate_zip_content(zip_data, expected_files):
    """验证 ZIP 文件内容"""
    zip_file = zipfile.ZipFile(io.BytesIO(zip_data))
    actual_files = set(zip_file.namelist())

    for expected_file in expected_files:
        if expected_file not in actual_files:
            raise AssertionError(f"Missing expected file: {expected_file}")

    return True


class TestExportPackagePermissions:
    """测试导出材料包权限控制"""

    def test_export_package_as_admin(self, admin_client, test_project):
        """EXP-API-001: 管理员导出项目材料包"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        assert response.content_type == 'application/zip'
        assert 'project_export_' in response.headers.get('Content-Disposition', '')
        assert '.zip' in response.headers.get('Content-Disposition', '')

    def test_export_package_as_user(self, user_client, test_project):
        """EXP-API-002: 普通用户调用导出 API"""
        response = user_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data

    def test_export_package_as_guest(self, guest_client, test_project):
        """EXP-API-003: 访客调用导出 API"""
        response = guest_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data

    def test_export_package_unauthenticated(self, client, test_project):
        """EXP-API-004: 未登录调用导出 API"""
        response = client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_export_nonexistent_project(self, admin_client):
        """EXP-API-005: 导出不存在的项目"""
        response = admin_client.get('/api/export/project/99999/package')

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data.get('code') == 'PROJECT_NOT_FOUND'


class TestExportPackageContent:
    """测试导出材料包内容"""

    def test_export_package_content(self, admin_client, test_project):
        """EXP-API-006: 验证 ZIP 包含所有预期文件"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data

        expected_files = [
            'README.md',
            'project_overview.md',
            'project_overview.xlsx',
            'coverage_trend.md',
            'coverage_trend.xlsx',
            'tc_cp_statistics.md',
            'tc_cp_statistics.xlsx',
            'dashboard_feature_matrix.md',
            'dashboard_feature_matrix.xlsx',
            'dashboard_owner_distribution.md',
            'dashboard_owner_distribution.xlsx',
            'dashboard_coverage_matrix.md',
            'dashboard_coverage_matrix.xlsx',
            'feature_list.md',
            'feature_list.xlsx',
            'snapshots.md',
            'snapshots.xlsx',
        ]

        validate_zip_content(zip_data, expected_files)

    def test_export_project_overview(self, admin_client, test_project):
        """EXP-API-007: 验证项目概览文件"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 project_overview.md 包含项目信息
        overview_md = zip_file.read('project_overview.md').decode('utf-8')
        assert test_project['name'] in overview_md
        assert 'project_overview.md' in zip_file.namelist()

        # 验证 project_overview.xlsx 存在
        assert 'project_overview.xlsx' in zip_file.namelist()

    def test_export_coverage_trend(self, admin_client, test_project):
        """EXP-API-008: 验证覆盖率数据"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 coverage_trend.md 包含历史快照表头
        trend_md = zip_file.read('coverage_trend.md').decode('utf-8')
        assert '| 日期 | 覆盖率 |' in trend_md

        # 验证 coverage_trend.xlsx 存在
        assert 'coverage_trend.xlsx' in zip_file.namelist()

    def test_export_tc_cp_statistics(self, admin_client, test_project):
        """EXP-API-009: 验证 TC/CP 统计"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 tc_cp_statistics.md 包含统计表
        stats_md = zip_file.read('tc_cp_statistics.md').decode('utf-8')
        assert '## TC 状态分布' in stats_md
        assert '## TC Owner 分布' in stats_md
        assert '## CP 按 Feature 分组' in stats_md

        # 验证 tc_cp_statistics.xlsx 存在
        assert 'tc_cp_statistics.xlsx' in zip_file.namelist()

    def test_export_dashboard_data(self, admin_client, test_project):
        """EXP-API-010: 验证 Dashboard 数据"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 Dashboard 相关文件
        assert 'dashboard_feature_matrix.md' in zip_file.namelist()
        assert 'dashboard_feature_matrix.xlsx' in zip_file.namelist()
        assert 'dashboard_owner_distribution.md' in zip_file.namelist()
        assert 'dashboard_owner_distribution.xlsx' in zip_file.namelist()
        assert 'dashboard_coverage_matrix.md' in zip_file.namelist()
        assert 'dashboard_coverage_matrix.xlsx' in zip_file.namelist()

    def test_export_feature_list(self, admin_client, test_project):
        """EXP-API-011: 验证 Feature 列表"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 feature_list.md 包含 Feature 统计
        feature_md = zip_file.read('feature_list.md').decode('utf-8')
        assert '## 按 Feature 统计汇总' in feature_md

        # 验证 feature_list.xlsx 存在
        assert 'feature_list.xlsx' in zip_file.namelist()

    def test_export_snapshots(self, admin_client, test_project):
        """EXP-API-012: 验证快照历史"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 snapshots.md 包含快照历史
        snapshots_md = zip_file.read('snapshots.md').decode('utf-8')
        assert '## 所有历史快照' in snapshots_md

        # 验证 snapshots.xlsx 存在
        assert 'snapshots.xlsx' in zip_file.namelist()

    def test_export_wiki_content(self, admin_client, project_with_wiki):
        """EXP-API-013: 验证 Wiki 内容"""
        response = admin_client.get(f'/api/export/project/{project_with_wiki["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 Wiki 文件
        assert 'wiki/index.json' in zip_file.namelist()
        assert 'wiki/changes_index.json' in zip_file.namelist()
        assert 'wiki/pages/test_page.html' in zip_file.namelist()

    def test_export_filename_format(self, admin_client, test_project):
        """EXP-API-014: 验证文件名格式"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200

        content_disp = response.headers.get('Content-Disposition', '')
        # 文件名格式: project_export_{name}_{YYYYMMDD_HHMMSS}.zip
        assert 'project_export_' in content_disp
        assert '.zip' in content_disp
        # 验证日期格式 (YYYYMMDD_HHMMSS)
        import re
        date_pattern = r'\d{8}_\d{6}'
        assert re.search(date_pattern, content_disp)


class TestExportPackageBoundary:
    """测试导出材料包边界条件"""

    def test_export_special_chars_in_project_name(self, admin_client, project_with_special_chars):
        """EXP-API-015: 项目名含特殊字符"""
        response = admin_client.get(f'/api/export/project/{project_with_special_chars["id"]}/package')

        assert response.status_code == 200

        content_disp = response.headers.get('Content-Disposition', '')
        # 空格替换为 _，特殊字符移除
        assert 'Special_Test_Project_' in content_disp or 'SpecialTestProject_' in content_disp
        assert '@' not in content_disp
        assert '#' not in content_disp

    def test_export_empty_project(self, admin_client, empty_project):
        """EXP-API-016: 空项目（无 TC/CP）"""
        response = admin_client.get(f'/api/export/project/{empty_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证所有文件都存在但内容可能为空
        expected_files = [
            'project_overview.md',
            'project_overview.xlsx',
            'coverage_trend.md',
            'tc_cp_statistics.md',
            'dashboard_feature_matrix.md',
            'dashboard_owner_distribution.md',
            'dashboard_coverage_matrix.md',
            'feature_list.md',
            'snapshots.md',
        ]

        for expected_file in expected_files:
            assert expected_file in zip_file.namelist(), f"Missing: {expected_file}"

    def test_export_large_project(self, admin_client, large_project):
        """EXP-API-017: 大项目（500+ TC）"""
        start_time = time.time()
        response = admin_client.get(f'/api/export/project/{large_project["id"]}/package')
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        # 导出时间 < 60秒
        assert elapsed_time < 60, f"Export took {elapsed_time:.2f}s, expected < 60s"

        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))
        # 验证 ZIP 可正常解压
        assert len(zip_file.namelist()) > 0


class TestExportPackageException:
    """测试导出材料包异常场景"""

    def test_export_invalid_project_id(self, admin_client):
        """EXP-API-018: 无效项目 ID"""
        response = admin_client.get('/api/export/project/invalid_id/package')

        # Flask 路由会返回 404，因为 project_id 类型不匹配
        assert response.status_code == 404

    def test_export_without_wiki(self, admin_client, test_project):
        """EXP-API-019: 项目无 Wiki"""
        response = admin_client.get(f'/api/export/project/{test_project["id"]}/package')

        assert response.status_code == 200
        zip_data = response.data
        zip_file = zipfile.ZipFile(io.BytesIO(zip_data))

        # 验证 ZIP 中没有 wiki/ 目录或 wiki/ 目录为空
        wiki_files = [f for f in zip_file.namelist() if f.startswith('wiki/')]
        # 如果项目没有 Wiki，ZIP 中不应该包含 wiki/ 目录或包含空目录
        # 根据规格书，无 Wiki 时应该跳过，所以这里验证 wiki/ 目录不存在
        assert len(wiki_files) == 0 or not any(f.endswith('.html') for f in wiki_files)
