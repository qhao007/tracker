#!/usr/bin/env python3
"""
修复测试数据库结构 - 添加 v0.6.0 新字段

使用方法:
    python3 scripts/fix_test_databases.py

功能:
    遍历 test_data/ 目录下的所有数据库
    添加 v0.6.0 新增的字段:
    - cover_point.priority
    - test_case.dv_milestone
    - test_case.coded_date
    - test_case.fail_date
    - test_case.pass_date
    - test_case.removed_date
    - test_case.target_date
"""

import sqlite3
import glob
import os
import json

def fix_database(db_path):
    """修复单个数据库结构"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 cover_point 表是否有 priority 列
        cursor.execute("PRAGMA table_info(cover_point)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'priority' not in columns:
            print(f"  添加: {os.path.basename(db_path)} -> cover_point.priority")
            cursor.execute("ALTER TABLE cover_point ADD COLUMN priority TEXT DEFAULT 'P0'")
        
        # 检查 test_case 表是否有新字段
        cursor.execute("PRAGMA table_info(test_case)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_fields = {
            'dv_milestone': 'TEXT',
            'coded_date': 'TEXT',
            'fail_date': 'TEXT',
            'pass_date': 'TEXT',
            'removed_date': 'TEXT',
            'target_date': 'TEXT'
        }
        
        for field, type_ in new_fields.items():
            if field not in columns:
                print(f"  添加: {os.path.basename(db_path)} -> test_case.{field}")
                cursor.execute(f"ALTER TABLE test_case ADD COLUMN {field} {type_}")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"  错误: {os.path.basename(db_path)} - {e}")
        return False

def main():
    print("=" * 60)
    print("修复测试数据库结构 - v0.6.0 字段迁移")
    print("=" * 60)
    
    # 获取所有测试数据库
    db_files = glob.glob('shared/data/test_data/*.db')
    
    if not db_files:
        print("未找到测试数据库")
        return
    
    print(f"\n找到 {len(db_files)} 个数据库文件\n")
    
    fixed_count = 0
    for db_file in sorted(db_files):
        if fix_database(db_file):
            fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完成! 修复了 {fixed_count}/{len(db_files)} 个数据库")
    print("=" * 60)

if __name__ == '__main__':
    main()
