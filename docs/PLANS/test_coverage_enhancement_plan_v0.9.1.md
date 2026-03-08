# Test Coverage Enhancement Plan - v0.9.1

> **版本**: v0.9.1 | **文件名**: test_coverage_enhancement_plan_v0.9.1.md  
> **创建日期**: 2026-03-08  
> **类型**: 测试覆盖增强计划  
> **关联测试报告**: `TEST_REPORT_v0.9.1_20260308.md`

---

## 1. 概述

本计划基于 v0.9.1 测试报告的深度审查，分析测试覆盖的薄弱环节，并提出改进建议。目标是提升后续版本的测试完整性和可靠性。

---

## 2. 审查发现的问题

### 2.1 问题汇总

| 问题 ID | 规格书要求 | 测试覆盖情况 | 严重程度 |
|---------|------------|--------------|----------|
| COV-001 | REQ-001: CP 覆盖率左右布局 | 无专门 UI 测试 | 中 |
| COV-002 | REQ-002: 反馈文件生成验证 | 未明确验证文件写入 | 低 |
| COV-003 | ISSUE-014: switchTab 非事件调用 | 无专项测试 | 低 |
| COV-004 | UI 测试 session 隔离 | 存在潜在状态污染 | 低 |

### 2.2 问题详细说明

#### COV-001: REQ-001 缺少 UI 测试

**问题描述**:
- 规格书要求验证 CP 表格覆盖率信息为左右显示
- 当前仅通过代码审查确认 CSS 实现
- 未通过 Playwright 测试验证实际布局效果

**影响**:
- 可能存在浏览器兼容性问题未被发现
- 视觉还原度无法保证

**建议测试用例**:
```typescript
// 建议添加到 tests/test_ui/specs/integration/
it('CP覆盖率信息应为左右布局', async ({ page }) => {
  await page.goto('http://localhost:8081');
  await login(page, 'admin', 'admin123');
  
  // 获取覆盖率单元格的布局
  const coverageCell = page.locator('.coverage-wrapper').first();
  await expect(coverageCell).toHaveCSS('display', 'flex');
  
  // 验证覆盖率 badge 和详情为并排显示
  const badge = coverageCell.locator('.coverage-badge');
  const detail = coverageCell.locator('.coverage-detail');
  
  const badgeBox = await badge.boundingBox();
  const detailBox = await detail.boundingBox();
  
  // 验证水平排列（y 坐标相近）
  expect(Math.abs(badgeBox.y - detailBox.y)).toBeLessThan(10);
});
```

---

#### COV-002: 反馈文件生成未验证

**问题描述**:
- API 测试验证了 `/api/feedback` 返回成功
- 但未验证反馈 JSON 文件实际写入 `user_data/feedbacks/` 目录
- 手工测试也未明确检查文件生成

**影响**:
- API 返回成功但文件写入失败时无法发现

**建议测试用例**:
```python
# 建议添加到 test_api_feedback.py
def test_feedback_file_created():
    """验证反馈提交后文件正确生成"""
    # ... 提交反馈 ...
    
    feedback_dir = Path('shared/data/test_data/feedbacks')
    files = list(feedback_dir.glob('FEEDBACK_*.json'))
    
    assert len(files) > 0, "反馈文件未生成"
    
    # 验证文件内容
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    with open(latest_file) as f:
        data = json.load(f)
    
    assert data['type'] == 'bug'
    assert 'title' in data
    assert 'created_at' in data
```

---

#### COV-003: switchTab 非事件调用场景未测试

**问题描述**:
- ISSUE-014 要求确保非事件调用场景正常工作
- 当前仅验证了通过 HTML onclick 调用的情况
- 代码中可能存在直接调用 `switchTab('cp')` 的场景未测试

**影响**:
- 边缘场景可能存在功能异常

**建议**:
- 扫描代码中所有 `switchTab` 调用
- 添加针对性测试覆盖直接函数调用场景

---

#### COV-004: UI 测试 Session 隔离问题

**问题描述**:
- 报告提及 Playwright 冒烟测试存在 session 隔离问题
- 测试间可能存在状态污染

**建议修复**:
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    testIsolation: true,  // 显式启用测试隔离
    contextOptions: {
      locale: 'zh-CN'
    }
  },
  
  // 每个测试后清理
  teardown: async ({ browser }) => {
    // 清理浏览器上下文
  }
});
```

---

## 3. 改进建议

### 3.1 短期改进（下一个版本）

| 建议 | 优先级 | 预计工作量 |
|------|--------|------------|
| 为 REQ-001 添加 UI 布局测试 | 中 | 1h |
| 添加反馈文件生成验证 | 低 | 0.5h |
| 修复 Playwright testIsolation 配置 | 低 | 0.5h |

### 3.2 长期改进（持续优化）

| 建议 | 优先级 | 说明 |
|------|--------|------|
| 建立视觉回归测试基线 | 低 | 使用 Applitools 或类似工具 |
| 完善边缘场景测试覆盖 | 中 | 梳理代码中的边缘调用路径 |
| 添加 API 响应完整性验证 | 中 | 验证文件实际写入、数据库实际变更 |

---

## 4. 实施计划

### 4.1 下版本迭代任务

```
[ ] 任务 1: 添加 REQ-001 UI 布局测试
    - 文件: tests/test_ui/specs/integration/13-layout.spec.ts
    - 负责人: Claude Code
    - 预估: 1h

[ ] 任务 2: 添加反馈文件生成验证
    - 文件: tests/test_api/test_api_feedback.py
    - 负责人: Claude Code
    - 预估: 0.5h

[ ] 任务 3: 修复 Playwright 配置
    - 文件: playwright.config.ts
    - 负责人: Claude Code
    - 预估: 0.5h
```

---

## 5. 总结

v0.9.1 版本的测试整体质量较高，核心功能测试覆盖完整。本次审查发现的问题均为"建议改进"级别，**不影响当前版本发布**。

建议在后续版本迭代中逐步完善测试覆盖，特别是：
1. UI 布局验证（COV-001）
2. 副作用验证（COV-002）

---

**文档创建时间**: 2026-03-08  
**创建人**: 小栗子 🌰
