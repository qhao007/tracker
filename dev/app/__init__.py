"""
Tracker Flask 应用 - v0.3 独立数据库版本
"""
from flask import Flask, g
from .api import api
import os


def create_app(testing=False):
    app = Flask(__name__)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    # 配置
    app.config['TESTING'] = testing
    app.config['BASE_DIR'] = base_dir
    app.config['DATA_DIR'] = data_dir

    # 确保数据目录存在
    os.makedirs(data_dir, exist_ok=True)

    # 设置静态文件目录
    app.static_folder = base_dir
    app.template_folder = base_dir

    # 注册蓝图
    app.register_blueprint(api, url_prefix='/')

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
