"""
Tracker Flask 应用 - v0.7.1 用户认证版本
"""
from flask import Flask, g
from .api import api
import os
import secrets


def create_app(testing=False):
    app = Flask(__name__)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    # 配置
    app.config['TESTING'] = testing
    app.config['BASE_DIR'] = base_dir
    app.config['DATA_DIR'] = data_dir
    
    # Session 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
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

    # 设置静态文件目录
    app.static_folder = base_dir
    app.template_folder = base_dir

    # 注册蓝图
    app.register_blueprint(api, url_prefix='/')

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
