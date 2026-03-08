# 阶段5：测试验收快速参考

## ⚠️ 重要改进：必须实际运行测试

### 强制验证步骤（不可跳过）

**你不能仅通过检查文件存在来判定测试通过！**

#### API测试验证:
```bash
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_feedback.py -v --tb=short
```
- 记录实际运行结果
- 必须看到 `X passed` 才算通过

#### UI测试验证:
```bash
cd /projects/management/tracker/dev && npx playwright test tests/test_ui/specs/integration/13-layout.spec.ts --project=firefox
```
- 记录实际运行结果
- 必须看到 `X passed` 才算通过

## 验收检查清单

| 检查项 | 验收标准 |
|--------|----------|
| API测试完成度 | 阶段1识别的所有API测试用例已开发 |
| **API测试通过率** | **100% (必须实际运行验证)** |
| UI测试完成度 | 阶段1识别的所有UI测试用例已开发 |
| **UI测试通过率** | **100% (必须实际运行验证)** |
| 手工测试完成度 | 阶段1识别的所有手工测试项已执行 |
| Bug记录完整性 | 发现的问题已记录到 Buglog |
| 测试报告完整性 | 各阶段产出已追加到测试报告 |

## 验收决策

**合格标准**:
- 所有测试实际运行通过
- 所有验收检查项通过
- 或者失败项有明确说明（非阻塞性问题）

**需迭代标准**:
- 测试实际运行失败
- 缺少必需的测试用例
- Bug记录不完整
