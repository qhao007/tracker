# 芯片验证 Tracker v0.11.0 总体规格书

> **版本**: v0.11.0 | **更新日期**: 2026-04-03 | **状态**: ✅ 已完成开发

---

## 目录

1. [需求分析](#1-需求分析)
2. [实现方案](#2-实现方案)
3. [功能规格](#3-功能规格)
4. [API 接口](#4-api-接口)
5. [数据库设计](#5-数据库设计)
6. [版本管理](#6-版本管理)
7. [测试计划](#7-测试计划)
8. [部署说明](#8-部署说明)
9. [版本历史](#9-版本历史)

---

## 1. 需求分析

### 1.1 背景

芯片验证团队需要管理 Cover Points（覆盖点）与 Test Cases（测试用例）的关联关系，跟踪验证进度和覆盖率。团队成员需要多人协作，实时共享数据。

### 1.2 核心目标

- 提供可视化的 Cover Points 管理界面
- 支持 Test Cases 的创建、编辑、状态跟踪
- 自动计算 Cover Points 的完成进度和整体覆盖率
- 支持多人协作，数据实时同步到服务器
- **支持多项目（Project）管理**
- **支持测试版本和正式版本分离**

### 1.3 范围

| 包含 | 不包含 |
|------|--------|
| 多项目（Project）管理 | 与外部 CI/CD 系统集成 |
| Cover Points 的增删改查 | 自动化测试执行引擎 |
| Test Cases 的增删改查 | 芯片仿真功能 |
| TC 与 CP 的多对多关联管理 | |
| 状态跟踪（OPEN/CODED/FAIL/PASS） | |
| 用户权限管理（admin/user/guest） | |
| 项目备份/恢复（Archive） | |
| 测试版本和正式版本分离 | |
| 进度/覆盖率统计面板 | |
| 数据持久化到 SQLite 数据库 | |
| systemd 正式版部署 | |
| **v0.9.0 前端界面优化** | |
| **v0.9.1 用户反馈功能** | |
| **v0.9.2 关联状态与滚动优化** | |
| **v0.10.0 Priority 过滤功能** | |
| **v0.10.1 批量创建用户** | |
| **v0.10.2 Intro 引导页** | |
| **v0.11.0 FC/Dashboard** | |

### 1.4 v0.9.0 重大变更

**v0.9.0 前端界面优化：**

- **设计系统**：建立统一的 CSS 变量系统（颜色、字体、间距、圆角、阴影）
- **视觉风格**：采用现代 Vercel/Linear 风格，主蓝色改为色调从紫色 (#4f46e5)
- **组件重构**：Header、Tabs、Table、Modal 等核心组件样式全面升级
- **交互体验**：添加微交互动画（按钮悬停、卡片悬浮、模态框动画）
- **兼容处理**：添加 CSS 类名兼容映射，确保平滑迁移
- **用户偏好**：尊重用户减少动画偏好 (prefers-reduced-motion)

**v0.6.0 第一阶段功能增强：**

- **Status 日期记录**: CODED/FAIL/PASS/REMOVED 状态变更时自动记录日期
- **Target Date 字段**: 支持设置测试预期完成日期
- **REMOVED 状态**: 新增已移除测试用例状态，统计时自动排除
- **批量修改功能**: 支持批量更新状态、Target Date、DV Milestone
- **DV Milestone 字段**: 跟踪测试用例所属的 DV 里程碑版本
- **CP Priority 字段**: 支持 Cover Point 优先级标记 (P0/P1/P2)

### 1.5 v0.6.1 重大变更

**v0.6.1 第二阶段功能增强：**

- **Status 颜色粗体显示**: Test Case Status 颜色改为粗体显示，更醒目
- **CP 过滤功能**: 支持按 Feature 和 Priority 过滤 Cover Points
- **备份恢复自定义路径**: 支持上传本地备份文件恢复项目

### 1.6 v0.6.2 重大变更

**v0.6.2 第三阶段功能增强（2026-02-10 完成）：**

- **CP 详情下拉**: 点击详情按钮展开 CP 完整信息和关联 TC 列表
  - 新增 API: `GET /api/cp/{id}/tcs` 获取 CP 关联的 TC 列表
  - 详情面板显示 cover_point_details、comments 和关联 TC

- **TC 过滤**: 支持多字段过滤 Test Cases 列表
  - Status 单选过滤（多选改为单选，体验更好）
  - DV Milestone 单选过滤
  - Owner 动态过滤（从 TC 列表自动填充）
  - Category 动态过滤
  - 显示过滤后的记录数量
  - 重置过滤条件

**v0.6.2 Bug 修复（BUG-027~036）：**

| Bug ID | 问题 | 修复内容 |
|--------|------|----------|
| BUG-027 | 展开所有 CP 详情时 TC 数据不加载 | toggleAllCPDetails() 添加 loadCPTcConnections() 调用 |
| BUG-028 | TC 过滤重置后列表不刷新 | resetTCFilter() 末尾添加 renderTC() 调用 |
| BUG-029 | TC 过滤重置代码存在无效语句 | 删除无效代码行 |
| BUG-030 | CP 详情关联 TC 显示错误 | API 添加 project_id 参数 |
| BUG-031 | TC Priority 过滤不需要 | 从过滤面板移除 Priority 选项 |
| BUG-032 | TC Owner/Category 过滤选项不动态加载 | 添加 loadTCFilterOptions() 函数 |
| BUG-033 | TC Status/DV Milestone 需要单选下拉框 | 多选改为单选 |
| BUG-034 | TC Status/DV Milestone 缺少全部选项 | 添加"全部"选项 |
| BUG-035 | TC DV Milestone 过滤选项不动态加载 | 动态从 TC 列表加载 |
| BUG-036 | projectSelector ID 拼写错误 | projectSelect → projectSelector |

### 1.7 v0.7.1 重大变更 (2026-02-25)

**v0.7.1 功能增强（用户认证与权限管理）：**

- **用户认证系统**: 支持用户名密码登录和访客登录
  - 新增独立用户数据库 `users.db`
  - 支持 admin/user/guest 三种角色
  - pbkdf2_sha256 密码哈希
  - 暴力破解防护（5次失败锁定15分钟）
  - Session 安全配置（HttpOnly, SameSite）

- **权限管理（RBAC）**: 基于角色的访问控制
  - 前端按钮权限控制（根据角色隐藏/显示）
  - 后端 API 权限校验（@admin_required, @guest_required）
  - created_by 字段记录创建者

- **项目删除功能**: 支持管理员删除项目
  - 删除前自动创建归档备份
  - 删除确认对话框
  - 仅 admin 可删除

- **用户手册**: 在线查看使用帮助
  - 帮助按钮在首页顶部工具栏
  - Markdown 渲染

**v0.7.1 Bug 修复：**

| Bug ID | 问题 | 修复内容 |
|--------|------|----------|
| BUG-063 | 项目删除缺少归档备份 | delete_project 添加归档备份逻辑 |
| BUG-064 | user 角色项目管理按钮可见 | 添加 projectManageBtn 权限控制 |

### 1.8 v0.8.0 重大变更 (2026-03-01)

**v0.8.0 功能增强（进度图表基础框架）：**

1. **项目起止日期字段**：
   - 数据库：projects 表新增 `start_date`、`end_date` 字段
   - API：创建/更新项目时支持日期参数
   - 前端：项目管理中输入/编辑日期
   - 校验：开始日期不能晚于结束日期

2. **Progress Charts 页面**：
   - 新增 Progress Charts Tab 页面
   - 集成 Chart.js (CDN)
   - 展示项目进度曲线框架
   - 无项目/无日期时显示友好提示

3. **Chart.js 加载失败降级处理**：
   - CDN 加载失败时设置 `window.ChartLoaded = false`
   - 页面检测加载失败显示友好提示："📊 图表库加载失败，请检查网络连接"

4. **管理员编辑项目日期功能**：
   - 项目列表添加编辑按钮
   - 弹窗编辑起止日期
   - 调用 PUT /api/projects/<id> 更新

5. **ISSUE-001 修复**：
   - 项目选择框宽度固定为 200px

### 1.9 v0.8.1 重大变更 (2026-03-02)

**v0.8.1 功能增强（计划曲线）：**

1. **计划曲线计算算法**：
   - 基于 TC target_date 计算每周预期覆盖率
   - 使用所有非 REMOVED 状态 TC 关联的 CP 去重计算
   - 按周分组，返回 `[{week: 'YYYY-MM-DD', coverage: float}]` 格式

2. **API 端点扩展**：
   - `GET /api/progress/<project_id>` 返回计划曲线数据
   - 支持 `start_date` 和 `end_date` 查询参数过滤

3. **前端图表渲染**：
   - 计划曲线使用蓝色虚线 (#2170bb, borderDash: [5, 5])
   - 支持图例和 Tooltip 显示

4. **时间段选择器**：
   - 起始日期和结束日期输入框
   - 应用按钮触发图表刷新
   - 清空按钮恢复显示全周期数据

5. **边界处理**：
   - 无项目：显示"请选择一个项目查看进度图表"
   - 无日期：显示"请先设置项目起止日期"
   - 无数据：显示空图表占位

**v0.8.1 Bug 修复：**

| Bug ID | 问题 | 修复内容 |
|--------|------|----------|
| BUG-065 | sync 命令未覆盖已存在的预置空文件 | 强制覆盖已存在的文件 |
| BUG-066 | 计划曲线 API 状态查询大小写不匹配 | tc.status = 'PASS' (全大写) |
| BUG-067 | clean 导致预置项目无法显示 | is_archived 默认值改为 False |

### 1.10 v0.8.2 重大变更 (2026-03-04)

**v0.8.2 功能增强（实际曲线与快照）：**

1. **实际曲线显示**：
   - 绿色实线 (#28a745) 展示实际覆盖率
   - 与蓝色虚线计划曲线同时显示
   - 共用时间段选择器

2. **快照数据采集**：
   - 手动触发：POST /api/progress/<project_id>/snapshot
   - 定时任务：POST /api/cron/progress-snapshot (需 Token 认证)
   - 计算当前 Pass 状态 TC 关联的 CP 覆盖率

3. **快照管理功能**：
   - 快照列表对话框
   - 管理员可删除快照
   - 非管理员只能查看

4. **导出功能**：
   - 导出快照数据为 CSV/JSON 格式

5. **Chart.js CDN Fallback**：
   - 3秒超时自动切换本地
   - window.ChartLoaded 状态标志

**v0.8.2 Bug 修复：**

| Bug ID | 问题 | 修复内容 |
|--------|------|----------|
| BUG-068 | 快照管理对话框缺少导出按钮 | 添加导出按钮 |
| BUG-069 | project_progress 数据库表未创建 | 自动创建表 |
| BUG-070 | sessionRole 变量未定义 | 改用 currentUser.role |
| BUG-071 | loadProgressChart 未调用 updateSnapshotButtons | 添加调用 |
| BUG-072 | currentProjectId 未设置 | selectProject 添加设置 |
| BUG-073 | 退出按钮选择器不存在 | 使用文本选择器 |

### 1.11 v0.8.3 重大变更 (2026-03-04)

**v0.8.3 功能增强（测试便利性与代码质量）：**

1. **自动创建测试用户**：
   - 创建项目时自动创建测试用户（test_user）
   - 新增"同时创建测试用户"复选框（默认勾选）
   - 显示生成的测试用户名和密码
   - 用户名格式：`test_user_{项目名}`
   - 密码固定：`test_user123`

2. **项目日期必填验证**：
   - 创建项目时起始日期和结束日期必填
   - 前端添加 required 标记和提交前验证
   - 后端 API 验证日期必填
   - 结束日期必须晚于起始日期

3. **前端常量管理**：
   - 新增 `app_constants.js` 文件
   - 统一管理 Session keys（USER, PROJECT, PROJECT_ID）
   - 统一管理 API endpoints（LOGIN, PROJECTS, TC, CP 等）
   - 便于后续维护和修改

**v0.8.3 Bug 修复：**

| Bug ID | 问题 | 修复内容 |
|--------|------|----------|
| BUG-074 | 创建项目缺少日期字段验证 | 添加 start_date/end_date 必填验证 |
| BUG-075 | 前端 Session key 分散 | 统一到 app_constants.js 管理 |

---

## 2. 实现方案

### 2.1 目录结构

```
/projects/management/tracker/              ← Git 仓库（只维护 dev/）
├── dev/                                  ← 开发版代码（Git 分支: develop）
│   ├── server.py                        # 开发启动脚本 (:8081)
│   ├── server_test.py      # 旧启动脚本（已弃用）
│   ├── start_server_test.sh     # 新启动脚本 (gunicorn)
│   ├── app/                             # Flask 应用
│   ├── index.html                       # 前端页面
│   ├── data → ../shared/data/test_data  # 测试数据
│   ├── tests/                           # 测试用例
│   └── docs/                            # 文档
│
├── shared/                              # 共享数据（不纳入 Git）
│   └── data/
│       ├── user_data/                   # 用户真实数据（正式版使用）
│       │   ├── projects.json
│       │   ├── Debugware_65K.db
│       │   └── EX5.db
│       │
│       └── test_data/                    # 测试数据（开发版使用）
│           ├── projects.json
│           └── *.db
│
└── scripts/                             # 工具脚本
    ├── release.py                      # 版本发布脚本
    ├── migrate_v02_to_v03.py            # v0.2 → v0.3 迁移
    ├── compat_check.py                  # 兼容性检查
    └── data_manager.py                  # 数据管理工具

/release/tracker/                         ← 发布目录（由 release.py 生成，不纳入 Git）
├── v0.3.1/                             ← 历史版本
├── v0.3.2/                             ← 当前版本
├── current → v0.3.2                    ← 软链接指向当前版本
└── RELEASE_NOTES.md                     ← 发布报告
```

### 2.2 数据隔离原则

| 原则 | 说明 |
|------|------|
| **用户数据独立** | `user_data/` 存储用户真实数据，独立于代码 |
| **测试数据隔离** | `test_data/` 存储测试数据，与用户数据完全隔离 |
| **dev 使用 test_data** | 开发测试操作 test_data，不影响用户数据 |
| **发布目录独立** | `/release/tracker/v{version}/` 存放发布版本，不纳入 Git |
| **current 软链接** | `/release/tracker/current` 指向当前运行版本 |
| **版本发布** | 发布到 `/release/tracker/v{version}`，切换软链接更新版本 |
| **数据库版本** | 每个数据库包含版本号，支持自动迁移 |

### 2.3 多版本架构

```
                            ┌─────────────────────────┐
                            │       systemd 服务      │
                            │  /release/tracker/current → v{version}/
                            └─────────────────────────┘
                                              │
              ┌─────────────────────────────────┼─────────────────────────────────┐
              │                                 │                                 │
              ▼                                 ▼                                 ▼
      ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
      │  发布版       │               │  开发版       │               │  共享数据     │
      │ /release/    │               │  dev/        │               │  shared/     │
      │ tracker/     │               │  :8081       │               │  data/       │
      │ current/     │               │  (Git)       │               │              │
      └───────────────┘               └───────────────┘               └───────────────┘
              │                                 │                                 │
              ▼                                 ▼                                 ▼
      ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
      │ user_data/    │               │ test_data/   │               │ backups/     │
      │ (用户真实数据) │               │ (测试数据)   │               │ (原始备份)   │
      └───────────────┘               └───────────────┘               └───────────────┘
```

### 2.4 数据兼容性测试

如需测试用户数据与 dev 版本的兼容性：

```bash
# 1. 同步用户项目到测试目录（复制一份）
python3 scripts/data_manager.py sync

# 2. 在 dev 版本中测试复制的用户数据
# 访问 http://localhost:8081
# 切换到复制的用户项目进行测试

# 3. 测试完成后清理（删除复制的用户项目）
python3 scripts/data_manager.py clean
```

### 2.5 端口配置

| 版本 | 端口 | 数据目录 | 启动命令 |
|------|------|----------|----------|
| 正式版 | 8080 | user_data | systemd 服务管理 (gunicorn) |
| 测试版 | 8081 | test_data | `cd dev && bash start_server_test.sh` |

---

## 3. 功能规格

### 3.1 功能列表

| 编号 | 功能 | 描述 | 优先级 |
|------|------|------|--------|
| F001 | **项目管理** | 创建、加载、切换项目 | P0 |
| F002 | **代码隔离** | stable/ 和 dev/ 目录分离 | P0 |
| F003 | **数据共享** | shared/data/ 集中存储 | P0 |
| F004 | **Cover Points 管理** | 按字段结构管理 CP | P0 |
| F005 | **Test Cases 管理** | 按字段结构管理 TC | P0 |
| F006 | **关联管理** | TC 关联 CP（多对多关系） | P0 |
| F007 | **状态跟踪** | OPEN → CODED → FAIL → PASS | P0 |
| F008 | **版本迁移** | 数据库版本号 + 自动迁移 | P0 |
| F009 | **排序过滤** | 按字段排序和过滤 TC | P1 |
| F010 | **完成日期** | 显示 TC 完成日期 | P1 |
| F011 | **进度统计** | 自动计算 CP 完成进度 | P1 |
| F012 | **覆盖率计算** | 整体覆盖率百分比显示 | P1 |
| F013 | **项目备份** | 导出项目 Archive | P1 |
| F014 | **项目恢复** | 从 Archive 导入恢复 | P1 |
| F015 | **版本管理** | 测试版/正式版分离 | P1 |
| F016 | **发布脚本** | 一键发布到正式版 | P1 |
| F017 | **兼容性检查** | 启动时自动检查 | P1 |
| F018 | **界面优化** | Excel 风格，紧凑显示 | P2 |
| F019 | **systemd 部署** | 正式版 24/7 运行 | P1 |
| **F020** | **Status 日期记录** | 状态变更时自动记录日期 | P0 |
| **F021** | **Target Date 字段** | 设置测试预期完成日期 | P0 |
| **F022** | **REMOVED 状态** | 已移除测试用例状态 | P0 |
| **F023** | **批量修改功能** | 批量更新状态/日期/里程碑 | P0 |
| **F024** | **DV Milestone 字段** | 跟踪 DV 里程碑版本 | P0 |
| **F025** | **CP Priority 字段** | Cover Point 优先级标记 | P0 |
| **F026** | **Status 粗体显示** | Test Case Status 颜色改为粗体 | P2 |
| **F027** | **CP 过滤功能** | 按 Feature/Priority 过滤 CP | P0 |
| **F028** | **备份路径自定义** | 支持上传本地备份文件恢复 | P1 |
| **F029** | **CP 详情下拉** | 展开 CP 完整信息和关联 TC 列表 | P0 |
| **F030** | **TC 过滤** | 多字段过滤 Test Cases 列表 | P0 |
| **F031** | **计划曲线显示** | 基于 TC target_date 的预期覆盖率曲线 | P0 |
| **F032** | **时间段选择器** | 按日期范围过滤曲线数据 | P1 |
| **F033** | **实际曲线显示** | 绿色实线展示实际覆盖率 | P0 |
| **F034** | **手动快照采集** | 管理员手动触发快照 | P0 |
| **F035** | **定时快照采集** | Cron 定时任务自动快照 | P1 |
| **F036** **快照管理** | 查看/删除历史快照 | P0 |
| **F037** | **导出进度数据** | 导出快照为 CSV/JSON | P1 |
| **F038** | **Chart.js CDN Fallback** | 超时自动切换本地 | P2 |
| **F039** | **自动创建测试用户** | 创建项目时自动创建测试用户 | P1 |
| **F040** | **项目日期必填验证** | 创建/编辑项目时日期必填校验 | P1 |
| **F041** | **前端常量管理** | 统一管理 Session keys 和 API 端点常量 | P2 |
| **F042** | **CP关联状态可视化** | 未关联CP显示红色加粗+🔗图标 | P1 |
| **F043** | **TC关联状态可视化** | 未关联TC显示红色加粗+🔗图标 | P1 |
| **F044** | **CP/TC独立滚动条** | 表头sticky固定，内容独立滚动，高度自适应 | P0 |
| **F045** | **TC过滤布局优化** | TC过滤选项单行显示，与CP布局一致 | P1 |
| **F046** | **CP未关联过滤** | 后端支持filter=unlinked参数过滤未关联CP | P1 |
| **F047** | **admin强制改密码** | admin首次登录强制弹窗修改密码 | P1 |
| **F048** | **用户反馈功能** | 反馈API+UI，收集用户建议和问题 | P1 |
| **F049** | **Priority 过滤功能** | 图表支持按 CP Priority (P0-P3) 过滤 | P1 |
| **F050** | **批量创建用户** | 批量创建普通用户 API，默认密码 123456 | P1 |
| **F051** | **FC Tab 页面** | Functional Coverage 管理界面 | P1 |
| **F052** | **FC-CP 关联** | FC 与 CP 的多对多关联 | P1 |
| **F053** | **FC Batch API** | 批量更新 FC coverage_pct/status | P1 |
| **F054** | **CP Dashboard** | Apple 风格覆盖率仪表板 | P0 |
| **F055** | **Cron 快照 Token** | 修复 BUG-129，定时任务认证 | P1 |
| **F056** | **覆盖率算法修复** | BUG-106/107/108 修复 | P0 |

### 3.2 Cover Point 字段

| 字段 | 说明 | 必填 |
|------|------|------|
| Feature | 功能模块 | ✅ |
| Sub-Feature | 子功能模块 | ✅ |
| Cover Point | 覆盖点名称 | ✅ **(首要)** |
| Cover Point Details | 覆盖点详情 | ✅ |
| **Priority** | 优先级 (P0/P1/P2) | ✅ |
| Comments | 备注 | ❌ |

### 3.3 Test Case 字段

| 字段 | 说明 | 必填 |
|------|------|------|
| TestBench | 测试台 | ✅ |
| Category | 类别 | ✅ |
| Owner | 负责人 | ✅ |
| Test Name | 测试名称 | ✅ **(首要)** |
| Scenario Details | 场景详情 | ✅ |
| Checker Details | 检查器详情 | ❌ (可隐藏) |
| Coverage Details | 覆盖详情 | ❌ (可隐藏) |
| Comments | 备注 | ❌ (可隐藏) |
| Status | 状态 | 系统字段 |
| DV Milestone | DV 里程碑版本 | 系统字段 |
| Target Date | 目标完成日期 | 系统字段 |
| Status Date | 状态变更日期 | 系统字段 |
| **coded_date** | CODED 状态日期 | 系统字段 |
| **fail_date** | FAIL 状态日期 | 系统字段 |
| **pass_date** | PASS 状态日期 | 系统字段 |
| **removed_date** | REMOVED 状态日期 | 系统字段 |

### 3.3 Cover Point 覆盖率计算规则

> **v0.3.1 新增功能**

每个 Cover Point 显示覆盖率百分比，基于关联的 Test Cases 状态计算：

| 关联 TC 状态 | 覆盖率 |
|-------------|--------|
| 全部 PASS | **100%** ✅ |
| 无关联 TC | **0%** （显示 0/0） |
| 部分 PASS | **PASS 数量 / 关联总数 × 100%** |

**计算逻辑：**

```python
# 获取 CP 关联的所有 TC
cursor.execute('''
    SELECT tc.status FROM test_case tc
    INNER JOIN tc_cp_connections tcc ON tc.id = tcc.tc_id
    WHERE tcc.cp_id = ?
''', (cp_id,))

connected_tcs = cursor.fetchall()
total = len(connected_tcs)
passed = sum(1 for tc in connected_tcs if tc['status'] == 'PASS')

coverage = round(passed / total * 100, 1) if total > 0 else 0.0
```

**前端显示示例：**

| 状态 | 覆盖率显示 |
|------|-----------|
| 100% | 🟢 100% (3/3) |
| 部分 | 🟡 66.7% (2/3) |
| 0% | ⚪ 0% (0/3) |
| 无关联 | ⚪ 0% (0/0) |

**API 返回字段：**

```json
{
  "id": 1,
  "feature": "...",
  "cover_point": "...",
  "coverage": 100.0,
  "coverage_detail": "3/3"
}
```

### 3.4 状态定义

| 状态 | 说明 | 计入统计 |
|------|------|----------|
| OPEN | 待开发/待执行 | ✅ |
| CODED | 已开发完成 | ✅ |
| FAIL | 测试失败 | ✅ |
| PASS | 测试通过 | ✅ |
| REMOVED | 已移除/废弃 | ❌ |

**REMOVED 状态特殊规则**:
- 不计入 Total 统计
- 不计入 Pass Rate 计算
- 状态变更时自动清除与 CP 的关联
- 可转移回 CODED 状态

---

## 4. API 接口

### 4.1 版本管理

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/version` | 获取版本信息 |

### 4.2 认证 API (v0.7.1 新增)

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 用户名密码登录 | 公开 |
| POST | `/api/auth/guest-login` | 访客登录 | 公开 |
| POST | `/api/auth/logout` | 登出 | 登录 |
| GET | `/api/auth/me` | 获取当前用户信息 | 登录 |

**POST /api/auth/login 请求体**:
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**成功响应**:
```json
{
    "success": true,
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "is_active": 1
    }
}
```

**错误响应**:
```json
{
    "error": "Unauthorized",
    "message": "用户名或密码错误"
}
```

### 4.3 用户管理 API (v0.7.1 新增)

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| GET | `/api/users` | 获取用户列表 | 管理员 |
| POST | `/api/users` | 创建用户 | 管理员 |
| **POST** | **`/api/users/batch`** | **批量创建用户（v0.10.1）** | **管理员** |
| PATCH | `/api/users/{id}` | 更新用户（禁用/启用） | 管理员 |
| DELETE | `/api/users/{id}` | 删除用户 | 管理员 |
| POST | `/api/users/{id}/reset-password` | 重置密码 | 管理员 |

**GET /api/users 响应**:
```json
[
    {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "is_active": 1,
        "created_at": "2026-02-25 10:00:00",
        "last_login": "2026-02-25 15:30:00"
    },
    {
        "id": 2,
        "username": "user01",
        "role": "user",
        "is_active": 1,
        "created_at": "2026-02-25 11:00:00",
        "last_login": null
    }
]
```

**POST /api/users 请求体**:
```json
{
    "username": "newuser",
    "password": "password123",
    "role": "user"
}
```

**POST /api/users/batch 请求体** (v0.10.1 新增):
```json
{
    "users": [
        {"username": "zhangsan"},
        {"username": "lisi"},
        {"username": "wangwu"}
    ]
}
```

**说明**：
- 密码固定为 `123456`（响应中返回）
- 角色固定为 `user`（普通用户）
- 单次最多创建 50 个用户

**响应**:
```json
{
    "success": true,
    "created": 3,
    "failed": 0,
    "password": "123456",
    "results": [
        {"username": "zhangsan", "status": "created", "id": 10},
        {"username": "lisi", "status": "created", "id": 11},
        {"username": "wangwu", "status": "created", "id": 12}
    ]
}
```

### 4.3.1 用户反馈 API (v0.9.1 新增)

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| GET | `/api/feedbacks` | 获取反馈列表 | 管理员 |
| POST | `/api/feedbacks` | 提交反馈 | 公开 |
| PATCH | `/api/feedbacks/{id}` | 更新反馈状态 | 管理员 |
| DELETE | `/api/feedbacks/{id}` | 删除反馈 | 管理员 |

**POST /api/feedbacks 请求体**:
```json
{
    "title": "功能建议",
    "content": "希望增加导出功能",
    "category": "feature_request",
    "contact": "user@example.com"
}
```

**响应**:
```json
{
    "success": true,
    "feedback_id": 1,
    "message": "反馈已提交"
}
```

### 4.4 项目管理

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| **GET** | **`/api/projects/{id}`** | **获取项目详情** |
| POST | `/api/projects` | 创建新项目 |
| POST | `/api/projects/{id}/archive` | 备份项目 |
| GET | `/api/projects/archive/list` | 获取归档列表 |
| POST | `/api/projects/restore` | 从归档恢复（按文件名） |
| **POST** | **`/api/projects/restore/upload`** | **从上传文件恢复（v0.6.1）** |
| DELETE | `/api/projects/{id}` | 删除项目 |

**POST /api/projects/restore/upload 请求示例**（v0.6.1 新增）:

```
POST /api/projects/restore/upload
Content-Type: multipart/form-data

Body: file=@backup.json
```

**请求参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `file` | file | JSON 格式的备份文件 |

**成功响应**:
```json
{
  "success": true,
  "project": {
    "id": 10,
    "name": "Restored_Project",
    "created_at": "2026-02-09 12:00:00"
  }
}
```

**错误响应**:
```json
{
  "error": "项目 \"xxx\" 已存在，无法恢复"
}
```

**POST /api/projects 请求体** (v0.8.3 新增字段):
```json
{
  "name": "项目名称",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "create_test_user": true
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 项目名称 |
| start_date | string | ✅ | 开始日期 (YYYY-MM-DD) |
| end_date | string | ✅ | 结束日期 (YYYY-MM-DD) |
| create_test_user | boolean | ❌ | 是否同时创建测试用户（默认 false） |

**POST /api/projects 响应** (v0.8.3 新增):
```json
{
  "success": true,
  "project": {
    "id": 1,
    "name": "项目名称",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31"
  },
  "test_user": {
    "username": "test_user_项目名称",
    "password": "test_user123",
    "role": "user"
  }
}
```

### 4.5 Cover Points

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/cp` | 获取 CP 列表（**含覆盖率 + Priority + 过滤**） |
| **GET** | **`/api/cp/{id}`** | **获取 CP 详情（需 project_id）** |
| **GET** | **`/api/cp/{id}/tcs`** | **获取 CP 关联的 TC 列表（v0.6.2）** |
| POST | `/api/cp` | 创建 CP |
| PUT | `/api/cp/{id}` | 更新 CP（**需 project_id**） |
| DELETE | `/api/cp/{id}` | 删除 CP（需 project_id） |
| **POST** | **`/api/cp/batch/priority`** | **批量更新 Priority（需 project_id）** |

**API 参数说明**:
- **GET /api/cp**: 通过查询参数传递 `project_id`，例如: `/api/cp?project_id=1`
- **GET /api/cp/{id}**: 通过查询参数传递 `project_id`，例如: `/api/cp/1?project_id=1`
- **POST /api/cp**: 在请求体中传递 `project_id`
- **PUT /api/cp/{id}**: 在请求体中必须包含 `project_id`
- **DELETE /api/cp/{id}**: 通过查询参数传递 `project_id`，例如: `/api/cp/1?project_id=1`

**GET /api/cp 过滤参数**（v0.6.1 新增，v0.9.2 扩展）:

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `project_id` | int | 项目 ID（必填） | `?project_id=1` |
| `feature` | string | Feature 过滤（支持多值，逗号分隔） | `?feature=FeatureA,FeatureB` |
| `priority` | string | Priority 过滤（支持多值，逗号分隔） | `?priority=P0,P1` |
| `filter` | string | **关联状态过滤（v0.9.2 新增）**：`all`(默认), `unlinked` | `?filter=unlinked` |

**GET /api/cp 请求示例**:

```
# 获取所有 CP
GET /api/cp?project_id=1

# 按 Feature 过滤
GET /api/cp?project_id=1&feature=FeatureA

# 按 Priority 过滤
GET /api/cp?project_id=1&priority=P0

# 组合过滤
GET /api/cp?project_id=1&feature=FeatureA,FeatureB&priority=P0,P1

# 过滤未关联的 CP（v0.9.2 新增）
GET /api/cp?project_id=1&filter=unlinked
```

**PUT /api/cp/{id} 请求体**:
```json
{
    "project_id": 1,
    "feature": "Feature A",
    "sub_feature": "SubFeature A",
    "cover_point": "CP_A",
    "cover_point_details": "Details",
    "priority": "P0",
    "comments": ""
}
```

**DELETE /api/cp/{id} 请求示例**:
```
DELETE /api/cp/1?project_id=1
```

**GET /api/cp 返回字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | CP ID |
| project_id | int | 项目 ID |
| feature | string | Feature |
| sub_feature | string | Sub-Feature |
| cover_point | string | Cover Point |
| cover_point_details | string | 详情 |
| comments | string | 备注 |
| created_at | string | 创建时间 |
| **priority** | string | **优先级 (P0/P1/P2)** |
| **coverage** | float | **覆盖率百分比 (0-100)** |
| **coverage_detail** | string | **详情格式: "PASS/总数"** |

**GET /api/cp/{id}/tcs 返回示例**（v0.6.2 新增）:
```json
{
  "cp_id": 1,
  "connected_tcs": [
    {
      "id": 10,
      "test_name": "TC_复位测试_001",
      "status": "PASS"
    },
    {
      "id": 15,
      "test_name": "TC_时钟测试_002",
      "status": "CODED"
    }
  ]
}
```

### 4.6 Test Cases

| 方法 | 路径 | 功能 |
|------|------|------|
| **GET** | **`/api/tc?project_id=1&status=...&dv_milestone=...`** | **获取 TC 列表（支持过滤，v0.6.2）** |
| GET | `/api/tc/{id}` | 获取 TC 详情（需 project_id） |
| POST | `/api/tc` | 创建 TC |
| PUT | `/api/tc/{id}` | 更新 TC 信息（**不含状态**，需 project_id） |
| DELETE | `/api/tc/{id}` | 删除 TC（需 project_id） |
| POST | `/api/tc/{id}/status` | 更新状态（**含日期自动记录**，需 project_id） |
| POST | `/api/tc/batch/status` | 批量更新状态（需 project_id） |
| POST | `/api/tc/batch/target_date` | 批量更新 Target Date（需 project_id） |
| POST | `/api/tc/batch/dv_milestone` | 批量更新 DV Milestone（需 project_id） |

**GET /api/tc 过滤参数**（v0.6.2 新增）:

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `project_id` | int | 项目 ID（必填） | `?project_id=1` |
| `status` | string | Status 过滤（单选） | `?status=PASS` |
| `dv_milestone` | string | DV Milestone 过滤（单选） | `?dv_milestone=DV1.0` |
| `owner` | string | Owner 过滤（动态填充） | `?owner=TestEng1` |
| `category` | string | Category 过滤（动态填充） | `?category=Sanity` |

**请求示例**（v0.6.2）:
```
# 获取所有 TC
GET /api/tc?project_id=1

# 按 Status 过滤
GET /api/tc?project_id=1&status=PASS

# 按 DV Milestone 过滤
GET /api/tc?project_id=1&dv_milestone=DV1.0

# 组合过滤
GET /api/tc?project_id=1&status=PASS&dv_milestone=DV1.0&owner=TestEng1
```

**API 参数说明**:
- **GET /api/tc**: 通过查询参数传递 `project_id`，例如: `/api/tc?project_id=1`
- **GET /api/tc/{id}**: 通过查询参数传递 `project_id`，例如: `/api/tc/1?project_id=1`
- **POST /api/tc**: 在请求体中传递 `project_id`
- **PUT /api/tc/{id}**: 在请求体中必须包含 `project_id`，**不能用于更新状态**
- **DELETE /api/tc/{id}**: 通过查询参数传递 `project_id`，例如: `/api/tc/1?project_id=1`
- **POST /api/tc/{id}/status**: 在请求体中必须包含 `project_id` 和 `status`

**PUT /api/tc/{id} 请求体**:
```json
{
    "project_id": 1,
    "testbench": "TB_A",
    "category": "Category",
    "owner": "Owner",
    "test_name": "TC_A",
    "scenario_details": "Scenario",
    "target_date": "2026-02-15",
    "dv_milestone": "DV0.5",
    "checker_details": "",
    "coverage_details": "",
    "comments": "",
    "connections": [1, 2, 3]
}
```
> **注意**: `connections` 字段用于设置 TC 关联的 CP ID 列表。调用时会覆盖原有的关联关系。

**POST /api/tc/{id}/status 请求体**:
```json
{
    "project_id": 1,
    "status": "PASS"
}
```

**DELETE /api/tc/{id} 请求示例**:
```
DELETE /api/tc/1?project_id=1
```

**GET /api/tc 返回字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | TC ID |
| project_id | int | 项目 ID |
| dv_milestone | string | DV 里程碑 |
| testbench | string | 测试台 |
| category | string | 类别 |
| owner | string | 负责人 |
| test_name | string | 测试名称 |
| status | string | 状态 |
| **target_date** | string | **目标完成日期** |
| **coded_date** | string | **CODED 日期** |
| **fail_date** | string | **FAIL 日期** |
| **pass_date** | string | **PASS 日期** |
| **removed_date** | string | **REMOVED 日期** |
| **connected_cps** | array | **关联的 CP ID 列表** |

> **说明**: `connected_cps` 是 TC 详情 API (`GET /api/tc/{id}`) 的返回字段，表示该 Test Case 关联的 Cover Points。

### 4.7 统计

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/stats` | 获取统计数据（**排除 REMOVED**） |

#### 4.5.1 请求示例

```
GET /api/stats?project_id=1
```

#### 4.5.2 返回示例

```json
{
  "total_cp": 10,
  "total_tc": 50,
  "open_tc": 15,
  "coded_tc": 20,
  "fail_tc": 5,
  "pass_tc": 10,
  "pass_rate": "20.0%",
  "coverage": "45.5%"
}
```

#### 4.5.3 返回字段说明

| 字段 | 类型 | 含义 | 计算方式 |
|------|------|------|----------|
| `total_cp` | int | Cover Points 总数 | CP 表记录数 |
| `total_tc` | int | Test Cases 总数 | 排除 REMOVED 状态的所有 TC |
| `open_tc` | int | 待开发/待执行 | status='OPEN' |
| `coded_tc` | int | 已开发完成 | status='CODED' |
| `fail_tc` | int | 测试失败 | status='FAIL' |
| `pass_tc` | int | 测试通过 | status='PASS' |
| `pass_rate` | string | TC 通过率 | `pass_tc / total_tc × 100%` |
| `coverage` | string | CP 覆盖率 | 所有 CP 关联 TC PASS 比例的**平均值** |

#### 4.5.4 Coverage 计算规则（重点）

Coverage 是**所有 Cover Point 覆盖率**的平均值：

```
coverage = (CP1覆盖率 + CP2覆盖率 + ... + CPn覆盖率) / n
```

**每个 CP 的覆盖率计算**：

| 关联 TC 状态 | 覆盖率 |
|-------------|--------|
| 全部 PASS | **100%** |
| 部分 PASS | **PASS 数量 / 关联总数 × 100%** |
| 无关联 TC | **0%** |

**示例计算**：
- CP1: 关联 4 个 TC，3 个 PASS → 75%
- CP2: 关联 2 个 TC，2 个 PASS → 100%
- CP3: 关联 0 个 TC → 0%
- **Coverage = (75% + 100% + 0%) / 3 = 58.3%**

#### 4.5.5 统计规则

| 规则 | 说明 |
|------|------|
| REMOVED 不计入 Total | `total_tc` 排除 REMOVED 状态的 TC |
| REMOVED 不参与计算 | PASS Rate 和 Coverage 计算均排除 REMOVED |
| 无关联 CP | Coverage 按 0% 计算 |

### 4.8 导入导出

| 方法 | 路径 | 功能 |
|------|------|------|
| **GET** | **`/api/import/template?type=cp\|tc`** | **下载导入模板** |
| **POST** | **`/api/import`** | **执行导入** |
| **GET** | **`/api/export?project_id=1&type=cp\|tc&format=xlsx\|csv`** | **导出数据** |

#### 4.7.1 GET /api/import/template

下载导入模板文件。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | ✅ | cp 或 tc |

**响应**: 文件下载 (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

#### 4.7.2 POST /api/import

执行数据导入。

**请求体**:
```json
{
  "project_id": 1,
  "type": "cp",
  "file_data": "base64编码的Excel文件内容"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | ✅ | 项目 ID |
| type | string | ✅ | cp 或 tc |
| file_data | string | ✅ | Base64 编码的文件内容 |

**成功响应**:
```json
{
  "success": true,
  "imported": 10,
  "failed": 0,
  "errors": []
}
```

#### 4.7.3 GET /api/export

导出项目数据。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | ✅ | 项目 ID |
| type | string | ✅ | cp 或 tc |
| format | string | ✅ | xlsx 或 csv |

**响应**: 文件下载

**文件名格式**: `{项目名}_{CP/TC}_{日期}.xlsx`

### 4.8 Progress Charts API (v0.8.1/v0.8.2 新增)

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| GET | `/api/progress/<project_id>` | 获取进度数据（含计划/实际曲线） | 登录 |
| POST | `/api/progress/<project_id>/snapshot` | 手动触发快照 | admin |
| POST | `/api/cron/progress-snapshot` | 定时任务快照 | Cron Token |
| GET | `/api/progress/<project_id>/snapshots` | 获取快照列表 | 登录 |
| DELETE | `/api/progress/snapshots/<id>` | 删除快照 | admin |
| GET | `/api/progress/<project_id>/export` | 导出进度数据 | 登录 |

### 4.9 FC (Functional Coverage) API (v0.11.0 新增)

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/fc` | 获取 FC 列表（支持筛选） | ✅ 已实现 |
| POST | `/api/fc/import` | 导入 FC (CSV) | ✅ 已实现 |
| GET | `/api/fc/export` | 导出 FC (CSV) | ✅ 已实现 |
| PUT | `/api/fc/batch` | 批量更新 FC items | ✅ 已实现 |
| GET | `/api/fc-cp-association` | 获取 FC-CP 关联列表 | ✅ 已实现 |
| POST | `/api/fc-cp-association` | 创建 FC-CP 关联 | ✅ 已实现 |
| DELETE | `/api/fc-cp-association` | 删除 FC-CP 关联 | ✅ 已实现 |
| POST | `/api/fc-cp-association/import` | 导入 FC-CP 关联 (CSV) | ✅ 已实现 |

### 4.10 Dashboard API (v0.11.0 新增)

| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| GET | `/api/dashboard/stats` | 获取 Dashboard 统计数据 | 登录 |

#### 4.8.1 GET /api/progress/<project_id>

获取完整进度数据，包含计划曲线和实际曲线。

**响应**:
```json
{
    "project_id": 1,
    "project_name": "SOC_DV",
    "start_date": "2026-01-06",
    "end_date": "2026-04-18",
    "planned": [
        {"week": "2026-01-06", "coverage": 0},
        {"week": "2026-01-13", "coverage": 10}
    ],
    "actual": [
        {"week": "2026-01-06", "coverage": 0},
        {"week": "2026-01-13", "coverage": 5}
    ]
}
```

#### 4.8.2 POST /api/progress/<project_id>/snapshot

手动触发快照采集。

**响应**:
```json
{
    "success": true,
    "snapshot": {
        "id": 1,
        "snapshot_date": "2026-03-04",
        "actual_coverage": 45.5,
        "tc_pass_count": 20,
        "tc_total": 50,
        "cp_covered": 12,
        "cp_total": 30
    }
}
```

#### 4.8.3 GET /api/progress/<project_id>/snapshots

获取快照列表。

**响应**:
```json
{
    "snapshots": [
        {
            "id": 1,
            "snapshot_date": "2026-02-01",
            "actual_coverage": 45.5,
            "tc_pass_count": 20,
            "tc_total": 50,
            "cp_covered": 12,
            "cp_total": 30
        }
    ]
}
```

---

### 4.9 API 使用说明

#### 4.7.1 为什么需要 project_id？

Tracker 使用**独立数据库架构**，每个项目拥有独立的 `.db` 文件。因此，所有涉及项目数据的 API 操作都需要知道操作的是哪个项目的数据。

**project_id 传递方式**:
| API 类型 | 传递方式 | 示例 |
|----------|----------|------|
| GET (列表) | 查询参数 | `GET /api/tc?project_id=1` |
| POST (创建) | 请求体 JSON | `{"project_id": 1, ...}` |
| PUT (更新) | 请求体 JSON | `{"project_id": 1, ...}` |
| DELETE | 查询参数 | `DELETE /api/tc/1?project_id=1` |

#### 4.7.2 错误处理

| 状态码 | 含义 | 常见原因 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 缺少 project_id、参数格式错误 |
| 404 | 资源不存在 | 项目不存在、CP/TC ID 不存在 |
| 500 | 服务器错误 | 数据库错误 |

**常见错误响应**:
```json
// 缺少 project_id
{"error": "需要指定项目"}

// 项目不存在
{"error": "项目不存在"}

// CP/TC 不存在
{"error": "Cover Point 不存在"}

/**
 * Test Case 不存在
{"error": "Test Case 不存在"}
```

---

## 5. 数据库设计

### 5.1 数据库结构

每个项目拥有独立的 SQLite 数据库文件 (`*.db`)：

```
{项目名}.db
├── cover_point           # Cover Points 表 (v0.6.0+ 含 priority)
├── test_case            # Test Cases 表 (v0.6.0+ 含新字段)
├── tc_cp_connections    # TC-CP 关联表
└── tracker_version      # 版本表 (v0.3+)
```

### 5.2 版本表

**tracker_version 表：**

```sql
CREATE TABLE tracker_version (
    version TEXT PRIMARY KEY,
    created_at TEXT,
    migrated_at TEXT
);
```

### 5.3 v0.6.0 字段变更

#### Test Case 表新增字段 (v0.6.0)

```sql
-- DV Milestone 字段
ALTER TABLE test_case ADD COLUMN dv_milestone VARCHAR(10) DEFAULT NULL;

-- Target Date 字段
ALTER TABLE test_case ADD COLUMN target_date DATE DEFAULT NULL;

-- Status 日期字段
ALTER TABLE test_case ADD COLUMN coded_date DATE DEFAULT NULL;
ALTER TABLE test_case ADD COLUMN fail_date DATE DEFAULT NULL;
ALTER TABLE test_case ADD COLUMN pass_date DATE DEFAULT NULL;
ALTER TABLE test_case ADD COLUMN removed_date DATE DEFAULT NULL;
```

#### Cover Point 表新增字段 (v0.6.0)

```sql
-- Priority 字段
ALTER TABLE cover_point ADD COLUMN priority VARCHAR(3) DEFAULT 'P0';
```

#### 数据迁移 (v0.6.0)

```sql
-- 为已有数据填充日期
UPDATE test_case SET pass_date = updated_at WHERE status = 'PASS';
UPDATE test_case SET coded_date = updated_at WHERE status = 'CODED';
UPDATE test_case SET fail_date = updated_at WHERE status = 'FAIL';

-- DV Milestone 默认值
UPDATE test_case SET dv_milestone = 'DV1.0' WHERE dv_milestone IS NULL;

-- CP Priority 默认值
UPDATE cover_point SET priority = 'P0' WHERE priority IS NULL;
```

### 5.4 v0.8.2 新增表

#### project_progress 表 (v0.8.2 新增，v0.10.0 扩展)

```sql
CREATE TABLE project_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    actual_coverage REAL,
    tc_pass_count INTEGER,
    tc_total INTEGER,
    cp_covered INTEGER,
    cp_total INTEGER,
    p0_coverage REAL,
    p1_coverage REAL,
    p2_coverage REAL,
    p3_coverage REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    updated_by TEXT,
    UNIQUE(project_id, snapshot_date)
);
```

| 字段 | 类型 | 说明 |
|------|------|------|
| project_id | INTEGER | 项目 ID |
| snapshot_date | DATE | 快照日期 |
| actual_coverage | REAL | 实际覆盖率 (%) |
| tc_pass_count | INTEGER | Pass 状态 TC 数 |
| tc_total | INTEGER | 总 TC 数 |
| cp_covered | INTEGER | 已覆盖 CP 数 |
| cp_total | INTEGER | 总 CP 数 |
| **p0_coverage** | REAL | **P0 Priority 覆盖率 (v0.10.0 新增)** |
| **p1_coverage** | REAL | **P1 Priority 覆盖率 (v0.10.0 新增)** |
| **p2_coverage** | REAL | **P2 Priority 覆盖率 (v0.10.0 新增)** |
| **p3_coverage** | REAL | **P3 Priority 覆盖率 (v0.10.0 新增)** |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TEXT | 更新时间 |
| updated_by | TEXT | 更新人 |

### 5.5 v0.11.0 新增表

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
    status TEXT DEFAULT 'missing' CHECK (status IN ('missing', 'ready')),
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
    UNIQUE (cp_id, fc_id)
);
```

#### project 表新增字段

```sql
ALTER TABLE project ADD COLUMN coverage_mode TEXT DEFAULT 'tc_cp';
```

### 5.6 v0.2 到 v0.3 迁移

现有用户需要执行迁移：

```bash
# 1. 检查兼容性
python3 scripts/compat_check.py shared/data/

# 2. 执行迁移
python3 scripts/migrate_v02_to_v03.py --source data/tracker.db --target shared/data/

# 3. 验证
python3 scripts/compat_check.py shared/data/
```

---

## 6. 版本管理

### 6.1 Git 分支策略

#### 6.1.1 分支结构

```
main (稳定代码，对应 /release/tracker/current)
│
├── develop (开发分支，存放 dev/ 代码)
│   ├── feature/* (功能开发分支，源自 develop，合并回 develop)
│   ├── release/* (发布分支，源自 develop，合并回 main 和 develop)
│   └── hotfix/* (紧急修复分支，源自 main，合并回 main 和 develop)
│
└── tags (在 main 分支上创建)
    ├── v0.3.0
    ├── v0.3.1
    └── v0.3.2

/release/tracker/                         ← 发布目录（由 release.py 生成）
├── v0.3.1/                               ← 历史版本
├── v0.3.2/                               ← 当前版本
└── current → v0.3.2/                    ← 软链接指向当前运行版本
```

#### 6.1.2 分支说明

| 分支 | 命名规则 | 来源 | 合并到 | 用途 |
|------|----------|------|--------|------|
| **main** | `main` | - | - | 生产环境代码（Git） |
| **develop** | `develop` | main | - | 开发主分支（存放 dev/ 代码） |
| **feature** | `feature/xxx` | develop | develop | 新功能开发 |
| **release** | `release/v0.x.x` | develop | main + develop | 发布准备 |
| **hotfix** | `hotfix/v0.x.x` | main | main + develop | 紧急修复 |

**发布目录（由 release.py 生成，不纳入 Git）：**

| 目录 | 说明 |
|------|------|
| `/release/tracker/v{version}/` | 发布版本目录 |
| `/release/tracker/current` | 软链接，指向当前运行版本 |

**说明：**
- Git 仓库只维护 `dev/` 代码
- 发布时由 `release.py` 生成到 `/release/tracker/v{version}/`
- systemd 服务指向 `/release/tracker/current`

#### 6.1.3 工作流程

**日常开发（dev 版本）：**
```bash
# 创建功能分支
git checkout develop
git checkout -b feature/user-auth

# 开发完成，合并回 develop
git checkout develop
git merge feature/user-auth --no-ff -m "feat: 添加用户认证功能"
git branch -d feature/user-auth
```

**版本发布：**
```bash
# 创建发布分支
git checkout develop
git checkout -b release/v0.3.3

# 测试完成后合并：
git checkout main
git merge release/v0.3.3 --no-ff -m "release: v0.3.3"
git tag -a v0.3.3 -m "Release v0.3.3"

git checkout develop
git merge release/v0.3.3 --no-ff

git branch -d release/v0.3.3
```

**Hotfix 紧急修复（用户反馈后）：**
```bash
# 场景：正式版发现紧急 bug
git checkout main
git checkout -b hotfix/v0.3.2-urgent

# 修复 bug
git add .
git commit -m "hotfix: 修复项目切换数据丢失问题"

# 合并到 main（立即发布）
git checkout main
git merge hotfix/v0.3.2-urgent --no-ff -m "hotfix: v0.3.2-urgent"
git tag -a v0.3.2 -m "Hotfix v0.3.2"

# 同步到 develop（保持一致）
git checkout develop
git merge hotfix/v0.3.2-urgent --no-ff

git branch -d hotfix/v0.3.2-urgent
```

#### 6.1.4 .gitignore 配置

```bash
# /projects/management/tracker/.gitignore

# 数据目录（不版本控制）
shared/data/
user_data/
test_data/
*.db

# 测试输出
test-results/
playwright-report/
htmlcov/

# Python
__pycache__/
*.pyc
.pytest_cache/
.coverage

# IDE
.vscode/
.idea/

# 系统文件
.DS_Store
```

---

### 6.2 发布流程

```
日常开发 → 功能测试 → 创建发布分支 → 集成测试 → 合并到 main → 打标签 → 执行 release.py → 切换软链接 → 重启服务
```

**自动完成以下步骤：**

1. **代码检查** - 测试是否全部通过
2. **版本号更新** - 更新版本文件中的版本号
3. **兼容性检查** - 检查用户数据库版本，如需迁移则执行迁移脚本
4. **创建发布版本** - 复制 dev/ 代码到 `/release/tracker/v{version}/`
5. **配置数据链接** - 创建 `data → ../../shared/data/user_data` 符号链接
6. **切换 current 软链接** - `/release/tracker/current` 指向新版本
7. **更新 systemd** - 服务配置指向新目录
8. **重启服务** - 自动重启 tracker 服务
9. **生成发布报告** - 创建 `/release/tracker/v{version}/RELEASE_NOTES.md`

---

### 6.3 发布命令

```bash
cd /projects/management/tracker

# 演练模式（不实际执行）
python3 scripts/release.py --dry-run

# 实际发布
python3 scripts/release.py --version v0.3.3 --migrate --force

# 回滚（切换到上一版本）
python3 scripts/release.py --rollback --force
```

**发布目录：**
```
/release/tracker/
├── v0.3.1/
├── v0.3.2/
└── current → v0.3.2  ← systemd 指向这里
```

---

### 6.4 发布流程详解

```
1. 检查数据目录结构
   └── 验证 user_data 和 test_data 存在

2. 创建发布版本
   └── /release/tracker/v{version}/（从 dev/ 复制，不包括 data、tests）

3. 配置数据符号链接
   └── /release/tracker/v{version}/data → ../../shared/data/user_data

4. 切换 current 软链接
   └── /release/tracker/current → /release/tracker/v{version}/

5. 更新 systemd 服务
   └── /etc/systemd/system/tracker.service

6. 重启服务
   └── sudo systemctl restart tracker

7. 验证服务状态
   └── 检查服务是否正常运行
```

**发布后访问：** http://10.0.0.8:8080

**发布目录结构：**
```
/release/tracker/
├── v0.3.1/              ← 历史版本
│   ├── server.py
│   ├── app/
│   ├── index.html
│   ├── data → ../../shared/data/user_data
│   └── RELEASE_NOTES.md
│
├── v0.3.2/              ← 当前版本
│   └── ...
│
└── current → v0.3.2/    ← 软链接，systemd 指向这里
```

---

### 6.5 发布摘要模板

发布脚本会自动生成 `/release/tracker/v{version}/RELEASE_NOTES.md`，包含以下内容：

```markdown
# Tracker v{版本号} 发布报告

> **版本**: {版本号} | **发布日期**: {日期} | **发布时间**: {时间}

---

## 发布摘要

| 项目 | 状态 |
|------|------|
| 版本 | {版本号} |
| 源版本 | dev |
| 目标版本 | stable |
| 兼容性检查 | ✅ 全部通过 |
| 代码发布 | ✅ dev → stable |

---

## 数据目录结构

```
shared/data/
├── user_data/       # 正式版数据 (stable 使用)
│   └── 2 个项目数据库
│
└── test_data/      # 测试数据 (dev 使用)
    └── 测试项目数据库
```

---

## 数据统计

| 指标 | 值 |
|------|-----|
| 用户项目数量 | 2 |
| 数据库文件 | 2 个 |

---

## 访问地址

| 环境 | 地址 | 端口 |
|------|------|------|
| 内网 | http://10.0.0.8 | 8080 |
| 外网 | http://外网IP | 8080 |

---

## 服务管理

```bash
# 重启服务（发布后需要）
sudo systemctl restart tracker

# 查看状态
sudo systemctl status tracker

# 查看日志
journalctl -u tracker -f
```

---

## 版本回滚

如需回滚到上一版本：

```bash
cd /projects/management/tracker
python3 scripts/release.py --rollback --force
```

**注意：** 回滚只恢复代码文件，用户数据不会改变。

---

## 备份位置

发布前已自动备份：

```
stable/backup_YYYYMMDD_HHMMSS
```

---

**文档生成时间**: {日期} {时间}
```

---

### 6.6 回滚方案

如果新版本有问题，执行回滚（切换软链接）：

```bash
cd /projects/management/tracker
python3 scripts/release.py --rollback --force
```

**回滚过程：**

1. 查找可用的历史版本
2. 切换 `current` 软链接到上一版本
3. 更新 systemd 服务配置
4. 重启 tracker 服务
5. 验证服务状态

**手动回滚（如果需要）：**

```bash
# 查看可用版本
ls -la /release/tracker/

# 切换到指定版本
sudo rm /release/tracker/current
sudo ln -s /release/tracker/v0.3.1 /release/tracker/current
sudo systemctl restart tracker
```

**⚠️ 注意：**
- 用户数据（user_data）独立存储，**不会改变**，无需回滚
- 回滚只是切换软链接，非常快速
- 历史版本目录保留，可以随时回滚

---

## 7. 测试计划

### 7.1 测试类型

| 测试类型 | 覆盖范围 | 通过标准 |
|----------|----------|----------|
| 单元测试 | API 接口、独立数据库 | 全部通过 |
| 集成测试 | 项目 + CP + TC 关联 | 全部通过 |
| 版本迁移 | v0.2 → v0.3 数据迁移 | 数据完整 |
| 手动测试 | 前端交互、界面显示 | 用户验收 |

### 7.2 目录结构测试

| ID | 测试项 | 预期结果 | 状态 |
|----|--------|----------|------|
| T001 | stable/data 是符号链接 | 指向 shared/data | ✅ |
| T002 | dev/data 是符号链接 | 指向 shared/data | ✅ |
| T003 | shared/data/ 独立存在 | 不随代码发布改变 | ✅ |
| T004 | stable/ 代码可独立启动 | 访问 http://localhost:8080 | ✅ |
| T005 | dev/ 代码可独立启动 | 访问 http://localhost:8081 | ✅ |

### 7.3 API 测试用例

| ID | API | 测试步骤 | 预期结果 |
|----|-----|----------|----------|
| A001 | GET /api/version | 获取版本信息 | 返回版本信息 |
| A002 | POST /api/projects | 创建项目 | 项目创建成功，生成独立 .db |
| A003 | GET /api/projects | 获取项目列表 | 返回所有项目 |
| A004 | POST /api/cp | 创建 CP | CP 创建成功 |
| A005 | GET /api/cp | 获取 CP 列表 | 返回 CP 列表 |
| A006 | POST /api/tc | 创建 TC（默认 OPEN） | TC 创建成功 |
| A007 | POST /api/tc/{id}/status | 更新状态 | 状态切换，完成日期更新 |
| A008 | GET /api/stats | 获取统计 | 返回统计数据 |

### 7.4 版本迁移测试

| ID | 测试项 | 预期结果 |
|----|--------|----------|
| M001 | 加载 v0.2 数据 | 正确读取 project, cp, tc 表 |
| M002 | 生成独立数据库 | 每个项目一个 .db 文件 |
| M003 | 创建 projects.json | 项目列表正确 |
| M004 | 数据完整性 | CP, TC 数量一致 |
| M005 | 关联关系 | tc_cp_connections 正确 |

### 7.5 发布流程测试

| ID | 测试项 | 预期结果 |
|----|--------|----------|
| R001 | 代码复制 | stable/ 代码被更新 |
| R002 | 数据保留 | shared/data/ 不变 |
| R003 | 符号链接 | stable/data 指向 shared/data |
| R004 | 回滚功能 | 可恢复到上一版本 |

---

## 8. 部署说明

### 8.1 快速开始

**启动正式版：**

```bash
cd /projects/management/tracker/stable
python3 server.py
# 访问 http://localhost:8080
```

**启动测试版：**

```bash
cd /projects/management/tracker/dev
bash start_server_test.sh
# 访问 http://localhost:8081
```

### 8.2 技术栈

| 层级 | 技术 | 版本要求 |
|------|------|----------|
| 前端 | HTML5 + Vanilla JavaScript | ES6+ |
| 后端 | Python Flask | 最新 |
| 数据库 | SQLite | 3.x |
| 部署 | systemd（正式版） | - |
| 测试 | pytest | - |

### 8.3 systemd 部署（正式版）

**说明：** systemd 服务指向 `/release/tracker/current`，由 `release.py` 自动更新配置。

```ini
# /etc/systemd/system/tracker.service
# （由 release.py 自动生成，无需手动配置）

[Unit]
Description=Chip Verification Tracker
After=network.target

[Service]
User=root
WorkingDirectory=/release/tracker/current
ExecStart=/usr/local/bin/gunicorn --config /release/tracker/current/gunicorn.conf.py wsgi:app
Restart=always
RestartSec=10
StandardOutput=append:/var/log/tracker.log
StandardError=append:/var/log/tracker_error.log

[Install]
WantedBy=multi-user.target
```

**常用命令：**

```bash
# 查看状态
sudo systemctl status tracker

# 重启服务
sudo systemctl restart tracker

# 查看日志
journalctl -u tracker -f
```

---

## 9. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.1 | 2026-02-03 | 初始版本：基础 CRUD + JSON 存储 |
| v0.2 | 2026-02-03 | **重大更新**：多项目、新字段结构、备份恢复 |
| v0.3 | 2026-02-04 | **架构重构**：代码隔离、数据共享、版本迁移 |
| v0.3.1 | 2026-02-04 | **数据隔离**：user_data/test_data 分离，测试不碰用户数据 |
| v0.4 | 2026-02-05 | **简化架构**：Git 只维护 dev/，发布到 /release/tracker/ |
| v0.5.0 | 2026-02-06 | **功能增强**：界面优化、测试报告、发布准备脚本 |
| v0.5.1 | 2026-02-07 | **Bug 修复**：API 和界面问题修复 |
| **v0.6.0** | **2026-02-08** | **第一阶段功能增强**：Status 日期、Target Date、REMOVED、批量修改、DV Milestone、CP Priority |
| **v0.6.1** | **2026-02-09** | **第二阶段功能增强**：Status 粗体、CP 过滤、备份路径自定义、ESLint 检查 |
| **v0.6.2** | **2026-02-10** | **第三阶段功能增强**：CP 详情下拉、TC 过滤、Bug 修复（BUG-027~040） |
| **v0.7.0** | **2026-02-16** | **导入导出功能**：CP/TC 批量导入导出、Excel/CSV 支持、模板下载 |
| **v0.7.1** | **2026-02-25** | **用户认证模块**：登录/访问控制、Session 管理、角色权限（admin/user/guest）、密码安全 |
| **v0.8.0** | **2026-03-01** | **进度图表基础**：项目起止日期、Progress Charts 页面框架、Chart.js 集成、加载失败降级处理 |
| **v0.8.1** | **2026-03-02** | **计划曲线**：基于 TC target_date 的预期覆盖率曲线、时间段选择器、Chart.js CDN Fallback |
| **v0.8.2** | **2026-03-04** | **实际曲线与快照**：绿色实线实际曲线、手动/定时快照采集、快照管理、导出功能 |
| **v0.8.3** | **2026-03-04** | **测试便利性**：创建项目自动创建测试用户、项目日期必填验证、前端常量管理 |
| **v0.9.0** | **2026-03-05** | **前端界面优化**：设计系统 CSS 变量（紫色主题 Vercel/Linear 风格）、组件样式重构（Header/Tabs/Table/Modal）、微交互动画、兼容映射 |
| **v0.9.1** | **2026-03-08** | **用户反馈功能**：反馈 API + UI、switchTab 函数改进、常量管理优化 |
| **v0.9.2** | **2026-03-17** | **关联状态与滚动优化**：CP/TC关联状态可视化（红色+🔗图标）、独立滚动条+表头sticky+高度自适应、TC过滤单行布局、CP未关联过滤、admin强制改密码前端、Manual更新 |
| **v0.10.0** | **2026-03-20** | **Priority 过滤功能**：图表支持按 CP Priority 过滤、新增 p0-p3_coverage 字段 |
| **v0.10.1** | **2026-03-21** | **批量创建用户**：POST /api/users/batch 批量创建普通用户 |
| **v0.10.2** | **2026-03-23** | **Intro 引导页**：首次访问引导页、5 slides 介绍功能 |
| **v0.11.0** | **2026-04-03** | **FC/Dashboard**：FC 功能、CP Dashboard、定时快照修复、覆盖率算法修复 |

### v0.8.3 详细变更

1. **CP 导入功能**：
   - 按钮位置：CP 页面工具栏 [+ 添加 CP] 旁边
   - 支持 Excel (.xlsx) 和 CSV 文件格式
   - 提供下载 CP 模板功能
   - 必填字段检查：Feature、Cover Point
   - 重名检测：同一项目内重复 Cover Point 跳过
   - 导入失败时事务回滚
   - 导入成功后显示成功数量并刷新列表

2. **TC 导入功能**：
   - 按钮位置：TC 页面工具栏 [+ 添加 TC] 旁边
   - 支持 Excel (.xlsx) 和 CSV 文件格式
   - 提供下载 TC 模板功能
   - 必填字段检查：TestBench、Test Name
   - 重名检测：同一项目内重复 Test Name 跳过
   - 导入失败时事务回滚
   - 导入成功后显示成功数量并刷新列表

3. **CP 导出功能**：
   - 按钮位置：CP 页面工具栏 [导入 CP] 旁边
   - 支持 Excel (.xlsx) 和 CSV 格式导出
   - 默认格式为 Excel
   - 显示当前项目名称和记录数量
   - 文件名格式：{项目名}_CP_{日期}.xlsx

4. **TC 导出功能**：
   - 按钮位置：TC 页面工具栏 [导入 TC] 旁边
   - 支持 Excel (.xlsx) 和 CSV 格式导出
   - 默认格式为 Excel
   - 显示当前项目名称和记录数量
   - 文件名格式：{项目名}_TC_{日期}.xlsx

5. **新增 API 接口**：

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/import/template?type=cp\|tc` | 下载导入模板 |
| POST | `/api/import` | 执行导入 |
| GET | `/api/export?project_id=1&type=cp\|tc&format=xlsx\|csv` | 导出数据 |

6. **界面修复**：
   - 项目选择框宽度固定为 200px

2. **Target Date 字段**：
   - TC 表格显示 Target Date 列
   - 支持单个和批量修改 Target Date

3. **REMOVED 状态**：
   - Status 下拉框新增 REMOVED 选项
   - REMOVED 状态的 TC 显示删除线样式
   - REMOVED 不计入 Total 和 Pass Rate 统计
   - REMOVED 时自动清除与 CP 的关联

4. **批量修改功能**：
   - TC 表格显示复选框列
   - 支持批量更新状态、Target Date、DV Milestone
   - 支持全选/取消全选

5. **DV Milestone 字段**：
   - TC 表格显示 DV Milestone 列
   - 支持选择 DV0.3/DV0.5/DV0.7/DV1.0
   - 默认值 DV1.0

6. **CP Priority 字段**：
   - CP 表格显示 Priority 列
   - 支持选择 P0/P1/P2
   - 默认值 P0

### v0.6.1 详细变更

1. **Status 颜色粗体显示**：
   - OPEN 状态：灰色粗体 (#6b7280)
   - CODED 状态：蓝色粗体 (#3b82f6)
   - FAIL 状态：红色粗体 (#ef4444)
   - PASS 状态：绿色粗体 (#22c55e)
   - REMOVED 状态：灰色粗体删除线 (#9ca3af)

2. **CP 过滤功能**：
   - Feature 下拉过滤：自动填充当前项目的 Feature 选项
   - Priority 下拉过滤：支持 P0/P1/P2
   - 组合过滤：支持同时按 Feature 和 Priority 过滤
   - API 支持 `feature` 和 `priority` 查询参数

3. **备份恢复自定义路径**：
   - 新增 POST /api/projects/restore/upload API
   - 支持 multipart/form-data 上传备份文件
   - 保留原有的按文件名恢复方式

4. **前端代码质量改进**：
   - 添加 ESLint 检查配置
   - 添加 Playwright 冒烟测试（控制台错误检测）
   - 添加 check_frontent.sh 快速检查脚本

### v0.6.2 详细变更

1. **CP 详情下拉**：
   - 操作栏新增"详情"按钮
   - 点击展开 CP 完整信息和关联 TC 列表
   - 详情面板显示 cover_point_details、comments
   - 关联 TC 列表显示 ID、Test Name、Status
   - 新增 API: `GET /api/cp/{id}/tcs`

2. **TC 过滤**：
   - 过滤面板显示在 TC 列表上方
   - Status 单选过滤（多选改为单选）
   - DV Milestone 单选过滤
   - Owner 动态过滤（从 TC 列表自动填充）
   - Category 动态过滤
   - 显示过滤后的记录数量
   - 重置过滤条件
   - API 支持 `status`、`dv_milestone`、`owner`、`category` 参数

3. **Bug 修复（BUG-027~036）**：
   - BUG-027: 展开所有 CP 详情时 TC 数据不加载
   - BUG-028: TC 过滤重置后列表不刷新
   - BUG-029: TC 过滤重置代码存在无效语句
   - BUG-030: CP 详情关联 TC 显示错误
   - BUG-031: TC Priority 过滤不需要（TC 没有 priority 字段）
   - BUG-032: TC Owner/Category 过滤选项不动态加载
   - BUG-033: TC Status/DV Milestone 需要单选下拉框
   - BUG-034: TC Status/DV Milestone 缺少全部选项
   - BUG-035: TC DV Milestone 过滤选项不动态加载
   - BUG-036: projectSelector ID 拼写错误

### v0.9.0 详细变更

1. **设计系统 CSS 变量**：
   - 新建 `dev/static/css/design-system.css`
   - 颜色系统：主色 #4f46e5、成功/警告/错误/信息色、背景色、文字色
   - 字体系统：系统字体兜底（-apple-system, BlinkMacSystemFont, Segoe UI, Microsoft YaHei）
   - 间距系统：基于 4px 基准（--space-1 到 --space-12）
   - 圆角系统：--radius-sm/-/-lg/-xl/-full
   - 阴影系统：--shadow-sm/-/-md/-lg/-xl

2. **核心组件样式重构**：
   - Header：紫色渐变背景 (#4f46e5 → #4338ca)
   - Tabs：透明背景 + 紫色底部指示器
   - Buttons：主按钮紫色、悬停阴影动画
   - Toolbar：使用 CSS 变量

3. **数据展示组件**：
   - Table：白色卡片背景、圆角边框、悬停效果
   - Stats Bar：统计数字紫色 (#4f46e5)
   - Filter Panel：白色卡片背景、圆角边框

4. **表单组件优化**：
   - Input/Select：聚焦时紫色边框 + 阴影
   - Modal：紫色头部背景、圆角边框、scaleIn 动画

5. **动画增强**：
   - 按钮悬停：translateY(-2px) + shadow
   - 按钮点击：scale(0.98)
   - 卡片悬浮：translateY(-4px) + shadow-lg
   - 模态框：scaleIn 缩放淡入
   - 尊重用户偏好：prefers-reduced-motion

6. **app_constants.js 整合**：
   - 颜色使用 CSS 变量 + 固定值兜底
   - 修复 N/A 键名语法错误

7. **样式迁移执行**：
   - 从 index.html 移除 68 行冗余样式
   - 添加状态徽章兼容映射（.status-* → .badge-*）
   - 添加模态框兼容映射

8. **Bug 修复**：
   - BUG-076: design-system.css 无法加载（移动到 static/css/）
   - BUG-077: app_constants.js JavaScript 语法错误（N/A 键名）

### 1.12 v0.9.1 重大变更 (2026-03-08)

**v0.9.1 用户反馈功能：**

- **反馈 API**：新增 `POST /api/feedback` 接口，支持提交反馈
- **反馈 UI**：关于对话框增加"反馈"标签页
- **反馈类型**：支持 Bug（问题缺陷）、Feature（功能需求）、Optimization（优化建议）
- **数据存储**：反馈保存到 `user_data/feedbacks/FEEDBACK_*.json`
- **权限控制**：需登录用户才能提交反馈

**switchTab 函数改进：**

- 函数签名改为 `switchTab(tab, event)`
- 使用 `event.currentTarget` 替代 `event.target`
- 修复登录后模态框无法关闭的 BUG

**常量管理优化：**

- `app_constants.js` 改用 `window.API_ENDPOINTS` 避免重复声明
- `index.html` 使用 `Object.assign()` 覆盖而非重新声明
- 代码中多处使用常量替代硬编码

### v0.9.1 Bug 修复

- BUG-082: switchTab 函数参数缺失导致登录模态框无法关闭
- BUG-083: API_ENDPOINTS 重复声明错误

### v0.9.2 详细变更

1. **CP/TC 关联状态可视化**（REQ-002/003）：
   - 未关联的 CP/TC 显示为红色加粗 + 🔗图标
   - 前端实时计算关联状态（无需后端改动）
   - 辅助色盲用户区分已关联/未关联状态

2. **CP/TC 独立滚动条 + 高度自适应**（REQ-004）：
   - 使用 `overflow-y: auto` 实现独立垂直滚动
   - 表头使用 `position: sticky; top: 0` 固定
   - 高度自适应：`calc(100vh - 280px)` + min(300px)/max(600px) 保护
   - 兼容现代浏览器（Chrome/Firefox/Edge/Safari）

3. **TC 过滤布局优化**（REQ-004B）：
   - TC 过滤选项改为单行显示，与 CP 布局一致
   - 移除 `<label>` 标签和独立容器 `.tc-filter-panel`
   - 过滤下拉框移至 `.toolbar-left`

4. **CP 未关联过滤**（REQ-005）：
   - CP Filter 下拉增加"未关联"选项
   - 后端 API 支持 `filter=unlinked` 参数
   - 返回 `linked: true/false` 字段

5. **admin 强制改密码前端**（ISSUE-017）：
   - admin 首次登录成功检测 `must_change_password === true`
   - 强制弹窗要求修改密码，禁用其他操作
   - 修改成功后刷新用户信息

6. **用户反馈功能**（REQ-001）：
   - 新增反馈 API (`GET/POST /api/feedbacks`)
   - 前端反馈入口和提交表单
   - Manual 补充用户反馈章节

### v0.10.0 详细变更 (2026-03-20)

1. **Priority 过滤功能**（REQ-2.2）：
   - 图表支持按 CP Priority (P0/P1/P2/P3) 过滤
   - 后端 API 支持 `priority` 参数（单值/多值）
   - 多值 Priority 使用加权平均计算覆盖率

2. **project_progress 表扩展**：
   - 新增 `p0_coverage`、`p1_coverage`、`p2_coverage`、`p3_coverage` 字段
   - 存储各 Priority 的独立覆盖率

3. **CP 关联列表优化**：
   - 关联选择列表支持搜索过滤
   - 已关联 CP 单独显示区域
   - Ctrl+K 快捷键聚焦搜索框

4. **Demo 项目生成脚本更新**：
   - 支持 Priority 快照数据生成
   - 生成包含各 Priority 的测试数据

### v0.10.1 详细变更 (2026-03-21)

1. **批量创建用户 API**：
   - 新增 `POST /api/users/batch` 接口
   - 支持一次性创建多个普通用户
   - 默认密码统一为 `123456`
   - 单次最多创建 50 个用户

2. **安全限制**：
   - 仅支持创建 `role=user`（普通用户）
   - 禁止创建 admin/guest 角色
   - 需要管理员权限 (`@admin_required`)

3. **生产环境用户管理手册**：
   - 新增 `Tracker_Production_User_Management_Guide_v1.1.md`
   - 包含 UI 创建、API 创建、批量创建三种方式

### v0.10.2 详细变更 (2026-03-23)

1. **Intro 引导页**：
   - 新增首次访问引导页（5 slides：封面 + 3 功能截图 + CTA）
   - 用户首次访问时显示引导页
   - 点击"开始使用"后进入主界面并弹出登录框
   - 通过 `localStorage` 记录用户是否已看过引导页
   - 再次访问时直接显示登录界面

2. **引导页功能特性**：
   - 滚动式导航（scroll-snap + 平滑滚动）
   - 右侧进度导航点（可点击跳转）
   - 滚动动画效果（fadeInUp）
   - 浏览器模拟框展示功能截图
   - 版本号从 API 动态获取

3. **相关文件**：
   - `dev/index.html` - 集成 Intro overlay
   - `dev/tracker-intro.html` - 独立引导页（保留）
   - `dev/static/images/slides/` - 截图图片目录

### v0.11.0 详细变更 (2026-04-03)

#### 1. FC (Functional Coverage) 功能

**FC 表结构与 API**：
- 新增 `functional_coverage` 表存储 bin 级别覆盖率数据
- 新增 `fc_cp_association` 表存储 FC-CP 多对多关联
- 项目新增 `coverage_mode` 字段（TC-CP / FC-CP 模式）

**FC API**:
- `GET /api/fc` - 获取 FC 列表（支持筛选）
- `POST /api/fc/import` - 导入 FC (CSV)
- `GET /api/fc/export` - 导出 FC (CSV)
- `PUT /api/fc/batch` - 批量更新 FC items

**FC Tab 界面**：
- 两级折叠（covergroup → coverpoint）
- 支持 covergroup/coverpoint/coverage_type 筛选
- 支持 bin_name 模糊搜索
- FC-CP 关联导入/导出

#### 2. CP Dashboard 功能

**Dashboard API**:
- `GET /api/dashboard/stats` - 获取统计数据

**Dashboard 页面**：
- 概览卡片（总 CP/已覆盖/覆盖率/未关联）
- Feature 覆盖率分布图
- Priority 分布卡片 (P0/P1/P2)
- 覆盖率趋势折线图 (7天)
- Top 5 未覆盖 CP 列表
- Recent Activity 动态

#### 3. 定时快照增强 (BUG-129 修复)

**问题**：`CRON_API_TOKEN` 配置从未设置，导致定时快照失败

**修复**：
- 改为从 `os.environ.get('CRON_API_TOKEN')` 读取
- 响应格式改为 `created_count/skipped_count/errors/timestamp`
- INSERT 语句添加 `p0_coverage/p1_coverage/p2_coverage/p3_coverage` 字段

#### 4. 覆盖率算法修复

**BUG-106**: `calculate_current_coverage` 算法改为"每个 CP 覆盖率求平均"

**BUG-107**: `create_snapshot` 字段映射修复

**BUG-108**: `calculate_planned_coverage` NULL target_date TC 计入分母

#### 5. FC 增强功能 (SUPPLEMENT)

- FC Tab 标题显示 "Functional Coverage"
- 移除"添加 FC"和"导入 FC-CP 关联"按钮
- CP 详情页 FC Item 可点击跳转
- FC Bin 显示 CP IDs 列（可点击）
- FC Comment 超过 150px 截断
- 项目对话框显示 coverage_mode 和 FC 个数

1. **Intro 引导页**：
   - 新增首次访问引导页（5 slides：封面 + 3 功能截图 + CTA）
   - 用户首次访问时显示引导页
   - 点击"开始使用"后进入主界面并弹出登录框
   - 通过 `localStorage` 记录用户是否已看过引导页
   - 再次访问时直接显示登录界面

2. **引导页功能特性**：
   - 滚动式导航（scroll-snap + 平滑滚动）
   - 右侧进度导航点（可点击跳转）
   - 滚动动画效果（fadeInUp）
   - 浏览器模拟框展示功能截图
   - 版本号从 API 动态获取

3. **相关文件**：
   - `dev/index.html` - 集成 Intro overlay
   - `dev/tracker-intro.html` - 独立引导页（保留）
   - `dev/static/images/slides/` - 截图图片目录

### v0.5.x 详细变更

1. **Git 仓库简化**：
   - 只维护 `dev/` 代码，移除 `stable/` 追踪
   - 发布目录 `/release/tracker/v{version}/` 由 `release.py` 生成

2. **发布目录独立**：
   - `/release/tracker/v{version}/`：历史版本目录
   - `/release/tracker/current`：软链接指向当前运行版本
   - systemd 服务指向 `current`

3. **发布流程改进**：
   - 一键发布到独立目录
   - 软链接切换版本，无需覆盖
   - 快速回滚（切换软链接）
   - 用户数据与测试数据物理隔离，互不影响

3. **数据管理工具**（scripts/data_manager.py）：
   - `sync`：同步用户数据到测试目录（用于兼容性测试）
   - `clean`：清理测试数据
   - `create`：创建测试项目

4. **CP 覆盖率计算**（v0.3.1 新增）：
   - 每个 Cover Point 显示覆盖率百分比
   - 基于关联 TC 的 PASS 状态计算
   - 全部 PASS = 100%，无关联 = 0%，部分 = PASS/总数
   - API 返回 `coverage` 和 `coverage_detail` 字段

### v0.3 详细变更

1. **代码隔离**：stable/ 和 dev/ 目录完全独立
2. **数据共享**：shared/data/ 集中存储用户数据
3. **版本迁移**：支持 v0.2 到 v0.3 自动迁移
4. **发布流程**：一键发布脚本，支持回滚
5. **兼容性检查**：启动时自动检查数据库版本

---

## 附录

### A. 文件结构

```
/projects/management/tracker/
├── stable/                   # 正式版
│   ├── server.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── index.html
│   └── data → ../shared/data/user_data
│
├── dev/                     # 测试版
│   ├── server.py
│   ├── server_test.py      # 原启动脚本（已弃用）
│   ├── start_server_test.sh     # 新启动脚本 (gunicorn)
│   ├── app/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── index.html
│   ├── tests/
│   │   ├── test_api.py      # 完整 API 测试
│   │   └── test_sanity.py   # 冒烟测试
│   └── data → ../shared/data/test_data
│
├── shared/                  # 共享数据
│   └── data/
│       ├── user_data/       # 用户真实数据
│       │   ├── projects.json
│       │   ├── Debugware_65K.db
│       │   └── EX5.db
│       │
│       ├── test_data/       # 测试数据
│       │   ├── projects.json
│       │   └── *.db        # 测试项目
│       │
│       └── tracker_backup_*.db  # v0.2 原始备份
│
└── scripts/                 # 工具脚本
    ├── release.py           # 版本发布
    ├── migrate_v02_to_v03.py  # v0.2 → v0.3 迁移
    ├── compat_check.py      # 兼容性检查
    └── data_manager.py      # 数据管理（sync/clean）
```

### B. 风险评估

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 迁移失败 | 数据丢失 | 自动备份原数据 |
| 符号链接损坏 | 数据不可访问 | 发布前验证链接 |
| 版本冲突 | 启动失败 | 版本检查 + 错误提示 |
| 端口冲突 | 服务无法启动 | 使用不同端口 (8080/8081) |

### C. 常见问题

**Q: 如何升级到 v0.3？**

A: 执行迁移脚本：
```bash
python3 scripts/migrate_v02_to_v03.py --source data/tracker.db --target shared/data/
```

**Q: 版本发布会丢失数据吗？**

A: 不会。数据存储在 `shared/data/`，独立于代码目录。

**Q: 如何回滚到上一版本？**

A: 执行回滚命令：
```bash
python3 scripts/release.py --rollback --force
```
