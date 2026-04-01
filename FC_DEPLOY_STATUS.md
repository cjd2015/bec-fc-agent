# 阿里云函数计算部署状态

**更新时间:** 2026-03-30 16:55  
**状态:** 🟡 准备部署

---

## 📋 部署准备

### 已完成
- ✅ 环境变量配置（ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET）
- ✅ 阿里云 CLI 安装和配置
- ✅ Serverless Devs 安装
- ✅ 函数代码准备（fc-code/）
- ✅ 配置文件准备（fc-config/s.yaml）
- ✅ 依赖安装（requirements-fc.txt）
- ✅ 部署脚本创建（deploy-fc.sh, deploy-fc-simple.sh）

### 待完成
- ⏳ 函数计算服务创建
- ⏳ 函数创建
- ⏳ HTTP 触发器配置
- ⏳ 部署验证

---

## 🚀 部署命令

### 方案 A：使用 Serverless Devs（推荐）

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform/fc-config
s deploy -y
```

### 方案 B：使用阿里云 CLI（简化版）

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
./scripts/deploy-fc-simple.sh
```

---

## 🌐 访问地址（部署后）

**默认地址：**
```
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/docs
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/api/v1/agent
```

**自定义域名（可选）：**
```
https://ai-agent.datahive.site
```

---

## 📊 验证步骤

```bash
# 1. 健康检查
curl https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/health

# 2. API 文档
curl https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/docs

# 3. Agent API
curl https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/api/v1/agent

# 4. 创建 Agent
curl -X POST https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"name": "测试 Agent", "model": "codex-mini-latest"}'
```

---

## 📝 日志查看

```bash
# 使用 Serverless Devs
s logs --function-name agent-api --tail

# 使用阿里云 CLI
aliyun fc GetFunctionLogs \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --limit 10
```

---

## ⚠️ 注意事项

1. **冷启动:** 首次调用会有 1-3 秒冷启动时间
2. **超时:** 函数超时设置为 60 秒
3. **内存:** 配置为 1024MB
4. **存储:** /tmp 目录有 512MB 临时存储空间

---

## 💰 成本估算

**免费额度:**
- 100 万调用/月
- 400,000 CU-秒/月
- 100 GB 流量/月

**预期成本:**
- 初期（<10 万调用）: ¥0
- 中期（10-100 万调用）: ¥0-100/月
- 后期（>100 万调用）: ¥100-500/月

---

## 🔧 故障排查

### 问题 1: 权限错误
```bash
# 检查 RAM 角色
aliyun ram GetRole --RoleName AliyunFCDefaultRole
```

### 问题 2: 服务已存在
```bash
# 删除旧服务重新创建
aliyun fc DeleteService --serviceName ai-agent-service
```

### 问题 3: 代码包过大
```bash
# 优化依赖
pip install -r requirements.txt --no-deps -t ./
```

---

**下一步:** 执行 `./scripts/deploy-fc-simple.sh` 开始部署
