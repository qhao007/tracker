#!/usr/bin/env python3
"""
芯片验证 Tracker 后端服务 - v0.3 独立数据库版本
"""
import os
from app import create_app

# 确保数据目录存在
os.makedirs('data', exist_ok=True)

if __name__ == '__main__':
    app = create_app()
    print("🚀 芯片验证 Tracker v0.3 服务器启动中...")
    print("📍 访问地址: http://localhost:8080")
    print("💡 独立数据库架构: 每个项目拥有独立数据库文件")
    app.run(host='0.0.0.0', port=8080, debug=False)
