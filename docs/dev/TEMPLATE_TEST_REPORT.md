# Tracker vX.X 测试报告

> **测试日期**: YYYY-MM-DD
> **测试版本**: vX.X
> **测试环境**: dev (localhost:8081)
> **数据目录**: test_data

---

## 测试摘要

| 测试类型 | 总数 | 通过 | 失败 | 超时 | 通过率 |
|----------|------|------|------|------|--------|
| API 测试 | XX | XX | X | X | **XX%** |
| Playwright 冒烟测试 | XX | XX | X | X | **XX%** |
| **综合统计** | **XXX** | **XXX** | **X** | **X** | **XX%** |

---

## 测试执行时间

| 测试阶段 | 开始时间 | 完成时间 | 持续时间 |
|----------|----------|----------|----------|
| API 测试 | HH:MM:SS | HH:MM:SS | XX min |
| Playwright 冒烟测试 | HH:MM:SS | HH:MM:SS | XX min |
| **整体测试** | **HH:MM:SS** | **HH:MM:SS** | **XX min** |

---

## 1. API 测试结果

### 1.1 测试结果

| 序号 | 测试类 | 测试方法 | 状态 | 执行时间 |
|------|--------|----------|------|----------|
| 1 | TestVersionAPI | test_get_version | ✅ PASS | XXms |
| ... | ... | ... | ... | ... |
| XX | TestStatsAPI | test_get_stats | ✅ PASS | XXms |

### 1.2 失败测试

| 序号 | 测试方法 | 失败原因 | 类型 |
|------|----------|----------|------|
| - | 无 | - | - |

### 1.3 超时测试

| 序号 | 测试方法 | 超时时间 | 类型 |
|------|----------|----------|------|
| - | 无 | - | - |

### 1.4 测试命令

```bash
# 启动服务
cd dev && bash start_server.sh

# API 测试
cd dev && PYTHONPATH=. pytest tests/test_api.py -v
```

---

## 2. Playwright 冒烟测试结果

### 2.1 测试执行概况

| 序号 | 测试项 | 功能编号 | 状态 | 执行时间 | 备注 |
|------|--------|----------|------|----------|------|
| 1 | TC 状态更新 | F007 | ✅ PASS | XXs | - |
| ... | ... | ... | ... | ... | ... |

### 2.2 失败测试

| 序号 | 测试项 | 失败原因 | 类型 |
|------|--------|----------|------|
| - | 无 | - | - |

### 2.3 超时测试

| 序号 | 测试项 | 超时时间 | 类型 |
|------|----------|----------|------|
| - | 无 | - | - |

### 2.4 测试命令

```bash
cd dev && npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000
```

---

## 3. 测试环境

| 项目 | 值 |
|------|-----|
| 操作系统 | Linux 6.x.x |
| Python | X.X.X |
| Flask | - |
| SQLite | 3.x |
| pytest | X.X.X |
| Playwright | 最新 |
| 浏览器 | Firefox |
| 测试服务器 | dev (localhost:8081) |
| 测试数据 | test_data/ |

---

## 4. 结论与建议

### 4.1 测试结论

| 检查项 | 状态 | 说明 |
|--------|------|------|
| API 完整性 | ✅ 通过 | XX/XX 测试全部通过 |
| Playwright 冒烟测试 | ✅ 通过 | XX/XX 测试全部通过 |

### 4.2 修复记录

| Bug | 描述 | 修复方案 |
|-----|------|----------|
| - | 无 | - |

### 4.3 发布建议

**综合评估**: ✅ **建议发布**

- API 测试优秀 (XX%)
- Playwright 冒烟测试优秀 (XX%)

---

## 5. 执行命令记录

```bash
# 启动 dev 版本
cd dev && bash start_server.sh

# API 测试
cd dev && PYTHONPATH=. python3 -m pytest tests/test_api.py -v

# Playwright 冒烟测试
cd dev && npx playwright test tests/test_smoke.spec.ts --project=firefox --timeout=60000
```

---

## 6. 版本信息

| 项目 | 值 |
|------|-----|
| 当前版本 | vX.X |
| 发布日期 | YYYY-MM-DD |
| 测试日期 | YYYY-MM-DD |

---

## 附录

### A. 测试结果统计

| 类别 | 通过 | 失败 | 超时 | 总计 | 通过率 |
|------|------|------|------|------|--------|
| API 测试 | XX | X | X | XX | XX% |
| Playwright 冒烟测试 | XX | X | X | XX | XX% |
| **总计** | **XXX** | **X** | **X** | **XXX** | **XX%** |

### B. 失败原因分类

| 类型 | 数量 | 占比 |
|------|------|------|
| 超时 | X | XX% |
| 断言失败 | X | XX% |
| 页面错误 | X | XX% |
| API 错误 | X | XX% |
| 其他 | X | XX% |

---

**报告生成时间**: YYYY-MM-DD HH:MM:SS GMT+8
**报告执行人**: [姓名/角色]
