#!/usr/bin/env python3
"""测试基线自检脚本

用途：自动化测试依赖固定的基线项目 id 与内容。基线一旦漂移，
API 测试会以极难排查的方式失败（甚至全绿但数据不对）。

背景（2026-10-22 事故）：某 cron 任务误用 `create_demo_project.py --force`，
在 ID 冲突中断后导致 `FC_DV.db` 被删除、`projects.json` 被垃圾记录覆写，
原 id 映射丢失 → 基线失效。`tracker_ops.py clean` 重建时会**静默给 SOC_DV 分配 id=2**，
进一步破坏基线。

用法:
    python3 scripts/verify_test_baseline.py

输出: 逐条列出检查结果
退出码: 0 = 基线正常, 1 = 基线漂移
"""

import json
import os
import sqlite3
import sys

# 基线项目 id（硬约束，自动化测试依赖）
BASELINE_IDS = {"EX5": 1, "SOC_DV": 3, "FC_DV": 4}

# 基线内容（表 -> 行数）
BASELINE_CONTENT = {
    "SOC_DV": {"test_case": 52, "cover_point": 30},
    "FC_DV": {
        "cover_point": 30,
        "functional_coverage": 44,
        "fc_cp_association": 44,
    },
}

# EX5 的内容不校验（老项目，历史遗留，仅约束 id）
CONTENT_CHECKED_PROJECTS = ("SOC_DV", "FC_DV")

DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "shared",
    "data",
    "test_data",
)


def read_projects(data_dir):
    """读取 projects.json，返回 [(name, id), ...]"""
    path = os.path.join(data_dir, "projects.json")
    if not os.path.exists(path):
        return []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    items = data if isinstance(data, list) else data.get("projects", [])
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        pid = item.get("id")
        if name is not None and pid is not None:
            result.append((name, pid))
    return result


def read_table_counts(db_path):
    """读取一个 db 中各表的行数，返回 {table: count}"""
    if not os.path.exists(db_path):
        return {}

    counts = {}
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cur.fetchall()]
            for table in tables:
                try:
                    cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                    counts[table] = cur.fetchone()[0]
                except sqlite3.Error:
                    counts[table] = -1
        finally:
            conn.close()
    except sqlite3.Error:
        return {}

    return counts


def check_baseline(data_dir):
    """校验基线，返回 (是否通过, 问题列表)"""
    problems = []

    projects = read_projects(data_dir)
    id_map = {name: pid for name, pid in projects}

    # 1. 检查基线项目存在且 id 正确
    for name, expected_id in BASELINE_IDS.items():
        if name not in id_map:
            problems.append(f"基线项目 {name} 缺失（projects.json 中不存在）")
            continue
        actual_id = id_map[name]
        if actual_id != expected_id:
            problems.append(
                f"基线项目 {name} id 漂移：期望 {expected_id}，实际 {actual_id}"
            )

    # 2. 检查基线内容
    for name in CONTENT_CHECKED_PROJECTS:
        if name not in id_map:
            continue  # 缺失问题已在上面报过

        db_path = os.path.join(data_dir, f"{name}.db")
        if not os.path.exists(db_path):
            problems.append(f"基线项目 {name} 数据库缺失：{db_path}")
            continue

        counts = read_table_counts(db_path)
        for table, expected_count in BASELINE_CONTENT[name].items():
            actual = counts.get(table)
            if actual is None:
                problems.append(
                    f"基线项目 {name} 缺少表 {table}（期望 {expected_count} 行）"
                )
            elif actual != expected_count:
                problems.append(
                    f"基线项目 {name}.{table} 行数漂移："
                    f"期望 {expected_count}，实际 {actual}"
                )

    return (len(problems) == 0), problems


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_DIR

    print("=" * 60)
    print("🔍 Tracker 测试基线自检")
    print("=" * 60)
    print(f"数据目录: {data_dir}\n")

    ok, problems = check_baseline(data_dir)

    if ok:
        print("✅ 基线正常")
        for name, expected_id in BASELINE_IDS.items():
            print(f"   ✅ {name} (id={expected_id})")
        print("\n结论: 测试基线完好")
        return 0

    print(f"❌ 发现 {len(problems)} 个基线问题:")
    for p in problems:
        print(f"   - {p}")
    print(
        "\n⚠️  自动化测试结果不可信，修复基线后再跑测试。\n"
        "   注意: tracker_ops.py clean 会静默给 SOC_DV 分配 id=2，不能用它修复。"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
