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


# 项目配置 - TC-CP 模式
SOC_DV_CONFIG = {
    "name": "SOC_DV",
    "desc": "RISC-V SoC 芯片系统级验证项目",
    "coverage_mode": "tc_cp",
    "start_date": "2026-01-06",
    "end_date": "2026-04-18",
}

# 项目配置 - FC-CP 模式
FC_DV_CONFIG = {
    "name": "FC_DV",
    "desc": "RISC-V SoC 功能覆盖验证项目",
    "coverage_mode": "fc_cp",
    "start_date": "2026-01-06",
    "end_date": "2026-04-18",
}

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

# FC 生成模板 (用于 FC-CP 模式)
# (covergroup, coverpoint, coverage_type, bin_name, bin_val, coverage_pct, status)
FC_TEMPLATES = [
    # CPU Core FC (所有指令类型覆盖)
    ("CPU Core", "instruction_rtype", "coverpoint", "rtype_add", "1", 95.5, "ready"),
    ("CPU Core", "instruction_rtype", "coverpoint", "rtype_sub", "1", 88.2, "ready"),
    ("CPU Core", "instruction_rtype", "coverpoint", "rtype_and", "1", 92.0, "ready"),
    ("CPU Core", "instruction_rtype", "coverpoint", "rtype_or", "1", 87.5, "ready"),
    ("CPU Core", "instruction_rtype", "coverpoint", "rtype_xor", "1", 78.3, "ready"),
    ("CPU Core", "instruction_itype", "coverpoint", "itype_addi", "1", 91.0, "ready"),
    ("CPU Core", "instruction_itype", "coverpoint", "itype_subi", "1", 85.5, "ready"),
    ("CPU Core", "instruction_itype", "coverpoint", "itype_andi", "1", 82.0, "ready"),
    ("CPU Core", "instruction_stype", "coverpoint", "stype_sw", "1", 89.0, "ready"),
    ("CPU Core", "instruction_stype", "coverpoint", "stype_sh", "1", 65.0, "ready"),
    ("CPU Core", "instruction_utype", "coverpoint", "utype_auipc", "1", 75.0, "ready"),
    ("CPU Core", "instruction_utype", "coverpoint", "utype_lui", "1", 80.0, "ready"),
    ("CPU Core", "instruction_jtype", "coverpoint", "jtype_jal", "1", 88.0, "ready"),
    ("CPU Core", "instruction_jtype", "coverpoint", "jtype_jalr", "1", 85.0, "ready"),
    ("CPU Core", "instruction_btype", "coverpoint", "btype_beq", "1", 90.0, "ready"),
    ("CPU Core", "instruction_btype", "coverpoint", "btype_bne", "1", 87.0, "ready"),
    ("CPU Core", "cache_coherency", "coverpoint", "mesi_states", "1", 100.0, "ready"),
    ("CPU Core", "cache_coherency", "coverpoint", "bus_transaction", "1", 78.0, "ready"),
    ("CPU Core", "exception", "coverpoint", "ecall", "1", 95.0, "ready"),
    ("CPU Core", "exception", "coverpoint", "ebreak", "1", 88.0, "ready"),
    ("CPU Core", "privilege", "coverpoint", "mode_switch", "1", 72.0, "ready"),
    # L2 Cache FC
    ("L2 Cache", "miss_rate", "coverpoint", "read_miss", "1", 45.0, "ready"),
    ("L2 Cache", "miss_rate", "coverpoint", "write_miss", "1", 52.0, "ready"),
    ("L2 Cache", "coherency", "coverpoint", "mesi_protocol", "1", 88.0, "ready"),
    ("L2 Cache", "coherency", "coverpoint", "snoops", "1", 75.0, "ready"),
    ("L2 Cache", "eviction", "coverpoint", "lru_replace", "1", 60.0, "ready"),
    # DDR Controller FC
    ("DDR Controller", "read_timing", "coverpoint", "read_latency", "1", 92.0, "ready"),
    ("DDR Controller", "write_timing", "coverpoint", "write_latency", "1", 89.0, "ready"),
    ("DDR Controller", "mode_switch", "coverpoint", "precharge", "1", 55.0, "ready"),
    ("DDR Controller", "mode_switch", "coverpoint", "refresh", "1", 78.0, "ready"),
    # PCIe Controller FC
    ("PCIe Controller", "config_space", "coverpoint", "cfg_read", "1", 85.0, "ready"),
    ("PCIe Controller", "config_space", "coverpoint", "cfg_write", "1", 80.0, "ready"),
    ("PCIe Controller", "transaction", "coverpoint", "mem_read", "1", 92.0, "ready"),
    ("PCIe Controller", "transaction", "coverpoint", "mem_write", "1", 88.0, "ready"),
    ("PCIe Controller", "msi", "coverpoint", "msi_x", "1", 45.0, "ready"),
    # GPIO FC
    ("GPIO", "interrupt", "coverpoint", "int_enable", "1", 78.0, "ready"),
    ("GPIO", "interrupt", "coverpoint", "int_pending", "1", 65.0, "ready"),
    ("GPIO", "edge", "coverpoint", "rising_edge", "1", 82.0, "ready"),
    ("GPIO", "edge", "coverpoint", "falling_edge", "1", 75.0, "ready"),
    # Clock Manager FC
    ("Clock Manager", "gating", "coverpoint", "clk_gated", "1", 90.0, "ready"),
    ("Clock Manager", "sync", "coverpoint", "cdc_path", "1", 68.0, "ready"),
    ("Clock Manager", "pll", "coverpoint", "pll_lock", "1", 95.0, "ready"),
    # Reset Logic FC
    ("Reset Logic", "power_on", "coverpoint", "reset_seq", "1", 100.0, "ready"),
    ("Reset Logic", "watchdog", "coverpoint", "wd_timeout", "1", 55.0, "ready"),
]


def get_db_path(project_name):
    """获取项目数据库路径"""
    return os.path.join(DATA_DIR, f"{project_name}.db")


def init_db(db_path, coverage_mode="tc_cp"):
    """初始化数据库

    Args:
        db_path: 数据库路径
        coverage_mode: "tc_cp" 或 "fc_cp"
    """
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

    # FC-CP 模式需要的功能覆盖表 (v0.11.0)
    if coverage_mode == "fc_cp":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS functional_coverage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                covergroup TEXT NOT NULL,
                coverpoint TEXT NOT NULL,
                coverage_type TEXT NOT NULL,
                bin_name TEXT NOT NULL,
                bin_val TEXT,
                comments TEXT,
                coverage_pct REAL DEFAULT 0.0,
                status TEXT DEFAULT 'missing' CHECK (status IN ('missing', 'ready')),
                owner TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                UNIQUE (project_id, covergroup, coverpoint, bin_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fc_cp_association (
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

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fc_covergroup ON functional_coverage(covergroup)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fc_coverpoint ON functional_coverage(coverpoint)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fc_cp_assoc_cp ON fc_cp_association(cp_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fc_cp_assoc_fc ON fc_cp_association(fc_id)")

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


def cleanup_project(project_name):
    """清理指定旧项目"""
    # 删除数据库文件
    db_path = get_db_path(project_name)
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"   ✅ 删除数据库: {db_path}")

    # 从 projects.json 移除
    projects = load_projects()
    projects = [p for p in projects if p.get("name") != project_name]
    save_projects(projects)


def create_project_record(project_id, config):
    """创建项目记录

    Args:
        project_id: 项目ID
        config: 项目配置字典
    """
    project_name = config["name"]
    projects = load_projects()

    # 检查是否已存在
    existing = [p for p in projects if p.get("name") == project_name]
    if existing:
        # 更新
        for p in projects:
            if p.get("name") == project_name:
                p["id"] = project_id
                p["start_date"] = config["start_date"]
                p["end_date"] = config["end_date"]
                p["coverage_mode"] = config.get("coverage_mode", "tc_cp")
    else:
        # 新增
        projects.append({
            "id": project_id,
            "name": project_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "dev",
            "is_archived": False,
            "start_date": config["start_date"],
            "end_date": config["end_date"],
            "coverage_mode": config.get("coverage_mode", "tc_cp")
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


def generate_test_cases(conn, project_id, cp_ids, config):
    """生成 Test Cases

    Args:
        conn: 数据库连接
        project_id: 项目ID
        cp_ids: CP ID列表
        config: 项目配置字典
    """
    project_start = config["start_date"]
    project_end = config["end_date"]

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
            target_date = calculate_target_date(dv_milestone, project_start, project_end)

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


def generate_functional_coverage(conn, project_id, config):
    """生成 Functional Coverage 数据 (FC-CP 模式)

    Args:
        conn: 数据库连接
        project_id: 项目ID
        config: 项目配置字典
    """
    print(f"\n📋 生成 Functional Coverage ({len(FC_TEMPLATES)} 个)...")

    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d")

    fc_ids = []
    for covergroup, coverpoint, coverage_type, bin_name, bin_val, coverage_pct, status in FC_TEMPLATES:
        cursor.execute("""
            INSERT INTO functional_coverage
            (project_id, covergroup, coverpoint, coverage_type, bin_name, bin_val,
             coverage_pct, status, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, covergroup, coverpoint, coverage_type, bin_name, bin_val,
              coverage_pct, status, "admin", created_at))
        fc_ids.append(cursor.lastrowid)

    conn.commit()
    print(f"   ✅ 已创建 {len(fc_ids)} 个 FC")
    return fc_ids


def generate_fc_cp_associations(conn, project_id, fc_ids, config):
    """生成 FC-CP 关联

    Args:
        conn: 数据库连接
        project_id: 项目ID
        fc_ids: FC ID列表
        config: 项目配置字典

    策略：根据 FC coverpoint 名称智能匹配对应的 CP
    - instruction_rtype -> R-Type
    - instruction_itype -> I-Type
    - instruction_stype -> S-Type
    - instruction_utype -> U-Type
    - instruction_jtype -> J-Type
    - instruction_btype -> B-Type
    - miss_rate -> Miss Rate
    - coherency -> Coherency
    - eviction -> Eviction
    - read_timing -> Read
    - write_timing -> Write
    - config_space -> Config
    - transaction -> Transaction
    - msi -> MSI
    - interrupt -> Interrupt
    - edge -> Edge
    - gating -> Gating
    - sync -> Sync
    - pll -> PLL
    - power_on / power_on_reset -> PowerOn
    - watchdog -> Watchdog
    - sw_reset / software_reset -> SW Reset
    """
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d")

    # 获取所有 CP
    all_cps = []
    cursor.execute("SELECT id, feature, sub_feature, cover_point FROM cover_point WHERE project_id = ?", (project_id,))
    for row in cursor.fetchall():
        cp_id, feature, sub_feature, cover_point = row
        all_cps.append({
            'id': cp_id,
            'feature': feature,
            'sub_feature': sub_feature,
            'cover_point': cover_point
        })

    # 建立 FC-CP 关联
    assoc_count = 0

    # 关键词到 CP 匹配规则的映射
    keyword_rules = [
        # 指令类型 -> 匹配 R/I/S/U/J/B-Type
        ('instruction_rtype', 'R-Type'),
        ('instruction_itype', 'I-Type'),
        ('instruction_stype', 'S-Type'),
        ('instruction_utype', 'U-Type'),
        ('instruction_jtype', 'J-Type'),
        ('instruction_btype', 'B-Type'),
        # CPU Core 其他
        ('cache_coherency', '缓存一致性协议'),
        ('exception', '异常场景覆盖'),
        ('privilege', '特权模式切换'),
        # L2 Cache
        ('miss_rate', '缓存未命中统计'),
        ('coherency', '缓存一致性 MESI'),
        ('eviction', '缓存行替换策略'),
        # DDR Controller
        ('read_timing', '读事务覆盖'),
        ('write_timing', '写事务覆盖'),
        ('mode_switch', 'DDR 模式切换'),
        # PCIe Controller
        ('config_space', '配置空间访问'),
        ('transaction', '事务层覆盖'),
        ('msi', 'MSI 中断传输'),
        ('power', '功耗状态转换'),
        # GPIO
        ('interrupt', '中断触发'),
        ('edge', '边沿检测'),
        ('debounce', '防抖处理'),
        # Clock Manager
        ('gating', '时钟门控'),
        ('sync', '跨时钟域同步'),
        ('pll', 'PLL 锁定时间'),
        # Reset Logic
        ('power_on', '上电复位序列'),
        ('watchdog', '看门狗复位'),
        ('sw_reset', '软件复位'),
    ]

    for fc_id, fc_data in zip(fc_ids, FC_TEMPLATES):
        covergroup = fc_data[0]
        coverpoint = fc_data[1]  # fc_data: (covergroup, coverpoint, coverage_type, bin_name, bin_val, coverage_pct, status)

        # 根据 coverpoint 关键词查找匹配的 CP
        matched_cp = None
        for keyword, target_name in keyword_rules:
            if keyword in coverpoint.lower():
                # 找到匹配的 CP：feature 相同且 cover_point 或 sub_feature 包含目标名称
                for cp in all_cps:
                    if cp['feature'] == covergroup:
                        cp_name = cp['cover_point'] or ''
                        sub_feat = cp['sub_feature'] or ''
                        if target_name in cp_name or target_name in sub_feat:
                            matched_cp = cp
                            break
                if matched_cp:
                    break

        if matched_cp:
            # 智能匹配：直接关联到对应的 CP
            try:
                cursor.execute("""
                    INSERT INTO fc_cp_association (project_id, cp_id, fc_id, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (project_id, matched_cp['id'], fc_id, "admin", created_at))
                assoc_count += 1
            except sqlite3.IntegrityError:
                pass
        else:
            # 回退策略：同一 feature 下随机关联 1 个 CP
            feature_cps = [cp for cp in all_cps if cp['feature'] == covergroup]
            if feature_cps:
                cp = random.choice(feature_cps)
                try:
                    cursor.execute("""
                        INSERT INTO fc_cp_association (project_id, cp_id, fc_id, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (project_id, cp['id'], fc_id, "admin", created_at))
                    assoc_count += 1
                except sqlite3.IntegrityError:
                    # 忽略重复关联
                    pass

    conn.commit()
    print(f"   ✅ 已创建 {assoc_count} 个 FC-CP 关联")
    return assoc_count


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


def calculate_priority_coverage(week_date):
    """
    计算指定周各 Priority 的覆盖率
    
    对于 Demo 项目，使用模拟策略生成符合真实场景的数据：
    - P0 优先级最高，进度最快
    - P1 次之
    - P2 进度较慢
    - P3 通常为 0
    
    策略：每周生成时，按照时间推进逐步增加各 Priority 的覆盖率
    
    Args:
        week_date: 周的起始日期 (ISO 格式字符串，如 '2026-01-06')
    """
    # 获取周索引 (0-11)
    weekly_dates = calculate_weekly_dates("2026-01-06", "2026-04-18")
    week_idx = 0
    for i, d in enumerate(weekly_dates[:12]):
        if d == week_date:
            week_idx = i
            break
    
    # Demo 策略：各 Priority 的覆盖率演变
    # 初期 P0 领先，P1/P2 跟进
    if week_idx < 4:
        # Week 1-4: 只有少量 CP 覆盖
        p0 = min(week_idx * 5 + 10, 40)   # 10%, 15%, 20%, 25%
        p1 = min(week_idx * 3, 12)         # 0%, 3%, 6%, 9%
        p2 = min(week_idx * 2, 8)         # 0%, 0%, 4%, 6%
        p3 = 0
    elif week_idx < 7:
        # Week 5-7: P0 快速提升
        offset = week_idx - 4
        p0 = min(40 + offset * 15, 85)    # 55%, 70%, 85%
        p1 = min(12 + offset * 10, 42)    # 22%, 32%, 42%
        p2 = min(8 + offset * 8, 32)       # 16%, 24%, 32%
        p3 = 0
    else:
        # Week 8-12: 全面追赶
        offset = week_idx - 7
        p0 = min(85 + offset * 3, 100)    # 接近完成
        p1 = min(42 + offset * 10, 80)
        p2 = min(32 + offset * 8, 60)
        p3 = 0
    
    result = {}
    result['p0_coverage'] = p0
    result['p1_coverage'] = p1
    result['p2_coverage'] = p2
    result['p3_coverage'] = p3
    
    return result


def generate_snapshots(conn, project_id, config):
    """生成 Demo 快照 - 根据实际计划曲线动态生成匹配的快照数据

    v0.10.0: 扩展支持各 Priority 覆盖率计算

    Args:
        conn: 数据库连接
        project_id: 项目ID
        config: 项目配置字典
    """

    # 项目周期
    project_start = config["start_date"]
    project_end = config["end_date"]

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
    
    # 获取每种 Priority 的 CP 总数
    cursor = conn.cursor()
    priority_totals = {}
    for priority in ['P0', 'P1', 'P2', 'P3']:
        cursor.execute("SELECT COUNT(*) FROM cover_point WHERE priority = ?", (priority,))
        priority_totals[priority] = cursor.fetchone()[0]
    print(f"   CP 分布: {priority_totals}")
    
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
        
        # 计算各 Priority 覆盖率
        priority_cov = calculate_priority_coverage(week_date)
        
        snapshots.append({
            'date': week_date,
            'actual_coverage': actual_cov,
            'tc_pass': tc_pass,
            'tc_total': 52,
            'cp_covered': cp_covered,
            'cp_total': 30,
            'p0_coverage': priority_cov.get('p0_coverage', 0),
            'p1_coverage': priority_cov.get('p1_coverage', 0),
            'p2_coverage': priority_cov.get('p2_coverage', 0),
            'p3_coverage': priority_cov.get('p3_coverage', 0),
        })
        prev_actual = actual_cov
    
    # 插入快照数据
    # 确保 project_progress 表存在（包含 Priority 覆盖率字段）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            snapshot_date TEXT NOT NULL,
            actual_coverage REAL,
            p0_coverage REAL,
            p1_coverage REAL,
            p2_coverage REAL,
            p3_coverage REAL,
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
    
    for snap in snapshots:
        cursor.execute("""
            INSERT OR REPLACE INTO project_progress 
            (project_id, snapshot_date, actual_coverage, 
             p0_coverage, p1_coverage, p2_coverage, p3_coverage,
             tc_pass_count, tc_total, cp_covered, cp_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, snap['date'], snap['actual_coverage'],
              snap['p0_coverage'], snap['p1_coverage'], snap['p2_coverage'], snap['p3_coverage'],
              snap['tc_pass'], snap['tc_total'], snap['cp_covered'], snap['cp_total']))
    
    conn.commit()
    print(f"   ✅ 已生成 {len(snapshots)} 个历史快照")
    print(f"   📈 初期偏离计划，后期加速追赶")
    print(f"   📊 Priority 覆盖率已计算并保存")


def create_demo_project(config):
    """创建单个演示项目

    Args:
        config: 项目配置字典
    """
    project_name = config["name"]
    coverage_mode = config.get("coverage_mode", "tc_cp")

    print(f"\n{'=' * 60}")
    print(f"🎯 创建项目: {project_name} ({coverage_mode})")
    print(f"{'=' * 60}")

    # 清理旧项目
    cleanup_project(project_name)

    # 检查项目是否已存在
    projects = load_projects()
    existing = [p for p in projects if p.get("name") == project_name]

    # 创建数据库
    db_path = get_db_path(project_name)
    print(f"\n📦 创建数据库: {db_path}")
    conn = init_db(db_path, coverage_mode)
    print(f"   ✅ 数据库初始化完成")

    # 获取项目 ID
    project_id = 1
    if projects:
        max_id = max(p.get("id", 0) for p in projects)
        project_id = max_id + 1

    # 创建项目记录
    create_project_record(project_id, config)

    # 生成 CP (共用 COVER_POINTS)
    cp_ids = generate_cover_points(conn, project_id)

    if coverage_mode == "fc_cp":
        # FC-CP 模式: 生成 FC 和 FC-CP 关联
        fc_ids = generate_functional_coverage(conn, project_id, config)
        generate_fc_cp_associations(conn, project_id, fc_ids, config)
        # FC-CP 模式也需要快照
        generate_snapshots(conn, project_id, config)
    else:
        # TC-CP 模式: 生成 TC 和 TC-CP 关联
        tc_ids = generate_test_cases(conn, project_id, cp_ids, config)
        # 生成 Demo 快照
        generate_snapshots(conn, project_id, config)

    conn.close()

    print(f"\n📁 项目: {project_name}")
    print(f"📅 周期: {config['start_date']} ~ {config['end_date']}")
    print(f"📋 CP 数量: {len(cp_ids)}")
    if coverage_mode == "fc_cp":
        print(f"📊 FC-CP 模式")
    else:
        print(f"📋 TC 模式")


def main():
    parser = argparse.ArgumentParser(description="创建演示项目")
    parser.add_argument("--force", "-f", action="store_true",
                        help="重新创建（带清理）")
    parser.add_argument("--project", "-p", choices=["soc_dv", "fc_dv", "all"],
                        default="all", help="指定要创建的项目")
    args = parser.parse_args()

    print("=" * 60)
    print("🎯 Tracker 演示项目生成器")
    print("=" * 60)

    # 检查数据目录
    if not os.path.exists(DATA_DIR):
        print(f"❌ 错误: 数据目录不存在: {DATA_DIR}")
        sys.exit(1)

    # 清理旧项目
    if args.force:
        print("\n🧹 清理旧项目...")
        if args.project in ["soc_dv", "all"]:
            cleanup_project(SOC_DV_CONFIG["name"])
        if args.project in ["fc_dv", "all"]:
            cleanup_project(FC_DV_CONFIG["name"])

    # 创建项目
    if args.project in ["soc_dv", "all"]:
        create_demo_project(SOC_DV_CONFIG)

    if args.project in ["fc_dv", "all"]:
        create_demo_project(FC_DV_CONFIG)

    print("\n" + "=" * 60)
    print("✅ 所有演示项目创建完成!")
    print("=" * 60)
    print(f"\n💡 访问: http://localhost:8081")
    print(f"   选择项目: SOC_DV (TC-CP) 或 FC_DV (FC-CP)")


if __name__ == "__main__":
    main()
