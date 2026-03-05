# Tracker 发布流程改进方案

> **版本**: v1.0 | **创建日期**: 2026-03-04 | **状态**: 待评审

---

## 1. 背景

### 1.1 问题描述

2026-03-04 发布 v0.8.2 时发生严重错误：
- release_preparation.py 脚本执行失败
- 但后续仍然执行了 release.py
- 导致发布的代码版本与版本号不一致（代码是 v0.8.1，版本号显示 v0.8.2）

### 1.2 根因分析

| 问题 | 性质 | 说明 |
|------|------|------|
| Bug #1 | 真实 Bug | `run_buglog_tests` 函数未定义，脚本崩溃 |
| Bug #2 | 真实 Bug | 脚本被 SIGKILL 杀死，merge 未执行 |
| 流程问题 | 设计缺陷 | 发布准备失败后仍可执行发布脚本 |
| 无回滚 | 设计缺陷 | 失败后无自动回滚机制 |

### 1.3 影响范围

- v0.8.2 发布失败，需手动修复
- 快照管理功能未发布
- 需手动合并代码到 main 分支

---

## 2. 改进方案

### 2.1 移除 run_buglog_tests

**问题**: 调用未定义的函数导致脚本崩溃

**修复**: 从 main() 函数中移除所有 buglog_tests 相关调用

```python
# 修改 main() 函数
# 修改前
if not args.skip_tests:
    results["api_tests"] = run_api_tests(args.dry_run)
    results["smoke_tests"] = run_smoke_tests(args.dry_run)
    results["buglog_tests"] = run_buglog_tests(args.dry_run)  # 删除这行

# 修改后
if not args.skip_tests:
    results["api_tests"] = run_api_tests(args.dry_run)
    results["smoke_tests"] = run_smoke_tests(args.dry_run)
```

---

### 2.2 Flag 文件机制

**问题**: 发布准备失败后仍可执行发布脚本

**方案**: 使用 flag 文件作为发布准入门槛

**Flag 文件位置**: `/projects/management/tracker/.release_ready`

**文件内容**:
```
VERSION=v0.8.2
PREPARED_AT=2026-03-04T16:30:00
MAIN_COMMIT=3a49702
MERGE_MSG=merge: 合并 v0.8.2 到正式版
```

**release.py 检查逻辑**:

```python
def check_release_ready(version):
    """检查是否满足发布条件"""
    flag_file = Path("/projects/management/tracker/.release_ready")
    
    # 1. 检查 flag 文件是否存在
    if not flag_file.exists():
        print(f"{RED}❌ 未执行发布准备，请先运行 release_preparation.py{RESET}")
        return False
    
    # 2. 检查版本是否匹配
    content = flag_file.read_text()
    if f"VERSION={version}" not in content:
        print(f"{RED}❌ 版本不匹配{RESET}")
        print(f"当前 flag: {content}")
        return False
    
    # 3. 检查 main 分支是否是预期提交
    current_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root, capture_output=True, text=True
    ).stdout.strip()
    
    if "MAIN_COMMIT" in content:
        expected_commit = content.split("MAIN_COMMIT=")[1].split("\n")[0]
        if current_commit != expected_commit:
            print(f"{RED}❌ main 分支提交不匹配{RESET}")
            return False
    
    return True
```

---

### 2.3 完善的回滚机制

**问题**: 发布失败后无自动回滚，main 分支可能处于不稳定状态

**方案**: 失败时自动回滚到上一个稳定版本

```python
def rollback_on_failure(version, failed_step, repo_root):
    """发布失败时自动回滚"""
    print(f"\n{'='*60}")
    print(f"🔄 执行回滚: {failed_step} 失败")
    print(f"{'='*60}\n")
    
    # 1. 找出上一个稳定版本 tag
    tags_result = subprocess.run(
        ["git", "tag", "--sort=-creatordate"],
        cwd=repo_root, capture_output=True, text=True
    )
    tags = tags_result.stdout.strip().split('\n')
    
    # 找到上一个非当前版本的 tag
    prev_tag = None
    for tag in tags:
        if tag and tag != f"v{version}":
            prev_tag = tag
            break
    
    # 2. 回滚 main 分支
    if prev_tag:
        print(f"1. 回滚到上一个稳定版本: {prev_tag}")
        subprocess.run(["git", "checkout", "main"], cwd=repo_root)
        subprocess.run(["git", "reset", "--hard", prev_tag], cwd=repo_root)
        print(f"✅ main 分支已回滚到 {prev_tag}")
    else:
        print("⚠️ 未找到上一个稳定版本，请手动处理")
    
    # 3. 切换到 develop 分支（不回滚代码）
    # 说明：develop 分支不需要代码回滚
    # 原因：develop 分支上的代码是开发中的代码，即使 merge 失败，develop 上的代码也不会丢失
    # 操作：只需要把 HEAD 切换到 develop 分支即可
    print("2. 切换到 develop 分支...")
    subprocess.run(["git", "checkout", "develop"], cwd=repo_root)
    print("✅ 已切换到 develop 分支")
    
    # 4. 删除 flag 文件
    flag_file = repo_root / ".release_ready"
    if flag_file.exists():
        flag_file.unlink()
    print("✅ Flag 文件已删除")
    
    # 5. 发送通知
    notify_failure(version, failed_step, prev_tag)
    
    return False

def notify_failure(version, failed_step, prev_tag):
    """通知用户发布失败"""
    message = f"""
🚨 **Tracker 发布失败**

版本: v{version}
失败步骤: {failed_step}
已回滚到: {prev_tag}

请检查问题后重新执行发布准备。
"""
    # 调用飞书 webhook
    send_feishu_notification(message)
```

**触发回滚的条件**:
- 任何测试失败
- VERSION 更新失败
- Merge 失败
- 脚本异常退出

---

### 2.4 分支状态管理

**问题**: 发布成功后切回 develop，可能导致代码不一致

**改进**:

| 阶段 | 分支状态 | 说明 |
|------|----------|------|
| release_preparation.py 成功 | main | 停留在 main，准备发布 |
| release.py 执行中 | main | 确保读取正确代码 |
| release.py 成功 | develop | 切换回 develop，继续开发 |
| 失败回滚 | develop | 回滚后保持在 develop |

**release_preparation.py 修改**:

```python
# merge_and_tag() 函数中
# 删除第5步"切换回 develop 分支"
# 修改后流程:
# 1. 切换到 main 分支
# 2. 拉取最新
# 3. 合并 develop 到 main
# 4. 创建发布标签
# 5. 创建 .release_ready flag
# 6. 停留在 main 分支（不切换回 develop）
```

**release.py 修改**:

```python
# 在 __main__ 部分添加
if __name__ == "__main__":
    # ... 发布逻辑 ...
    
    # 完成后切换回 develop
    print("\n🔄 切换回 develop 分支...")
    subprocess.run(["git", "checkout", "develop"], cwd=repo_root)
    
    # 删除 flag 文件
    flag_file = repo_root / ".release_ready"
    if flag_file.exists():
        flag_file.unlink()
    
    print("✅ 发布完成，已切换到 develop 分支")
```

---

## 3. 改进后的完整流程

### 3.1 成功流程

```
1. release_preparation.py --version v0.8.2
   ├── [1] API 测试 ✅
   ├── [2] 冒烟测试 ✅
   ├── [3] VERSION 更新 ✅
   ├── [4] Git 状态检查 ✅
   ├── [5] Merge develop → main ✅
   ├── [6] 创建 tag v0.8.2 ✅
   ├── [7] 创建 .release_ready flag ✅
   └── [8] 停留在 main 分支 ✅

2. release.py --version v0.8.2 --force
   ├── [1] 检查 .release_ready flag ✅
   ├── [2] 复制代码到发布目录
   ├── [3] 更新软链接
   ├── [4] 重启服务
   ├── [5] 切换回 develop 分支
   └── [6] 删除 .release_ready flag
```

### 3.2 失败回滚流程

```
1. release_preparation.py --version v0.8.2
   ├── [1] API 测试 ❌ 失败
   ├── 🔄 触发回滚
   │   ├── 回滚 main 分支到上一稳定版本（代码回滚）
   │   ├── 切换到 develop 分支（仅切换，不回滚代码）
   │   ├── 删除 flag 文件
   │   └── 发送通知 🚨
   └── 终止执行
```

**说明**：
- **main 分支**：需要代码回滚到上一稳定版本
- **develop 分支**：只需要切换分支（checkout），不需要回滚代码
  - 原因：develop 上的代码是开发中的代码，即使 merge 失败，develop 上的代码不会丢失
  - 操作：`git checkout develop` 即可

---

## 4. 需要修改的文件

| 文件 | 修改内容 | 优先级 |
|------|----------|--------|
| `scripts/release_preparation.py` | 移除 buglog_tests、添加回滚机制、flag 文件 | P0 |
| `scripts/release.py` | 添加 flag 检查、完成后切回 develop | P0 |
| `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` | 更新发布流程说明 | P1 |

---

## 5. 风险控制

| 风险点 | 防护措施 |
|--------|----------|
| flag 文件被误删 | 重新运行 release_preparation.py |
| 回滚到错误版本 | 手动确认上一 tag，输出详细信息 |
| 通知失败 | 打印详细回滚信息到控制台 |
| 并发发布 | 添加文件锁机制 |

---

## 6. 验收标准

- [ ] run_buglog_tests 调用已移除
- [ ] 发布准备失败时自动回滚
- [ ] 发布脚本检查 flag 文件
- [ ] 发布成功后自动切换回 develop
- [ ] 发布失败时发送通知
- [ ] 更新 DEVELOPMENT_PROCESS.md 文档

---

## 7. 实施计划

| 阶段 | 任务 | 预估时间 |
|------|------|----------|
| P0 | 修复 run_buglog_tests Bug | 10 min |
| P0 | 实现 flag 文件机制 | 30 min |
| P0 | 实现自动回滚机制 | 30 min |
| P1 | 修改 release.py | 20 min |
| P1 | 更新文档 | 10 min |
| - | **总计** | **~1.5h** |

---

## 8. 历史记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-04 | v1.0 | 初始版本 |
