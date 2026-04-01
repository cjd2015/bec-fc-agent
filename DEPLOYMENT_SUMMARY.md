# 阿里云函数计算部署总结

**日期:** 2026-03-30  
**状态:** 🟡 准备就绪，等待手动部署

---

## ✅ 已完成准备

### 1. 代码准备
- ✅ 函数代码（fc-code/）
- ✅ FastAPI 应用（fc-code/main.py）
- ✅ 入口函数（fc-code/index.py）
- ✅ 依赖配置（requirements-fc.txt）

### 2. 配置文件
- ✅ Serverless Devs 配置（fc-config/s.yaml）
- ✅ 部署脚本（scripts/deploy-fc-simple.sh）
- ✅ 环境变量配置

### 3. 环境变量
- ✅ ALIYUN_ACCESS_KEY_ID
- ✅ ALIYUN_ACCESS_KEY_SECRET
- ✅ ALIYUN_USER_ID (AccountID)

### 4. 工具安装
- ✅ 阿里云 CLI
- ✅ Serverless Devs
- ✅ Python 阿里云 SDK

---

## 🚀 部署方法

### 方法 1：使用部署脚本（推荐）

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
./scripts/deploy-fc-simple.sh
```

### 方法 2：使用 Serverless Devs

```bash
cd fc-config
s deploy -y
```

### 方法 3：使用阿里云控制台（备用）

1. 访问 https://fcnext.console.aliyun.com
2. 创建服务：ai-agent-service
3. 创建函数：agent-api
4. 上传 fc-code/ 目录
5. 配置 HTTP 触发器

---

## 🌐 访问地址

**部署成功后访问：**
```
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/docs
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/api/v1/agent
https://ai-agent-service.cn-hangzhou.fc.aliyuncs.com/health
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

## ⚠️ 当前状态

**自动化部署遇到网络/权限问题，建议：**

1. **检查网络连接**
   ```bash
   ping fc.cn-hangzhou.aliyuncs.com
   curl -I https://fc.cn-hangzhou.aliyuncs.com
   ```

2. **验证阿里云凭证**
   ```bash
   aliyun sts GetCallerIdentity
   ```

3. **使用控制台手动部署**（如自动化失败）

---

## 📝 手动部署步骤

### 1. 打包代码

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform/fc-code
zip -r ../fc-code.zip ./*
```

### 2. 创建服务

访问：https://fcnext.console.aliyun.com

- 服务名称：ai-agent-service
- 地域：华东 1（杭州）
- 日志配置：创建新的 Logstore

### 3. 创建函数

- 函数名称：agent-api
- 运行环境：Custom Runtime
- 内存：1024MB
- 超时：60 秒
- 启动命令：`python3 -m uvicorn main:app --host 0.0.0.0 --port 8080`
- 代码上传：上传 fc-code.zip

### 4. 配置触发器

- 触发器类型：HTTP
- 认证方式：anonymous
- 方法：GET/POST/PUT/DELETE/PATCH

---

## 💰 成本估算

**免费额度：**
- 100 万调用/月
- 400,000 CU-秒/月
- 100 GB 流量/月

**预期成本：**
- 初期：¥0/月
- 中期：¥0-100/月
- 后期：¥100-500/月

---

## 📞 获取帮助

如部署遇到问题，请提供：
1. 错误日志（/tmp/fc-deploy-final.log）
2. 阿里云 CLI 版本（aliyun version）
3. Serverless Devs 版本（s -v）
4. 网络测试结果（ping/curl）

---

**下一步：** 执行 `./scripts/deploy-fc-simple.sh` 或使用阿里云控制台手动部署
