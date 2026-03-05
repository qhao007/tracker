# 测试数据生成工具 - Demo Project Generator

> **版本**: v1.2 | **创建日期**: 2026-03-02 | **状态**: ✅ 已完成

---

## 1. 概述

### 1.1 目的

创建一个便捷的工具，用于在测试数据目录 (`test_data`) 中生成芯片验证主题的示例项目，方便演示和功能测试。

### 1.2 背景

Tracker 作为一个芯片验证管理工具，需要一个真实感的示例项目来：
- 演示系统功能
- 进行功能测试
- 展示给新用户

### 1.3 目标

- 生成一个包含完整数据（CP/TC/关联关系）的示例项目
- 主题采用真实芯片验证场景（SOC 级别验证）
- 工具化，支持按需重新生成

---

## 2. 主题设计

### 2.1 项目名称

**项目名称**: `SOC_DV` (System-on-Chip Design Verification)

**项目描述**: 一款 RISC-V 架构的 SoC 芯片系统级验证项目

### 2.2 项目周期

| 字段 | 值 |
|------|-----|
| 开始日期 | 2026-01-06 (第一周周一) |
| 结束日期 | 2026-04-18 (15周后周五) |

> **DV Milestone 含义**：
> - DV1.0: 项目结束日期 (100%)
> - DV0.5: 项目中期 (50%，约第8周)
> - DV0.7: 项目后期 (70%，约第11周)
> - DV0.3: 项目早期 (30%，约第5周)

### 2.3 数据层级结构

```
SOC_DV 项目 (15 周周期)
│
├── DV Milestone (验证里程碑 - 使用系统选项，与项目进度相关)
│   ├── DV1.0 (项目结束日期，100%)
│   ├── DV0.5 (项目进度 50%，中间节点)
│   ├── DV0.7 (项目进度 70%)
│   └── DV0.3 (项目进度 30%，早期节点)
│
├── Feature (功能模块)
│   ├── CPU Core (CPU 核心)
│   ├── L2 Cache (二级缓存)
│   ├── DDR Controller (内存控制器)
│   ├── PCIe Controller (PCIe 控制器)
│   ├── GPIO (通用输入输出)
│   ├── Clock Manager (时钟管理)
│   └── Reset Logic (复位逻辑)
│
├── Category (测试类别 - 自定义)
│   ├── Block (模块级)
│   ├── Integration (集成)
│   └── System (系统级)
│
└── Priority (优先级)
    ├── P0 (关键路径)
    ├── P1 (重要)
    └── P2 (一般)
```

---

## 3. 数据规格

### 3.1 Cover Points (目标点)

**总计**: 32 个 CP

| Feature | Sub-Feature | Cover Point | Priority |
|---------|-------------|--------------|----------|
| **CPU Core** | | | |
| | Instruction | 指令覆盖 - R-Type | P0 |
| | Instruction | 指令覆盖 - I-Type | P0 |
| | Instruction | 指令覆盖 - S-Type | P0 |
| | Instruction | 指令覆盖 - U-Type | P1 |
| | Instruction | 指令覆盖 - J-Type | P1 |
| | Instruction | 指令覆盖 - B-Type | P1 |
| | Cache | 缓存一致性协议 | P0 |
| | Cache | L1 缓存命中率 | P1 |
| | Exception | 异常场景覆盖 | P1 |
| | Privilege | 特权模式切换 | P2 |
| **L2 Cache** | | | |
| | Miss Rate | 缓存未命中统计 | P1 |
| | Coherency | 缓存一致性 MESI | P0 |
| | Eviction | 缓存行替换策略 | P2 |
| **DDR Ctrl** | | | |
| | Read | 读事务覆盖 | P0 |
| | Write | 写事务覆盖 | P0 |
| | Timing | 时序约束覆盖 | P1 |
| | Mode | DDR 模式切换 | P2 |
| **PCIe** | | | |
| | Config | 配置空间访问 | P1 |
| | Transaction | 事务层覆盖 | P0 |
| | MSI | MSI 中断传输 | P2 |
| | Power | 功耗状态转换 | P2 |
| **GPIO** | | | |
| | Interrupt | 中断触发 | P1 |
| | Edge | 边沿检测 | P2 |
| | Debounce | 防抖处理 | P2 |
| **Clock** | | | |
| | Gating | 时钟门控 | P1 |
| | Sync | 跨时钟域同步 | P0 |
| | PLL | PLL 锁定时间 | P2 |
| **Reset** | | | |
| | PowerOn | 上电复位序列 | P0 |
| | Watchdog | 看门狗复位 | P1 |
| | SW Reset | 软件复位 | P1 |

### 3.2 Test Cases (测试用例)

**总计**: 52 个 TC

#### 3.2.1 状态分布

| Status | 数量 | 说明 |
|--------|------|------|
| PASS | 20 | 已完成并通过 |
| FAIL | 6 | 执行失败待修复 |
| CODED | 10 | 已编码待执行 |
| OPEN | 16 | 待开发 |

#### 3.2.2 目标日期分布 (按周)

| 周次 | 日期 | PASS | FAIL | CODED | OPEN |
|------|------|------|------|-------|------|
| W01 | 01-06~01-12 | 3 | 1 | 2 | 2 |
| W02 | 01-13~01-19 | 3 | 1 | 2 | 2 |
| W03 | 01-20~01-26 | 3 | 1 | 2 | 2 |
| W04 | 01-27~02-02 | 3 | 1 | 2 | 2 |
| W05 | 02-03~02-09 | 2 | 1 | 1 | 2 |
| W06 | 02-10~02-16 | 2 | 1 | 1 | 2 |
| W07 | 02-17~02-23 | 2 | 0 | 0 | 2 |
| W08 | 02-24~03-02 | 1 | 0 | 0 | 1 |
| W09-W15 | ... | 1 | 0 | 0 | 1 |

#### 3.2.3 TC 命名规范

```
{DV_Milestone}_{Feature}_{Category}_{序号}

示例:
DV1.0_CPU_Block_001    (项目末期，覆盖全部功能)
DV0.5_DDR_Integration_001  (项目中期的集成测试)
DV0.3_PCIe_System_001  (项目早期的系统测试)
```

> **说明**：DV Milestone 表示 TC 计划完成的时间点，与项目进度相关。

### 3.3 TC-CP 关联关系

**规则**:
- 每个 TC 关联 1-3 个 CP
- PASS 状态的 TC 必须有关联的 CP
- 整体覆盖率目标: 60-80%

---

## 4. 工具设计

### 4.1 脚本位置

```
/projects/management/tracker/scripts/create_demo_project.py
```

### 4.2 使用方式

```bash
# 创建示例项目
python3 scripts/create_demo_project.py

# 重新创建（带清理）
python3 scripts/create_demo_project.py --force

# 查看帮助
python3 scripts/create_demo_project.py --help
```

### 4.3 功能清单

| 功能 | 说明 |
|------|------|
| 创建项目 | 在 test_data 目录创建 SOC_DV 项目 |
| 生成 CP | 按设计规格生成 32 个目标点 |
| 生成 TC | 按状态/日期分布生成 52 个用例 |
| 建立关联 | 自动建立 TC-CP 关联关系 |
| 设置日期 | 设置项目起止日期 (15周) |
| 清理旧数据 | --force 时清理旧项目 |
| **生成 Demo 快照** | **生成 project_progress 表数据，模拟项目实际进度** |

### 4.4 代码结构

脚本采用函数式实现，主要函数如下：

```python
# 主函数
def main():
    """入口函数"""
    
# 辅助函数
def get_db_path(project_name):
    """获取项目数据库路径"""
    
def init_db(db_path):
    """初始化数据库（创建表结构）"""
    
def load_projects():
    """加载项目列表"""
    
def save_projects(projects):
    """保存项目列表"""
    
def cleanup():
    """清理旧项目"""
    
def create_project_record(project_id):
    """创建项目记录"""
    
def generate_cover_points(conn, project_id):
    """生成 Cover Points (32个)"""
    
def calculate_target_date(dv_milestone, project_start, project_end):
    """根据 DV Milestone 计算目标日期"""
    
def generate_test_cases(conn, project_id, cp_ids):
    """生成 Test Cases (52个)"""
    
def generate_snapshots(conn, project_id):
    """生成 Demo 快照（模拟项目实际进度）"""
    
def calculate_planned_coverage_from_db(conn, project_start, project_end):
    """从数据库计算计划曲线（与后端算法一致）"""
```

---

## 5. 验收标准

### 5.1 功能验收

- [x] 成功创建 SOC_DV 项目
- [x] 项目包含 32 个 CP
- [x] 项目包含 52 个 TC
- [x] TC 状态分布符合设计
- [x] TC 有合理的目标日期分布
- [x] TC-CP 关联关系正确建立
- [x] 项目起止日期设置正确 (15周)

### 5.2 数据质量

- [x] CP 覆盖主要功能模块
- [x] TC 命名符合规范
- [x] PASS 状态的 TC 都有 CP 关联
- [x] 覆盖率可计算（60-80%）

### 5.3 工具验收

- [x] 可正常执行
- [x] --force 选项正常工作
- [x] 不影响现有数据

### 5.4 Demo 快照验收

- [x] 生成 project_progress 表数据
- [x] 快照数据与计划曲线匹配
- [x] 初期偏离计划（0%→45%）
- [x] 后期加速追赶（45%→75%）

---

## 6. 实施计划

| 任务 | 预估时间 | 优先级 |
|------|----------|--------|
| 脚本开发 | 1.5h | P0 |
| 数据验证 | 0.5h | P1 |
| 文档更新 | 0.5h | P2 |

---

## 7. 相关资源

- 数据库表结构: `cover_point`, `test_case`, `tc_cp_connections`
- 项目列表文件: `data/test_data/projects.json`
- 现有示例: `EX5.db`, `Debugware_65K.db`
- DV Milestone 选项: DV1.0, DV0.3, DV0.5, DV0.7

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.3 | 2026-03-05 | 更新：完成状态，添加 Demo 快照功能，代码结构改为函数式 |
| v1.2 | 2026-03-02 | 更新：DV Milestone 含义说明（与项目进度相关） |
| v1.1 | 2026-03-02 | 更新：DV Milestone使用系统选项，CP 32个，TC 52个，周期15周 |
| v1.0 | 2026-03-02 | 初版规划 |
