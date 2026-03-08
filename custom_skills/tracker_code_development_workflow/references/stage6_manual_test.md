# 阶段6：手工测试 (Subagent E)

> 详细内容见原始SKILL.md段落

## 快速参考

### 调用方式
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker手工测试执行"
- max_retries: 2

### 必须激活的技能
1. **agent-browser** - 命令行浏览器自动化
2. **Bash** - 辅助命令
3. **mcp__plugin_playwright_playwright** - 备用浏览器工具

### 必须阅读的文档
1. `/projects/management/tracker/CLAUDE.md` - 测试命令
2. `/root/.claude/skills/agent-browser/SKILL.md` - agent-browser使用文档

### agent-browser 命令
```bash
# 打开页面
agent-browser --args "--no-sandbox" open http://localhost:8081

# 截图
agent-browser --args "--no-sandbox" screenshot /tmp/page.png

# 检查控制台错误
agent-browser --args "--no-sandbox" errors

# 查看控制台消息
agent-browser --args "--no-sandbox" console

# 交互操作
agent-browser --args "--no-sandbox" click @e1
agent-browser --args "--no-sandbox" fill "#username" "admin"

# 执行JS
agent-browser --args "--no-sandbox" eval "document.title"

# 关闭浏览器
agent-browser --args "--no-sandbox" close
```

### 适用场景
- Playwright无法稳定运行的复杂UI测试
- 需要实时观察浏览器行为的测试
- CSS/样式调试
- 交互流程验证

### 核心任务
1. **手工验证（必做）**
   - 验证Playwright难以稳定测试的UI功能
   - 检查控制台错误: `agent-browser errors`
   - 检查JavaScript运行时问题
   - 验证CSS样式渲染

2. **问题定位（必做）**
   - 复现问题并记录步骤
   - 分析控制台错误
   - 检查元素存在性和状态
   - **应用代码问题** → 确认根因 + 记录到 Buglog（**不修复**）
   - **测试代码问题** → 修复测试代码 + **记录到测试报告**（必须修复）

3. **Bug记录（必做）**
   - 应用代码问题: 记录到 `/projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md`（只记录根因，不修复）
   - **测试代码问题**: 修复细节记录到测试报告

### 测试报告要求
- 输出路径: `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{版本号}_{YYYYMMDD}.md`
- 必须追加到已有报告

### 禁止事项
- 🔴 **严格禁止在非/tmp目录以外执行 rm -rf 命令**
