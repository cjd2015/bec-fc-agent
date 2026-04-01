# BEC 商务英语智能学习平台 - 技术设计文档

**版本:** 2.1  
**更新日期:** 2026-04-01  
**技术栈:** Python 3.10 + FC Handler + React + TypeScript

---

## 1. 架构设计

### 1.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│               Web / H5 Frontend (React + TS)                │
│          本地/ECS 构建 → 部署到 ECS Nginx 或 OSS            │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│         阿里云函数计算 FC（Python / 自定义 Handler）         │
│  用户接口 │ 学习接口 │ 测试接口 │ 内容接口 │ 审核接口 │ AI编排 │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    Core Services Layer                       │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐      │
│ │ User     │ │ Learning │ │ Testing  │ │ Content     │      │
│ │ Service  │ │ Service  │ │ Service  │ │ Service     │      │
│ └──────────┘ └──────────┘ └──────────┘ └─────────────┘      │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐      │
│ │ Review   │ │ Progress │ │ Recommend│ │ Analytics   │      │
│ │ Service  │ │ Service  │ │ Service  │ │ Service     │      │
│ └──────────┘ └──────────┘ └──────────┘ └─────────────┘      │
└──────────────────────────────────────────────────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          ▼                                     ▼
┌──────────────────────────────┐   ┌──────────────────────────┐
│ 阿里云模型/第三方AI服务       │   │  阿里云 ECS（2核2G）      │
│ Qwen / DeepSeek / Kimi 等    │   │ OpenClaw + Docker DB +   │
└──────────────────────────────┘   │ Nginx(前端静态资源/反代)  │
                                   │ PostgreSQL/MySQL(低配)   │
                                   └──────────────────────────┘
```

### 1.2 设计原则

- **业务域分层:** 用户、学习、测试、内容、审核分层设计
- **内容资产化:** 单词、句型、场景、题目作为结构化内容资产管理
- **MVP 优先:** 先打通测试→学习→场景→模考主链路
- **可扩展:** 为推荐、积分、错题本、学习报告预留扩展能力
- **内容驱动:** 前台学习能力依赖稳定内容供给系统
- **计算与存储分离:** Python 业务服务部署在阿里云函数计算，数据库部署在阿里云 ECS，降低 ECS 资源压力
- **入口收敛优先:** 当前阶段仅以 FC 自定义 handler 作为线上真实 API 入口，避免 FastAPI router 与 handler 双轨并行造成混乱
- **前后端分层部署:** 前端静态资源采用“本地/ECS 构建 + ECS Nginx 或 OSS 托管”，后端 API 部署在 FC
- **低成本启动:** 复用现有 FC 包年包月资源与现有 ECS，避免首版直接采购高成本云数据库
- **渐进式演进:** 首版采用“前端静态资源 + FC API + 自建数据库”方案，待业务稳定后再评估迁移至云数据库或更高规格架构

---

## 2. 目录结构建议

```
ai-agent-platform/
├── docs/
│   ├── requirements.md
│   ├── technical-design.md
│   ├── IMPLEMENTATION_CHECKLIST.md
│   └── requirements-library/
├── src/
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── level_test.py
│   │   │   ├── vocab.py
│   │   │   ├── pattern.py
│   │   │   ├── scene.py
│   │   │   ├── mock_exam.py
│   │   │   ├── content.py
│   │   │   └── review.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── level_test_service.py
│   │   ├── vocab_service.py
│   │   ├── pattern_service.py
│   │   ├── scene_service.py
│   │   ├── mock_exam_service.py
│   │   ├── progress_service.py
│   │   ├── content_service.py
│   │   ├── review_service.py
│   │   └── recommendation_service.py
│   ├── models/
│   │   ├── user.py
│   │   ├── content.py
│   │   ├── learning.py
│   │   └── exam.py
│   ├── repositories/
│   ├── schemas/
│   ├── utils/
│   └── tasks/
├── frontend/
├── tests/
├── config/
└── scripts/
```

---

## 3. 核心模块设计

### 3.1 用户模块

职责：
- 用户注册/登录
- 用户画像维护
- 学习目标记录
- 登录态与权限校验

关键实体：
- user
- user_profile

### 3.2 水平测试模块

职责：
- 测试引导
- 测试题分发
- 自动评分
- 等级判定
- 测试结果报告

关键实体：
- question_content（module_type=level_test）
- level_test_record
- level_test_answer

### 3.3 单词学习模块

职责：
- 单词内容展示
- 商务主题词汇分类
- 学习状态记录
- 复习基础能力

关键实体：
- vocab_content
- user_vocab_progress

### 3.4 句型学习模块

职责：
- 商务句型展示
- 使用场景与功能类型管理
- 学习状态记录

关键实体：
- pattern_content
- user_pattern_progress

### 3.5 场景对话训练模块

职责：
- 场景列表与详情
- 场景目标与角色定义
- 多轮对话记录
- 反馈总结与评分

关键实体：
- scene_content
- user_scene_session

### 3.6 模拟考试模块

职责：
- 模考试卷分发
- 作答流程
- 自动评分
- 成绩与弱项分析

关键实体：
- question_content（module_type=mock_exam）
- mock_exam_record
- mock_exam_answer

### 3.7 内容采集与内容生产模块

职责：
- 内容来源管理
- 原始内容存储
- 数据结构化
- 标签绑定
- 内容审核
- 内容发布

关键实体：
- content_source
- raw_content
- vocab_content
- pattern_content
- scene_content
- question_content
- content_tag
- content_tag_relation
- content_review_record
- content_publish_record

### 3.8 推荐与分析模块（预留）

职责：
- 基于测试结果推荐学习内容
- 基于模考结果推荐补强模块
- 汇总用户学习行为

关键实体：
- user_learning_record
- recommendation_record
- wrong_book_record

---

## 4. 数据模型设计

### 4.1 数据域划分

- **用户域**：user, user_profile
- **内容域**：content_source, raw_content, vocab_content, pattern_content, scene_content, question_content, content_tag, content_tag_relation
- **采集审核域**：collect_task, content_review_record, content_publish_record
- **学习行为域**：user_vocab_progress, user_pattern_progress, user_scene_session, user_learning_record
- **测试模考域**：level_test_record, level_test_answer, mock_exam_record, mock_exam_answer
- **运营扩展域**：user_points_account, user_points_log, recommendation_record, wrong_book_record

### 4.2 MVP 核心表

- user
- user_profile
- content_source
- raw_content
- vocab_content
- pattern_content
- scene_content
- question_content
- content_tag
- content_tag_relation
- content_review_record
- user_vocab_progress
- user_pattern_progress
- user_scene_session
- level_test_record
- level_test_answer
- mock_exam_record
- mock_exam_answer

### 4.3 表关系原则

- 用户与画像：1:1
- 用户与学习记录：1:N
- 用户与测试/模考：1:N
- 内容来源与原始内容：1:N
- 原始内容与结构化内容：1:N
- 内容与标签：N:N
- 题目内容被水平测试与模考答案引用

---

## 5. API 设计

### 5.1 用户接口
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/profile`
- `PUT /api/v1/users/profile`

### 5.2 水平测试接口
- `GET /api/v1/level-test/start`
- `POST /api/v1/level-test/submit`
- `GET /api/v1/level-test/result/{id}`

### 5.3 单词学习接口
- `GET /api/v1/vocab`
- `GET /api/v1/vocab/{id}`
- `POST /api/v1/vocab/{id}/progress`

### 5.4 句型学习接口
- `GET /api/v1/patterns`
- `GET /api/v1/patterns/{id}`
- `POST /api/v1/patterns/{id}/progress`

### 5.5 场景训练接口
- `GET /api/v1/scenes`
- `GET /api/v1/scenes/{id}`
- `POST /api/v1/scenes/{id}/start`
- `POST /api/v1/scenes/{id}/message`
- `POST /api/v1/scenes/{id}/finish`

### 5.6 模拟考试接口
- `GET /api/v1/mock-exams`
- `POST /api/v1/mock-exams/{id}/submit`
- `GET /api/v1/mock-exams/result/{id}`

### 5.7 内容管理与审核接口
- `POST /api/v1/content/import`
- `GET /api/v1/content/review/pending`
- `POST /api/v1/content/review/{id}`
- `POST /api/v1/content/publish/{id}`

---

## 6. 技术选型

### 6.1 后端
- FC 自定义 handler（当前线上主入口）
- FastAPI（保留为参考/本地组织形式，不作为当前线上真实入口）
- SQLAlchemy
- Pydantic
- Alembic

### 6.2 前端
- React 18
- TypeScript
- Zustand / React Query
- Ant Design

### 6.3 数据层
- SQLite（开发）
- PostgreSQL / MySQL（生产，优先部署在阿里云 ECS 的 Docker 容器中）
- Redis（缓存/任务扩展，后续按需增加）
- ChromaDB / Qdrant（推荐和语义检索后续扩展）

### 6.4 部署策略
- **前端层部署：** React 前端在本地或 ECS 完成 build，产物优先部署到 ECS Nginx；后续可按需迁移到 OSS 静态站点
- **应用层部署：** Python 服务部署在阿里云函数计算 FC，当前阶段以 `fc-code/index.py` 的 `index.handler` 作为唯一真实线上入口
- **数据库层部署：** PostgreSQL / MySQL 部署在现有阿里云 ECS（2核2G，Docker 低配运行）
- **OpenClaw 部署：** 保持运行在现有 ECS 上，不与 Python 常驻服务抢占过多资源
- **Web 接入层：** `datahive.top` 域名优先解析到 ECS，由 Nginx 承担 HTTPS、前端静态资源分发与 `/api/` 反向代理到 FC
- **架构目标：** 通过“前端静态托管 + 函数计算承载业务计算 + ECS 承载数据库存储”的方式，兼顾低成本、可落地性与后续扩展性
- **安全要求：** FC 访问 ECS 数据库时需配置安全组、白名单、强密码与必要的连接保护措施
- **运维原则：** ECS 仅承载 OpenClaw、数据库、Nginx 与必要备份任务，避免叠加重采集任务、向量库和高内存服务

### 6.5 AI / 智能能力
- 用于场景对话反馈
- 用于内容辅助生成
- 用于后续学习建议与推荐增强

---

## 7. 实施步骤

### 第一阶段：基础部署与 MVP 核心链路
- 完成阿里云函数计算 FC 的 Python / FastAPI 服务部署
- 完成阿里云 ECS 上数据库 Docker 化部署与低配调优
- 打通 FC 到 ECS 数据库的网络连接、安全组与访问控制
- 用户注册/登录
- 水平测试
- 单词学习
- 句型学习
- 场景训练
- 模拟考试
- 内容采集与结构化基础能力
- 审核基础能力

### 第二阶段：体验与反馈增强
- 重新测试
- 对话复盘
- 模考弱项推荐
- 学习进度看板
- 内容发布管理
- 数据质量监控
- 数据库备份与恢复机制增强

### 第三阶段：增长与智能化
- 推荐系统
- 积分系统
- 错题本与弱项本
- 学习报告增强
- AI 辅助内容生产优化
- 评估数据库是否迁移至更高规格 ECS 或云数据库

---

## 8. 测试策略

### 8.1 单元测试
- 用户服务
- 测试评分逻辑
- 学习进度逻辑
- 内容审核逻辑

### 8.2 集成测试
- 注册/登录流程
- 水平测试到结果流程
- 单词/句型学习状态保存
- 场景训练记录
- 模考评分与结果生成
- 内容导入到审核流程

### 8.3 端到端测试
- 用户从测试到学习到模考的完整流程
- 内容录入到发布的完整流程

---

## 9. 风险与约束

### 9.1 风险
- 内容供给不足会导致前台功能空转
- 场景反馈质量不足会削弱核心竞争力
- 数据结构设计不清会影响后续推荐与分析
- MVP 过大容易拖慢首版上线
- FC 连接 ECS 数据库存在公网链路稳定性与安全风险
- 现有 ECS 仅 2核2G，数据库必须控制资源占用，否则会与 OpenClaw 争抢内存

### 9.2 应对策略
- 优先建设内容供给体系
- 场景训练先做少量高质量场景
- 数据模型先规范化
- 推荐和积分系统后置
- ECS 仅运行 OpenClaw 与低配数据库，不承载 Python 常驻服务和高负载组件
- 为数据库设置低内存参数、连接数限制和备份机制
- 为 FC 到 ECS 的访问配置安全组、白名单、强密码与必要的传输保护

---

## 10. 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-30 | 原 AI Agent Platform 技术设计文档 | AI Assistant |
| 2.0 | 2026-03-31 | 重写为 BEC 商务英语智能学习平台技术设计文档，匹配最新需求、数据设计与内容采集体系 | AI Assistant |
