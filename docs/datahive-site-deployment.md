# datahive.site 实际部署说明

**更新时间：** 2026-04-01  
**适用域名：** `datahive.site` / `www.datahive.site`

---

## 1. 当前部署结论

截至 2026-04-01，`datahive.site` 已切换到 BEC 商务英语学习平台前端，采用如下实际运行架构：

- 前端静态站：Docker Nginx
- HTTPS 域名：`datahive.site` / `www.datahive.site`
- API 入口：`/api/`
- `/api/` 转发目标：ECS 本机 `8081`
- `8081` 服务：`bec-signing-proxy.service`（systemd 常驻）
- 签名代理后端：阿里云 FC HTTP Trigger（Function Auth）
- 数据库：ECS 本机 Docker PostgreSQL（`bec-postgres`）

整体链路如下：

```text
Browser
  -> https://datahive.site
  -> Docker Nginx (80/443)
  -> /api/* reverse proxy
  -> bec-signing-proxy.service (127.0.0.1:8081 / 0.0.0.0:8081)
  -> Aliyun FC HTTP Trigger (authType=function)
  -> PostgreSQL (bec-postgres)
```

---

## 2. 前端部署来源

当前上线的前端产物来自：

- 项目目录：`projects/ai-agent-platform/frontend`
- 构建命令：

```bash
cd /root/.openclaw/workspace/projects/ai-agent-platform/frontend
npm run build
```

构建产物目录：

- `projects/ai-agent-platform/frontend/dist`

当前页面标题：

- `BEC 商务英语学习平台`

---

## 3. Docker Nginx 部署方式

### 3.1 使用镜像
由于 Docker Hub 访问超时，实际使用国内镜像源拉取：

```bash
docker pull docker.m.daocloud.io/nginx:1.27-alpine
```

### 3.2 容器名

```text
datahive-site-nginx
```

### 3.3 监听端口

- `80:80`
- `443:443`

### 3.4 挂载目录

实际部署目录：

- `/root/.openclaw/workspace/projects/ai-agent-platform/deploy/nginx-datahive-site/html`
- `/root/.openclaw/workspace/projects/ai-agent-platform/deploy/nginx-datahive-site/ssl`
- `/root/.openclaw/workspace/projects/ai-agent-platform/deploy/nginx-datahive-site/conf.d/default.conf`

其中：

- `html/`：前端构建产物
- `ssl/`：证书与私钥
- `default.conf`：Nginx 站点配置

---

## 4. 证书文件

当前部署使用证书：

- `datahive.site_bundle.pem`
- `datahive.site.key`

说明：

- 该证书适用于 `datahive.site` / `www.datahive.site`
- **不适用于 `datahive.top`**
- 若后续要切 `datahive.top`，必须重新提供 `datahive.top` 对应证书

---

## 5. Nginx 关键配置

核心逻辑如下：

### 5.1 HTTP 自动跳转 HTTPS

```nginx
server {
    listen 80;
    server_name datahive.site www.datahive.site;
    return 301 https://$host$request_uri;
}
```

### 5.2 HTTPS 静态站

```nginx
server {
    listen 443 ssl;
    server_name datahive.site www.datahive.site;

    ssl_certificate     /etc/nginx/ssl/datahive.site_bundle.pem;
    ssl_certificate_key /etc/nginx/ssl/datahive.site.key;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://172.17.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
    }
}
```

### 5.3 注意事项

`proxy_pass` 必须写成：

```nginx
proxy_pass http://172.17.0.1:8081;
```

而不是：

```nginx
proxy_pass http://172.17.0.1:8081/;
```

否则会把 `/api/` 前缀裁掉，导致 FC 返回 `route not found`。

---

## 6. signing-proxy 常驻方式

### 6.1 systemd 服务名

```text
bec-signing-proxy.service
```

### 6.2 当前状态

- enabled
- active (running)

### 6.3 systemd 服务文件位置

```text
/etc/systemd/system/bec-signing-proxy.service
```

### 6.4 服务核心配置

```ini
[Service]
WorkingDirectory=/root/.openclaw/workspace/projects/ai-agent-platform/signing-proxy
ExecStart=/root/.openclaw/workspace/projects/ai-agent-platform/signing-proxy/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8081
Restart=always
RestartSec=3
User=root
```

这意味着：

- 机器重启后，`signing-proxy` 会自动恢复
- 不再依赖手工 `nohup` 启动

---

## 7. 实际验收结果

### 7.1 静态首页验收
已验证：

- `https://127.0.0.1` 返回前端首页 HTML
- `<title>BEC 商务英语学习平台</title>`

### 7.2 API 验收
已验证：

```bash
curl -k https://127.0.0.1/api/v1/health
```

返回：

- `code = 0`
- `status = ok`

还额外验证了：

```bash
curl -k 'https://127.0.0.1/api/v1/learning/summary?username=fc_user_1775006297'
```

返回成功，说明：

- Nginx `/api/` 反代正常
- signing-proxy 正常
- FC 正常
- PostgreSQL 正常

---

## 8. 当前线上能力范围

通过 `datahive.site` 当前已经可访问到的 BEC 平台核心能力包括：

- 学习进度看板
- 词汇与句型列表
- 场景训练页面
- `/api/v1/health`
- `/api/v1/learning/summary`
- 以及已实现的其它 FC 接口

---

## 9. 后续建议

### 9.1 建议保留的操作
- 前端每次改动后执行 `npm run build`
- 将最新 `dist/` 同步到 Nginx 静态目录
- 若更换证书，更新 `ssl/` 挂载目录中的文件

### 9.2 需要注意的风险
- 当前部署域名是 `datahive.site`，并非 `datahive.top`
- 若以后切换域名，证书必须同步切换
- 若 Docker 容器被误删，需要重新运行 `datahive-site-nginx`
- 若 `bec-signing-proxy.service` 被停掉，前端页面可打开，但 `/api/` 会失败

### 9.3 后续优化建议
- 将 Docker Nginx 启动命令整理为脚本或 `docker-compose.yml`
- 将部署目录与证书目录纳入正式运维文档
- 后续可补充自动化发布脚本（前端 build + Nginx reload / container update）

---

## 10. 最终结论

截至 2026-04-01：

- `datahive.site` 已切换到 BEC 商务英语学习平台前端
- Docker Nginx 已作为主站入口运行
- `/api/` 已通过 signing-proxy 接到 FC
- signing-proxy 已通过 systemd 常驻化
- 当前部署已经具备基本稳定性，可用于继续联调和后续迭代
