# 阶段5：UI测试 (Subagent D)

> 详细内容见原始SKILL.md段落

## 快速参考

### 调用方式
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker Playwright UI测试开发"
- max_retries: 3

### 必须激活的技能
1. **Bash** - 运行 Playwright
2. **Playwright** - UI测试框架

### 必须阅读的文档
1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. `/projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{version}.md` - **版本测试计划（必须阅读）**

### 测试命令
```bash
# UI 冒烟测试
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/smoke/ --project=firefox

# 特定测试文件
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/12-feedback.spec.ts --project=firefox
```

### 核心任务
1. **新测试用例开发（必做）**
   - 根据版本测试计划开发新测试用例
   - 测试文件命名: `{序号}-{功能名}.spec.ts`
   - 位置: `/projects/management/tracker/dev/tests/test_ui/specs/integration/`

2. **测试调试（必做）**
   - 运行测试并分析失败原因
   - **应用代码问题** → 确认根因 + 报告给主代理 + 记录到 Buglog（**不修复**）
   - **测试代码问题** → 修复测试代码 + **记录到测试报告**（必须修复）
   - **session隔离问题** → 修复测试代码添加清理逻辑 + **记录到测试报告**（必须修复）

3. **Bug记录（必做）**
   - 应用代码问题: 记录到 `/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md`（只记录根因，不修复）
   - **测试代码问题**: 修复细节记录到测试报告 (见下方测试报告格式)

### 测试报告要求
- 输出路径: `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md`
- 必须追加到已有报告
- 报告结构参考 SKILL.md 第5阶段

### 通过标准
- UI 冒烟测试 100% 通过
- UI 版本测试计划规定的新测试用例 100% 通过

### 禁止事项
- 🔴 **严格禁止在非/tmp目录以外执行 rm -rf 命令**
- 禁止跳过任何测试用例
- 禁止忽略session隔离问题
