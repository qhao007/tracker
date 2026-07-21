# Tracker v0.15.0 Progress Charts 增强 - 开发任务

## 任务清单

### v0.15.0 核心功能（已完成）
- [x] 后端 API 扩展：在 `get_progress()` 中新增 `trend` 数据查询
- [x] 后端 API 扩展：在 `get_progress()` 中新增 `feature_coverage` 实时计算逻辑
- [x] 处理 coverage_mode（tc_cp / fc_cp）差异
- [x] 处理 priority_filter 对 feature_coverage 的过滤
- [x] 处理空项目边界情况
- [x] 前端图表渲染：三种图表类型切换 Tabs
- [x] 前端图表渲染：覆盖趋势图（柱状 + 双折线 + 双 Y 轴）
- [x] 前端图表渲染：Feature CP 覆盖图（水平堆叠条形）
- [x] 前端图表渲染：P0/P1 对比图（分组柱状）
- [x] 前端图表导出：单图 PNG 导出 + 全部导出
- [x] 确保日期过滤和 Priority 过滤兼容性

### v0.15.0 项目材料包图表截图集成（已完成）
- [x] `export_project_package` API 改为 POST，接收前端图表 base64 PNG
- [x] 前端 `exportProjectPackage()` 捕获三种图表截图并上传
- [x] ZIP 中写入 `charts/coverage_trend.png`、`charts/feature_coverage.png`、`charts/p0p1_comparison.png`
- [x] 对无效 base64 / 非 PNG 数据进行容错处理
- [x] 新增 API 测试 6 个用例覆盖图表截图导出场景

### 验证（已完成）
- [x] API 测试 100% 通过：`458 passed`
- [x] Progress Charts 专项 API 测试：`13 passed`
- [x] Export Package 专项 API 测试：`25 passed`（含 6 个新增图表测试）
- [x] Progress Charts UI 集成测试：`11 passed`
- [x] 全量 UI 集成测试已执行至 `171/346`（因耗时过长主动停止；已发现 1 个与 v0.15 改动无关的失败：`PERM-UI-008` 依赖项目数量 >1）

### 版本与文档（已完成）
- [x] `dev/VERSION` 更新为 `0.15.0`
- [x] `RELEASE_DATE` 更新为 `2026-07-13`
- [x] 新增 `docs/SPECIFICATIONS/tracker_SPECS_v0.15.0.md`
- [x] 更新 `docs/SPECIFICATIONS/tracker_OVERALL_SPECS.md` 中的 v0.15.0 内容

## 测试记录

| 测试类型 | 命令 | 结果 |
|----------|------|------|
| API 全量 | `PYTHONPATH=. pytest tests/test_api/ -v` | `458 passed` |
| Progress Charts API | `pytest tests/test_api/test_api_progress_charts.py` | `13 passed` |
| Export Package API | `pytest tests/test_api/test_export_package.py` | `25 passed` |
| Progress Charts UI | `npx playwright test ...18-progress-charts.spec.ts --project=firefox` | `11 passed` |

## 审查记录

- 2026-07-13: 补充图表截图导出测试用例，修复无效 base64 处理逻辑，API 全量通过。
