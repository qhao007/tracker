# 阶段3：优化确认 (Subagent A)

> 详细内容见原始SKILL.md段落

## 快速参考

### 调用方式
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker代码优化"
- max_retries: 3

### 必须激活的技能
1. **minimax-skills:fullstack-dev** - 全栈开发技能（必须激活，获取后端API和前端集成开发指南）
2. **frontend-design** - 前端界面开发
3. **Explore** - 探索现有代码结构
4. **Bash** - 运行检查脚本

### 必须阅读的文档
1. `/projects/management/tracker/CLAUDE.md`
2. `/projects/management/tracker/docs/DEVELOPMENT/coding_standard.md`
3. 审查反馈意见（从Subagent B获取）

### 核心任务
- 根据审查意见优化代码
- 重新运行前端检查脚本
- 确保通过所有检查

### 禁止事项
- 🔴 禁止跳过前端检查脚本
- 🔴 禁止在 8080 端口调试
- 🔴 禁止 main 分支开发
- 🔴 严格禁止对非/tmp以外的目录执行 rm -rf
