# Tracker 编程标准

> **版本**: v1.0 | **创建日期**: 2026-03-07 | **状态**: 生效

---

## 目录

1. [概述](#1-概述)
2. [Python 后端标准](#2-python-后端标准)
3. [前端标准](#3-前端标准)
4. [API 设计标准](#4-api-设计标准)
5. [数据库操作标准](#5-数据库操作标准)
6. [测试代码标准](#6-测试代码标准)
7. [错误处理标准](#7-错误处理标准)
8. [代码组织规范](#8-代码组织规范)
9. [安全规范](#9-安全规范)

---

## 1. 概述

### 1.1 目的

本文档定义了 Tracker 项目后续版本开发应遵循的编程标准，确保代码质量一致、可维护性高、团队协作高效。

### 1.2 适用范围

- 所有 Tracker 项目的代码编写
- 包括后端 (Python/Flask)、前端 (HTML/JavaScript)、测试代码
- 适用于功能开发、Bug 修复、重构等所有代码变更

### 1.3 技术栈

| 层次 | 技术 |
|------|------|
| 后端 | Python 3.x + Flask + Flask-SQLAlchemy |
| 前端 | 原生 HTML/JS (无框架) |
| 数据库 | SQLite (每项目独立数据库) |
| API 测试 | pytest |
| UI 测试 | Playwright (Page Object 模式) |

---

## 2. Python 后端标准

### 2.1 代码风格

**遵循 PEP 8 规范**，主要要求：

| 规则 | 示例 |
|------|------|
| 缩进 | 4 空格 (不使用 Tab) |
| 行长度 | 最大 100 字符 |
| 命名 | `snake_case` (变量/函数)，`PascalCase` (类) |
| 导入 | 标准库 → 第三方库 → 本地模块，按顺序分组 |

```python
# 正确示例
import json
import time
from datetime import datetime

import pytest
from flask import Blueprint, jsonify, session

from app.models import Project
from app.utils import validate_date


def get_user_info(user_id):
    """获取用户信息"""
    pass


class ProjectService:
    """项目服务类"""
    pass
```

### 2.2 函数与类定义

**函数命名**：
- 使用 `snake_case`
- 名称应表达函数功能，如 `create_project`, `update_test_case`

**类定义**：
- 放在模块顶部或专用文件中
- 保持单一职责

```python
# 好的函数定义
def validate_project_name(name: str) -> bool:
    """验证项目名称是否合法

    Args:
        name: 项目名称

    Returns:
        验证结果
    """
    if not name or len(name) > 100:
        return False
    return True


# 避免
def check(n):  # 名称不明确
    return n and len(n) <= 100
```

### 2.3 注释与文档

**必须添加文档字符串的场景**：
- 所有公开的函数/类
- 复杂的业务逻辑
- 重要的数据模型

```python
def calculate_coverage(project_id: int, cp_list: list) -> dict:
    """计算项目覆盖率

    Args:
        project_id: 项目 ID
        cp_list: 覆盖点列表

    Returns:
        包含覆盖率统计的字典

    Raises:
        ValueError: 项目不存在时
    """
    pass
```

**行内注释**：
- 解释为什么，而不是做什么
- 保持简洁

```python
# 正确的注释
# 由于历史原因，项目ID从1开始
project_id = generate_project_id()

# 避免的注释
# 遍历列表
for item in items:
    process(item)
```

---

## 3. 前端标准

### 3.1 JavaScript 代码风格

**变量声明**：

```javascript
// 使用 const/let，不使用 var
const API_BASE = '/api';
let currentProject = null;
```

**函数定义**：

```javascript
// 优先使用 async/await 处理异步操作
async function loadCP(projectId) {
    try {
        const res = await fetch(`${API_BASE}/cp?project_id=${projectId}`);
        if (!res.ok) {
            throw new Error('加载失败');
        }
        return await res.json();
    } catch (e) {
        console.error('加载 CP 失败:', e);
        return [];
    }
}
```

**避免全局变量污染**：
- 使用 IIFE 或模块模式
- 核心状态使用单一全局对象管理

```javascript
// 推荐：集中管理状态
const AppState = {
    currentProject: null,
    coverPoints: [],
    testCases: [],
    currentUser: null
};
```

### 3.2 DOM 操作

**选择器使用**：

```javascript
// 推荐：使用 data-* 属性
const modal = document.querySelector('[data-modal="project"]');

// 避免：依赖 class 或结构
const modal = document.querySelector('.modal-content');
```

**事件处理**：

```javascript
// 推荐：事件委托
document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action="delete"]');
    if (btn) {
        handleDelete(btn.dataset.id);
    }
});

// 避免：内联事件
// <button onclick="deleteItem()">删除</button>
```

### 3.3 fetch 封装

**全局 fetch 包装**（已在项目中实现）：

```javascript
// 已实现：自动添加 credentials
const originalFetch = window.fetch;
window.fetch = async function(url, options = {}) {
    if (!options.credentials) {
        options.credentials = 'include';
    }
    return originalFetch(url, options);
};

// API 调用示例
async function deleteProject(id) {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
        method: 'DELETE'
    });

    if (!res.ok) {
        const data = await res.json();
        alert(data.message || '删除失败');
        return false;
    }
    return true;
}
```

---

## 4. API 设计标准

### 4.1 RESTful 规范

**HTTP 方法使用**：

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 获取资源 | `GET /api/projects` |
| POST | 创建资源 | `POST /api/projects` |
| PUT | 完整更新 | `PUT /api/projects/1` |
| PATCH | 部分更新 | `PATCH /api/projects/1/status` |
| DELETE | 删除资源 | `DELETE /api/projects/1` |

**URL 命名**：
- 资源使用复数形式
- 使用 kebab-case（如有多个单词）
- 查询参数使用 snake_case

```
# 正确
GET /api/test-cases?project_id=1&status=PASS
GET /api/cover-points?project_id=1

# 避免
GET /api/testCase?id=1
GET /api/CoverPointList
```

### 4.2 响应格式

**成功响应**：

```python
# 标准成功响应
return jsonify({
    "success": True,
    "data": {...}
})

# 列表响应
return jsonify({
    "success": True,
    "items": [...],
    "total": 100
})

# 创建成功
return jsonify({
    "success": True,
    "project": {...}
}), 201
```

**错误响应**：

```python
# 标准错误响应
return jsonify({
    "error": "错误类型",
    "message": "用户友好的错误消息"
}), 400
```

**HTTP 状态码使用**：

| 状态码 | 使用场景 |
|--------|----------|
| 200 | GET 成功、PUT/PATCH 更新成功 |
| 201 | POST 创建成功 |
| 400 | 请求参数错误、业务逻辑错误 |
| 401 | 未登录 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 4.3 路由组织

**使用 Blueprint 组织路由**：

```python
# app/api.py
from flask import Blueprint

api = Blueprint("api", __name__)

# 按功能模块用注释分隔
# ============ 项目管理 ============

@api.route('/projects', methods=['GET'])
def get_projects():
    """获取项目列表"""
    pass


@api.route('/projects', methods=['POST'])
def create_project():
    """创建项目"""
    pass
```

### 4.4 访问控制

**使用装饰器控制访问**：

```python
from functools import wraps
from flask import session, jsonify

SESSION_USER_KEY = 'user'


def login_required(f):
    """要求登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if SESSION_USER_KEY not in session:
            return jsonify({"error": "Unauthorized", "message": "请先登录"}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """要求管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if SESSION_USER_KEY not in session:
            return jsonify({"error": "Unauthorized", "message": "请先登录"}), 401
        if session.get('role') != 'admin':
            return jsonify({"error": "Forbidden", "message": "需要管理员权限"}), 403
        return f(*args, **kwargs)
    return decorated_function
```

---

## 5. 数据库操作标准

### 5.1 SQLAlchemy 模型定义

**模型基类使用**：

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Project(db.Model):
    """项目模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    start_date = db.Column(db.String(10))
    end_date = db.Column(db.String(10))
    created_at = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # 关系定义
    cover_points = db.relationship('CoverPoint', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'created_at': self.created_at
        }
```

### 5.2 序列化方法

**每个模型必须实现 `to_dict()` 方法**：

```python
class CoverPoint(db.Model):
    # ... 字段定义 ...

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'feature': self.feature,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at
        }
```

### 5.3 事务处理

**显式提交事务**：

```python
# 手动管理事务
conn = sqlite3.connect(db_path)
conn.execute("INSERT INTO projects ...")
conn.commit()
conn.close()

# 或使用 Flask-SQLAlchemy
db.session.add(project)
db.session.commit()
```

### 5.4 原生 SQL 使用

**当需要使用原生 SQL 时**：

```python
# 参数化查询，防止 SQL 注入
def get_project_stats(project_id):
    conn = get_db_connection(project_id)
    cursor = conn.execute(
        "SELECT status, COUNT(*) as count FROM test_case GROUP BY status",
        ()
    )
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]
```

---

## 6. 测试代码标准

### 6.1 API 测试 (pytest)

**测试文件组织**：

```
tests/test_api/
├── conftest.py          # 共享 fixture
├── test_api.py          # 核心 API 测试
├── test_api_auth.py     # 认证 API 测试
├── test_api_import.py   # 导入功能测试
└── ...
```

**Fixture 定义**：

```python
# conftest.py
import pytest
import json
from app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_client(client):
    """创建已登录的管理员客户端"""
    client.post('/api/auth/login',
        data=json.dumps({'username': 'admin', 'password': 'admin123'}),
        content_type='application/json')
    return client
```

**测试用例编写**：

```python
# test_api.py
import json
import pytest


class TestProjectsAPI:
    """项目 API 测试"""

    def test_get_projects(self, admin_client):
        """GET /api/projects - 获取项目列表"""
        response = admin_client.get('/api/projects')
        assert response.status_code == 200

    def test_create_project(self, admin_client):
        """POST /api/projects - 创建项目"""
        name = f"Test_{int(time.time())}"
        response = admin_client.post('/api/projects',
                              data=json.dumps({
                                  'name': name,
                                  'start_date': '2026-01-01',
                                  'end_date': '2026-12-31'
                              }),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
```

**测试数据管理**：

- 使用时间戳生成唯一名称
- 测试结束后清理数据

```python
@pytest.fixture(scope='module')
def test_project():
    """创建测试项目，测试结束后清理"""
    # 创建
    name = f"API_Test_{int(time.time())}"
    response = admin_client.post('/api/projects',
                          data=json.dumps({
                              'name': name,
                              'start_date': '2026-01-01',
                              'end_date': '2026-12-31'
                          }),
                          content_type='application/json')

    project_id = json.loads(response.data)['project']['id']

    yield {'id': project_id, 'name': name}

    # 清理
    admin_client.delete(f"/api/projects/{project_id}")
```

### 6.2 UI 测试 (Playwright)

**Page Object 模式**：

```typescript
// pages/base.page.ts
import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
  protected page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  abstract navigate(): Promise<void>;

  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
  }

  async safeClick(selector: string): Promise<void> {
    await this.page.click(selector, { timeout: 10000 });
  }
}
```

**页面类示例**：

```typescript
// pages/project.page.ts
import { BasePage } from './base.page';

export class ProjectPage extends BasePage {
  readonly projectList: Locator;

  constructor(page: Page) {
    super(page);
    this.projectList = page.locator('[data-testid="project-list"]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('/');
  }

  async createProject(name: string): Promise<void> {
    await this.page.click('[data-action="create-project"]');
    await this.page.fill('[name="projectName"]', name);
    await this.page.click('[data-action="submit"]');
  }
}
```

**测试用例**：

```typescript
// specs/smoke/smoke.spec.ts
import { test, expect } from '@playwright/test';
import { ProjectPage } from '../pages/project.page';

test.describe('项目管理', () => {
  test('创建项目', async ({ page }) => {
    const projectPage = new ProjectPage(page);
    await projectPage.navigate();

    const projectName = `Test_${Date.now()}`;
    await projectPage.createProject(projectName);

    await expect(projectPage.projectList).toContainText(projectName);
  });
});
```

### 6.3 测试执行标准

**所有测试必须通过才能提交**：

```bash
# 前端代码检查
cd /projects/management/tracker/dev
bash check_frontent.sh

# API 测试
PYTHONPATH=. pytest tests/test_api/ -v

# UI 冒烟测试
npx playwright test tests/test_ui/specs/smoke/ --project=firefox
```

---

## 7. 错误处理标准

### 7.1 后端错误处理

**业务逻辑错误**：

```python
@api.route('/projects', methods=['POST'])
def create_project():
    """创建项目"""
    data = request.get_json()

    # 验证必填字段
    if not data.get('name'):
        return jsonify({
            "error": "ValidationError",
            "message": "项目名称不能为空"
        }), 400

    # 验证数据格式
    if data.get('start_date') and data.get('end_date'):
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                return jsonify({
                    "error": "ValidationError",
                    "message": "开始日期不能晚于结束日期"
                }), 400
        except ValueError:
            return jsonify({
                "error": "ValidationError",
                "message": "日期格式应为 YYYY-MM-DD"
            }), 400
```

**异常处理**：

```python
@api.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目详情"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                "error": "NotFound",
                "message": "项目不存在"
            }), 404

        return jsonify({
            "success": True,
            "project": project.to_dict()
        })
    except Exception as e:
        app.logger.error(f"获取项目失败: {e}")
        return jsonify({
            "error": "InternalError",
            "message": "服务器内部错误"
        }), 500
```

### 7.2 前端错误处理

**API 错误处理**：

```javascript
async function saveProject(data) {
    try {
        const res = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        if (!res.ok) {
            const error = await res.json();
            alert(error.message || '保存失败');
            return null;
        }

        return await res.json();
    } catch (e) {
        console.error('保存项目失败:', e);
        alert('网络错误，请稍后重试');
        return null;
    }
}
```

### 7.3 数据验证规范

**必填字段验证**：

```python
def validate_required(data: dict, fields: list) -> tuple:
    """验证必填字段

    Args:
        data: 请求数据
        fields: 必填字段列表

    Returns:
        (is_valid, error_message)
    """
    for field in fields:
        if field not in data or not data[field]:
            return False, f"{field} 不能为空"
    return True, None
```

---

## 8. 代码组织规范

### 8.1 目录结构

```
dev/
├── app/
│   ├── __init__.py      # Flask 应用工厂
│   ├── api.py           # API 路由定义
│   ├── models.py        # 数据库模型
│   └── utils.py         # 工具函数
├── tests/
│   ├── test_api/        # API 测试
│   └── test_ui/         # UI 测试
├── index.html           # 前端入口
├── server.py            # Flask 服务器
└── check_frontent.sh    # 前端检查脚本
```

### 8.2 模块导入顺序

```python
# 1. 标准库
import json
import os
import sys
from datetime import datetime
from functools import wraps

# 2. 第三方库
import pytest
from flask import Blueprint, jsonify, request, session

# 3. 本地模块
from app.models import Project, CoverPoint, TestCase
from app.utils import validate_date, format_response
```

### 8.3 代码分隔

**使用注释分隔功能模块**：

```python
# ============ 项目管理 ============

@api.route('/projects', methods=['GET'])
def get_projects():
    pass


# ============ 覆盖点管理 ============

@api.route('/cp', methods=['GET'])
def get_cover_points():
    pass
```

---

## 9. 安全规范

### 9.1 数据安全

| 规则 | 说明 |
|------|------|
| 不修改 user_data | 禁止操作 `shared/data/user_data/` 目录 |
| 使用 test_data | 开发测试使用 `shared/data/test_data/` |
| 密码加密 | 用户密码必须使用哈希存储 |

### 9.2 访问控制

- 所有修改类 API 必须使用 `@login_required` 装饰器
- 管理类 API 必须使用 `@admin_required` 装饰器
- 敏感操作记录日志

### 9.3 SQL 注入防护

**必须使用参数化查询**：

```python
# 正确
cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))

# 避免
cursor.execute(f"SELECT * FROM projects WHERE id = {project_id}")
```

### 9.4 Session 安全

```python
# Flask Session 配置
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# 生产环境必须使用强密钥
# os.environ['FLASK_SECRET_KEY'] = '随机字符串'
```

---

## 10. Git 分支管理规范

### 10.1 分支结构

```
main (生产稳定版)
│
├── develop (开发主分支)
│   ├── feature/* (功能开发分支)
│   ├── bugfix/* (Bug修复分支)
│   └── release/* (发布准备分支)
│
└── tags (发布标签)
```

### 10.2 分支说明

| 分支 | 来源 | 合并到 | 用途 |
|------|------|--------|------|
| **main** | - | - | 生产环境代码，任何时候都应保持稳定 |
| **develop** | main | - | 开发主分支，聚合所有功能分支 |
| **feature/*** | develop | develop | 新功能开发 |
| **bugfix/*** | develop | develop | Bug 修复 |
| **release/*** | develop | main + develop | 发布准备 |

### 10.3 绝对规则

| 规则 | 说明 |
|------|------|
| 🔴 **禁止 main 直接开发** | 绝对不允许在 main 分支上直接修改/提交代码 |
| 🔴 **禁止 develop 直接开发** | 不允许在 develop 分支上直接开发功能 |
| ✅ **必须创建功能分支** | 所有开发必须从 develop 创建 feature/* 或 bugfix/* 分支 |

### 10.4 开发流程

```bash
# 1. 确保本地 develop 是最新
git checkout develop
git pull origin develop

# 2. 创建功能分支（从 develop）
git checkout -b feature/功能名称
# 或创建 Bug 修复分支
git checkout -b bugfix/问题描述

# 3. 开发完成后，切换到 develop
git checkout develop

# 4. 合并功能分支（使用 --no-ff 保留分支历史）
git merge feature/功能名称 --no-ff -m "feat: 功能说明"

# 5. 推送到远程
git push origin develop

# 6. 删除已合并的本地分支（可选）
git branch -d feature/功能名称
```

### 10.5 分支命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 功能分支 | feature/功能名称 | feature/user-auth |
| Bug 修复 | bugfix/问题描述 | bugfix/login-error |
| 发布分支 | release/v版本号 | release/v0.10.0 |

### 10.6 提交信息格式

```
<type>: <subject>

<body>

<footer>
```

**Type 类型**：

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | `feat: 添加用户认证功能` |
| fix | Bug 修复 | `fix: 修复项目切换数据丢失问题` |
| docs | 文档更新 | `docs: 更新规格书` |
| style | 代码格式 | `style: 格式化代码` |
| refactor | 重构 | `refactor: 重构 API 结构` |
| test | 测试 | `test: 添加单元测试` |
| chore | 构建/工具 | `chore: 更新依赖版本` |

**提交示例**：
```bash
git commit -m "feat: 添加 TC-CP 关联导入功能

- 新增关联关系表
- 添加导入页面和 API
- 添加 CSV 文件解析

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 附录 A: 快速参考

### 代码提交信息格式

```
<type>: <subject>

<body>

<footer>
```

**Type 类型**：

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式 |
| refactor | 重构 |
| test | 测试 |
| chore | 构建/工具 |

### ESLint 检查

```bash
cd /projects/management/tracker/dev
bash check_frontent.sh
```

### 测试命令

```bash
# API 测试
cd /projects/management/tracker/dev
PYTHONPATH=. pytest tests/test_api/ -v

# UI 冒烟测试
cd /projects/management/tracker/dev
npx playwright test tests/test_ui/specs/smoke/ --project=firefox
```

---

**文档版本**: v1.0
**最后更新**: 2026-03-07
**维护者**: 小栗子
