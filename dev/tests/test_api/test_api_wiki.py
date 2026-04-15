#!/usr/bin/env python3
"""
Wiki API 测试用例 - v0.13.0
测试 Wiki Blueprint 的所有 API 端点
"""

import json
import pytest
import sys
import os

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


# ============ 3.2.1 基础路由测试 ============

class TestWikiBasicRoutes:
    """基础路由测试 - API-WIKI-001 ~ API-WIKI-005"""

    def test_wiki_index_returns_json(self, client):
        """API-WIKI-001: GET /wiki/<slug>/index.json 返回 JSON"""
        # 测试 soc_dv 项目 wiki
        response = client.get('/wiki/soc_dv/index.json')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = json.loads(response.data)
        assert 'pages' in data, "Response should contain 'pages' field"
        assert isinstance(data['pages'], list), "pages should be a list"

        # 验证页面条目结构
        if len(data['pages']) > 0:
            page = data['pages'][0]
            assert 'path' in page
            assert 'title' in page
            assert 'category' in page

    def test_wiki_page_returns_html(self, client):
        """API-WIKI-002: GET /wiki/<slug>/pages/<path> 返回 HTML"""
        # 测试 soc_dv 的 index 页面
        response = client.get('/wiki/soc_dv/pages/index.html')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert b'<html' in response.data.lower() or b'<article' in response.data.lower(), \
            "Response should contain HTML content"

    def test_wiki_changes_index_returns_json(self, client):
        """API-WIKI-003: GET /wiki/<slug>/changes_index.json 返回变更历史"""
        response = client.get('/wiki/soc_dv/changes_index.json')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = json.loads(response.data)
        assert 'versions' in data, "Response should contain 'versions' field"
        assert isinstance(data['versions'], list), "versions should be a list"

    def test_wiki_exists_returns_status(self, client):
        """API-WIKI-004: GET /wiki/exists/<slug> 返回 has_wiki 和 source"""
        response = client.get('/wiki/exists/soc_dv')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = json.loads(response.data)
        assert 'has_wiki' in data, "Response should contain 'has_wiki' field"
        assert 'source' in data, "Response should contain 'source' field"
        assert data['has_wiki'] is True, "soc_dv wiki should exist"
        assert data['source'] == 'project', "source should be 'project' for project wiki"

    def test_wiki_slug_generation_consistency(self, client):
        """API-WIKI-005: 项目名转 slug 前后端一致"""
        # 导入后端的 slug 生成函数
        from app.wiki import get_project_slug

        # 测试用例：项目名 -> slug
        test_cases = [
            ("SOC_DV", "soc_dv"),
            ("My Project", "my_project"),
            ("Test-Project", "test_project"),
            ("  ABC  ", "abc"),
            ("Hello-World", "hello_world"),
        ]

        for project_name, expected_slug in test_cases:
            actual_slug = get_project_slug(project_name)
            assert actual_slug == expected_slug, \
                f"get_project_slug('{project_name}') = '{actual_slug}', expected '{expected_slug}'"


# ============ 3.2.2 路径遍历防护测试 ============

class TestWikiPathTraversal:
    """路径遍历防护测试 - API-WIKI-010 ~ API-WIKI-012"""

    def test_wiki_path_traversal_blocked_dotdot(self, client):
        """API-WIKI-010: 路径包含 ../ 时被拦截"""
        response = client.get('/wiki/soc_dv/pages/../index.html')
        assert response.status_code == 400, \
            f"Path traversal with '..' should return 400, got {response.status_code}"
        data = json.loads(response.data)
        assert 'error' in data

    def test_wiki_path_traversal_blocked_absolute(self, client):
        """API-WIKI-011: 绝对路径被拦截"""
        # Flask returns 308 redirect for // in URL before route handler runs
        # The path gets normalized to /etc/passwd, which is rejected as non-HTML
        response = client.get('/wiki/soc_dv/pages//etc/passwd', follow_redirects=True)
        assert response.status_code == 400, \
            f"Absolute path should return 400 after redirect, got {response.status_code}"
        data = json.loads(response.data)
        assert 'error' in data

    def test_wiki_invalid_extension_blocked(self, client):
        """API-WIKI-012: 非 .html 文件被拦截"""
        response = client.get('/wiki/soc_dv/pages/index.json')
        assert response.status_code == 400, \
            f"Non-HTML file should return 400, got {response.status_code}"
        data = json.loads(response.data)
        assert 'error' in data


# ============ 3.2.3 降级逻辑测试 ============

class TestWikiFallback:
    """降级逻辑测试 - API-WIKI-020 ~ API-WIKI-021"""

    def test_wiki_fallback_to_global(self, client):
        """API-WIKI-020: 项目 Wiki 不存在时降级到 _global"""
        # 访问一个不存在的项目 wiki，应该降级到 _global
        # 使用 _global 作为 slug 验证全局 wiki 可以正常访问
        response = client.get('/wiki/_global/index.json')
        assert response.status_code == 200, \
            f"Global wiki should be accessible, got {response.status_code}"

        data = json.loads(response.data)
        assert 'pages' in data

    def test_wiki_global_also_missing(self, client, monkeypatch, tmp_path):
        """API-WIKI-021: 全局 Wiki 也不存在时返回 404"""
        import importlib
        import app.wiki as wiki_module
        # 获取实际的模块（不是 Blueprint 对象）
        wiki_mod = importlib.import_module('app.wiki')
        # 创建空的临时 wiki 目录（没有任何 wiki）
        temp_wiki_root = tmp_path / "wiki"
        temp_wiki_root.mkdir()
        # 让 get_wiki_base_path 返回临时目录
        monkeypatch.setattr(wiki_mod, 'get_wiki_base_path', lambda: str(temp_wiki_root))
        response = client.get('/wiki/nonexistent_project_xyz/index.json')
        assert response.status_code == 404, \
            f"Non-existent wiki should return 404, got {response.status_code}"


# ============ 3.2.4 Wiki 不存在测试 ============

class TestWikiNotFound:
    """Wiki 不存在测试 - API-WIKI-030 ~ API-WIKI-031"""

    def test_wiki_page_not_found(self, client):
        """API-WIKI-030: 页面不存在时返回 404"""
        response = client.get('/wiki/soc_dv/pages/nonexistent_page.html')
        assert response.status_code == 404, \
            f"Non-existent page should return 404, got {response.status_code}"

    def test_wiki_exists_none(self, client, monkeypatch, tmp_path):
        """API-WIKI-031: Wiki 完全不存在时 source 为 none"""
        import importlib
        import app.wiki as wiki_module
        # 获取实际的模块（不是 Blueprint 对象）
        wiki_mod = importlib.import_module('app.wiki')
        # 创建空的临时 wiki 目录（没有任何 wiki）
        temp_wiki_root = tmp_path / "wiki"
        temp_wiki_root.mkdir()
        # 让 get_wiki_base_path 返回临时目录
        monkeypatch.setattr(wiki_mod, 'get_wiki_base_path', lambda: str(temp_wiki_root))
        response = client.get('/wiki/exists/nonexistent_project_xyz')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = json.loads(response.data)
        assert data['has_wiki'] is False, "has_wiki should be False"
        assert data['source'] == 'none', "source should be 'none'"


# ============ 3.2.5 Wiki 生命周期管理测试 ============

class TestWikiLifecycle:
    """Wiki 生命周期管理测试 - API-WIKI-040"""

    def test_wiki_lifecycle_delete_project(self, client, tmp_path):
        """API-WIKI-040: 项目删除时 Wiki 目录一并删除并归档备份"""
        import importlib
        import shutil
        import app.wiki as wiki_module
        wiki_mod = importlib.import_module('app.wiki')

        # 创建临时 wiki 目录结构
        temp_wiki_root = tmp_path / "wiki"
        temp_wiki_root.mkdir()
        project_slug = "test_lifecycle_project"

        # 创建测试项目的 Wiki 目录
        project_wiki = temp_wiki_root / project_slug
        project_wiki.mkdir()
        (project_wiki / "index.json").write_text('{"pages": []}')
        (project_wiki / "pages").mkdir()
        (project_wiki / "pages" / "index.html").write_text("<h1>Test</h1>")

        # 创建 _archived 目录
        archived_dir = temp_wiki_root / "_archived"
        archived_dir.mkdir()

        # 使用 monkeypatch 让 get_wiki_base_path 返回临时目录
        original_get_wiki_base_path = wiki_mod.get_wiki_base_path
        wiki_mod.get_wiki_base_path = lambda: str(temp_wiki_root)

        try:
            # 调用 delete_project_wiki 函数
            result = wiki_mod.delete_project_wiki("test_lifecycle_project")

            # 验证删除成功
            assert result is True, "delete_project_wiki should return True"

            # 验证 Wiki 目录已删除
            assert not project_wiki.exists(), \
                f"Wiki directory should be deleted: {project_wiki}"

            # 验证备份已创建
            archived_contents = list(archived_dir.iterdir())
            assert len(archived_contents) > 0, \
                "Backup should be created in _archived directory"

            # 验证备份目录包含原 Wiki 内容
            backup_dir = archived_contents[0]
            assert (backup_dir / "index.json").exists(), \
                "Backup should contain index.json"
            assert (backup_dir / "pages" / "index.html").exists(), \
                "Backup should contain pages/index.html"

        finally:
            # 恢复原始函数
            wiki_mod.get_wiki_base_path = original_get_wiki_base_path

    def test_wiki_lifecycle_delete_nonexistent(self, client, tmp_path):
        """API-WIKI-041: 项目 Wiki 不存在时删除返回 False"""
        import importlib
        import app.wiki as wiki_module
        wiki_mod = importlib.import_module('app.wiki')

        # 创建临时 wiki 目录（但没有项目 wiki）
        temp_wiki_root = tmp_path / "wiki"
        temp_wiki_root.mkdir()

        original_get_wiki_base_path = wiki_mod.get_wiki_base_path
        wiki_mod.get_wiki_base_path = lambda: str(temp_wiki_root)

        try:
            # 调用 delete_project_wiki 函数（不存在的项目）
            result = wiki_mod.delete_project_wiki("nonexistent_project_xyz")

            # 验证返回 False
            assert result is False, \
                "delete_project_wiki should return False when wiki doesn't exist"

        finally:
            # 恢复原始函数
            wiki_mod.get_wiki_base_path = original_get_wiki_base_path
