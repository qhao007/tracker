"""
release_preparation.py 集成行为的单元测试

复刻 2026-07-21 的 v0.16.1 事故：

    a745269 main@{2026-07-21 22:33:08}: merge develop: Merge made by the 'ort' strategy.
    471f2f3 main@{2026-07-21 22:33:08}: reset: moving to v0.16.0

`merge_and_tag()` 成功合出 merge 提交并打好 tag，但此前的检查（API/冒烟测试）失败，
于是 `main()` 走到 `rollback_on_failure()`，执行
`git checkout main` + `git reset --hard <prev_tag>`，
把 main 退回上一个版本 —— 而 merge 提交因为被 tag 引用而存活，
变成"只在 tag 上、不在任何分支上"的孤儿提交。

要验证的修复：
1. 前置检查失败时不得执行 merge_and_tag（不能产生 merge 提交和 tag）
2. 回滚时若已产生 tag，必须一并删除，不留孤儿 tag
3. 回滚时若 merge 从未发生，不得 reset main（否则会白白把 main 退回去）
4. merge_and_tag 成功后必须自检 tag 是否真的在 main 分支上
"""
import os
import subprocess
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

import release_preparation as rp  # noqa: E402
from release_guard import find_orphaned_tags, verify_tag_on_branch  # noqa: E402


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """main + develop 两个分支，develop 上有一个新提交"""
    path = tmp_path / "repo"
    path.mkdir()

    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)

    (path / "f.txt").write_text("v1", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "c1"], cwd=path, check=True,
                   capture_output=True)
    _git(path, "tag", "-a", "v0.1.0", "-m", "v0.1.0")

    subprocess.run(["git", "checkout", "-b", "develop"], cwd=path, check=True,
                   capture_output=True)
    (path / "f.txt").write_text("v2", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "c2"], cwd=path, check=True,
                   capture_output=True)

    subprocess.run(["git", "checkout", "main"], cwd=path, check=True,
                   capture_output=True)
    return path


@pytest.fixture(autouse=True)
def no_notification(monkeypatch):
    """拦截飞书通知，避免测试真的发消息"""
    sent = []
    monkeypatch.setattr(
        rp, "notify_failure",
        lambda version, failed_step, prev_tag: sent.append((version, failed_step)),
    )
    yield sent


# ------------------------------------------------- merge_and_tag 自检


def test_merge_and_tag_success_creates_tag_on_main(repo):
    assert rp.merge_and_tag("0.2.0", dry_run=False, repo_root=repo) is True

    ok, msg = verify_tag_on_branch(repo, "v0.2.0", branch="main")
    assert ok is True, msg


def test_merge_and_tag_self_check_fails_when_tag_detached(repo, monkeypatch):
    """模拟 merge 成功后 main 被外部 reset —— 自检必须发现并返回失败"""
    real_run = rp.run_command

    def sabotage(cmd, desc, cwd=None):
        success, output = real_run(cmd, desc, cwd=cwd)
        if "git tag -a" in cmd and success:
            # 模拟事故：tag 打好后 main 被 reset 退回上一个 tag
            subprocess.run(["git", "reset", "--hard", "v0.1.0"], cwd=repo,
                           capture_output=True)
        return success, output

    monkeypatch.setattr(rp, "run_command", sabotage)

    assert rp.merge_and_tag("0.2.0", dry_run=False, repo_root=repo) is False


def test_merge_and_tag_dry_run_creates_no_tag(repo):
    assert rp.merge_and_tag("0.2.0", dry_run=True, repo_root=repo) is True
    assert "v0.2.0" not in _git(repo, "tag", "--list")


# ------------------------------------------------- rollback_on_failure


def test_rollback_deletes_tag_it_created(repo):
    """复刻事故：merge 成功打了 tag，随后检查失败触发回滚"""
    assert rp.merge_and_tag("0.2.0", dry_run=False, repo_root=repo) is True
    assert "v0.2.0" in _git(repo, "tag", "--list")

    rp.rollback_on_failure(
        "0.2.0",
        {"api_tests": False, "smoke_tests": True, "merge_tag": True},
        repo,
    )

    # tag 必须被删除 —— 否则留下指向孤儿提交的 tag
    assert "v0.2.0" not in _git(repo, "tag", "--list")
    assert find_orphaned_tags(repo) == []


def test_rollback_restores_main_to_previous_tag(repo):
    """merge 成功后回滚，main 应退回上一个 tag"""
    rp.merge_and_tag("0.2.0", dry_run=False, repo_root=repo)
    merge_sha = _git(repo, "rev-parse", "HEAD")

    rp.rollback_on_failure(
        "0.2.0",
        {"api_tests": False, "merge_tag": True},
        repo,
    )

    # 回滚后切回 main 看它的位置
    subprocess.run(["git", "checkout", "main"], cwd=repo, capture_output=True)
    assert _git(repo, "rev-parse", "HEAD") != merge_sha
    # 注意: annotated tag 的 rev-parse 返回 tag 对象 sha，需用 ^{commit} 取提交
    assert _git(repo, "rev-parse", "HEAD") == _git(repo, "rev-parse", "v0.1.0^{commit}")


def test_rollback_does_not_reset_main_when_merge_never_happened(repo):
    """merge 从未发生 → 回滚不得动 main（否则白白把 main 退回去）"""
    main_before = _git(repo, "rev-parse", "main")

    rp.rollback_on_failure(
        "0.2.0",
        {"api_tests": False, "merge_tag": False},
        repo,
    )

    assert _git(repo, "rev-parse", "main") == main_before


def test_rollback_keeps_preexisting_tag(repo):
    """回滚不得删除非本次发布创建的 tag"""
    _git(repo, "tag", "-a", "v0.0.9", "-m", "old")

    rp.rollback_on_failure(
        "0.2.0",
        {"api_tests": False, "merge_tag": True},
        repo,
    )

    assert "v0.0.9" in _git(repo, "tag", "--list")


def test_rollback_removes_release_ready_flag(repo):
    rp.merge_and_tag("0.2.0", dry_run=False, repo_root=repo)
    flag = repo / ".release_ready"
    assert flag.exists()

    rp.rollback_on_failure(
        "0.2.0",
        {"api_tests": False, "merge_tag": True},
        repo,
    )

    assert not flag.exists()


# ------------------------------------------------- main() 前置检查失败时短路


def test_main_skips_merge_when_pre_merge_check_fails(repo, monkeypatch):
    """前置检查失败时不得执行 merge_and_tag —— 不能产生 merge 提交和 tag"""
    calls = {"merge": 0}

    real_merge = rp.merge_and_tag

    def spy_merge(version, dry_run=False, repo_root=None):
        calls["merge"] += 1
        return real_merge(version, dry_run=dry_run, repo_root=repo_root)

    monkeypatch.setattr(rp, "merge_and_tag", spy_merge)
    monkeypatch.setattr(rp, "run_api_tests", lambda dry_run=False: False)
    monkeypatch.setattr(rp, "run_smoke_tests", lambda dry_run=False: True)
    monkeypatch.setattr(rp, "update_version", lambda version, dry_run=False: True)
    monkeypatch.setattr(rp, "check_git_status", lambda dry_run=False: True)

    argv = sys.argv
    sys.argv = ["release_preparation.py", "--version", "0.2.0"]
    try:
        rp.main(repo_root=repo)
    finally:
        sys.argv = argv

    assert calls["merge"] == 0, "前置检查失败时不应执行 merge_and_tag"
    assert "v0.2.0" not in _git(repo, "tag", "--list")


def test_main_accepts_injected_repo_root(repo, monkeypatch):
    """main() 必须支持注入 repo_root —— 否则测试会操作真实仓库！

    这是个真实踩过的坑：测试调用 rp.main() 时若无法注入 repo_root，
    会直接对真实 Tracker 仓库执行 git checkout / reset 等操作。
    """
    monkeypatch.setattr(rp, "run_api_tests", lambda dry_run=False: True)
    monkeypatch.setattr(rp, "run_smoke_tests", lambda dry_run=False: True)
    monkeypatch.setattr(rp, "update_version", lambda version, dry_run=False: True)
    monkeypatch.setattr(rp, "check_git_status", lambda dry_run=False: True)

    argv = sys.argv
    sys.argv = ["release_preparation.py", "--version", "0.2.0"]
    try:
        rp.main(repo_root=repo)
    finally:
        sys.argv = argv

    # 真实仓库的当前分支不应被这个测试改动
    assert os.path.isdir(repo / ".git")


def test_main_repo_root_defaults_to_script_parent(monkeypatch):
    """不注入时，repo_root 仍默认为脚本所在仓库根"""
    import inspect

    sig = inspect.signature(rp.main)
    assert "repo_root" in sig.parameters
    assert sig.parameters["repo_root"].default is None
