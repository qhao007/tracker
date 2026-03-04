# Tracker 发布脚本代码审查报告

> **版本**: v1.0 | **审查日期**: 2026-03-04 | **状态**: 已完成

---

## 1. 背景

本文档对 `scripts/release_preparation.py` 和 `scripts/release.py` 进行代码审查，审查依据为 `docs/PLANS/RELEASE_PROCESS_IMPROVEMENT.md` 中的改进方案。

---

## 2. 审查范围

| 文件 | 版本 | 说明 |
|------|------|------|
| `scripts/release_preparation.py` | v0.6.2 | 发布前准备脚本 |
| `scripts/release.py` | v0.4 | 版本发布脚本 |

---

## 3. 严重问题 (P0)

### 🔴 Bug #1: merge_and_tag 函数结构错误

**位置**: `release_preparation.py` 第255-312行

**问题描述**:
```python
def create_release_ready_flag(version, repo_root):
    """创建发布就绪 flag 文件"""
    # ... 函数体 ...
    return True
    """
    步骤 6: 执行 Merge 和 Tag 操作
    ...
    """
    print_step(6, f"执行 Merge 和 Tag (v{version})")
    # ... 实际的 merge_and_tag 代码 ...
```

`merge_and_tag()` 函数的代码被错误地放在了 `create_release_ready_flag()` 函数的文档字符串内部。

**影响**:
- 函数 `merge_and_tag` 实际上只有函数签名，没有函数体
- 当代码执行到 `results["merge_tag"] = merge_and_tag(...)` (第489行) 时，会触发 `NameError: name 'merge_and_tag' is not defined`
- **这是导致 v0.8.2 发布失败的根因 Bug**

**修复建议**:
1. 将第255-312行的代码从 `create_release_ready_flag` 的文档字符串中移出
2. 正确定义 `merge_and_tag` 函数

---

### 🟠 Bug #2: Flag 文件解析不健壮

**位置**: `release.py` 第84行

**问题描述**:
```python
expected_commit = content.split("MAIN_COMMIT=")[1].split("\n")[0]
```

**问题**:
- 如果 flag 文件内容没有换行（如 `VERSION=v0.8.2MAIN_COMMIT=xxx`），split 后取 [0] 会返回整个字符串而非单个 commit hash
- 缺乏对文件格式的校验

**修复建议**:
```python
# 更健壮的解析方式
try:
    expected_commit = content.split("MAIN_COMMIT=")[1].split("\n")[0]
except IndexError:
    print("   ❌ Flag 文件格式错误")
    return False
```

---

## 4. 设计问题 (P1)

### 4.1 release_preparation.py

| 位置 | 问题 | 严重度 | 修复建议 |
|------|------|--------|----------|
| L328 | 使用 `os.system()` 启动服务，而非 `subprocess` | 低 | 改用 `subprocess.Popen` |
| L372 | 冒烟测试路径过时: `smoke/smoke.spec.ts` | 中 | 改为 `smoke/` 目录 |
| L348/L379 | `"passed" in output` 匹配过于宽松 | 低 | 使用正则匹配具体数字 |
| L121 | Git commit message 直接拼接版本号 | 低 | 使用 shlex.quote 或格式化 |
| L471 | 注释遗留 `# 已移除:` | 低 | 删除注释 |

**L372 详细说明**:
```python
# 当前代码
cmd = f"cd {dev_dir} && npx playwright test tests/test_ui/specs/smoke/smoke.spec.ts ..."

# 问题: v0.8.2 改革后，smoke 测试目录结构已变化
# 应改为
cmd = f"cd {dev_dir} && npx playwright test tests/test_ui/specs/smoke/ ..."
```

---

### 4.2 release.py

| 位置 | 问题 | 严重度 | 修复建议 |
|------|------|--------|----------|
| L540-544 | 分支切换失败后仍继续执行 flag 删除 | 中 | 添加 try-except 并在失败时返回 |
| L446-452 | rollback 只切换软链接，未验证服务健康 | 中 | 添加健康检查 |
| L138 | 访问全局变量 `args.force` | 低 | 作为参数传入 |
| 全局 | 缺少并发发布锁机制 | 中 | 添加文件锁 |

**L540-544 详细说明**:
```python
# 当前代码
print("\n🔄 切换回 develop 分支...")
try:
    subprocess.run(["git", "checkout", "develop"], cwd=TRACKER_DIR, check=True)
    print("✅ 已切换到 develop 分支")
except subprocess.CalledProcessError as e:
    print(f"⚠️  切换分支失败: {e}")

# 删除 flag 文件 (即使切换失败也会执行)
flag_file = os.path.join(TRACKER_DIR, '.release_ready')
if os.path.exists(flag_file):
    os.remove(flag_file)  # ← 应该在切换成功后执行

# 建议修复
print("\n🔄 切换回 develop 分支...")
try:
    subprocess.run(["git", "checkout", "develop"], cwd=TRACKER_DIR, check=True)
    print("✅ 已切换到 develop 分支")

    # 删除 flag 文件
    flag_file = os.path.join(TRACKER_DIR, '.release_ready')
    if os.path.exists(flag_file):
        os.remove(flag_file)
        print("✅ Flag 文件已删除")
except subprocess.CalledProcessError as e:
    print(f"⚠️  切换分支失败: {e}")
    print("⚠️  请手动切换到 develop 分支并删除 flag 文件")
    return  # 添加返回
```

---

## 5. 流程问题 (P2)

### 5.1 兼容性测试

| 问题 | 说明 |
|------|------|
| 文档描述 | "用户数据 → 测试数据" |
| 实际执行 | `python3 scripts/tracker_ops.py all` |

**建议**: 确认 `tracker_ops.py all` 是否真正执行了"用户数据→测试数据"的兼容性测试。

---

### 5.2 通知机制

**位置**: `release_preparation.py` L222-233

```python
def notify_failure(version, failed_step, prev_tag):
    """通知用户发布失败"""
    message = f"""..."""
    print(f"\n{message}")
    print(f"\n提示: 使用飞书 webhook 发送通知（待实现）")
```

**问题**: `notify_failure()` 函数只打印消息，未实际发送飞书通知。

**建议**: 实现飞书 webhook 通知功能。

---

### 5.3 回滚后健康检查

**位置**: `release.py` L446-452

```python
# 更新软链接
update_current_symlink(target_version)
update_systemd_service(target_version)
restart_service()
```

**问题**: `restart_service()` 执行后未验证服务是否真正启动成功。

**建议**: 添加健康检查端点验证。

---

## 6. 改进方案对照

| 文档方案 | 实现状态 | 说明 |
|----------|----------|------|
| 添加 check_release_ready flag 检查 | ✅ 已实现 | release.py L55-92 |
| 添加 rollback_on_failure 机制 | ⚠️ 部分实现 | release_preparation.py L170-219，但有 Bug #1 |
| 发布后切回 develop | ✅ 已实现 | release.py L540-550，但错误处理不足 |
| merge_and_tag 停留 main | ⚠️ 已实现 | 代码在 docstring 内导致不可用 |

---

## 7. 修复优先级

| 优先级 | 任务 | 预计时间 |
|--------|------|----------|
| P0 | 修复 merge_and_tag 函数结构错误 | 5 min |
| P0 | 改进 flag 解析逻辑 | 5 min |
| P1 | 增强分支切换错误处理 | 10 min |
| P1 | 更新冒烟测试路径 | 5 min |
| P1 | 实现 rollback 后健康检查 | 10 min |
| P2 | 清理遗留注释 | 5 min |
| P2 | 实现飞书通知 | 20 min |
| P2 | 添加并发锁机制 | 15 min |

---

## 8. 总结

| 指标 | 数量 |
|------|------|
| 严重 Bug | 1 |
| 设计问题 | 9 |
| 流程问题 | 3 |
| 需修复总数 | 13 |

**核心问题**: `merge_and_tag` 函数结构错误导致 v0.8.2 发布失败。建议优先修复此问题后，再处理其他设计问题。

---

**审查人**: 小栗子
**审查时间**: 2026-03-04
