# BEC 商务英语智能学习平台 - 后端技术设计文档

**版本:** 1.0  
**更新日期:** 2026-03-31  
**适用范围:** Python API、业务服务层、AI能力编排层

---

## 1. 文档目标

本文档用于定义 BEC 商务英语智能学习平台后端部分的技术架构、模块边界、API 设计、服务拆分与部署方式，指导后端研发落地。

---

## 2. 后端定位

后端承担以下职责：
- 提供统一 REST API
- 承载用户、学习、测试、内容、审核等核心业务逻辑
- 调用大模型服务完成场景反馈与内容辅助处理
- 连接部署在 ECS 上的数据库

后端不承担：
- 前端静态页面渲染
- 数据库直接管理界面
- 本地大模型推理

---

## 3. 技术选型

- Python 3.10+
- FC 自定义 handler（当前线上主入口）
- FastAPI（保留为参考/本地组织形式，不作为当前线上真实入口）
- SQLAlchemy
- Pydantic
- Alembic
- httpx

### 选型原因
- FC 自定义 handler 已经完成线上鉴权、数据库连接和真实业务写入验证，是当前唯一可信的线上入口
- FastAPI 仍可作为代码组织与后续演进参考，但当前阶段不能假定其 router 已直接对外生效
- Pydantic 适合请求/响应数据校验
- SQLAlchemy 适合复杂业务建模
- Alembic 适合数据库版本迁移
- httpx 适合调用第三方模型与外部接口

---

## 4. 后端模块划分

### 4.1 认证与用户模块
- 注册
- 登录
- Token 鉴权
- 用户画像维护

### 4.2 水平测试模块
- 题目分发
- 测试提交
- 自动评分
- 等级判定

### 4.3 单词学习模块
- 单词列表与详情
- 学习状态更新
- 复习入口

### 4.4 句型学习模块
- 句型列表与详情
- 学习状态更新

### 4.5 场景训练模块
- 场景列表与详情
- 对话上下文管理
- 调用 AI 生成反馈
- 训练结果记录

### 4.6 模拟考试模块
- 试卷分发
- 作答提交
- 自动评分
- 成绩输出

### 4.7 内容管理模块
- 内容导入
- 内容查询
- 内容审核
- 内容发布

---

## 5. 服务层设计

建议目录：

```text
src/
├── api/
├── services/
├── repositories/
├── models/
├── schemas/
├── integrations/
└── utils/
```

### 5.1 services
承载业务逻辑：
- user_service
- level_test_service
- vocab_service
- pattern_service
- scene_service
- mock_exam_service
- content_service
- review_service

### 5.2 repositories
承载数据库访问逻辑，减少服务层直接写 SQL。

### 5.3 integrations
承载外部服务接入：
- AI 模型调用
- 第三方接口

---

## 6. API 设计原则

### 6.1 统一前缀
- `/api/v1/`

### 6.2 返回规范
- 成功：统一返回 `code/message/data`
- 失败：统一返回错误码与错误说明

### 6.3 鉴权策略
- 登录后获取 Token
- 受保护接口统一校验 Token

---

## 7. 核心 API 列表

### 7.1 用户接口
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/profile`
- `PUT /api/v1/users/profile`

### 7.2 水平测试接口
- `GET /api/v1/level-test/start`
- `POST /api/v1/level-test/submit`
- `GET /api/v1/level-test/result/{id}`

### 7.3 单词接口
- `GET /api/v1/vocab`
- `GET /api/v1/vocab/{id}`
- `POST /api/v1/vocab/{id}/progress`

### 7.4 句型接口
- `GET /api/v1/patterns`
- `GET /api/v1/patterns/{id}`
- `POST /api/v1/patterns/{id}/progress`

### 7.5 场景训练接口
- `GET /api/v1/scenes`
- `GET /api/v1/scenes/{id}`
- `POST /api/v1/scenes/{id}/start`
- `POST /api/v1/scenes/{id}/message`
- `POST /api/v1/scenes/{id}/finish`

### 7.6 模拟考试接口
- `GET /api/v1/mock-exams`
- `POST /api/v1/mock-exams/{id}/submit`
- `GET /api/v1/mock-exams/result/{id}`

### 7.7 内容管理接口
- `POST /api/v1/content/import`
- `GET /api/v1/content/review/pending`
- `POST /api/v1/content/review/{id}`
- `POST /api/v1/content/publish/{id}`

---

## 8. AI 能力接入设计

### 8.1 主要使用场景
- 场景对话回复生成
- 表达纠错与优化建议
- 内容辅助结构化

### 8.2 接入原则
- 统一封装模型调用接口
- 业务服务不直接耦合具体模型厂商
- 支持 Qwen / DeepSeek / Kimi 替换

---

## 9. 部署方式

### 9.1 部署位置
- 后端服务部署在阿里云函数计算 FC

### 9.2 当前线上入口约定
- 当前线上唯一可信 API 入口为：`fc-code/index.py` 的 `index.handler`
- `src/api/routes/*.py` 当前不应被视为线上真实入口
- 若某接口仅存在于 FastAPI router 中，而未落入 `index.handler` 路由分发表，则应视为未上线

### 9.3 调用链路
- 前端通过 `datahive.top/api/` 调用后端
- ECS signing-proxy 负责服务端签名后访问 FC
- FC 由 `index.handler` 承接请求
- FC 再连接 ECS 上的 Docker PostgreSQL 数据库

### 9.3 约束
- FC 不适合长连接重任务
- 后端应尽量保持轻量请求模型
- 重采集和重处理任务不建议放在主请求链路中执行

---

## 10. 风险与应对

### 10.1 风险
- FC 到 ECS 数据库连接稳定性受网络影响
- 模型调用成本和稳定性不一致
- 场景训练链路复杂，容易成为性能瓶颈

### 10.2 应对
- 控制数据库连接池与超时参数
- 统一封装模型接口，保留切换能力
- 首版优先做少量高质量场景

---

## 11. 结论

后端应采用 FastAPI 单体服务架构，部署在阿里云函数计算 FC 中，通过统一服务层承载 BEC 商务英语平台的核心业务逻辑，并通过 Nginx + `/api/` 入口与前端对接，通过安全受控方式访问 ECS 上的数据库。
