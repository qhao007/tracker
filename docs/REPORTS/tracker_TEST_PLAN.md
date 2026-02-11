# 芯片验证 Tracker v0.3 测试计划

> **版本**: v0.3 | **更新日期**: 2026-02-05 | **状态**: 进行中

---

## 1. 测试策略

### 1.1 目录结构

> **说明**: Git 只维护 dev/ 代码，stable/ 已移除。发布时由 release.py 生成到 `/release/tracker/` 目录。

```
/projects/management/tracker/              ← Git 仓库（只维护 dev/）
├── dev/                                  ← 开发版代码（Git 分支: develop）
│   ├── server.py                        # 开发启动脚本 (:8081)
│   ├── server_test.py                   # 旧启动脚本（已弃用）
│   ├── start_server_test.sh                 # 新启动脚本 (gunicorn)
│   ├── app/                             # Flask 应用
│   ├── index.html                       # 前端页面
│   ├── data → ../shared/data/test_data  # 测试数据
│   ├── tests/                            # 测试用例
│   └── docs/                             # 文档
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
├── current → v0.3.2/                   ← 软链接指向当前版本
└── RELEASE_NOTES.md                     ← 发布报告
```

### 1.2 双版本数据隔离策略

| 版本 | 数据目录 | 用途 | 数据安全 |
|------|----------|------|----------|
| **stable** | `/release/tracker/current` | 用户正常使用 | ✅ 使用 user_data |
| **dev** | `test_data/` | 开发测试专用 | ✅ 与用户数据完全隔离 |

**说明：**
- **stable 版本**：发布目录 `/release/tracker/current`，使用 `user_data`，可读写
- **dev 版本**：使用 `test_data`，可读写，测试操作不影响 `user_data`

### 1.3 测试策略

| 版本 | 测试范围 | 测试数据目录 | 数据安全保证 |
|------|----------|--------------|--------------|
| **dev** | 完整测试：17个API + **Playwright 关键功能** + **BugLog 回归测试** | `test_data/` | ✅ 测试数据与用户数据完全隔离 |
| **stable** | 冒烟测试：5个核心API + **playwright_firefox.js 测试** | `user_data/` | ✅ 测试代码只做只读验证 |

**dev 版本测试要求：**
- ✅ API 测试：17 个测试全部通过 (100%)
- ✅ 关键功能点：F001, F004, F005, F006, F007, F009, F010, F011, F012
- ✅ Playwright 冒烟测试：6 个核心功能验证 (90% 通过)
- ✅ **playwright_firefox.js 测试**：P001-P014 基础功能验证
- ✅ **BugLog 回归测试**：11 个测试用例 (BUG-008, BUG-009, BUG-010, FEAT-001, BUG-002, BUG-007)
- ⚠️ **超时测试计入失败统计**

### 1.4 数据兼容性测试

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

### 1.5 测试目标

- 验证 v0.3 代码隔离架构正确
- 验证数据共享机制工作正常
- 确保正式版和测试版功能正常
- **确保 stable 与 dev 代码同步，无回归**
- **确保用户数据与测试数据物理隔离，互不影响**

### 1.6 测试范围

| 版本 | 测试类型 | 覆盖范围 | 通过标准 | 数据目录 |
|------|----------|----------|----------|----------|
| **dev** | 单元测试 | 全部 API 接口 | 100% 通过 | test_data |
| **dev** | 集成测试 | 项目 + CP + TC 关联 | 100% 通过 | test_data |
| **dev** | UI 自动化 | Playwright 冒烟测试 (6 个核心功能) | 90% 通过 | test_data |
| **dev** | BugLog 回归测试 | 11 个测试用例 | 90% 通过 | test_data |
| **stable** | 冒烟测试 | 核心 API | 100% 通过 | user_data |
| **stable** | playwright_firefox.js | P001-P014 基础功能验证 | 100% 通过 | user_data |
| **共同** | 版本迁移 | v0.2 → v0.3 数据迁移 | 数据完整 | - |
| **共同** | 发布测试 | 发布脚本执行 | 流程正常 | - |
| **共同** | 手动测试 | 前端交互、界面显示 | 用户验收 | - |

**注意：** stable 的冒烟测试代码**只执行只读操作**（获取列表、读取详情），不创建或删除任何数据，确保不误修改用户项目。

---

## 2. 目录结构测试

### 2.1 测试环境

```
/projects/management/tracker/              ← Git 仓库（只维护 dev/）
├── dev/                                    ← 测试版 (端口 8081)
│   ├── server_test.py          # 旧启动脚本（已弃用）
│   ├── start_server_test.sh        # 新启动脚本 (gunicorn)
│   ├── index.html
│   └── data → ../shared/data/test_data
│
├── shared/                                  ← 共享数据
│   └── data/
│       ├── user_data/                      ← 用户数据（stable 使用）
│       └── test_data/                      ← 测试数据（dev 使用）
│
└── scripts/                                 # 工具脚本
    ├── release.py
    ├── migrate_v02_to_v03.py
    └── compat_check.py

/release/tracker/                            ← 发布目录（由 release.py 生成）
├── v0.3.1/
├── v0.3.2/
├── current → v0.3.2/                        ← 软链接
└── data → /projects/management/tracker/shared/data/user_data
```

### 2.2 目录结构测试用例

| ID | 测试项 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|
| T001 | 发布目录符号链接 | `ls -la /release/tracker/current/data` | 指向 /projects/management/tracker/shared/data/user_data |
| T002 | dev/data 符号链接 | `ls -la dev/data` | 指向 ../shared/data/test_data |
| T003 | shared/data 目录结构 | 检查目录 | user_data/ 和 test_data/ 分离 |
| T004 | dev/ 启动 | `cd dev && bash start_server_test.sh` | 访问 http://localhost:8081 |
| T005 | stable/ 启动 | `/release/tracker/current/server.py` | 访问 http://localhost:8080 |

### 2.3 数据隔离测试

| ID | 测试项 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|
| D001 | stable 使用 user_data | stable 操作 | 数据写入 user_data/ |
| D002 | dev 使用 test_data | dev 创建项目 | 数据写入 test_data/ |
| D003 | 数据完全隔离 | 在 dev 创建数据，stable 读取 | 互不可见 |
| D004 | 发布不覆盖 | 发布后检查 user_data | 数据不变 |
| D005 | 回滚保留数据 | 回滚后检查 user_data | 数据不变 |

---

## 2. 数据安全规范

### 2.1 用户数据保护规则 ⚠️

> **核心原则**: 开发代码测试中绝不允许对用户正式数据的项目做任何修改！

| 规则 | 说明 |
|------|------|
| **禁止修改用户项目** | 测试代码不得修改、删除 Debugware_65K、EX5 等正式用户项目 |
| **允许的操作** | 版本迁移时对旧版本数据库的调整（兼容性修复） |
| **允许的操作** | 读取用户项目数据进行验证 |
| **禁止的操作** | 创建/修改/删除用户项目中的 CP、TC、数据 |

### 2.2 测试项目命名规范

> 所有测试创建的项目必须使用明确标记的前缀或后缀，便于识别和清理

| 前缀/后缀 | 示例 | 用途 |
|-----------|------|------|
| `Test*` | TestProject, Test_v03 | 一般测试 |
| `*Test` | PlaywrightTest | 测试后缀 |
| `API*` | APITestProject | API 测试 |
| `Dev*` | DevTestProject | 开发测试 |
| `Stable*` | StableTest | 稳定版测试 |
| `Final*` | Final_P005_Test | 最终测试 |

### 2.3 测试项目清理流程

> **重要**: 测试完成后必须清理所有测试创建的项目，但绝不能误删用户项目！

#### 清理步骤

```bash
# 1. 识别测试项目（使用明确的前缀/后缀）
# 2. 确认不是用户项目（Debugware_65K, EX5）
# 3. 删除测试项目数据库
# 4. 更新 projects.json

# 安全清理命令（只删除测试项目）
python3 << 'EOF'
import json
import os

# 用户项目列表（绝不能删除）
USER_PROJECTS = ['Debugware_65K', 'EX5']

# 加载项目列表
with open('shared/data/projects.json', 'r') as f:
    projects = json.load(f)

# 识别测试项目
test_projects = [p for p in projects if p['name'].startswith('Test') 
                                             or p['name'].endswith('Test')
                                             or p['name'].startswith('API')
                                             or p['name'].startswith('Dev')
                                             or p['name'].startswith('Stable')
                                             or p['name'].startswith('Final')]

# 保护用户项目
user_projects = [p for p in projects if p['name'] in USER_PROJECTS]

print(f"用户项目（保护）: {[p['name'] for p in user_projects]}")
print(f"测试项目（将删除）: {[p['name'] for p in test_projects]}")

# 删除测试项目数据库
for p in test_projects:
    db_file = f"shared/data/{p['name'].replace(' ', '_')}.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"   ✅ 已删除: {db_file}")

# 更新 projects.json
filtered = [p for p in projects if p['name'] in USER_PROJECTS]
with open('shared/data/projects.json', 'w') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print(f"\n✅ 清理完成，保留 {len(filtered)} 个用户项目")
EOF
```

#### ⚠️ 清理检查清单

- [ ] 确认用户项目列表 `USER_PROJECTS` 正确
- [ ] 确认测试项目识别规则覆盖所有测试场景
- [ ] 确认不会误删用户项目
- [ ] 确认 `projects.json` 已更新
- [ ] 确认兼容性检查通过

---

## 3. API 测试用例

### 3.1 基础 API 测试

| ID | 用例描述 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| A001 | 获取版本信息 | GET /api/version | 返回版本信息 |
| A002 | 创建项目 | POST /api/projects | 项目创建成功 |
| A003 | 创建重复项目 | POST 相同名称 | 返回错误 |
| A004 | 获取项目列表 | GET /api/projects | 返回所有项目 |
| A005 | 创建 Cover Point | POST /api/cp | CP 创建成功 |
| A006 | 获取 CP 列表 | GET /api/cp | 返回 CP 列表 |
| A007 | 更新 Cover Point | PUT /api/cp/{id} | CP 更新成功 |
| A008 | 删除 Cover Point | DELETE /api/cp/{id} | CP 删除成功 |
| A009 | 创建 Test Case | POST /api/tc | TC 创建成功，状态为 OPEN |
| A010 | 更新 TC 状态 | POST /api/tc/{id}/status | 状态切换 |
| A011 | TC 状态过滤 | GET /api/tc?status=PASS | 返回 PASS 状态 TC |
| A012 | TC 排序 | GET /api/tc?sort_by=testbench | 按 TestBench 排序 |
| A013 | 项目备份 | POST /api/projects/{id}/archive | 生成备份文件 |
| A014 | 获取统计 | GET /api/stats | 返回统计数据 |

### 3.2 独立数据库测试

| ID | 测试项 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|
| D001 | 创建项目 TestA | POST /api/projects {name: "TestA"} | 生成 TestA.db |
| D002 | 在 TestA 添加数据 | POST /api/cp {project_id: TestA.id} | 数据写入 TestA.db |
| D003 | 切换到 TestB | GET /api/projects | 读取 TestB.db |
| D004 | 删除 TestA | DELETE /api/projects/TestA | 删除 TestA.db |

### 3.3 状态转换测试

| ID | 测试项 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|
| S001 | OPEN → CODED | 创建 TC，状态更新 | 状态变为 CODED |
| S002 | CODED → FAIL | 更新状态 | 状态变为 FAIL |
| S003 | FAIL → PASS | 更新状态 | 状态变为 PASS，完成日期更新 |
| S004 | PASS → OPEN | 重置状态 | 状态变为 OPEN，完成日期清空 |

---

## 4. 版本迁移测试

### 4.1 迁移前检查

```bash
# 检查兼容性
python3 scripts/compat_check.py shared/data/
```

**预期输出：**
```
🔍 数据库兼容性检查
📂 检查 {n} 个项目
✅ 所有数据库兼容
```

### 4.2 v0.2 → v0.3 迁移测试

| ID | 测试项 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|
| M001 | 加载 v0.2 数据 | 执行迁移脚本 | 正确读取 project, cp, tc 表 |
| M002 | 生成独立数据库 | 检查 shared/data/*.db | 每个项目一个 .db 文件 |
| M003 | 创建 projects.json | 检查 projects.json | 项目列表正确 |
| M004 | 数据完整性 | 对比 CP, TC 数量 | 数量一致 |
| M005 | 关联关系 | 检查 tc_cp_connections | 关联正确 |

### 4.3 迁移命令

```bash
# 演练模式
python3 scripts/migrate_v02_to_v03.py --dry-run

# 实际迁移
python3 scripts/migrate_v02_to_v03.py --source data/tracker.db --target shared/data/

# 验证
python3 scripts/compat_check.py shared/data/
```

---

## 5. 发布流程测试

### 5.1 发布命令

```bash
cd /projects/management/tracker

# 演练模式（不实际执行）
python3 scripts/release.py --dry-run

# 实际发布
python3 scripts/release.py --version v0.3.3 --force

# 回滚
python3 scripts/release.py --rollback --force
```

**发布目录：**
```
/release/tracker/
├── v0.3.1/
├── v0.3.2/
└── current → v0.3.2/  ← systemd 指向这里
```

### 5.2 发布测试用例

| ID | 测试项 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|
| R001 | 创建发布版本 | 执行发布脚本 | /release/tracker/v{version}/ 生成 |
| R002 | 数据保留 | 发布后检查 user_data/ | 数据不变 |
| R003 | 符号链接 | 检查 /release/tracker/v{version}/data | 指向 /projects/management/tracker/shared/data/user_data |
| R004 | current 软链接 | 检查 /release/tracker/current | 指向最新版本目录 |
| R005 | systemd 更新 | 检查服务配置 | WorkingDirectory 指向 /release/tracker/current |
| R006 | 回滚功能 | 执行回滚 | current 软链接切换 |
| R007 | 回滚保留数据 | 回滚后检查 user_data/ | 数据不变 |

---

## 6. Playwright 自动化测试

### 6.1 工具配置

**使用 Playwright Firefox 进行前端自动化测试**

```bash
# 安装 Playwright
npm install @playwright/test
npx playwright install firefox
```

### 6.2 测试脚本

| 脚本 | 说明 |
|------|------|
| `tests/playwright_firefox.js` | Firefox 自动化测试脚本 |

运行命令:
```bash
# 启动 Tracker 服务
cd stable && python3 server.py &

# 运行 Firefox 测试
node tests/playwright_firefox.js
```

### 6.3 当前状态 ✅

> **✅ 已完成**: Firefox 浏览器安装成功，Playwright 测试全部通过！

**已验证功能 (Firefox):**
| 测试项 | 结果 | 说明 |
|--------|------|------|
| P001 | ✅ 页面加载 | 标题正确: "芯片验证 Tracker v1.0" |
| P003 | ✅ 项目列表 | 10 个项目正常显示 |
| P006 | ✅ CP 标签 | Cover Points 标签存在 |
| P008 | ✅ TC 标签 | Test Cases 标签存在 |
| P011 | ✅ 统计面板 | 7 个统计项 |
| P012 | ✅ 备份按钮 | 备份按钮存在 |
| P014 | ✅ 元素可见性 | header, container, toolbar, table 正常 |

**额外验证:**
- ✅ 无 JavaScript 错误
- ✅ 截图功能正常 (`/tmp/tracker_firefox.png`)
- ✅ API 接口响应正常

- ✅ 无 JavaScript 错误
- ✅ 截图功能正常 (`/tmp/tracker_firefox.png`)
- ✅ API 接口响应正常

### 6.3 BugLog 回归测试

> **说明**: 基于 BugLog 中的 bug 和功能创建 Playwright 测试用例，确保修复后不会再次出现

**测试文件:** `dev/tests/tracker.spec.ts`

**BugLog 覆盖:**

| Bug ID | 描述 | 严重性 | 测试用例 |
|--------|------|--------|----------|
| BUG-008 | EX5 项目 TC 数据无法加载 | 高 | '切换项目后 Test Cases 应该正常显示' |
| BUG-009 | TC 状态无法更新 | 高 | '状态选择后应该更新为新状态' |
| BUG-010 | 删除功能失效 | 高 | '删除 CP 后列表应更新', '删除 TC 后列表应更新' |
| FEAT-001 | CP 覆盖率计算 | 新功能 | 'CP 列表应显示覆盖率', '覆盖率颜色正确显示' |
| BUG-002 | 项目切换数据不刷新 | 低 | '项目切换后数据刷新' |
| BUG-007 | 刷新后项目选择重置 | 低 | '页面刷新后项目选择保持' |

**运行命令:**

```bash
# 运行所有回归测试
cd dev
npx playwright test tests/tracker.spec.ts --project=firefox --reporter=line

# 运行特定测试
npx playwright test tests/tracker.spec.ts -g "BUG-008" --project=firefox
npx playwright test tests/tracker.spec.ts -g "覆盖率" --project=firefox

# 生成 HTML 报告
npx playwright test tests/tracker.spec.ts --project=firefox --reporter=html
```

**测试结构:**

```typescript
test.describe('BUG-008: 项目 TC 数据加载', () => {
  test('切换项目后 Test Cases 应该正常显示', ...)
  test('EX5 项目 TC 数据加载', ...)
});

test.describe('BUG-009: Test Case 状态更新', () => {
  test('状态选择后应该更新为新状态', ...)
});

test.describe('BUG-010: 删除功能', () => {
  test('删除 CP 后列表应更新', ...)
  test('删除 TC 后列表应更新', ...)
});

test.describe('FEAT-001: CP 覆盖率计算', () => {
  test('CP 列表应显示覆盖率', ...)
  test('覆盖率颜色正确显示', ...)
});
```

### 6.4 E2E 测试生成器

> **说明**: 由于 e2e-writer (ai-e2e-gen) 网络问题无法安装，创建了自定义测试生成器

**测试生成器脚本:** `scripts/generate_tests.py`

```bash
# 生成测试
python3 scripts/generate_tests.py --url http://localhost:8080 --output tests/tracker.spec.ts
```

**生成的测试文件:** `tests/tracker.spec.ts`

**测试覆盖范围:**
| 测试类型 | 数量 | 说明 |
|----------|------|------|
| 页面加载 | 2 | P001-P002 |
| 项目操作 | 3 | P003-P005 |
| CP 操作 | 2 | P006-P007 |
| TC 操作 | 6 | P008-P010c |
| 编辑操作 | 2 | P015, P017 |
| 删除操作 | 2 | P016, P018 |
| 备份操作 | 2 | P012-P013 |
| 统计面板 | 1 | P011 |
| **总计** | **20** | **全部可运行** |

**API 测试已覆盖:**
| 测试项 | 结果 |
|--------|------|
| P004 | ✅ 版本信息 |
| P005 | ✅ 创建项目 |
| P007 | ✅ 创建 CP |
| P009 | ✅ 创建 TC |
| P010 | ✅ 统计信息 |
| P010b | ✅ 状态切换 FAIL |
| P010c | ✅ 状态切换 PASS |

**待执行测试:**
| 测试项 | 操作 | 状态 |
|--------|------|------|
| P015 | 编辑 TC | ⏳ 待执行 |
| P016 | 删除 TC | ⏳ 待执行 |
| P017 | 编辑 CP | ⏳ 待执行 |
| P018 | 删除 CP | ⏳ 待执行 |

### 6.5 浏览器安装状态

| 浏览器 | 状态 | 说明 |
|--------|------|------|
| Firefox | ✅ 可用 | 已安装并测试通过 |
| WebKit | ⚠️ 缺少依赖 | 需要系统库 (libgtk-4 等) |
| Chromium | ❌ 网络问题 | 下载超时 |

推荐使用 **Firefox** 进行 UI 测试。

### 6.6 Playwright 测试脚本示例

```javascript
// 测试脚本示例
{
  "name": "Tracker UI Tests",
  "tests": [
    {
      "name": "P001 - Page Load",
      "command": "navigate http://localhost:8080",
      "assert": "title contains 'Tracker'"
    },
    {
      "name": "P005 - Create Project",
      "command": "click button:has-text('创建')",
      "command": "fill input[name='name'] 'PlaywrightTest'",
      "command": "click button:has-text('保存')",
      "assert": "toast contains '项目创建成功'"
    },
    {
      "name": "P009 - Create TC",
      "command": "click tab:has-text('Test Cases')",
      "command": "click button:has-text('+ 添加 TC')",
      "command": "fill input[name='testbench'] 'TB01'",
      "command": "fill input[name='category'] 'Sanity'",
      "command": "fill input[name='owner'] 'Tester'",
      "command": "fill input[name='test_name'] 'TC001'",
      "command": "fill textarea[name='scenario'] 'Test scenario'",
      "command": "click button:has-text('保存')",
      "assert": "table contains 'TC001'"
    }
  ]
}
```

### 6.7 运行 Playwright 测试

```bash
# 方式 1: 使用 playwright-mcp
playwright-mcp
# 然后执行测试命令

# 方式 2: 使用 playwright CLI
npx playwright test tests/ui/

# 方式 3: 使用浏览器快照
npx playwright screenshot http://localhost:8080 --full-page
```

### 6.8 截图测试

```bash
# 完整页面截图
playwright screenshot http://localhost:8080 --full-page

# 元素截图
playwright screenshot --selector="#project-list"

# 对比测试
playwright screenshot --diff
```

---

## 7. 手动测试用例

> **说明**: 以下测试需要用户手动执行验收，自动化脚本无法完全覆盖

### 7.1 用户验收测试

| ID | 功能 | 测试步骤 | 预期结果 | 备注 |
|----|------|----------|----------|------|
| **U001** | **整体功能验收** | 访问页面、创建项目、添加 CP/TC、状态切换 | 所有功能正常 | **必须** |
| U002 | 界面体验 | 手动操作页面，检查布局、样式、交互 | 界面友好 | 推荐 |
| U003 | 多项目切换 | 在多个项目间切换测试 | 数据正确切换 | 推荐 |
| U004 | 导出备份 | 手动下载备份文件 | 文件下载正常 | 推荐 |
| U005 | 项目恢复 | 上传备份文件执行恢复 | 数据正确恢复 | **推荐** |

### 7.2 无法自动化的测试

| ID | 功能 | 说明 | 原因 |
|----|------|------|------|
| - | 无 | 当前所有功能均可通过自动化测试覆盖 | - |

### 7.3 兼容性测试（通过脚本执行）

| ID | 测试项 | 测试步骤 | 预期结果 | 执行方式 |
|----|--------|----------|----------|----------|
| C001 | 正式版启动 | `cd stable && python3 server.py` | 正常启动 | 脚本 |
| C002 | 测试版启动 | `cd dev && bash start_server_test.sh` | 正常启动 | 脚本 |
| C003 | 端口占用 | 检查 8080/8081 端口 | 互不冲突 | 脚本 |
| C004 | 数据迁移 | 从 v0.2 迁移 | 数据完整 | 脚本 |

---

## 8. 测试报告规范

### 8.1 报告文件命名规则

```
TRACKER_TEST_REPORT_{版本号}_{YYYYMMDD}_{HHMM}.md
```

**示例：**
```
TRACKER_TEST_REPORT_v0.3.1_20260204_2250.md
```

### 8.2 报告内容要求

每份测试报告必须包含以下章节：

| 章节 | 必需 | 说明 |
|------|------|------|
| 测试摘要 | ✅ | 通过/失败/超时统计 |
| API 测试结果 | ✅ | 详细测试用例列表 |
| 冒烟测试结果 | ✅ | 核心功能验证 |
| UI 测试结果 | ✅ | 界面功能测试 |
| Bug 修复验证 | ✅ | 对应 Bug 状态 |
| 测试环境 | ✅ | 版本、环境信息 |
| 结论 | ✅ | 是否可发布建议 |

### 8.3 结果判断标准

#### 测试结果状态定义

| 状态 | 定义 | 判定依据 |
|------|------|----------|
| ✅ 通过 (PASS) | 测试执行成功，达到预期结果 | 断言全部通过 |
| ❌ 失败 (FAIL) | 测试执行未达到预期结果 | 断言失败或异常 |
| ⏱️ 超时 (TIMEOUT) | 测试执行超出预设时间 | 执行时间超过 timeout 设置 |
| ⏭️ 跳过 (SKIP) | 测试未执行 | 依赖条件不满足 |
| ❌ 错误 (ERROR) | 测试执行出错 | 未捕获的异常 |

#### 结果优先级

1. **超时视为失败**：超时的测试用例在报告中计入失败统计
2. **失败必须标注**：每个失败用例需标注具体原因
3. **耗时记录**：记录执行耗时，便于性能分析

### 8.4 报告模板

**模板文件:** `docs/TEMPLATES/TEMPLATE_TEST_REPORT.md`

---

## 9. 规格书关键功能点测试
| GET | `/api/tc` | test_api.py |
| POST | `/api/tc` | test_api.py |
| PUT | `/api/tc/{id}` | test_api.py |
| DELETE | `/api/tc/{id}` | test_api.py |
| POST | `/api/tc/{id}/status` | test_api.py |
| GET | `/api/tc?status=` | test_api.py |
| GET | `/api/tc?sort_by=` | test_api.py |
| GET | `/api/stats` | test_api.py |

**未覆盖 (1/18):**

| 方法 | 路径 | 优先级 |
|------|------|--------|
| POST | `/api/projects/{id}/archive` | P2 |

### 8.3 测试用例模板

**API 测试模板:**

| 方法 | 路径 | 测试文件 |
|------|------|----------|
| GET/POST/PUT/DELETE | /api/* | test_api.py |

**Playwright 测试模板:** `tests/tracker.spec.ts`

### 8.4 覆盖率目标

| 目标 | 目标值 |
|------|--------|
| API 端点覆盖率 | 100% |
| Python 单元测试 | 70% |
| UI 功能测试 | 100% |
| 综合覆盖率 | 70% |

### 8.5 运行覆盖率测试
| Python 单元测试 (dev) | 100% | 100% | 70% | ✅ 已达成 |
| Playwright 冒烟测试 (dev) | 83% | - | 90% | P1 |
| **playwright_firefox.js (stable)** | - | **14/14** | **14/14** | ✅ 已达成 |
| **BugLog 回归测试 (dev)** | - | **11** | **11** | ✅ 已达成 |
| 冒烟测试 (stable) | - | 5/5 | 5/5 | ✅ 已达成 |
| 综合覆盖率 (dev) | 80% | - | 70% | ✅ 已达成 |

```bash
# dev 版本 - 完整测试
cd dev
PYTHONPATH=. coverage run -m pytest tests/test_api.py -v
coverage report -m
coverage html

# dev 版本 - Playwright 回归测试
npx playwright test tests/tracker.spec.ts --project=firefox

# stable 版本 - 冒烟测试
cd stable
PYTHONPATH=. coverage run -m pytest tests/test_sanity.py -v
coverage report -m
```

**测试文件位置：**

```
dev/
└── tests/
    ├── test_api.py           # 完整 API 测试 (17 个测试)
    ├── tracker.spec.ts       # Playwright 回归测试 (11 个测试)
    └── conftest.py           # pytest 配置

stable/
└── tests/
    ├── test_api.py          # 完整 API 测试 (用于回归检查)
    └── test_sanity.py       # 冒烟测试 (5 个核心测试)
```

### 8.7 BugLog 回归测试

| Bug ID | 描述 | 测试用例数 | 文件 |
|--------|------|------------|------|
| BUG-008 | EX5 项目 TC 数据无法加载 | 2 | tracker.spec.ts |
| BUG-009 | TC 状态无法更新 | 2 | tracker.spec.ts |
| BUG-010 | 删除功能失效 | 2 | tracker.spec.ts |
| FEAT-001 | CP 覆盖率计算 | 3 | tracker.spec.ts |
| BUG-002 | 项目切换数据不刷新 | 1 | tracker.spec.ts |
| BUG-007 | 刷新后项目选择重置 | 1 | tracker.spec.ts |
| **总计** | - | **11** | - |

**运行回归测试:**

```bash
cd dev

# 运行所有回归测试
npx playwright test tests/tracker.spec.ts --project=firefox --reporter=line

# 运行特定 bug 回归测试
npx playwright test tests/tracker.spec.ts -g "BUG-008" --project=firefox
npx playwright test tests/tracker.spec.ts -g "BUG-009" --project=firefox
npx playwright test tests/tracker.spec.ts -g "覆盖率" --project=firefox

# 生成 HTML 报告
npx playwright test tests/tracker.spec.ts --project=firefox --reporter=html
open playwright-report/index.html
```

### 8.8 测试用例模板

**dev 版本 - 完整测试:**
| 测试类 | 测试方法数 | 说明 |
|------|----------|------|
| TestVersionAPI | 1 | 版本 API 测试 |
| TestProjectsAPI | 4 | 项目管理 API 测试 |
| TestCoverPointsAPI | 4 | Cover Points API 测试 |
| TestTestCasesAPI | 7 | Test Cases API 测试 |
| TestStatsAPI | 1 | 统计 API 测试 |
| **总计** | **17** | - |

**stable 版本 - 冒烟测试:**
| 测试类 | 测试方法数 | 说明 |
|------|----------|------|
| TestSanity | 5 | 核心功能冒烟测试 |
| **总计** | **5** | - |

---

### 7.4 测试报告要求（已废弃）

> ⚠️ 此节内容已废弃，请参考第11章测试报告规范

---

## 8. 测试报告规范

### 8.1 报告文件命名规则
- Playwright UI 测试：20/20 ⏳ (待执行)
```

#### stable (正式版) - 冒烟测试
```
总用例数：5 (核心 sanity)
通过：5
失败：0
通过率：100%

冒烟测试覆盖：
- S001 版本 API 正常
- S002 项目列表获取
- S003 创建项目
- S004 CP 创建/读取
- S005 TC 创建/读取
```

### 8.3 已完成测试

| 版本 | 测试类型 | 状态 | 说明 |
|------|----------|------|------|
| **dev** | API 测试 | ✅ 17/17 | 94% 端点覆盖 |
| **dev** | pytest | ✅ 100% | coverage: 80% |
| **dev** | Playwright | ⏳ 已生成 | 20 个测试用例 |
| **stable** | 冒烟测试 | ✅ 可执行 | 5 个核心测试 |
| **共同** | 兼容性测试 | ✅ 可脚本执行 | C001-C004 |
| **共同** | 手动验收 | U001-U005 |

### 8.4 待测试项目

| 项目 | 版本测试 | ✅ 用户 | 优先级 |
|------|------|--------|
| Playwright UI | dev | P0 |
| 版本迁移完整测试 | dev | P1 |
| 发布回滚功能 | dev | P1 |
| 备份 API 测试 | dev | P2 |

### 8.5 发布前检查清单

```bash
# 1. dev 版本完整 API 测试 ✅
cd dev && PYTHONPATH=. pytest tests/test_api.py -v

# 2. Playwright 冒烟测试 ✅
cd dev && npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000

# 3. BugLog 回归测试 ✅
cd dev && npx playwright test tests/tracker.spec.ts --project=firefox

# 4. 演练发布（验证命令）
cd /projects/management/tracker
python3 scripts/release.py --dry-run

# 5. 实际发布
python3 scripts/release.py --version v0.3.3 --force
```

**注意**: 只有在 dev 版本所有测试通过后，才能执行发布流程。

---

## 9. 规格书关键功能点测试

### 9.1 覆盖功能列表

根据规格书 `docs/SPECIFICATIONS/tracker_OVERALL_SPECS.md` 3.1 功能列表，以下关键功能需要 Playwright 自动化测试覆盖：

| 编号 | 功能 | 描述 | 测试优先级 |
|------|------|------|----------|
| **F001** | 项目管理 | 创建、加载、切换项目 | P0 |
| **F004** | Cover Points 管理 | 按字段结构管理 CP | P0 |
| **F005** | Test Cases 管理 | 按字段结构管理 TC | P0 |
| **F006** | 关联管理 | TC 关联 CP（多对多关系） | P0 |
| **F007** | 状态跟踪 | OPEN → CODED → FAIL → PASS | P0 |
| **F009** | 排序过滤 | 按字段排序和过滤 TC | P1 |
| **F010** | 完成日期 | 显示 TC 完成日期 | P1 |
| **F011** | 进度统计 | 自动计算 CP 完成进度 | P1 |
| **F012** | 覆盖率计算 | 整体覆盖率百分比显示 | P1 |

### 9.2 测试用例定义

#### F001 项目管理

| ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|----------|
| F001-01 | 项目选择 | 页面加载 | 1. 访问页面<br>2. 点击项目选择器<br>3. 选择项目 | 项目列表正常显示，选项可选择 |
| F001-02 | 项目保持 | 已选择项目 | 1. 刷新页面<br>2. 检查项目选择 | 项目选择保持 |
| F001-03 | 项目切换 | 已选择项目A | 1. 切换到项目B<br>2. 检查数据切换 | 显示项目B的数据 |

#### F004 Cover Points 管理

| ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|----------|
| F004-01 | CP 列表加载 | 已选择项目 | 1. 点击 Cover Points 标签<br>2. 检查列表 | CP 表格正常显示 |
| F004-02 | CP 搜索 | CP 列表加载 | 1. 输入搜索关键词<br>2. 检查筛选结果 | 只显示匹配的 CP |

#### F005 Test Cases 管理

| ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|----------|
| F005-01 | TC 列表加载 | 已选择项目 | 1. 点击 Test Cases 标签<br>2. 检查列表 | TC 表格正常显示 |
| F005-02 | TC 搜索 | TC 列表加载 | 1. 输入搜索关键词<br>2. 检查筛选结果 | 只显示匹配的 TC |

#### F006 关联管理

| ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|----------|
| F006-01 | TC 关联 CP | 存在 CP 和 TC | 1. 编辑 TC<br>2. 勾选关联 CP<br>3. 保存 | TC 关联 CP 成功 |

#### F007 状态跟踪

| ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|----------|
| F007-01 | TC 状态切换 | TC 列表加载 | 1. 选择 TC 状态<br>2. 验证更新 | 状态立即更新 |
| F007-02 | 状态颜色 | TC 列表加载 | 1. 检查状态颜色 | OPEN=蓝, CODED=橙, FAIL=红, PASS=绿 |

#### F012 覆盖率计算

| ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|----------|
| F012-01 | 覆盖率显示 | CP 列表加载 | 1. 点击 Cover Points 标签<br>2. 检查覆盖率列 | 覆盖率列正常显示 |
| F012-02 | 覆盖率颜色 | 覆盖率列显示 | 1. 检查覆盖率颜色 | 100%=绿, 部分=黄, 0%=红 |

### 9.3 测试文件

**测试文件:** `dev/tests/test_smoke.spec.ts`

```bash
# 运行关键功能测试
cd dev
npx playwright test tests/test_smoke.spec.ts --project=firefox --reporter=line --timeout=60000
```

### 9.4 测试结果统计

| 功能编号 | 测试项 | 执行状态 | 结果 |
|----------|--------|----------|------|
| F001 | 项目管理 | 已执行 | ✅/❌ |
| F004 | Cover Points 管理 | 已执行 | ✅/❌ |
| F005 | Test Cases 管理 | 已执行 | ✅/❌ |
| F006 | 关联管理 | API 覆盖 | ✅ |
| F007 | 状态跟踪 | 已执行 | ✅/❌ |
| F009 | 排序过滤 | API 覆盖 | ✅ |
| F010 | 完成日期 | API 覆盖 | ✅ |
| F011 | 进度统计 | API 覆盖 | ✅ |
| F012 | 覆盖率计算 | 已执行 | ✅/❌ |

**说明:**
- ✅ UI/API 均覆盖
- UI 覆盖: Playwright 测试已验证
- API 覆盖: pytest 测试已验证

### 9.5 关键功能测试命令

```bash
cd /projects/management/tracker/dev

# 运行所有关键功能测试
npx playwright test tests/test_smoke.spec.ts --project=firefox --reporter=line --timeout=60000

# 运行单个功能测试
npx playwright test tests/test_smoke.spec.ts -g "F001" --project=firefox
npx playwright test tests/test_smoke.spec.ts -g "F007" --project=firefox
npx playwright test tests/test_smoke.spec.ts -g "F012" --project=firefox
```

---

## 10. 冒烟测试 (stable 专用)

### 9.1 冒烟测试用例

| ID | 测试项 | 测试步骤 | 预期结果 |
|----|--------|----------|----------|
| **S001** | 版本 API | `GET /api/version` | 返回版本信息 |
| **S002** | 项目列表 | `GET /api/projects` | 返回项目列表 |
| **S003** | 创建项目 | `POST /api/projects` | 创建成功 |
| **S004** | CP CRUD | CP 创建/读取 | CP 操作正常 |
| **S005** | TC CRUD | TC 创建/读取 | TC 操作正常 |

### 9.2 运行冒烟测试

```bash
cd stable
PYTHONPATH=. pytest tests/test_api.py -v -k sanity
```

---

## 10. 已知问题

| 问题 | 状态 | 说明 |
|------|------|------|
| v0.2 迁移 | 待完整测试 | 需要完整数据测试 |
| 前端界面 | 正常 | 无已知问题 |
| Playwright | ✅ 已完成 | Firefox 测试通过 |

---

## 10. 测试环境

| 项目 | 版本/说明 |
|------|-----------|
| Python | 3.11.6 |
| Flask | 最新 |
| SQLite | 3.x |
| pytest | 9.0.2 |
| Playwright | 最新 (playwright-mcp) |
| 数据目录 | shared/data/ |

---

## 11. 快速测试命令

### 11.1 版本启动

```bash
# 启动正式版 (stable) - 通过 systemd 管理
sudo systemctl start tracker
# 访问 http://localhost:8080

# 启动测试版 (dev)
cd dev && bash start_server_test.sh
# 访问 http://localhost:8081
```

### 11.2 测试执行（区分版本）

```bash
# ========================================
# dev 版本 - 完整测试
# ========================================
cd dev

# 完整 pytest 测试
PYTHONPATH=. pytest tests/test_api.py -v

# 生成覆盖率报告
PYTHONPATH=. coverage run -m pytest tests/test_api.py
coverage report -m
coverage html

# Playwright 冒烟测试
npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000

# BugLog 回归测试 (11 个测试用例)
npx playwright test tests/tracker.spec.ts --project=firefox

# ========================================
# stable 版本 - 冒烟测试（发布前必须）
# ========================================

# playwright_firefox.js 测试 (P001-P014)
# stable 目录已移除，测试使用 /release/tracker/current/ 代码
cd /release/tracker/current && node tests/playwright_firefox.js

# 或运行 API 冒烟测试
cd /projects/management/tracker
python3 -c "from app import create_app; app = create_app(); print('API OK')"
```

### 11.3 发布前检查清单

```bash
# 1. dev 版本完整测试 ✅
cd dev && PYTHONPATH=. pytest tests/test_api.py -v

# 2. Playwright 冒烟测试 ✅
cd dev && npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000

# 3. BugLog 回归测试 ✅
cd dev && npx playwright test tests/tracker.spec.ts --project=firefox

# 4. 演练发布（验证命令）
cd /projects/management/tracker
python3 scripts/release.py --dry-run

# 5. 实际发布
python3 scripts/release.py --version v0.3.3 --force

# 6. 验证 stable 服务
sudo systemctl status tracker
curl http://localhost:8080/api/version

# 回滚（如需要）
python3 scripts/release.py --rollback --force
```

### 11.4 生成测试

```bash
# 生成 Playwright 测试
python3 scripts/generate_tests.py --url http://localhost:8081 --output tests/tracker.spec.ts

# 运行 Playwright 测试
npx playwright test tests/tracker.spec.ts
```

---

## 12. 用户验收测试（必须手动执行）

```bash
# 访问 http://localhost:8080
# 切换到用户项目 (Debugware_65K 或 EX5)

# U001 - 整体功能验收（必须）
1. 创建测试 CP 和 TC
2. 验证状态切换
3. 导出备份文件

# U002-U005 - 推荐测试（可选）
界面体验、多项目切换、备份导出、项目恢复
```

---

## 13. 数据清理

⚠️ 只删除测试项目，保护用户项目！

```bash
cd /projects/management/tracker

python3 << 'EOF'
import json
import os

# 用户项目列表（绝不能删除）
USER_PROJECTS = ['Debugware_65K', 'EX5']

with open('shared/data/projects.json', 'r') as f:
    projects = json.load(f)

# 识别测试项目
test_patterns = ['Test', 'API', 'Dev', 'Stable', 'Final', 'Smoke', 'Coverage']
test_projects = [p for p in projects if any(p['name'].startswith(p) for p in test_patterns)]

# 保护用户项目
user_projects = [p for p in projects if p['name'] in USER_PROJECTS]

print(f"用户项目（保护）: {[p['name'] for p in user_projects]}")
print(f"测试项目（将删除）: {[p['name'] for p in test_projects]}")

# 删除测试项目数据库
for p in test_projects:
    db_file = f"shared/data/{p['name'].replace(' ', '_')}.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"  删除: {db_file}")

# 清理 projects.json
filtered = user_projects
with open('shared/data/projects.json', 'w') as f:
    json.dump(filtered, f, indent=2)

print(f"\n✅ 保留 {len(user_projects)} 个用户项目")
EOF
        os.remove(db_file)
        print(f"   ✅ 已删除: {db_file}")

# 更新 projects.json
filtered = user_projects
with open('shared/data/projects.json', 'w') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print(f"\n✅ 清理完成，保留 {len(filtered)} 个用户项目")
EOF
```

---

## 附录 A: Playwright 测试脚本模板

```javascript
// dev/tests/tracker.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Tracker UI Tests', () => {
  test.beforeAll(async ({ }) => {
    // 启动服务器
  });

  test.afterAll(async ({ }) => {
    // 清理
  });

  test('P001 - Page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:8080');
    await expect(page).toHaveTitle(/Tracker/);
  });

  test('P005 - Create new project', async ({ page }) => {
    await page.goto('http://localhost:8080');
    await page.click('button:has-text("创建")');
    await page.fill('input[name="name"]', 'PlaywrightTest');
    await page.click('button:has-text("保存")');
    await expect(page.locator('.toast')).toContainText('项目创建成功');
  });
});
```

---

**文档版本**: v0.3  
**最后更新**: 2026-02-05  
**维护者**: 小栗子 🌰
