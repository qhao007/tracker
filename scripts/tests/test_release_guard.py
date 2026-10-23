"""
发布守卫（release guard）的单元测试

背景：2026-07-21 的 v0.16.1 发布中，`rollback_on_failure()` 用
`git reset --hard <prev_tag>` 把 main 退回到 v0.16.0，而已打好的 tag v0.16.1
仍指向那个被孤立的 merge 提交 —— 导致发布代码只存在于 tag、不在任何分支上，
任何从 main 检出的部署都会退回旧版本。

守卫要做两件事：
1. `release_preparation.py` 合并打 tag 后，断言 tag 提交确实在 main 分支上
2. 回滚时若已创建 tag，必须一并删除，避免留下孤儿 tag
"""
import os
import subprocess
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from release_guard import (  # noqa: E402
    delete_tag,
    find_orphaned_tags,
    verify_tag_on_branch,
)


def _git(repo, *args):
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """构造一个含 main/develop/tag 的临时 git 仓库"""
    path = tmp_path / "repo"
    path.mkdir()

    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)

    (path / "f.txt").write_text("v1", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "c1"], cwd=path, check=True,
                   capture_output=True)
    _git(path, "tag", "-a", "v0.1.0", "-m", "v0.1.0")

    subprocess.run(["git", "checkout", "-b", "develop"], cwd=path, check=True,
                   capture_output=True)
    (path / "f.txt").write_text("v2", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "c2"], cwd=path, check=True,
                   capture_output=True)

    subprocess.run(["git", "checkout", "main"], cwd=path, check=True,
                   capture_output=True)
    return path


# ------------------------------------------------------- verify_tag_on_branch


def test_verify_tag_on_branch_passes_when_tag_is_on_main(repo):
    """tag 指向的提交在 main 上 → 通过"""
    ok, message = verify_tag_on_branch(repo, "v0.1.0", branch="main")
    assert ok is True
    assert message == ""


def test_verify_tag_on_branch_fails_when_tag_is_orphaned(repo):
    """复刻 v0.16.1 事故：merge 提交被打 tag 后，main 被 reset --hard 退回"""
    subprocess.run(["git", "merge", "develop", "--no-ff", "-m", "merge v2"],
                   cwd=repo, check=True, capture_output=True)
    _git(repo, "tag", "-a", "v0.2.0", "-m", "v0.2.0")

    # 回滚到上一个 tag，模拟 rollback_on_failure()
    subprocess.run(["git", "reset", "--hard", "v0.1.0"], cwd=repo, check=True,
                   capture_output=True)

    ok, message = verify_tag_on_branch(repo, "v0.2.0", branch="main")
    assert ok is False
    assert "v0.2.0" in message
    assert "main" in message


def test_verify_tag_on_branch_fails_for_unknown_tag(repo):
    ok, message = verify_tag_on_branch(repo, "v9.9.9", branch="main")
    assert ok is False
    assert "v9.9.9" in message


def test_verify_tag_on_branch_detaches_after_rollback(repo):
    """与上一个测试互补：确认 reset 确实造成了脱离"""
    subprocess.run(["git", "merge", "develop", "--no-ff", "-m", "merge v2"],
                   cwd=repo, check=True, capture_output=True)
    _git(repo, "tag", "-a", "v0.2.0", "-m", "v0.2.0")
    subprocess.run(["git", "reset", "--hard", "v0.1.0"], cwd=repo, check=True,
                   capture_output=True)

    branches = _git(repo, "branch", "--contains", "v0.2.0")
    assert branches.strip() == ""


# ------------------------------------------------------------- delete_tag


def test_delete_tag_removes_the_tag(repo):
    _git(repo, "tag", "-a", "v0.2.0", "-m", "v0.2.0")
    assert "v0.2.0" in _git(repo, "tag", "--list")

    ok, message = delete_tag(repo, "v0.2.0")
    assert ok is True
    assert "v0.2.0" not in _git(repo, "tag", "--list")


def test_delete_tag_on_missing_tag_is_not_fatal(repo):
    ok, message = delete_tag(repo, "v9.9.9")
    assert ok is True  # 幂等：不存在也视为成功


def test_delete_tag_actually_detaches_tag_from_branch(repo):
    """删除孤儿 tag 后，该 tag 不再能引用到被 reset 掉的 merge 提交"""
    subprocess.run(["git", "merge", "develop", "--no-ff", "-m", "merge v2"],
                   cwd=repo, check=True, capture_output=True)
    _git(repo, "tag", "-a", "v0.2.0", "-m", "v0.2.0")
    subprocess.run(["git", "reset", "--hard", "v0.1.0"], cwd=repo, check=True,
                   capture_output=True)

    delete_tag(repo, "v0.2.0")

    assert _git(repo, "tag", "--list").strip() == "v0.1.0"


# -------------------------------------------------------- find_orphaned_tags


def test_find_orphaned_tags_finds_reset_orphans(repo):
    subprocess.run(["git", "merge", "develop", "--no-ff", "-m", "merge v2"],
                   cwd=repo, check=True, capture_output=True)
    _git(repo, "tag", "-a", "v0.2.0", "-m", "v0.2.0")
    subprocess.run(["git", "reset", "--hard", "v0.1.0"], cwd=repo, check=True,
                   capture_output=True)

    orphans = find_orphaned_tags(repo, branch="main")
    assert "v0.2.0" in orphans
    assert "v0.1.0" not in orphans


def test_find_orphaned_tags_returns_empty_when_all_healthy(repo):
    orphans = find_orphaned_tags(repo, branch="main")
    assert orphans == []
