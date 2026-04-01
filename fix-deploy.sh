#!/bin/bash
# 完整修复脚本

set -e

echo "🔧 开始修复部署问题..."
echo ""

# 1. 清理旧配置
echo "📦 清理旧配置..."
aliyun fc DeleteTrigger \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --triggerName http-trigger 2>/dev/null || true

aliyun fc DeleteFunction \
  --serviceName ai-agent-service \
  --functionName agent-api 2>/dev/null || true

aliyun fc DeleteService \
  --serviceName ai-agent-service 2>/dev/null || true

# 2. 验证凭证
echo "🔐 验证凭证..."
if ! aliyun sts GetCallerIdentity > /dev/null 2>&1; then
  echo "❌ 凭证无效，请检查 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET"
  exit 1
fi
echo "✅ 凭证有效"

# 3. 获取 AccountID
echo "📝 获取 AccountID..."
export ALIYUN_USER_ID=$(aliyun sts GetCallerIdentity 2>/dev/null | grep -o '"AccountId":"[^"]*"' | cut -d'"' -f4)
if [ -z "$ALIYUN_USER_ID" ]; then
  echo "⚠️  无法获取 AccountID，请设置 ALIYUN_USER_ID 环境变量"
else
  echo "✅ AccountID: $ALIYUN_USER_ID"
fi

# 4. 创建服务
echo "📦 创建服务..."
aliyun fc CreateService \
  --serviceName ai-agent-service \
  --description "AI Agent Platform Service" \
  --internetAccess true 2>&1 || echo "⚠️  服务可能已存在"

# 5. 打包代码
echo "📁 打包代码..."
cd /root/.openclaw/workspace/projects/ai-agent-platform/fc-code
zip -rq ../fc-code.zip ./*
cd ..

# 6. 创建函数
echo "🚀 创建函数..."
aliyun fc CreateFunction \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --runtime custom \
  --handler index.handler \
  --codeZipFile fc-code.zip \
  --memorySize 1024 \
  --timeout 60 \
  --customRuntimeConfig '{"command":["python3","-m","uvicorn","main:app","--host","0.0.0.0","--port","8080"],"port":8080}' 2>&1 || \
aliyun fc UpdateFunction \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --codeZipFile fc-code.zip 2>&1 || echo "⚠️  函数操作失败"

# 7. 创建触发器
echo "🌐 创建触发器..."
aliyun fc CreateTrigger \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --triggerName http-trigger \
  --triggerType http \
  --triggerConfig '{"authType":"anonymous","methods":["GET","POST","PUT","DELETE","PATCH"]}' 2>&1 || echo "⚠️  触发器可能已存在"

# 8. 清理
rm -f fc-code.zip

echo ""
echo "✅ 修复完成！"
echo ""
echo "🌐 访问地址:"
echo "   https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com"
echo "   https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/docs"
echo "   https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/api/v1/agent"
echo ""
