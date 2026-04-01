#!/bin/bash
# 快速启动脚本

set -e

echo "🚀 AI Agent Platform - 快速启动"
echo ""

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✅ Python 版本：$python_version"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 创建必要目录
echo "📁 创建目录..."
mkdir -p data logs

# 检查配置文件
if [ ! -f "config/.env" ]; then
    echo "⚠️  配置文件不存在，从示例复制..."
    cp config/.env.example config/.env
    echo "📝 请编辑 config/.env 填入 API Key"
fi

# 启动服务
echo ""
echo "🎯 启动服务..."
echo "📚 API 文档：http://localhost:8000/docs"
echo "💡 按 Ctrl+C 停止服务"
echo ""

uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
