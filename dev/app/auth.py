"""
用户认证模块 - v0.7.1
包含用户管理、密码哈希、Session 管理功能
"""
import os
import sqlite3
import hashlib
import secrets
import json
import time
from datetime import datetime
from flask import current_app


def get_users_db_path():
    """获取用户数据库路径"""
    from flask import current_app
    return os.path.join(current_app.config["DATA_DIR"], "users.db")


def init_users_db():
    """初始化用户数据库"""
    db_path = get_users_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user', 'guest')),
            is_active INTEGER DEFAULT 1,
            must_change_password INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def get_users_connection():
    """获取用户数据库连接"""
    db_path = get_users_db_path()
    if not os.path.exists(db_path):
        init_users_db()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password, salt=None):
    """使用 pbkdf2_hmac 哈希密码"""
    import hashlib
    if salt is None:
        salt = secrets.token_hex(16)
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    
    return f"{salt}${key}"


def verify_password(password, password_hash):
    """验证密码"""
    import hashlib
    if not password_hash:
        return False
    
    try:
        salt, key = password_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return new_hash == key
    except:
        return False


def create_default_users():
    """创建默认用户（如果不存在）"""
    conn = get_users_connection()
    cursor = conn.cursor()
    
    # 检查是否已有用户
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # 创建默认 admin 账户
        admin_password = hash_password("admin123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, is_active, must_change_password)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", admin_password, "admin", 1, 1))
        
        # 创建默认 guest 账户（无密码）
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, is_active)
            VALUES (?, ?, ?, ?)
        """, ("guest", None, "guest", 1))
        
        conn.commit()
    
    conn.close()


def get_user_by_username(username):
    """根据用户名获取用户"""
    conn = get_users_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id):
    """根据 ID 获取用户"""
    conn = get_users_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def create_user(username, password, role='user'):
    """创建新用户"""
    conn = get_users_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password) if password else None
    
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, is_active)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, role, 1))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id


def update_user(user_id, **kwargs):
    """更新用户信息"""
    conn = get_users_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['username', 'password_hash', 'role', 'is_active', 'must_change_password', 'last_login']
    updates = []
    values = []
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            values.append(value)
    
    if updates:
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    
    conn.close()


def delete_user(user_id):
    """删除用户"""
    conn = get_users_connection()
    cursor = conn.cursor()
    
    # 获取用户信息
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row and row[0] in ['admin', 'guest']:
        conn.close()
        return False, "无法删除系统用户"
    
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    return True, "删除成功"


def get_all_users():
    """获取所有用户"""
    conn = get_users_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, is_active, must_change_password, created_at, last_login FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ============ 暴力破解防护 ============

def get_login_attempts_file():
    """获取登录尝试记录文件路径"""
    return os.path.join(current_app.config["DATA_DIR"], "login_attempts.json")


def load_login_attempts():
    """加载登录尝试记录"""
    filepath = get_login_attempts_file()
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"attempts": {}}


def save_login_attempts(data):
    """保存登录尝试记录"""
    filepath = get_login_attempts_file()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_login_attempts(username):
    """检查登录尝试次数"""
    data = load_login_attempts()
    attempts = data.get("attempts", {}).get(username)
    
    if not attempts:
        return True, None
    
    count = attempts.get("count", 0)
    locked_until = attempts.get("locked_until", 0)
    current_time = int(time.time())
    
    # 检查是否已解锁
    if current_time > locked_until:
        return True, None
    
    remaining = locked_until - current_time
    return False, f"账户已锁定，请 {remaining} 秒后重试"


def record_failed_login(username):
    """记录失败的登录尝试"""
    data = load_login_attempts()
    
    if "attempts" not in data:
        data["attempts"] = {}
    
    if username not in data["attempts"]:
        data["attempts"][username] = {"count": 0, "locked_until": 0}
    
    data["attempts"][username]["count"] += 1
    
    # 连续 5 次失败，锁定 15 分钟
    if data["attempts"][username]["count"] >= 5:
        data["attempts"][username]["locked_until"] = int(time.time()) + 900  # 15 分钟
    
    save_login_attempts(data)


def clear_login_attempts(username):
    """清除登录尝试记录（登录成功时）"""
    data = load_login_attempts()
    
    if "attempts" in data and username in data["attempts"]:
        del data["attempts"][username]
        save_login_attempts(data)


# 初始化默认用户（在应用启动时调用）
def init_auth():
    """初始化认证系统"""
    init_users_db()
    create_default_users()
