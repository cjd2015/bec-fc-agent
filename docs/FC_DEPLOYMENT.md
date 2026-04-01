# 阿里云函数计算部署文档

**版本:** 1.0  
**更新日期:** 2026-03-30  
**环境:** 阿里云函数计算 FC 3.0

---

## 1️⃣ 前置准备

### 1.1 环境变量

确保已设置以下环境变量：

```bash
export ALIYUN_ACCESS_KEY_ID="your_access_key_id"
export ALIYUN_ACCESS_KEY_SECRET="your_access_key_secret"
```

### 1.2 安装工具

```bash
# 安装阿里云 CLI
curl -o aliyun https://aliyuncli.oss-cn-hangzhou.aliyuncs.com/aliyun
chmod +x aliyun
sudo mv aliyun /usr/local/bin/

# 安装 Serverless Devs
npm install -g @serverless-devs/s

# 验证安装
aliyun version
s -v
```

---

## 2️⃣ 部署步骤

### 2.1 一键部署（推荐）

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
./scripts/deploy-fc.sh
```

### 2.2 手动部署

```bash
# 1. 配置阿里云 CLI
aliyun configure set \
    --profile aliyun \
    --mode AK \
    --access-key-id $ALIYUN_ACCESS_KEY_ID \
    --access-key-secret $ALIYUN_ACCESS_KEY_SECRET \
    --region cn-hangzhou

# 2. 准备代码
cd fc-code
pip install -r requirements.txt -t ./

# 3. 部署函数
cd ../fc-config
s deploy -y
```

---

## 3️⃣ 访问地址

| 服务 | 地址 |
|------|------|
| **API 根路径** | https://ai-agent.fc.aliyuncs.com |
| **API 文档** | https://ai-agent.fc.aliyuncs.com/docs |
| **Agent API** | https://ai-agent.fc.aliyuncs.com/api/v1/agent |
| **健康检查** | https://ai-agent.fc.aliyuncs.com/health |

---

## 4️⃣ 验证部署

### 4.1 测试健康检查

```bash
curl https://ai-agent.fc.aliyuncs.com/health
```

### 4.2 测试 API

```bash
# 获取 Agent 列表
curl https://ai-agent.fc.aliyuncs.com/api/v1/agent

# 创建 Agent
curl -X POST https://ai-agent.fc.aliyuncs.com/api/v1/agent \
  -H "Content-Type: application/json" \
  -d '{"name": "测试 Agent", "model": "codex-mini-latest"}'
```

### 4.3 查看日志

```bash
# 使用 Serverless Devs
s logs --function-name agent-api

# 使用阿里云 CLI
aliyun fc invocation log get \
  --service-name ai-agent-service \
  --function-name agent-api
```

---

## 5️⃣ 配置说明

### 5.1 函数配置

| 参数 | 值 | 说明 |
|------|-----|------|
| **Runtime** | custom | 自定义运行时 |
| **Memory** | 1024 MB | 内存大小 |
| **Timeout** | 60 秒 | 超时时间 |
| **Disk** | 512 MB | 磁盘空间 |

### 5.2 环境变量

| 变量 | 说明 |
|------|------|
| `ALIYUN_ACCESS_KEY_ID` | 阿里云访问密钥 ID |
| `ALIYUN_ACCESS_KEY_SECRET` | 阿里云访问密钥 Secret |
| `DATABASE_URL` | 数据库连接 URL |
| `LOG_LEVEL` | 日志级别 |

### 5.3 触发器配置

| 参数 | 值 | 说明 |
|------|-----|------|
| **Type** | http | HTTP 触发器 |
| **AuthType** | anonymous | 公开访问（生产环境应改为 function） |
| **Methods** | GET/POST/PUT/DELETE | 支持的 HTTP 方法 |

---

## 6️⃣ 成本估算

### 6.1 免费额度

- 每月 100 万调用
- 每月 400,000 CU-秒
- 每月 100 GB 互联网流出流量

### 6.2 预期成本

| 阶段 | 调用次数 | 月成本 |
|------|----------|--------|
| **初期** | <10 万 | ¥0 |
| **中期** | 10-100 万 | ¥0-100 |
| **后期** | >100 万 | ¥100-500 |

---

## 7️⃣ 监控和告警

### 7.1 云监控配置

```bash
# 创建 CPU 使用率告警
aliyun cms PutMetricRuleTemplate \
  --Name "FC CPU 告警" \
  --Rules "[{\"MetricName\":\"FunctionInstanceCPUUtilization\",\"Threshold\":80,\"ComparisonOperator\":\"GreaterThanThreshold\"}]"
```

### 7.2 日志服务配置

```bash
# 创建错误日志告警
aliyun cms PutMetricRuleTemplate \
  --Name "FC 错误告警" \
  --Rules "[{\"MetricName\":\"FunctionInstanceError\",\"Threshold\":10,\"ComparisonOperator\":\"GreaterThanThreshold\"}]"
```

---

## 8️⃣ 性能优化

### 8.1 减少冷启动

```yaml
# 使用预留模式
provisionConfig:
  target: 1  # 预留 1 个实例
```

### 8.2 优化依赖大小

```bash
# 仅安装必要依赖
pip install -r requirements.txt --no-deps

# 压缩代码
zip -r code.zip .
```

### 8.3 使用层（Layer）

```yaml
# 使用官方 Python 层
layers:
  - acs:fc:${region}:official:layers/Python310/versions/1
```

---

## 9️⃣ 故障排查

### 9.1 函数无法启动

```bash
# 查看初始化日志
s logs --function-name agent-api --tail

# 查看函数配置
s get --function-name agent-api
```

### 9.2 API 返回 502

```bash
# 检查函数日志
s logs --function-name agent-api --start-time "2026-03-30T00:00:00"

# 检查超时设置
# 增加 timeout 和 initializationTimeout
```

### 9.3 权限错误

```bash
# 检查 RAM 角色
aliyun ram GetRole --RoleName AliyunFCDefaultRole

# 创建角色（如需要）
aliyun ram CreateRole \
  --RoleName AliyunFCDefaultRole \
  --AssumeRolePolicyDocument '{"Statement":[{"Action":"sts:AssumeRole","Effect":"Allow","Principal":{"Service":["fc.aliyuncs.com"]}}],"Version":"1"}'
```

---

## 🔟 CI/CD集成

### 10.1 GitHub Actions

```yaml
name: Deploy to FC

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      
      - name: Install Serverless Devs
        run: npm install -g @serverless-devs/s
      
      - name: Deploy to FC
        env:
          ALIYUN_ACCESS_KEY_ID: ${{ secrets.ALIYUN_ACCESS_KEY_ID }}
          ALIYUN_ACCESS_KEY_SECRET: ${{ secrets.ALIYUN_ACCESS_KEY_SECRET }}
        run: |
          cd fc-config
          s deploy -y
```

---

## 📋 部署检查清单

部署前:
- [ ] 环境变量已设置
- [ ] 阿里云 CLI 已安装
- [ ] Serverless Devs 已安装
- [ ] 代码已准备
- [ ] 依赖已安装

部署后:
- [ ] 函数状态正常
- [ ] API 可访问
- [ ] 日志正常
- [ ] 监控已配置
- [ ] 告警已配置

---

**文档版本:** 1.0  
**最后更新:** 2026-03-30  
**审核状态:** ✅ 已完成
