# BEC 商务英语智能学习平台 - 部署策略与架构收敛决策

**版本:** 1.0  
**更新日期:** 2026-04-01

---

## 1. 文档目的

本文档用于明确 BEC 平台当前阶段的部署策略、FC 对外入口方案、数据库连接策略，以及本次已经做出的架构收敛决策，避免后续继续在“FastAPI 路由入口”和“FC 自定义 handler 入口”之间反复摇摆。

---

## 2. 当前已确认的部署现实

截至 2026-04-01，线上实际生效链路为：

- 客户端
- ECS 上的 signing-proxy
- 阿里云 FC HTTP Trigger（`authType=function`）
- FC 函数入口：`fc-code/index.py` 的 `index.handler`
- ECS 上的 PostgreSQL（Docker）

已实测打通：
- `signing-proxy -> FC Function Auth`
- `FC -> PostgreSQL`
- PostgreSQL schema 初始化
- 真实业务写入链路（注册 / 登录 / profile 查询 / profile 更新）

---

## 3. 关键事实：当前真正生效的 API 入口

当前 FC 部署配置 `fc-config/s.yaml` 使用：

- `handler: index.handler`

这意味着：

### 3.1 真正生效的入口是
- `projects/ai-agent-platform/fc-code/index.py`

### 3.2 当前不会直接生效的入口是
- `src/api/routes/*.py`
- `fc-code/src/api/routes/*.py`
- `main.py -> FastAPI app`

也就是说，过去一段时间里如果修改的是 FastAPI router，而不是 `index.py`，那么：
- 代码可能改了
- 本地看起来合理
- 但 FC 对外行为不会变

这正是此前“改了接口代码，但线上仍返回 skeleton-ready”的根因。

---

## 4. 本次架构决策

### 决策：**只保留 FC handler 方案，不再继续把 FastAPI 路由作为当前线上主入口。**

具体含义：

1. 当前阶段以 `fc-code/index.py` 为唯一真实生效入口
2. 新增或修复线上接口时，必须先确认是否落在 `index.handler` 路径下
3. 不再把“继续恢复成 FastAPI 主入口”作为当前阶段默认目标
4. 若未来要切回标准 ASGI / FastAPI 入口，必须作为**单独架构升级项目**处理，而不是在日常修 bug 时顺手混改

---

## 5. 为什么做这个决策

### 5.1 避免双轨代码长期误导
当前仓库里同时存在：
- FastAPI router 代码
- FC 自定义 handler 代码

如果不立刻定下来，后续会持续出现：
- 改了但没生效
- 测了但测错入口
- 文档和真实部署不一致
- 排查不断从头来过

### 5.2 当前 FC handler 方案已经实测可用
已完成的事实包括：
- 鉴权链路可用
- 数据库可连通
- schema 已初始化
- 业务写入链路已验证成功

因此从工程效率角度看，继续沿当前可工作的入口推进，成本最低、风险最小。

### 5.3 当前最需要的是收敛，不是再引入新变量
当前阶段的主要风险已经不是“技术选型不高级”，而是：
- 入口不统一
- 配置不统一
- 文档不统一

所以当前正确动作是：
- 先收敛
- 再扩展

---

## 6. 当前需求落地要求

从本文件发布起，BEC 项目当前阶段应遵守以下要求：

### 6.1 API 入口要求
- 当前线上 API 的真实实现，以 `fc-code/index.py` 为准
- 所有线上接口需求、修复和验证，优先落在 `index.handler` 可达路径上
- 若某接口仅存在于 FastAPI router 中，但未映射到 `index.py`，则视为**未上线**

### 6.2 数据库要求
- 生产 / FC 环境数据库统一使用 PostgreSQL
- 不再把 SQLite 作为线上行为参考基线
- 文档、部署配置、健康检查、业务验证都应以 PostgreSQL 为准

### 6.3 验证要求
每次关键接口改动后，至少验证：
- 经 `signing-proxy` 访问 FC 是否成功
- FC 是否返回正确业务结果
- PostgreSQL 中是否有真实读写变化

### 6.4 文档要求
涉及以下内容的文档必须与本决策保持一致：
- 部署说明
- 后端技术设计
- 总体技术设计
- 业务验证文档

若文档中仍写“当前主入口是 FastAPI”，则属于过时描述，应及时修正。

---

## 7. 当前推荐调用链路

推荐统一对外链路：

1. 外部请求到达 ECS
2. 由 signing-proxy 使用服务端 AK/SK 按 ACS3-HMAC-SHA256 进行签名
3. 请求进入 FC HTTP Trigger（`authType=function`）
4. FC 通过 `index.handler` 分发到业务逻辑
5. FC 使用 PostgreSQL 连接串访问 ECS 上数据库

这条链路已验证可用，应作为当前阶段标准路径。

---

## 8. 当前不做的事

为了避免再次发散，当前阶段**不做**以下动作：

1. 不把 FastAPI 路由和 `index.handler` 双线并行都当成线上入口维护
2. 不在没有单独迁移计划的前提下，边修 bug 边尝试“顺手切回 FastAPI 主入口”
3. 不再把 SQLite 当作线上数据库行为的默认参考

---

## 9. 后续工作建议

在“只保留 FC handler”为当前决策的前提下，建议后续工作顺序为：

1. 继续补齐 `fc-code/index.py` 中的核心业务接口
2. 将临时 SQL 逻辑逐步抽取到统一的 service/repository 层（若仍保留 FC handler 入口，也可以内部复用服务层）
3. 清理或标注那些当前不生效的 FastAPI 路由代码，避免误导
4. 持续补充真实接口验证文档，确保每条链路有证据闭环

---

## 10. 当前阶段结论

截至 2026-04-01，BEC 项目的部署与架构收敛结论如下：

- **当前线上唯一可信 API 入口：`fc-code/index.py` 的 `index.handler`**
- **当前阶段只保留 FC handler 方案作为主入口**
- **数据库基线统一为 PostgreSQL**
- **后续需求、修复、验证、文档都必须围绕这一现实展开**

这不是最终架构永远不变的承诺，
而是当前阶段为了避免继续混乱、重复排查、错误修改而做出的明确工程决策。
