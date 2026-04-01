#!/bin/bash
# 完整部署脚本 - 前端 + 后端 + Nginx
# 用法：sudo ./scripts/deploy-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 AI Agent Platform 完整部署"
echo "=============================="
echo ""

# 1. 构建前端
echo "📦 构建前端..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "   安装依赖..."
    npm install
fi
echo "   构建前端..."
npm run build
echo "✅ 前端构建完成"

# 2. 启动后端
echo ""
echo "🔧 启动后端服务..."
cd "$PROJECT_DIR"
if [ ! -d "venv" ]; then
    echo "   创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# 停止旧的后端进程
pkill -f "uvicorn src.api.main" 2>/dev/null || true
sleep 2

# 启动新的后端进程
nohup uvicorn src.api.main:app --host 127.0.0.1 --port 8000 > logs/backend.log 2>&1 &
sleep 3

if pgrep -f "uvicorn src.api.main" > /dev/null; then
    echo "✅ 后端服务已启动 (端口 8000)"
else
    echo "❌ 后端服务启动失败"
    exit 1
fi

# 3. 部署 Nginx
echo ""
echo "🌐 部署 Nginx..."
"$SCRIPT_DIR/deploy-nginx.sh"

# 4. 验证
echo ""
echo "✅ 验证部署..."
echo ""

# 检查后端
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
fi

# 检查 HTTPS
if curl -skI https://datahive.site > /dev/null; then
    echo "✅ HTTPS 访问正常"
else
    echo "❌ HTTPS 访问异常"
fi

# 检查 API
if curl -sk https://datahive.site/api/v1/agent > /dev/null; then
    echo "✅ API 代理正常"
else
    echo "⚠️  API 代理可能需要配置"
fi

echo ""
echo "🎉 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "   https://datahive.site"
echo "   https://www.datahive.site"
echo ""
echo "📊 API 文档:"
echo "   https://datahive.site/docs"
echo ""
echo "📝 查看日志:"
echo "   后端：tail -f $PROJECT_DIR/logs/backend.log"
echo "   Nginx: tail -f /var/log/nginx/access.log"
echo ""
