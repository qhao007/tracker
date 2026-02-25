# Tracker Daily Review Agent - 每日代码审查与分析任务

## 任务目标
每天凌晨3点自动执行，对Tracker开发版进行代码审查、行业调研、经验总结，并生成改进建议报告。

## 执行步骤

### 1. 代码审查与Bug扫描
```
1.1 切换到Tracker开发目录: cd /projects/management/tracker
1.2 获取最新代码: git fetch && git status
1.3 检查上次审查以来的变更: git diff HEAD~1
1.4 运行API测试: cd dev && python3 -m pytest tests/ -v
1.5 检查冒烟测试: bash dev/smoke_test.sh
1.6 审阅前端代码: 检查 index.html, app.js 是否有语法错误
1.7 检查Python后端: 运行 flake8 或 pylint 检查代码质量
1.8 记录发现的bug或问题
```

### 2. 芯片验证Tracking行业调研
```
2.1 使用web_search搜索以下主题（每次轮换）：
    - "chip verification tracking system best practices"
    - "IC design test case management methodology"
    - "verification database design patterns"
    - "automated test tracking system architecture"
    - "soc verification workflow management"
    - "digital chip validation tools comparison"
    - "test management system for semiconductor"
    - "verification plan tracking implementation"

2.2 使用web_fetch提取前3-5个最有价值的链接内容
2.3 对比我们的Tracker功能，找出可以改进的地方
2.4 记录关键洞察和建议
```

### 3. 前一天开发经验回顾
```
3.1 读取昨天的开发记录: memory/YYYY-MM-DD.md
3.2 读取v0.6.1相关的BUGLOG: dev/docs/tracker_BUG_RECORD.md
3.3 分析：
    - 发现了哪些bug？根本原因是什么？
    - 哪些流程导致了bug？（代码审查不足？测试覆盖不足？）
    - 开发方法有什么可以改进的？
    - 是否有重复出现的问题？
3.4 更新开发流程改进建议
```

### 4. 生成改进建议报告
```
4.1 报告存放路径: /projects/management/self_reviews/tracker-review-YYYY-MM-DD.md
4.2 报告结构：
    - 执行摘要（1-2句话）
    - 代码审查结果（bug列表、代码质量问题）
    - 行业调研发现（对比分析、改进建议）
    - 开发流程回顾（经验教训、改进建议）
    - 建议功能添加列表
    - 建议Bug修复优先级
    - 下次审查关注点

4.3 报告格式：Markdown，简洁明了
```

### 5. 发送摘要消息
```
5.1 生成报告后，发送简短摘要到用户
5.2 摘要内容：
    - 发现的关键问题数量
    - 建议的功能改进数量
    - 最重要的1-2个建议
    - 报告完整路径
```

## 输出文件
- `/projects/management/self_reviews/tracker-review-YYYY-MM-DD.md` - 完整报告

## 重要提示
- 不要修改Tracker的任何代码
- 只做分析、调研、建议
- 保持报告简洁，突出重点
- 每次搜索不同主题，避免重复
