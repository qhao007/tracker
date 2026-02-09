#!/usr/bin/env python3
"""
数据库迁移脚本 - 为 v0.6.0 添加新字段

执行方式:
    python3 scripts/migrate_v0.6.0.py
"""

import os
import sqlite3
from pathlib import Path

DATA_DIR = '/projects/management/tracker/shared/data/user_data'

def migrate_database(db_path):
    """迁移单个数据库"""
    print(f"\n处理: {os.path.basename(db_path)}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查是否需要添加新字段
    cursor.execute("PRAGMA table_info(cover_point)")
    cp_columns = {row[1] for row in cursor.fetchall()}
    
    cursor.execute("PRAGMA table_info(test_case)")
    tc_columns = {row[1] for row in cursor.fetchall()}
    
    # 为 Cover Points 添加 priority 字段
    if 'priority' not in cp_columns:
        cursor.execute("ALTER TABLE cover_point ADD COLUMN priority TEXT DEFAULT 'P0'")
        print("  ✅ 添加 cover_point.priority")
    else:
        print("  ℹ️  cover_point.priority 已存在")
    
    # 为 Test Cases 添加新字段
    new_tc_columns = {
        'coded_date': 'TEXT',
        'fail_date': 'TEXT',
        'pass_date': 'TEXT',
        'removed_date': 'TEXT',
        'target_date': 'TEXT'
    }
    
    for col_name, col_type in new_tc_columns.items():
        if col_name not in tc_columns:
            cursor.execute(f"ALTER TABLE test_case ADD COLUMN {col_name} {col_type}")
            print(f"  ✅ 添加 test_case.{col_name}")
        else:
            print(f"  ℹ️  test_case.{col_name} 已存在")
    
    # 删除已废弃的字段
    if 'completed_date' in tc_columns:
        print("  ⚠️  test_case.completed_date 字段存在（将在后续版本删除）")
    
    if 'priority' in tc_columns:
        print("  ⚠️  test_case.priority 字段存在（将在后续版本删除）")
    
    conn.commit()
    conn.close()
    print(f"完成: {os.path.basename(db_path)}")

def main():
    """主函数"""
    print("=" * 60)
    print("v0.6.0 数据库迁移")
    print("=" * 60)
    
    data_dir = Path(DATA_DIR)
    if not data_dir.exists():
        print(f"错误: 数据目录不存在: {DATA_DIR}")
        return
    
    # 获取所有数据库文件
    db_files = list(data_dir.glob('*.db'))
    
    if not db_files:
        print("未找到数据库文件")
        return
    
    print(f"找到 {len(db_files)} 个数据库文件")
    
    for db_file in sorted(db_files):
        migrate_database(db_file)
    
    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
