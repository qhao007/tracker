# Tracker 生产环境用户管理指南 v1.0

> 生产环境用户创建必须遵循本指南，以避免破坏数据库或导致已有用户无法登录。

---

## 目录

1. [环境信息](#环境信息)
2. [创建方式对比](#创建方式对比)
3. [方式一：通过 UI 创建用户（推荐）](#方式一通过-ui-创建用户推荐)
4. [方式二：通过 API 创建用户](#方式二通过-api-创建用户)
5. [方式三：批量创建用户（API）](#方式三批量创建用户api)
6. [⚠️ 关键安全注意事项](#关键安全注意事项)
7. [常见问题处理](#常见问题处理)

---

## 环境信息

| 项目 | 值 |
|------|-----|
| 生产服务地址 | http://localhost:8080 |
| 用户数据库 | `/projects/management/tracker/shared/data/user_data/users.db` |
| 项目数据库 | `/projects/management/tracker/shared/data/user_data/*.db` |

---

## 创建方式对比

| 方式 | 优点 | 缺点 |
|------|------|------|
| **UI 创建（推荐）** | 安全、无需技术操作、自动验证 | 需要 admin 账号登录 |
| **API 创建** | 可单个人创建 | 需要编写脚本、需要 admin token |
| **API 批量创建** | 一次性创建多个用户 | 需要编写脚本、密码固定为 123456 |

---

## 方式一：通过 UI 创建用户（推荐）

### 操作步骤

1. **登录 admin 账号**
   - 访问 http://localhost:8080
   - 使用 admin 账号登录

2. **进入用户管理**
   - 点击页面右上角的用户名
   - 选择「用户管理」（仅 admin 可见）

3. **创建新用户**
   - 点击「添加用户」按钮
   - 填写用户名、密码、选择角色
   - 点击「保存」

### 角色说明

| 角色 | 权限 | 说明 |
|------|------|------|
| `admin` | 全部权限 | 仅初始 admin 账号，不推荐创建更多 admin |
| `user` | 读写权限 | 普通项目操作者 |
| `guest` | 只读权限 | 仅查看项目数据，无需密码 |

---

## 方式二：通过 API 创建用户

### 前提条件

- 拥有 admin 账号
- 获取 session token（通过登录获取）

### API 接口

```
POST /api/users
```

### 请求头

```bash
Content-Type: application/json
Cookie: session=<your_session_token>
```

### 请求体

```json
{
  "username": "新用户名",
  "password": "密码",
  "role": "user"  // 或 guest
}
```

### cURL 示例

```bash
# 1. 先登录获取 session
curl -c cookies.txt -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 创建新用户
curl -b cookies.txt -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"password123","role":"user"}'
```

### Python 脚本示例

```python
import requests

BASE_URL = "http://localhost:8080"

# 登录获取 session
session = requests.Session()
login_data = {"username": "admin", "password": "admin123"}
session.post(f"{BASE_URL}/api/login", json=login_data)

# 创建用户
new_user = {
    "username": "testuser",
    "password": "SecurePass123!",
    "role": "user"  # 或 guest
}
response = session.post(f"{BASE_URL}/api/users", json=new_user)
print(response.json())
```

### 方式三：批量创建用户（API）

> 适用于一次性创建多个普通用户场景

#### API 接口

```
POST /api/users/batch
```

#### 请求头

```bash
Content-Type: application/json
Cookie: session=<your_session_token>
```

#### 请求体

```json
{
  "users": [
    {"username": "zhangsan"},
    {"username": "lisi"},
    {"username": "wangwu"}
  ]
}
```

**说明**：
- 密码固定为 `123456`（响应中返回）
- 角色固定为 `user`（普通用户）
- 单次最多创建 50 个用户

#### 响应示例

```json
{
  "success": true,
  "created": 3,
  "failed": 0,
  "password": "123456",
  "results": [
    {"username": "zhangsan", "status": "created", "id": 10},
    {"username": "lisi", "status": "created", "id": 11},
    {"username": "wangwu", "status": "created", "id": 12}
  ]
}
```

#### cURL 示例

```bash
# 1. 先登录获取 session
curl -c cookies.txt -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 批量创建用户
curl -b cookies.txt -X POST http://localhost:8080/api/users/batch \
  -H "Content-Type: application/json" \
  -d '{"users":[{"username":"user1"},{"username":"user2"},{"username":"user3"}]}'
```

#### Python 脚本示例

```python
import requests

BASE_URL = "http://localhost:8080"

# 登录获取 session
session = requests.Session()
login_data = {"username": "admin", "password": "admin123"}
session.post(f"{BASE_URL}/api/login", json=login_data)

# 批量创建用户
users = [
    {"username": "zhangsan"},
    {"username": "lisi"},
    {"username": "wangwu"}
]
response = session.post(f"{BASE_URL}/api/users/batch", json={"users": users})
result = response.json()

print(f"成功创建: {result['created']} 个用户")
print(f"默认密码: {result['password']}")
print(f"结果: {result['results']}")
```

#### 错误响应

| 错误码 | 说明 |
|--------|------|
| 400 | 请求格式错误或超过50个用户限制 |
| 401 | 未登录 |
| 403 | 无管理员权限 |

---

## ⚠️ 关键安全注意事项

### 🔴 绝对禁止事项

| 禁止项 | 风险 | 说明 |
|--------|------|------|
| ❌ 直接修改 `users.db` | 数据库损坏、无法登录 | 禁止用 sqlite3 直接操作 |
| ❌ 删除 admin 账号 | 系统无法管理 | admin 账户受保护 |
| ❌ 修改 guest 账号角色 | 系统功能异常 | guest 账户受保护 |
| ❌ 在测试环境操作生产数据 | 数据混乱 | 区分 8080/8081 端口 |

### 🟡 强烈建议

| 建议项 | 原因 |
|--------|------|
| ✅ 使用 UI 创建 | 自动验证、风险最小 |
| ✅ 设置强密码 | 防止账户被盗 |
| ✅ 记录创建的用户 | 便于审计和回收 |
| ✅ 创建前确认用户名未存在 | 避免冲突错误 |

### 用户权限保护

系统保护以下系统用户，**无法通过 API 修改**：

- `admin` - 管理员账户，不能删除、不能修改角色
- `guest` - 访客账户，不能删除、不能修改角色

尝试修改这些账户会返回 403 错误。

---

## 常见问题处理

### Q1: 创建用户时提示 "用户名已存在"

**原因**：用户名已被使用

**解决方案**：
1. 使用不同的用户名
2. 或先查询现有用户列表确认

```bash
# 查询现有用户
curl -b cookies.txt http://localhost:8080/api/users
```

### Q2: 忘记 admin 密码

**风险等级**：高

**解决方案**：
1. **不要**尝试修改数据库
2. 联系系统管理员
3. 或重置整个系统（极端情况）

### Q3: 新用户无法登录

**可能原因**：
1. 用户名或密码错误
2. 账号被禁用（is_active=0）
3. 角色配置错误

**排查步骤**：
1. 确认用户名和密码正确
2. 通过 UI 检查用户状态
3. 检查用户角色是否正确

### Q4: 误删用户怎么办

**风险等级**：高

**注意**：删除用户**不会**删除该用户创建的项目数据，项目数据仍然存在。

**恢复方式**：
1. 重新创建同名用户
2. 或通过数据库备份恢复（需要专业操作）

---

## 快速检查清单

创建用户前确认：

- [ ] 在正确的环境（生产 8080 / 测试 8081）
- [ ] 使用 admin 账号操作
- [ ] 新用户名不与已有用户冲突
- [ ] 密码符合安全要求
- [ ] 选择了正确的角色

---

## 附录：相关文件位置

| 文件 | 路径 |
|------|------|
| 用户数据库（生产） | `/projects/management/tracker/shared/data/user_data/users.db` |
| 用户数据库（测试） | `/projects/management/tracker/dev/data/users.db` |
| 项目数据库（生产） | `/projects/management/tracker/shared/data/user_data/*.db` |
| API 源码 | `/projects/management/tracker/dev/app/api.py` |
| 认证模块 | `/projects/management/tracker/dev/app/auth.py` |

---

*Last Updated: 2026-03-21*
*版本: v1.1*
