# Tracker v0.9.1 版本测试计划

> **版本**: v0.9.1
> **创建日期**: 2026-03-07
> **关联规格书**: `/projects/management/tracker/docs/SPECIFICATIONS/tracker_v0.9.1_SPEC.md`

---

## 1. 测试范围

### 1.1 功能测试范围

| # | 功能 | 测试类型 | 优先级 |
|---|------|----------|--------|
| 1 | CP 页面覆盖率左右布局显示 | UI 测试 | P1 |
| 2 | 关于对话框增加用户反馈功能 | API + UI 测试 | P2 |
| 3 | switchTab 函数改进 | UI 测试 | P3 |
| 4 | 常量替换 | UI 测试 | P2 |

### 1.2 测试环境

| 项目 | 值 |
|------|-----|
| 测试服务器 | http://localhost:8081 |
| 浏览器 | Firefox (Playwright) |
| 测试框架 | Playwright + pytest |

---

## 2. 测试策略

### 2.1 冒烟测试

每次代码提交前必须执行的测试：

```bash
# ESLint 检查
cd /projects/management/tracker/dev && bash check_frontent.sh

# API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v --reruns 2

# 冒烟测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/smoke/ --project=firefox
```

### 2.2 回归测试

本版本功能变更较小，以回归测试为主，确保现有功能不受影响。

### 2.3 新功能测试

针对 REQ-002 用户反馈功能，需要：
- API 测试：验证 POST /api/feedback 接口
- UI 测试：验证反馈表单提交流程

---

## 3. 测试用例

### 3.1 REQ-001: CP 覆盖率左右布局

| 用例 ID | 说明 | 测试类型 | 状态 |
|---------|------|----------|------|
| UI-CP-001 | CP 表格覆盖率显示为左右布局 | UI | ⏳ 待实现 |
| UI-CP-002 | 移动端 CP 表格显示正常 | UI | ⏳ 待实现 |

### 3.2 REQ-002: 用户反馈功能

#### API 测试用例

| 用例 ID | 说明 | 测试类型 | 状态 |
|---------|------|----------|------|
| API-FB-001 | 提交反馈接口 - 成功 | API | ⏳ 待实现 |
| API-FB-002 | 提交反馈接口 - 未登录 | API | ⏳ 待实现 |
| API-FB-003 | 提交反馈接口 - 参数验证 | API | ⏳ 待实现 |

#### UI 测试用例

| 用例 ID | 说明 | 测试类型 | 状态 |
|---------|------|----------|------|
| UI-FB-001 | 反馈标签页存在 | UI | ⏳ 待实现 |
| UI-FB-002 | 反馈表单类型选择 | UI | ⏳ 待实现 |
| UI-FB-003 | 反馈表单必填验证 | UI | ⏳ 待实现 |
| UI-FB-004 | 反馈提交成功提示 | UI | ⏳ 待实现 |
| UI-FB-005 | 反馈列表显示 | UI | ⏳ 待实现 |

### 3.3 ISSUE-014: switchTab 改进

| 用例 ID | 说明 | 测试类型 | 状态 |
|---------|------|----------|------|
| UI-TAB-001 | Tab 切换功能正常 | UI | ⏳ 待实现 |
| UI-TAB-002 | 非事件调用场景正常 | UI | ⏳ 待实现 |

### 3.4 ISSUE-015: 常量替换

| 用例 ID | 说明 | 测试类型 | 状态 |
|---------|------|----------|------|
| UI-CONST-001 | 登录功能正常 | UI | ⏳ 待实现 |
| UI-CONST-002 | 项目切换正常 | UI | ⏳ 待实现 |
| UI-CONST-003 | API 请求正常 | UI | ⏳ 待实现 |

---

## 4. 执行计划

### 4.1 开发阶段测试

| 阶段 | 测试内容 | 执行时机 |
|------|----------|----------|
| 开发中 | 冒烟测试 | 每次提交前 |
| 开发完成 | API 测试 | REQ-002 API 开发完成后 |
| 开发完成 | UI 集成测试 | 各功能开发完成后 |
| 发布前 | 完整回归测试 | 版本发布前 |

### 4.2 测试命令

```bash
# 开发版服务启动
cd /projects/management/tracker/dev && ./start_server_test.sh

# API 测试 (本地开发)
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v --reruns 2

# UI 冒烟测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/smoke/ --project=firefox

# UI 集成测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/ --project=firefox
```

---

## 5. 风险评估

| 风险 | 影响 | 可能性 | 应对措施 |
|------|------|--------|----------|
| REQ-002 文件写入权限 | 中 | 低 | 使用 user_data 目录已有权限 |
| 反馈 JSON 格式问题 | 低 | 低 | 添加格式验证 |

---

## 6. 验收标准

### 6.1 发布前必须通过

- [ ] ESLint 检查通过
- [ ] API 测试 207/207 通过
- [ ] 冒烟测试 20/20 通过
- [ ] REQ-002 API 测试通过
- [ ] REQ-002 UI 测试通过

---

## 7. 相关文档

| 文档 | 路径 |
|------|------|
| 版本规格书 | `/projects/management/tracker/docs/SPECIFICATIONS/tracker_v0.9.1_SPEC.md` |
| API 测试策略 | `docs/DEVELOPMENT/API_TESTING_STRATEGY.md` |
| UI 测试策略 | `docs/DEVELOPMENT/UI_TESTING_STRATEGY.md` |
| 测试执行计划 | `docs/DEVELOPMENT/TEST_EXECUTION_PLAN.md` |

---

**文档创建时间**: 2026-03-07
**创建人**: 小栗子 🌰
