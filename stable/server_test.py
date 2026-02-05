#!/usr/bin/env python3
"""
芯片验证 Tracker 测试版服务器 - v0.3
"""
import os
from app import create_app

# 确保数据目录存在
os.makedirs('data', exist_ok=True)

if __name__ == '__main__':
    app = create_app()
    print("🚀 芯片验证 Tracker v0.3 测试版服务器启动中...")
    print("📍 访问地址: http://localhost:8081")
    print("💡 独立数据库架构: 每个项目拥有独立数据库文件")
    print("⚠️  注意: 这是测试版，请勿用于生产环境")
    app.run(host='0.0.0.0', port=8081, debug=True)
