# 阶段7：测试验收 (Subagent F)

> 详细内容见原始SKILL.md段落

## 快速参考

### 调用方式
- subagent_type: "general-purpose"
- model: "opus"
- description: "Tracker测试验收"
- max_retries: 2

### 必须激活的技能
1. **Bash** - 验证文件存在和测试结果
2. **Read** - 检查文档内容

### 必须执行的验收检查

#### 1. API测试验收 (Subagent C输出)

| 检查项 | 验收标准 |
|--------|----------|
| 新测试文件存在 | `/projects/management/tracker/dev/tests/test_api/test_api_{name}.py` |
| 测试用例数量 | >= 测试计划要求的API测试用例数 |
| 测试通过率 | 100% |
| Bug记录 | 至少记录了发现的应用代码问题 |
| 测试报告 | 存在于 `/projects/management/tracker/docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md` |

#### 2. UI测试验收 (Subagent D输出)

| 检查项 | 验收标准 |
|--------|----------|
| 新测试文件存在 | `/projects/management/tracker/dev/tests/test_ui/specs/integration/{name}.spec.ts` |
| 测试用例数量 | >= 测试计划要求的UI测试用例数 |
| 测试通过率 | >= 80% (允许环境问题导致20%失败) |
| Bug记录 | 至少记录了发现的应用代码问题 |

#### 3. 手工测试验收 (Subagent E输出)

| 检查项 | 验收标准 |
|--------|----------|
| 控制台检查 | 已执行控制台错误检查 |
| 问题记录 | 发现的问题已记录 |
| 修复验证 | 已验证问题是否修复 |

### 验证命令
```bash
# 检查API测试文件
ls /projects/management/tracker/dev/tests/test_api/test_api_*.py

# 检查UI测试文件
ls /projects/management/tracker/dev/tests/test_ui/specs/integration/*.spec.ts

# 检查测试报告
ls /projects/management/tracker/docs/REPORTS/TEST_REPORT_v{version}_*.md

# 运行API测试验证
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v --tb=short

# 检查Bug记录
grep -l "BUG-" /projects/management/tracker/docs/BUGLOG/tracker_BUG_RECORD.md
```

### 验收决策

#### 合格标准
- 所有验收检查项通过
- 或者失败项有明确说明（非阻塞性问题）

#### 迭代建议
如果不合格，给出具体迭代建议：
1. 哪个Subagent需要重做
2. 具体需要补充什么
3. 预计需要几轮迭代

### 重要
**主代理不参与实际验收判断，完全依赖测试验收Subagent的反馈**
