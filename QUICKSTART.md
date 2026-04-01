# AI Agent Platform - 快速启动指南

**域名:** datahive.site  
**状态:** 🟡 部署中

---

## 🚀 快速启动

### 1. 一键部署

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
sudo ./scripts/deploy-all.sh
```

### 2. 验证部署

```bash
./scripts/verify-https.sh
```

### 3. 访问地址

- **Web UI:** https://datahive.site
- **API 文档:** https://datahive.site/docs
- **API 接口:** https://datahive.site/api/v1/

---

## 📋 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| **SSL 证书** | ✅ 已配置 | datahive.site |
| **Nginx** | ✅ 已安装 | 配置完成 |
| **后端服务** | ⏳ 待启动 | FastAPI |
| **前端构建** | ⏳ 待构建 | React + TypeScript |

---

## 🔧 手动启动

### 后端服务

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
source venv/bin/activate
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

### 前端构建

```bash
cd frontend
npm install
npm run build
```

### Nginx 配置

```bash
sudo ./scripts/deploy-nginx.sh
```

---

## 📊 验证步骤

```bash
# 1. 后端健康检查
curl http://127.0.0.1:8000/health

# 2. HTTPS 访问
curl -I https://datahive.site

# 3. API 测试
curl https://datahive.site/api/v1/agent

# 4. 前端页面
curl https://datahive.site
```

---

## 📝 日志查看

```bash
# 后端日志
tail -f logs/backend.log

# Nginx 访问日志
tail -f /var/log/nginx/access.log

# Nginx 错误日志
tail -f /var/log/nginx/error.log
```

---

**完整文档:** [DEPLOYMENT.md](docs/DEPLOYMENT.md)
