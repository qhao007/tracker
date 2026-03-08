# 阶段1：代码开发 (Subagent A)

> 详细内容见原始SKILL.md段落

## 快速参考

### 调用方式
- subagent_type: "general-purpose"
- model: "sonnet"
- description: "Tracker代码开发"

### 必须激活的技能
1. **frontend-design** - 前端界面开发
2. **Explore** - 探索现有代码结构
3. **Bash** - 运行检查脚本

### 必须阅读的文档
1. `/projects/management/tracker/CLAUDE.md`
2. `/projects/management/tracker/docs/DEVELOPMENT/coding_standard.md`
3. `/projects/management/tracker/docs/SPECIFICATIONS/tracker_OVERALL_SPECS.md`
4. `{spec_path}` - 规格文档

### 核心检查清单
- [ ] 前端检查脚本通过 (bash check_frontent.sh)
- [ ] 代码语法正确
- [ ] 符合规格要求
- [ ] 符合 coding_standard.md 规范
- [ ] API 路由正确注册
- [ ] 前端关键函数完整

### 禁止事项
- 🔴 禁止跳过前端检查脚本
- 🔴 禁止在 8080 端口调试
- 🔴 禁止 main 分支开发
- 🔴 禁止 develop 直接开发
- 🔴 严格禁止对非/tmp以外的目录执行 rm -rf

### 测试服务器
```bash
cd /projects/management/tracker/dev && ./start_server_test.sh
```
