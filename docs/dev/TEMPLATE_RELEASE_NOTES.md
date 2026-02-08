# Tracker v{{VERSION}} 发布报告

> **版本**: {{VERSION}} | **发布日期**: {{DATE}} | **发布时间**: {{TIME}}

---

## 发布摘要

| 项目 | 状态 |
|------|------|
| 版本 | {{VERSION}} |
| 发布日期 | {{DATE}} |
| 源版本 | {{SOURCE_VERSION}} |
| 目标版本 | {{TARGET_VERSION}} |
| Git 分支 | {{BRANCH}} |
| Git Commit | {{COMMIT}} |
| 兼容性检查 | ✅ 全部通过 |
| 代码发布 | ✅ {{SOURCE}} → {{TARGET}} |

---

## 变更内容

### 新功能
- 

### Bug 修复
- 

### 优化改进
- 

---

## 数据目录结构

```
shared/data/
├── user_data/       # 正式版数据 (stable 使用)
│   └── {{USER_PROJECT_COUNT}} 个项目数据库
│
└── test_data/       # 测试数据 (dev 使用)
    └── 测试项目数据库
```

---

## 数据统计

| 指标 | 值 |
|------|-----|
| 用户项目数量 | {{USER_PROJECT_COUNT}} |
| 数据库文件 | {{DB_FILE_COUNT}} 个 |

---

## Git 标签

| 标签 | 说明 |
|------|------|
| v{{VERSION}} | 当前发布版本 |
| v0.3.1 | 上一版本 |

---

## 访问地址

| 环境 | 地址 | 端口 |
|------|------|------|
| 内网 | http://10.0.0.8 | 8080 |
| 外网 | http://{{外网IP}} | 8080 |

---

## 服务管理

```bash
# 重启服务
sudo systemctl restart tracker

# 查看状态
sudo systemctl status tracker

# 查看日志
journalctl -u tracker -f
```

---

## 版本回滚

如需回滚到上一版本：

```bash
cd /projects/management/tracker
python3 scripts/release.py --rollback --force
```

**注意：** 回滚只恢复代码文件，用户数据不会改变。

---

## 备份位置

发布前已自动备份：

```
{{BACKUP_DIR}}
```

---

## 相关资源

- **规格书**: `docs/dev/tracker_SPECIFICATION.md`
- **测试计划**: `docs/dev/tracker_TEST_PLAN.md`
- **Git 分支策略**: 规格书 6.1 章节

---

**文档生成时间**: {{DATE}} {{TIME}}
