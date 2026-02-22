#!/bin/bash
# Tracker 生产版服务启动脚本 (gunicorn + gevent)
cd /projects/management/tracker/dev

echo "启动 Tracker 生产版服务 (v0.7.1)..."
gunicorn \
    --workers 2 \
    --worker-class=gevent \
    --bind 0.0.0.0:8080 \
    --access-logfile /tmp/gunicorn_prod_access.log \
    --error-logfile /tmp/gunicorn_prod_error.log \
    --capture-output \
    wsgi:app &

sleep 3

if pgrep -f "gunicorn.*8080" > /dev/null 2>&1; then
    echo "✅ 生产服务启动成功"
    echo "📍 访问地址: http://localhost:8080"
else
    echo "❌ 服务启动失败"
fi
