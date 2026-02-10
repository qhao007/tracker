#!/bin/bash
#
# 前端代码检查脚本
# 用途：检查 JavaScript 语法错误，防止 BUG-023 类似问题
#

ERRORS=0

echo "=== Tracker 前端代码检查 ==="
echo ""

echo "1. ESLint 检查..."
if [ -f eslint.config.mjs ]; then
    if npx eslint index.html --quiet 2>/dev/null; then
        echo "   ✅ ESLint 检查通过"
    else
        echo "   ❌ ESLint 发现问题"
        npx eslint index.html 2>&1 || true
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "   ⚠️  未找到 eslint.config.mjs，跳过"
fi

echo ""
echo "2. 关键函数完整性检查..."

# 检查关键函数是否存在
FUNCTIONS=("renderTC" "renderCP" "loadCP" "loadTC" "loadProjects" "selectProject" "renderTC")

for func in "${FUNCTIONS[@]}"; do
    if grep -q "function ${func}" index.html; then
        echo "   ✅ ${func} 函数存在"
    else
        echo "   ❌ ${func} 函数缺失！"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "3. 函数定义格式检查..."

# 检查 renderTC 函数定义是否完整（有 { 结尾）
if sed -n '/function renderTC/,/^        function/p' index.html | head -1 | grep -q "{"; then
    echo "   ✅ renderTC 函数定义完整"
else
    echo "   ❌ renderTC 函数定义可能不完整"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "4. API 端点检查..."

if grep -q "API_BASE = '/api'" index.html; then
    echo "   ✅ API_BASE 定义正确"
else
    echo "   ❌ API_BASE 未定义"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "/api/projects" index.html && grep -q "/api/cp" index.html && grep -q "/api/tc" index.html; then
    echo "   ✅ API 端点定义完整"
else
    echo "   ❌ API 端点缺失"
    ERRORS=$((ERRORS + 1))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "=== 检查通过 ✅ ==="
    exit 0
else
    echo "=== 发现 $ERRORS 个问题 ❌ ==="
    exit 1
fi
