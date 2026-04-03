# Tracker v0.11.0 补充版本测试计划

> **版本**: v0.11.0-supplement-test-plan
> **创建日期**: 2026-03-30
> **基于规格书**: `tracker_SPECS_v0.11.0_SUPPLEMENT.md`
> **评审报告**: `tracker_SPECS_v0.11.0_SUPPLEMENT_REVIEW.md`

---

## 1. 测试范围

### 1.1 功能测试清单

| # | 功能 | 测试类型 | 优先级 |
|---|------|----------|--------|
| 1 | PUT /api/fc/batch 批量更新 | API | P1 |
| 2 | GET /api/fc 返回 cp_ids | API | P1 |
| 3 | GET /api/projects 返回 fc_count | API | P1 |
| 4 | FC Tab 标题显示 "Functional Coverage" | UI | P2 |
| 5 | FC Tab 移除"添加 FC"和"导入 FC-CP 关联"按钮 | UI | P2 |
| 6 | CP 详情 FC Item 可点击跳转 | UI | P1 |
| 7 | FC Bin 显示关联 CP IDs 列 | UI | P1 |
| 8 | CP IDs 可点击跳转到 CP 详情 | UI | P1 |
| 9 | FC Comment 列超过 150px 截断 | UI | P2 |
| 10 | 项目对话框显示 coverage_mode 和 FC 个数 | UI | P1 |

---

## 2. API 测试用例

### 2.1 测试文件

**位置**: `dev/tests/test_api/test_api_fc_batch.py`（新建）

### 2.2 测试用例

#### FC Batch Update API 测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| API-FC-BATCH-001 | 批量更新 coverage_pct | POST /api/fc/batch with items=[{id:1, coverage_pct:98.5}] | success=true, updated=1 |
| API-FC-BATCH-002 | 批量更新 status | POST /api/fc/batch with items=[{id:1, status:"ready"}] | success=true, updated=1 |
| API-FC-BATCH-003 | 批量更新部分字段 | POST /api/fc/batch with items=[{id:1, coverage_pct:85.0}] 只更新pct | coverage_pct=85.0, status不变 |
| API-FC-BATCH-004 | 批量更新多个items | POST /api/fc/batch with items=[{id:1,...},{id:2,...}] | updated=2 |
| API-FC-BATCH-005 | 空数组 | POST /api/fc/batch with items=[] | success=true, updated=0 |
| API-FC-BATCH-006 | 部分成功部分失败 | items中包含无效id | updated=1, failed=1, errors有记录 |
| API-FC-BATCH-007 | coverage_pct超出范围-过大 | coverage_pct=150 | 返回校验错误 |
| API-FC-BATCH-008 | coverage_pct超出范围-负数 | coverage_pct=-10 | 返回校验错误 |
| API-FC-BATCH-009 | 无效status值 | status="invalid" | 返回校验错误 |
| API-FC-BATCH-010 | 缺少必填字段 | 只传coverage_pct无id | 返回校验错误 |
| API-FC-BATCH-011 | 无效JSON格式 | body为无效JSON | 返回400错误 |
| API-FC-BATCH-012 | TC-CP模式下调用 | 对TC-CP模式项目调用 | 返回错误"Not in FC-CP mode" |

### 2.3 GET /api/fc 返回 cp_ids 测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| API-FC-CPIDS-001 | 无关联CP返回空数组 | 创建FC无关联 | cp_ids=[] |
| API-FC-CPIDS-002 | 单个关联CP | FC关联1个CP | cp_ids=[1] |
| API-FC-CPIDS-003 | 多个关联CP | FC关联3个CP | cp_ids=[1,3,5]按顺序 |

### 2.4 GET /api/projects 返回 fc_count 测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| API-PROJ-FCCOUNT-001 | TC-CP模式返回fc_count=0 | 创建TC-CP项目 | fc_count=0 |
| API-PROJ-FCCOUNT-002 | FC-CP模式返回fc_count实际数量 | 创建FC-CP项目并添加FC | fc_count=实际数量 |
| API-PROJ-FCCOUNT-003 | 返回值包含coverage_mode | 查询项目列表 | 每条记录包含coverage_mode字段 |

---

## 3. UI 测试用例

### 3.1 测试文件

**位置**: `dev/tests/test_ui/specs/integration/fc_supplement.spec.ts`（新建）

### 3.2 前置条件

```typescript
// FC-CP 模式测试项目
const fcCpProject = {
  name: `TestUI_FC_Supp_${Date.now()}`,
  coverage_mode: 'fc_cp'
};

// 创建关联数据
const fcItem = {
  covergroup: 'cg_test',
  coverpoint: 'cp_test',
  bin_name: 'bin_test',
  coverage_pct: 85.0,
  status: 'ready'
};

const cpItem = {
  feature: 'feat_test',
  cover_point: 'CP_Test'
};
```

### 3.3 测试用例

#### FC Tab 标题测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| UI-FC-TITLE-001 | FC Tab显示完整标题 | 切换到FC-CP模式项目 | Tab显示"Functional Coverage"而非"FC" |

#### FC Tab 按钮移除测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| UI-FC-BTN-001 | 无添加FC按钮 | 在FC Tab页面 | 找不到"+ 添加 FC"按钮 |
| UI-FC-BTN-002 | 无导入FC-CP关联按钮 | 在FC Tab页面 | 找不到"📥 导入 FC-CP 关联"按钮 |
| UI-FC-BTN-003 | 保留导入FC按钮 | 在FC Tab页面 | "📥 导入 FC"按钮存在 |
| UI-FC-BTN-004 | 保留导出FC按钮 | 在FC Tab页面 | "📤 导出 FC"按钮存在 |

#### CP 详情 FC 跳转测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| UI-CP-FC-JUMP-001 | CP详情显示FC Item链接 | 展开CP详情 | FC Item名称可点击 |
| UI-CP-FC-JUMP-002 | 点击FC Item跳转 | 点击FC Item链接 | 切换到FC Tab |
| UI-CP-FC-JUMP-003 | 跳转后展开对应covergroup | 点击跳转 | 对应covergroup自动展开 |
| UI-CP-FC-JUMP-004 | 跳转后展开对应coverpoint | 点击跳转 | 对应coverpoint自动展开 |
| UI-CP-FC-JUMP-005 | 跳转后高亮条目 | 点击跳转 | FC条目背景色变为#fff3cd |
| UI-CP-FC-JUMP-006 | 高亮持续3秒后消失 | 高亮显示 | 3秒后背景色恢复正常 |
| UI-CP-FC-JUMP-007 | 跳转后滚动到视图 | 点击跳转 | 页面自动滚动到条目位置 |

#### FC Bin CP IDs 列测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| UI-FC-CPIDS-001 | 显示关联CP IDs | FC有关联CP | 显示CP ID列表，格式如"CP_1, CP_3" |
| UI-FC-CPIDS-002 | 无关联显示横杠 | FC无关联CP | 显示"-" |
| UI-FC-CPIDS-003 | 点击CP ID跳转 | 点击CP ID链接 | 切换到CP Tab |
| UI-FC-CPIDS-004 | 跳转后展开CP详情 | 点击CP ID跳转 | CP详情自动展开 |
| UI-FC-CPIDS-005 | 跳转后高亮CP条目 | 点击CP ID跳转 | CP条目背景色变为#fff3cd |

#### FC Comment 截断测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| UI-FC-CMT-001 | 短comment正常显示 | comment<150px | 完整显示，无省略号 |
| UI-FC-CMT-002 | 长comment截断显示 | comment>150px | 显示省略号"..." |
| UI-FC-CMT-003 | 鼠标悬停显示完整内容 | hover长comment | title属性显示完整文本 |

#### 项目对话框显示测试

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| UI-PROJ-DIALOG-001 | TC-CP模式显示TC数 | 项目列表TC-CP项目 | 显示"TC: X"，不显示"FC: X" |
| UI-PROJ-DIALOG-002 | FC-CP模式显示FC数 | 项目列表FC-CP项目 | 显示"FC: X"，不显示"TC: X" |
| UI-PROJ-DIALOG-003 | 显示coverage_mode标签 | 项目列表 | 显示"TC-CP"或"FC-CP"标签 |
| UI-PROJ-DIALOG-004 | FC-CP模式不显示TC | 项目列表FC-CP项目 | meta中不包含"TC:" |

#### 关联高亮逻辑测试 (v0.11.0 Bug-122)

| ID | 测试名称 | 测试步骤 | 预期结果 |
|----|----------|----------|----------|
| UI-CP-LINK-001 | TC-CP模式未关联TC的CP应该高亮 | TC-CP模式下创建无关联CP | CP名称显示红色（unlinked class） |
| UI-CP-LINK-002 | TC-CP模式有关联TC的CP正常显示 | TC-CP模式下创建有关联CP | CP名称正常显示，无unlinked class |
| UI-CP-LINK-003 | FC-CP模式未关联FC的CP应该高亮 | FC-CP模式下创建无关联CP | CP名称显示红色（unlinked class） |
| UI-CP-LINK-004 | FC-CP模式有关联FC的CP正常显示 | FC-CP模式下创建有关联CP | CP名称正常显示，无unlinked class |
| UI-TC-LINK-001 | TC-CP模式未关联CP的TC应该高亮 | TC-CP模式下创建无关联TC | TC名称显示红色（unlinked class） |
| UI-TC-LINK-002 | FC-CP模式TC不高亮 | FC-CP模式下创建TC | TC名称正常显示，无unlinked class |
| UI-FC-LINK-001 | 未关联CP的FC应该高亮 | FC-CP模式下创建无关联FC | FC行背景色为#fff3cd |
| UI-FC-LINK-002 | 有关联CP的FC正常显示 | FC-CP模式下创建有关联FC | FC行背景色正常（白色） |

---

## 4. 测试执行

### 4.1 执行顺序

```
1. API 测试（可并行）
   ├── test_api_fc_batch.py (12 cases)
   ├── test_api_fc_cpids.py (3 cases)
   └── test_api_project_fccount.py (3 cases)
   
2. UI 测试（顺序执行）
   └── fc_supplement.spec.ts (26 cases)
```

### 4.2 执行命令

```bash
cd /projects/management/tracker/dev

# API 测试
PYTHONPATH=. pytest tests/test_api/test_api_fc_batch.py -v
PYTHONPATH=. pytest tests/test_api/ -k "fc_batch or fc_cpids or proj_fccount" -v

# UI 测试
PLAYWRIGHT_BROWSERS_PATH=/tmp/.playwright HOME=/home/hqi XDG_RUNTIME_DIR=/tmp \
  npx playwright test tests/test_ui/specs/integration/fc_supplement.spec.ts --project=firefox

# 完整补充测试套件
PYTHONPATH=. pytest tests/test_api/ -v
PLAYWRIGHT_BROWSERS_PATH=/tmp/.playwright HOME=/home/hqi XDG_RUNTIME_DIR=/tmp \
  npx playwright test tests/test_ui/specs/integration/fc_supplement.spec.ts --project=firefox
```

### 4.3 预期结果

| 测试类型 | 用例数 | 预计时间 |
|----------|--------|----------|
| API 测试 | 18 | ~2 min |
| UI 测试 | 18 | ~5 min |
| **总计** | **44** | **~10 min** |

---

## 5. 验收标准

### 5.1 API 验收

| # | 标准 | 测试ID |
|---|------|--------|
| 1 | `/api/fc/batch` 支持批量更新 coverage_pct | API-FC-BATCH-001 |
| 2 | `/api/fc/batch` 支持批量更新 status | API-FC-BATCH-002 |
| 3 | `/api/fc/batch` 部分更新正常工作 | API-FC-BATCH-003 |
| 4 | `/api/fc/batch` 空数组返回 updated: 0 | API-FC-BATCH-005 |
| 5 | `/api/fc/batch` 部分成功返回正确统计 | API-FC-BATCH-006 |
| 6 | `/api/fc/batch` 校验 coverage_pct 范围 (0-100) | API-FC-BATCH-007,008 |
| 7 | `/api/fc/batch` 校验 status 值 | API-FC-BATCH-009 |
| 8 | `/api/fc/batch` 校验必填字段 | API-FC-BATCH-010 |
| 9 | `/api/fc/batch` 非 FC-CP 模式返回错误 | API-FC-BATCH-012 |
| 10 | `/api/fc` 返回 cp_ids 字段 | API-FC-CPIDS-001~003 |
| 11 | `/api/projects` 返回 fc_count 字段 | API-PROJ-FCCOUNT-001~003 |

### 5.2 UI 验收

| # | 标准 | 测试ID |
|---|------|--------|
| 12 | FC Tab 标题显示 "Functional Coverage" | UI-FC-TITLE-001 |
| 13 | FC Tab 移除"添加 FC"按钮 | UI-FC-BTN-001 |
| 14 | FC Tab 移除"导入 FC-CP 关联"按钮 | UI-FC-BTN-002 |
| 15 | FC Tab 保留"导入 FC"按钮 | UI-FC-BTN-003 |
| 16 | FC Tab 保留"导出 FC"按钮 | UI-FC-BTN-004 |
| 17 | CP 详情中 FC Item 可点击 | UI-CP-FC-JUMP-001 |
| 18 | 点击 FC Item 切换到 FC Tab | UI-CP-FC-JUMP-002 |
| 19 | 跳转后自动展开 covergroup/coverpoint | UI-CP-FC-JUMP-003,004 |
| 20 | 跳转后高亮持续 3 秒 | UI-CP-FC-JUMP-005,006 |
| 21 | 跳转后自动滚动到位置 | UI-CP-FC-JUMP-007 |
| 22 | FC Bin 显示关联 CP IDs | UI-FC-CPIDS-001 |
| 23 | FC 无关联显示 "-" | UI-FC-CPIDS-002 |
| 24 | CP IDs 可点击跳转到 CP 详情 | UI-FC-CPIDS-003 |
| 25 | 跳转后展开 CP 详情并高亮 | UI-FC-CPIDS-004,005 |
| 26 | FC Comment 超过 150px 截断 | UI-FC-CMT-001,002 |
| 27 | FC Comment 鼠标悬停显示完整 | UI-FC-CMT-003 |
| 28 | TC-CP 模式显示 TC count | UI-PROJ-DIALOG-001 |
| 29 | FC-CP 模式显示 FC count | UI-PROJ-DIALOG-002 |
| 30 | 项目列表显示 coverage_mode 标签 | UI-PROJ-DIALOG-003 |

### 5.3 高亮逻辑验收 (BUG-122)

| # | 标准 | 测试ID |
|---|------|--------|
| 31 | TC-CP 模式：未关联 TC 的 CP 高亮 | UI-CP-LINK-001 |
| 32 | TC-CP 模式：有关联 TC 的 CP 正常 | UI-CP-LINK-002 |
| 33 | FC-CP 模式：未关联 FC 的 CP 高亮 | UI-CP-LINK-003 |
| 34 | FC-CP 模式：有关联 FC 的 CP 正常 | UI-CP-LINK-004 |
| 35 | TC-CP 模式：未关联 CP 的 TC 高亮 | UI-TC-LINK-001 |
| 36 | FC-CP 模式：TC 不高亮 | UI-TC-LINK-002 |
| 37 | 未关联 CP 的 FC 高亮 | UI-FC-LINK-001 |
| 38 | 有关联 CP 的 FC 正常显示 | UI-FC-LINK-002 |

---

## 6. 测试数据清理

### 6.1 API 测试清理

```python
@pytest.fixture
def cleanup_fc(client, test_project):
    """自动清理测试 FC"""
    created_ids = []
    yield created_ids
    for fc_id in created_ids:
        try:
            client.delete(f'/api/fc/{fc_id}?project_id={test_project["id"]}')
        except:
            pass
```

### 6.2 UI 测试清理

```typescript
// 在 fc_supplement.spec.ts 中使用 cleanup.ts
import { cleanupProjectData } from '../utils/cleanup';

test.afterEach(async () => {
  await cleanupProjectData(page, 5);
});
```

---

## 7. 风险与注意事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| FC-CP 模式项目切换后 FC 数据丢失 | 高 | 测试前确保数据完整 |
| 跳转后页面状态不一致 | 中 | 使用 beforeEach 确保初始状态 |
| CP IDs 关联复杂场景 | 中 | 使用简单的 1:1 关联测试 |

---

## 8. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.11.0-supplement-test-plan | 2026-03-30 | 初始版本 |

---

**文档创建时间**: 2026-03-30
**创建人**: OpenClaw
