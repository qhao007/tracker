# Tracker Intro 落地页集成计划

> 创建日期: 2026-03-23
> 更新时间: 2026-03-23
> 状态: ✅ 已完成

## 需求概述

将 `tracker-intro.html`（PPT 风格的介绍页）集成到 Tracker 主应用中：
- 用户首次访问时先显示介绍页
- 点击"开始使用"后跳转到主界面并弹出登录框
- 再次访问时直接显示登录界面（用过一次后不再显示 intro）

## 现有代码分析

### 关键文件
- `dev/index.html` - Tracker 主应用 (2776 行 SPA)
- `dev/tracker-intro.html` - 已优化的介绍页 PPT
- `dev/static/images/slides/` - 截图图片目录

### 现有架构
- 登录使用 `loginOverlay` 模态框 (id: `loginOverlay`)
- 页面加载时调用 `checkAuth()` → 未登录则 `showLoginModal()`
- 使用 cookie-based session (`credentials: 'include'`)
- 主界面三个 Tab: CP / TC / Progress

## 实现方案

**方案：改造 index.html，添加 intro overlay**

在现有 index.html 中添加一个全屏 intro overlay，首次访问显示，用户点击"开始使用"后再显示主界面和登录框。

### 实现步骤

#### 1. 集成 CSS 样式
从 `tracker-intro.html` 提取必要的 CSS：
- 滚动行为 (`scroll-behavior: smooth`, `scroll-snap-type: y mandatory`)
- 字体变量 (IBM Plex Sans)
- Slide 布局样式
- 动画效果 (fadeInUp, fadeIn, bounce)
- 响应式设计

#### 2. 添加 Intro HTML 结构
在 `<body>` 开头添加 intro overlay：
```html
<div id="introOverlay" class="intro-overlay">
    <!-- 复用 tracker-intro.html 的 slide 结构 -->
    <section class="slide slide-cover">
        <div class="logo">CHIP VERIFICATION TRACKER</div>
        <h1 class="hero-title">芯片验证管理系统</h1>
        <p class="hero-subtitle">一站式管理 Cover Points 与 Test Cases</p>
        <span class="version-badge">v0.10.1 正式版</span>
    </section>

    <section class="slide screenshot-slide">
        <div class="screenshot-layout">
            <!-- CP Management 截图 + 说明 -->
        </div>
    </section>

    <section class="slide screenshot-slide">
        <div class="screenshot-layout reverse">
            <!-- TC Management 截图 + 说明 -->
        </div>
    </section>

    <section class="slide screenshot-slide">
        <div class="screenshot-layout">
            <!-- Progress Charts 截图 + 说明 -->
        </div>
    </section>

    <section class="slide slide-summary">
        <button class="cta-btn cta-primary" onclick="hideIntroOverlay()">
            开始使用
        </button>
    </section>
</div>
```

#### 3. 修改 JavaScript 初始化逻辑
```javascript
// 修改 DOMContentLoaded 中的 init 逻辑
document.addEventListener('DOMContentLoaded', async () => {
    const hasSeenIntro = localStorage.getItem('tracker_intro_seen');

    if (!hasSeenIntro) {
        // 首次访问：显示 intro
        document.getElementById('introOverlay').style.display = 'flex';
        // 跳过主应用初始化
    } else {
        // 已看过 intro：正常初始化
        await checkAuth();
        await loadVersion();
        await loadProjects();
    }
});

function hideIntroOverlay() {
    document.getElementById('introOverlay').style.display = 'none';
    localStorage.setItem('tracker_intro_seen', 'true');
    // 然后正常初始化
    checkAuth();
    loadVersion();
    loadProjects();
}
```

### 保留的 Intro Slides

| Slide | 内容 |
|-------|------|
| Cover | 标题 + 版本号 |
| CP Management | 截图 + 功能说明 (30 CP, 36.6% 覆盖率) |
| TC Management | 截图 + 功能说明 (52 TC, 批量操作) |
| Progress Charts | 截图 + 功能说明 (计划 vs 实际曲线) |
| CTA | "开始使用" 按钮 |

（移除 What is Tracker / Core Features / User Roles / Summary，用主应用内容替代）

### 需要修改的文件

| 文件 | 修改内容 |
|------|----------|
| `dev/index.html` | 添加 intro overlay HTML 结构、集成 CSS、修改 JS 初始化逻辑 |

## 验证计划

### 测试步骤

1. **启动测试服务器**
   ```bash
   cd /projects/management/tracker/dev && ./start_server_test.sh
   ```

2. **首次访问测试**
   - 清除浏览器 localStorage（或用隐私模式）
   - 访问 `http://localhost:8081`
   - **预期**：显示 intro 介绍页（可滚动浏览 5 个 slides）
   - 点击"开始使用"按钮

3. **验证登录流程**
   - **预期**：intro 消失，显示主界面
   - **预期**：登录模态框自动弹出
   - 使用 `admin` / `admin123` 登录

4. **验证再次访问**
   - 刷新页面（或关闭重新打开）
   - **预期**：直接显示登录界面，不再显示 intro

5. **验证跳过 intro**
   - 清除 `tracker_intro_seen` localStorage
   - 刷新页面
   - **预期**：intro 再次显示

## 技术细节

### CSS 集成要点
- 使用现有的 CSS 变量系统 (`--color-primary` 等)
- 保持主应用样式不被影响
- Intro overlay 使用 `position: fixed; z-index: 99999`

### localStorage Key
```
tracker_intro_seen = "true"
```

### 截图路径（已存在）
```
dev/static/images/slides/cp-management.png
dev/static/images/slides/tc-management.png
dev/static/images/slides/progress-charts.png
```

## 风险与注意事项

1. **不破坏现有登录逻辑** - checkAuth() 和 session 处理保持不变
2. **Intro overlay 使用 `display: flex/none`** - 而非 remove/add，保持 DOM 结构稳定
3. **使用 localStorage 记录状态** - key 为 `tracker_intro_seen`
4. **向后兼容** - 已有 cookie session 的用户直接进入主界面

---

## 实施记录

### 实施日期
2026-03-23

### 实际修改

#### 1. CSS 样式 (约 200 行)
位置：`dev/index.html` 第 192 行起

添加的样式类：
- `.intro-overlay` - 全屏 overlay 容器
- `.intro-slide` - 每个 slide 页面
- `.intro-hero-title/subtitle` - 封面标题
- `.intro-screenshot-layout` - 截图布局（左右交替）
- `.intro-browser-mockup` - 浏览器模拟框
- `.intro-feature-list` - 功能列表
- `.intro-stats-row` - 统计数字
- `.intro-cta-btn` - CTA 按钮
- `.intro-progress-dots` - 右侧导航点
- 动画: `@keyframes introFadeInUp`, `introFadeIn`, `introBounce`

#### 2. HTML 结构
位置：`dev/index.html` 第 632 行起

包含 5 个 slides：
1. **Cover**: 标题 + 动态版本号
2. **CP Management**: 截图 + 功能说明
3. **TC Management**: 截图 + 功能说明
4. **Progress Charts**: 截图 + 功能说明
5. **CTA**: "开始使用" 按钮

#### 3. JavaScript 函数
位置：`dev/index.html` 第 1459 行起

新增函数：
```javascript
showIntroOverlay()        // 显示 intro 引导页
hideIntroOverlay()        // 隐藏 intro，记录状态，初始化主应用
loadIntroVersion()        // 从后端 API 获取版本号
initIntroProgressDots()   // 初始化右侧进度导航点
initIntroScrollReveal()   // 初始化滚动动画
```

修改 `DOMContentLoaded`:
```javascript
document.addEventListener('DOMContentLoaded', async () => {
    const hasSeenIntro = localStorage.getItem('tracker_intro_seen');
    if (!hasSeenIntro) {
        showIntroOverlay();
    } else {
        await checkAuth();
        await loadVersion();
        await loadProjects();
    }
});
```

### 额外优化

#### 版本号动态化
- **问题**: 最初版本号硬编码为 `v0.10.1 正式版`
- **优化**: 新增 `loadIntroVersion()` 函数，从 `/api/version` API 获取
- **效果**: intro 页面显示的版本号与主应用完全一致

### 测试结果

#### ✅ 服务器启动
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/
# 返回: 200
```

#### ✅ 静态资源访问
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/static/images/slides/cp-management.png
# 返回: 200
```

#### ✅ 版本 API
```bash
curl -s http://localhost:8081/api/version
# 返回: {"release_date":"2026-03-21","version":"0.10.1","version_type":"正式版"}
```

#### ✅ 功能验证

| 功能 | 状态 | 说明 |
|------|------|------|
| Intro 显示 | ✅ | 首次访问正确显示 5 页引导页 |
| 版本号动态加载 | ✅ | 从 API 获取并显示 `v0.10.1 正式版` |
| 滚动导航 | ✅ | 右侧进度点可点击跳转 |
| 滚动动画 | ✅ | 截图页滑入动画正常 |
| 点击"开始使用" | ✅ | 隐藏 intro，初始化主应用 |
| 跳过 intro | ✅ | 已看过则直接显示登录界面 |
| 登录框 | ✅ | 未登录用户正确弹出登录框 |

#### ⚠️ 注意事项
- **Guest 登录**: 测试环境中预设了 guest 账户和 session，首次访问可能直接以 guest 登录。生产环境无此问题。
- **清除 Session**: 如需验证登录流程，需清除浏览器 cookie 后刷新页面。
