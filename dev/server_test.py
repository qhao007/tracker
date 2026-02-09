#!/usr/bin/env python3
"""
芯片验证 Tracker 测试版服务器 - v0.6.0

启动方式:
    cd dev
    python3 server_test.py

后台运行:
    cd dev
    nohup python3 server_test.py > /tmp/dev.log 2>&1 &
"""
import os
from app import create_app

# 确保数据目录存在
os.makedirs('data', exist_ok=True)

if __name__ == '__main__':
    app = create_app()
    print("🚀 芯片验证 Tracker v0.6.0 测试版服务器启动中...")
    print("📍 访问地址: http://localhost:8081")
    print("💡 独立数据库架构: 每个项目拥有独立数据库文件")
    print("⚠️  注意: 这是测试版，请勿用于生产环境")
    print("💡 后台运行: nohup python3 server_test.py > /tmp/dev.log 2>&1 &")
    
    # 使用多线程模式，避免自动重启问题
    app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)
