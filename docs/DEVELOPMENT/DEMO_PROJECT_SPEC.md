# 测试数据生成工具 - Demo Project Generator

> **版本**: v1.1 | **创建日期**: 2026-03-02 | **状态**: 规划中

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

### 2.3 数据层级结构

```
SOC_DV 项目 (15 周周期)
│
├── DV Milestone (验证里程碑 - 使用系统选项)
│   ├── DV1.0 (默认)
│   ├── DV0.3
│   ├── DV0.5
│   └── DV0.7
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
DV1.0_CPU_Block_001
DV0.5_DDR_Integration_001
DV0.3_PCIe_System_001
```

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

### 4.4 代码结构

```python
class DemoProjectGenerator:
    def __init__(self, data_dir):
        self.data_dir = data_dir
    
    def create_project(self, name="SOC_DV"):
        """创建项目"""
        
    def generate_cover_points(self, project_id):
        """生成 Cover Points (32个)"""
        
    def generate_test_cases(self, project_id):
        """生成 Test Cases (52个)"""
        
    def create_connections(self, project_id):
        """建立 TC-CP 关联"""
        
    def set_project_dates(self, project_id):
        """设置项目日期 (15周)"""
        
    def cleanup(self, name="SOC_DV"):
        """清理旧项目"""
```

---

## 5. 验收标准

### 5.1 功能验收

- [ ] 成功创建 SOC_DV 项目
- [ ] 项目包含 32 个 CP
- [ ] 项目包含 52 个 TC
- [ ] TC 状态分布符合设计
- [ ] TC 有合理的目标日期分布
- [ ] TC-CP 关联关系正确建立
- [ ] 项目起止日期设置正确 (15周)

### 5.2 数据质量

- [ ] CP 覆盖主要功能模块
- [ ] TC 命名符合规范
- [ ] PASS 状态的 TC 都有 CP 关联
- [ ] 覆盖率可计算（60-80%）

### 5.3 工具验收

- [ ] 可正常执行
- [ ] --force 选项正常工作
- [ ] 不影响现有数据

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
| v1.1 | 2026-03-02 | 更新：DV Milestone使用系统选项，CP 32个，TC 52个，周期15周 |
| v1.0 | 2026-03-02 | 初版规划 |
