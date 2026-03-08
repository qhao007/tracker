# 阶段4：API测试 (Subagent C)

> 详细内容见原始SKILL.md段落

## 快速参考

### 调用方式
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker API测试开发"
- max_retries: 3

### 必须激活的技能
1. **Bash** - 运行 pytest
2. **pytest** - API测试框架

### 必须阅读的文档
1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. `/projects/management/tracker/docs/PLANS/TRACKER_TEST_PLAN_v{version}.md` - **版本测试计划（必须阅读）**

### 测试命令
```bash
# API 测试
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v

# 特定测试文件
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_{name}.py -v
```

### 核心任务
1. **新测试用例开发（必做）**
   - 根据版本测试计划开发新测试用例
   - 测试文件命名: `test_api_{功能名}.py`
   - 位置: `/projects/management/tracker/dev/tests/test_api/`

2. **测试调试（必做）**
   - 运行测试并分析失败原因
   - **应用代码问题** → 确认根因 + 报告给主代理 + 记录到 Buglog（**不修复**）
   - **测试代码问题** → 修复测试代码 + **记录到测试报告**（必须修复）

3. **Bug记录（必做）**
   - 应用代码问题: 记录到 `/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md`（只记录根因，不修复）
   - **测试代码问题**: 修复细节记录到测试报告 (见下方测试报告格式)

### 测试报告要求
- 输出路径: `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md`
- 必须追加到已有报告
- 报告结构参考 SKILL.md 第4阶段

### 禁止事项
- 🔴 **严格禁止在非/tmp目录以外执行 rm -rf 命令**
- 禁止跳过任何测试用例
