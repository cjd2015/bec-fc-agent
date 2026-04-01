# 阿里云函数计算 - 部署就绪

**更新时间:** 2026-03-30 17:20  
**状态:** 🟢 准备部署

---

## ✅ 已配置环境变量

- ✅ `ALIYUN_ACCESS_KEY_ID`
- ✅ `ALIYUN_ACCESS_KEY_SECRET`
- ✅ `ALIYUN_USER_ID` (AccountID)

---

## 🚀 一键部署

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
./scripts/deploy-fc-simple.sh
```

---

## 📋 部署流程

1. ✅ 检查环境变量
2. ✅ 配置阿里云 CLI
3. ✅ 自动获取 AccountID（如未提供）
4. ✅ 创建函数计算服务
5. ✅ 打包函数代码
6. ✅ 创建/更新函数
7. ✅ 创建 HTTP 触发器
8. ✅ 清理临时文件

---

## 🌐 访问地址（部署后）

**函数计算默认地址:**
```
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/docs
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/api/v1/agent
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/health
```

**完整 URL 格式:**
```
https://{accountId}.{region}.fc.aliyuncs.com/2016-08-15/proxy/{serviceName}/{functionName}/
```

---

## 📊 验证部署

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

## 📝 查看日志

```bash
# 使用阿里云 CLI
aliyun fc GetFunctionLogs \
  --serviceName ai-agent-service \
  --functionName agent-api \
  --limit 10

# 使用 Serverless Devs
s logs --function-name agent-api --tail
```

---

## 💰 成本

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
# 检查 RAM 权限
aliyun ram ListPoliciesForUser --UserName <your-username>
```

### 问题 2: AccountID 错误
```bash
# 获取正确的 AccountID
aliyun sts GetCallerIdentity
```

### 问题 3: 服务已存在
```bash
# 删除旧服务
aliyun fc DeleteService --serviceName ai-agent-service
# 重新部署
./scripts/deploy-fc-simple.sh
```

---

## ✅ 部署检查清单

- [x] 环境变量已设置
- [x] 阿里云 CLI 已配置
- [x] AccountID 已配置
- [x] 函数代码已准备
- [x] 部署脚本已更新
- [ ] 执行部署脚本
- [ ] 验证部署成功

---

**下一步:** 执行 `./scripts/deploy-fc-simple.sh` 开始部署！
