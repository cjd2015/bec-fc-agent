# 阿里云函数计算部署 - 网络和权限问题修复清单

**更新日期:** 2026-03-30  
**用途:** 排查和修复部署问题

---

## 🔍 问题诊断流程

### 第一步：检查基础配置

```bash
# 1. 检查环境变量
echo "ALIYUN_ACCESS_KEY_ID: ${ALIYUN_ACCESS_KEY_ID:0:10}***"
echo "ALIYUN_ACCESS_KEY_SECRET: ${ALIYUN_ACCESS_KEY_SECRET:0:10}***"
echo "ALIYUN_USER_ID: ${ALIYUN_USER_ID}"

# 2. 检查阿里云 CLI
aliyun version
aliyun configure list

# 3. 测试凭证
aliyun sts GetCallerIdentity
```

**预期输出：**
```
✅ 环境变量已设置
✅ 阿里云 CLI 已安装
✅ 凭证有效，显示 AccountID
```

---

## 🌐 网络问题修复

### 问题 1：无法访问阿里云 API

**症状：**
```
curl: (28) Failed to connect to fc.cn-hangzhou.aliyuncs.com
```

**修复步骤：**

```bash
# 1. 检查 DNS 解析
nslookup fc.cn-hangzhou.aliyuncs.com
ping -c 4 fc.cn-hangzhou.aliyuncs.com

# 2. 如 DNS 失败，修改 DNS
sudo tee /etc/resolv.conf > /dev/null << EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF

# 3. 检查防火墙
sudo ufw status
sudo ufw allow out 443/tcp  # 允许 HTTPS 出站

# 4. 检查代理设置
echo $http_proxy
echo $https_proxy
unset http_proxy
unset https_proxy

# 5. 测试连接
curl -I https://fc.cn-hangzhou.aliyuncs.com
```

---

### 问题 2：HTTPS 证书验证失败

**症状：**
```
curl: (60) SSL certificate problem
```

**修复步骤：**

```bash
# 1. 更新 CA 证书
sudo apt-get update
sudo apt-get install -y ca-certificates

# 2. 重新配置证书
sudo update-ca-certificates

# 3. 测试 HTTPS
curl -v https://fc.cn-hangzhou.aliyuncs.com
```

---

### 问题 3：连接超时

**症状：**
```
curl: (28) Connection timed out
```

**修复步骤：**

```bash
# 1. 检查网络延迟
ping -c 10 fc.cn-hangzhou.aliyuncs.com

# 2. 检查路由
traceroute fc.cn-hangzhou.aliyuncs.com

# 3. 尝试其他区域
export ALIYUN_REGION=cn-shanghai
# 或
export ALIYUN_REGION=cn-beijing

# 4. 增加超时时间
export REQUESTS_TIMEOUT=60
```

---

## 🔐 权限问题修复

### 问题 4：AccessKey 无效

**症状：**
```
InvalidAccessKeyId.NotFound
```

**修复步骤：**

```bash
# 1. 验证 AK/SK 格式
echo $ALIYUN_ACCESS_KEY_ID  # 应该是 LTAI5t 开头
echo $ALIYUN_ACCESS_KEY_SECRET  # 应该是 30 位字符

# 2. 重新配置
aliyun configure set \
  --profile aliyun \
  --mode AK \
  --access-key-id "$ALIYUN_ACCESS_KEY_ID" \
  --access-key-secret "$ALIYUN_ACCESS_KEY_SECRET" \
  --region cn-hangzhou

# 3. 验证配置
aliyun sts GetCallerIdentity

# 4. 如仍失败，重新创建 AK
# 访问：https://ram.console.aliyun.com/manage/ak
```

---

### 问题 5：权限不足

**症状：**
```
Forbidden.RAM
You are not authorized to operate FC
```

**修复步骤：**

```bash
# 1. 检查当前用户权限
aliyun ram ListPoliciesForUser --UserName <your-username>

# 2. 需要的权限
# - AliyunFCFullAccess (函数计算完全访问)
# - AliyunSTSAssumeRoleAccess (STS 授权)
# - AliyunLogFullAccess (日志服务访问)

# 3. 添加权限（需要主账号操作）
# 访问：https://ram.console.aliyun.com/users
# 找到用户 → 添加权限 → 选择上述策略

# 4. 验证权限
aliyun fc ListServices
```

---

### 问题 6：RAM 角色未配置

**症状：**
```
RoleNotFound: The role AliyunFCDefaultRole does not exist
```

**修复步骤：**

```bash
# 1. 创建 RAM 角色
aliyun ram CreateRole \
  --RoleName AliyunFCDefaultRole \
  --AssumeRolePolicyDocument '{
    "Statement": [{
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {"Service": ["fc.aliyuncs.com"]}
    }],
    "Version": "1"
  }'

# 2. 添加权限策略
aliyun ram AttachPolicyToRole \
  --PolicyType System \
  --PolicyName AliyunFCFullAccess \
  --RoleName AliyunFCDefaultRole

# 3. 验证角色
aliyun ram GetRole --RoleName AliyunFCDefaultRole
```

---

### 问题 7：AccountID 错误

**症状：**
```
InvalidAccountId.Malformed
```

**修复步骤：**

```bash
# 1. 获取正确的 AccountID
aliyun sts GetCallerIdentity | grep AccountId

# 2. 设置环境变量
export ALIYUN_USER_ID=$(aliyun sts GetCallerIdentity | grep -o '"AccountId":"[^"]*"' | cut -d'"' -f4)
echo "AccountID: $ALIYUN_USER_ID"

# 3. 验证格式
# AccountID 应该是 16 位数字
echo $ALIYUN_USER_ID | wc -c  # 应该是 17 (16 位 + 换行)
```

---

## 📦 服务/函数相关问题

### 问题 8：服务已存在

**症状：**
```
ServiceAlreadyExist
```

**修复步骤：**

```bash
# 选项 1：使用现有服务
echo "⚠️ 服务已存在，继续使用"

# 选项 2：删除重建
aliyun fc DeleteService --serviceName ai-agent-service

# 选项 3：更新服务
aliyun fc UpdateService --serviceName ai-agent-service --description "Updated"
```

---

### 问题 9：函数创建失败

**症状：**
```
InvalidArgument: CodeZipFile not found
```

**修复步骤：**

```bash
# 1. 检查代码包
cd /root/.openclaw/workspace/projects/ai-agent-platform
ls -lh fc-code.zip

# 2. 重新打包
cd fc-code
zip -r ../fc-code.zip ./*
cd ..

# 3. 验证包内容
unzip -l fc-code.zip | head -20

# 4. 检查包大小
du -sh fc-code.zip
# 应该 < 50MB

# 5. 重新部署
aliyun fc CreateFunction \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --codeZipFile fc-code.zip \
  ...
```

---

### 问题 10：触发器创建失败

**症状：**
```
TriggerAlreadyExist
```

**修复步骤：**

```bash
# 1. 删除旧触发器
aliyun fc DeleteTrigger \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --triggerName http-trigger

# 2. 重新创建
aliyun fc CreateTrigger \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --triggerName http-trigger \
  --triggerType http \
  --triggerConfig '{"authType":"anonymous","methods":["GET","POST","PUT","DELETE"]}'
```

---

## 🛠️ 完整修复流程

### 快速修复脚本

```bash
#!/bin/bash
# 保存为 fix-deploy.sh

set -e

echo "🔧 开始修复部署问题..."

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
aliyun sts GetCallerIdentity > /dev/null || {
  echo "❌ 凭证无效，请检查 AK/SK"
  exit 1
}

# 3. 获取 AccountID
echo "📝 获取 AccountID..."
export ALIYUN_USER_ID=$(aliyun sts GetCallerIdentity | grep -o '"AccountId":"[^"]*"' | cut -d'"' -f4)
echo "✅ AccountID: $ALIYUN_USER_ID"

# 4. 创建服务
echo "📦 创建服务..."
aliyun fc CreateService \
  --serviceName ai-agent-service \
  --description "AI Agent Platform Service" \
  --internetAccess true

# 5. 打包代码
echo "📁 打包代码..."
cd /root/.openclaw/workspace/projects/ai-agent-platform/fc-code
zip -r ../fc-code.zip ./*

# 6. 创建函数
echo "🚀 创建函数..."
cd ..
aliyun fc CreateFunction \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --runtime custom \
  --handler index.handler \
  --codeZipFile fc-code.zip \
  --memorySize 1024 \
  --timeout 60 \
  --customRuntimeConfig '{"command":["python3","-m","uvicorn","main:app","--host","0.0.0.0","--port","8080"],"port":8080}'

# 7. 创建触发器
echo "🌐 创建触发器..."
aliyun fc CreateTrigger \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --triggerName http-trigger \
  --triggerType http \
  --triggerConfig '{"authType":"anonymous","methods":["GET","POST","PUT","DELETE"]}'

# 8. 清理
rm -f fc-code.zip

echo ""
echo "✅ 修复完成！"
echo ""
echo "🌐 访问地址:"
echo "   https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com"
```

---

## 📊 验证清单

修复后执行以下验证：

```bash
# 1. 检查服务
aliyun fc GetService --serviceName ai-agent-service

# 2. 检查函数
aliyun fc GetFunction --serviceName ai-agent-service --functionName agent-api

# 3. 检查触发器
aliyun fc GetTrigger --serviceName ai-agent-service --functionName agent-api --triggerName http-trigger

# 4. 测试 API
curl https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/health

# 5. 测试文档
curl https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/docs
```

---

## 📞 获取帮助

如以上步骤都无法解决问题，请收集以下信息：

```bash
# 1. 系统信息
uname -a
cat /etc/os-release

# 2. 网络信息
ping -c 4 fc.cn-hangzhou.aliyuncs.com
curl -v https://fc.cn-hangzhou.aliyuncs.com 2>&1 | head -30

# 3. 阿里云 CLI 信息
aliyun version
aliyun configure list

# 4. 错误日志
cat /tmp/fc-deploy-final.log

# 5. 凭证验证（隐藏敏感信息）
aliyun sts GetCallerIdentity 2>&1 | grep -v "Secret"
```

---

**下一步：** 根据具体错误信息，执行对应的修复步骤
