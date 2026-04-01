# FC 部署说明

**版本:** 1.0  
**更新日期:** 2026-03-31

## 1. 部署目标
- 在阿里云函数计算 FC 上部署 Python 服务
- 当前阶段以 **FC 自定义 handler** 方式承载 BEC 平台 API
- 通过 Nginx 的 `/api/` 路径对外提供访问

> 重要：截至 2026-04-01，线上真正生效的入口不是 FastAPI router，而是 `fc-code/index.py` 的 `index.handler`。部署、修复与验证都必须以这一事实为准。

## 2. FC 承载内容
适合放在 FC：
- 用户认证接口
- 单词/句型接口
- 水平测试接口
- 场景训练接口
- 模考接口
- 内容管理接口

不建议放在 FC：
- 前端构建流程
- 数据库
- 长时间批处理任务
- 高内存常驻服务

## 3. 部署步骤建议
### 第一步：整理后端项目
当前阶段请优先围绕 FC handler 组织代码：

```bash
ai-agent-platform/
├── fc-code/
│   ├── index.py          # 当前线上真实生效入口
│   ├── requirements.txt
│   └── src/
├── signing-proxy/
├── runtime/
└── docs/
```

### 第二步：准备依赖
`requirements.txt` 至少包含：
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- psycopg2-binary 或 pymysql
- httpx

### 第三步：配置环境变量
至少包括：
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `JWT_SECRET`
- `MODEL_API_KEY`

对于当前 BEC 项目，推荐将真实 PostgreSQL 连接信息保存在本地运行时文件中，例如：
- `projects/ai-agent-platform/runtime/postgres.env`（真实值，权限建议 `600`）
- `projects/ai-agent-platform/runtime/postgres.env.example`（示例模板，不含真实密码）

推荐连接串形态：
- `postgresql+psycopg2://<user>:<urlencoded_password>@<host>:5432/<dbname>`

### 第四步：部署到 FC
通过阿里云函数控制台或工具链完成部署。

对于现代 Python / FastAPI 项目，若依赖栈要求 Python 3.10+，建议优先采用**FC 自定义容器**方案，而不是继续依赖 `custom.debian10` 这类低版本 Python 运行环境。推荐方式：
- 在代码目录中维护 `Dockerfile`
- 基础镜像使用 `python:3.10-slim` 或 `python:3.11-slim`
- 在镜像内安装 `requirements.txt`
- 容器启动命令统一为 `uvicorn main:app --host 0.0.0.0 --port 8080`

这样可以避免：
- FC 默认 Python 版本过低
- 依赖已打包但解释器版本不兼容
- `fastapi / uvicorn / pydantic 2.x` 与 Python 3.7 冲突

**安全要求：FC HTTP Trigger 不允许使用匿名访问（anonymous）。**
必须至少满足以下要求：
- `authType` 使用 `function` 或等效强制认证方式
- 不将 FC 公网 URL 作为最终对外开放 API 入口
- 对外统一通过 ECS Nginx / 受控网关暴露 `/api/`
- FC 函数访问凭证应仅保存在服务端，不进入前端代码

### 第五步：验证接口
建议先验证：
- 健康检查接口
- 登录接口
- 数据库连通性
- 未携带认证信息访问 FC 直连地址时应被拒绝

## 4. 建议增加的接口
```text
GET /api/v1/health
GET /api/v1/ping
```

## 5. 部署注意事项
- 函数超时时间不要过短
- 数据库连接池要克制
- 模型调用要有超时控制
- 错误处理统一规范
- 日志中不要打印敏感信息
- 当 FC 启用 `function` 认证后，不能继续使用普通 Nginx `proxy_pass` 直接反代 FC 公网地址
- 若需要继续保留 `datahive.top/api/` 入口，必须增加服务端签名调用层或改用更适合的阿里云网关产品
