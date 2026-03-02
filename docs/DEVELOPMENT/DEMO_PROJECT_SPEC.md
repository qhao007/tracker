# 测试数据生成工具 - Demo Project Generator

> **版本**: v1.0 | **创建日期**: 2026-03-02 | **状态**: 规划中

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
| 结束日期 | 2026-06-26 (26周后周五) |

### 2.3 数据层级结构

```
SOC_DV 项目 (26 周周期)
│
├── DV Milestone (验证里程碑)
│   ├── RTL_Freeze (RTL 冻结)
│   ├── DA (Design Achievement)
│   ├── SI (Sign-off Integration)
│   └── MA (Mass Production)
│
├── Feature (功能模块)
│   ├── CPU Core (CPU 核心)
│   ├── L2 Cache (二级缓存)
│   ├── DDR Controller (内存控制器)
│   ├── PCIe Controller (PCIe 控制器)
│   ├── GPIO (通用输入输出)
│   └── Clock Manager (时钟管理)
│
├── Category (测试类别)
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

**总计**: 15-20 个 CP

| Feature | Sub-Feature | Cover Point | Priority |
|---------|-------------|--------------|-----------|
| **CPU Core** | | | |
| | Instruction | 指令覆盖 - R-Type | P0 |
| | Instruction | 指令覆盖 - I-Type | P0 |
| | Instruction | 指令覆盖 - Load/Store | P0 |
| | Cache | 缓存一致性协议 | P0 |
| | Exception | 异常场景覆盖 | P1 |
| **L2 Cache** | | | |
| | Miss Rate | 缓存未命中统计 | P1 |
| | Coherency | 缓存一致性 | P0 |
| **DDR Ctrl** | | | |
| | Read | 读事务覆盖 | P0 |
| | Write | 写事务覆盖 | P0 |
| | Timing | 时序约束覆盖 | P1 |
| **PCIe** | | | |
| | Config | 配置空间访问 | P1 |
| | Transaction | 事务层覆盖 | P0 |
| | Power | 功耗状态转换 | P2 |
| **GPIO** | | | |
| | Interrupt | 中断触发 | P1 |
| | Edge | 边沿检测 | P2 |
| **Clock** | | | |
| | Gating | 时钟门控 | P1 |
| | Sync | 跨时钟域同步 | P0 |

### 3.2 Test Cases (测试用例)

**总计**: 25-30 个 TC

#### 3.2.1 状态分布

| Status | 数量 | 说明 |
|--------|------|------|
| PASS | 10 | 已完成并通过 |
| FAIL | 3 | 执行失败待修复 |
| CODED | 5 | 已编码待执行 |
| OPEN | 8 | 待开发 |

#### 3.2.2 目标日期分布 (按周)

| 周次 | 日期 | PASS | FAIL | CODED | OPEN |
|------|------|------|------|-------|------|
| W01 | 01-06~01-12 | 2 | 0 | 1 | 1 |
| W02 | 01-13~01-19 | 2 | 1 | 1 | 1 |
| W03 | 01-20~01-26 | 2 | 1 | 1 | 1 |
| W04 | 01-27~02-02 | 2 | 0 | 1 | 2 |
| W05 | 02-03~02-09 | 1 | 1 | 1 | 2 |
| W06-W10 | ... | 1 | 0 | 0 | 4 |

#### 3.2.3 TC 命名规范

```
{DV_Milestone}_{Feature}_{Category}_{序号}

示例:
RTL_Freeze_CPU_Block_001
DA_DDR_Ctrl_Integration_001
SI_PCIe_System_001
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
| 生成 CP | 按设计规格生成 15+ 个目标点 |
| 生成 TC | 按状态/日期分布生成 25+ 个用例 |
| 建立关联 | 自动建立 TC-CP 关联关系 |
| 设置日期 | 设置项目起止日期 |
| 清理旧数据 | --force 时清理旧项目 |

### 4.4 代码结构

```python
class DemoProjectGenerator:
    def __init__(self, data_dir):
        self.data_dir = data_dir
    
    def create_project(self, name="SOC_DV"):
        """创建项目"""
        
    def generate_cover_points(self, project_id):
        """生成 Cover Points"""
        
    def generate_test_cases(self, project_id):
        """生成 Test Cases"""
        
    def create_connections(self, project_id):
        """建立 TC-CP 关联"""
        
    def set_project_dates(self, project_id):
        """设置项目日期"""
        
    def cleanup(self, name="SOC_DV"):
        """清理旧项目"""
```

---

## 5. 验收标准

### 5.1 功能验收

- [ ] 成功创建 SOC_DV 项目
- [ ] 项目包含 15+ 个 CP
- [ ] 项目包含 25+ 个 TC
- [ ] TC 状态分布符合设计
- [ ] TC 有合理的目标日期分布
- [ ] TC-CP 关联关系正确建立
- [ ] 项目起止日期设置正确

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
| 脚本开发 | 1h | P0 |
| 数据验证 | 0.5h | P1 |
| 文档更新 | 0.5h | P2 |

---

## 7. 相关资源

- 数据库表结构: `cover_point`, `test_case`, `tc_cp_connections`
- 项目列表文件: `data/test_data/projects.json`
- 现有示例: `EX5.db`, `Debugware_65K.db`

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-03-02 | 初版规划 |
