# Tracker Code Development Workflow 优化方案

> 创建日期: 2026-03-08
> 状态: 待执行

---

## 一、优化目标

1. 让技能更容易被触发 (更pushy的description)
2. 添加测试用例验证技能效果 (evals)
3. 拆分到references/实现渐进式加载
4. 添加验证脚本确保交付物完整

---

## 二、优化项清单

### P0: 更新Description (5分钟)

**当前描述**:
```yaml
description: Tracker项目代码开发工作流，通过7个阶段子代理完成...
```

**优化后描述**:
```yaml
description: This skill should be used when the user wants to develop new features for Tracker (芯片验证管理系统), including Flask backend API development, frontend UI implementation, pytest API testing, Playwright UI testing, or needs to run the complete 7-stage development workflow. Must use this workflow for any Tracker v0.x.x feature development.
```

---

### P1: 创建Evals测试用例 (30分钟)

创建 `evals/evals.json` 包含2-3个测试用例:
- eval-1: 完整工作流执行
- eval-2: API测试开发与修复

**注意**: 不执行evals测试，避免污染代码库

---

### P2: 拆分到References结构 (1小时)

目标结构:
```
tracker_code_development_workflow/
├── SKILL.md                    # 精简版 (~200行)
├── evals/
│   └── evals.json             # 测试用例
├── scripts/
│   ├── verify_deliverables.py  # 验证脚本
│   └── run_tests.py           # 测试执行脚本
└── references/
    ├── stage1_development.md   # 阶段1详细Prompt
    ├── stage2_review.md        # 阶段2详细Prompt
    ├── stage3_optimize.md      # 阶段3详细Prompt
    ├── stage4_api_test.md      # 阶段4详细Prompt
    ├── stage5_ui_test.md       # 阶段5详细Prompt
    ├── stage6_manual_test.md   # 阶段6详细Prompt
    └── stage7_acceptance.md   # 阶段7详细Prompt
```

---

### P3: 添加验证脚本 (30分钟)

- `scripts/verify_deliverables.py` - 检查交付物
- `scripts/run_tests.py` - 统一测试入口

---

## 三、执行记录

| 序号 | 优化项 | 状态 | 日期 |
|------|--------|------|------|
| P0 | 更新Description | ✅ 已完成 | 2026-03-08 |
| P1 | 创建Evals | ✅ 已完成 | 2026-03-08 |
| P2 | 拆分References | ✅ 已完成 | 2026-03-08 |
| P3 | 添加验证脚本 | ✅ 已完成 | 2026-03-08 |

## 四、P0&P1执行详情

### P0 - Description更新
- 修改前: 纯中文描述，触发词不够明确
- 修改后: 中英双语 + pushy描述 + 明确触发场景

### P1 - Evals创建
- 创建文件: evals/evals.json
- 包含4个测试用例:
  1. 完整工作流执行
  2. Subagent C API测试阶段
  3. Subagent D UI测试阶段
  4. Subagent F 测试验收阶段
- **重要**: 未执行测试，避免污染代码库

### P2 - 拆分References
- 创建文件: references/stage{1-7}_*.md
- 包含7个阶段的详细快速参考:
  - stage1_development.md
  - stage2_review.md
  - stage3_optimize.md
  - stage4_api_test.md
  - stage5_ui_test.md
  - stage6_manual_test.md
  - stage7_acceptance.md

### P3 - 添加验证脚本
- 创建 scripts/verify_deliverables.py - 交付物验证脚本
- 创建 scripts/run_tests.py - 统一测试入口脚本

---

## 四、后续迭代建议

1. 运行evals测试验证技能效果
2. 根据测试结果优化Prompt模板
3. 优化description提高触发准确性
