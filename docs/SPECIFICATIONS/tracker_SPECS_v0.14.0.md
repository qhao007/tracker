# Tracker v0.14.0 版本开发规格书

> **版本**: v0.14.0
> **创建日期**: 2026-05-12
> **状态**: 待开发
> **关联需求**: `/projects/management/feedbacks/reviewed/requirements_analysis_EXPORT_PACKAGE_v0.14.0_20260512.md`

---

## 1. 概述

### 1.1 功能列表

| # | 功能 | 优先级 | 预估时间 |
|---|------|--------|----------|
| 1 | 项目概览导出 | P0 | 1h |
| 2 | 覆盖率数据导出 | P0 | 1h |
| 3 | TC/CP 统计导出 | P0 | 1h |
| 4 | Dashboard 数据导出 | P1 | 2h |
| 5 | Feature 列表导出 | P1 | 1h |
| 6 | 快照历史导出 | P2 | 1h |
| 7 | Wiki 内容导出 | P2 | 1h |
| 8 | ZIP 打包下载 | P0 | 1h |
| 9 | 权限控制 | P0 | 0.5h |
| 10 | API 支持 | P1 | 1h |
| | **总计** | | **~10.5h** |

### 1.2 背景

Tracker 目前是纯数据管理工具，用户需要手动从系统中提取数据来制作项目汇报PPT。这个过程耗时且容易出错。

**目标**：提供一键导出项目材料包的功能，包含所有必要的信息（md文档、Excel表格等），便于快速生成项目汇报材料。

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 项目概览（含 coverage_mode 配置） | PPT 文件生成 |
| 覆盖率数据及趋势（完整历史） | 邮件自动发送 |
| TC/CP 统计（状态分布、通过率） | 移动端适配 |
| Dashboard 数据（Feature×Priority矩阵、Owner分布、Coverage Matrix） | Wiki 内容在线编辑 |
| Feature 列表（统计汇总） | 多项目同时导出 |
| 快照历史（所有 project_progress 记录） | 数据分析/可视化 |
| Wiki 内容（HTML + 索引 + 变更历史） | 导出历史记录 |
| ZIP 打包下载 | 异步导出/进度条 |
| 管理员权限控制 | 导出频率限制 |
| API 支持（供 AI Agent 后台获取） | 缓存机制 |

---

## 2. 需求详情

### 2.1 功能需求 #1：项目概览导出

**需求编号**: REQ-EXP-001

**需求描述**:
导出项目的基本信息、配置数据

**后端需求**:
- 查询项目基本信息（名称、创建日期、起止日期、状态）
- 查询项目配置（coverage_mode: tc_cp/fc_cp）
- 生成 Markdown 文档和 Excel 表格

**验收标准**:
- [ ] 导出项目名称、创建日期、起止日期、状态
- [ ] 导出 coverage_mode 配置
- [ ] 生成 project_overview.md 和 project_overview.xlsx

---

### 2.2 功能需求 #2：覆盖率数据导出

**需求编号**: REQ-EXP-002

**需求描述**:
导出项目的覆盖率数据，包括当前覆盖率、里程碑覆盖率、历史趋势

**后端需求**:
- 计算当前覆盖率（按 coverage_mode）
- 按 dv_milestone 分组统计里程碑覆盖率（DV0.3/DV0.5/DV0.7/DV1.0）
- 查询所有 project_progress 快照记录
- 生成 Markdown 文档和 Excel 表格（不含图表图片）

**验收标准**:
- [ ] 导出当前覆盖率
- [ ] 导出按 dv_milestone 分组的里程碑覆盖率
- [ ] 导出所有历史快照数据（project_progress 表）

---

### 2.3 功能需求 #3：TC/CP 统计导出

**需求编号**: REQ-EXP-003

**需求描述**:
导出 TC/CP 的统计数据

**后端需求**:
- 统计 TC 总数及 OPEN/CODED/FAIL/PASS/REMOVED 各状态数量
- 统计 CP 总数及按 Feature 分组的 CP 数量
- 计算 TC 通过率（PASS / 总数）
- 统计 TC Owner 分布（仅汇总，不含详细列表）

**验收标准**:
- [ ] 导出 TC 状态分布
- [ ] 导出 CP 按 Feature 分组统计
- [ ] 导出 TC 通过率
- [ ] 导出 TC Owner 分布（统计汇总）

---

### 2.4 功能需求 #4：Dashboard 数据导出

**需求编号**: REQ-EXP-004

**需求描述**:
导出 Dashboard 相关数据（Feature×Priority 矩阵、Owner 分布、Coverage Matrix）

**后端需求**:
- 生成 Feature×Priority Matrix 数据（行=Feature，列=Priority）
- 生成 Owner 分布表（TC 数量）
- 生成 Coverage Matrix 数据（Feature × Priority）

**验收标准**:
- [ ] 导出 Feature×Priority Matrix 数据（md + xlsx）
- [ ] 导出 Owner 分布表（md + xlsx）
- [ ] 导出 Coverage Matrix 数据含行合计和列合计（md + xlsx）

---

### 2.5 功能需求 #5：Feature 列表导出

**需求编号**: REQ-EXP-005

**需求描述**:
导出项目所有 Feature 的统计汇总

**后端需求**:
- 按 Feature 分组统计
- 每个 Feature 包含：CP 数量、覆盖率范围、优先级分布
- 不包含单个 CP 的详细列表

**验收标准**:
- [ ] 导出所有 Feature 列表（统计汇总，不含 CP 详情）

---

### 2.6 功能需求 #6：快照历史导出

**需求编号**: REQ-EXP-006

**需求描述**:
导出项目的所有历史快照数据

**后端需求**:
- 查询 project_progress 表所有记录
- 包含日期、覆盖率、TC/CP 数量等

**验收标准**:
- [ ] 导出所有 project_progress 快照记录

---

### 2.7 功能需求 #7：Wiki 内容导出

**需求编号**: REQ-EXP-007

**需求描述**:
导出项目的 Wiki 内容（HTML 页面、索引、变更历史）

**后端需求**:
- 查询 Wiki 目录结构
- 复制 Wiki 页面 HTML 文件
- 导出 Wiki 索引（index.json）和变更历史（changes_index.json）
- Wiki 内容保持原有语言（中英文不变）

**验收标准**:
- [ ] 导出 Wiki 索引（index.json）
- [ ] 导出 Wiki 变更历史（changes_index.json）
- [ ] 导出所有 Wiki 页面 HTML 文件

---

### 2.8 功能需求 #8：ZIP 打包下载

**需求编号**: REQ-EXP-008

**需求描述**:
将所有导出文件打包为 ZIP，供用户下载

**后端需求**:
- 使用内存流（io.BytesIO）生成 ZIP
- 临时文件使用 tempfile.mkdtemp()，失败时清理
- 项目名称 sanitized（特殊字符移除）
- 文件名格式：`project_export_{project_name}_{YYYYMMDD_HHMMSS}.zip`

**验收标准**:
- [ ] 所有文件打包为单个 ZIP
- [ ] ZIP 可正常解压
- [ ] 文件名符合格式要求

---

### 2.9 功能需求 #9：权限控制

**需求编号**: REQ-EXP-009

**需求描述**:
导出功能仅管理员可用，前端仅管理员可见

**前端需求**:
- 导出按钮仅 admin 角色可见
- 非管理员用户看不到导出按钮

**后端需求**:
- API 使用 @admin_required 装饰器
- 非管理员调用返回 403

**错误响应**:
```json
// 项目不存在
{"error": "项目不存在", "code": "PROJECT_NOT_FOUND"}

// 无权访问（非管理员）
{"error": "无权限执行此操作", "code": "FORBIDDEN"}
```

**验收标准**:
- [ ] 前端：非管理员看不到导出按钮
- [ ] 后端：非管理员调用 API 返回 FORBIDDEN
- [ ] 后端：项目不存在返回 PROJECT_NOT_FOUND

---

### 2.10 功能需求 #10：API 支持

**需求编号**: REQ-EXP-010

**需求描述**:
提供 API 接口供 AI Agent 后台获取导出材料包

**后端需求**:
- 端点：`GET /api/export/project/<project_id>/package`
- 权限：管理员
- 响应：ZIP 二进制流（Content-Type: application/zip）

**验收标准**:
- [ ] API 支持 ZIP 下载
- [ ] 仅管理员可调用

---

## 3. 导出材料包结构

```
project_export_{project_name}_{YYYYMMDD_HHMMSS}.zip
├── README.md                          # 材料包说明
├── project_overview.md                # 项目概览
├── project_overview.xlsx              # 项目配置表格
├── coverage_trend.md                  # 覆盖率趋势
├── coverage_trend.xlsx                # 覆盖率数据表
├── tc_cp_statistics.md                # TC/CP统计说明
├── tc_cp_statistics.xlsx              # TC/CP详细列表
├── dashboard_feature_matrix.md        # Feature×Priority矩阵
├── dashboard_feature_matrix.xlsx      # 矩阵数据
├── dashboard_owner_distribution.md    # Owner分布说明
├── dashboard_owner_distribution.xlsx  # Owner数据
├── dashboard_coverage_matrix.md       # Coverage Matrix说明
├── dashboard_coverage_matrix.xlsx     # Matrix数据
├── feature_list.md                    # Feature列表说明
├── feature_list.xlsx                 # Feature统计汇总
├── snapshots.md                       # 快照历史说明
├── snapshots.xlsx                     # 快照数据
└── wiki/                              # Wiki内容
    ├── index.json                     # Wiki索引
    ├── changes_index.json             # Wiki变更历史
    └── pages/                         # Wiki页面HTML
        └── {page_slug}.html           # 页面文件
```

---

## 4. 技术方案

### 4.1 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 后端框架 | Flask | 现有项目技术栈 |
| Excel 生成 | openpyxl>=3.0.0,<4.0.0 | Python Excel 库 |
| ZIP 打包 | zipfile | Python 标准库 |
| 临时文件 | tempfile.mkdtemp() | 安全临时目录 |
| 权限控制 | @admin_required | 复用现有权限装饰器 |

### 4.2 API 设计

#### 导出材料包

**端点**: `GET /api/export/project/<project_id>/package`

**权限**: 管理员

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | 是 | 项目ID |

**响应**:
- Content-Type: `application/zip`
- Content-Disposition: `attachment; filename="project_export_{name}_{date}.zip"`

### 4.3 数据库修改

**无数据库修改需求**。使用现有数据模型。

### 4.4 新增依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| openpyxl | >=3.0.0,<4.0.0 | Excel 文件生成 |

---

## 5. 前端界面

### 5.1 导出按钮

| 元素 | 说明 |
|------|------|
| **位置** | 项目列表页面，每行末的操作按钮列 |
| **可见性** | 仅管理员可见（前端完全隐藏，非管理员看不到） |
| **按钮样式** | "📦 导出材料包" 图标按钮 |
| **状态** | 导出中显示 "导出中..." 加载状态 |

### 5.2 导出流程

1. 用户在项目列表页面找到目标项目
2. 点击该行末操作列的"📦 导出材料包"按钮
3. 前端显示 "导出中..." 加载状态
4. 前端调用 API `/api/export/project/<id>/package`
5. 浏览器自动弹出下载对话框
6. 成功后显示 toast 提示"导出成功"
7. 失败时显示错误信息，用户可重试

### 5.3 文件命名规范

| 字段 | 规则 |
|------|------|
| 格式 | `project_export_{project_name}_{date}.zip` |
| 日期格式 | `YYYYMMDD_HHMMSS`（如：`20260512_143025`） |
| 特殊字符处理 | 空格替换为 `_`，其他非字母数字字符移除 |
| 示例 | `project_export_ProjectName_20260512_143025.zip` |

---

## 6. 验收标准

### 6.1 功能验收

- [ ] 管理员可以导出任意项目材料包
- [ ] 非管理员用户看不到导出按钮
- [ ] 非管理员调用 API 返回 FORBIDDEN
- [ ] 材料包包含所有指定文件
- [ ] ZIP 文件可正常解压
- [ ] Excel 文件可正常打开和编辑
- [ ] Wiki 内容保持原有语言（中英文不变）

### 6.2 性能验收

- [ ] 小型项目（<100 TC）导出时间 < 5秒
- [ ] 中型项目（100-500 TC）导出时间 < 30秒
- [ ] 大型项目（>500 TC）导出时间 < 60秒

**测试说明**：单用户顺序导出，标准开发服务器配置

### 6.3 权限验收

- [ ] guest/user 角色无法访问导出 API（403）
- [ ] 未登录用户无法访问导出 API（401）

---

## 7. 开发计划

### 7.1 开发任务

| 任务 | 状态 | 预计时间 |
|------|------|----------|
| 后端：导出 API 框架 | ⏳ 待开发 | 1h |
| 后端：各模块导出逻辑 | ⏳ 待开发 | 6h |
| 后端：ZIP 打包生成 | ⏳ 待开发 | 1h |
| 前端：导出按钮 | ⏳ 待开发 | 0.5h |
| 测试与优化 | ⏳ 待开发 | 2h |
| **总计** | | **~10.5h** |

### 7.2 里程碑

| 里程碑 | 计划日期 | 状态 |
|--------|----------|------|
| 技术方案评审完成 | 2026-05-12 | ✅ |
| 后端开发完成 | TBD | ⏳ |
| 前端开发完成 | TBD | ⏳ |
| 测试完成 | TBD | ⏳ |
| 发布 | TBD | ⏳ |

---

## 8. 风险与对策

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| 大项目导出超时 | 高 | 中 | v0.14.0 先实现同步版本；后续版本添加异步导出 |
| Excel 格式兼容问题 | 中 | 低 | 使用标准 xlsx 格式；提供 CSV 备选 |
| Wiki 内容为空 | 低 | 低 | 检查 Wiki 是否存在，缺失则跳过 |
| 磁盘空间不足 | 中 | 低 | 检查磁盘空间；使用内存流替代磁盘存储 |
| 临时文件清理失败 | 低 | 低 | 使用 finally 块确保清理；定期 cron 清理 |

---

## 9. 术语表

| 术语 | 定义 |
|------|------|
| DV0.3/DV0.5/DV0.7/DV1.0 | DV Milestone，芯片验证阶段的里程碑 |
| 里程碑覆盖率 | 该里程碑下已覆盖的 CP 占总 CP 的比例（按 dv_milestone 分组统计） |
| Coverage Matrix | Feature × Priority 覆盖率矩阵 |
| TC (Test Case) | 测试用例，验证功能的最小单元 |
| CP (Cover Point) | 覆盖点，需要被验证的设计点 |
| project_progress | 项目进度快照表，存储历史覆盖率数据 |
| coverage_mode | 覆盖率计算模式：`tc_cp`（按TC计算）或 `fc_cp`（按Feature计算） |

---

## 10. 相关文档

| 文档 | 路径 |
|------|------|
| 需求分析 | `/projects/management/feedbacks/done/requirements_analysis_EXPORT_PACKAGE_v0.14.0_20260512.md` |
| 开发规范 | `/projects/management/tracker/docs/DEVELOPMENT/DEVELOPMENT_PROCESS.md` |
| API 测试策略 | `/projects/management/tracker/docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| UI 测试策略 | `/projects/management/tracker/docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` |
| BugLog | `/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md` |

---

## 11. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.14.0 | 2026-05-12 | 初始版本规格书 |
| v0.14.0 | 2026-05-12 | 更新相关文档路径（从 reviewed 改为 done） |

---

**文档创建时间**: 2026-05-12 12:00:00
**创建人**: OpenClaw