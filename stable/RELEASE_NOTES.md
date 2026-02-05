# Tracker vv0.3 发布报告

> **版本**: v0.3 | **发布日期**: 2026-02-05 | **发布时间**: 08:20:36

---

## 发布摘要

| 项目 | 状态 |
|------|------|
| 版本 | v0.3 |
| 发布日期 | 2026-02-05 |
| 源版本 | dev |
| 目标版本 | stable |
| 兼容性检查 | ✅ 全部通过 |
| 代码发布 | ✅ dev → stable |

---

## 数据目录结构

```
shared/data/
├── user_data/       # 正式版数据 (stable 使用)
│   └── 2 个项目数据库
│
└── test_data/      # 测试数据 (dev 使用)
    └── 测试项目数据库
```

---

## 数据统计

| 指标 | 值 |
|------|-----|
| 用户项目数量 | 2 |
| 数据库文件 | 2 个 |

---

## 访问地址

| 环境 | 地址 | 端口 |
|------|------|------|
| 内网 | http://10.0.0.8 | 8080 |
| 外网 | http://外网IP | 8080 |

---

## 服务管理

```bash
# 重启服务（发布后需要）
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
stable/backup_20260205_082036
```

---

**文档生成时间**: 2026-02-05 08:20:36
