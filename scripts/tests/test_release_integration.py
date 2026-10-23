"""
release.py 守卫接入的单元测试

验证 `check_release_ready()` 会在"标签未包含在 main 分支"时拒绝发布 ——
这是阻止孤儿标签版本被发布出去的最后一道闸门。
"""
import os
import subprocess
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

import release  # noqa: E402


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """临时仓库 + 把 release 的路径常量指向它"""
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

    monkeypatch.setattr(release, "TRACKER_DIR", str(path))
    return path


def _write_flag(repo, version, dry_run="false"):
    flag = repo / ".release_ready"
    head = _git(repo, "rev-parse", "HEAD")
    flag.write_text(
        f"VERSION={version}\nPREPARED_AT=2026-10-24T00:00:00\n"
        f"MAIN_COMMIT={head}\nDRY_RUN={dry_run}\n",
        encoding="utf-8",
    )
    return flag


def test_check_release_ready_passes_when_tag_on_main(repo):
    _write_flag(repo, "0.1.0")
    assert release.check_release_ready("0.1.0") is True


def test_check_release_ready_rejects_orphaned_tag(repo):
    """复刻 v0.16.1 事故：标签在，但 main 被 reset 退回 —— 必须拒绝发布"""
    # 造一个 merge 提交并打 tag，然后把 main reset 回去
    subprocess.run(["git", "checkout", "-b", "develop"], cwd=repo, check=True,
                   capture_output=True)
    (repo / "f.txt").write_text("v2", encoding="utf-8")
    subprocess.run(["git", "commit", "-am", "c2"], cwd=repo, check=True,
                   capture_output=True)
    subprocess.run(["git", "checkout", "main"], cwd=repo, check=True,
                   capture_output=True)
    subprocess.run(["git", "merge", "develop", "--no-ff", "-m", "merge"], cwd=repo,
                   check=True, capture_output=True)
    _git(repo, "tag", "-a", "v0.2.0", "-m", "v0.2.0")
    subprocess.run(["git", "reset", "--hard", "v0.1.0"], cwd=repo, check=True,
                   capture_output=True)

    _write_flag(repo, "0.2.0")

    assert release.check_release_ready("0.2.0") is False


def test_check_release_ready_rejects_missing_tag(repo):
    """版本无对应 tag → 拒绝发布"""
    _write_flag(repo, "0.9.9")
    assert release.check_release_ready("0.9.9") is False


def test_check_release_ready_still_rejects_missing_flag(repo):
    assert release.check_release_ready("0.1.0") is False
