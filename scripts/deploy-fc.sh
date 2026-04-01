#!/bin/bash
# 阿里云函数计算部署脚本
# 用法：./scripts/deploy-fc.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FC_DIR="$PROJECT_DIR/fc-code"
CONFIG_FILE="$PROJECT_DIR/fc-config/s.yaml"

echo "🚀 阿里云函数计算部署脚本"
echo "=========================="
echo ""

# 检查环境变量
echo "📝 检查环境变量..."
if [ -z "$ALIYUN_ACCESS_KEY_ID" ]; then
    echo "❌ 错误：ALIYUN_ACCESS_KEY_ID 未设置"
    exit 1
fi

if [ -z "$ALIYUN_ACCESS_KEY_SECRET" ]; then
    echo "❌ 错误：ALIYUN_ACCESS_KEY_SECRET 未设置"
    exit 1
fi

echo "✅ 环境变量检查通过"

# 检查是否安装 aliyun cli
echo ""
echo "📦 检查阿里云 CLI..."
if ! command -v aliyun &> /dev/null; then
    echo "⚠️  阿里云 CLI 未安装，正在安装..."
    curl -o aliyun https://aliyuncli.oss-cn-hangzhou.aliyuncs.com/aliyun
    chmod +x aliyun
    sudo mv aliyun /usr/local/bin/
    echo "✅ 阿里云 CLI 安装完成"
else
    echo "✅ 阿里云 CLI 已安装：$(aliyun version)"
fi

# 配置阿里云 CLI
echo ""
echo "⚙️  配置阿里云 CLI..."
aliyun configure set \
    --profile aliyun \
    --mode AK \
    --access-key-id "$ALIYUN_ACCESS_KEY_ID" \
    --access-key-secret "$ALIYUN_ACCESS_KEY_SECRET" \
    --region cn-hangzhou \
    --language zh-CN

echo "✅ 阿里云 CLI 配置完成"

# 安装 Serverless Devs
echo ""
echo "📦 检查 Serverless Devs..."
if ! command -v s &> /dev/null; then
    echo "⚠️  Serverless Devs 未安装，正在安装..."
    npm install -g @serverless-devs/s
    echo "✅ Serverless Devs 安装完成"
else
    echo "✅ Serverless Devs 已安装：$(s -v)"
fi

# 准备代码
echo ""
echo "📁 准备函数代码..."
mkdir -p "$FC_DIR"

# 复制必要文件
echo "   复制源代码..."
cp -r "$PROJECT_DIR/src" "$FC_DIR/"
cp "$PROJECT_DIR/requirements-fc.txt" "$FC_DIR/requirements.txt"

# 创建启动脚本
cat > "$FC_DIR/start.sh" << 'EOF'
#!/bin/bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8080
EOF
chmod +x "$FC_DIR/start.sh"

echo "✅ 函数代码准备完成"

# 部署函数
echo ""
echo "🚀 部署函数到阿里云..."
cd "$PROJECT_DIR/fc-config"
s deploy -y

echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "   https://ai-agent.fc.aliyuncs.com"
echo "   https://ai-agent.fc.aliyuncs.com/docs"
echo "   https://ai-agent.fc.aliyuncs.com/api/v1/agent"
echo ""
echo "📊 查看日志:"
echo "   s logs --function-name agent-api"
echo ""
