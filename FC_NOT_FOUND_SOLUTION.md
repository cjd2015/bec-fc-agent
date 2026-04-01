# 函数计算部署成功但控制台找不到 - 完整解决方案

**问题:** 部署脚本显示成功，但在阿里云 FC 控制台（杭州区域）找不到函数

---

## 🔍 可能原因

### 1️⃣ 部署实际失败（最可能）

**症状:**
- 部署脚本输出"成功"但实际有错误
- 控制台没有任何服务/函数

**验证:**
```bash
# 直接调用 FC API 查看
aliyun fc ListServices --region cn-hangzhou
```

**如返回空或错误，说明部署失败**

---

### 2️⃣ 区域不匹配

**症状:**
- 部署在区域 A，在区域 B 查看

**验证:**
```bash
# 检查所有区域
for region in cn-hangzhou cn-shanghai cn-beijing cn-shenzhen; do
  echo "=== $region ==="
  aliyun fc ListServices --region $region 2>&1 | head -3
done
```

---

### 3️⃣ AccountID 不匹配

**症状:**
- 使用账号 A 的 AK 部署，用账号 B 登录控制台

**验证:**
```bash
# 获取部署使用的 AccountID
aliyun sts GetCallerIdentity | grep AccountId

# 控制台右上角查看当前 AccountID
# 两者必须一致
```

---

### 4️⃣ FC 版本问题 (2.0 vs 3.0)

**症状:**
- 部署到 FC 2.0，在 FC 3.0 控制台查看

**解决:**
- FC 2.0 控制台：https://fc.console.aliyun.com
- FC 3.0 控制台：https://fcnext.console.aliyun.com

---

## 🛠️ 解决方案

### 方案 1：重新部署（推荐）

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform

# 1. 清理旧部署
aliyun fc DeleteTrigger \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --triggerName http-trigger \
  --region cn-hangzhou 2>/dev/null || true

aliyun fc DeleteFunction \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --region cn-hangzhou 2>/dev/null || true

aliyun fc DeleteService \
  --serviceName ai-agent-service \
  --region cn-hangzhou 2>/dev/null || true

# 2. 验证凭证
echo "验证凭证..."
aliyun sts GetCallerIdentity

# 3. 重新部署
./fix-deploy.sh

# 4. 验证部署
echo "验证部署..."
aliyun fc GetService --serviceName ai-agent-service --region cn-hangzhou
aliyun fc ListFunctions --serviceName ai-agent-service --region cn-hangzhou
```

---

### 方案 2：手动在控制台创建

**步骤:**

1. **访问 FC 控制台**
   - FC 2.0: https://fc.console.aliyun.com
   - FC 3.0: https://fcnext.console.aliyun.com

2. **确认区域：华东 1（杭州）**

3. **创建服务**
   - 服务名称：`ai-agent-service`
   - 描述：AI Agent Platform Service

4. **创建函数**
   - 函数名称：`agent-api`
   - 运行环境：Custom Runtime
   - 内存：1024MB
   - 超时：60 秒
   - 启动命令：`python3 -m uvicorn main:app --host 0.0.0.0 --port 8080`

5. **上传代码**
   - 打包：`cd fc-code && zip -r ../fc-code.zip ./*`
   - 上传 `fc-code.zip`

6. **配置触发器**
   - 类型：HTTP
   - 认证：anonymous

---

### 方案 3：使用 Terraform（高级）

```bash
# 创建 terraform 配置
cat > main.tf << 'EOF'
provider "alicloud" {
  access_key = var.access_key
  secret_key = var.secret_key
  region     = "cn-hangzhou"
}

resource "alicloud_fc_service" "ai_agent" {
  name        = "ai-agent-service"
  description = "AI Agent Platform Service"
}

resource "alicloud_fc_function" "agent_api" {
  service      = alicloud_fc_service.ai_agent.name
  name         = "agent-api"
  runtime      = "custom"
  handler      = "index.handler"
  memory_size  = 1024
  timeout      = 60
  # ... 更多配置
}
EOF

# 部署
terraform init
terraform apply
```

---

## 📋 验证清单

部署成功后应能看到：

### CLI 验证
```bash
# 1. 列出服务
aliyun fc ListServices --region cn-hangzhou
# 应显示：ai-agent-service

# 2. 获取服务详情
aliyun fc GetService --serviceName ai-agent-service --region cn-hangzhou
# 应显示服务信息

# 3. 列出函数
aliyun fc ListFunctions --serviceName ai-agent-service --region cn-hangzhou
# 应显示：agent-api

# 4. 获取函数详情
aliyun fc GetFunction --serviceName ai-agent-service --functionName agent-api --region cn-hangzhou
# 应显示函数配置
```

### 控制台验证
1. 访问：https://fcnext.console.aliyun.com
2. 选择区域：华东 1（杭州）
3. 查看服务列表：应有 `ai-agent-service`
4. 点击进入 → 查看函数：应有 `agent-api`

---

## 🔧 常见错误和解决

### 错误 1：PermissionDenied
```
You are not authorized to operate FC
```
**解决:** 添加 RAM 权限 `AliyunFCFullAccess`

### 错误 2：InvalidAccessKeyId
```
InvalidAccessKeyId.NotFound
```
**解决:** 检查 AK/SK 是否正确

### 错误 3：ServiceNotFound
```
Service ai-agent-service does not exist
```
**解决:** 服务未创建，重新部署

### 错误 4：RegionNotSupport
```
Region cn-hangzhou not support
```
**解决:** 确认区域支持 FC 服务

---

## 📞 获取帮助

请提供以下信息：

1. **部署日志**
   ```bash
   cat /tmp/fc-redeploy.log
   ```

2. **CLI 验证结果**
   ```bash
   aliyun fc ListServices --region cn-hangzhou
   ```

3. **AccountID**
   ```bash
   aliyun sts GetCallerIdentity
   ```

4. **控制台截图**
   - 显示区域
   - 显示服务列表

---

**下一步：** 执行方案 1 的重新部署命令
