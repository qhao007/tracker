# 阶段4：手工测试快速参考

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

1. 根据阶段1的分析执行手工验证
2. 检查控制台错误
3. 验证CSS样式渲染
4. 记录问题到Buglog
5. 追加到测试报告

## 测试用例ID格式

`MANUAL-COV-XXX` (如 MANUAL-COV-003)

## 输出要求

- 测试报告: `docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md`

## 通过标准

- 控制台无关键错误
- 所有问题已记录
