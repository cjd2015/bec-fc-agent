# Nginx 部署配置文档

**域名:** datahive.site  
**版本:** 1.0  
**更新日期:** 2026-03-30

---

## 1️⃣ 配置文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| **主配置** | `config/nginx/nginx.conf` | Nginx 主配置 |
| **站点配置** | `config/nginx/sites-available/datahive.site` | datahive.site 站点配置 |
| **部署脚本** | `scripts/deploy-nginx.sh` | 自动化部署脚本 |

---

## 2️⃣ 核心功能

### 2.1 HTTPS 配置

```nginx
# SSL 证书
ssl_certificate /root/.openclaw/workspace/certs/datahive.site/fullchain.pem;
ssl_certificate_key /root/.openclaw/workspace/certs/datahive.site/privkey.pem;

# TLS 协议
ssl_protocols TLSv1.2 TLSv1.3;

# 加密套件
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...;
```

### 2.2 HTTP → HTTPS 重定向

```nginx
server {
    listen 80;
    server_name datahive.site www.datahive.site;
    return 301 https://$server_name$request_uri;
}
```

### 2.3 安全头配置

| 头 | 值 | 说明 |
|------|------|------|
| **HSTS** | `max-age=63072000` | 强制 HTTPS（2 年） |
| **X-Frame-Options** | `DENY` | 禁止 iframe 嵌入 |
| **X-Content-Type-Options** | `nosniff` | 防止 MIME 嗅探 |
| **X-XSS-Protection** | `1; mode=block` | XSS 防护 |
| **Referrer-Policy** | `strict-origin-when-cross-origin` | Referrer 策略 |
| **CSP** | `default-src 'self'; ...` | 内容安全策略 |

### 2.4 API 代理

```nginx
location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
    # WebSocket 支持
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### 2.5 限流配置

```nginx
# 定义限流区域
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

# API 限流
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
}

# 登录限流（更严格）
location /api/v1/auth/login {
    limit_req zone=login_limit burst=3 nodelay;
}
```

### 2.6 静态资源缓存

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

### 2.7 前端路由支持（SPA）

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

---

## 3️⃣ 部署步骤

### 3.1 自动部署（推荐）

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform
sudo ./scripts/deploy-nginx.sh
```

### 3.2 手动部署

```bash
# 1. 复制配置文件
sudo cp config/nginx/sites-available/datahive.site \
  /etc/nginx/sites-available/datahive.site

# 2. 创建符号链接
sudo ln -s /etc/nginx/sites-available/datahive.site \
  /etc/nginx/sites-enabled/datahive.site

# 3. 删除默认站点
sudo rm -f /etc/nginx/sites-enabled/default

# 4. 测试配置
sudo nginx -t

# 5. 重启 Nginx
sudo systemctl restart nginx

# 6. 设置开机自启
sudo systemctl enable nginx
```

---

## 4️⃣ 验证步骤

### 4.1 检查 Nginx 状态

```bash
systemctl status nginx
```

### 4.2 测试 HTTP 跳转

```bash
curl -I http://datahive.site
# 应该返回 301 跳转到 HTTPS
```

### 4.3 测试 HTTPS

```bash
curl -I https://datahive.site
# 应该返回 200 OK
```

### 4.4 测试 API 代理

```bash
curl -I https://datahive.site/api/v1/agent
# 应该返回后端 API 响应
```

### 4.5 测试 WebSocket

```bash
# 使用 wscat 或其他 WebSocket 客户端
wscat -c wss://datahive.site/api/v1/chat
```

### 4.6 查看日志

```bash
# 访问日志
tail -f /var/log/nginx/access.log

# 错误日志
tail -f /var/log/nginx/error.log
```

---

## 5️⃣ 防火墙配置

### UFW（Ubuntu）

```bash
# 允许 Nginx
sudo ufw allow 'Nginx Full'

# 允许 SSH（如需要）
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

## 6️⃣ 性能优化

### 6.1 Gzip 压缩

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript 
             application/json application/javascript 
             application/xml+rss application/atom+xml 
             image/svg+xml;
```

### 6.2 连接优化

```nginx
keepalive_timeout 65;
tcp_nopush on;
tcp_nodelay on;
```

### 6.3 缓冲配置

```nginx
# API 代理缓冲
proxy_buffering off;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
```

---

## 7️⃣ 监控和日志

### 7.1 日志配置

```nginx
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                '$status $body_bytes_sent "$http_referer" '
                '"$http_user_agent" "$http_x_forwarded_for"';

access_log /var/log/nginx/access.log main;
error_log /var/log/nginx/error.log warn;
```

### 7.2 日志分析

```bash
# 查看访问最多的 IP
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# 查看 404 错误
grep " 404 " /var/log/nginx/access.log

# 查看慢请求
grep -E "([1-9]|[1-9][0-9])s" /var/log/nginx/error.log
```

---

## 8️⃣ 故障排查

### 8.1 Nginx 无法启动

```bash
# 检查配置
sudo nginx -t

# 查看错误日志
sudo journalctl -u nginx -f
```

### 8.2 HTTPS 不工作

```bash
# 检查证书文件
ls -la /root/.openclaw/workspace/certs/datahive.site/

# 检查证书权限
chmod 600 /root/.openclaw/workspace/certs/datahive.site/privkey.pem
chmod 644 /root/.openclaw/workspace/certs/datahive.site/fullchain.pem

# 测试证书
openssl x509 -in /root/.openclaw/workspace/certs/datahive.site/fullchain.pem -noout -dates
```

### 8.3 API 代理失败

```bash
# 检查后端服务
curl http://127.0.0.1:8000/health

# 检查 Nginx 日志
tail -f /var/log/nginx/error.log | grep api
```

### 8.4 WebSocket 连接失败

```bash
# 检查 Upgrade 头配置
grep -A5 "Upgrade" /etc/nginx/sites-enabled/datahive.site

# 测试 WebSocket
wscat -c wss://datahive.site/api/v1/chat
```

---

## 9️⃣ 证书续期

### Let's Encrypt Certbot

```bash
# 安装
sudo apt install certbot python3-certbot-nginx

# 续期
sudo certbot renew --nginx

# 测试续期
sudo certbot renew --dry-run

# 自动续期（Cron）
sudo crontab -e
# 每天凌晨 2 点检查续期
0 2 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

---

## 🔟 安全加固

### 10.1 隐藏 Nginx 版本

```nginx
http {
    server_tokens off;
}
```

### 10.2 限制请求大小

```nginx
client_max_body_size 10M;
client_body_buffer_size 128k;
```

### 10.3 禁止访问敏感文件

```nginx
location ~ /\. {
    deny all;
}

location ~* \.(key|pem|crt|csr|bak|config|sql|fla|psd|ini|log|sh|inc|swp|dist)$ {
    deny all;
}
```

---

## 📋 检查清单

部署前检查:

- [ ] Nginx 已安装
- [ ] SSL 证书文件存在
- [ ] 证书权限正确（privkey.pem 600）
- [ ] 配置文件语法正确
- [ ] 后端服务运行正常
- [ ] 防火墙规则配置
- [ ] DNS 解析正确

部署后验证:

- [ ] HTTP → HTTPS 跳转正常
- [ ] HTTPS 访问正常
- [ ] API 代理正常
- [ ] WebSocket 连接正常
- [ ] 静态资源缓存正常
- [ ] 限流配置生效
- [ ] 日志记录正常

---

**文档版本:** 1.0  
**最后更新:** 2026-03-30  
**审核状态:** ✅ 已完成
