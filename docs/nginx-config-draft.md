# Nginx 配置草案

**版本:** 1.0  
**更新日期:** 2026-03-31

## 1. 部署目标
- `https://datahive.top/` 提供前端静态资源
- `https://datahive.top/api/` 反向代理到阿里云函数计算 FC
- 启用 HTTPS
- 80 自动跳转 443
- 支持 React SPA 路由刷新

## 2. 目录约定
前端静态文件目录示例：
```bash
/var/www/datahive.top/
```

证书目录示例：
```bash
/etc/nginx/ssl/datahive.top.pem
/etc/nginx/ssl/datahive.top.key
```

## 3. Nginx 配置示例
```nginx
server {
    listen 80;
    server_name datahive.top www.datahive.top;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name datahive.top www.datahive.top;

    ssl_certificate     /etc/nginx/ssl/datahive.top.pem;
    ssl_certificate_key /etc/nginx/ssl/datahive.top.key;

    ssl_session_timeout 10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    root /var/www/datahive.top;
    index index.html;

    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass https://你的-fc-访问地址/;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff2?)$ {
        expires 7d;
        access_log off;
    }
}
```

## 4. 注意事项
- `proxy_pass` 替换为实际 FC 公网地址
- React 路由必须保留 `try_files ... /index.html`
- 后续可视情况增加 gzip、缓存与更严格安全头
