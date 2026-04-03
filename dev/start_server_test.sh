#!/bin/bash
# Tracker 开发版服务启动脚本
# 使用 gunicorn 启动开发版服务
# 规格文档下载服务已集成到 8081 端口 (/docs/SPECIFICATIONS/)

cd /projects/management/tracker/dev

# 读取版本号
if [ -f VERSION ]; then
    source VERSION
    VERSION_NUM=${VERSION#v}
else
    VERSION_NUM="dev"
fi

# 日志目录（hqi 用户有权限）
LOG_DIR="/home/hqi/logs"
mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="/tmp"
ACCESS_LOG="$LOG_DIR/tracker_access_8081.log"
ERROR_LOG="$LOG_DIR/tracker_error_8081.log"

# 检测服务是否运行（兼容 gunicorn 和 python3 直接启动）
is_running() {
    pgrep -f "gunicorn.*8081" > /dev/null 2>&1 && return 0
    pgrep -f "python3.*8081" > /dev/null 2>&1 && return 0
    return 1
}

get_pid() {
    pgrep -f "gunicorn.*8081" 2>/dev/null || pgrep -f "python3.*8081" 2>/dev/null
}

# 检查服务是否已运行
if is_running; then
    echo "✅ Tracker 测试服务已在运行中，PID: $(get_pid)"
    exit 0
fi

# 停止可能占用端口的进程
echo "停止旧进程..."
pkill -f "server_test.py" 2>/dev/null || true
pkill -f "gunicorn.*8081" 2>/dev/null || true
pkill -f "python3.*8081" 2>/dev/null || true
sleep 1

# 使用 gunicorn 启动 (gevent worker 解决多进程 session 问题)
echo "启动 Tracker 测试版服务 (v$VERSION_NUM)..."
gunicorn \
    --workers 2 \
    --worker-class=gevent \
    --bind 0.0.0.0:8081 \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG" \
    --capture-output \
    --daemon \
    wsgi:app

sleep 3

# 检查启动结果
if is_running; then
    echo "✅ 服务启动成功"
    echo "📍 访问地址: http://localhost:8081"
    echo "📚 规格书下载: http://localhost:8081/docs/SPECIFICATIONS/"
    echo "📝 访问日志: $ACCESS_LOG"
    echo "📝 错误日志: $ERROR_LOG"
else
    echo "❌ 服务启动失败，检查日志: $ERROR_LOG"
    exit 1
fi
