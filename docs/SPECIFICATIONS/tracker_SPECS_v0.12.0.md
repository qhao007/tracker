# Tracker v0.12.0 版本开发规格书

> **版本**: v0.12.0 [Phase 5]
> **创建日期**: 2026-04-07
> **状态**: 开发中
> **关联需求**: `/projects/management/feedbacks/reviewed/REQ_DASHBOARD_ENHANCEMENT_v1.0.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | Dashboard Tab 重构 | P1 | 2h |
| 2 | 覆盖率空洞看板 | P1 | 4h |
| 3 | TC Owner 分布 | P1 | 5h |
| 4 | Feature × Priority 覆盖率矩阵 | P2 | 4h |
| 5 | 快照 CP + TC 状态信息 | P1 | 3h |
| 6 | FC 页面 Group 覆盖率显示 | P2 | 2h |
| | **总计** | | **~20h** |

### 1.2 背景

当前 Dashboard (v0.11.0) 存在以下问题：
- 概览卡片与 Feature/Priority 分布、趋势图存在数据重叠
- Top 5 未覆盖 CP 价值有限，无法区分"未关联 TC"和"覆盖策略问题"
- 缺乏对 TC Owner 工作量的可视化
- 缺乏 Feature × Priority 二维覆盖率视角
- 快照缺少 TC/CP 详细状态，无法支持未来分析

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| Dashboard 4 Tab 结构（概览/空洞/Owner/矩阵） | Recent Activity 页面重构（移至页面底部） |
| 覆盖率空洞看板 | TC-CP 关联热力图（未来功能） |
| TC Owner 分布统计 | 周报生成（未来功能） |
| Feature × Priority 覆盖率矩阵 | TC 效率指标趋势图（未来功能） |
| 快照增强（CP + TC 状态） | 快照历史趋势分析（未来功能） |
| FC Group 覆盖率显示 | FC 页面其他增强 |

---

## 2. 组件变更

### 2.1 去除组件

| # | 组件 | 去除理由 |
|---|------|----------|
| 1 | 总 CP 卡片 | 覆盖率矩阵中有总数，无需单独展示 |
| 2 | 覆盖率卡片 | 趋势图里已有数字 |
| 3 | Feature 分布图 | 被 Feature × Priority 矩阵替代 |
| 4 | Priority 分布卡 | 被 Feature × Priority 矩阵替代 |
| 5 | Top 5 未覆盖 | 被空洞看板替代 |
| 6 | Recent Activity | 从概览页移除，移至页面底部 |

### 2.2 保留组件

| # | 组件 |
|---|------|
| 1 | 趋势折线图 |
| 2 | 已覆盖卡片（增加周环比） |
| 3 | 未关联卡片（增加周环比） |

### 2.3 新增组件

| # | 组件 | 位置 |
|---|------|------|
| 1 | TC 通过率卡片 | 概览页 |
| 2 | 覆盖率空洞看板 | Tab 2 |
| 3 | TC Owner 分布 | Tab 3 |
| 4 | Feature × Priority 矩阵 | Tab 4 |
| 5 | 矩阵预览 | 概览页 |
| 6 | 空洞摘要 | 概览页 |
| 7 | Owner 摘要 | 概览页 |

---

## 3. Dashboard 布局

### 3.1 Tab 结构

| Tab | 内容 |
|-----|------|
| 概览 | 数字卡片 + 矩阵预览 + 趋势图 + 空洞/Owner 摘要 |
| 覆盖率矩阵 | Feature × Priority 完整热力图 |
| Owner 分布 | Owner 表格 + 通过率 |
| 覆盖空洞 | 空洞看板完整版（按 mode 区分逻辑） |

### 3.2 概览页布局

```
┌─────────────────────────────────────────────────────────────────┐
│  ┌───────────┐  ┌───────────┐  ┌───────────┐                   │
│  │ 已覆盖     │  │ 未关联    │  │ TC通过率  │                   │
│  │ 25/30    │  │   1       │  │   38.5%  │                   │
│  │   ↑+8    │  │   --      │  │   ↑+3%   │                   │
│  └───────────┘  └───────────┘  └───────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  矩阵预览 (Top 4 Features)  [查看完整 →]                        │
├─────────────────────────────────────────────────────────────────┤
│  覆盖率趋势图 (7天)                                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐                          │
│  │ 空洞摘要      │  │ Owner摘要     │                          │
│  │ Top 5 严重   │  │ Top 3        │                          │
│  └───────────────┘  └───────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Tab 2：覆盖率矩阵

**颜色映射**：

| 覆盖率范围 | 颜色 | 状态 |
|------------|------|------|
| >= 80% | #22c55e 绿色 | ✅ 达标 |
| 50% - 79% | #f59e0b 橙色 | ⚠️ 关注 |
| 20% - 49% | #ef4444 红色 | 🔴 预警 |
| < 20% | #991b1b 深红 | 🔴🔴 严重 |

**告警阈值**：

| 等级 | 条件 |
|------|------|
| 薄弱区域 | 覆盖率 < 50% |
| 严重薄弱 | 覆盖率 < 20% |

**预览版（概览页）**：
- 只显示 Top 4 Features（按 CP 总数排序）
- 右侧显示薄弱区域告警

### 3.4 Tab 3：Owner 分布

**通过率颜色规则**：

| 通过率范围 | 颜色 | 状态 |
|------------|------|------|
| >= 90% | #22c55e 绿色 | ✅ 优秀 |
| 70% - 89% | #f59e0b 橙色 | ⚠️ 正常 |
| < 70% | #ef4444 红色 | 🔴 预警 |

**Owner 详情弹窗**：
- TC 列表限制显示 20 条
- 超过显示"[查看全部 N 个 TC →]"链接

### 3.5 Tab 4：覆盖空洞看板

**空洞分析需区分 coverage_mode**：

#### tc-cp 模式

**空洞定义**：

| 条件 | 说明 |
|------|------|
| ① 已关联 TC | `linked_tcs >= 1` |
| ② 覆盖率为 0 | `coverage_rate = 0`（所有关联 TC 都未 PASS）|

**空洞等级**：

| 等级 | 条件 | 排序 |
|------|------|------|
| 🔴 严重 | P0 + coverage=0% | 先 priority 降序，再 linked_tcs 降序 |
| 🟡 警告 | P1 + coverage=0% | 先 priority 降序，再 linked_tcs 降序 |
| 🟡 关注 | P2 + coverage=0% | 先 priority 降序，再 linked_tcs 降序 |

**说明**：tc-cp 模式下，同一 CP 关联的 TC 不可能同时满足"覆盖率=0"和"至少一个 PASS"。因此简化判断逻辑。

#### fc-cp 模式（简化版）

**空洞定义**：

| 条件 | 说明 |
|------|------|
| ① 已关联 FC | `linked_fcs >= 1` |
| ② 覆盖率很低 | `coverage_rate < 25%` |

**空洞等级**：

| 等级 | 条件 | 排序 |
|------|------|------|
| 🔴 严重 | coverage_rate = 0% | 先 priority 降序，再 coverage_rate 升序，再 linked_fcs 降序 |
| 🟡 警告 | 0% < coverage_rate < 15% | 先 priority 降序，再 coverage_rate 升序，再 linked_fcs 降序 |
| 🟡 关注 | 15% <= coverage_rate < 25% | 先 priority 降序，再 coverage_rate 升序，再 linked_fcs 降序 |

**说明**：fc-cp 模式下，TC 和 CP 是隐式关联。简化算法直接使用 FC 的 coverage_pct 作为 CP 的覆盖率指标，筛选覆盖率很低的 CP 作为空洞。

#### 通用规则

- 每类等级最多显示 20 条
- 未关联 TC/FC 的 CP（unlinked）不计入空洞
- 概览页 Top 5 只显示 `critical` 等级的前 5 条

**API 返回结构**：

```json
{
  "success": true,
  "data": {
    "mode": "tc_cp",
    "critical": [...],
    "warning": [...],
    "attention": [...],
    "total_critical": 5,
    "total_warning": 10,
    "total_attention": 15
  }
}
```

---

## 4. 快照增强

### 4.1 快照数据结构变更

**新增字段**：

```json
{
  "snapshot_date": "2026-04-07",
  "coverage_rate": 67.5,
  "cp_summary": { "total": 156, "covered": 89 },
  "cp_states": {
    "1": { "name": "AXI_TIMEOUT", "coverage_rate": 85, "linked_tcs": 3 },
    "2": { "name": "BURST_ALIGN", "coverage_rate": 0, "linked_tcs": 2 }
  },
  "tc_summary": {
    "total": 156,
    "pass": 138,
    "fail": 12,
    "not_run": 6,
    "pass_rate": 88.5
  },
  "tc_states": {
    "1": "PASS",
    "2": "FAIL",
    "3": "NOT_RUN"
  }
}
```

**Key 设计**：使用数字 ID 作为 key，便于 name 变化时快照数据仍可访问。

### 4.2 向后兼容

| 情况 | 处理 |
|------|------|
| 旧快照（`cp_states` 为 null） | 前端显示"--"，不显示依赖功能 |
| 新快照 | 正常显示 |

### 4.3 存储估算

**计算公式**：
```
单条 CP 状态 ≈ {
  "id": "1",              // 数字 → ~3 bytes
  "name": "AXI_TIMEOUT",  // 字符串 → ~12 bytes
  "coverage_rate": 85.5,   // 浮点数 → ~4 bytes
  "linked_tcs": 3         // 整数 → ~2 bytes
} ≈ 21 bytes (原始)

JSON 序列化后 ≈ 80 bytes/CP
156 CP × 80 bytes ≈ 12.5 KB

单条 TC 状态 ≈ {
  "id": "1",              // ~3 bytes
  "status": "PASS"       // ~6 bytes
} ≈ 9 bytes (原始)

JSON 序列化后 ≈ 35 bytes/TC
156 TC × 35 bytes ≈ 5.5 KB

考虑 JSON overhead 和冗余字段 × 1.5 系数:
CP states ≈ 8 KB/快照
TC states ≈ 3 KB/快照
```

| 数据 | 单次快照 | 1 年 (52 次) | 5 年 |
|------|----------|--------------|------|
| CP states (156 个) | ~8KB | ~400KB | ~2MB |
| TC states (156 个) | ~3KB | ~150KB | ~750KB |
| **合计** | ~11KB | ~550KB | ~2.75MB |

**存储方式**：所有状态存储在快照行的 JSON 列中，保持 1 行/快照的结构。

### 4.4 未来应用场景

| 场景 | 说明 |
|------|------|
| CP 覆盖历史分析 | 哪些 CP 长期停滞（空洞检测前置化） |
| TC 通过率趋势图 | Dashboard 展示 TC 每周通过率变化 |
| 周报生成 | 自动引用 TC/CP 统计数据 |
| Owner 效率分析 | 结合历史数据分析 Owner 工作质量 |
| TC-CP 关联分析 | 如需实现热力图，需要此数据作为基础 |

---

## 5. FC 页面增强

### 5.1 Group 覆盖率显示

每个 Cover Group 行显示组覆盖率：

```
┌─────────────────────────────────────────────────────────────────┐
│  ▼ AXI_CG (Cover Group)                              52% ████ │
│    ├── CP-001: AXI_WRITE_VALID     [████████████] 85%         │
│    ├── CP-002: AXI_READ_VALID      [███████░░░] 72%         │
│    └── CP-003: AXI_BURST_ALIGN     [░░░░░░░░░░]  0%         │
└─────────────────────────────────────────────────────────────────┘
```

**计算公式**：
```
Group 覆盖率 = Σ(每个 CP 的覆盖率) / CP 总数
```

**说明**：使用简单算术平均（受数据模型限制，`cover_point` 无 bins 数量字段）。

**语义对比**：

| 方法 | 公式 | 语义正确性 |
|------|------|------------|
| 简单平均（当前） | Σ(rate_i) / N | ⚠️ 假设每个 CP bins 数量相近 |
| 加权平均（理想） | Σ(covered_bins_i) / Σ(total_bins_i) | ✅ 语义正确 |

**未来扩展**：如需精确的 Group 覆盖率，需要扩展 `cover_point` 表添加 `total_bins` 和 `covered_bins` 字段。

---

## 6. 周环比变化计算

### 6.1 计算规则

| 情况 | 计算方式 |
|------|----------|
| 本周已有快照 | 本周数值 - 上周数值 |
| 本周尚无快照 | 上周数值 - 上上周数值 |
| 仅有一周数据 | 显示"--" |
| 无快照数据 | 显示"--" |

### 6.2 前端代码

```javascript
function getChangeValue(currentSnapshot, allSnapshots) {
  if (allSnapshots.length < 2) return null;
  const sorted = allSnapshots.sort((a, b) => b.date - a.date);
  const latestIndex = sorted.findIndex(s => s.date === currentSnapshot.date);
  
  if (latestIndex === 0 && sorted.length >= 2) {
    return sorted[0].value - sorted[1].value;
  } else if (latestIndex > 0) {
    return sorted[latestIndex].value - sorted[latestIndex + 1].value;
  }
  return null;
}
```

---

## 7. API 设计

### 7.1 新增端点

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/dashboard/stats` | 概览统计数据（复用） |
| GET | `/api/dashboard/coverage-holes` | 覆盖空洞数据 |
| GET | `/api/dashboard/owner-stats` | Owner 统计数据 |
| GET | `/api/dashboard/coverage-matrix` | Feature×Priority 矩阵 |

### 7.2 API 响应格式

#### GET /api/dashboard/coverage-holes

```json
{
  "success": true,
  "data": {
    "critical": [
      {
        "cp_id": 45,
        "cp_name": "AXI_TIMEOUT_ERR",
        "feature": "AXI",
        "priority": "P0",
        "coverage_rate": 0,
        "linked_tcs": [
          {"tc_id": 101, "tc_name": "AXI Timeout Test", "status": "PASS"},
          {"tc_id": 205, "tc_name": "AXI Edge Case", "status": "PASS"},
          {"tc_id": 308, "tc_name": "AXI Stress Test", "status": "FAIL"}
        ]
      }
    ],
    "warning": [...],
    "attention": [...]
  }
}
```

#### GET /api/dashboard/owner-stats

**设计原则**：API 返回原始计数，前端计算百分比。

```json
{
  "success": true,
  "data": {
    "owners": [
      {
        "owner": "@zhangsan",
        "tc_total": 45,
        "tc_pass": 41,
        "tc_fail": 3,
        "tc_not_run": 1
      }
    ],
    "summary": {
      "total_owners": 5,
      "unassigned_tc_count": 21
    }
  }
}
```

#### GET /api/dashboard/coverage-matrix

**设计原则**：API 返回原始计数，前端计算百分比。

```json
{
  "success": true,
  "data": {
    "matrix": {
      "AXI": {
        "P0": {"covered": 17, "total": 20, "cp_ids": [1, 5, 12]},
        "P1": {"covered": 18, "total": 25, "cp_ids": [2, 6, 13]}
      }
    },
    "features": ["AXI", "SRAM", "CPU", "MEM"],
    "priorities": ["P0", "P1", "P2", "P3"],
    "weak_areas": [
      {"feature": "SRAM", "priority": "P3", "covered": 0, "total": 5, "severity": "critical"},
      {"feature": "MEM", "priority": "P3", "covered": 2, "total": 7, "severity": "warning"}
    ]
  }
}
```

---

## 8. 数据库设计

### 8.1 tc_cp_connections 表（已存在）

```sql
CREATE TABLE tc_cp_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tc_id INTEGER,
    cp_id INTEGER,
    UNIQUE(tc_id, cp_id)
);
```

### 8.2 project_progress 表变更

**新增字段**：在 `progress_data` JSON 列中存储 `cp_states` 和 `tc_states`。

**查询逻辑**：
```python
# 快照保存时序列化
progress_data = json.dumps({
    "cp_summary": {...},
    "cp_states": {...},  # 新增
    "tc_summary": {...},  # 新增
    "tc_states": {...}   # 新增
})

# 快照读取时反序列化
data = json.loads(row['progress_data'])
cp_states = data.get('cp_states', {})
```

---

## 9. 验收标准

### 9.1 Dashboard 功能验收

- [ ] Tab 切换正常，无白屏
- [ ] 概览页去除组件已移除
- [ ] 空洞识别正确（满足条件的 CP 被识别）
- [ ] 空洞分级正确（严重/警告/关注三级）
- [ ] 空洞详情弹窗显示关联 TC 列表
- [ ] Owner 统计正确（TC 数量和通过率）
- [ ] Owner 详情弹窗显示 TC 列表（限制 20 条）
- [ ] 矩阵正确渲染（Feature × Priority）
- [ ] 矩阵颜色根据阈值正确显示
- [ ] 矩阵单元格点击显示 CP 列表

### 9.2 FC 页面验收

- [ ] 每个 Cover Group 行显示组覆盖率
- [ ] Group 覆盖率 = CP 覆盖率平均值
- [ ] 颜色根据阈值正确显示

### 9.3 快照功能验收

- [ ] 快照包含 `tc_summary` 数据
- [ ] 快照包含 `cp_states` 数据
- [ ] 旧快照兼容（`cp_states` 为 null 时正常）
- [ ] `tc_summary.pass + tc_summary.fail + tc_summary.not_run = tc_summary.total`
- [ ] `coverage_rate = Σ(cp_states[].coverage_rate) / len(cp_states)`
- [ ] `cp_states[id].linked_tcs = COUNT(tc_cp_connections WHERE cp_id = id)`

### 9.4 性能验收

| 指标 | 阈值 |
|------|------|
| Dashboard 页面加载 | <2s |
| Tab 切换响应 | <500ms |
| API 响应时间 | <500ms |
| 快照创建时间 | <3s |

### 9.5 空数据场景验收

- [ ] 无 CP 数据时，矩阵/空洞 Tab 显示"暂无 Cover Point 数据"
- [ ] 无 TC 数据时，Owner 分布 Tab 显示"暂无 TC 数据"
- [ ] 无空洞数据时，覆盖空洞 Tab 显示"当前无覆盖空洞"
- [ ] 无快照数据时，周环比显示"--"

### 9.6 UI 交互验收

- [ ] Tab 切换有过渡动画
- [ ] 弹窗可点击遮罩关闭
- [ ] 弹窗可按 ESC 键关闭
- [ ] Tab 内容加载中显示 skeleton 或 spinner
- [ ] 详情弹窗支持刷新数据

---

## 10. 里程碑

| 里程碑 | 计划日期 | 状态 |
|--------|----------|------|
| 数据库设计完成 | +0.5 天 | ⏳ |
| API 开发完成 | +1.5 天 | ⏳ |
| 前端开发完成 | +2 天 | ⏳ |
| 测试完成 | +2.5 天 | ⏳ |
| 发布 | +2.5 天 | ⏳ |

---

## 11. 相关文档

| 文档 | 路径 |
|------|------|
| 需求文档 | `/projects/management/feedbacks/reviewed/REQ_DASHBOARD_ENHANCEMENT_v1.0.md` |
| 开发规范 | `/projects/management/tracker/docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| API 测试策略 | `/projects/management/tracker/docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| UI 测试策略 | `/projects/management/tracker/docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` |

---

## 12. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.12.0 | 2026-04-07 | 初始版本 |

---

**文档创建时间**: 2026-04-07
**创建人**: OpenClaw
