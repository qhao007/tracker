# Tracker 离线开发环境迁移脚本使用指南

> 文档位置：`docs/OPERATIONS/tracker_offline_migration_guide.md`  
> 适用版本：Tracker v0.x.x  
> 最后更新：2026-07-06  
> 署名：Claude Code

---

## 1. 概述

`scripts/tracker_deploy_helper.sh` 是 Tracker 项目的离线开发环境迁移辅助脚本。它用于将当前 Tracker 开发环境完整迁移到**无法连接外网、普通用户没有 sudo 权限**的 Linux 服务器上，并确保迁移后的环境可以继续使用项目现有的开发、测试和发布脚本。

脚本提供三种模式：

| 模式 | 作用 | 运行位置 |
|------|------|----------|
| `check`（默认） | 检查目标服务器环境并生成离线准备清单 | 目标服务器（可离线） |
| `prepare` | 根据清单下载依赖并打包完整离线迁移包 | 联网打包机 |
| `configure` | 解压离线包、安装依赖、适配路径、生成启动入口 | 目标服务器（离线） |

---

## 2. 适用场景

- 目标服务器处于内网，无法访问 PyPI、npm 等外部仓库。
- 目标服务器上只有普通用户账号，无法使用 `sudo` 安装系统级软件。
- 需要把当前 Tracker 代码、Python 依赖、前端开发依赖一并迁移到新服务器。
- 迁移完成后，希望继续使用 `start_server_test.sh`、`check_frontent.sh`、`pytest`、`playwright` 等现有脚本。

---

## 3. 前置条件

### 3.1 目标服务器

| 项目 | 要求 |
|------|------|
| 操作系统 | Linux（x86_64 或 aarch64） |
| Python | 3.8 或更高版本 |
| SQLite | Python 内置，通常无需额外安装 |
| 磁盘空间 | 建议 ≥ 5GB（含源码、依赖、数据） |
| 端口 | 8080/8081 未被占用 |
| 网络 | 无需外网，也无需 sudo |

### 3.2 联网打包机

| 项目 | 要求 |
|------|------|
| 操作系统 | 建议与目标服务器同架构（x86_64/aarch64） |
| Python | 3.x，带有 pip |
| 网络 | 可访问 `https://pypi.org/simple` |
| 工具 | `bash`、`tar`、`curl` 或 `wget`；推荐 `rsync` |

### 3.3 可选但建议

- 目标服务器预装 Node.js/npm，以便运行前端检查和 Playwright 测试。
- 如需 UI 测试，目标服务器需有 Playwright 浏览器；可通过 `--include-playwright-browsers` 打包到离线包中。

---

## 4. 快速开始

### 4.1 在目标服务器生成清单

```bash
# 把脚本拷贝到目标服务器，或直接手写相同命令
./scripts/tracker_deploy_helper.sh check --target-dir /home/user/tracker
```

执行后会生成 `tracker_manifest.json`，记录目标机的 Python 版本、架构、端口、磁盘、权限等信息。

### 4.2 把清单传回联网打包机

```bash
# 在目标服务器
scp tracker_manifest.json user@packager:/path/to/workspace/
```

### 4.3 在联网打包机准备离线包

```bash
# 在打包机（与 Tracker 源码同一台机器）
./scripts/tracker_deploy_helper.sh prepare \
  --manifest tracker_manifest.json \
  --output tracker_offline_bundle.tar.gz
```

### 4.4 把离线包传到目标服务器

```bash
# 在打包机
scp tracker_offline_bundle.tar.gz user@target:/home/user/
```

### 4.5 在目标服务器配置环境

```bash
# 在目标服务器
./scripts/tracker_deploy_helper.sh configure \
  --bundle tracker_offline_bundle.tar.gz \
  --target-dir /home/user/tracker \
  --run-now
```

配置完成后，可以通过 `http://localhost:8081` 访问测试服务。

---

## 5. 命令详解

### 5.1 check 模式

```bash
./scripts/tracker_deploy_helper.sh check [OPTIONS]
```

**选项：**

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--output MANIFEST` | 输出清单文件路径 | `./tracker_manifest.json` |
| `--project-dir DIR` | 项目源码目录，用于读取 `requirements.txt` | 脚本所在项目根目录 |
| `--target-dir DIR` | 目标部署目录 | `$HOME/tracker` |

**示例：**

```bash
./scripts/tracker_deploy_helper.sh check \
  --output /tmp/tracker_manifest.json \
  --target-dir /home/user/tracker
```

**输出说明：**

清单 `tracker_manifest.json` 包含以下信息：

- 操作系统发行版、版本、架构、内核
- Python 版本、路径、pip 版本、是否支持 venv
- SQLite 版本
- Node.js/npm 版本
- Playwright 浏览器状态
- 外网可达性（PyPI/npm/Internet）
- 8080/8081 端口占用情况
- Home 目录可用空间
- 是否可写入 `/projects/management/tracker`、`/release/tracker`、`/etc/systemd/system/tracker.service`
- `requirements.txt` 依赖列表
- 注意事项与建议

### 5.2 prepare 模式

```bash
./scripts/tracker_deploy_helper.sh prepare --manifest MANIFEST [OPTIONS]
```

**必填选项：**

| 选项 | 说明 |
|------|------|
| `--manifest MANIFEST` | 由 `check` 模式生成的清单文件 |

**可选选项：**

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--output BUNDLE` | 输出离线包路径 | `./tracker_offline_bundle.tar.gz` |
| `--source-dir DIR` | 源码目录 | 脚本所在项目根目录 |
| `--include-playwright-browsers` | 在离线包中包含 Playwright 浏览器 | 默认不包含 |
| `--skip-node-modules` | 不打包 `dev/node_modules` | 默认打包 |
| `--exclude-git` | 不打包 `.git` 目录 | 默认保留 |

**示例：**

```bash
# 最小包：不含 .git、node_modules、浏览器
./scripts/tracker_deploy_helper.sh prepare \
  --manifest tracker_manifest.json \
  --output tracker_minimal.tar.gz \
  --exclude-git \
  --skip-node-modules

# 完整开发包：含 .git、node_modules，不含浏览器
./scripts/tracker_deploy_helper.sh prepare \
  --manifest tracker_manifest.json \
  --output tracker_dev.tar.gz

# 完整隔离包：含浏览器
./scripts/tracker_deploy_helper.sh prepare \
  --manifest tracker_manifest.json \
  --output tracker_full.tar.gz \
  --include-playwright-browsers
```

**离线包内容：**

```
tracker_offline_bundle/
├── manifest.json              # 清单副本
├── src/tracker/               # 完整项目源码
│   ├── dev/
│   ├── scripts/
│   ├── shared/data/           # 保留目录结构，user_data 内容为空
│   └── ...
├── wheels/                    # Python 依赖 wheel 包
└── config/                    # 配置模板目录
```

### 5.3 configure 模式

```bash
./scripts/tracker_deploy_helper.sh configure --bundle BUNDLE [OPTIONS]
```

**必填选项：**

| 选项 | 说明 |
|------|------|
| `--bundle BUNDLE` | 由 `prepare` 模式生成的离线包 |

**可选选项：**

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--target-dir DIR` | 目标部署目录 | `$HOME/tracker` |
| `--port PORT` | 服务端口 | `8081` |
| `--adapt-paths MODE` | 路径适配模式：`patch`/`symlink`/`env` | `patch` |
| `--run-now` | 配置完成后立即启动测试服务 | 默认不启动 |

**路径适配模式说明：**

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| `patch`（默认） | 将脚本中的 `/projects/management/tracker`、`/home/hqi/logs`、`/var/log/tracker_*` 替换为目标目录 | 大多数无 sudo 场景 |
| `symlink` | 在 `/projects/management/tracker` 创建指向目标目录的软链 | 有权限创建系统路径时 |
| `env` | 不修改脚本，只生成 `tracker_env.sh` | 希望手动管理路径时 |

**示例：**

```bash
./scripts/tracker_deploy_helper.sh configure \
  --bundle tracker_offline_bundle.tar.gz \
  --target-dir /home/user/tracker \
  --port 8081 \
  --adapt-paths patch \
  --run-now
```

**配置完成后生成的文件：**

| 文件/目录 | 说明 |
|-----------|------|
| `tracker_env.sh` | 环境变量文件，`source` 后可用便捷 alias |
| `venv/` | Python 虚拟环境 |
| `logs/` | 日志目录 |
| `dev/data/` | 运行时数据目录 |
| `shared/data/user_data/` | 空用户数据目录 |
| `test-results/` | 测试结果输出目录 |

---

## 6. 迁移后的日常使用

配置完成后，进入 Tracker 根目录并激活环境：

```bash
cd /home/user/tracker
source tracker_env.sh
```

可用的便捷命令：

| 命令 | 说明 |
|------|------|
| `tracker-start` | 启动测试服务（8081 端口） |
| `tracker-logs` | 查看错误日志 |
| `tracker-test-api` | 运行 API 测试 |
| `tracker-test-ui` | 运行 UI 冒烟测试（需 Node.js 和浏览器） |

### 6.1 启动测试服务

```bash
bash dev/start_server_test.sh
```

服务启动后访问：

```bash
curl http://localhost:8081
```

### 6.2 运行 API 测试

```bash
cd dev
PYTHONPATH=. pytest tests/test_api/ -v
```

### 6.3 运行前端检查

```bash
cd dev
bash check_frontent.sh
```

> 需要 Node.js/npm 已安装。

### 6.4 运行 Playwright UI 测试

```bash
cd dev
npx playwright test tests/test_ui/specs/smoke/ --project=firefox
```

> 需要 Node.js/npm 和 Playwright 浏览器。

---

## 7. 路径适配说明

`configure` 默认会修改目标目录中部分脚本的硬编码路径，使它们指向新的部署目录。受影响的文件包括：

- `dev/start_server_test.sh`
- `dev/gunicorn.conf.py`
- `dev/playwright.config.ts`
- `scripts/memory-monitor.sh`

**不会被修改的文件：**

- `scripts/release.py`：其中 `/release/tracker` 和 `/etc/systemd/system/tracker.service` 需要 root 权限，脚本仅给出警告。

如果你希望保留原始脚本不变，可以使用 `--adapt-paths env`，然后手动 `source tracker_env.sh`。

---

## 8. 常见问题

### Q1: `check` 模式提示 "无 sudo 权限，release.py 的 systemd 发布功能不可用"

这是预期行为。在无 sudo 环境中，使用 `start_server_test.sh` 启动本地测试/开发服务即可。`release.py` 仅用于有 root 权限的正式发布服务器。

### Q2: 目标服务器没有 Node.js，能否运行 Tracker？

可以。Tracker 后端和前端页面不依赖 Node.js 运行。没有 Node.js 时，只是 `check_frontent.sh` 和 Playwright UI 测试无法运行。

### Q3: 离线包是否需要包含 Playwright 浏览器？

取决于目标机环境：

- 如果目标机已有 Playwright 浏览器或可以后续安装，不需要打包。
- 如果目标机完全无法下载任何外部资源，使用 `--include-playwright-browsers` 打包。

浏览器目录约 280MB，会显著增加离线包体积。

### Q4: 为什么 `prepare` 生成的包体积比预期大？

常见原因：

- 包含了 `.git` 目录（默认保留，约 45MB）。
- 包含了 `dev/node_modules`（默认保留，约 67MB）。
- 包含了大量 `shared/data/test_data/` 测试数据库文件。
- 使用了 `--include-playwright-browsers`（约 280MB）。

如需减小体积，可使用 `--exclude-git --skip-node-modules`。

### Q5: 能否把离线包直接解压后手动运行？

不建议。`configure` 模式会完成创建 venv、安装依赖、路径适配、生成环境文件等关键步骤。手动解压后需要自行完成这些操作。

### Q6: 同一台目标服务器能否部署多个 Tracker 实例？

可以。每次使用不同的 `--target-dir` 和 `--port`：

```bash
./scripts/tracker_deploy_helper.sh configure \
  --bundle tracker_offline_bundle.tar.gz \
  --target-dir /home/user/tracker_v2 \
  --port 8082
```

---

## 9. 安全注意事项

- **禁止打包 `shared/data/user_data/` 内容**：脚本会自动排除该目录，仅保留空目录结构。
- **禁止打包 `shared/data/user_data_backup*` 备份目录**。
- 离线包中只包含 `shared/data/test_data/` 等开发测试数据。
- 配置完成后，目标机上的 `shared/data/user_data/` 为空，需要导入或创建新的用户数据。

---

## 10. 附录：参数速查表

### check 模式

```
--output MANIFEST       输出清单文件路径
--project-dir DIR       项目源码目录
--target-dir DIR        目标部署目录
```

### prepare 模式

```
--manifest MANIFEST                   必填，清单文件
--output BUNDLE                       输出离线包路径
--source-dir DIR                      源码目录
--include-playwright-browsers         包含 Playwright 浏览器
--skip-node-modules                   跳过 node_modules
--exclude-git                         不保留 .git
```

### configure 模式

```
--bundle BUNDLE          必填，离线包路径
--target-dir DIR         目标部署目录
--port PORT              服务端口
--adapt-paths MODE       路径适配模式：patch|symlink|env
--run-now                配置后立即启动服务
```

---

*文档版本: v1.0*  
*创建日期: 2026-07-06*  
*署名: Claude Code*
