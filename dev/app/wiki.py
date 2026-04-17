"""
Wiki Blueprint - v0.13.0
提供 Wiki 内容访问路由，指向 shared/data/{user,test}_data/wiki/ 目录
"""

from flask import Blueprint, jsonify, send_from_directory, current_app, request
from functools import wraps
import os
import re
import shutil

wiki = Blueprint("wiki", __name__)

# Wiki 目录名称
WIKI_DIR_NAME = "wiki"
GLOBAL_WIKI_SLUG = "_global"


def get_wiki_base_path():
    """获取 Wiki 基础路径"""
    return os.path.join(current_app.config["DATA_DIR"], WIKI_DIR_NAME)


def get_project_slug(project_name):
    """
    项目名转 slug，用于 Wiki 目录命名
    规则：
    1. 转小写
    2. 移除特殊字符（只保留字母、数字、空格、连字符）
    3. 空格/连字符转为下划线
    """
    slug = project_name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)      # 移除特殊字符
    slug = re.sub(r'[-\s]+', '_', slug)         # 空格/连字符转下划线
    slug = slug.strip('_')                      # 移除首尾下划线
    return slug


def normalize_path(path):
    """
    规范化路径，防止路径遍历攻击
    - 拦截 ../
    - 拦截绝对路径
    - 确保只返回 .html 文件
    """
    # 移除 .. 和绝对路径
    if '..' in path or path.startswith('/') or ':' in path:
        return None

    # 确保只允许 .html 文件
    if not path.endswith('.html'):
        return None

    # 规范化路径
    normalized = os.path.normpath(path)
    if normalized.startswith('..') or normalized.startswith('/'):
        return None

    return normalized


def wiki_exists(slug):
    """检查 Wiki 是否存在（项目级或全局）"""
    wiki_base = get_wiki_base_path()
    project_wiki = os.path.join(wiki_base, slug)
    global_wiki = os.path.join(wiki_base, GLOBAL_WIKI_SLUG)

    if os.path.isdir(project_wiki):
        return "project", project_wiki
    elif os.path.isdir(global_wiki):
        return "global", global_wiki
    else:
        return "none", None


def get_wiki_info(slug):
    """
    获取 Wiki 信息
    返回 (exists, source, wiki_path)
    """
    wiki_base = get_wiki_base_path()
    project_wiki = os.path.join(wiki_base, slug)
    global_wiki = os.path.join(wiki_base, GLOBAL_WIKI_SLUG)

    if os.path.isdir(project_wiki):
        return True, "project", project_wiki
    elif os.path.isdir(global_wiki):
        return True, "global", global_wiki
    else:
        return False, "none", None


# ============ Wiki 路由 ============

@wiki.route("/wiki/<slug>/index.json")
def get_wiki_index(slug):
    """
    获取 Wiki 索引
    - 如果项目 Wiki 存在，返回项目 Wiki 的 index.json
    - 如果不存在，降级到 _global/ 全局 Wiki
    - 如果全局 Wiki 也不存在，返回 404
    """
    exists, source, wiki_path = get_wiki_info(slug)

    if not exists:
        return jsonify({
            "error": "Wiki not found",
            "project_slug": slug
        }), 404

    index_path = os.path.join(wiki_path, "index.json")

    if not os.path.isfile(index_path):
        # 降级到全局 Wiki
        if source == "project":
            global_path = os.path.join(get_wiki_base_path(), GLOBAL_WIKI_SLUG)
            index_path = os.path.join(global_path, "index.json")
            if not os.path.isfile(index_path):
                return jsonify({
                    "error": "Wiki index not found",
                    "project_slug": slug
                }), 404
            source = "global"
        else:
            return jsonify({
                "error": "Wiki index not found",
                "project_slug": slug
            }), 404

    try:
        return send_from_directory(os.path.dirname(index_path), "index.json")
    except Exception as e:
        return jsonify({
            "error": f"Failed to load wiki index: {str(e)}",
            "project_slug": slug
        }), 500


@wiki.route("/wiki/<slug>/pages/<path:path>")
def get_wiki_page(slug, path):
    """
    获取 Wiki 页面 HTML
    - 路径遍历防护
    - 只返回 .html 文件
    - 降级到全局 Wiki（如果项目 Wiki 不存在页面）
    """
    # 规范化路径，防止路径遍历
    normalized = normalize_path(path)
    if normalized is None:
        return jsonify({
            "error": "Invalid path - path traversal detected or non-HTML file"
        }), 400

    wiki_base = get_wiki_base_path()
    project_wiki = os.path.join(wiki_base, slug)
    global_wiki = os.path.join(wiki_base, GLOBAL_WIKI_SLUG)

    # 尝试项目 Wiki
    project_page = os.path.join(project_wiki, "pages", normalized)
    if os.path.isfile(project_page):
        try:
            return send_from_directory(os.path.join(project_wiki, "pages"), normalized)
        except Exception as e:
            return jsonify({
                "error": f"Failed to load wiki page: {str(e)}"
            }), 500

    # 降级到全局 Wiki
    global_page = os.path.join(global_wiki, "pages", normalized)
    if os.path.isfile(global_page):
        try:
            return send_from_directory(os.path.join(global_wiki, "pages"), normalized)
        except Exception as e:
            return jsonify({
                "error": f"Failed to load wiki page: {str(e)}"
            }), 500

    return jsonify({
        "error": "Page not found"
    }), 404


@wiki.route("/wiki/<slug>/changes_index.json")
def get_wiki_changes(slug):
    """
    获取 Wiki 变更历史
    - 如果项目 Wiki 存在，返回项目 Wiki 的 changes_index.json
    - 如果不存在，返回空的 versions 列表
    """
    wiki_base = get_wiki_base_path()
    project_wiki = os.path.join(wiki_base, slug)
    global_wiki = os.path.join(wiki_base, GLOBAL_WIKI_SLUG)

    # 优先使用项目 Wiki 的变更历史
    project_changes = os.path.join(project_wiki, "changes_index.json")
    if os.path.isfile(project_changes):
        try:
            return send_from_directory(project_wiki, "changes_index.json")
        except Exception as e:
            pass

    # 降级到全局 Wiki
    global_changes = os.path.join(global_wiki, "changes_index.json")
    if os.path.isfile(global_changes):
        try:
            return send_from_directory(global_wiki, "changes_index.json")
        except Exception as e:
            pass

    # 如果都没有，返回空变更历史
    return jsonify({
        "versions": []
    })


@wiki.route("/wiki/exists/<slug>")
def check_wiki_exists(slug):
    """
    检查 Wiki 是否存在
    返回 has_wiki 和 source
    """
    exists, source, wiki_path = get_wiki_info(slug)

    return jsonify({
        "project_slug": slug,
        "has_wiki": exists,
        "source": source
    })


# ============ Wiki 生命周期管理 ============

def delete_project_wiki(project_name):
    """
    删除项目的 Wiki 目录（如果有）
    删除前会自动创建归档备份

    Args:
        project_name: 项目名称

    Returns:
        bool: 是否删除了 Wiki 目录
    """
    slug = get_project_slug(project_name)
    wiki_base = get_wiki_base_path()
    project_wiki = os.path.join(wiki_base, slug)

    if not os.path.isdir(project_wiki):
        return False

    # 创建归档备份
    try:
        backup_dir = os.path.join(wiki_base, "_archived")
        os.makedirs(backup_dir, exist_ok=True)

        backup_name = f"{slug}_{os.path.getmtime(project_wiki)}_deleted"
        backup_path = os.path.join(backup_dir, backup_name)

        # 复制到备份目录
        shutil.copytree(project_wiki, backup_path)
    except Exception as e:
        print(f"Wiki backup failed: {e}")

    # 删除 Wiki 目录
    try:
        shutil.rmtree(project_wiki)
        return True
    except Exception as e:
        print(f"Failed to delete wiki: {e}")
        return False


def list_all_wikis():
    """
    列出所有 Wiki（项目级）
    """
    wiki_base = get_wiki_base_path()
    if not os.path.isdir(wiki_base):
        return []

    wikis = []
    for item in os.listdir(wiki_base):
        item_path = os.path.join(wiki_base, item)
        if os.path.isdir(item_path) and item != GLOBAL_WIKI_SLUG and not item.startswith('_'):
            index_path = os.path.join(item_path, "index.json")
            wikis.append({
                "slug": item,
                "has_index": os.path.isfile(index_path)
            })

    return wikis


# ============ Wiki 响应头配置 (v0.13.0) ============

@wiki.after_request
def add_csp_header(response):
    """
    为 Wiki 响应添加 CSP Header
    符合规格书 REQ-W002 要求
    """
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
    return response
