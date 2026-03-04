#!/usr/bin/env python3
"""
Demo Project Generator - 创建芯片验证示例项目

用途：在 test_data 目录中创建 SOC_DV 示例项目，方便演示和测试

使用方法：
    python3 scripts/create_demo_project.py       # 创建示例项目
    python3 scripts/create_demo_project.py --force  # 重新创建（带清理）
"""

import argparse
import json
import os
import sqlite3
import sys
import random
from datetime import datetime, timedelta


# 项目配置
PROJECT_NAME = "SOC_DV"
PROJECT_DESC = "RISC-V SoC 芯片系统级验证项目"

# 数据目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "shared", "data", "test_data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")

# DV Milestone 选项
DV_MILESTONES = ["DV0.3", "DV0.5", "DV0.7", "DV1.0"]

# DV Milestone 对应的项目进度百分比
DV_MILESTONE_PROGRESS = {
    "DV0.3": 0.3,
    "DV0.5": 0.5,
    "DV0.7": 0.7,
    "DV1.0": 1.0
}

# 项目周期 (15周)
PROJECT_START = "2026-01-06"  # 第一周周一
PROJECT_END = "2026-04-18"    # 15周后周五

# 32 个 Cover Points
COVER_POINTS = [
    # CPU Core (10个)
    ("CPU Core", "Instruction", "指令覆盖 - R-Type", "P0"),
    ("CPU Core", "Instruction", "指令覆盖 - I-Type", "P0"),
    ("CPU Core", "Instruction", "指令覆盖 - S-Type", "P0"),
    ("CPU Core", "Instruction", "指令覆盖 - U-Type", "P1"),
    ("CPU Core", "Instruction", "指令覆盖 - J-Type", "P1"),
    ("CPU Core", "Instruction", "指令覆盖 - B-Type", "P1"),
    ("CPU Core", "Cache", "缓存一致性协议", "P0"),
    ("CPU Core", "Cache", "L1 缓存命中率", "P1"),
    ("CPU Core", "Exception", "异常场景覆盖", "P1"),
    ("CPU Core", "Privilege", "特权模式切换", "P2"),
    
    # L2 Cache (3个)
    ("L2 Cache", "Miss Rate", "缓存未命中统计", "P1"),
    ("L2 Cache", "Coherency", "缓存一致性 MESI", "P0"),
    ("L2 Cache", "Eviction", "缓存行替换策略", "P2"),
    
    # DDR Controller (4个)
    ("DDR Controller", "Read", "读事务覆盖", "P0"),
    ("DDR Controller", "Write", "写事务覆盖", "P0"),
    ("DDR Controller", "Timing", "时序约束覆盖", "P1"),
    ("DDR Controller", "Mode", "DDR 模式切换", "P2"),
    
    # PCIe Controller (4个)
    ("PCIe Controller", "Config", "配置空间访问", "P1"),
    ("PCIe Controller", "Transaction", "事务层覆盖", "P0"),
    ("PCIe Controller", "MSI", "MSI 中断传输", "P2"),
    ("PCIe Controller", "Power", "功耗状态转换", "P2"),
    
    # GPIO (3个)
    ("GPIO", "Interrupt", "中断触发", "P1"),
    ("GPIO", "Edge", "边沿检测", "P2"),
    ("GPIO", "Debounce", "防抖处理", "P2"),
    
    # Clock Manager (3个)
    ("Clock Manager", "Gating", "时钟门控", "P1"),
    ("Clock Manager", "Sync", "跨时钟域同步", "P0"),
    ("Clock Manager", "PLL", "PLL 锁定时间", "P2"),
    
    # Reset Logic (3个)
    ("Reset Logic", "PowerOn", "上电复位序列", "P0"),
    ("Reset Logic", "Watchdog", "看门狗复位", "P1"),
    ("Reset Logic", "SW Reset", "软件复位", "P1"),
]

# TC 状态分布
TC_STATUS = {
    "PASS": 20,
    "FAIL": 6,
    "CODED": 10,
    "OPEN": 16
}

# TC 生成模板
TC_TEMPLATES = [
    ("CPU Core", "Block", ["指令集验证", "流水线测试", "分支预测"]),
    ("CPU Core", "Integration", ["多核协同测试", "缓存一致性集成"]),
    ("CPU Core", "System", ["系统启动测试", "中断响应"]),
    ("L2 Cache", "Block", ["缓存读写测试", "替换算法"]),
    ("L2 Cache", "Integration", ["多核缓存一致性"]),
    ("DDR Controller", "Block", ["DDR 初始化", "读写时序"]),
    ("DDR Controller", "Integration", ["DMA 传输测试"]),
    ("DDR Controller", "System", ["内存带宽测试"]),
    ("PCIe Controller", "Block", ["PCIe 枚举", "配置测试"]),
    ("PCIe Controller", "Integration", ["MSI-X 中断"]),
    ("PCIe Controller", "System", ["高速数据传输"]),
    ("GPIO", "Block", ["GPIO 输入输出", "中断测试"]),
    ("GPIO", "Integration", ["外设互联"]),
    ("Clock Manager", "Block", ["时钟切换", "PLL 锁定"]),
    ("Clock Manager", "Integration", ["跨时钟域"]),
    ("Reset Logic", "Block", ["复位时序", "看门狗"]),
    ("Reset Logic", "System", ["全系统复位"]),
]


def get_db_path(project_name):
    """获取项目数据库路径"""
    return os.path.join(DATA_DIR, f"{project_name}.db")


def init_db(db_path):
    """初始化数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建 cover_point 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cover_point (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            feature TEXT,
            sub_feature TEXT,
            cover_point TEXT,
            cover_point_details TEXT,
            comments TEXT,
            priority TEXT DEFAULT 'P0',
            created_at TEXT
        )
    """)
    
    # 创建 test_case 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_case (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            dv_milestone TEXT,
            testbench TEXT,
            category TEXT,
            owner TEXT,
            test_name TEXT,
            scenario_details TEXT,
            checker_details TEXT,
            coverage_details TEXT,
            comments TEXT,
            priority TEXT DEFAULT 'P0',
            status TEXT DEFAULT 'OPEN',
            created_at TEXT,
            coded_date TEXT,
            fail_date TEXT,
            pass_date TEXT,
            removed_date TEXT,
            target_date TEXT
        )
    """)
    
    # 创建关联表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tc_cp_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tc_id INTEGER,
            cp_id INTEGER
        )
    """)
    
    # 创建 tracker_version 表（兼容）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracker_version (
            version TEXT,
            migrated_at TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO tracker_version VALUES (?, ?)", 
                   ("v0.8.0", datetime.now().strftime("%Y-%m-%d")))
    
    conn.commit()
    return conn


def load_projects():
    """加载项目列表"""
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_projects(projects):
    """保存项目列表"""
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)


def cleanup():
    """清理旧项目"""
    print(f"\n🧹 清理旧项目...")
    
    # 删除数据库文件
    db_path = get_db_path(PROJECT_NAME)
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"   ✅ 删除数据库: {db_path}")
    
    # 从 projects.json 移除
    projects = load_projects()
    projects = [p for p in projects if p.get("name") != PROJECT_NAME]
    save_projects(projects)
    print(f"   ✅ 从项目列表移除")


def create_project_record(project_id):
    """创建项目记录"""
    projects = load_projects()
    
    # 检查是否已存在
    existing = [p for p in projects if p.get("name") == PROJECT_NAME]
    if existing:
        # 更新
        for p in projects:
            if p.get("name") == PROJECT_NAME:
                p["id"] = project_id
                p["start_date"] = PROJECT_START
                p["end_date"] = PROJECT_END
    else:
        # 新增
        projects.append({
            "id": project_id,
            "name": PROJECT_NAME,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "dev",
            "is_archived": False,
            "start_date": PROJECT_START,
            "end_date": PROJECT_END
        })
    
    save_projects(projects)
    print(f"   ✅ 项目记录已保存")


def generate_cover_points(conn, project_id):
    """生成 Cover Points"""
    print(f"\n📋 生成 Cover Points ({len(COVER_POINTS)} 个)...")
    
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    cp_ids = []
    for feature, sub_feature, cover_point, priority in COVER_POINTS:
        cursor.execute("""
            INSERT INTO cover_point 
            (project_id, feature, sub_feature, cover_point, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (project_id, feature, sub_feature, cover_point, priority, created_at))
        cp_ids.append(cursor.lastrowid)
    
    conn.commit()
    print(f"   ✅ 已创建 {len(cp_ids)} 个 CP")
    return cp_ids


def calculate_target_date(dv_milestone, project_start, project_end):
    """根据 DV Milestone 计算目标日期"""
    start_date = datetime.strptime(project_start, "%Y-%m-%d")
    end_date = datetime.strptime(project_end, "%Y-%m-%d")
    total_days = (end_date - start_date).days
    
    progress = DV_MILESTONE_PROGRESS.get(dv_milestone, 0.5)
    target_days = int(total_days * progress)
    target_date = start_date + timedelta(days=target_days)
    
    return target_date.strftime("%Y-%m-%d")


def generate_test_cases(conn, project_id, cp_ids):
    """生成 Test Cases"""
    print(f"\n📋 生成 Test Cases ({sum(TC_STATUS.values())} 个)...")
    
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    tc_ids = []
    tc_statuses = []
    for status, count in TC_STATUS.items():
        tc_statuses.extend([status] * count)
    
    # 打乱顺序
    random.shuffle(tc_statuses)
    
    # 按 Feature 分组 CP
    cp_by_feature = {}
    cursor.execute("SELECT id, feature FROM cover_point WHERE project_id = ?", (project_id,))
    for row in cursor.fetchall():
        cp_id, feature = row
        if feature not in cp_by_feature:
            cp_by_feature[feature] = []
        cp_by_feature[feature].append(cp_id)
    
    # 生成 TC
    tc_index = 0
    for dv_milestone in DV_MILESTONES:
        for feature, category, scenarios in TC_TEMPLATES:
            if tc_index >= len(tc_statuses):
                break
            
            status = tc_statuses[tc_index]
            tc_index += 1
            
            scenario = random.choice(scenarios)
            testbench = f"tb_{feature.lower().replace(' ', '_')}"
            test_name = f"{dv_milestone}_{feature}_{category}_{tc_index:03d}"
            owner = random.choice(["zhangsan", "lisi", "wangwu", "zhaoliu"])
            
            # 目标日期
            target_date = calculate_target_date(dv_milestone, PROJECT_START, PROJECT_END)
            
            # 状态日期
            status_date = None
            if status == "PASS":
                status_date = target_date
            elif status == "FAIL":
                status_date = target_date
            elif status == "CODED":
                status_date = target_date
            
            cursor.execute("""
                INSERT INTO test_case 
                (project_id, dv_milestone, testbench, category, owner, test_name,
                 scenario_details, priority, status, created_at, target_date, pass_date, fail_date, coded_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, dv_milestone, testbench, category, owner, test_name,
                  scenario, "P0", status, created_at, target_date, 
                  status_date if status == "PASS" else None,
                  status_date if status == "FAIL" else None,
                  status_date if status == "CODED" else None))
            
            tc_id = cursor.lastrowid
            tc_ids.append(tc_id)
            
            # 建立 TC-CP 关联 (PASS 状态的 TC 必须关联 CP)
            if feature in cp_by_feature:
                num_connections = random.randint(1, min(3, len(cp_by_feature[feature])))
                selected_cps = random.sample(cp_by_feature[feature], num_connections)
                for cp_id in selected_cps:
                    cursor.execute("""
                        INSERT INTO tc_cp_connections (tc_id, cp_id)
                        VALUES (?, ?)
                    """, (tc_id, cp_id))
    
    conn.commit()
    print(f"   ✅ 已创建 {len(tc_ids)} 个 TC")
    return tc_ids


# Demo 快照数据 - 模拟项目进行中的实际进度
# 特点：初期偏离计划大，后期加速追赶，在计划线附近波动
#
# ⚠️ 重要修正：快照日期必须对齐后端的计划曲线 week 起始日！
# 后端 calculate_planned_coverage() 使用 current.isoformat() 作为 week 字段
#
# 项目周期: 2026-01-06 (周二) ~ 2026-04-18
#
# 当前实际计划曲线（由 PASS TC 分布决定）:
#   Week 1-4: 0% (无 PASS TC target_date 在这些周)
#   Week 5-7: 50% (15 CP)
#   Week 8-10: 60% (18 CP)
#   Week 11+: 73.3% (22 CP)
#
# 实际曲线设计：
# - 初期大幅落后于计划（0% vs 50%）
# - Week 7 追赶到 45%（仍低于计划50%）
# - Week 8 超过计划（55% vs 60%计划）
# - 之后在计划线附近波动
DEMO_SNAPSHOTS = [
    # (日期对齐计划的 week 起始日, 实际覆盖率, TC_Pass, TC_Total, CP_Covered, CP_Total)
    # Week 1: 计划0%, 实际0%
    ("2026-01-06", 0, 0, 52, 0, 30),
    # Week 2: 计划0%, 实际2% (开始落后)
    ("2026-01-12", 2, 1, 52, 1, 30),
    # Week 3: 计划0%, 实际5%
    ("2026-01-19", 5, 3, 52, 3, 30),
    # Week 4: 计划0%, 实际8% (最大偏离)
    ("2026-01-26", 8, 4, 52, 4, 30),
    # Week 5: 计划50%, 实际15% (大幅落后)
    ("2026-02-02", 15, 8, 52, 8, 30),
    # Week 6: 计划50%, 实际25%
    ("2026-02-09", 25, 13, 52, 13, 30),
    # Week 7: 计划50%, 实际45% (接近计划)
    ("2026-02-16", 45, 22, 52, 22, 30),
    # Week 8: 计划60%, 实际55% (被计划超过)
    ("2026-02-23", 55, 27, 52, 27, 30),
    # Week 9: 计划60%, 实际58% (接近计划)
    ("2026-03-02", 58, 29, 52, 29, 30),
    # Week 10: 计划60%, 实际65% (超过计划)
    ("2026-03-09", 65, 32, 52, 32, 30),
    # Week 11: 计划73.3%, 实际70% (被计划超过)
    ("2026-03-16", 70, 35, 52, 35, 30),
    # Week 12: 计划73.3%, 实际75%
    ("2026-03-23", 75, 37, 52, 37, 30),
]


from datetime import datetime, timedelta


def calculate_weekly_dates(project_start, project_end):
    """计算每周的起始日期（对齐后端计划曲线算法）"""
    dates = []
    current = datetime.strptime(project_start, '%Y-%m-%d').date()
    end = datetime.strptime(project_end, '%Y-%m-%d').date()
    
    while current <= end:
        dates.append(current.isoformat())
        # 计算本周的周日
        days_until_sunday = (6 - current.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        week_end = current + timedelta(days=days_until_sunday)
        if week_end > end:
            week_end = end
        # 移到下一周
        current = week_end + timedelta(days=1)
    
    return dates


def calculate_planned_coverage_from_db(conn, project_start, project_end):
    """从数据库计算实际计划曲线（与后端算法一致）"""
    cursor = conn.cursor()
    
    # 获取总 CP 数
    cursor.execute('SELECT COUNT(*) FROM cover_point')
    total_cp = cursor.fetchone()[0]
    if total_cp == 0:
        return {}
    
    # 计算每周的计划覆盖率
    weekly_dates = calculate_weekly_dates(project_start, project_end)
    planned = {}
    
    for week_start in weekly_dates:
        week_start_date = datetime.strptime(week_start, '%Y-%m-%d').date()
        days_until_sunday = (6 - week_start_date.weekday()) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
        week_end = week_start_date + timedelta(days=days_until_sunday)
        week_end_str = week_end.isoformat()
        
        # 计算该周末之前的 PASS TC 关联 CP 覆盖率
        cursor.execute('''
            WITH pass_tcs AS (
                SELECT DISTINCT tc.id FROM test_case tc
                WHERE tc.status = "PASS" AND tc.target_date IS NOT NULL AND tc.target_date <= ?
            ),
            covered_cps AS (
                SELECT DISTINCT cp.id FROM tc_cp_connections tcc
                INNER JOIN pass_tcs pt ON tcc.tc_id = pt.id
                INNER JOIN cover_point cp ON tcc.cp_id = cp.id
            )
            SELECT COUNT(*) FROM covered_cps
        ''', (week_end_str,))
        
        covered_cp = cursor.fetchone()[0]
        coverage = round((covered_cp / total_cp) * 100, 1)
        planned[week_start] = coverage
    
    return planned


def generate_snapshots(conn, project_id):
    """生成 Demo 快照 - 根据实际计划曲线动态生成匹配的快照数据"""
    
    # 项目周期
    project_start = "2026-01-06"
    project_end = "2026-04-18"
    
    # 先计算实际计划曲线
    print(f"\n📸 计算实际计划曲线...")
    planned = calculate_planned_coverage_from_db(conn, project_start, project_end)
    
    # 获取每周日期
    weekly_dates = calculate_weekly_dates(project_start, project_end)
    
    # 找到计划曲线的关键跳跃点
    jumps = []
    prev_coverage = 0
    for date, coverage in planned.items():
        if coverage != prev_coverage:
            jumps.append((date, coverage))
        prev_coverage = coverage
    
    print(f"   计划曲线关键点: {jumps}")
    
    # 生成匹配的快照数据
    # 策略：初期落后于计划，后期在计划线附近波动
    snapshots = []
    prev_actual = 0
    
    for i, week_date in enumerate(weekly_dates[:12]):  # 取前12周
        planned_cov = planned.get(week_date, 0)
        
        if i < 4:
            # 前4周：计划0%，实际逐步增加
            actual_cov = (i + 1) * 2  # 2%, 4%, 6%, 8%
        elif i == 4:
            # 第5周：计划跳跃后大幅落后
            actual_cov = planned_cov * 0.3  # 30% of 计划
        elif i == 5:
            # 第6周：继续追赶
            actual_cov = planned_cov * 0.5
        elif i == 6:
            # 第7周：接近计划
            actual_cov = planned_cov * 0.85
        elif i == 7:
            # 第8周：首次超过或接近
            actual_cov = planned_cov + 2
        else:
            # 之后：在计划线附近波动
            diff = (i - 7) * 3  # 轻微波动
            actual_cov = min(planned_cov + diff, 95)  # 不超过95%
        
        actual_cov = round(actual_cov, 1)
        tc_pass = int(actual_cov * 52 / 100)  # 估算
        cp_covered = int(actual_cov * 30 / 100)  # 估算
        
        snapshots.append((week_date, actual_cov, tc_pass, 52, cp_covered, 30))
        prev_actual = actual_cov
    
    # 插入快照数据
    cursor = conn.cursor()
    
    # 确保 project_progress 表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            snapshot_date TEXT NOT NULL,
            actual_coverage REAL,
            tc_pass_count INTEGER,
            tc_total INTEGER,
            cp_covered INTEGER,
            cp_total INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT,
            updated_by TEXT,
            UNIQUE(project_id, snapshot_date)
        )
    """)
    
    for date, coverage, tc_pass, tc_total, cp_covered, cp_total in snapshots:
        cursor.execute("""
            INSERT OR REPLACE INTO project_progress 
            (project_id, snapshot_date, actual_coverage, 
             tc_pass_count, tc_total, cp_covered, cp_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project_id, date, coverage, tc_pass, tc_total, cp_covered, cp_total))
    
    conn.commit()
    print(f"   ✅ 已生成 {len(snapshots)} 个历史快照")
    print(f"   📈 初期偏离计划，后期加速追赶")


def main():
    parser = argparse.ArgumentParser(description="创建 SOC_DV 示例项目")
    parser.add_argument("--force", "-f", action="store_true", 
                        help="重新创建（带清理）")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎯 SOC_DV 示例项目生成器")
    print("=" * 60)
    
    # 检查数据目录
    if not os.path.exists(DATA_DIR):
        print(f"❌ 错误: 数据目录不存在: {DATA_DIR}")
        sys.exit(1)
    
    # 清理旧项目
    if args.force:
        cleanup()
    
    # 检查项目是否已存在
    projects = load_projects()
    existing = [p for p in projects if p.get("name") == PROJECT_NAME]
    if existing and not args.force:
        print(f"\n⚠️ 项目 '{PROJECT_NAME}' 已存在")
        print(f"   使用 --force 重新创建")
        sys.exit(0)
    
    # 创建数据库
    db_path = get_db_path(PROJECT_NAME)
    print(f"\n📦 创建数据库: {db_path}")
    conn = init_db(db_path)
    print(f"   ✅ 数据库初始化完成")
    
    # 获取项目 ID
    project_id = 1
    if projects:
        max_id = max(p.get("id", 0) for p in projects)
        project_id = max_id + 1
    
    # 创建项目记录
    create_project_record(project_id)
    
    # 生成 CP
    cp_ids = generate_cover_points(conn, project_id)
    
    # 生成 TC
    tc_ids = generate_test_cases(conn, project_id, cp_ids)
    
    # 生成 Demo 快照
    generate_snapshots(conn, project_id)
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 示例项目创建完成!")
    print("=" * 60)
    print(f"\n📁 项目: {PROJECT_NAME}")
    print(f"📅 周期: {PROJECT_START} ~ {PROJECT_END} (15 周)")
    print(f"📋 CP 数量: {len(cp_ids)}")
    print(f"📋 TC 数量: {len(tc_ids)}")
    print(f"\n💡 访问: http://localhost:8081")
    print(f"   选择项目: {PROJECT_NAME}")


if __name__ == "__main__":
    main()
