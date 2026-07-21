# 测试数据清理运维手册

> **适用版本**: v0.16.0+ | **更新日期**: 2026-07-21 | **署名**: Claude Code

本文档面向运维/开发人员，说明如何安全清理 Tracker 测试数据目录，并保留/重建基本 demo 项目。

---

## 1. 数据目录布局

| 目录 | 用途 | 可否清理 |
|------|------|----------|
| `shared/data/test_data/` | 测试数据（pytest + 8081 测试服共用） | ✅ 可清理（按本文流程） |
| `dev/data` | 指向 `shared/data/test_data` 的**符号链接** | （同一目录，勿重复操作） |
| `shared/data/user_data/` | **生产数据（8080）** | ❌ 严禁操作 |

关键点：`dev/data` 只是符号链接，pytest（`create_app`）与 8081 测试服（`wsgi:app`）实际都读写 `shared/data/test_data`。测试项目会在此持续积压（每次 pytest/UI 测试都会创建项目），导致项目列表变慢、性能测试超阈值。

---

## 2. 清理命令

```bash
cd /projects/management/tracker

# 1. 预览（默认 dry-run，不删除任何文件）
python3 scripts/tracker_ops.py clean

# 2. 确认执行
python3 scripts/tracker_ops.py clean --yes
```

**建议执行顺序**：先停 8081 测试服（`./dev/start_server_test.sh` 会先自动停旧进程，或手动停止），清理并验证后再重启。运行中的 gunicorn 持有 db 连接，边删边用可能产生空库文件。

---

## 3. 清理行为明细

### 保留（不动）

- **基本 demo 项目**：`EX5`(id=1)、`SOC_DV`(id=3, TC-CP)、`FC_DV`(id=4, FC-CP)
- `projects.json` 中这三个项目的**完整原始记录（含 id）**——id 不变是测试基线的硬约束（`test_api_dashboard.py`、`test_api_report_export.py` 等硬编码 `project/3`）
- `wiki/` 下非数字目录（`_global`、`_archived`、项目 slug 目录）

### 删除

- 其他所有项目 `*.db`（sync 来的 + 测试创建的）
- `users.db`（随后自动重建为默认账号 admin/admin123、guest）
- `sessions/` 全部文件（8081 所有在线会话失效，需重新登录）
- `*.db-journal`、`projects.json.new` 残留文件
- `wiki/<数字id>/` 中 id 已不存在的孤儿目录

### 重建

- 清理后若 `SOC_DV` / `FC_DV` 缺失（例如被误删），自动调用 `create_demo_project.py` **按原 id** 重建

### 安全约束

- 脚本内置检查：目标目录必须解析为 `shared/data/test_data`，与 `user_data` 相同或目录名不符时**拒绝执行**
- `python3 scripts/tracker_ops.py all` 中的 clean 步骤为实际执行（保持原语义）

---

## 4. Demo 项目手动重建

demo 数据损坏或被误删时，可精确恢复到测试基线 id：

```bash
# 重建两个 demo 并恢复标准 id（SOC_DV=3, FC_DV=4）
python3 scripts/create_demo_project.py --force --ids SOC_DV=3,FC_DV=4

# 只重建 SOC_DV
python3 scripts/create_demo_project.py --force -p soc_dv --ids SOC_DV=3
```

- `--ids NAME=ID` 指定 id（逗号分隔多个），缺省自动分配 `max(id)+1`
- 指定 id 与其他项目冲突时脚本报错退出
- 重建内容：30 CP + 52 TC（TC-CP）/ 44 FC（FC-CP）+ 12 个历史快照
- 该脚本同样内置 user_data 拒绝保护

---

## 5. 清理后验证清单

```bash
# 1. projects.json 应只剩 3 个项目且 id 为 1/3/4
python3 -c "import json; print([(p['id'],p['name']) for p in json.load(open('shared/data/test_data/projects.json'))])"

# 2. 重启 8081
cd dev && ./start_server_test.sh

# 3. 关键测试（依赖 SOC_DV id=3 + 性能阈值）
cd dev && PYTHONPATH=. pytest tests/test_api/test_api_dashboard.py tests/test_api/test_api_report_export.py tests/test_api/test_api_performance.py -q
```

---

## 6. 注意事项

- 清理**不可恢复**：被删项目无法找回（生产项目归档在 `archives/`，不在此列）
- users.db 重建后，自定义测试用户（如 user/user123）需重新创建；pytest fixture 会自动重建
- 清理频率建议：性能测试出现 `/api/projects` 超 500ms、或 UI 测试因项目过多超时时执行
- 2026-07-21 首次执行：2282 个测试项目 → 3 个，目录 152MB → 33MB，`/api/projects` 由 ~590ms 降至正常

---

*最后更新: 2026-07-21 | 署名: Claude Code*
