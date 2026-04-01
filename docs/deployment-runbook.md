# BEC 商务英语智能学习平台 - 部署执行手册

**版本:** 1.0  
**更新时间:** 2026-03-31  
**适用范围:** ECS + Nginx + 阿里云函数计算 FC + Docker PostgreSQL

---

## 1. 目标

本手册用于指导 BEC 商务英语智能学习平台 MVP 阶段的实际部署，部署结构如下：

- 前端：本地或 ECS build，部署到 ECS 上的 Nginx
- 后端 API：部署到阿里云函数计算 FC
- 数据库：部署到 ECS 的 Docker PostgreSQL
- 域名：`datahive.top`
- HTTPS：由 ECS Nginx 承担

---

## 2. 部署前准备

### 2.1 确认资源
- [ ] 阿里云 ECS 已可 SSH 登录
- [ ] 阿里云函数计算 FC 已开通并可部署
- [ ] 域名 `datahive.top` 已可操作解析
- [ ] SSL 证书已准备

### 2.2 确认本地文件
建议准备以下文件：
- `docker-compose.secure.yml`
- `postgresql.conf`
- `pg_hba.conf`
- 前端 build 产物 `dist/`
- 后端项目代码

---

## 3. ECS 目录准备

在 ECS 上创建部署目录：

```bash
mkdir -p /opt/bec-agent/postgres
mkdir -p /opt/bec-agent/nginx
mkdir -p /var/www/datahive.top
mkdir -p /etc/nginx/ssl
```

说明：
- `/opt/bec-agent/postgres`：数据库配置与数据目录
- `/var/www/datahive.top`：前端静态资源目录
- `/etc/nginx/ssl`：证书目录

---

## 4. 部署 PostgreSQL

### 4.1 上传数据库配置文件
将以下文件上传到：

```bash
/opt/bec-agent/postgres/
```

包括：
- `docker-compose.secure.yml`
- `postgresql.conf`
- `pg_hba.conf`

### 4.2 修改数据库密码
编辑 `docker-compose.secure.yml`：

```yaml
POSTGRES_PASSWORD: 改成强密码
```

### 4.3 修改 pg_hba.conf 白名单
将示例 IP 替换成可信来源 IP：
- FC 出口 IP（如可确定）
- 管理员固定 IP

默认不要对全网开放。

### 4.4 启动数据库
```bash
cd /opt/bec-agent/postgres
docker compose -f docker-compose.secure.yml up -d
```

### 4.5 检查数据库状态
```bash
docker ps
docker logs bec-postgres --tail 100
```

### 4.6 检查数据库健康状态
```bash
docker inspect bec-postgres | grep -A 20 Health
```

---

## 5. 初始化数据库结构

### 5.1 上传 schema.sql
将 `docs/schema.sql` 上传到 ECS，例如：

```bash
/opt/bec-agent/schema.sql
```

### 5.2 执行建表
```bash
docker exec -i bec-postgres psql -U bec_user -d bec_agent < /opt/bec-agent/schema.sql
```

### 5.3 验证表是否创建成功
```bash
docker exec -it bec-postgres psql -U bec_user -d bec_agent
```
进入后执行：
```sql
\dt
```

---

## 6. 配置 Nginx

### 6.1 上传 SSL 证书
将证书文件放到：

```bash
/etc/nginx/ssl/datahive.top.pem
/etc/nginx/ssl/datahive.top.key
```

### 6.2 上传前端静态资源
将前端构建产物上传到：

```bash
/var/www/datahive.top/
```

### 6.3 写入 Nginx 配置
将 `nginx.conf` 中的配置整理为实际配置文件，例如：

```bash
/etc/nginx/conf.d/datahive.top.conf
```

注意：
- SSL 证书路径需替换为真实路径
- 前端静态资源目录需替换为真实目录
- **不要再把 `/api/` 直接裸反代到 FC 公网 URL**
- 当前 FC 已启用 `function` 认证，Nginx 不能仅靠 `proxy_pass` 完成调用
- `/api/` 应转发到“受控服务端签名代理”或更合适的网关层

### 6.4 检查 Nginx 配置
```bash
nginx -t
```

### 6.5 重载 Nginx
```bash
systemctl reload nginx
```
或：
```bash
nginx -s reload
```

---

## 7. 配置域名解析

到域名服务商或阿里云 DNS 控制台：

- 将 `datahive.top` A 记录解析到 ECS 公网 IP
- 如需 `www.datahive.top`，也同步配置

完成后验证：
```bash
ping datahive.top
```

---

## 8. 部署后端到阿里云函数计算 FC

### 8.1 准备后端代码
整理后端项目，确保至少包含：
- `requirements.txt`
- `main.py`
- 应用代码目录

### 8.2 配置环境变量
至少包括：
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `JWT_SECRET`
- `MODEL_API_KEY`

### 8.3 部署 FC
通过阿里云函数控制台或部署工具完成部署。

**强制安全要求：**
- FC HTTP Trigger 不得配置为 `anonymous`
- 推荐使用 `function` 认证方式
- FC 公网 URL 仅作为受控后端调用目标，不作为面向用户的正式入口
- 对外统一由 ECS Nginx 暴露 `https://datahive.top/api/`
- 若需要调用 FC 直连地址，认证凭证必须仅保存在服务端

**重要架构说明：**
- 当 FC 使用 `function` 认证后，ECS Nginx 不能直接用裸 `proxy_pass` 转发到 FC 公网 URL
- 必须增加一层“服务端签名调用组件”负责生成认证头并调用 FC
- 推荐落地方式：
  1. 浏览器 -> `https://datahive.top/api/`
  2. ECS Nginx -> 本机签名代理服务（如 Python / Node）
  3. 签名代理服务 -> 阿里云 FC（Function Auth）

### 8.4 验证 FC 接口
优先验证：
- `/api/v1/health`
- 登录接口
- 数据库连通性
- 未认证请求访问 FC 直连地址时应返回拒绝
- 经签名代理转发后访问 FC 时应正常返回

---

## 9. 配置安全组

### 9.1 ECS 必开端口
- 80
- 443
- 22（仅限可信 IP）

### 9.2 数据库端口策略
- 不建议对全网开放 5432
- 若必须开放，只允许可信来源 IP
- 与 `pg_hba.conf` 保持一致

### 9.3 原则
- 最小暴露面
- 最小权限
- 白名单优先

---

## 10. 上线验证

### 10.1 访问验证
- [ ] `https://datahive.top` 可打开前端
- [ ] 页面刷新不 404
- [ ] `/api/` 可正常转发到 FC

### 10.2 数据库验证
- [ ] PostgreSQL 健康检查通过
- [ ] 表结构已创建
- [ ] 后端能成功连接数据库

### 10.3 业务验证
- [ ] 注册/登录正常
- [ ] 水平测试正常
- [ ] 单词学习正常
- [ ] 场景训练正常
- [ ] 模拟考试正常
- [ ] 学习记录正常入库

---

## 11. 备份与维护

### 11.1 数据库备份
建议至少每日备份一次。

示例：
```bash
docker exec bec-postgres pg_dump -U bec_user bec_agent > /opt/bec-agent/backup-$(date +%F).sql
```

### 11.2 日志检查
定期检查：
- PostgreSQL 容器日志
- Nginx 访问日志 / 错误日志
- FC 运行日志

### 11.3 磁盘空间检查
重点检查：
- Docker 数据目录
- PostgreSQL 日志目录
- 备份文件是否堆积

---

## 12. 常见问题

### 12.1 FC 无法连接数据库
排查顺序：
1. ECS 安全组
2. `pg_hba.conf`
3. 数据库端口监听
4. 数据库账号密码
5. FC 环境变量

### 12.2 页面能打开但 API 失败
排查顺序：
1. Nginx `/api/` 反向代理配置
2. FC 地址是否可访问
3. FC 接口是否正常运行
4. 后端日志是否有异常

### 12.3 Nginx HTTPS 不生效
排查顺序：
1. 证书路径
2. 证书内容
3. 443 配置是否生效
4. `nginx -t` 是否通过

---

## 13. 当前部署结论

当前 MVP 阶段部署方案推荐如下：

- 前端静态资源部署到 ECS Nginx
- Python API 部署到阿里云函数计算 FC
- PostgreSQL 部署到 ECS Docker
- `datahive.top` 统一接入 ECS，由 Nginx 提供 HTTPS 并反向代理 `/api/`

这是当前资源条件下，兼顾低成本、可执行性和后续扩展性的最优落地路径。
