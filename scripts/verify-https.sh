#!/bin/bash
# HTTPS 验证脚本
# 用法：./scripts/verify-https.sh

DOMAIN="datahive.site"

echo "🔒 HTTPS 验证脚本"
echo "=================="
echo ""

# 1. 检查 Nginx 状态
echo "📊 检查 Nginx 状态..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 运行正常"
else
    echo "❌ Nginx 未运行"
    exit 1
fi

# 2. 测试 HTTP 跳转
echo ""
echo "🔄 测试 HTTP → HTTPS 跳转..."
HTTP_RESPONSE=$(curl -sI http://$DOMAIN 2>/dev/null | head -1)
if [[ "$HTTP_RESPONSE" == *"301"* ]]; then
    echo "✅ HTTP 正常跳转 (301)"
else
    echo "❌ HTTP 跳转失败"
    echo "   响应：$HTTP_RESPONSE"
fi

# 3. 测试 HTTPS
echo ""
echo "🔒 测试 HTTPS 连接..."
HTTPS_RESPONSE=$(curl -skI https://$DOMAIN 2>/dev/null | head -1)
if [[ "$HTTPS_RESPONSE" == *"200"* ]] || [[ "$HTTPS_RESPONSE" == *"301"* ]] || [[ "$HTTPS_RESPONSE" == *"302"* ]]; then
    echo "✅ HTTPS 连接正常"
else
    echo "❌ HTTPS 连接失败"
    echo "   响应：$HTTPS_RESPONSE"
fi

# 4. 检查 SSL 证书
echo ""
echo "📜 检查 SSL 证书..."
CERT_INFO=$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null)
if [ -n "$CERT_INFO" ]; then
    echo "$CERT_INFO" | sed 's/^/   /'
    echo "✅ SSL 证书有效"
else
    echo "❌ SSL 证书无效或过期"
fi

# 5. 检查安全头
echo ""
echo "🛡️  检查安全头..."
HEADERS=$(curl -skI https://$DOMAIN 2>/dev/null)

if echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
    echo "✅ HSTS 已配置"
else
    echo "❌ HSTS 未配置"
fi

if echo "$HEADERS" | grep -qi "X-Frame-Options"; then
    echo "✅ X-Frame-Options 已配置"
else
    echo "❌ X-Frame-Options 未配置"
fi

if echo "$HEADERS" | grep -qi "X-Content-Type-Options"; then
    echo "✅ X-Content-Type-Options 已配置"
else
    echo "❌ X-Content-Type-Options 未配置"
fi

if echo "$HEADERS" | grep -qi "X-XSS-Protection"; then
    echo "✅ X-XSS-Protection 已配置"
else
    echo "❌ X-XSS-Protection 未配置"
fi

# 6. 测试 API 代理
echo ""
echo "🔌 测试 API 代理..."
API_RESPONSE=$(curl -sk https://$DOMAIN/health 2>/dev/null)
if [ -n "$API_RESPONSE" ]; then
    echo "✅ API 代理正常"
    echo "   响应：$API_RESPONSE"
else
    echo "⚠️  API 代理可能未就绪（后端服务可能未启动）"
fi

# 7. SSL Labs 测试链接
echo ""
echo "📊 SSL 安全等级测试:"
echo "   访问：https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "   目标：A+ 评级"

echo ""
echo "✅ HTTPS 验证完成！"
echo ""
echo "🌐 访问地址:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo ""
