#!/usr/bin/env python3
"""
数据库迁移脚本 - 为 v0.8.0 添加项目起止日期字段

执行方式:
    python3 scripts/migrate_v0.8.0.py
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
    
    # 检查 project 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project'")
    if not cursor.fetchone():
        print(f"  ⚠️  project 表不存在，跳过")
        conn.close()
        return
    
    # 检查 project 表字段
    cursor.execute("PRAGMA table_info(project)")
    columns = {row[1] for row in cursor.fetchall()}
    
    # 添加 start_date 字段
    if 'start_date' not in columns:
        cursor.execute("ALTER TABLE project ADD COLUMN start_date TEXT")
        print("  ✅ 添加 project.start_date")
    else:
        print("  ℹ️  project.start_date 已存在")
    
    # 添加 end_date 字段
    if 'end_date' not in columns:
        cursor.execute("ALTER TABLE project ADD COLUMN end_date TEXT")
        print("  ✅ 添加 project.end_date")
    else:
        print("  ℹ️  project.end_date 已存在")
    
    conn.commit()
    conn.close()
    print(f"  ✅ 完成: {os.path.basename(db_path)}")


def main():
    """主函数"""
    print("=" * 50)
    print("v0.8.0 数据库迁移：为项目添加起止日期字段")
    print("=" * 50)
    
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
    print("✅ v0.8.0 数据库迁移完成")
    print("=" * 50)


if __name__ == '__main__':
    main()
