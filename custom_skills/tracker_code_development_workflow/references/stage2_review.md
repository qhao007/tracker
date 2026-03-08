# 阶段2：代码审查 (Subagent B)

> 详细内容见原始SKILL.md段落

## 快速参考

### 调用方式
- subagent_type: "general-purpose"
- model: "opus"
- description: "Tracker代码审查"
- max_retries: 3

### 必须激活的技能
1. **Bash** - 检查脚本
2. **Explore** - 探索代码结构
3. **code-review** - 代码审查

### 必须阅读的文档
1. `/projects/management/tracker/CLAUDE.md`
2. `/projects/management/tracker/docs/DEVELOPMENT/coding_standard.md`
3. `/projects/management/tracker/docs/SPECIFICATIONS/tracker_OVERALL_SPECS.md`
4. `{spec_path}` - 规格文档

### 核心检查清单
- [ ] 前端检查脚本通过
- [ ] 代码语法正确
- [ ] 符合规格要求
- [ ] 符合 coding_standard.md 规范

### 审查决策
- 需要优化: 轮次1-3轮
- 优化通过: 进入测试阶段

### 禁止事项
- 🔴 禁止跳过前端检查脚本
- 🔴 禁止在 8080 端口调试
- 🔴 禁止 main 分支开发
- 🔴 严格禁止对非/tmp以外的目录执行 rm -rf
