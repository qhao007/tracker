"""
测试基线自检脚本的单元测试

覆盖场景：
- 基线项目 id 正确（EX5=1 / SOC_DV=3 / FC_DV=4）
- 基线内容正确（SOC_DV 52 TC + 30 CP / FC_DV 30 CP + 44 FC + 44 FC-CP）
- id 漂移能被发现
- 内容漂移能被发现
- 基线项目缺失能被发现
"""
import json
import os
import sqlite3
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from verify_test_baseline import (  # noqa: E402
    BASELINE_CONTENT,
    BASELINE_IDS,
    check_baseline,
    read_projects,
    read_table_counts,
)


@pytest.fixture
def fake_data_dir(tmp_path):
    """构造一个临时的 test_data 目录骨架"""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()

    # projects.json：基线项目 id 正确
    projects = [
        {"id": 1, "name": "EX5"},
        {"id": 3, "name": "SOC_DV"},
        {"id": 4, "name": "FC_DV"},
        {"id": 99, "name": "SomeOtherProject"},
    ]
    (data_dir / "projects.json").write_text(json.dumps(projects), encoding="utf-8")

    # SOC_DV.db：52 TC + 30 CP
    soc_db = data_dir / "SOC_DV.db"
    conn = sqlite3.connect(soc_db)
    conn.execute("CREATE TABLE test_case (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE cover_point (id INTEGER PRIMARY KEY)")
    conn.executemany(
        "INSERT INTO test_case (id) VALUES (?)", [(i,) for i in range(52)]
    )
    conn.executemany(
        "INSERT INTO cover_point (id) VALUES (?)", [(i,) for i in range(30)]
    )
    conn.commit()
    conn.close()

    # FC_DV.db：30 CP + 44 FC + 44 FC-CP
    fc_db = data_dir / "FC_DV.db"
    conn = sqlite3.connect(fc_db)
    conn.execute("CREATE TABLE cover_point (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE functional_coverage (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE fc_cp_association (id INTEGER PRIMARY KEY)")
    conn.executemany(
        "INSERT INTO cover_point (id) VALUES (?)", [(i,) for i in range(30)]
    )
    conn.executemany(
        "INSERT INTO functional_coverage (id) VALUES (?)", [(i,) for i in range(44)]
    )
    conn.executemany(
        "INSERT INTO fc_cp_association (id) VALUES (?)", [(i,) for i in range(44)]
    )
    conn.commit()
    conn.close()

    # EX5.db 存在即可（不校验内容）
    conn = sqlite3.connect(data_dir / "EX5.db")
    conn.execute("CREATE TABLE test_case (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    return data_dir


# ---------------------------------------------------------------- 读取逻辑


def test_read_projects_returns_id_name_pairs(fake_data_dir):
    projects = read_projects(fake_data_dir)
    assert ("SOC_DV", 3) in projects
    assert ("FC_DV", 4) in projects
    assert ("EX5", 1) in projects


def test_read_table_counts_counts_rows(fake_data_dir):
    counts = read_table_counts(fake_data_dir / "SOC_DV.db")
    assert counts["test_case"] == 52
    assert counts["cover_point"] == 30


def test_read_table_counts_missing_table_is_absent(fake_data_dir):
    counts = read_table_counts(fake_data_dir / "EX5.db")
    assert "cover_point" not in counts


def test_read_table_counts_missing_file_returns_empty(fake_data_dir):
    counts = read_table_counts(fake_data_dir / "NoSuch.db")
    assert counts == {}


# ---------------------------------------------------------------- 基线校验


def test_check_baseline_passes_on_healthy_data(fake_data_dir):
    ok, problems = check_baseline(fake_data_dir)
    assert ok is True
    assert problems == []


def test_check_baseline_detects_id_drift(fake_data_dir):
    """SOC_DV 的 id 被改成 2（tracker_ops clean 的静默行为）→ 必须报错"""
    projects = json.loads((fake_data_dir / "projects.json").read_text(encoding="utf-8"))
    for p in projects:
        if p["name"] == "SOC_DV":
            p["id"] = 2
    (fake_data_dir / "projects.json").write_text(
        json.dumps(projects), encoding="utf-8"
    )

    ok, problems = check_baseline(fake_data_dir)
    assert ok is False
    assert any("SOC_DV" in p and "id" in p for p in problems)


def test_check_baseline_detects_missing_project(fake_data_dir):
    projects = json.loads((fake_data_dir / "projects.json").read_text(encoding="utf-8"))
    projects = [p for p in projects if p["name"] != "FC_DV"]
    (fake_data_dir / "projects.json").write_text(
        json.dumps(projects), encoding="utf-8"
    )

    ok, problems = check_baseline(fake_data_dir)
    assert ok is False
    assert any("FC_DV" in p for p in problems)


def test_check_baseline_detects_content_drift(fake_data_dir):
    """SOC_DV 少 1 条 TC → 内容基线不符"""
    conn = sqlite3.connect(fake_data_dir / "SOC_DV.db")
    conn.execute("DELETE FROM test_case WHERE id = 51")
    conn.commit()
    conn.close()

    ok, problems = check_baseline(fake_data_dir)
    assert ok is False
    assert any("SOC_DV" in p and "test_case" in p for p in problems)


def test_check_baseline_detects_missing_database(fake_data_dir):
    os.remove(fake_data_dir / "FC_DV.db")

    ok, problems = check_baseline(fake_data_dir)
    assert ok is False
    assert any("FC_DV" in p for p in problems)


def test_check_baseline_reports_all_problems_not_just_first(fake_data_dir):
    """同时破坏 id 和内容 → 两个问题都要报出来"""
    projects = json.loads((fake_data_dir / "projects.json").read_text(encoding="utf-8"))
    for p in projects:
        if p["name"] == "SOC_DV":
            p["id"] = 99
    (fake_data_dir / "projects.json").write_text(
        json.dumps(projects), encoding="utf-8"
    )
    conn = sqlite3.connect(fake_data_dir / "FC_DV.db")
    conn.execute("DELETE FROM functional_coverage WHERE id > 40")
    conn.commit()
    conn.close()

    ok, problems = check_baseline(fake_data_dir)
    assert ok is False
    assert len(problems) >= 2


# ---------------------------------------------------------------- 常量契约


def test_baseline_ids_are_the_agreed_values():
    assert BASELINE_IDS == {"EX5": 1, "SOC_DV": 3, "FC_DV": 4}


def test_baseline_content_matches_agreed_values():
    assert BASELINE_CONTENT["SOC_DV"] == {"test_case": 52, "cover_point": 30}
    assert BASELINE_CONTENT["FC_DV"] == {
        "cover_point": 30,
        "functional_coverage": 44,
        "fc_cp_association": 44,
    }
