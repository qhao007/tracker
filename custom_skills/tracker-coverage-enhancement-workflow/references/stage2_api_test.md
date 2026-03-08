# 阶段2：API测试开发快速参考

## ⚠️ 重要改进：必须先验证环境

### 环境验证步骤（不可跳过）

1. **读取 Flask 配置**:
   ```bash
   cat /projects/management/tracker/dev/app/__init__.py | grep -A5 "create_app"
   ```

2. **确认测试模式 DATA_DIR**:
   - 找到 `app.config['DATA_DIR'] = ...`
   - 确认测试模式下的实际路径

3. **验证目录存在**:
   ```bash
   ls -la {确认的路径}/feedbacks/
   ```

## 测试命令

```bash
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/ -v
cd /projects/management/tracker/dev && PYTHONPATH=. pytest tests/test_api/test_api_{name}.py -v
```

## 核心任务

1. **环境验证** (必做) - 先确认路径再编写代码
2. 根据阶段1的分析开发测试用例
3. 运行测试并调试 - 必须通过！
4. 记录Bug到Buglog
5. 更新测试报告

## 测试用例ID格式

`API-COV-XXX` (如 API-COV-002)

## 输出要求

- 测试文件: `tests/test_api/test_api_{功能}.py`
- 测试报告: `docs/REPORTS/TEST_REPORT_v{version}_{YYYYMMDD}.md`

## 通过标准

- **100% 测试通过** - 必须实际运行验证
- 所有发现的Bug已记录
