#!/bin/bash
# Tracker 开发版服务启动脚本
# 使用 gunicorn + systemd 用户单元，稳定运行
# 同时启动规格文档下载服务

cd /projects/management/tracker/dev

# ========== 规格文档下载服务 ==========
DOCS_PORT=8888
DOCS_DIR="/projects/management/tracker/docs/dev"

# 检查是否已有 HTTP 服务运行
if lsof -i:$DOCS_PORT > /dev/null 2>&1; then
    echo "⚠️  端口 $DOCS_PORT 已被占用，规格文档服务已存在"
else
    echo "📄 启动规格文档下载服务..."
    cd "$DOCS_DIR"
    nohup python3 -m http.server $DOCS_PORT > /tmp/http_docs.log 2>&1 &
    sleep 1
    if curl -s http://localhost:$DOCS_PORT > /dev/null; then
        echo "✅ 规格文档服务启动成功"
        echo "📍 下载地址: http://<你的IP>:$DOCS_PORT/"
    else
        echo "❌ 规格文档服务启动失败"
    fi
    cd /projects/management/tracker/dev
fi
# =====================================

# 检查服务是否已运行
if pgrep -f "gunicorn.*8081" > /dev/null 2>&1; then
    echo "✅ Tracker 服务已在运行中，PID: $(pgrep -f 'gunicorn.*8081')"
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
