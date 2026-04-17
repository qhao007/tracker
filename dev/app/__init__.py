"""
Tracker Flask 应用 - v0.7.1 用户认证版本
"""
from flask import Flask, g, request, session
from .api import api
from .wiki import wiki
import os
import secrets
import time
import json
import logging


def create_app(testing=False):
    app = Flask(__name__, static_folder=None)  # 禁用默认静态路由，使用自定义路由
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    # 配置日志
    log_dir = os.path.join(data_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'api.log')

    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    # 请求计时开始
    @app.before_request
    def before_request():
        request.start_time = time.time()

    # 统一记录 API 请求日志
    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            duration_ms = int(duration * 1000)

            # 获取用户信息
            user_id = session.get('user_id', 'anonymous')
            username = session.get('username', '')

            log_data = {
                "event": "api_call",
                "endpoint": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "user": username or user_id,
                "ip": request.remote_addr
            }

            # 根据状态码选择日志级别
            if response.status_code >= 500:
                logger.error(json.dumps(log_data))
            elif response.status_code >= 400:
                logger.warning(json.dumps(log_data))
            else:
                logger.info(json.dumps(log_data))

        return response

    # 配置
    app.config['TESTING'] = testing
    app.config['BASE_DIR'] = base_dir
    app.config['DATA_DIR'] = data_dir
    
    # Session 配置 - 使用固定的 SECRET_KEY 确保 session 持久化
    # 生产环境应使用环境变量设置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tracker-dev-secret-key-v071')
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # 使用文件系统存储 session，支持多 worker
    session_dir = os.path.join(data_dir, 'sessions')
    os.makedirs(session_dir, exist_ok=True)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = session_dir
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    # 初始化 Flask-Session
    from flask_session import Session
    Session(app)
    # 注意：生产环境需要配置 HTTPS，设置 SESSION_COOKIE_SECURE = True
    
    # 配置文件上传大小限制 (16MB)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # 确保数据目录存在
    os.makedirs(data_dir, exist_ok=True)

    # 设置模板目录（静态文件使用自定义路由）
    app.template_folder = base_dir

    # 注册蓝图
    app.register_blueprint(api, url_prefix='/')
    app.register_blueprint(wiki, url_prefix='/')

    # 手动添加 /manual 路由（因为模板在 base_dir）
    from flask import render_template, send_from_directory, render_template_string

    @app.route('/manual')
    def manual():
        return render_template('templates/manual.html')

    # 提供 manual.md 文件访问
    @app.route('/manual.md')
    def serve_manual():
        return send_from_directory(base_dir, 'manual.md')

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(os.path.join(base_dir, 'static'), filename)

    # 提供 app_static 目录访问（用于本地静态资源，如 Chart.js）
    @app.route('/app_static/<path:filename>')
    def serve_app_static(filename):
        app_static_dir = os.path.join(base_dir, 'app_static')
        return send_from_directory(app_static_dir, filename)

    # 提供 SPECIFICATIONS 目录访问（用于测试期间下载规格书文档）
    @app.route('/docs/SPECIFICATIONS/')
    @app.route('/docs/SPECIFICATIONS')
    def list_specifications():
        """列出测试版规格书目录"""
        from datetime import datetime
        specs_dir = os.path.join(os.path.dirname(base_dir), 'docs', 'SPECIFICATIONS')
        files = []
        if os.path.exists(specs_dir):
            for f in sorted(os.listdir(specs_dir)):
                if f.endswith('.md'):
                    filepath = os.path.join(specs_dir, f)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
                    size = os.path.getsize(filepath)
                    files.append({'name': f, 'size': size, 'mtime': mtime})
        
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>规格书目录 - Tracker 测试版</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f5f5f5; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .size { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <h1>📋 Tracker 测试版规格书</h1>
    <table>
        <tr><th>文件名</th><th>大小</th><th>修改时间</th></tr>
        {% for f in files %}
        <tr>
            <td><a href="/docs/SPECIFICATIONS/{{ f.name }}">{{ f.name }}</a></td>
            <td class="size">{{ (f.size / 1024) | round(1) }} KB</td>
            <td class="size">{{ f.mtime }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>'''
        return render_template_string(html, files=files)
    
    @app.route('/docs/SPECIFICATIONS/<path:filename>')
    def serve_specifications(filename):
        """服务测试版规格书文档"""
        specs_dir = os.path.join(os.path.dirname(base_dir), 'docs', 'SPECIFICATIONS')
        return send_from_directory(specs_dir, filename)

    # 初始化认证系统
    from . import auth
    if not testing:
        with app.app_context():
            auth.init_auth()

    # 清理数据库连接
    @app.teardown_appcontext
    def teardown(exception=None):
        if hasattr(g, 'db_connections'):
            for conn in g.db_connections.values():
                conn.close()
            g.db_connections.clear()

    return app


def get_db_path(project_name):
    """获取项目数据库文件路径"""
    data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    safe_name = (project_name.replace(' ', '_')
                 .replace('/', '_')
                 .replace('\\', '_'))
    return os.path.join(data_dir, 'data', f'{safe_name}.db')
