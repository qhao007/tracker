# Tracker v0.11.0 版本开发规格书

> **版本**: v0.11.0
> **创建日期**: 2026-03-27
> **状态**: 开发中
> **关联需求**: `/projects/management/feedbacks/reviewed/requirements_analysis_v0.11.0_20260327.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | FC 表结构与 API | P1 | 4h |
| 2 | FC-CP 关联表与 API | P1 | 2h |
| 3 | 项目 coverage_mode 字段 | P1 | 1h |
| 4 | FC Tab 前端页面（筛选/搜索/折叠） | P1 | 6h |
| 5 | FC CSV 导入/导出 | P1 | 2h |
| 6 | FC-CP 关联导入 | P1 | 1h |
| 7 | 导入重名检查改进 | P1 | 1h |
| 8 | 数据库迁移脚本（tracker_ops.py） | P1 | 2h |
| | **总计** | | **~19h** |

### 1.2 背景

FC (Functional Coverage) 是 SV 代码中的 bin 级别覆盖率数据。本次版本新增 Functional Coverage 管理功能，支持：
- 项目级别切换覆盖率模式（TC-CP / FC-CP）
- FC 数据导入导出
- FC-CP 多对多关联

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| FC 表设计与 CRUD API | FC 详情编辑页面 |
| FC-CP 关联表与导入 | FC 批量删除功能 |
| 项目 coverage_mode 切换 | FC 分页 API |
| FC Tab 页面（筛选/搜索/折叠/导入/导出） | TC Tab 页面修改 |
| 导入重名检查改进 | HTTPS 配置 |
| 数据库迁移脚本 | TypeScript CI 集成 |

---

## 2. 数据库修改

### 2.1 表结构变更

#### project 表新增字段

```sql
ALTER TABLE project ADD COLUMN coverage_mode TEXT DEFAULT 'tc_cp';
```

### 2.2 新增表

#### functional_coverage 表

```sql
CREATE TABLE functional_coverage (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    covergroup TEXT NOT NULL,
    coverpoint TEXT NOT NULL,
    coverage_type TEXT NOT NULL,
    bin_name TEXT NOT NULL,
    bin_val TEXT,
    comments TEXT,
    coverage_pct REAL DEFAULT 0.0,
    status TEXT DEFAULT 'missing',
    owner TEXT,
    created_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE (project_id, covergroup, coverpoint, bin_name)
);
```

#### fc_cp_association 表

```sql
CREATE TABLE fc_cp_association (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    cp_id INTEGER,
    fc_id INTEGER,
    created_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE (cp_id, fc_id),
    FOREIGN KEY (cp_id) REFERENCES cover_point(id),
    FOREIGN KEY (fc_id) REFERENCES functional_coverage(id)
);
```

### 2.3 索引设计

```sql
CREATE INDEX idx_fc_covergroup ON functional_coverage(covergroup);
CREATE INDEX idx_fc_coverpoint ON functional_coverage(coverpoint);
CREATE INDEX idx_fc_coverage_type ON functional_coverage(coverage_type);
CREATE INDEX idx_fc_cp_assoc_cp ON fc_cp_association(cp_id);
CREATE INDEX idx_fc_cp_assoc_fc ON fc_cp_association(fc_id);
```

### 2.4 数据迁移脚本

**迁移文件**: `scripts/migrations/v0.11.0_migration.py`

**集成方式**: `python3 scripts/tracker_ops.py migrate [--version v0.11.0]`

---

## 3. API 接口设计

### 3.1 接口列表

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/fc` | 获取 FC 列表（支持筛选） | ⏳ 待实现 |
| POST | `/api/fc/import` | 导入 FC (CSV) | ⏳ 待实现 |
| GET | `/api/fc/export` | 导出 FC (CSV) | ⏳ 待实现 |
| GET | `/api/fc-cp-association` | 获取 FC-CP 关联列表 | ⏳ 待实现 |
| POST | `/api/fc-cp-association` | 创建 FC-CP 关联 | ⏳ 待实现 |
| DELETE | `/api/fc-cp-association` | 删除 FC-CP 关联 | ⏳ 待实现 |
| POST | `/api/fc-cp-association/import` | 导入 FC-CP 关联 (CSV) | ⏳ 待实现 |
| POST | `/api/projects` | 创建项目（新增 coverage_mode） | ⏳ 待实现 |
| GET | `/api/projects/{id}` | 获取项目（返回 coverage_mode） | ⏳ 待实现 |

### 3.2 CSV 格式

#### FC 导入/导出

```
Covergroup,Coverpoint,Type,Bin_Name,Bin_Value,Coverage_Pct,Status,Comments
apb_protocol_cg,cp_addr_range,coverpoint,addr_max,{32'hFFFFFFFC},0.98,ready,CP_048
```

#### FC-CP 关联导入

```
cp_feature,cp_sub_feature,cp_cover_point,fc_covergroup,fc_coverpoint,fc_bin_name
apb_protocol,addr_range,CP_048,apb_protocol_cg,cp_addr_range,addr_max
```

---

## 4. 前端界面设计

### 4.1 页面/组件列表

| 页面/组件 | 功能 | 状态 |
|----------|------|------|
| FC Tab | FC-CP 模式下显示 | ⏳ 待实现 |
| FC 筛选器 | covergroup/coverpoint/coverage_type | ⏳ 待实现 |
| FC 搜索框 | bin_name 模糊搜索 | ⏳ 待实现 |
| FC 折叠/展开 | 两级折叠，默认全部折叠 | ⏳ 待实现 |
| FC 导入弹窗 | 文件选择+预览+结果 | ⏳ 待实现 |
| FC 导出弹窗 | 格式选择+导出 | ⏳ 待实现 |
| 项目创建弹窗 | 新增 coverage_mode 选择 | ⏳ 待实现 |
| CP 详情页 | FC-CP 模式显示关联 FC | ⏳ 待实现 |

### 4.2 FC Tab 显示样式

**默认折叠状态**（按 covergroup 折叠）:
```
┌─ 🔽 apb_protocol_cg (3 coverpoints, 8 bins) ──────────────────┐
│   [+ 展开]                                                     │
└────────────────────────────────────────────────────────────────┘
```

**展开 covergroup**（显示 coverpoint）:
```
┌─ 🔼 apb_protocol_cg ─────────────────────────────────────────┐
│   ├─ 🔽 cp_addr_range (3 bins) ────────────────────────────┐  │
│   │   ├── addr_max        {32'hFFFFFFFC}  coverpoint  0.98  ✅  │
│   │   ├── addr_mid        default         coverpoint  0.85  ✅  │
│   │   └── addr_min        {32'h00000000}  coverpoint  0.92  ✅  │
│   └─ ...                                                       │
└────────────────────────────────────────────────────────────────┘
```

**展开 coverpoint**（显示 bin 列表）:
```
┌─ 🔼 cp_addr_range ──────────────────────────────────────────┐
│   bin_name          bin_val            type        pct   状态 │
│   ─────────────────────────────────────────────────────────  │
│   addr_max          {32'hFFFFFFFC}    coverpoint  0.98  ✅  │
│   addr_mid          default           coverpoint  0.85  ✅  │
└──────────────────────────────────────────────────────────────┘
```

**图例**:

| 符号 | 含义 |
|------|------|
| 🔼 | 已展开 |
| 🔽 | 已折叠 |
| ⏳ | status = missing |
| ✅ | status = ready |
| 0.98 | coverage_pct = 98% |

### 4.3 UI 交互细则

#### 折叠/展开
| 项目 | 规格 |
|------|------|
| 首次加载 | 默认全部折叠 |
| 快捷操作 | 提供"全部展开/全部折叠"按钮 |
| 折叠记忆 | localStorage 记录用户偏好，刷新后保持状态 |

#### 筛选
| 项目 | 规格 |
|------|------|
| UI 形式 | 下拉多选（与 CP/TC 筛选一致） |
| 条件关系 | AND（同时满足所有筛选条件） |
| 触发方式 | 即时筛选（选择后立即生效） |
| 清除操作 | 提供"清除筛选"快捷操作 |

#### 搜索
与 CP/TC 现有搜索方式一致。

#### 导入/导出
与现有 CP 导入导出方式一致。

---

## 5. 验收标准

### 5.1 项目与 coverage_mode

- [ ] 项目创建时可选择 Coverage Mode (TC-CP / FC-CP)
- [ ] 项目创建后 Coverage Mode 不可更改
- [ ] 新建项目默认 TC-CP 模式
- [ ] 已有项目默认 TC-CP 模式

### 5.2 FC Tab

- [ ] FC Tab 仅在 FC-CP 模式显示
- [ ] FC Tab 支持两级折叠/展开（covergroup → coverpoint）
- [ ] FC Tab 默认全部折叠
- [ ] FC Tab 提供"全部展开/全部折叠"按钮
- [ ] FC Tab 支持 covergroup/coverpoint/coverage_type 筛选
- [ ] FC Tab 支持 bin_name 模糊搜索
- [ ] FC Tab 支持 CSV 导入
- [ ] FC Tab 支持 CSV 导出

### 5.3 FC-CP 关联

- [ ] FC-CP 关联表正确创建
- [ ] FC-CP 关联支持 CSV 导入
- [ ] CP 详情页根据 coverage_mode 显示对应关联项

### 5.4 导入重名检查

- [ ] CP 导入使用 `feature + sub_feature + cover_point` 重名检查
- [ ] TC 导入使用 `testbench + test_name` 重名检查
- [ ] 冲突时拒绝导入并显示冲突列表

### 5.5 数据库迁移

- [ ] `tracker_ops.py migrate` 命令正确执行
- [ ] 支持 `--version` 指定迁移版本
- [ ] 迁移后数据库结构正确

---

## 6. 开发计划

### 6.1 开发任务

| 任务 | 状态 | 预计时间 |
|------|------|----------|
| 数据库迁移脚本 | ⏳ 待开发 | 2h |
| 后端 FC API | ⏳ 待开发 | 4h |
| 后端 FC-CP 关联 API | ⏳ 待开发 | 2h |
| 项目 coverage_mode 字段 | ⏳ 待开发 | 1h |
| 前端 FC Tab 页面 | ⏳ 待开发 | 6h |
| FC 导入/导出功能 | ⏳ 待开发 | 2h |
| FC-CP 关联导入 | ⏳ 待开发 | 1h |
| 导入重名检查改进 | ⏳ 待开发 | 1h |
| **小计** | | **15h** |
| **Buffer (20%)** | | **3h** |
| **总计** | | **~19h** |

### 6.2 里程碑

| 里程碑 | 计划日期 | 实际日期 | 状态 |
|--------|----------|----------|------|
| 数据库设计完成 | | | ⏳ 待完成 |
| 后端 API 开发完成 | | | ⏳ 待完成 |
| 前端开发完成 | | | ⏳ 待完成 |
| API 测试完成 | | | ⏳ 待完成 |
| UI 冒烟测试完成 | | | ⏳ 待完成 |
| 发布 | | | ⏳ 待完成 |

---

## 7. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| SQLite 不支持 DROP COLUMN | 低 | 低 | 回滚方案：删除新表，不删除字段 |
| FC 数据量大导致性能问题 | 中 | 中 | 通过折叠减少渲染量，后续迭代加分页 |
| CSV 格式不标准 | 中 | 中 | 完善校验逻辑，提供清晰的错误提示 |

---

## 8. 相关文档

| 文档 | 路径 |
|------|------|
| 需求文档 | `/projects/management/feedbacks/reviewed/requirements_analysis_v0.11.0_20260327.md` |
| 开发规范 | `docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| API 测试策略 | `docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| UI 测试策略 | `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` |

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.11.0 | 2026-03-27 | 初始版本 |

---

**文档创建时间**: 2026-03-27
**创建人**: OpenClaw
