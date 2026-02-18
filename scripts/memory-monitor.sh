#!/bin/bash
# =============================================================================
# memory-monitor.sh - 测试内存监控脚本
# =============================================================================
# 
# 功能：监控测试执行时的内存使用情况
# - 监控 Firefox 进程内存使用
# - 超过限制时自动终止进程
# - 记录日志到 test-results/memory-monitor.log
#
# 使用方法：
#   1. 直接运行（前台）:
#      bash scripts/memory-monitor.sh
#
#   2. 后台运行:
#      bash scripts/memory-monitor.sh &
#
#   3. 设置定时任务（每分钟检查）:
#      * * * * * bash /projects/management/tracker/scripts/memory-monitor.sh >> /dev/null 2>&1
#
#   4. 停止监控:
#      pkill -f memory-monitor.sh
#
# =============================================================================

# 配置参数
MAX_MEMORY_KB=1500000        # 最大内存限制（KB），1.5GB = 1500000KB
MAX_MEMORY_MB=1500           # 最大内存限制（MB），便于阅读
LOG_FILE="/projects/management/tracker/test-results/memory-monitor.log"  # 日志文件路径
POLL_INTERVAL=10             # 检查间隔（秒）
PROCESS_NAME="firefox"       # 要监控的进程名
PROCESS_MATCHER="--browser=firefox"  # Playwright 浏览器匹配模式

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# 日志函数
# =============================================================================

log() {
    local level=$1
    shift
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*"
    echo "$message" >> "$LOG_FILE"
    echo -e "$message"
}

log_info() {
    log "INFO" "$GREEN$*$NC"
}

log_warn() {
    log "WARN" "$YELLOW$*$NC"
}

log_error() {
    log "ERROR" "$RED$*$NC"
}

# =============================================================================
# 内存检查函数
# =============================================================================

get_memory_usage_kb() {
    # 获取 Firefox 进程的内存使用（KB）
    # 匹配包含 --browser=firefox 的进程
    local mem_usage=$(ps aux 2>/dev/null | grep -E "$PROCESS_MATCHER" | grep -v grep | awk '{sum+=$6} END {print sum}')
    
    # 如果上面的方法没有结果，尝试简单的进程名匹配
    if [ -z "$mem_usage" ]; then
        mem_usage=$(ps aux 2>/dev/null | grep -i "$PROCESS_NAME" | grep -v grep | grep -v memory-monitor | awk '{sum+=$6} END {print sum}')
    fi
    
    echo "${mem_usage:-0}"
}

get_memory_usage_mb() {
    local kb=$1
    echo "scale=2; $kb / 1024" | bc 2>/dev/null || echo "0"
}

check_memory() {
    local mem_kb=$(get_memory_usage_kb)
    local mem_mb=$(get_memory_usage_mb "$mem_kb")
    
    # 检查内存是否超过限制
    if [ -n "$mem_kb" ] && [ "$mem_kb" -gt "$MAX_MEMORY_KB" ]; then
        return 1  # 内存超限
    fi
    
    return 0  # 内存正常
}

# =============================================================================
# 进程终止函数
# =============================================================================

terminate_firefox_processes() {
    log_warn "正在终止 Firefox 进程..."
    
    # 首先尝试优雅终止
    pkill -f "$PROCESS_MATCHER" 2>/dev/null || true
    
    # 等待进程结束
    sleep 2
    
    # 如果还有进程，强制终止
    local remaining=$(ps aux 2>/dev/null | grep -E "$PROCESS_MATCHER" | grep -v grep | wc -l)
    if [ "$remaining" -gt 0 ]; then
        log_warn "仍有 $remaining 个进程运行，强制终止..."
        pkill -9 -f "$PROCESS_MATCHER" 2>/dev/null || true
        sleep 1
    fi
    
    # 最终检查
    remaining=$(ps aux 2>/dev/null | grep -E "$PROCESS_MATCHER" | grep -v grep | wc -l)
    if [ "$remaining" -eq 0 ]; then
        log_info "所有 Firefox 进程已终止"
    else
        log_error "无法终止部分进程，请手动检查"
    fi
}

# =============================================================================
# 清理函数
# =============================================================================

cleanup() {
    log_info "收到终止信号，正在清理..."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# =============================================================================
# 主循环
# =============================================================================

main() {
    local loop_count=0
    local start_time=$(date +%s)
    
    # 确保日志目录存在
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log_info "=========================================="
    log_info "内存监控脚本启动"
    log_info "监控进程: $PROCESS_NAME"
    log_info "最大内存限制: ${MAX_MEMORY_MB}MB"
    log_info "检查间隔: ${POLL_INTERVAL}秒"
    log_info "日志文件: $LOG_FILE"
    log_info "=========================================="
    
    while true; do
        loop_count=$((loop_count + 1))
        local mem_kb=$(get_memory_usage_kb)
        local mem_mb=$(get_memory_usage_mb "$mem_kb")
        local elapsed=$(($(date +%s) - start_time))
        
        # 格式化输出
        local mem_mb_formatted=$(printf "%.1f" "$mem_mb")
        
        if check_memory; then
            # 内存正常
            if [ $((loop_count % 6)) -eq 0 ]; then
                # 每分钟输出一次状态（6次循环 * 10秒）
                log_info "[运行 ${elapsed}s] 内存使用: ${mem_mb_formatted}MB / ${MAX_MEMORY_MB}MB ✓"
            fi
        else
            # 内存超限
            log_error "=========================================="
            log_error "内存警告!"
            log_error "当前使用: ${mem_mb_formatted}MB"
            log_error "限制大小: ${MAX_MEMORY_MB}MB"
            log_error "超时时间: ${elapsed}s"
            log_error "=========================================="
            
            # 保存诊断信息
            log_info "保存诊断信息..."
            echo "=== 内存诊断报告 ===" >> "$LOG_FILE"
            echo "时间: $(date)" >> "$LOG_FILE"
            echo "内存使用: ${mem_kb}KB (${mem_mb_formatted}MB)" >> "$LOG_FILE"
            echo "限制: ${MAX_MEMORY_KB}KB" >> "$LOG_FILE"
            echo "" >> "$LOG_FILE"
            echo "相关进程:" >> "$LOG_FILE"
            ps aux | grep -E "$PROCESS_MATCHER" | grep -v grep >> "$LOG_FILE" 2>/dev/null
            
            # 终止进程
            terminate_firefox_processes
            
            log_error "由于内存超限，监控脚本将退出"
            log_error "建议: 增加系统内存或减少并发测试数量"
            
            # 退出代码 1 表示因内存问题退出
            exit 1
        fi
        
        # 等待下次检查
        sleep "$POLL_INTERVAL"
    done
}

# =============================================================================
# 快速检查模式
# =============================================================================

quick_check() {
    local mem_kb=$(get_memory_usage_kb)
    local mem_mb=$(get_memory_usage_mb "$mem_kb")
    
    echo "内存使用检查"
    echo "============"
    echo "当前使用: ${mem_kb}KB (${mem_mb}MB)"
    echo "限制: ${MAX_MEMORY_KB}KB (${MAX_MEMORY_MB}MB)"
    
    if [ -n "$mem_kb" ] && [ "$mem_kb" -gt "$MAX_MEMORY_KB" ]; then
        echo "状态: ⚠️ 超过限制"
        return 1
    else
        echo "状态: ✓ 正常"
        return 0
    fi
}

# =============================================================================
# 启动入口
# =============================================================================

# 检查是否传入了 quick-check 参数
if [ "$1" = "--quick" ] || [ "$1" = "-q" ]; then
    quick_check
else
    main
fi
