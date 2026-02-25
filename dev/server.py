#!/usr/bin/env python3
"""
芯片验证 Tracker 后端服务 - v0.7.1 用户认证版本
"""
import os
from app import create_app

# 确保数据目录存在
os.makedirs('data', exist_ok=True)

if __name__ == '__main__':
    app = create_app()
    print("🚀 芯片验证 Tracker v0.7.1 服务器启动中...")
    print("📍 访问地址: http://localhost:8080")
    print("💡 用户认证: 支持 admin/user/guest 角色")
    app.run(host='0.0.0.0', port=8080, debug=False)
