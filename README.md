# AI Agent Platform

基于 Python 的 AI Agent 平台，支持多模型接入、知识库 RAG、任务编排和插件扩展。

## 🎯 核心功能

- **多模型支持** - 通义千问、DeepSeek、Kimi 等
- **知识库 RAG** - 网页采集、质量评分、向量检索
- **任务编排** - 工作流引擎、定时任务
- **插件系统** - 动态加载、扩展能力
- **Web UI** - 对话界面、知识管理

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ai-agent-platform
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp config/.env.example config/.env
# 编辑 config/.env，填入 API Key
```

### 3. 运行服务

```bash
# 开发模式
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 或 Docker
docker-compose up
```

### 4. 访问

- API 文档：http://localhost:8000/docs
- Web UI：http://localhost:8000

## 📚 文档

- [需求文档](docs/requirements.md)
- [技术设计](docs/technical-design.md)
- [功能清单](docs/IMPLEMENTATION_CHECKLIST.md)

## 🏗️ 项目结构

```
ai-agent-platform/
├── src/                      # 源代码
│   ├── core/                 # 核心引擎
│   ├── providers/            # AI 模型提供商
│   ├── api/                  # API 接口
│   ├── plugins/              # 插件系统
│   ├── models/               # 数据模型
│   └── utils/                # 工具函数
├── tests/                    # 测试
├── config/                   # 配置文件
├── data/                     # 数据持久化
├── docs/                     # 文档
└── scripts/                  # 脚本
```

## 📦 技术栈

- **后端:** Python 3.10 + FastAPI
- **数据库:** SQLite (单机) / PostgreSQL (扩展)
- **向量库:** ChromaDB
- **AI 模型:** Qwen / DeepSeek / Kimi
- **部署:** Docker Compose / Systemd

## 💰 成本

- **服务器:** 阿里云 ECS 2 核 2G（现有资源）
- **额外成本:** ¥0/月（仅 OSS 按量付费）

## 📝 开发进度

- [x] 项目骨架
- [ ] AI Provider 集成
- [ ] Agent 引擎
- [ ] 基础 API
- [ ] Web UI

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License
