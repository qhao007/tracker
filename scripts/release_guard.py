#!/usr/bin/env python3
"""发布守卫工具

背景（2026-07-21 v0.16.1 事故）：
`release_preparation.py` 的 `merge_and_tag()` 成功合出 merge 提交并打好 tag，
但后续某项检查失败触发 `rollback_on_failure()`，该函数执行
`git checkout main` + `git reset --hard <prev_tag>`，把 main 指针退回上一个 tag。
merge 提交因为被 tag 引用而未被 GC，于是变成"只存在于 tag、不在任何分支上"的孤儿提交。

后果：任何从 main 检出的部署都会退回旧版本（生产跑 v0.16.1，main 却是 v0.16.0），
问题潜伏 3 个月才被发现。

本模块提供三个能力：
1. `verify_tag_on_branch()` — 断言 tag 提交确实在目标分支上（发布后必检）
2. `delete_tag()` — 回滚时删除刚创建的 tag，避免留下孤儿 tag
3. `find_orphaned_tags()` — 全量体检，找出所有"不在任何分支上"的 tag
"""

import subprocess


def _run(repo_root, args, check=True):
    """执行 git 命令，返回 stdout 文本"""
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} 失败 (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def tag_commit(repo_root, tag):
    """返回 tag 指向的 commit sha；tag 不存在则返回 None"""
    result = subprocess.run(
        ["git", "rev-list", "-n", "1", tag],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None


def branches_containing(repo_root, commit):
    """返回包含该 commit 的本地分支名列表"""
    output = _run(repo_root, ["branch", "--contains", commit])
    branches = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("*"):
            line = line[1:].strip()
        if line:
            branches.append(line)
    return branches


def verify_tag_on_branch(repo_root, tag, branch="main"):
    """断言 tag 指向的提交在指定分支上。

    返回 (是否通过, 失败原因)。通过时原因为空字符串。
    """
    commit = tag_commit(repo_root, tag)
    if commit is None:
        return False, f"标签 {tag} 不存在"

    branches = branches_containing(repo_root, commit)
    if not branches:
        return False, (
            f"标签 {tag} 指向的提交 {commit[:8]} 不在任何分支上 —— "
            f"发布代码已成孤儿！{branch} 分支不会包含本次发布的代码。"
            f"（常见原因：回滚时 git reset --hard 抹掉了 merge 指针）"
        )

    if branch not in branches:
        return False, (
            f"标签 {tag} 指向的提交 {commit[:8]} 不在 {branch} 分支上 "
            f"（实际位于: {', '.join(branches)}）"
        )

    return True, ""


def delete_tag(repo_root, tag):
    """删除 tag（幂等：不存在也算成功）"""
    result = subprocess.run(
        ["git", "tag", "-d", tag],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # tag 不存在 → 视为成功
        if "not found" in (result.stderr or "").lower():
            return True, f"标签 {tag} 不存在，无需删除"
        return False, f"删除标签 {tag} 失败: {result.stderr.strip()}"
    return True, f"已删除标签 {tag}"


def find_orphaned_tags(repo_root, branch="main"):
    """找出所有不在任何分支上的 tag，返回 tag 名列表"""
    tags_output = _run(repo_root, ["tag", "--list"])
    orphans = []
    for tag in [t.strip() for t in tags_output.splitlines() if t.strip()]:
        commit = tag_commit(repo_root, tag)
        if commit is None:
            continue
        if not branches_containing(repo_root, commit):
            orphans.append(tag)
    return orphans


if __name__ == "__main__":
    import sys

    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    orphans = find_orphaned_tags(repo)
    if orphans:
        print(f"❌ 发现 {len(orphans)} 个孤儿标签（不在任何分支上）:")
        for t in orphans:
            print(f"   - {t}")
        sys.exit(1)
    print("✅ 所有标签都在分支上")
