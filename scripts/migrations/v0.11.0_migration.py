#!/usr/bin/env python3
"""
数据库迁移脚本 - 为 v0.11.0 添加 FC 和 FC-CP 关联功能

执行方式:
    python3 scripts/tracker_ops.py migrate --version v0.11.0
"""

import os
import sqlite3
from pathlib import Path

DATA_DIR = '/projects/management/tracker/shared/data'


def migrate_database(db_path):
    """迁移单个数据库"""
    print(f"\n处理: {os.path.basename(db_path)}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查 functional_coverage 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='functional_coverage'")
    if cursor.fetchone():
        print(f"  ℹ️  functional_coverage 表已存在，跳过")
    else:
        # 创建 Functional Coverage 表
        cursor.execute("""
            CREATE TABLE functional_coverage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                covergroup TEXT NOT NULL,
                coverpoint TEXT NOT NULL,
                coverage_type TEXT NOT NULL,
                bin_name TEXT NOT NULL,
                bin_val TEXT,
                comments TEXT,
                coverage_pct REAL DEFAULT 0.0,
                status TEXT DEFAULT 'missing',
                owner TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                UNIQUE (project_id, covergroup, coverpoint, bin_name)
            )
        """)
        print("  ✅ 创建 functional_coverage 表")

    # 检查 fc_cp_association 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fc_cp_association'")
    if cursor.fetchone():
        print(f"  ℹ️  fc_cp_association 表已存在，跳过")
    else:
        # 创建 FC-CP 关联表
        cursor.execute("""
            CREATE TABLE fc_cp_association (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                cp_id INTEGER,
                fc_id INTEGER,
                created_by TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                UNIQUE (cp_id, fc_id),
                FOREIGN KEY (cp_id) REFERENCES cover_point(id),
                FOREIGN KEY (fc_id) REFERENCES functional_coverage(id)
            )
        """)
        print("  ✅ 创建 fc_cp_association 表")

    # 创建索引
    try:
        cursor.execute("CREATE INDEX idx_fc_covergroup ON functional_coverage(covergroup)")
        print("  ✅ 创建 idx_fc_covergroup 索引")
    except sqlite3.OperationalError:
        pass  # 索引已存在

    try:
        cursor.execute("CREATE INDEX idx_fc_coverpoint ON functional_coverage(coverpoint)")
        print("  ✅ 创建 idx_fc_coverpoint 索引")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("CREATE INDEX idx_fc_coverage_type ON functional_coverage(coverage_type)")
        print("  ✅ 创建 idx_fc_coverage_type 索引")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("CREATE INDEX idx_fc_cp_assoc_cp ON fc_cp_association(cp_id)")
        print("  ✅ 创建 idx_fc_cp_assoc_cp 索引")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("CREATE INDEX idx_fc_cp_assoc_fc ON fc_cp_association(fc_id)")
        print("  ✅ 创建 idx_fc_cp_assoc_fc 索引")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    print(f"  ✅ 完成: {os.path.basename(db_path)}")


def main():
    """主函数"""
    import sys

    version = None
    if len(sys.argv) >= 3 and sys.argv[1] == '--version':
        version = sys.argv[2]

    print("=" * 50)
    print("v0.11.0 数据库迁移：添加 FC 和 FC-CP 关联功能")
    print("=" * 50)

    if version and version != 'v0.11.0':
        print(f"\n⚠️  版本不匹配: expected v0.11.0, got {version}")
        return

    # 迁移 user_data
    user_data_dir = os.path.join(DATA_DIR, 'user_data')
    if os.path.exists(user_data_dir):
        print(f"\n📁 迁移 user_data: {user_data_dir}")
        for db_file in Path(user_data_dir).glob('*.db'):
            if db_file.stat().st_size > 0:  # 跳过空文件
                migrate_database(str(db_file))

    # 迁移 test_data
    test_data_dir = os.path.join(DATA_DIR, 'test_data')
    if os.path.exists(test_data_dir):
        print(f"\n📁 迁移 test_data: {test_data_dir}")
        for db_file in Path(test_data_dir).glob('*.db'):
            if db_file.stat().st_size > 0:  # 跳过空文件
                migrate_database(str(db_file))

    print("\n" + "=" * 50)
    print("✅ v0.11.0 数据库迁移完成")
    print("=" * 50)


if __name__ == '__main__':
    main()
