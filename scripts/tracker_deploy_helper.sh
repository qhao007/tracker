#!/bin/bash
# =============================================================================
# Tracker 离线开发环境迁移辅助脚本
# =============================================================================
#
# 用途：
#   帮助将 Tracker 开发环境迁移到无外网、无 sudo 的 Linux 服务器。
#   支持三种模式：
#     check     - 检查目标服务器环境，生成离线准备清单
#     prepare   - 在联网机器上根据清单准备离线迁移包
#     configure - 在目标服务器上根据离线包配置运行环境
#
# 用法：
#   ./scripts/tracker_deploy_helper.sh check [OPTIONS]
#   ./scripts/tracker_deploy_helper.sh prepare --manifest MANIFEST [OPTIONS]
#   ./scripts/tracker_deploy_helper.sh configure --bundle BUNDLE [OPTIONS]
#
# 设计文档：.claude/plans/validated-beaming-flask.md
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# 常量与默认值
# -----------------------------------------------------------------------------
SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT_DEFAULT="$(cd "$SCRIPT_DIR/.." && pwd)"

DEFAULT_TARGET_DIR="$HOME/tracker"
DEFAULT_MANIFEST="./tracker_manifest.json"
DEFAULT_BUNDLE="./tracker_offline_bundle.tar.gz"

REQUIREMENTS_DEFAULT=(
    "Flask>=3.0.0"
    "Flask-Session>=0.8.0"
    "gevent>=25.0.0"
    "gunicorn>=25.0.0"
    "requests>=2.31.0"
    "openpyxl>=3.1.0"
    "Pillow>=10.0.0"
)

# -----------------------------------------------------------------------------
# 颜色输出
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $*"
}

# -----------------------------------------------------------------------------
# 通用工具函数
# -----------------------------------------------------------------------------
fail() {
    log_error "$1"
    exit "${2:-1}"
}

cleanup() {
    if [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

trap cleanup EXIT

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查网络可达性（URL，超时秒数）
check_url_reachable() {
    local url="$1"
    local timeout="${2:-5}"
    if command_exists curl; then
        curl -fsS --max-time "$timeout" -I "$url" >/dev/null 2>&1
    elif command_exists wget; then
        wget --timeout="$timeout" --tries=1 -q --spider "$url" >/dev/null 2>&1
    else
        return 2
    fi
}

# 检查端口是否被占用
# 返回 0 表示可用，1 表示被占用
check_port_available() {
    local port="$1"
    if command_exists ss; then
        ! ss -tln 2>/dev/null | awk '{print $4}' | grep -qE ":${port}$"
    elif command_exists netstat; then
        ! netstat -tln 2>/dev/null | awk '{print $4}' | grep -qE ":${port}$"
    else
        # 没有工具，默认认为可用
        return 0
    fi
}

# 检查目录是否可写
# 返回 0 表示可写，1 表示不可写
check_writable() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        [[ -w "$dir" ]]
    else
        local parent
        parent="$(dirname "$dir")"
        [[ -w "$parent" ]]
    fi
}

# 读取 requirements.txt 内容到数组
read_requirements() {
    local req_file="$1"
    if [[ -f "$req_file" ]]; then
        grep -vE '^\s*(#|$)' "$req_file" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' || true
    else
        printf '%s\n' "${REQUIREMENTS_DEFAULT[@]}"
    fi
}

# 从 requirements 行解析包名和版本
parse_requirement() {
    local spec="$1"
    # 支持 Flask>=3.0.0, Flask==3.0.0, Flask ~=3.0.0 等
    local name spec_part
    name="$(echo "$spec" | sed -E 's/([A-Za-z0-9_.-]+).*/\1/')"
    spec_part="$(echo "$spec" | sed -E 's/[A-Za-z0-9_.-]+//')"
    echo "$name|$spec_part"
}

# 生成 JSON（使用 Python one-liner，避免 jq 依赖）
python_json() {
    python3 - "$@" <<'PYEOF'
import sys, json
# 参数：key value key value ...
args = sys.argv[1:]
obj = {}
for i in range(0, len(args), 2):
    k = args[i]
    v = args[i+1]
    try:
        v = json.loads(v)
    except Exception:
        pass
    obj[k] = v
print(json.dumps(obj, indent=2, ensure_ascii=False))
PYEOF
}

# 读取 JSON 字段
json_get() {
    local file="$1"
    local key="$2"
    python3 -c "import json,sys; print(json.load(open('$file')).get('$key',''))"
}

# 获取 JSON 嵌套字段（点号分隔）
json_get_nested() {
    local file="$1"
    local path="$2"
    python3 -c "
import json,sys
data = json.load(open('$file'))
for part in '$path'.split('.'):
    if isinstance(data, dict) and part in data:
        data = data[part]
    else:
        data = ''
        break
print(data if not isinstance(data, (dict,list)) else json.dumps(data, ensure_ascii=False))
"
}

# 平台标签映射（根据 OS arch）
map_arch_to_platform() {
    local arch="$1"
    case "$arch" in
        x86_64|amd64) echo "manylinux2014_x86_64" ;;
        aarch64|arm64) echo "manylinux2014_aarch64" ;;
        *) echo "" ;;
    esac
}

# 检查 Python 版本是否满足 Flask>=3.0 的要求（>=3.8）
check_python_version_ok() {
    local version="$1"
    local major minor
    major="$(echo "$version" | cut -d. -f1)"
    minor="$(echo "$version" | cut -d. -f2)"
    if [[ "$major" -gt 3 ]] || { [[ "$major" -eq 3 && "$minor" -ge 8 ]]; }; then
        return 0
    fi
    return 1
}

# -----------------------------------------------------------------------------
# 使用说明
# -----------------------------------------------------------------------------
usage() {
    cat <<EOF
Tracker 离线开发环境迁移辅助脚本

用法：
  $SCRIPT_NAME check [OPTIONS]
  $SCRIPT_NAME prepare --manifest MANIFEST [OPTIONS]
  $SCRIPT_NAME configure --bundle BUNDLE [OPTIONS]

模式说明：
  check      检查目标服务器环境并生成离线准备清单（默认模式）
  prepare    在联网机器上根据清单准备离线迁移包
  configure  在目标服务器上根据离线包配置运行环境

选项：
  check 模式：
    --output MANIFEST          输出清单文件路径（默认：$DEFAULT_MANIFEST）
    --project-dir DIR          项目源码目录，用于读取 requirements.txt
    --target-dir DIR           目标部署目录（默认：$DEFAULT_TARGET_DIR）

  prepare 模式：
    --manifest MANIFEST        必填，由 check 模式生成的清单文件
    --output BUNDLE            输出离线包路径（默认：$DEFAULT_BUNDLE）
    --source-dir DIR           源码目录（默认：脚本所在项目根目录）
    --include-playwright-browsers  在离线包中包含 Playwright 浏览器
    --skip-node-modules        不在离线包中包含 node_modules
    --exclude-git              不在离线包中包含 .git 目录

  configure 模式：
    --bundle BUNDLE            必填，由 prepare 模式生成的离线包
    --target-dir DIR           目标部署目录（默认：$DEFAULT_TARGET_DIR）
    --port PORT                服务端口（默认：8081）
    --adapt-paths MODE         路径适配模式：patch|symlink|env（默认：patch）
    --run-now                  配置完成后立即启动测试服务

通用选项：
    -h, --help                 显示此帮助信息

示例：
  # 在目标服务器检查环境
  $SCRIPT_NAME check --target-dir /home/user/tracker

  # 在联网机器准备离线包
  $SCRIPT_NAME prepare --manifest tracker_manifest.json --output bundle.tar.gz

  # 在目标服务器配置环境
  $SCRIPT_NAME configure --bundle bundle.tar.gz --target-dir /home/user/tracker --run-now
EOF
}

# -----------------------------------------------------------------------------
# 命令行参数解析
# -----------------------------------------------------------------------------
MODE=""
ARG_MANIFEST="$DEFAULT_MANIFEST"
ARG_BUNDLE="$DEFAULT_BUNDLE"
ARG_TARGET_DIR="$DEFAULT_TARGET_DIR"
ARG_PROJECT_DIR=""
ARG_SOURCE_DIR="$PROJECT_ROOT_DEFAULT"
ARG_OUTPUT=""
ARG_PORT="8081"
ARG_ADAPT_PATHS="patch"
ARG_INCLUDE_PLAYWRIGHT_BROWSERS=false
ARG_SKIP_NODE_MODULES=false
ARG_EXCLUDE_GIT=false
ARG_RUN_NOW=false

parse_args() {
    if [[ $# -eq 0 ]]; then
        MODE="check"
        return 0
    fi

    # 第一个非选项参数是模式
    case "$1" in
        check|prepare|configure)
            MODE="$1"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            # 未指定模式，默认 check
            MODE="check"
            ;;
        *)
            fail "未知模式：$1。请使用 check、prepare 或 configure。"
            ;;
    esac

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --manifest)
                ARG_MANIFEST="$2"
                shift 2
                ;;
            --bundle)
                ARG_BUNDLE="$2"
                shift 2
                ;;
            --output)
                ARG_OUTPUT="$2"
                shift 2
                ;;
            --project-dir)
                ARG_PROJECT_DIR="$2"
                shift 2
                ;;
            --target-dir)
                ARG_TARGET_DIR="$2"
                shift 2
                ;;
            --source-dir)
                ARG_SOURCE_DIR="$2"
                shift 2
                ;;
            --port)
                ARG_PORT="$2"
                shift 2
                ;;
            --adapt-paths)
                ARG_ADAPT_PATHS="$2"
                shift 2
                ;;
            --include-playwright-browsers)
                ARG_INCLUDE_PLAYWRIGHT_BROWSERS=true
                shift
                ;;
            --skip-node-modules)
                ARG_SKIP_NODE_MODULES=true
                shift
                ;;
            --exclude-git)
                ARG_EXCLUDE_GIT=true
                shift
                ;;
            --run-now)
                ARG_RUN_NOW=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                fail "未知选项：$1"
                ;;
        esac
    done

    # 设置默认输出
    if [[ -z "$ARG_OUTPUT" ]]; then
        case "$MODE" in
            check) ARG_OUTPUT="$DEFAULT_MANIFEST" ;;
            prepare) ARG_OUTPUT="$DEFAULT_BUNDLE" ;;
        esac
    fi

    # 校验模式必填参数
    case "$MODE" in
        prepare)
            [[ -f "$ARG_MANIFEST" ]] || fail "prepare 模式需要有效的 --manifest 文件：$ARG_MANIFEST"
            ;;
        configure)
            [[ -f "$ARG_BUNDLE" ]] || fail "configure 模式需要有效的 --bundle 文件：$ARG_BUNDLE"
            ;;
    esac

    # 校验 adapt-paths
    case "$ARG_ADAPT_PATHS" in
        patch|symlink|env) ;;
        *) fail "--adapt-paths 必须是 patch、symlink 或 env 之一" ;;
    esac
}

# -----------------------------------------------------------------------------
# check 模式
# -----------------------------------------------------------------------------
mode_check() {
    log_step "运行检查模式（check）..."

    local manifest_file="$ARG_OUTPUT"
    local target_dir="$ARG_TARGET_DIR"
    local project_dir="${ARG_PROJECT_DIR:-$PROJECT_ROOT_DEFAULT}"
    local req_file="$project_dir/dev/requirements.txt"

    log_info "目标部署目录：$target_dir"
    log_info "项目源码目录：$project_dir"

    # 1. OS 信息
    local os_id="unknown" os_version="unknown" os_arch kernel
    if [[ -f /etc/os-release ]]; then
        os_id="$(source /etc/os-release && echo "$ID")"
        os_version="$(source /etc/os-release && echo "$VERSION_ID")"
    fi
    os_arch="$(uname -m)"
    kernel="$(uname -r)"

    # 2. Python 信息
    local py_version="" py_exec="" py_mm="" pip_version="" venv_module=false py_ok=false
    if command_exists python3; then
        py_exec="$(command -v python3)"
        py_version="$(python3 --version 2>&1 | awk '{print $2}')"
        py_mm="$(echo "$py_version" | cut -d. -f1,2)"
        if python3 -m venv --help >/dev/null 2>&1; then
            venv_module=true
        fi
        if command_exists pip || python3 -m pip --version >/dev/null 2>&1; then
            pip_version="$(python3 -m pip --version 2>/dev/null | awk '{print $2}' || echo "unknown")"
        fi
        if check_python_version_ok "$py_version"; then
            py_ok=true
        fi
    fi

    # 3. SQLite 版本
    local sqlite_version=""
    if command_exists python3; then
        sqlite_version="$(python3 -c "import sqlite3; print(sqlite3.sqlite_version)" 2>/dev/null || echo "")"
    fi

    # 4. Node/npm 信息
    local node_available=false node_version="" npm_version="" node_modules_present=false
    if command_exists node; then
        node_available=true
        node_version="$(node --version 2>/dev/null || echo "")"
    fi
    if command_exists npm; then
        npm_version="$(npm --version 2>/dev/null || echo "")"
    fi
    if [[ -d "$project_dir/dev/node_modules" ]]; then
        node_modules_present=true
    fi

    # 5. Playwright 信息
    local pw_available=false pw_browsers_dir="" pw_browsers_installed=false
    if [[ -d "$project_dir/dev/node_modules/@playwright/test" ]]; then
        pw_available=true
    fi
    if [[ -d "$project_dir/dev/.playwright-browsers" ]]; then
        pw_browsers_dir="$project_dir/dev/.playwright-browsers"
        pw_browsers_installed=true
    fi

    # 6. 网络状态
    local pypi_reachable=false npm_reachable=false internet_reachable=false
    if check_url_reachable "https://pypi.org/simple"; then
        pypi_reachable=true
    fi
    if check_url_reachable "https://registry.npmjs.org"; then
        npm_reachable=true
    fi
    if check_url_reachable "https://www.google.com"; then
        internet_reachable=true
    fi

    # 7. 端口
    local port_8080="available" port_8081="available"
    if ! check_port_available 8080; then port_8080="occupied"; fi
    if ! check_port_available 8081; then port_8081="occupied"; fi

    # 8. 磁盘
    local home_free_gb="0"
    if command_exists df; then
        home_free_gb="$(df -BG "$HOME" 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/G//' || echo "0")"
    fi

    # 9. 权限
    local can_write_tracker_root=false can_write_release_dir=false can_write_systemd=false
    if check_writable "/projects/management/tracker"; then can_write_tracker_root=true; fi
    if check_writable "/release/tracker"; then can_write_release_dir=true; fi
    if check_writable "/etc/systemd/system/tracker.service"; then can_write_systemd=true; fi

    # 10. requirements
    local req_json=""
    req_json="$(read_requirements "$req_file" | while read -r line; do
        local parsed name spec
        parsed="$(parse_requirement "$line")"
        name="$(echo "$parsed" | cut -d'|' -f1)"
        spec="$(echo "$parsed" | cut -d'|' -f2)"
        echo "{\"name\":\"$name\",\"spec\":\"$spec\"}"
    done | paste -sd',' | sed 's/^/[/' | sed 's/$/]/')"

    # 11. 生成建议
    local notes="[]"
    local note_list=()
    if [[ "$py_ok" != "true" ]]; then
        note_list+=("Python 版本过低（$py_version），需要 3.8+")
    fi
    if [[ "$node_available" != "true" ]]; then
        note_list+=("未检测到 Node.js，前端检查与 Playwright 测试将不可用")
    fi
    if [[ "$pypi_reachable" != "true" && "$npm_reachable" != "true" ]]; then
        note_list+=("目标服务器无法访问外网，请使用 prepare 模式准备离线包")
    fi
    if [[ "$can_write_release_dir" != "true" || "$can_write_systemd" != "true" ]]; then
        note_list+=("无 sudo 权限，release.py 的 systemd 发布功能不可用，可使用 start_server_test.sh 本地启动")
    fi

    notes="$(printf '%s\n' "${note_list[@]}" | python3 -c 'import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))')"

    # 12. 生成 manifest JSON
    python3 - "$manifest_file" "$target_dir" "$os_id" "$os_version" "$os_arch" "$kernel" \
        "$py_version" "$py_mm" "$py_exec" "$pip_version" "$venv_module" "$py_ok" \
        "$sqlite_version" "$node_available" "$node_version" "$npm_version" "$node_modules_present" \
        "$pw_available" "$pw_browsers_dir" "$pw_browsers_installed" \
        "$pypi_reachable" "$npm_reachable" "$internet_reachable" \
        "$port_8080" "$port_8081" "$home_free_gb" \
        "$can_write_tracker_root" "$can_write_release_dir" "$can_write_systemd" \
        "$req_json" "$notes" <<'PYEOF'
import sys, json
from datetime import datetime, timezone

mf, target_dir, os_id, os_version, os_arch, kernel, \
py_version, py_mm, py_exec, pip_version, venv_module, py_ok, \
sqlite_version, node_available, node_version, npm_version, node_modules_present, \
pw_available, pw_browsers_dir, pw_browsers_installed, \
pypi_reachable, npm_reachable, internet_reachable, \
port_8080, port_8081, home_free_gb, \
can_write_tracker_root, can_write_release_dir, can_write_systemd, \
req_json, notes = sys.argv[1:]

def to_bool(s):
    return s.lower() == 'true'

data = {
    "generated_at": datetime.now(timezone.utc).astimezone().isoformat(),
    "hostname": __import__('socket').gethostname(),
    "os": {
        "id": os_id,
        "version_id": os_version,
        "arch": os_arch,
        "kernel": kernel
    },
    "python": {
        "version": py_version,
        "major_minor": py_mm,
        "executable": py_exec,
        "pip_version": pip_version,
        "venv_module": to_bool(venv_module),
        "version_ok": to_bool(py_ok)
    },
    "sqlite_version": sqlite_version,
    "node": {
        "available": to_bool(node_available),
        "version": node_version,
        "npm_version": npm_version,
        "node_modules_present": to_bool(node_modules_present)
    },
    "playwright": {
        "available": to_bool(pw_available),
        "browsers_dir": pw_browsers_dir,
        "browsers_installed": to_bool(pw_browsers_installed)
    },
    "network": {
        "pypi_reachable": to_bool(pypi_reachable),
        "npm_reachable": to_bool(npm_reachable),
        "internet_reachable": to_bool(internet_reachable)
    },
    "ports": {
        "8080": port_8080,
        "8081": port_8081
    },
    "disk": {
        "home_free_gb": float(home_free_gb) if home_free_gb.replace('.','',1).isdigit() else 0,
        "target_dir": target_dir
    },
    "privileges": {
        "can_write_tracker_root": to_bool(can_write_tracker_root),
        "can_write_release_dir": to_bool(can_write_release_dir),
        "can_write_systemd": to_bool(can_write_systemd)
    },
    "requirements": json.loads(req_json) if req_json.strip() else [],
    "notes": json.loads(notes) if notes.strip() else []
}

with open(mf, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(json.dumps(data, indent=2, ensure_ascii=False))
PYEOF

    log_info "清单已生成：$manifest_file"

    # 打印关键结论
    echo ""
    echo "=== 检查结论 ==="
    echo "操作系统：$os_id $os_version ($os_arch)"
    echo "Python：$py_version ($py_exec)"
    echo "Node.js：$node_version"
    echo "外网访问：pypi=$pypi_reachable, npm=$npm_reachable"
    echo "端口 8080/8081：$port_8080 / $port_8081"
    echo "Home 可用空间：${home_free_gb}G"
    echo ""

    if [[ ${#note_list[@]} -gt 0 ]]; then
        log_warn "注意事项："
        for note in "${note_list[@]}"; do
            echo "  - $note"
        done
    else
        log_info "环境检查通过，可以直接部署。"
    fi
}

# -----------------------------------------------------------------------------
# prepare 模式
# -----------------------------------------------------------------------------
mode_prepare() {
    log_step "运行准备模式（prepare）..."

    local manifest_file="$ARG_MANIFEST"
    local bundle_file="$ARG_OUTPUT"
    local source_dir="$ARG_SOURCE_DIR"

    log_info "清单文件：$manifest_file"
    log_info "源码目录：$source_dir"
    log_info "输出离线包：$bundle_file"

    # 1. 读取并校验清单
    local py_mm os_arch target_dir
    py_mm="$(json_get_nested "$manifest_file" "python.major_minor")"
    os_arch="$(json_get_nested "$manifest_file" "os.arch")"
    target_dir="$(json_get_nested "$manifest_file" "disk.target_dir")"

    [[ -n "$py_mm" ]] || fail "清单中缺少 python.major_minor"
    [[ -n "$os_arch" ]] || fail "清单中缺少 os.arch"

    local platform_tag
    platform_tag="$(map_arch_to_platform "$os_arch")"
    [[ -n "$platform_tag" ]] || fail "不支持的架构：$os_arch"

    # 2. 检查本机联网
    log_info "检查打包机网络..."
    if ! check_url_reachable "https://pypi.org/simple"; then
        fail "打包机无法访问 pypi.org，无法准备离线包"
    fi

    # 3. 创建临时工作目录
    TEMP_DIR="$(mktemp -d)"
    local bundle_root="$TEMP_DIR/tracker_offline_bundle"
    mkdir -p "$bundle_root/src" "$bundle_root/wheels" "$bundle_root/config"

    # 4. 拷贝源码
    log_info "拷贝项目源码..."
    local rsync_opts=(-a --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' --exclude='test-results' --exclude='pw-output' --exclude='shared/data/user_data' --exclude='shared/data/user_data_backup*')
    if [[ "$ARG_EXCLUDE_GIT" == "true" ]]; then
        rsync_opts+=(--exclude='.git')
    fi
    if [[ "$ARG_SKIP_NODE_MODULES" == "true" ]]; then
        rsync_opts+=(--exclude='node_modules')
    fi
    if [[ "$ARG_INCLUDE_PLAYWRIGHT_BROWSERS" != "true" ]]; then
        rsync_opts+=(--exclude='.playwright-browsers')
    fi

    if command_exists rsync; then
        rsync "${rsync_opts[@]}" "$source_dir/" "$bundle_root/src/tracker/"
    else
        cp -r "$source_dir" "$bundle_root/src/tracker"
        # 简单清理（如需要可扩展）
        find "$bundle_root/src/tracker" -type d \( -name __pycache__ -o -name .pytest_cache \) -exec rm -rf {} + 2>/dev/null || true
    fi

    # 保留 user_data 空目录结构（不拷贝内容）
    mkdir -p "$bundle_root/src/tracker/shared/data/user_data"

    # 5. 拷贝 node_modules（如果未跳过且存在）
    if [[ "$ARG_SKIP_NODE_MODULES" != "true" ]]; then
        if [[ -d "$source_dir/dev/node_modules" ]]; then
            log_info "拷贝 node_modules..."
            if command_exists rsync; then
                rsync -a "$source_dir/dev/node_modules/" "$bundle_root/src/tracker/dev/node_modules/"
            else
                cp -r "$source_dir/dev/node_modules" "$bundle_root/src/tracker/dev/node_modules"
            fi
        else
            log_warn "源码目录中未找到 dev/node_modules，离线包将不包含前端依赖"
        fi
    fi

    # 6. 拷贝 Playwright 浏览器（如果指定）
    if [[ "$ARG_INCLUDE_PLAYWRIGHT_BROWSERS" == "true" ]]; then
        if [[ -d "$source_dir/dev/.playwright-browsers" ]]; then
            log_info "拷贝 Playwright 浏览器..."
            if command_exists rsync; then
                rsync -a "$source_dir/dev/.playwright-browsers/" "$bundle_root/src/tracker/dev/.playwright-browsers/"
            else
                cp -r "$source_dir/dev/.playwright-browsers" "$bundle_root/src/tracker/dev/.playwright-browsers"
            fi
        else
            log_warn "源码目录中未找到 dev/.playwright-browsers"
        fi
    fi

    # 7. 下载 Python wheels
    log_info "下载 Python 依赖 wheel（目标 Python $py_mm，平台 $platform_tag）..."
    local req_file="$source_dir/dev/requirements.txt"
    if [[ ! -f "$req_file" ]]; then
        fail "未找到 requirements.txt：$req_file"
    fi

    pip download \
        --python-version "$py_mm" \
        --platform "$platform_tag" \
        --only-binary=:all: \
        -d "$bundle_root/wheels" \
        -r "$req_file" || {
        log_warn "纯二进制下载失败，尝试允许源码包..."
        pip download \
            --python-version "$py_mm" \
            --platform "$platform_tag" \
            -d "$bundle_root/wheels" \
            -r "$req_file"
    }

    # 8. 校验 wheels 是否完整
    log_info "校验 Python 依赖完整性..."
    python3 -m venv "$TEMP_DIR/test_venv"
    # shellcheck disable=SC1091
    source "$TEMP_DIR/test_venv/bin/activate"
    if ! pip install --no-index --find-links "$bundle_root/wheels" -r "$req_file" >/dev/null 2>&1; then
        deactivate || true
        fail "wheel 包无法覆盖 requirements.txt 中的所有依赖"
    fi
    deactivate || true

    # 9. 校验 node_modules（如果包含）
    if [[ "$ARG_SKIP_NODE_MODULES" != "true" && -d "$bundle_root/src/tracker/dev/node_modules" ]]; then
        log_info "校验 node_modules 完整性..."
        local pkg_name
        for pkg_name in $(python3 -c "import json; print(' '.join(json.load(open('$source_dir/dev/package.json')).get('devDependencies', {}).keys()))"); do
            if [[ ! -d "$bundle_root/src/tracker/dev/node_modules/$pkg_name" ]]; then
                log_warn "node_modules 中缺少包：$pkg_name"
            fi
        done
    fi

    # 10. 拷贝 manifest
    cp "$manifest_file" "$bundle_root/manifest.json"

    # 11. 打包
    log_info "打包离线迁移包..."
    local bundle_dir
    bundle_dir="$(dirname "$bundle_file")"
    mkdir -p "$bundle_dir"
    tar czvf "$bundle_file" -C "$TEMP_DIR" "tracker_offline_bundle"

    local bundle_size
    bundle_size="$(du -sh "$bundle_file" | cut -f1)"
    log_info "离线包已生成：$bundle_file（大小：$bundle_size）"
    echo ""
    echo "=== 离线包内容摘要 ==="
    echo "源码目录：tracker_offline_bundle/src/tracker/"
    echo "Python wheels：tracker_offline_bundle/wheels/"
    echo "清单：tracker_offline_bundle/manifest.json"
    echo ""
    echo "下一步：将 $bundle_file 拷贝到目标服务器，运行："
    echo "  $SCRIPT_NAME configure --bundle $bundle_file --target-dir $target_dir"
}

# -----------------------------------------------------------------------------
# configure 模式
# -----------------------------------------------------------------------------
mode_configure() {
    log_step "运行配置模式（configure）..."

    local bundle_file="$ARG_BUNDLE"
    local target_dir="$ARG_TARGET_DIR"
    local port="$ARG_PORT"
    local adapt_mode="$ARG_ADAPT_PATHS"

    log_info "离线包：$bundle_file"
    log_info "目标目录：$target_dir"
    log_info "服务端口：$port"
    log_info "路径适配模式：$adapt_mode"

    # 1. 检查目标目录
    if [[ -e "$target_dir" && ! -d "$target_dir" ]]; then
        fail "目标路径已存在且不是目录：$target_dir"
    fi
    mkdir -p "$target_dir"

    # 2. 解压 bundle
    TEMP_DIR="$(mktemp -d)"
    log_info "解压离线包..."
    tar xzvf "$bundle_file" -C "$TEMP_DIR" >/dev/null

    local bundle_root="$TEMP_DIR/tracker_offline_bundle"
    [[ -d "$bundle_root" ]] || fail "离线包结构异常，未找到 tracker_offline_bundle/"

    # 3. 校验清单
    local manifest_file="$bundle_root/manifest.json"
    [[ -f "$manifest_file" ]] || fail "离线包中缺少 manifest.json"

    local manifest_py_mm manifest_arch
    manifest_py_mm="$(json_get_nested "$manifest_file" "python.major_minor")"
    manifest_arch="$(json_get_nested "$manifest_file" "os.arch")"

    local local_py_mm local_arch
    local_py_mm="$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)"
    local_arch="$(uname -m)"

    if [[ "$local_py_mm" != "$manifest_py_mm" ]]; then
        log_warn "本地 Python 版本（$local_py_mm）与清单（$manifest_py_mm）不一致，可能安装失败"
    fi

    # 4. 校验关键文件
    local src_dir="$bundle_root/src/tracker"
    for f in dev/wsgi.py dev/gunicorn.conf.py dev/index.html dev/start_server_test.sh dev/requirements.txt; do
        [[ -f "$src_dir/$f" ]] || fail "源码中缺少关键文件：$f"
    done

    # 5. 拷贝源码到目标目录
    log_info "拷贝源码到目标目录..."
    if [[ -d "$target_dir/dev" ]]; then
        log_warn "目标目录已存在 dev/，将进行覆盖"
    fi
    cp -a "$src_dir/." "$target_dir/"

    # 6. 创建 Python venv 并安装依赖
    log_info "创建 Python 虚拟环境..."
    python3 -m venv "$target_dir/venv"
    # shellcheck disable=SC1091
    source "$target_dir/venv/bin/activate"

    log_info "离线安装 Python 依赖..."
    pip install --no-index --find-links "$bundle_root/wheels" -r "$target_dir/dev/requirements.txt"

    # 测试导入
    log_info "验证 Flask 应用可导入..."
    (cd "$target_dir/dev" && python -c "from app import create_app; print('app import OK')")

    deactivate || true

    # 7. 创建日志和数据目录
    mkdir -p "$target_dir/logs"
    mkdir -p "$target_dir/dev/data"
    mkdir -p "$target_dir/shared/data/user_data"
    mkdir -p "$target_dir/test-results"

    # 8. 路径适配
    case "$adapt_mode" in
        patch)
            adapt_paths_patch "$target_dir"
            ;;
        symlink)
            adapt_paths_symlink "$target_dir"
            ;;
        env)
            log_info "使用 env 模式，不修改原脚本，仅生成 tracker_env.sh"
            ;;
    esac

    # 9. 生成 tracker_env.sh
    generate_tracker_env "$target_dir" "$port"

    # 10. 可选：启动服务
    if [[ "$ARG_RUN_NOW" == "true" ]]; then
        log_info "启动测试服务..."
        if [[ -f "$target_dir/dev/start_server_test.sh" ]]; then
            bash "$target_dir/dev/start_server_test.sh"
        else
            log_warn "未找到 start_server_test.sh，跳过启动"
        fi
    fi

    log_info "环境配置完成：$target_dir"
    echo ""
    echo "=== 使用说明 ==="
    echo "1. 激活环境：source $target_dir/tracker_env.sh"
    echo "2. 启动测试服务：bash $target_dir/dev/start_server_test.sh"
    echo "3. 访问服务：http://localhost:$port"
    echo "4. 查看日志：$target_dir/logs/"
    echo ""

    if [[ "$adapt_mode" == "patch" ]]; then
        echo "注意：已对以下脚本进行路径适配："
        echo "  - dev/start_server_test.sh"
        echo "  - dev/gunicorn.conf.py"
        echo "  - dev/playwright.config.ts"
        echo "  - scripts/memory-monitor.sh"
        echo ""
    fi

    echo "注意：scripts/release.py 的 systemd 发布功能需要 sudo，当前环境如未授权则不可用。"
}

# 使用 sed 替换目标目录中的硬编码路径
adapt_paths_patch() {
    local target_dir="$1"
    local abs_target_dir
    abs_target_dir="$(cd "$target_dir" && pwd)"

    log_info "执行路径适配（patch 模式）：/projects/management/tracker -> $abs_target_dir"

    local files_to_patch=(
        "dev/start_server_test.sh"
        "dev/gunicorn.conf.py"
        "dev/playwright.config.ts"
        "scripts/memory-monitor.sh"
    )

    for rel_file in "${files_to_patch[@]}"; do
        local file_path="$target_dir/$rel_file"
        if [[ -f "$file_path" ]]; then
            log_info "  适配：$rel_file"
            # 替换项目根目录
            sed -i "s|/projects/management/tracker|$abs_target_dir|g" "$file_path"
            # 替换 hqi 日志目录
            sed -i "s|/home/hqi/logs|$abs_target_dir/logs|g" "$file_path"
            # 替换 /var/log/tracker_ 日志路径
            sed -i "s|/var/log/tracker_|$abs_target_dir/logs/tracker_|g" "$file_path"
        fi
    done

    # 对 release.py 中的系统路径给出警告（不修改）
    local release_py="$target_dir/scripts/release.py"
    if [[ -f "$release_py" ]] && grep -qE '/release/tracker|/etc/systemd/system/tracker.service' "$release_py"; then
        log_warn "scripts/release.py 仍包含需要 root 的系统路径（/release/tracker、/etc/systemd/system/tracker.service），未做修改"
    fi
}

# 创建符号链接（需要父目录写权限，通常无 sudo 不可用）
adapt_paths_symlink() {
    local target_dir="$1"
    local abs_target_dir
    abs_target_dir="$(cd "$target_dir" && pwd)"

    log_info "执行路径适配（symlink 模式）：创建 /projects/management/tracker -> $abs_target_dir"

    local tracker_root="/projects/management/tracker"
    if [[ -e "$tracker_root" ]]; then
        log_warn "$tracker_root 已存在，跳过创建软链"
    else
        local parent_dir
        parent_dir="$(dirname "$tracker_root")"
        if [[ -w "$parent_dir" ]]; then
            mkdir -p "$parent_dir"
            ln -s "$abs_target_dir" "$tracker_root"
            log_info "已创建软链：$tracker_root -> $abs_target_dir"
        else
            log_warn "无权限写入 $parent_dir，symlink 模式失败，将回退到 patch 模式"
            adapt_paths_patch "$target_dir"
        fi
    fi
}

# 生成 tracker_env.sh 环境文件
generate_tracker_env() {
    local target_dir="$1"
    local port="$2"

    log_info "生成环境文件：$target_dir/tracker_env.sh"

    cat > "$target_dir/tracker_env.sh" <<EOF
# Tracker 环境变量文件
# 用法：source $target_dir/tracker_env.sh

export TRACKER_ROOT="$target_dir"
export TRACKER_VENV="$target_dir/venv"
export TRACKER_PORT="$port"
export PLAYWRIGHT_BROWSERS_PATH="$target_dir/dev/.playwright-browsers"

# 激活 Python 虚拟环境
if [ -f "\$TRACKER_VENV/bin/activate" ]; then
    source "\$TRACKER_VENV/bin/activate"
fi

# 便捷 alias
alias tracker-start="bash \$TRACKER_ROOT/dev/start_server_test.sh"
alias tracker-logs="tail -f \$TRACKER_ROOT/logs/tracker_error_\${TRACKER_PORT}.log"
alias tracker-test-api="cd \$TRACKER_ROOT/dev && PYTHONPATH=. pytest tests/test_api/ -v"
alias tracker-test-ui="cd \$TRACKER_ROOT/dev && npx playwright test tests/test_ui/specs/smoke/ --project=firefox"

echo "Tracker 环境已激活，根目录：\$TRACKER_ROOT"
echo "可用命令：tracker-start, tracker-logs, tracker-test-api, tracker-test-ui"
EOF

    chmod +x "$target_dir/tracker_env.sh"
}

# -----------------------------------------------------------------------------
# 主入口
# -----------------------------------------------------------------------------
main() {
    parse_args "$@"

    case "$MODE" in
        check)
            mode_check
            ;;
        prepare)
            mode_prepare
            ;;
        configure)
            mode_configure
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
