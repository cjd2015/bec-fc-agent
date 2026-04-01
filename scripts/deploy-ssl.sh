#!/bin/bash
# SSL 证书部署脚本
# 用法：./scripts/deploy-ssl.sh

set -e

CERT_DIR="/root/.openclaw/workspace/certs/datahive.site"
NGINX_CONF="/etc/nginx/sites-available/datahive.site"

echo "🔒 SSL 证书部署脚本"
echo "=================="

# 检查证书文件
echo ""
echo "📁 检查证书文件..."
if [ ! -f "$CERT_DIR/fullchain.pem" ]; then
    echo "❌ 错误：证书文件不存在 $CERT_DIR/fullchain.pem"
    exit 1
fi

if [ ! -f "$CERT_DIR/privkey.pem" ]; then
    echo "❌ 错误：私钥文件不存在 $CERT_DIR/privkey.pem"
    exit 1
fi

echo "✅ 证书文件存在"

# 检查文件权限
echo ""
echo "🔐 检查文件权限..."
PRIVKEY_PERMS=$(stat -c %a "$CERT_DIR/privkey.pem")
if [ "$PRIVKEY_PERMS" != "600" ]; then
    echo "⚠️  私钥权限不正确，正在修复..."
    chmod 600 "$CERT_DIR/privkey.pem"
fi
echo "✅ 文件权限正确"

# 验证证书
echo ""
echo "🔍 验证证书..."
if ! openssl x509 -in "$CERT_DIR/fullchain.pem" -noout -checkend 0 2>/dev/null; then
    echo "⚠️  警告：证书可能已过期或即将过期"
else
    echo "✅ 证书有效"
fi

# 显示证书信息
echo ""
echo "📋 证书信息:"
openssl x509 -in "$CERT_DIR/fullchain.pem" -noout -subject -dates | sed 's/^/   /'

# Nginx 配置
echo ""
echo "📝 Nginx 配置路径:"
echo "   $NGINX_CONF"
echo ""
echo "📄 配置文件已生成在:"
echo "   /root/.openclaw/workspace/projects/ai-agent-platform/config/nginx/ssl.conf"
echo ""
echo "🔧 部署步骤:"
echo "   1. 复制配置到 Nginx:"
echo "      sudo cp config/nginx/ssl.conf /etc/nginx/sites-available/datahive.site"
echo "      sudo ln -s /etc/nginx/sites-available/datahive.site /etc/nginx/sites-enabled/"
echo ""
echo "   2. 测试 Nginx 配置:"
echo "      sudo nginx -t"
echo ""
echo "   3. 重启 Nginx:"
echo "      sudo systemctl restart nginx"
echo ""
echo "   4. 验证 HTTPS:"
echo "      curl -I https://datahive.site"
echo ""
echo "✅ SSL 证书配置完成！"
