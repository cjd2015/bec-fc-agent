#!/bin/bash
# 阿里云函数计算简化部署脚本（带 AccountID）

set -e

echo "🚀 阿里云函数计算部署"
echo "======================"
echo ""

# 检查环境变量
echo "📝 检查环境变量..."
if [ -z "$ALIYUN_ACCESS_KEY_ID" ]; then
    echo "❌ ALIYUN_ACCESS_KEY_ID 未设置"
    exit 1
fi
if [ -z "$ALIYUN_ACCESS_KEY_SECRET" ]; then
    echo "❌ ALIYUN_ACCESS_KEY_SECRET 未设置"
    exit 1
fi
if [ -z "$ALIYUN_USER_ID" ]; then
    echo "⚠️  ALIYUN_USER_ID 未设置，尝试自动获取..."
fi

echo "✅ 环境变量检查通过"

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

# 获取 AccountID（如未提供）
if [ -z "$ALIYUN_USER_ID" ]; then
    echo ""
    echo "🔍 获取 AccountID..."
    ALIYUN_USER_ID=$(aliyun sts GetCallerIdentity --profile aliyun 2>&1 | grep -o '"AccountId":"[^"]*"' | cut -d'"' -f4)
    if [ -z "$ALIYUN_USER_ID" ]; then
        echo "⚠️  无法自动获取 AccountID，请手动设置 ALIYUN_USER_ID 环境变量"
    else
        echo "✅ 获取到 AccountID: $ALIYUN_USER_ID"
        export ALIYUN_USER_ID
    fi
fi

# 创建服务
echo ""
echo "📦 创建函数计算服务..."
aliyun fc CreateService \
    --serviceName ai-agent-service \
    --description "AI Agent Platform Service" \
    --internetAccess true \
    --logConfig "{\"project\":\"ai-agent-logs\",\"logstore\":\"ai-agent-executions\"}" \
    2>&1 || echo "⚠️  服务可能已存在"

# 准备代码
echo ""
echo "📁 准备函数代码..."
cd /root/.openclaw/workspace/projects/ai-agent-platform
zip -r fc-code.zip fc-code/*

# 创建函数
echo ""
echo "🚀 创建函数..."
aliyun fc CreateFunction \
    --serviceName ai-agent-service \
    --functionName agent-api \
    --description "Agent API Function" \
    --runtime custom \
    --handler index.handler \
    --codeZipFile fc-code.zip \
    --memorySize 1024 \
    --timeout 60 \
    --initializationTimeout 30 \
    --initializer index.initializer \
    --environmentVariables "{\"ALIYUN_ACCESS_KEY_ID\":\"$ALIYUN_ACCESS_KEY_ID\",\"ALIYUN_ACCESS_KEY_SECRET\":\"$ALIYUN_ACCESS_KEY_SECRET\",\"DATABASE_URL\":\"sqlite+aiosqlite:///tmp/agent.db\",\"LOG_LEVEL\":\"INFO\"}" \
    --customRuntimeConfig "{\"command\":[\"python3\",\"-m\",\"uvicorn\",\"main:app\",\"--host\",\"0.0.0.0\",\"--port\",\"8080\"],\"port\":8080}" \
    2>&1 || aliyun fc UpdateFunction \
    --serviceName ai-agent-service \
    --functionName agent-api \
    --codeZipFile fc-code.zip \
    2>&1 || echo "⚠️  函数更新失败"

# 创建 HTTP 触发器
echo ""
echo "🌐 创建 HTTP 触发器..."
aliyun fc CreateTrigger \
    --serviceName ai-agent-service \
    --functionName agent-api \
    --triggerName http-trigger \
    --triggerType http \
    --triggerConfig "{\"authType\":\"anonymous\",\"methods\":[\"GET\",\"POST\",\"PUT\",\"DELETE\",\"PATCH\"]}" \
    2>&1 || echo "⚠️  触发器可能已存在"

# 清理
echo ""
echo "🧹 清理临时文件..."
rm -f fc-code.zip

echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "   https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com"
echo "   https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/docs"
echo "   https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/api/v1/agent"
echo ""
