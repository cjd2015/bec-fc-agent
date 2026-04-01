# FC 真实业务写入链路验证

**更新时间:** 2026-04-01

## 目标
验证以下完整链路是否可用：

- client
- signing-proxy
- FC Function Auth
- FC 自定义 handler (`index.handler`)
- PostgreSQL
- 业务表读写

## 关键发现

### 1. FC 实际入口不是 FastAPI 路由，而是 `fc-code/index.py`
当前 FC 部署配置 `fc-config/s.yaml` 使用：
- `handler: index.handler`

因此：
- 修改 `src/api/routes/*.py` 或 `fc-code/src/api/routes/*.py`
- **不会直接影响 FC 对外接口行为**

FC 当前真正生效的 HTTP 业务逻辑在：
- `fc-code/index.py`

这也是前一次测试中 `/auth/register` 仍返回 `skeleton-ready` 的原因。

### 2. 已在 `fc-code/index.py` 中补齐最小真实业务读写能力
本次已补齐：

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/profile?username=...`
- `PUT /api/v1/users/profile?username=...`

实现方式：
- 直接在 `index.py` 中使用 SQLAlchemy engine + SQL 文本查询
- 注册时写入 `users` 和 `user_profile`
- 登录时校验 `password_hash`
- profile 支持查询与更新

## 实测结果

### 注册
请求：
- `POST /api/v1/auth/register`

结果：
- 返回 `200`
- 成功写入用户，例如：
  - `username = fc_user_1775006297`
  - `email = fc_user_1775006297@example.com`

### 登录
请求：
- `POST /api/v1/auth/login`

结果：
- 返回 `200`
- 成功读取数据库中用户并通过密码校验

### 查询 profile
请求：
- `GET /api/v1/users/profile?username=fc_user_1775006297`

结果：
- 返回 `200`
- 初始 profile 字段均为 `null`

### 更新 profile
请求：
- `PUT /api/v1/users/profile?username=fc_user_1775006297`

写入内容：
- `target_level = BEC Higher`
- `current_level = BEC Vantage`
- `industry_background = SaaS`
- `learning_goal = close enterprise deals in English`
- `learning_preference = scenario practice`

结果：
- 返回 `200`
- 再次查询 profile 可读到更新后的值

### PostgreSQL 侧复核
容器内查询结果：
- `users` 表中已存在该用户
- `user_profile` 表中已存在对应 profile 记录

说明：
- 真实业务写入链路已经打通
- 不只是 health check 成功，而是实际 CRUD 已在 FC → PostgreSQL 上工作

## 当前结论

截至 2026-04-01：

1. `signing-proxy` → FC Function Auth 已通
2. FC → PostgreSQL 已通
3. PostgreSQL schema 已初始化
4. 最小真实业务写入链路已通（注册 / 登录 / profile 查询 / profile 更新）
5. 当前 FC 的业务主入口应以 `fc-code/index.py` 为准，而不是误以为是 FastAPI router

## 下一步建议

1. 将 `index.py` 的临时 SQL 逻辑逐步替换成真正统一的应用层实现
2. 明确长期架构：
   - 继续使用 `index.handler` 自定义路由
   - 还是切回标准 FastAPI ASGI 入口
3. 统一本地开发、FC 部署、文档配置，避免 SQLite / PostgreSQL 双轨漂移
