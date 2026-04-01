#!/bin/bash
# Nginx 部署脚本
# 用法：./scripts/deploy-nginx.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
NGINX_CONF="$PROJECT_DIR/config/nginx/sites-available/datahive.site"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"

echo "🚀 Nginx 部署脚本"
echo "=================="
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  请使用 sudo 运行此脚本"
    echo "   sudo $0"
    exit 1
fi

# 1. 检查 Nginx 是否安装
echo "📦 检查 Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx 未安装，正在安装..."
    apt update
    apt install -y nginx
fi
echo "✅ Nginx 已安装：$(nginx -v 2>&1)"

# 2. 检查配置文件
echo ""
echo "📄 检查配置文件..."
if [ ! -f "$NGINX_CONF" ]; then
    echo "❌ 配置文件不存在：$NGINX_CONF"
    exit 1
fi
echo "✅ 配置文件存在"

# 3. 检查 SSL 证书
echo ""
echo "🔒 检查 SSL 证书..."
CERT_DIR="/root/.openclaw/workspace/certs/datahive.site"
if [ ! -f "$CERT_DIR/fullchain.pem" ] || [ ! -f "$CERT_DIR/privkey.pem" ]; then
    echo "❌ SSL 证书文件不存在"
    exit 1
fi
echo "✅ SSL 证书存在"

# 4. 创建符号链接
echo ""
echo "🔗 创建符号链接..."
if [ -f "$NGINX_SITES_ENABLED/datahive.site" ]; then
    echo "⚠️  已存在符号链接，删除旧的..."
    rm -f "$NGINX_SITES_ENABLED/datahive.site"
fi
ln -s "$NGINX_CONF" "$NGINX_SITES_ENABLED/datahive.site"
echo "✅ 符号链接创建成功"

# 5. 删除默认站点（避免冲突）
echo ""
echo "🗑️  删除默认站点..."
if [ -f "$NGINX_SITES_ENABLED/default" ]; then
    rm -f "$NGINX_SITES_ENABLED/default"
    echo "✅ 默认站点已删除"
else
    echo "ℹ️  默认站点不存在"
fi

# 6. 测试 Nginx 配置
echo ""
echo "🔍 测试 Nginx 配置..."
if nginx -t; then
    echo "✅ Nginx 配置测试通过"
else
    echo "❌ Nginx 配置测试失败"
    exit 1
fi

# 7. 重启 Nginx
echo ""
echo "🔄 重启 Nginx..."
systemctl restart nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx 重启成功"
else
    echo "❌ Nginx 重启失败"
    exit 1
fi

# 8. 设置开机自启
echo ""
echo "⚙️  设置开机自启..."
systemctl enable nginx
echo "✅ 开机自启已设置"

# 9. 配置防火墙
echo ""
echo "🔥 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    echo "✅ 防火墙规则已添加"
else
    echo "ℹ️  UFW 未安装，跳过"
fi

# 10. 验证
echo ""
echo "✅ 部署完成！"
echo ""
echo "📊 验证步骤:"
echo "   1. 检查 Nginx 状态：systemctl status nginx"
echo "   2. 测试 HTTP 跳转：curl -I http://datahive.site"
echo "   3. 测试 HTTPS: curl -I https://datahive.site"
echo "   4. 查看日志：tail -f /var/log/nginx/access.log"
echo ""
echo "🌐 访问地址:"
echo "   https://datahive.site"
echo "   https://www.datahive.site"
echo ""
