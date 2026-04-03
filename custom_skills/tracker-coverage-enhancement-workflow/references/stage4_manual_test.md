# 阶段4：手工测试快速参考

## ⚠️ 必须激活的技能

**在开始手工测试前，必须先激活 `playwright-debug` 技能！**

```bash
使用 Skill 工具激活技能:
skill: "playwright-debug"
```

**playwright-debug 技能提供**:
- Playwright 测试调试最佳实践
- Tracker 项目特有的沙箱环境问题处理
- 浏览器自动化问题排查指南

## agent-browser 命令

```bash
agent-browser --args "--no-sandbox" open http://localhost:8081
agent-browser --args "--no-sandbox" screenshot /tmp/page.png
agent-browser --args "--no-sandbox" errors
agent-browser --args "--no-sandbox" console
agent-browser --args "--no-sandbox" click @e1
agent-browser --args "--no-sandbox" fill "#username" "admin"
agent-browser --args "--no-sandbox" close
```

## 核心任务

1. **激活 playwright-debug 技能** (必做)
2. 根据阶段1的分析执行手工验证
3. 检查控制台错误
4. 验证CSS样式渲染
5. 记录问题到Buglog
6. 追加到测试报告

## 测试用例ID格式

`MANUAL-COV-XXX` (如 MANUAL-COV-003)

## 输出要求

- 测试报告: `docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md`

## 通过标准

- 控制台无关键错误
- 所有问题已记录
