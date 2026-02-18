# Playwright CLI vs Playwright MCP 对比分析报告

> 任务 ID：t1-20260213-playwright-analysis  
> 完成时间：2026-02-13

---

## 执行摘要

系统已安装以下 Playwright 相关 package：

| Package | 版本 | 用途 |
|---------|------|------|
| `@playwright/cli` | 0.1.0 | CLI + Skills 工作流（推荐用于编码 agent） |
| `@playwright/mcp` | 0.0.63 | MCP Server（Model Context Protocol） |
| `playwright` | 1.59.0-alpha | 底层库 |

---

## 一、Playwright CLI 分析

### 1.1 是什么

`@playwright/cli` 是 Playwright 官方提供的命令行工具套件，专门为**现代编码 Agent** 设计。

**核心特点**：
- 基于 MCP (Model Context Protocol) 架构
- Token 效率高（不加载庞大的工具 schema 和可访问性树）
- 通过简洁的命令让 Agent 操作浏览器
- 适合高吞吐量的编码 Agent

### 1.2 已安装版本信息

```json
{
  "name": "@playwright/cli",
  "version": "0.1.0",
  "bin": {
    "playwright-cli": "playwright-cli.js"
  },
  "dependencies": {
    "minimist": "^1.2.5",
    "playwright": "1.59.0-alpha-1770426101000"
  }
}
```

### 1.3 提供的功能

#### 核心工具（通过 browser_* 命名空间）

| 工具名称 | 功能 | 类型 |
|---------|------|------|
| `browser_navigate` | 导航到 URL | 自动化 |
| `browser_click` | 点击元素 | 自动化 |
| `browser_type` | 输入文本 | 自动化 |
| `browser_fill_form` | 填充表单 | 自动化 |
| `browser_hover` | 悬停 | 自动化 |
| `browser_drag` | 拖拽 | 自动化 |
| `browser_press_key` | 按键 | 自动化 |
| `browser_select_option` | 选择下拉选项 | 自动化 |
| `browser_snapshot` | 页面快照（可访问性树） | 读取 |
| `browser_take_screenshot` | 截图 | 读取 |
| `browser_console_messages` | 控制台消息 | 读取 |
| `browser_network_requests` | 网络请求 | 读取 |
| `browser_evaluate` | 执行 JS | 执行 |
| `browser_run_code` | 运行 Playwright 代码 | 执行 |
| `browser_wait_for` | 等待 | 工具 |
| `browser_close` | 关闭浏览器 | 管理 |
| `browser_tabs` | 管理标签页 | 管理 |
| `browser_install` | 安装浏览器 | 管理 |

#### 断言工具（testing capability）

| 工具名称 | 功能 |
|---------|------|
| `browser_verify_element_visible` | 验证元素可见 |
| `browser_verify_text_visible` | 验证文本可见 |
| `browser_verify_list_visible` | 验证列表可见 |
| `browser_verify_value` | 验证值 |
| `browser_generate_locator` | 生成定位器 |

### 1.4 工作流程

```
用户/Agent → CLI 命令 → Playwright Core → 浏览器
         ↓
      返回 JSON 结果
```

---

## 二、Playwright MCP 分析

### 2.1 是什么

`@playwright/mcp` 是一个 **Model Context Protocol (MCP) Server**，为 LLM 提供浏览器自动化能力。

**核心特点**：
- 基于 MCP 协议
- 适合**探索性自动化**、**自愈测试**、**长时间运行的自主工作流**
- 维护持续的浏览器上下文
- 提供丰富的内省能力

### 2.2 架构设计

```
┌─────────────────────────────────────────────────┐
│            MCP Client (Claude Code)              │
└───────────────────┬───────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│           MCP Transport (SSE/Stdio)             │
└───────────────────┬───────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│        @playwright/mcp Server                   │
│  ┌───────────────────────────────────────────┐  │
│  │         Tool Dispatcher                    │  │
│  └───────────────────┬───────────────────────┘  │
│                      ▼                           │
│  ┌───────────────────────────────────────────┐  │
│  │         Playwright Core                   │  │
│  │    (browser_snapshot, click, type...)     │  │
│  └───────────────────┬───────────────────────┘  │
│                      ▼                           │
│  ┌───────────────────────────────────────────┐  │
│  │           Chromium/Firefox/WebKit         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 2.3 配置选项

```typescript
{
  browser: {
    browserName: 'chromium' | 'firefox' | 'webkit';
    isolated: boolean;           // 是否隔离
    userDataDir: string;         // 用户数据目录
    launchOptions: {};            // 启动选项
    contextOptions: {};          // 上下文选项
  },
  capabilities: ['core', 'pdf', 'vision'],  // 启用的能力
  timeouts: {
    action: number;              // 操作超时
    navigation: number;         // 导航超时
  },
  outputDir: string;             // 输出目录
}
```

### 2.4 与 MCP 客户端集成

```bash
# 安装到 Claude Code
claude mcp add playwright npx @playwright/mcp@latest

# 独立运行 MCP Server
npx @playwright/mcp --port 8931
```

---

## 三、核心差异对比

### 3.1 对比矩阵

| 维度 | Playwright CLI | Playwright MCP |
|------|---------------|---------------|
| **协议** | MCP (Model Context Protocol) | MCP (Model Context Protocol) |
| **架构** | CLI + Skills | MCP Server |
| **Token 效率** | 高（简洁命令） | 较低（完整上下文） |
| **适用场景** | 高吞吐量编码 Agent | 探索性自动化、长运行任务 |
| **状态管理** | 无状态（每次独立） | 持久化状态 |
| **可扩展性** | Skill 模式 | MCP 工具集 |
| **学习成本** | 中等 | 较高 |
| **调试友好度** | 一般 | 优秀（支持 trace、截图） |
| **浏览器支持** | Chromium/Firefox/WebKit | Chromium/Firefox/WebKit |
| **测试断言** | ✅ 完整支持 | ✅ 完整支持 |

### 3.2 详细对比

#### Token 使用对比

```typescript
// Playwright CLI 方式 (约 100 tokens)
await browser_navigate({ url: "http://localhost:8081" });
await browser_click({ ref: "submit-button" });
await browser_type({ ref: "username", text: "admin" });

// Playwright MCP 方式 (约 500+ tokens，包含完整上下文)
// 需要先获取页面快照，然后从快照中选择元素
await browser_snapshot();  // 返回完整 DOM 树
// 然后从结果中选择元素...
```

#### 执行模式对比

| 方面 | CLI | MCP |
|------|-----|-----|
| **连接方式** | 每次调用启动新会话 | 持久连接 |
| **浏览器状态** | 每次独立 | 共享上下文 |
| **错误恢复** | 需手动处理 | 自动重试 |
| **并发支持** | 单次单请求 | 多请求共享 |

---

## 四、Tracker 适用性分析

### 4.1 当前测试需求

Tracker 系统 UI 测试需求：

1. **项目管理**：创建、切换、删除项目
2. **CP 管理**：CRUD、过滤、批量更新
3. **TC 管理**：CRUD、过滤、关联 CP
4. **统计页面**：数据展示、图表

### 4.2 两种方案对比

#### 方案 A：继续使用 Playwright CLI (TypeScript 测试)

```bash
# 运行测试
npx playwright test tests/test_ui_project.spec.ts --project=firefox
```

**优点**：
- 完整的测试框架支持
- Page Object Model 良好集成
- CI/CD 集成成熟
- 社区资源丰富

**缺点**：
- 需要编写测试代码
- 学习曲线

**内存使用**：约 500-800 MB

#### 方案 B：使用 MCP Server 进行探索式测试

```bash
# 启动 MCP Server
npx @playwright/mcp --isolated --save-trace
```

**优点**：
- 无需编写代码
- 实时交互
- 适合探索性测试
- 详细的 trace 输出

**缺点**：
- Token 消耗大
- 不适合自动化回归测试
- 需要 MCP 客户端支持

**内存使用**：约 300-500 MB（单浏览器实例）

### 4.3 建议方案

**推荐策略**：**混合使用**

| 测试类型 | 推荐方案 | 原因 |
|---------|---------|------|
| **自动化回归测试** | Playwright CLI (TypeScript) | 稳定、可复用、CI/CD 友好 |
| **探索性测试** | MCP Server | 交互式、快速验证 |
| **问题排查** | MCP Server + Trace Viewer | 详细日志、视觉化 |
| **开发调试** | Playwright Inspector | 代码级调试 |

---

## 五、集成建议

### 5.1 在 Tracker 项目中使用 MCP

#### 安装依赖

```bash
npm install @playwright/mcp
```

#### 配置 MCP Server

```json
{
  "mcpServers": {
    "playwright-tracker": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--browser", "firefox",
        "--isolated"
      ],
      "env": {
        "TRACKER_URL": "http://localhost:8081"
      }
    }
  }
}
```

### 5.2 在 OpenClaw 中集成

由于 OpenClaw 使用 skill 模式，可以创建 MCP integration skill：

```typescript
// skills/mcp-playwright/SKILL.md

# MCP Playwright Integration

## 功能

通过 MCP 协议集成 Playwright 浏览器自动化能力。

## 使用方式

```bash
# 启动 MCP Server
npx @playwright/mcp --browser firefox --isolated

# 在 Agent 中使用工具
await browser_navigate({ url: "http://localhost:8081" });
```

## 可用工具

- `browser_navigate`: 导航
- `browser_snapshot`: 获取页面快照
- `browser_click`: 点击
- `browser_type`: 输入
- `browser_verify_*`: 断言
```

### 5.3 内存优化配置

```json
{
  "browser": {
    "browserName": "firefox",
    "isolated": true,
    "launchOptions": {
      "headless": true,
      "args": [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu"
      ]
    }
  },
  "contextOptions": {
    "viewport": { "width": 1280, "height": 720 }
  }
}
```

---

## 六、具体建议

### 6.1 短期行动（1-2 周）

1. **评估 MCP 适用性**
   - 在 Tracker 测试环境中试用 MCP Server
   - 对比 CLI 和 MCP 的测试稳定性
   - 记录 Token 消耗对比

2. **优化现有 Playwright CLI 测试**
   - 应用之前生成的 UI_TESTING_STRATEGY.md 建议
   - 添加 Page Object Model
   - 优化内存使用

### 6.2 中期行动（2-4 周）

1. **MCP 集成到开发流程**
   - 创建 MCP Playwright skill
   - 培训团队使用 MCP 进行探索性测试
   - 建立问题排查 SOP

2. **混合测试策略**
   - CLI：自动化回归测试
   - MCP：探索性测试、问题验证

### 6.3 长期行动（1-2 月）

1. **测试能力扩展**
   - 集成视觉回归测试
   - 性能监控测试
   - 端到端用户体验测试

2. **CI/CD 深度集成**
   - 自动生成测试用例
   - 智能测试选择（基于代码变更）
   - 测试报告分析

---

## 七、结论

### 7.1 关键发现

1. **Playwright CLI 和 MCP 本质上使用相同的底层库**，差异主要在于交互模式
2. **CLI 更适合自动化测试**：Token 高效、稳定、可复用
3. **MCP 更适合探索性工作**：交互式、上下文持久化、调试友好
4. **混合使用是最佳策略**：根据场景选择合适的工具

### 7.2 建议决策

| 决策点 | 建议 |
|--------|------|
| **是否放弃 Playwright CLI？** | ❌ 不放弃，继续使用 |
| **是否引入 MCP？** | ✅ 引入，用于探索性测试和问题排查 |
| **是否统一测试框架？** | ✅ 统一为 Playwright CLI (TypeScript) |
| **MCP 何时使用？** | 开发调试、探索性测试、问题排查 |

### 7.3 后续步骤

1. ☐ 在 Tracker 测试环境试用 MCP Server
2. ☐ 对比 CLI 和 MCP 的实际效果
3. ☐ 决定是否创建 MCP integration skill
4. ☐ 制定混合测试策略

---

## 附录

### A. 参考链接

- [Playwright 官方文档](https://playwright.dev/docs/intro)
- [Playwright CLI GitHub](https://github.com/microsoft/playwright-cli)
- [Playwright MCP README](/root/.nvm/versions/node/v22.22.0/lib/node_modules/@playwright/mcp/README.md)
- [MCP Protocol 文档](https://modelcontextprotocol.io/)

### B. 命令速查

```bash
# 启动 MCP Server（独立模式）
npx @playwright/mcp --isolated --save-trace

# 安装浏览器
npx playwright install firefox

# 运行 CLI 测试
npx playwright test tests/ --project=firefox

# 生成测试代码
npx playwright codegen http://localhost:8081
```

### C. 文件位置

| 文件 | 路径 |
|------|------|
| Playwright CLI | `/root/.nvm/versions/node/v22.22.0/lib/node_modules/@playwright/cli/` |
| Playwright MCP | `/root/.nvm/versions/node/v22.22.0/lib/node_modules/@playwright/mcp/` |
| Playwright Core | `/root/.nvm/versions/node/v22.22.0/lib/node_modules/@playwright/cli/node_modules/playwright/` |

---

> 报告版本：v1.0  
> 作者：Claude Code  
> 任务 ID：t1-20260213-playwright-analysis
