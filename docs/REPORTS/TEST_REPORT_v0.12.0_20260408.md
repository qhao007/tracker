# 测试报告 - v0.12.0 手工测试阶段 (COV_D)

**测试日期**: 2026-04-08
**测试工程师**: Claude Code (Subagent COV_D)
**测试工具**: agent-browser
**测试环境**: 8081 端口 (test_data)

---

## 手工测试执行结果

| 测试项 | 结果 |
|--------|------|
| Tab 切换 (Cover Points / Test Cases / Progress Charts / Dashboard) | PASS |
| Dashboard 显示 (Coverage Holes / Owner Distribution) | PASS |
| 数据展示正确性 (30 CP, 52 TC, 36.6% 覆盖率) | PASS |
| 控制台 JavaScript 错误检查 | PASS |
| 版本号显示 | FAIL (显示 v0.11.0 而非 v0.12.0) |

**通过**: 4
**失败**: 1
**发现问题**: 1

---

## 问题列表

| 问题 | 状态 | 说明 |
|------|------|------|
| 版本号显示为 v0.11.0 | 待修复 | VERSION 文件仍为 0.11.0，需更新 |

---

## Bug 记录

### BUG-001: 版本号显示不正确
- **严重程度**: 低
- **描述**: 页脚显示 "v0.11.0 正式版"，但当前分支为 feature/dashboard-enhancement-v0.12.0
- **根因**: `/projects/management/tracker/dev/VERSION` 文件中 `VERSION=0.11.0` 未更新
- **修复建议**: 将 VERSION 文件更新为 `VERSION=0.12.0`

---

## 测试详情

### 1. Tab 切换测试
- **Cover Points Tab**: 显示 30 CP 表格，包含 Feature/Sub-Feature/Priority 等列
- **Test Cases Tab**: 显示 52 TC 表格，包含状态标签 (PASS/FAIL/CODED/OPEN)
- **Progress Charts Tab**: 显示 "tracker.soc_dv/charts" 面包屑和图表
- **Dashboard Tab**: 显示 Coverage Holes 统计和 Owner Distribution

### 2. Dashboard 功能测试
- Coverage Holes: 显示 11 个漏洞 (4 Critical, 4 High, 3 Medium)
- Owner Distribution: 正确显示各 Owner 的 TC 分布
- 统计数据: 30 CP / 52 TC / 36.6% 覆盖率

### 3. 控制台检查
- 无 JavaScript 错误
- 无控制台警告
- API 调用正常

---

## 已知问题

1. **Playwright 浏览器安装失败**: 无法以 root 权限安装 Firefox 浏览器，导致 UI 自动化测试无法运行
2. **VERSION 文件未更新**: 需要在发布前更新版本号

---

## 测试结论

手工测试基本通过，v0.12.0 的 Dashboard 功能正常，Tab 切换流畅，数据展示正确。主要问题为版本号未更新。建议修复 VERSION 文件后进行发布。

---

*报告生成时间: 2026-04-08 11:25*
*署名: Claude Code*
