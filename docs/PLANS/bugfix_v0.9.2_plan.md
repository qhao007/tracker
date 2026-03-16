# BUG修复计划 - v0.9.2

## 待修复的BUG

### 任务1: BUG-089 - CP未关联过滤不生效

**问题描述**: 在CP页面Filter下拉中选择"未关联"选项后，列表仍然显示所有CP（包括已关联的CP），过滤功能未生效。

**根因分析**:
- 前端 `renderCP()` 函数在第1502-1505行使用JavaScript进行本地过滤
- 逻辑看起来正确: `if (linkedFilter === 'unlinked') { filtered = filtered.filter(cp => !linkedCPIds.has(cp.id)); }`
- 可能原因: 需要验证测试或实际使用时的行为

**修复方案**:
1. 验证前端过滤逻辑是否正确工作
2. 如果有问题，修复过滤逻辑

---

### 任务2: BUG-090 - 修改密码API网络错误

**问题描述**: admin用户首次登录后，强制改密码弹窗中的"确认修改"按钮点击后返回"网络错误"，无法修改密码。

**根因分析**:
- 前端调用: `${API_BASE}/auth/password` = `/api/auth/password` (第993行)
- 后端没有 `/api/auth/password` 端点
- 后端只有 `/api/users/<int:user_id>/reset-password` (admin重置其他用户密码)

**修复方案**:
1. 后端添加 `/api/auth/password` 端点用于当前用户修改密码
2. 或修改前端调用正确的现有端点

---

### 任务3: 冒烟测试失败

**问题描述**: UI冒烟测试有1个失败用例

**根因分析**:
- `tests/test_ui/specs/smoke/archives/` 目录下的旧测试文件导致模块导入错误
- Playwright扫描整个tests目录时加载了archives中的文件，导致错误

**修复方案**:
1. 从playwright配置中排除archives目录
2. 或删除/移动archives目录

---

## 验收标准

- [ ] BUG-089 修复并验证通过
- [ ] BUG-090 修复并验证通过
- [ ] 冒烟测试 100% 通过
