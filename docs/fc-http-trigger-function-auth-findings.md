# FC HTTP Trigger + Function Auth 排查结论

**版本:** 1.2  
**更新时间:** 2026-04-01

---

## 1. 背景

当前 BEC 平台已将阿里云函数计算 FC HTTP Trigger 从 `anonymous` 调整为 `function` 认证，以满足安全要求，避免 FC 直连公网地址被匿名访问。

为适配该模式，已在 ECS 侧设计并实现 Python 签名代理服务，尝试通过服务端签名方式访问 FC。

---

## 2. 当前已确认事实

### 2.1 FC 部署成功
已成功部署：
- functionName: `bec-agent-api`
- region: `cn-hangzhou`
- runtime: `custom.debian10`
- trigger authType: `function`

### 2.2 未认证直连已被拒绝
直接访问 FC 直连地址时，未提供认证头会被拒绝，说明：
- `function` 认证已生效
- FC 不再处于匿名开放状态

### 2.3 Python signing-proxy 已成功启动
本地已验证：
- `GET /health` 正常
- 代理转发链路可工作
- `.env` 中真实 AK/SK 已成功加载

### 2.4 AK/SK 不一致问题已修复
此前出现过：
- 使用占位值 `replace_me`
- 使用不匹配的 AK/SK 对

当前该问题已排除。

---

## 3. 官方文档新增确认结论

用户提供的官方文档：
- `https://help.aliyun.com/zh/functioncompute/fc/user-guide/configure-signature-authentication-for-http-triggers`

官方文档明确说明：

### 3.1 HTTP Trigger 的签名认证遵循阿里云 SDK 的签名机制
官方说明：
- 通过阿里云 SDK 生成签名字符串
- 将签名字符串设置到 HTTP 请求的 `Authorization` Header 中
- 使用任意 HTTP 客户端发起请求

### 3.2 Python 官方示例使用的不是 `aliyun-fc2`
而是：
- `alibabacloud-openapi-util`
- `Tea.request.TeaRequest`

### 3.3 官方示例的关键 Header 是
- `x-acs-date`
- `x-acs-security-token`（STS 时可选）
- `authorization`

### 3.4 官方示例采用的签名算法是
- `ACS3-HMAC-SHA256`

### 3.5 官方示例签名输入结构包含
- `method`
- `pathname`
- `headers`
- `query`

并通过：
- `util.get_authorization(...)`

生成签名。

---

## 4. 当前排查过但仍失败的方案

### 4.1 手写旧版 FC 风格签名方案
已尝试：
- `Date`
- `Content-MD5`
- `Content-Type`
- 路径与 query 拼接
- HMAC-SHA256
- `Authorization: FC <AK>:<signature>`

结果：
- FC 返回 `invalid authorization`

### 4.2 更接近旧 FC 规则的手写版本
已进一步尝试：
- 加入 canonicalized query
- canonicalized `x-fc-*` headers
- `x-fc-date`

结果：
- 仍返回 `invalid authorization`

### 4.3 使用 `aliyun-fc2` SDK 内置 Auth
已尝试：
- 安装 `aliyun-fc2`
- 使用 SDK 中 `fc2.auth.Auth.sign_request(...)`

结果：
- 仍返回 `invalid authorization`

---

## 5. 当前最新结论

截至当前，问题已经可以排除为：
- AK/SK 未加载
- AK/SK 不一致
- proxy 未启动
- 代理链路不通
- FC 未启用认证
- 简单手写签名遗漏

结合官方文档，当前更明确的结论是：

> HTTP Trigger 的签名认证应按照阿里云 OpenAPI / ACS3 风格签名来做，而不是继续沿用旧 `FC <AK>:<signature>` 风格或 `aliyun-fc2` 的旧 Auth 规则。

也就是说：
- `aliyun-fc2` 更像旧 FC SDK / 控制面接口风格
- 当前 HTTP Trigger + Function Auth 的官方推荐方式，是使用：
  - `alibabacloud-openapi-util`
  - `TeaRequest`
  - `ACS3-HMAC-SHA256`
  - `x-acs-date`
  - `authorization`

---

## 6. 当前最可能的问题层

当前问题已收敛到：
- 代理服务尚未切换到官方文档给出的 `ACS3-HMAC-SHA256` 签名方式
- 当前使用的仍然是旧 FC SDK 风格签名，和 HTTP Trigger 官方样例不一致

---

## 7. 推荐下一步

建议按以下顺序继续推进：

### 7.1 改造 signing-proxy
将当前 Python 签名代理改为官方文档示例风格：
- 安装 `alibabacloud-openapi-util`
- 安装 `Tea`
- 使用 `TeaRequest`
- 使用 `util.get_authorization(...)`
- Header 切换为 `x-acs-date` / `authorization`

### 7.2 重新联调
验证：
- `GET http://127.0.0.1:9000/api/v1/health`
- 若仍失败，再判断是否需要额外处理 STS token / query / path 编码

---

## 8. 2026-04-01 补充验证（本次复盘新增）

### 8.1 上次关键结论并没有失效
本次复盘重新核对后确认：
- 旧结论仍成立，HTTP Trigger + Function Auth 的正确方向仍然是 **ACS3-HMAC-SHA256**
- `signing-proxy/app/main.py` 当前代码已经切换到：
  - `alibabacloud-openapi-util`
  - `Tea.request.TeaRequest`
  - `OpenApiUtilClient.get_authorization(...)`
  - `x-acs-date`
  - `authorization`
- `signing-proxy/requirements.txt` 也已经包含：
  - `alibabacloud-openapi-util==0.2.4`
  - `Tea==0.1.7`

这说明：
- “继续使用旧 FC 风格签名”这个历史问题，代码层面已经修过
- 本次若再次从旧签名思路重试，属于重复排查

### 8.2 本次实测新增事实
2026-04-01 早晨再次实测得到：

#### 8.2.1 本地 signing-proxy 未常驻
直接访问本地代理：
- `http://127.0.0.1:8081/api/v1/health`
最初返回：
- `Connection refused`

说明本次首先不是签名错误，而是：
- 本地 signing-proxy 进程当时并没有在运行

#### 8.2.2 FC 公网地址可达，网络放行已基本生效
在重新启动本地服务后，实测：
- 本地 `curl http://127.0.0.1:8081/api/v1/health` 返回 `200`
- 直连 FC：
  - `GET https://bec-agent-api-yelolrsptv.cn-hangzhou.fcapp.run/api/v1/health`
  - 返回 `400 MissingRequiredHeader`
  - 提示：`required HTTP header Date was not specified`

这说明：
- 请求已经能到达 FC
- 当前不是简单的“ECS 安全组未放行 / 网络完全不通”
- FC 鉴权仍然在拦截未签名请求

### 8.3 当前最需要避免的误区
后续排查时，应避免再次把问题重新归零成：
- 安全组没放行
- AK/SK 没配置
- 旧签名方案还没切 ACS3

因为这些点都已经有过明确验证或已有代码落地。

### 8.4 当前真正需要继续确认的点
后续应优先检查以下问题，而不是重新从头实验：
- `signing-proxy` 是否已在 ECS 上稳定常驻运行
- 业务侧实际请求是否走了 `signing-proxy`，而不是绕过代理直连 FC
- 若走了代理但仍失败，需进一步确认：
  - 当前 ACS3 签名请求头是否仍缺少 FC 要求的 `Date` 头
  - FC HTTP Trigger 在当前模式下是否同时接受/要求 `Date` 与 `x-acs-date`
  - 请求 path/query/header canonicalization 是否与 FC 侧完全一致
- 若签名完全正确但仍被拒绝，则继续核对：
  - RAM 用户是否具备 `fc:InvokeFunction`
  - 是否存在 STS token / 区域 / trigger 路径级别差异

## 9. 2026-04-01 进一步验证：FC 与 PostgreSQL 已打通

### 9.1 鉴权链路已恢复正常
本次继续实测确认：
- `GET http://127.0.0.1:8081/api/v1/health` 已返回 `200`

说明：
- 本地 `signing-proxy` → FC Function Auth 这条链路已经可用
- 之前的鉴权阻塞已不再是当前主问题

### 9.2 FC 到数据库最小健康检查已通过
实测：
- `GET http://127.0.0.1:8081/api/v1/db/health` 返回 `200`
- 返回字段确认：
  - `database = postgresql`
  - `database_name = bec_agent`
  - `database_user = bec_app`
  - `schema = public`
  - `host = 8.147.56.124`

说明：
- FC 已可通过环境变量中的 `DATABASE_URL` 连接 PostgreSQL
- “FC 与数据库未打通”这一层已被验证通过

### 9.3 发现的真正业务问题：数据库表未初始化
继续检查发现：
- PostgreSQL 中最初不存在 `users` 表
- 即：连通性虽然没问题，但业务 schema 尚未完成初始化

### 9.4 已执行的修复动作
本次已完成：
1. 扩展 `fc-code/index.py` 的 `/api/v1/db/health` 返回信息，增加：
   - `database_name`
   - `database_user`
   - `schema`
   - `users_table_exists`
   - `users_count`
2. 重新部署 FC
3. 将 `docs/schema.sql` 导入 PostgreSQL
4. 再次实测 `/api/v1/db/health`

最终返回：
- `users_table_exists = true`
- `users_count = 0`

这说明：
- FC ↔ PostgreSQL 网络与认证已通
- PostgreSQL 业务 schema 已初始化成功
- 至少以 `users` 表为代表的核心业务表，FC 已可以看到

## 10. 当前阶段结论

当前系统已经完成以下关键链路打通：
- `signing-proxy` → FC Function Auth：已通
- FC → PostgreSQL：已通
- PostgreSQL schema 初始化：已完成

当前后续重点不再是“连不连得上”，而是：
- 统一本地开发 / FC 部署 / 文档中的数据库配置，避免 SQLite 与 PostgreSQL 分叉
- 开始验证真实业务接口是否已基于 PostgreSQL 正常读写

## 9. 当前阶段结论

当前系统安全目标已达成一半：
- FC 已不再匿名开放
- 外部不得直接无认证访问 FC

并且已经从官方文档与现有代码共同确认：
- HTTP Trigger + Function Auth 的正确方向是 **ACS3-HMAC-SHA256** 官方 SDK 签名方式
- `signing-proxy` 代码层面已经切到了该方向
- 本次新增暴露的问题首先是：**代理进程未常驻 / 调用链可能没有稳定走代理**
- 当前下一步不应再从旧分析重做，而应在现有文档基础上继续验证“代理是否稳定在线、业务请求是否真的经过代理、ACS3 头部是否还差 FC 所需字段”
