# Agent-Browser 使用技巧与最佳实践

> 本文档记录 agent-browser CLI 工具的使用技巧和常见场景
> 适用于 Tracker 项目的快速 UI 检查和调试

---

## 1. 基础使用

### 1.1 启动浏览器

```bash
# 基本启动（需要 --no-sandbox 参数）
agent-browser --args "--no-sandbox" open http://localhost:8081

# 带headed模式（显示浏览器窗口）
agent-browser --args "--no-sandbox" --headed open http://localhost:8081
```

### 1.2 常用命令速查

| 命令 | 说明 |
|------|------|
| `open <url>` | 打开URL |
| `snapshot` | 获取页面快照（可访问性树）|
| `screenshot [path]` | 截图 |
| `click <sel>` | 点击元素 |
| `fill <sel> <text>` | 填写表单 |
| `type <sel> <text>` | 输入文本（逐字符）|
| `get <what> <sel>` | 获取元素信息 |
| `wait <sel\|ms>` | 等待元素或时间 |
| `reload` | 刷新页面 |
| `close` | 关闭浏览器 |

---

## 2. 核心功能

### 2.1 页面导航

```bash
# 打开页面
agent-browser open http://localhost:8081

# 刷新页面
agent-browser reload

# 后退/前进
agent-browser back
agent-browser forward
```

### 2.2 元素交互

```bash
# 点击元素（使用 @ref 引用）
agent-browser click @e2

# 填写输入框
agent-browser fill @e2 "admin"
agent-browser fill @e3 "admin123"

# 输入（逐字符输入）
agent-browser type @e2 "admin"

# 悬停
agent-browser hover @e5

# 下拉选择
agent-browser select @e6 "value"

# 按键
agent-browser press Enter
agent-browser press Tab
```

### 2.3 页面检查

```bash
# 获取快照（可访问性树，包含元素引用）
agent-browser snapshot

# 交互式快照（仅显示可交互元素）
agent-browser snapshot -i

# 紧凑快照（移除空元素）
agent-browser snapshot -c

# 获取元素文本
agent-browser get text @e1

# 获取元素HTML
agent-browser get html @e1

# 获取元素属性
agent-browser get attr href @e1

# 检查元素状态
agent-browser is visible @e1
agent-browser is enabled @e1
```

### 2.4 截图

```bash
# 截图（默认保存为 page-{timestamp}.png）
agent-browser screenshot

# 指定路径
agent-browser screenshot /projects/management/tracker/preview.png

# 整页截图
agent-browser screenshot --full

# 截取特定元素
agent-browser screenshot --selector ".header"
```

### 2.5 等待

```bash
# 等待元素出现
agent-browser wait @e1

# 等待指定毫秒
agent-browser wait 2000

# 等待文本出现
agent-browser wait "登录成功"

# 等待文本消失
agent-browser wait-gone "加载中"
```

---

## 3. 元素定位

### 3.1 使用引用 (@ref)

`snapshot` 命令返回的元素引用格式为 `@e1`, `@e2` 等：

```bash
# snapshot 输出示例
- button "登录" [ref=e1]
- textbox [ref=e2]

# 使用引用
agent-browser click @e1
agent-browser fill @e2 "admin"
```

### 3.2 使用定位器

```bash
# 按角色查找
agent-browser find role button click --name 登录

# 按文本查找
agent-browser find text 提交 click

# 按占位符查找
agent-browser find placeholder "请输入用户名" fill --name admin
```

---

## 4. 调试技巧

### 4.1 快速检查页面状态

```bash
# 获取完整快照
agent-browser snapshot

# 获取交互元素快照
agent-browser snapshot -i

# 深度限制（只看前3层）
agent-browser snapshot -d 3
```

### 4.2 检查控制台

```bash
# 查看控制台消息
agent-browser console

# 查看错误
agent-browser errors

# 清除并查看
agent-browser console --clear
```

### 4.3 检查 CSS 样式（计算后样式）

调试 UI 样式问题时，可以使用 `eval` 获取元素的计算后样式：

```bash
# 获取元素背景色
agent-browser eval "getComputedStyle(document.querySelector('.tab.active')).backgroundColor"

# 获取边框颜色
agent-browser eval "getComputedStyle(document.querySelector('.tab.active')).borderBottomColor"

# 获取文字颜色
agent-browser eval "getComputedStyle(document.querySelector('.header')).color"

# 获取 CSS 变量值
agent-browser eval "getComputedStyle(document.documentElement).getPropertyValue('--color-primary')"
```

**常用计算样式属性**：

| 属性 | 说明 |
|------|------|
| `backgroundColor` | 背景色 |
| `color` | 文字颜色 |
| `borderBottomColor` | 下边框颜色 |
| `borderBottomWidth` | 下边框宽度 |
| `padding` | 内边距 |
| `margin` | 外边距 |
| `fontSize` | 字体大小 |
| `fontWeight` | 字体粗细 |

### 4.4 验证 CSS 是否生效流程

1. **截图确认** - 初步视觉检查
2. **计算样式验证** - 使用 `eval` 获取实际样式值
3. **CSS 文件检查** - 确认服务器返回正确 CSS

```bash
# 步骤1: 截图
agent-browser screenshot /path/to/screenshot.png

# 步骤2: 检查计算样式
agent-browser eval "getComputedStyle(document.querySelector('.your-class')).backgroundColor"

# 步骤3: 确认 CSS 文件可访问
curl http://localhost:8081/static/css/design-system.css | grep ".your-class"
```

### 4.3 高亮元素

```bash
# 高亮显示元素（调试用）
agent-browser highlight @e1
```

### 4.4 执行JavaScript

```bash
# 执行JavaScript
agent-browser eval "document.title"

# 获取计算样式
agent-browser eval "getComputedStyle(document.querySelector('.header')).background"
```

---

## 5. 高级功能

### 5.1 浏览器设置

```bash
# 设置视口大小
agent-browser set viewport 1280 800

# 暗黑模式
agent-browser set media dark

# 减少动画
agent-browser set media reduced-motion

# 离线模式
agent-browser set offline on
```

### 5.2 网络控制

```bash
# 阻止请求
agent-browser network route "*.js" --abort

# 模拟响应
agent-browser network route "/api/*" --body '{"status":"ok"}'

# 清除路由规则
agent-browser network unroute "/api/*"
```

### 5.3 存储管理

```bash
# 获取Cookie
agent-browser cookies get

# 设置Cookie
agent-browser cookies set --url http://localhost:8081 --name token --value abc123

# 清除Cookie
agent-browser cookies clear

# 获取LocalStorage
agent-browser storage local

# 获取SessionStorage
agent-browser storage session
```

### 5.4 标签页管理

```bash
# 新建标签页
agent-browser tab new

# 列出标签页
agent-browser tab list

# 切换到第2个标签页
agent-browser tab 2

# 关闭当前标签页
agent-browser tab close
```

---

## 6. 常见场景

### 6.1 登录测试

```bash
# 打开登录页
agent-browser open http://localhost:8081

# 填写用户名密码并登录
agent-browser fill @e2 "admin"
agent-browser fill @e3 "admin123"
agent-browser click @e4

# 等待登录完成
agent-browser wait 2
```

### 6.2 UI 效果检查

```bash
# 登录后截图
agent-browser screenshot /projects/management/tracker/ui_check.png

# 获取Header快照
agent-browser snapshot -s .header
```

### 6.3 表单提交测试

```bash
# 填写表单
agent-browser fill @inputName "测试项目"
agent-browser fill @inputDesc "测试描述"

# 选择下拉框
agent-browser select @prioritySelect "P1"

# 提交
agent-browser click @submitBtn

# 验证结果
agent-browser wait "创建成功"
```

---

## 7. 环境配置

### 7.1 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--args` | 浏览器参数 | `--args "--no-sandbox"` |
| `--headed` | 显示浏览器窗口 | `--headed` |
| `--session` | 会话名称 | `--session test1` |
| `--profile` | 浏览器配置路径 | `--profile ~/.myapp` |
| `--viewport` | 视口大小 | `--viewport-width 1280` |
| `--full` | 整页截图 | `--full` |

### 7.2 常见问题解决

**Chrome沙箱问题**:
```bash
# 使用 --no-sandbox 参数
agent-browser --args "--no-sandbox" open http://localhost:8081
```

**自动化检测绕过**:
```bash
# 禁用自动化控制标志
agent-browser --args "--no-sandbox,--disable-blink-features=AutomationControlled" open http://localhost:8081
```

---

## 8. 与 Playwright 对比

| 特性 | agent-browser | Playwright MCP |
|------|---------------|-----------------|
| 启动速度 | 快 | 较慢 |
| 命令行交互 | ✅ | ❌ |
| 脚本化 | ❌ | ✅ |
| 调试便利 | ✅ 实时交互 | ⚠️ 需配置 |
| 无头/headed | 需 `--headed` | 配置灵活 |
| 会话保持 | ✅ | ✅ |

**使用场景建议**:
- **快速检查/调试**: 使用 agent-browser（交互式）
- **自动化测试**: 使用 Playwright（脚本化）

---

## 9. 快速命令清单

```bash
# 1. 打开页面
agent-browser --args "--no-sandbox" open http://localhost:8081

# 2. 登录
agent-browser fill @e2 "admin"
agent-browser fill @e3 "admin123"
agent-browser click @e4
agent-browser wait 2

# 3. 截图
agent-browser screenshot /projects/management/tracker/preview.png

# 4. 获取快照
agent-browser snapshot

# 5. 关闭
agent-browser close
```

---

## 10. 相关文档

| 文档 | 说明 |
|------|------|
| [Playwright 调试最佳实践](./playwright_debug_best_practices.md) | Playwright 测试调试 |
| [Agent-Browser GitHub](https://github.com/e2b-dev/agent-browser) | 官方文档 |

---

*最后更新: 2026-03-05*
