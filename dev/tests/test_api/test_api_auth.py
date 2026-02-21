"""
认证 API 测试 - v0.7.1
使用 TDD 流程：先写测试 → 失败 → 写代码 → 通过
"""
import json
import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 设置测试环境
os.environ['TESTING'] = '1'


@pytest.fixture(scope='session')
def app():
    """创建测试应用（session 级别，整个测试会话只创建一次）"""
    # 删除旧的测试数据库
    test_db = '/tmp/test_users.db'
    test_attempts = '/tmp/test_login_attempts.json'
    for f in [test_db, test_attempts]:
        if os.path.exists(f):
            os.remove(f)
    
    # 临时修改 auth 模块使用测试数据库
    import app.auth as auth_module
    original_get_db_path = auth_module.get_users_db_path
    
    def test_get_users_db_path():
        return test_db
    
    def test_get_login_attempts_file():
        return test_attempts
    
    auth_module.get_users_db_path = test_get_users_db_path
    auth_module.get_login_attempts_file = test_get_login_attempts_file
    
    # 创建 app
    from app import create_app
    app = create_app(testing=True)
    
    with app.app_context():
        auth_module.init_users_db()
        auth_module.create_default_users()
    
    yield app
    
    # 清理
    auth_module.get_users_db_path = original_get_db_path


@pytest.fixture
def client(app):
    """创建测试客户端（每个测试创建新的客户端）"""
    with app.test_client() as c:
        yield c


# ============ 登录 API 测试 ============

class TestLoginAPI:
    """登录 API 测试"""
    
    def test_login_success(self, client):
        """正确用户名密码应登录成功"""
        response = client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['username'] == 'admin'
        assert data['user']['role'] == 'admin'
    
    def test_login_wrong_password(self, client):
        """错误密码应登录失败"""
        response = client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'wrongpassword'}),
            content_type='application/json')
        
        assert response.status_code == 401
    
    def test_login_empty_username(self, client):
        """空用户名应失败"""
        response = client.post('/api/auth/login', 
            data=json.dumps({'username': '', 'password': 'admin123'}),
            content_type='application/json')
        
        assert response.status_code == 400
    
    def test_login_empty_password(self, client):
        """空密码应失败"""
        response = client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': ''}),
            content_type='application/json')
        
        assert response.status_code == 400


class TestGuestLoginAPI:
    """访客登录 API 测试"""
    
    def test_guest_login_success(self, client):
        """访客登录应成功"""
        response = client.post('/api/auth/guest-login')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['username'] == 'guest'
        assert data['user']['role'] == 'guest'


class TestLogoutAPI:
    """登出 API 测试"""
    
    def test_logout_success(self, client):
        """登出应成功"""
        # 先登录
        client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        # 登出
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
    
    def test_logout_unauthenticated(self, client):
        """未登录应返回 401"""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 401


class TestGetCurrentUserAPI:
    """获取当前用户 API 测试"""
    
    def test_get_current_user(self, client):
        """获取当前用户信息"""
        # 先登录
        client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['username'] == 'admin'
    
    def test_get_current_user_unauthenticated(self, client):
        """未登录应返回 401"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401


class TestUserListAPI:
    """用户列表 API 测试"""
    
    def test_get_users_admin(self, client):
        """管理员应能获取用户列表"""
        # 先用 admin 登录
        client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        response = client.get('/api/users')
        
        assert response.status_code == 200
        users = response.get_json()
        assert isinstance(users, list)
    
    def test_get_users_unauthenticated(self, client):
        """未登录应无法获取用户列表"""
        response = client.get('/api/users')
        
        assert response.status_code == 401


class TestCreateUserAPI:
    """创建用户 API 测试"""
    
    def test_create_user_admin(self, client):
        """管理员应能创建用户"""
        # 先用 admin 登录
        client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        # 创建用户
        unique_name = f"testuser_{int(time.time())}"
        response = client.post('/api/users',
            data=json.dumps({'username': unique_name, 'password': 'test123', 'role': 'user'}),
            content_type='application/json')
        
        assert response.status_code == 201
    
    def test_create_duplicate_username(self, client):
        """创建重复用户名应失败"""
        # 先用 admin 登录
        client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        unique_name = f"duplicate_{int(time.time())}"
        
        # 第一次创建
        client.post('/api/users',
            data=json.dumps({'username': unique_name, 'password': 'test123', 'role': 'user'}),
            content_type='application/json')
        
        # 第二次创建同名用户
        response = client.post('/api/users',
            data=json.dumps({'username': unique_name, 'password': 'test123', 'role': 'user'}),
            content_type='application/json')
        
        assert response.status_code == 409


class TestPermissionControl:
    """权限控制测试"""
    
    def test_user_cannot_access_users(self, client):
        """普通用户无法访问用户管理"""
        # 先创建普通用户并登录
        client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        unique_name = f"regularuser_{int(time.time())}"
        client.post('/api/users',
            data=json.dumps({'username': unique_name, 'password': 'test123', 'role': 'user'}),
            content_type='application/json')
        
        # 用普通用户登录
        client.post('/api/auth/logout')
        client.post('/api/auth/login', 
            data=json.dumps({'username': unique_name, 'password': 'test123'}),
            content_type='application/json')
        
        # 尝试访问用户列表
        response = client.get('/api/users')
        
        assert response.status_code == 403
    
    def test_user_can_access_projects(self, client):
        """普通用户可以访问项目"""
        # 创建普通用户并登录
        client.post('/api/auth/login', 
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json')
        
        unique_name = f"projectuser_{int(time.time())}"
        client.post('/api/users',
            data=json.dumps({'username': unique_name, 'password': 'test123', 'role': 'user'}),
            content_type='application/json')
        
        client.post('/api/auth/logout')
        client.post('/api/auth/login', 
            data=json.dumps({'username': unique_name, 'password': 'test123'}),
            content_type='application/json')
        
        # 访问项目
        response = client.get('/api/projects')
        
        assert response.status_code == 200
