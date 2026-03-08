# 阶段3：UI测试开发快速参考

## ⚠️ 重要改进：必须先参考现有代码

### 选择器验证步骤（不可跳过）

1. **阅读现有UI测试**: 读取 `tests/test_ui/specs/smoke/01-smoke.spec.ts`
   - 确认登录输入框: `#loginUsername` (不是 #username!)
   - 确认登录密码: `#loginPassword`
   - 确认登录按钮: `button.login-btn`
   - 确认登录后验证: `waitForFunction` 检查 `#projectSelector`

2. **确认Tab切换**: 读取其他 integration 测试
   - `button.tab:has-text("Cover Points")`

3. **复制辅助函数**: 直接复制 `loginAsAdmin` 函数使用

## 测试命令

```bash
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/ --project=firefox
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/13-layout.spec.ts --project=firefox
```

## 核心任务

1. **选择器验证** (必做) - 先确认选择器再编写代码
2. 根据阶段1的分析开发Playwright测试用例
3. 运行测试并调试 - 必须通过！
4. 记录Bug到Buglog
5. 追加到测试报告

## 测试用例ID格式

`UI-COV-XXX` (如 UI-COV-001)

## 输出要求

- 测试文件: `tests/test_ui/specs/integration/{序号}-{功能}.spec.ts`
- 测试报告: `docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md`

## 通过标准

- **100% 测试通过** - 必须实际运行验证
- 所有发现的Bug已记录
