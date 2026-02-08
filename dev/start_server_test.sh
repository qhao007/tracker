#!/bin/bash
# Tracker 开发版服务启动脚本
# 使用 gunicorn + systemd 用户单元，稳定运行

cd /projects/management/tracker/dev

# 检查服务是否已运行
if pgrep -f "gunicorn.*8081" > /dev/null 2>&1; then
    echo "服务已在运行中，PID: $(pgrep -f 'gunicorn.*8081')"
    exit 0
fi

# 停止可能占用端口的进程
pkill -f "server_test.py" 2>/dev/null || true
sleep 1

# 使用 gunicorn 启动
echo "启动 Tracker 开发版服务 (v0.6.0)..."
gunicorn \
    --workers 2 \
    --bind 0.0.0.0:8081 \
    --access-logfile /tmp/gunicorn_access.log \
    --error-logfile /tmp/gunicorn_error.log \
    --capture-output \
    wsgi:app &

sleep 3

# 检查启动结果
if pgrep -f "gunicorn.*8081" > /dev/null 2>&1; then
    echo "✅ 服务启动成功"
    echo "📍 访问地址: http://localhost:8081"
    echo "📝 日志: /tmp/gunicorn_access.log"
else
    echo "❌ 服务启动失败，检查日志: /tmp/gunicorn_error.log"
fi
