# BEC 项目 Sprint 拆分与冻结策略

## 1. 当前整体状态
- **总体进度**：约 47%。
- **已完成（可冻结）**：
  - Web UI 框架 + 路由守卫、鉴权、Layout。
  - BEC Agent CRUD + 版本/回滚 API（FastAPI）以及前端管理界面。
  - 通用 API 层（登录、任务、知识库壳子）与数据模型。
- **进行中**：
  - AI Provider 接入&模型路由（56%）：多 Provider 模型配置、调用链路。
  - RAG 知识库（0% → 需求已定，等待实现）：内容导入、检索、质量评分。
- **未开始**：
  - Chat Testing Page / Conversation Inspect。
  - Task Flow UI / 自动化操作记录。
  - QA/发布流程自动化。

## 2. Sprint 拆分（按优先级）
| Sprint | 目标 | 工作内容 | 优先级 | 负责人 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Sprint 0（已完成） | 骨架搭建 & Agent 基础 | Web UI、权限、BEC Agent CRUD、API 基线、数据库 schema | ⭐️⭐️⭐️⭐️⭐️ | Dev 团队 | ✅ 冻结中 |
| Sprint 1 | 学习内容中心上线 | 词汇/句型接口落地、分页显示、FC handler 数据接入、内容种子脚本 | ⭐️⭐️⭐️⭐️⭐️ | Dev 团队 | ⏳（前端改完，待 build 发布；FC 数据脚本需跑） |
| Sprint 2 | AI Provider & RAG | Provider 抽象（完成 56%）、多模型开关、知识库导入、Embedding/Retrieval API、质量监控 | ⭐️⭐️⭐️⭐️ | AI/Infra | 🔄 进行中 |
| Sprint 3 | 评测 / 任务 / 发布 | Chat 测试页、任务管理页、内容审核→发布流水线、回滚机制 | ⭐️⭐️⭐️ | App / Ops | 🚫 未启动 |

优先级说明：⭐️越多表示越紧迫。Sprint 1 与 Sprint 2 同步推进，但判定上线顺序以学习内容中心作为对外可见里程碑。

## 3. Backlog 详情（优先队列）
1. **学习中心前端 Build & 发布**（阻塞用户反馈）。
2. **FC handler 数据灌入**：运行 `python3 scripts/seed_vocab_from_files.py` / `seed_patterns_from_files.py` 生成真实数据。
3. **AI Provider 56% → 80%**：完成路由、异常处理、Provider 配置 UI。
4. **知识库 RAG MVP**：内容导入（Web/文档）、向量化、检索 API。
5. **Chat 测试面板**：可选模型、实时日志。
6. **任务管理页**：列出执行链路、失败回滚。
7. **内容审核/发布**：加权限 + 审核流。

## 4. 已完成模块的冻结策略
- **代码冻结**：为 Sprint 0（基础骨架）建立 Tag：`git tag bec-sprint0-freeze <commit>`，若需回滚可 `git checkout tags/bec-sprint0-freeze`。
- **配置冻结**：记录当前 `.env` / `fc-config/s.yaml`，保存在 `deploy/freeze/bec-sprint0/`（已在仓库 ignore 外部 secret）。
- **数据库快照**：对基础 schema & 初始数据导出 SQL（见 `docs/schema.sql`，可再导出 `sql/bec_sprint0_seed.sql`）。
- **恢复流程**：
  1. `git checkout bec-sprint0-freeze` 获取代码。
  2. `psql < sql/bec_sprint0_seed.sql`（或对应 RDS snapshot）。
  3. `npm install && npm run build`，`uvicorn src.api.main:app`。
  4. 验证 Agent CRUD、登录、基础 UI 是否恢复。

## 5. 后续文档与追踪
- 本文作为迭代计划 & 冻结记录，请在每个 Sprint 完成后追加 `Sprint X Freeze` 小节记录：
  - 完成时间 / Commit Hash / Tag。
  - 数据/配置快照位置。
  - 已知问题与恢复步骤。
- 对外沟通统一引用本文件链接，确保优先级、状态一致，避免“已完成 vs 未 build”这类沟通偏差。

## 6. Sprint 1 冻结记录（2026-04-06）
- **Tag**：`sprint1-freeze-20260406`（与 master 对齐后立即 `git tag -a sprint1-freeze-20260406` + `git push origin sprint1-freeze-20260406`）
- **范围**：完成学习内容中心 MVP，包括词汇/句型分页展示、FC handler 接口（词汇/句型/场景/模拟考试）、内容 YAML & 脚本、签名代理 + nginx 正式站点以及前端响应式适配+模拟考试随机抽题。
- **数据快照**：
  - `content/` 目录保存全部词汇、句型、场景、模拟考试 YAML；
  - `scripts/seed_*.py` + `sql/seed_demo_content.sql`、`sql/seed_content_snapshot.sql` 为恢复脚本；
  - PostgreSQL 通过 `scripts/export_content_snapshot.py` 导出的 `sql/seed_content_snapshot.sql` 可用于灌库；
  - 线上静态包位于 `deploy/nginx-datahive-site/html/`，Proxy/FC 配置记录在 `docs/datahive-site-deployment.md`。
- **验收/回归**：
  1. https://datahive.site 登录 → 查看“学习看板 / 词汇与句型 / 模拟考试”全部走 API；
  2. `curl https://datahive.site/api/v1/vocab?page=1&page_size=100`、`/patterns`、`/mock-exams` 返回真实数据；
  3. `python3 scripts/seed_vocab_from_files.py`、`seed_patterns_from_files.py` 可从 `content/` 重新灌库；
  4. `python3 scripts/export_content_snapshot.py` 可再生 snapshot 与当前一致；
  5. 模拟考试页面点击“换一套试题”时确认题目顺序发生变化。
- **已知问题**：AI Provider&RAG 仍在 Sprint 2，下一阶段重点，不影响 Sprint 1 交付。

