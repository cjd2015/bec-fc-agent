# AI Agent Platform - 部署文档

**域名:** datahive.site  
**版本:** 1.0  
**更新日期:** 2026-03-30

---

## 1️⃣ 快速部署

### 一键部署（推荐）

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
sudo ./scripts/deploy-all.sh
```

此脚本会自动：
1. 构建前端静态文件
2. 启动后端服务（FastAPI）
3. 配置 Nginx
4. 验证部署

---

## 2️⃣ 手动部署

### 2.1 前端构建

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 输出目录
ls -la dist/
```

### 2.2 后端启动

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform

# 创建虚拟环境（首次）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
uvicorn src.api.main:app --host 127.0.0.1 --port 8000

# 后台运行（生产环境）
nohup uvicorn src.api.main:app --host 127.0.0.1 --port 8000 > logs/backend.log 2>&1 &
```

### 2.3 Nginx 配置

```bash
# 复制配置文件
sudo cp config/nginx/sites-available/datahive.site \
  /etc/nginx/sites-available/datahive.site

# 创建符号链接
sudo ln -s /etc/nginx/sites-available/datahive.site \
  /etc/nginx/sites-enabled/datahive.site

# 删除默认站点
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 设置开机自启
sudo systemctl enable nginx
```

---

## 3️⃣ 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端页面** | https://datahive.site | Web UI |
| **API 文档** | https://datahive.site/docs | Swagger UI |
| **API 接口** | https://datahive.site/api/v1/* | REST API |
| **健康检查** | https://datahive.site/health | 健康检查 |

---

## 4️⃣ 验证步骤

### 4.1 检查服务状态

```bash
# 后端服务
ps aux | grep uvicorn

# Nginx
systemctl status nginx
```

### 4.2 测试访问

```bash
# 后端健康检查
curl http://127.0.0.1:8000/health

# HTTPS 访问
curl -I https://datahive.site

# API 测试
curl -k https://datahive.site/api/v1/agent

# 前端页面
curl -k https://datahive.site
```

### 4.3 查看日志

```bash
# 后端日志
tail -f logs/backend.log

# Nginx 访问日志
tail -f /var/log/nginx/access.log

# Nginx 错误日志
tail -f /var/log/nginx/error.log
```

---

## 5️⃣ 配置文件

### 5.1 环境变量

创建 `config/.env` 文件：

```bash
# API Keys
QWEN_API_KEY=sk-your_api_key
DEEPSEEK_API_KEY=sk-your_api_key
KIMI_API_KEY=sk-your_api_key

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/agent.db

# 向量库
CHROMA_PERSIST_DIR=./data/chroma

# 应用配置
APP_ENV=production
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key
```

### 5.2 Nginx 配置

**位置:** `/etc/nginx/sites-available/datahive.site`

**关键配置:**
```nginx
# SSL 证书
ssl_certificate /root/.openclaw/workspace/certs/datahive.site/fullchain.pem;
ssl_certificate_key /root/.openclaw/workspace/certs/datahive.site/privkey.pem;

# 前端静态文件
root /root/.openclaw/workspace/projects/ai-agent-platform/frontend/dist;

# API 代理
location /api {
    proxy_pass http://127.0.0.1:8000;
}
```

---

## 6️⃣ 防火墙配置

### UFW（Ubuntu）

```bash
# 允许 HTTP 和 HTTPS
sudo ufw allow 'Nginx Full'

# 允许 SSH
sudo ufw allow OpenSSH

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### Firewalld（CentOS/RHEL）

```bash
# 允许 HTTP 和 HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# 重载配置
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-all
```

---

## 7️⃣ 监控和维护

### 7.1 服务监控

```bash
# 后端服务状态
systemctl status agent-platform  # 如配置了 systemd 服务

# Nginx 状态
systemctl status nginx

# 查看进程
ps aux | grep -E "nginx|uvicorn"
```

### 7.2 日志轮转

```bash
# 配置日志轮转
sudo vim /etc/logrotate.d/ai-agent-platform

# 内容：
/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && nginx -s reload
    endscript
}
```

### 7.3 自动备份

```bash
# 创建备份脚本
cat > /root/backup-agent.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/agent-platform/$DATE"
mkdir -p "$BACKUP_DIR"

# 备份数据
cp -r /root/.openclaw/workspace/projects/ai-agent-platform/data "$BACKUP_DIR/"

# 备份配置
cp -r /root/.openclaw/workspace/projects/ai-agent-platform/config "$BACKUP_DIR/"

# 备份证书
cp -r /root/.openclaw/workspace/certs "$BACKUP_DIR/"

# 删除 7 天前的备份
find /backup/agent-platform -type d -mtime +7 -delete

echo "备份完成：$BACKUP_DIR"
EOF

chmod +x /root/backup-agent.sh

# 添加到 crontab（每天凌晨 3 点）
sudo crontab -e
0 3 * * * /root/backup-agent.sh
```

---

## 8️⃣ 故障排查

### 8.1 前端无法访问

```bash
# 检查前端文件
ls -la /root/.openclaw/workspace/projects/ai-agent-platform/frontend/dist/

# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log
```

### 8.2 API 无法访问

```bash
# 检查后端服务
curl http://127.0.0.1:8000/health

# 检查后端日志
tail -f logs/backend.log

# 检查 Nginx 代理配置
grep -A10 "location /api" /etc/nginx/sites-enabled/datahive.site
```

### 8.3 HTTPS 不工作

```bash
# 检查证书文件
ls -la /root/.openclaw/workspace/certs/datahive.site/

# 检查证书权限
chmod 600 /root/.openclaw/workspace/certs/datahive.site/privkey.pem

# 测试证书
openssl x509 -in /root/.openclaw/workspace/certs/datahive.site/fullchain.pem -noout -dates

# 查看 Nginx SSL 配置
grep -A5 "ssl_" /etc/nginx/sites-enabled/datahive.site
```

---

## 9️⃣ 性能优化

### 9.1 Gzip 压缩

已在 Nginx 配置中启用：
```nginx
gzip on;
gzip_vary on;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript 
             application/json application/javascript;
```

### 9.2 静态资源缓存

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 9.3 数据库优化

```bash
# SQLite 优化（已配置）
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
```

---

## 🔟 安全加固

### 10.1 防火墙

```bash
# 仅开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 10.2 文件权限

```bash
# 项目文件
chmod -R 755 /root/.openclaw/workspace/projects/ai-agent-platform

# 私钥文件
chmod 600 /root/.openclaw/workspace/certs/datahive.site/privkey.pem

# 数据库文件
chmod 600 /root/.openclaw/workspace/projects/ai-agent-platform/data/*.db
```

### 10.3 定期更新

```bash
# 系统更新
sudo apt update && sudo apt upgrade -y

# Python 依赖更新
cd /root/.openclaw/workspace/projects/ai-agent-platform
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Node 依赖更新
cd frontend
npm update
```

---

## 📋 部署检查清单

部署前:
- [ ] 域名 DNS 解析正确
- [ ] SSL 证书文件存在
- [ ] 服务器资源充足（2C2G40G）
- [ ] 防火墙规则配置
- [ ] 环境变量配置

部署后:
- [ ] 前端页面可访问
- [ ] API 文档可访问
- [ ] API 接口正常
- [ ] HTTPS 强制跳转
- [ ] 安全头配置
- [ ] 日志记录正常
- [ ] 监控告警配置

---

**文档版本:** 1.0  
**最后更新:** 2026-03-30  
**审核状态:** ✅ 已完成
