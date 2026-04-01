# BEC 商务英语智能学习平台 - 部署版 README

**版本:** 1.0  
**更新时间:** 2026-03-31  
**定位:** 当前整套部署、技术设计、数据库、安全与执行文档的入口索引

---

## 1. 这份文档的作用

本文档是 BEC 商务英语智能学习平台当前阶段的部署与实施入口文档，适合用于：

- 快速了解项目当前技术方案
- 快速找到部署相关文档
- 作为研发、测试、运维的统一入口
- 用于后续继续补充和维护整套文档库

---

## 2. 当前部署方案结论

当前项目采用以下 MVP 部署架构：

### 前端
- 本地或 ECS 构建
- 构建产物部署到 ECS 上的 Nginx
- 后续可迁移到 OSS 静态站点

### 后端 API
- 部署到阿里云函数计算 FC

### 数据库
- 部署到当前 ECS 的 Docker PostgreSQL

### 域名与 HTTPS
- `datahive.top` 指向 ECS
- ECS 上的 Nginx 提供 HTTPS
- `/api/` 反向代理到 FC

---

## 3. 推荐阅读顺序

如果你是第一次接手本项目，建议按以下顺序阅读：

### 第一层：先看整体方案
1. `requirements.md`
2. `technical-design.md`
3. `deployment-strategy.md`

### 第二层：再看详细设计
4. `frontend-technical-design.md`
5. `backend-technical-design.md`
6. `database-technical-design.md`
7. `api-spec.md`

### 第三层：看数据库落地文件
8. `schema.sql`
9. `field-dictionary.md`
10. `seed.sql`

### 第四层：看部署执行文件
11. `deployment-runbook.md`
12. `nginx.conf`
13. `fc-deployment.md`
14. `docker-compose.secure.yml`
15. `postgresql.conf`
16. `pg_hba.conf`
17. `Makefile`

### 第五层：看安全与上线
18. `security-checklist.md`
19. `go-live-checklist.md`
20. `domain-ssl-security-checklist.md`

---

## 4. 关键文档说明

### 4.1 产品与技术主文档
- `requirements.md`：正式需求文档
- `technical-design.md`：总体技术设计文档
- `deployment-strategy.md`：部署方案文档

### 4.2 分层技术设计
- `frontend-technical-design.md`：前端技术设计
- `backend-technical-design.md`：后端技术设计
- `database-technical-design.md`：数据库技术设计
- `api-spec.md`：接口规范文档

### 4.3 数据库文件
- `schema.sql`：核心建表草案
- `field-dictionary.md`：字段字典
- `seed.sql`：初始化数据脚本

### 4.4 部署文件
- `deployment-runbook.md`：部署执行手册
- `nginx.conf`：Nginx 正式配置骨架
- `fc-deployment.md`：FC 部署说明
- `docker-compose.secure.yml`：PostgreSQL Docker 安全部署文件
- `postgresql.conf`：PostgreSQL 低配安全配置
- `pg_hba.conf`：PostgreSQL 白名单访问配置
- `Makefile`：常用部署命令集合

### 4.5 安全与检查文件
- `security-checklist.md`：前后端安全检查清单
- `go-live-checklist.md`：上线检查清单
- `domain-ssl-security-checklist.md`：域名/SSL/安全组检查清单

---

## 5. 当前部署落地建议

实际落地时建议按如下步骤执行：

1. 准备 ECS 目录和基础环境
2. 部署 PostgreSQL Docker
3. 导入 `schema.sql`
4. 导入 `seed.sql`
5. 配置 `postgresql.conf` 和 `pg_hba.conf`
6. 配置 Nginx 与 SSL
7. 配置域名解析
8. 部署 FC 后端 API
9. 部署前端静态资源
10. 按 `go-live-checklist.md` 完成上线检查

详细执行步骤请参考：
- `deployment-runbook.md`

---

## 6. 当前资源约束说明

当前服务器资源：
- 阿里云 ECS：2核2G / 40G / 3M 带宽

因此当前方案明确约束：
- ECS 只跑 OpenClaw、Nginx、Docker PostgreSQL
- Python API 不在 ECS 常驻运行
- Python API 放在阿里云函数计算 FC
- 当前环境定位为 MVP / 小规模验证环境

---

## 7. 当前文档库状态

当前文档已经覆盖以下方面：
- 产品需求
- 总体技术设计
- 部署方案
- 前后端数据库设计
- API 规范
- SQL 草案
- 初始化数据
- Nginx / FC / Docker / PostgreSQL 配置
- 安全清单
- 上线清单
- 研发任务拆解

说明：
当前文档库已具备“研发开工 + 部署准备 + 上线检查”的基础能力。

---

## 8. 下一步建议

如果继续推进，建议优先补充以下内容：

### 代码与执行层
- 前端实际项目骨架
- 后端实际项目骨架
- 数据库 migration 机制

### 管理与协作层
- 联调检查表
- 研发排期表
- 负责人分工表

### 运维增强层
- 备份脚本
- 日志轮转脚本
- 健康检查脚本

---

## 9. 结论

如果只看一份入口文档，请先看本文件；
如果只做一次部署，请直接结合以下文件执行：

- `deployment-runbook.md`
- `nginx.conf`
- `docker-compose.secure.yml`
- `postgresql.conf`
- `pg_hba.conf`
- `schema.sql`
- `seed.sql`
- `go-live-checklist.md`

这几份文件已经构成当前 MVP 阶段最核心的落地组合。
