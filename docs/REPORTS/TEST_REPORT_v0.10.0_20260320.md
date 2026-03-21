# Tracker v0.10.0 测试报告 (REQ-2.2 补充)

> **测试版本**: v0.10.0 | **日期**: 2026-03-20 | **状态**: ✅ REQ-2.2 开发完成 + BUG-093 已修复

---

## 1. 测试概览

### 1.1 本次测试范围

本次测试针对 **REQ-2.2: 实际曲线 Priority 过滤** 功能，包含：
- 后端 API 开发
- 数据库表扩展
- API 测试
- UI 测试

### 1.2 测试环境

| 项目 | 值 |
|------|-----|
| 测试服务器 | http://localhost:8081 |
| 测试框架 | pytest + Playwright |
| 测试日期 | 2026-03-20 |
| 测试数据库 | SOC_DV (project_id=3) |

---

## 2. 开发内容

### 2.1 后端修改

| 文件 | 修改内容 |
|------|----------|
| `api.py` | 扩展 `project_progress` 表，添加 p0~p3_coverage 字段 |
| `api.py` | 修改 `calculate_current_coverage()` 计算各 Priority 覆盖率 |
| `api.py` | 修改 `get_progress()` 根据 priority 参数返回对应覆盖率 |
| `api.py` | 修改 `create_snapshot()` 存储各 Priority 覆盖率 |

### 2.2 数据库变更

```sql
ALTER TABLE project_progress ADD COLUMN p0_coverage REAL;
ALTER TABLE project_progress ADD COLUMN p1_coverage REAL;
ALTER TABLE project_progress ADD COLUMN p2_coverage REAL;
ALTER TABLE project_progress ADD COLUMN p3_coverage REAL;
```

### 2.3 API 行为

| 请求 | 返回数据源 |
|------|-----------|
| `/api/progress/3` | `actual_coverage` (总体覆盖率) |
| `/api/progress/3?priority=P0` | `p0_coverage` |
| `/api/progress/3?priority=P1` | `p1_coverage` |

---

## 3. API 测试结果

### 3.1 测试文件

| 文件 | 路径 |
|------|------|
| test_api_progress.py | dev/tests/test_api/ |

### 3.2 测试结果汇总

| 测试组 | 总数 | 通过 | 失败 | 通过率 |
|--------|------|------|------|--------|
| Priority 过滤 (计划曲线) | 9 | 9 | 0 | **100%** |
| 实际曲线 Priority 过滤 | 5 | 5 | 0 | **100%** |
| **总计** | **14** | **14** | **0** | **100%** |

### 3.3 新增测试用例 (API-PROG-010 ~ API-PROG-014)

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| API-PROG-010 | 实际曲线单Priority过滤 | ✅ 通过 |
| API-PROG-011 | 实际曲线多Priority过滤 | ✅ 通过 |
| API-PROG-012 | 实际曲线无过滤 | ✅ 通过 |
| API-PROG-013 | 实际曲线覆盖率存储验证 | ✅ 通过 |
| API-PROG-014 | 实际曲线覆盖率计算验证 | ✅ 通过 |

---

## 4. UI 测试结果

### 4.1 测试文件

| 文件 | 路径 |
|------|------|
| cp_link_filter.spec.ts | dev/tests/test_ui/specs/integration/ |

### 4.2 测试结果汇总

| 测试组 | 总数 | 通过 | 失败 | 通过率 |
|--------|------|------|------|--------|
| UI-LINK (关联选择) | 7 | 7 | 0 | **100%** |
| UI-PRIO (Priority过滤) | 10 | 10 | 0 | **100%** |
| **总计** | **17** | **17** | **0** | **100%** |

### 4.3 新增 UI 测试用例 (UI-PRIO-007 ~ UI-PRIO-010)

| 用例 ID | 说明 | 结果 |
|---------|------|------|
| UI-PRIO-007 | 实际曲线单Priority过滤 | ✅ 通过 |
| UI-PRIO-008 | 实际曲线多Priority过滤 | ✅ 通过 |
| UI-PRIO-009 | 实际曲线无过滤 | ✅ 通过 |
| UI-PRIO-010 | 计划曲线vs实际曲线对比 | ✅ 通过 |

---

## 5. 代码审查问题修复

### 5.1 发现的问题

| 问题 | 严重性 | 状态 |
|------|--------|------|
| 多值 Priority 过滤只使用第一个 | 高 | 已记录 |
| SQL 注入防护 | 高 | ✅ 已修复 |
| fetchone vs fetchall 误用 | 高 | ✅ 已修复 |

### 5.2 SQL 注入防护修复

**修复前**：
```python
coverage_column = f'{first_priority}_coverage'
```

**修复后**：
```python
ALLOWED_COVERAGE_COLUMNS = {'actual_coverage', 'p0_coverage', 'p1_coverage', 'p2_coverage', 'p3_coverage'}
if candidate_column in ALLOWED_COVERAGE_COLUMNS:
    coverage_column = candidate_column
```

### 5.3 fetchone vs fetchall 修复

**修复前**：
```python
result = cursor.fetchone()
covered_cps = result[0] if result else 0
```

**修复后**：
```python
results = cursor.fetchall()
covered_cps = len(results) if results else 0
```

---

## 6. Bug 修复记录

### 6.1 BUG-093: Priority 多值过滤时实际曲线覆盖率计算错误

| 属性 | 值 |
|------|-----|
| **严重性** | High |
| **状态** | ✅ 已修复 |
| **发现日期** | 2026-03-20 |
| **修复日期** | 2026-03-20 |

**问题**：选择 P0+P1+P2 过滤时，实际曲线覆盖率应该与无过滤时相同（因为 P0+P1+P2 覆盖了全部 CP），但当时返回的是第一个 Priority (P0) 的覆盖率。

**修复方案**：
- 当 priority 参数覆盖了**全部 CP** 时，使用 `actual_coverage`
- 当只覆盖**部分 CP** 时，计算加权平均覆盖率

**验证结果**：
| 过滤条件 | actual 覆盖率 | 说明 |
|----------|---------------|------|
| 无过滤 | **72.0%** | actual_coverage |
| P0+P1+P2 | **72.0%** | ✅ 与无过滤相同（覆盖全部 CP） |
| P0+P1 | 80.3% | ✅ 加权平均 |
| P0 | 97.0% | p0_coverage |

---

## 7. 手工验证结果

### 7.1 API 数据对比 (2026-03-20 更新)

| 过滤条件 | actual 覆盖率 | 数据源 | 验证结果 |
|----------|---------------|--------|----------|
| 无过滤 | 72.0% | actual_coverage | ✅ |
| P0 | 97.0% | p0_coverage | ✅ |
| P1 | 80.0% | p1_coverage | ✅ |
| P2 | 60.0% | p2_coverage | ✅ |
| P0+P1 | 80.3% | 加权平均 | ✅ |
| P0+P1+P2 | 72.0% | actual_coverage | ✅ (覆盖全部 CP) |
| P0+P1+P3 | 80.3% | 加权平均 | ✅ |

### 7.2 快照数据 (SOC_DV)

```
日期        actual  p0     p1     p2     p3
2026-03-09  56%    91%    62%    48%    0%
2026-03-16  69%    94%    72%    56%    0%
2026-03-23  72%    97%    80%    60%    0%
```

---

## 8. 验收标准

| 验收项 | 状态 | 说明 |
|--------|------|------|
| API 支持 priority 参数 | ✅ | 已验证 |
| 实际曲线数据根据过滤变化 | ✅ | 已验证 |
| P0+P1+P2 = 无过滤 | ✅ | 72.0% = 72.0% |
| 多值 Priority 加权平均 | ✅ | P0+P1 = 80.3% |
| API 测试 100% 通过 | ✅ | 14/14 |
| UI 测试 100% 通过 | ✅ | 17/17 |
| SQL 注入防护 | ✅ | 已修复 |
| BUG-093 已修复 | ✅ | 多值 Priority 计算正确 |

---

## 9. 测试文件

| 文件 | 用例数 | 结果 |
|------|--------|------|
| test_api_progress.py | 14 | ✅ 全部通过 |
| cp_link_filter.spec.ts | 17 | ✅ 全部通过 |

---

**报告生成时间**: 2026-03-20 (更新)
**署名**: Claude Code
