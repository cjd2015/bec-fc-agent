# AI Agent Platform - 技术设计文档

**版本:** 1.0  
**更新日期:** 2026-03-30  
**技术栈:** Python 3.10

---

## 1. 架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│              Web UI (React 18 + TypeScript)              │
│         Ant Design 5 + Zustand + React Query            │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                 │
│  - REST API  │  WebSocket  │  Auth  │  Rate Limiting    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Core Services Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   Agent  │  │  Memory  │  │   Task   │  │  Plugin  │ │
│  │  Engine  │  │  Manager │  │ Scheduler│  │  System  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   AI Provider Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Qwen    │  │ DeepSeek │  │  Kimi    │  │  Others  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Persistence                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │PostgreSQL│  │  SQLite  │  │  Redis   │              │
│  │ (Prod)   │  │  (Dev)   │  │ (Cache)  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 1.2 设计原则

- **模块化:** 各组件独立，可单独测试和替换
- **可扩展:** 插件架构，支持水平扩展
- **云优先:** 优先适配阿里云 MCP/Agent 生态
- **AI 原生:** 深度集成 AI 能力，支持向量检索、语义理解

---

## 2. 目录结构

```
ai-agent-platform/
├── docs/                      # 文档
│   ├── requirements.md        # 需求文档
│   ├── technical-design.md    # 技术设计
│   └── api.md                 # API 文档
├── src/                       # 源代码
│   ├── core/                  # 核心引擎
│   │   ├── __init__.py
│   │   ├── agent.py           # Agent 引擎
│   │   ├── memory.py          # 记忆管理
│   │   ├── task.py            # 任务调度
│   │   └── plugin.py          # 插件系统
│   ├── providers/             # AI 模型提供商
│   │   ├── __init__.py
│   │   ├── base.py            # 基础接口
│   │   ├── qwen.py            # 通义千问
│   │   ├── deepseek.py        # DeepSeek
│   │   └── kimi.py            # Kimi
│   ├── api/                   # API 接口
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── routes/            # 路由
│   │   │   ├── chat.py
│   │   │   ├── memory.py
│   │   │   ├── task.py
│   │   │   └── plugin.py
│   │   └── middleware/        # 中间件
│   │       ├── auth.py
│   │       └── rate_limit.py
│   ├── plugins/               # 内置插件
│   │   ├── __init__.py
│   │   ├── web_search.py
│   │   ├── file_manager.py
│   │   └── calendar.py
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── memory.py
│   │   ├── task.py
│   │   └── plugin.py
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── config.py
│       ├── logger.py
│       └── helpers.py
├── tests/                     # 测试
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── fixtures/              # 测试数据
├── config/                    # 配置文件
│   ├── default.yaml
│   ├── development.yaml
│   └── production.yaml
├── scripts/                   # 脚本
│   ├── setup.sh
│   ├── migrate.py
│   └── deploy.sh
├── requirements.txt           # Python 依赖
├── requirements-dev.txt       # 开发依赖
├── pyproject.toml             # 项目配置
├── Dockerfile                 # Docker 镜像
├── docker-compose.yml         # Docker Compose
└── README.md                  # 项目说明
```

---

## 3. 核心模块设计

### 3.1 Agent 引擎

```python
# src/core/agent.py
class AgentEngine:
    def __init__(self, provider: AIProvider, memory: MemoryManager):
        self.provider = provider
        self.memory = memory
        self.plugins: List[Plugin] = []
    
    async def chat(self, message: str, context: dict) -> str:
        # 1. 检索相关记忆
        relevant_memories = await self.memory.search(message)
        
        # 2. 构建上下文
        context = self._build_context(message, relevant_memories)
        
        # 3. 调用 AI 模型
        response = await self.provider.generate(context)
        
        # 4. 存储新记忆
        await self.memory.add(message, response)
        
        return response
    
    def register_plugin(self, plugin: Plugin):
        self.plugins.append(plugin)
```

### 3.2 记忆管理

```python
# src/core/memory.py
class MemoryManager:
    def __init__(self, db: Database, vector_store: VectorStore):
        self.db = db
        self.vector_store = vector_store
    
    async def add(self, user_msg: str, assistant_msg: str):
        # 存储到数据库
        memory = Memory(
            user_message=user_msg,
            assistant_message=assistant_msg,
            embedding=self.vector_store.embed(user_msg + assistant_msg)
        )
        await self.db.save(memory)
    
    async def search(self, query: str, limit: int = 5) -> List[Memory]:
        # 语义搜索
        query_embedding = self.vector_store.embed(query)
        return await self.vector_store.similarity_search(query_embedding, limit)
```

### 3.3 任务调度

```python
# src/core/task.py
class TaskScheduler:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.executor = AsyncExecutor()
    
    async def schedule(self, task: Task, trigger: Trigger):
        if trigger.type == "cron":
            await self._schedule_cron(task, trigger.expression)
        elif trigger.type == "event":
            await self._subscribe_event(task, trigger.event)
    
    async def execute(self, task: Task):
        try:
            result = await self.executor.run(task.workflow)
            await self._notify_completion(task, result)
        except Exception as e:
            await self._handle_error(task, e)
```

### 3.4 插件系统

```python
# src/core/plugin.py
class PluginSystem:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
    
    def load(self, plugin_path: str):
        # 动态加载插件
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        plugin = module.Plugin()
        self.plugins[plugin.name] = plugin
    
    def unload(self, plugin_name: str):
        del self.plugins[plugin_name]
    
    def get_tools(self) -> List[Tool]:
        # 聚合所有插件的工具
        tools = []
        for plugin in self.plugins.values():
            tools.extend(plugin.get_tools())
        return tools
```

---

## 4. 数据模型

### 4.1 用户模型

```python
class User(Base):
    __tablename__ = "users"
    
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(50), unique=True)
    email: str = Column(String(100))
    api_key: str = Column(String(64), unique=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, onupdate=datetime.utcnow)
```

### 4.2 记忆模型

```python
class Memory(Base):
    __tablename__ = "memories"
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    user_message: Text = Column(Text)
    assistant_message: Text = Column(Text)
    embedding: Vector = Column(Vector(1536))  # 向量嵌入
    tags: List[str] = Column(JSON)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

### 4.3 任务模型

```python
class Task(Base):
    __tablename__ = "tasks"
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    name: str = Column(String(100))
    workflow: JSON = Column(JSON)  # 工作流定义
    trigger: JSON = Column(JSON)   # 触发器配置
    status: str = Column(String(20))  # pending, running, completed, failed
    last_run: datetime = Column(DateTime)
    next_run: datetime = Column(DateTime)
```

---

## 5. API 设计

### 5.1 对话接口

```http
POST /api/v1/chat
Content-Type: application/json
Authorization: Bearer <token>

{
  "message": "你好，请介绍一下自己",
  "model": "qwen",
  "stream": true
}

Response:
{
  "id": "chat_123",
  "content": "你好！我是 AI 助手...",
  "model": "qwen",
  "usage": {"prompt_tokens": 10, "completion_tokens": 50}
}
```

### 5.2 记忆接口

```http
GET /api/v1/memories?q=项目进度&limit=10
Authorization: Bearer <token>

Response:
{
  "items": [
    {
      "id": 1,
      "user_message": "项目进度如何？",
      "assistant_message": "目前完成了 80%...",
      "created_at": "2026-03-29T10:00:00Z"
    }
  ],
  "total": 1
}
```

### 5.3 任务接口

```http
POST /api/v1/tasks
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "每日报告",
  "workflow": {...},
  "trigger": {
    "type": "cron",
    "expression": "0 9 * * *"
  }
}
```

---

## 6. 依赖管理

### 6.1 核心依赖 (requirements.txt)

```txt
# Web 框架
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.25
asyncpg==0.29.0
aiosqlite==0.19.0

# AI 集成
httpx==0.26.0
tenacity==8.2.3

# 向量检索
chromadb==0.4.22
sentence-transformers==2.3.1

# 任务调度
apscheduler==3.10.4
celery==5.3.6

# 认证
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# 配置
pyyaml==6.0.1
pydantic==2.5.3
pydantic-settings==2.1.0

# 日志
loguru==0.7.2

# 工具
python-dotenv==1.0.0
click==8.1.7
```

### 6.2 开发依赖 (requirements-dev.txt)

```txt
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
black==23.12.1
ruff==0.1.11
mypy==1.8.0
httpx==0.26.0  # 用于测试客户端
```

---

## 7. 部署方案

### 7.1 Docker Compose (开发环境)

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/agent
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=agent
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 7.2 阿里云部署 (生产环境)

- **计算:** 阿里云 ECS 或 函数计算 FC
- **数据库:** 阿里云 RDS PostgreSQL
- **缓存:** 阿里云 Redis
- **存储:** 阿里云 OSS（文件存储）
- **监控:** 阿里云 ARMS + SLS

---

## 8. 测试策略

### 8.1 单元测试

- 覆盖核心逻辑（Agent、Memory、Task、Plugin）
- 目标覆盖率：≥ 80%
- 使用 pytest + pytest-asyncio

### 8.2 集成测试

- API 接口测试
- 数据库操作测试
- AI Provider 集成测试

### 8.3 端到端测试

- 完整工作流测试
- 性能测试（负载、压力）
- 使用 pytest + httpx

---

## 9. 安全考虑

### 9.1 认证授权

- JWT Token 认证
- API Key 管理
- 基于角色的访问控制（RBAC）

### 9.2 数据安全

- 敏感数据加密存储
- API 通信 HTTPS
- SQL 注入防护（使用 ORM）

### 9.3 速率限制

- 基于 IP 的限流
- 基于用户的限流
- 可配置的限流策略

---

## 10. 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0 | 2026-03-30 | 初始版本，确认 Python 3.10 技术栈 | AI Assistant |

---

## 11. 题库与知识库设计

### 11.1 题库来源

题库是结构化知识，用于测试、评估和训练场景。

#### 来源渠道

| 来源 | 描述 | 获取方式 | 优先级 |
|------|------|----------|--------|
| **用户导入** | 用户上传 Excel/Word/Markdown 格式题库 | Web UI 批量导入 | P0 |
| **API 采集** | 从公开题库网站爬取（如考试官网） | 爬虫 + 解析器 | P1 |
| **手动创建** | 通过 Web UI 单题录入 | 表单录入 | P0 |
| **AI 生成** | 基于知识文档自动生成题目 | AI 模型生成 | P1 |
| **第三方导入** | 导入现有题库系统数据 | API/文件导入 | P2 |

#### 题库数据结构

```python
class Question(Base):
    __tablename__ = "questions"
    
    id: int = Column(Integer, primary_key=True)
    bank_id: int = Column(Integer, ForeignKey("question_banks.id"))
    
    # 题目内容
    content: Text = Column(Text)              # 题干
    question_type: str = Column(String(20))   # single/multi/true_false/essay
    options: JSON = Column(JSON)              # 选项 [{"A": "..."}, {"B": "..."}]
    answer: JSON = Column(JSON)               # 答案 {"correct": ["A"], "explanation": "..."}
    
    # 元数据
    difficulty: str = Column(String(10))      # easy/medium/hard
    tags: List[str] = Column(JSON)            # 标签
    score: int = Column(Integer, default=1)   # 分值
    
    # 向量嵌入（用于相似题检索）
    embedding: Vector = Column(Vector(1536))
    
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, onupdate=datetime.utcnow)


class QuestionBank(Base):
    __tablename__ = "question_banks"
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    name: str = Column(String(100))           # 题库名称
    description: Text = Column(Text)          # 描述
    subject: str = Column(String(50))         # 科目/领域
    question_count: int = Column(Integer, default=0)
    is_public: bool = Column(Boolean, default=False)
```

#### 题库目录结构

```
data/
└── question_banks/
    ├── bec_business/                    # BEC 商务英语题库
    │   ├── beginner/                    # 初级
    │   │   ├── reading.json
    │   │   ├── listening.json
    │   │   └── writing.json
    │   ├── intermediate/                # 中级
    │   └── advanced/                    # 高级
    ├── travel_guide/                    # 旅游攻略题库
    └── custom/                          # 用户自定义题库
```

---

### 11.2 知识库来源

知识库是非结构化/半结构化知识，用于 RAG 检索增强。

#### 来源渠道

| 来源 | 描述 | 获取方式 | 优先级 |
|------|------|----------|--------|
| **文档上传** | 用户上传 PDF/Word/Markdown | Web UI 上传 + 解析 | P0 |
| **网页采集** | 爬取指定网站内容 | 爬虫 + 正文提取 | P0 |
| **API 同步** | 从 Notion/语雀/飞书同步 | API 集成 | P1 |
| **数据库导入** | 从现有数据库导入 | ETL 工具 | P2 |
| **AI 生成** | 基于主题自动生成知识 | AI 模型生成 | P2 |

---

### 11.2.1 网页采集技术详解

#### 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| **HTTP 客户端** | `httpx` (异步) | 高性能，支持 HTTP/2 |
| **HTML 解析** | `BeautifulSoup4` + `lxml` | 快速解析，支持 CSS 选择器 |
| **浏览器自动化** | `Playwright` | 处理 JS 渲染、反爬 |
| **反爬绕过** | `fake-useragent` + 代理 | User-Agent 轮换 |
| **任务队列** | `Celery` + Redis | 分布式爬取 |

#### 爬虫架构

```python
# src/plugins/crawler/base_crawler.py
class BaseCrawler:
    """基础爬虫框架"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(config.requests_per_second)
    
    def _create_session(self) -> httpx.AsyncClient:
        """创建 HTTP 会话（带重试和代理）"""
        transport = httpx.AsyncHTTPTransport(
            retries=3,
            verify=False,  # 可选：忽略 SSL 验证
        )
        
        return httpx.AsyncClient(
            transport=transport,
            timeout=httpx.Timeout(30.0),
            headers={
                "User-Agent": fake_useragent.UserAgent().random,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
            proxy=self.config.proxy_url if self.config.use_proxy else None
        )
    
    async def crawl(self, start_urls: List[str]) -> AsyncIterator[Page]:
        """爬取入口"""
        visited = set()
        queue = asyncio.Queue()
        
        for url in start_urls:
            await queue.put(url)
        
        while not queue.empty():
            url = await queue.get()
            
            if url in visited or not self._should_crawl(url):
                continue
            
            visited.add(url)
            
            # 速率限制
            await self.rate_limiter.wait()
            
            # 获取页面
            page = await self._fetch(url)
            if page:
                yield page
                
                # 提取新链接
                new_urls = self._extract_links(page)
                for new_url in new_urls:
                    await queue.put(new_url)
    
    async def _fetch(self, url: str) -> Optional[Page]:
        """获取单个页面"""
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            
            # 检测编码
            encoding = response.apparent_encoding or 'utf-8'
            html = response.content.decode(encoding, errors='ignore')
            
            # 解析 HTML
            soup = BeautifulSoup(html, 'lxml')
            
            # 提取正文
            content = self._extract_content(soup, url)
            
            return Page(
                url=url,
                html=html,
                title=self._extract_title(soup),
                content=content,
                metadata=self._extract_metadata(soup, url)
            )
        
        except Exception as e:
            logger.error(f"爬取失败 {url}: {e}")
            return None
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """提取正文内容（核心算法）"""
        
        # 策略 1: 使用 readability-lxml（类似浏览器阅读模式）
        try:
            from readability import Document
            doc = Document(soup.prettify())
            return doc.summary()
        except:
            pass
        
        # 策略 2: 基于密度和分数的启发式算法
        content_nodes = []
        
        # 移除无用标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # 遍历所有段落
        for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
            text = p.get_text(strip=True)
            if len(text) > 50:  # 过滤太短的
                score = self._calculate_node_score(p)
                if score > 0.6:  # 阈值
                    content_nodes.append((score, text))
        
        # 按分数排序，取 top
        content_nodes.sort(key=lambda x: x[0], reverse=True)
        
        # 合并内容
        return '\n\n'.join([text for score, text in content_nodes[:20]])
    
    def _calculate_node_score(self, node) -> float:
        """计算节点质量分数"""
        score = 0.0
        
        text = node.get_text(strip=True)
        text_len = len(text)
        
        # 文本长度适中（100-2000 字）
        if 100 < text_len < 2000:
            score += 0.3
        
        # 包含标点符号（说明是正文）
        punctuation_ratio = len(re.findall(r'[,.!?.,]', text)) / max(text_len, 1)
        if 0.05 < punctuation_ratio < 0.3:
            score += 0.2
        
        # 标签类型权重
        if node.name in ['p', 'article', 'section']:
            score += 0.3
        elif node.name in ['h1', 'h2', 'h3']:
            score += 0.2
        
        # class/id 包含 content/article/post 等关键词
        class_str = ' '.join(node.get('class', [])) + ' ' + node.get('id', '')
        if any(kw in class_str.lower() for kw in ['content', 'article', 'post', 'main']):
            score += 0.2
        
        return score
    
    def _extract_links(self, page: Page) -> List[str]:
        """提取页面链接"""
        soup = BeautifulSoup(page.html, 'lxml')
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            
            # 转绝对路径
            full_url = urljoin(page.url, href)
            
            # 过滤：同域名、符合规则
            if self._should_follow(full_url):
                links.append(full_url)
        
        return links[:50]  # 限制数量
```

#### 反爬策略

```python
# src/plugins/crawler/anti_bot.py
class AntiBotProtection:
    """反爬虫绕过"""
    
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.proxies = self._load_proxies()
        self.cookies = {}
    
    def _load_user_agents(self) -> List[str]:
        """加载 User-Agent 池"""
        return [
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
            # Chrome macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ...",
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 ...",
        ]
    
    def get_random_headers(self) -> dict:
        """随机请求头"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
    
    async def handle_cloudflare(self, url: str) -> str:
        """处理 Cloudflare 防护（使用 Playwright）"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                user_agent=self.get_random_headers()["User-Agent"],
                viewport={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")
            
            # 等待 JS 渲染
            await page.wait_for_timeout(3000)
            
            html = await page.content()
            await browser.close()
            
            return html
    
    def rotate_proxy(self):
        """轮换代理"""
        # 从代理池获取新代理
        pass
```

#### 分布式爬取

```python
# src/plugins/crawler/distributed_crawler.py
from celery import Celery

app = Celery('crawler', broker='redis://localhost:6379/0')

@app.task(bind=True, max_retries=3)
def crawl_url(self, url: str, crawler_id: str):
    """分布式爬取任务"""
    try:
        crawler = CrawlerFactory.get(crawler_id)
        page = crawler.fetch(url)
        
        if page:
            # 保存到数据库
            save_page(page)
            
            # 发现新链接，分发新任务
            for link in page.links[:20]:
                crawl_url.delay(link, crawler_id)
    
    except Exception as e:
        # 重试
        raise self.retry(exc=e, countdown=60)
```

####  robots.txt 遵守

```python
# src/plugins/crawler/robots_parser.py
from urllib.robotparser import RobotFileParser

class RobotsChecker:
    """robots.txt 检查器"""
    
    def __init__(self):
        self.parsers: Dict[str, RobotFileParser] = {}
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """检查是否允许爬取"""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # 缓存 parsers
        if base_url not in self.parsers:
            robots_url = f"{base_url}/robots.txt"
            parser = RobotFileParser()
            try:
                parser.set_url(robots_url)
                parser.read()
                self.parsers[base_url] = parser
            except:
                # 没有 robots.txt，默认允许
                return True
        
        return self.parsers[base_url].can_fetch(user_agent, url)
```

#### 采集配置示例

```yaml
# config/crawlers.yaml
crawlers:
  bec_english:
    name: "BEC 英语学习网站"
    start_urls:
      - "https://www.bec.com.cn/grammar"
      - "https://www.bec.com.cn/vocabulary"
    allowed_domains:
      - "bec.com.cn"
    rate_limit:
      requests_per_second: 2
      delay_between_requests: 0.5
    anti_bot:
      rotate_user_agent: true
      use_proxy: false
      handle_cloudflare: true
    content_rules:
      extract_by_css:
        - "article.content"
        - "div.post-body"
      remove_by_css:
        - "div.advertisement"
        - "div.sidebar"
        - "div.comments"
    quality_filter:
      min_word_count: 200
      max_word_count: 5000
      require_images: false
    schedule:
      cron: "0 3 * * *"  # 每天凌晨 3 点
```

---

### 11.2.2 PDF/Word 文档解析技术

#### 技术选型对比

| 格式 | 库 | 优点 | 缺点 | 选用 |
|------|------|------|------|------|
| **PDF** | `PyMuPDF` (fitz) | 速度极快，支持文本+图片 | 商业许可需注意 | ✅ 主选 |
| **PDF** | `pdfplumber` | 表格提取好 | 速度慢 | 备选 |
| **PDF** | `pymupdf4llm` | 输出 Markdown 格式 | 较新库 | 推荐 |
| **Word** | `python-docx` | 官方库，稳定 | 仅支持.docx | ✅ 主选 |
| **Word** | `textract` | 支持旧.doc | 依赖多 | 备选 |

#### PDF 解析实现

```python
# src/utils/parsers/pdf_parser.py
import fitz  # PyMuPDF
from typing import List, Tuple

class PDFParser:
    """PDF 解析器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.use_llm = self.config.get('use_llm', False)  # 是否用 AI 增强
    
    async def parse(self, file_path: str) -> List[KnowledgeChunk]:
        """解析 PDF 文件"""
        chunks = []
        
        # 打开 PDF
        doc = fitz.open(file_path)
        
        for page_num, page in enumerate(doc, 1):
            # 策略 1: 直接提取文本（最快）
            text = page.get_text("text")
            
            # 策略 2: 结构化提取（保留标题层级）
            blocks = self._extract_blocks(page)
            
            # 策略 3: 表格提取
            tables = self._extract_tables(page)
            
            # 策略 4: 图片提取（可选）
            if self.config.get('extract_images'):
                images = self._extract_images(page)
            
            # 分块处理
            page_chunks = self._split_into_chunks(
                text=blocks,
                page_num=page_num,
                source=file_path
            )
            
            chunks.extend(page_chunks)
        
        doc.close()
        return chunks
    
    def _extract_blocks(self, page) -> List[dict]:
        """提取结构化块（标题、段落、列表）"""
        blocks = []
        
        # 获取文本块（带坐标和字体信息）
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if block["type"] != 0:  # 0=文本，1=图片
                continue
            
            block_info = {
                "text": "",
                "level": 0,  # 标题层级
                "type": "paragraph",
                "bbox": block["bbox"]
            }
            
            for line in block["lines"]:
                line_text = ""
                font_sizes = []
                
                for span in line["spans"]:
                    line_text += span["text"]
                    font_sizes.append(span["size"])
                
                # 判断是否为标题（字体大小）
                avg_font_size = sum(font_sizes) / len(font_sizes)
                if avg_font_size > 16:
                    block_info["type"] = "heading"
                    block_info["level"] = 1
                elif avg_font_size > 14:
                    block_info["type"] = "heading"
                    block_info["level"] = 2
                elif avg_font_size > 12:
                    block_info["type"] = "heading"
                    block_info["level"] = 3
                else:
                    block_info["type"] = "paragraph"
                
                block_info["text"] += line_text + "\n"
            
            if block_info["text"].strip():
                blocks.append(block_info)
        
        return blocks
    
    def _extract_tables(self, page) -> List[List[List[str]]]:
        """提取表格"""
        tables = page.find_tables()
        return [table.extract() for table in tables]
    
    def _extract_images(self, page) -> List[dict]:
        """提取图片"""
        images = []
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = page.parent.extract_image(xref)
                images.append({
                    "index": img_index,
                    "image": base_image["image"],
                    "ext": base_image["ext"],
                    "bbox": img  # 位置
                })
            except:
                pass
        
        return images
    
    def _split_into_chunks(self, text: str, page_num: int, source: str) -> List[KnowledgeChunk]:
        """将文本分块"""
        chunks = []
        
        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        chunk_num = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果当前块 + 新段落超过阈值，保存当前块
            if len(current_chunk) + len(para) > 800:
                if current_chunk:
                    chunks.append(KnowledgeChunk(
                        content=current_chunk,
                        title=f"第{page_num}页 - 块{chunk_num}",
                        source=source,
                        page_number=page_num,
                        metadata={"chunk_index": chunk_num}
                    ))
                    chunk_num += 1
                
                # 保留部分重叠
                overlap = current_chunk[-100:] if len(current_chunk) > 100 else ""
                current_chunk = overlap + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # 保存最后一块
        if current_chunk.strip():
            chunks.append(KnowledgeChunk(
                content=current_chunk,
                title=f"第{page_num}页 - 块{chunk_num}",
                source=source,
                page_number=page_num,
                metadata={"chunk_index": chunk_num}
            ))
        
        return chunks
```

#### Word 解析实现

```python
# src/utils/parsers/word_parser.py
from docx import Document
from docx.oxml.ns import qn

class WordParser:
    """Word 文档解析器"""
    
    async def parse(self, file_path: str) -> List[KnowledgeChunk]:
        """解析 Word 文件"""
        doc = Document(file_path)
        chunks = []
        current_chunk = ""
        chunk_num = 0
        
        # 遍历所有段落
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            # 判断样式（标题/正文）
            style_name = para.style.name if para.style else ""
            
            # 添加标记
            if 'Heading 1' in style_name or para.style.name == '标题 1':
                prefix = "# "
            elif 'Heading 2' in style_name or para.style.name == '标题 2':
                prefix = "## "
            elif 'Heading 3' in style_name or para.style.name == '标题 3':
                prefix = "### "
            else:
                prefix = ""
            
            formatted_text = f"{prefix}{text}\n\n"
            
            # 分块逻辑
            if len(current_chunk) + len(formatted_text) > 800:
                if current_chunk:
                    chunks.append(KnowledgeChunk(
                        content=current_chunk,
                        title=f"块{chunk_num}",
                        source=file_path,
                        metadata={"chunk_index": chunk_num}
                    ))
                    chunk_num += 1
                
                current_chunk = formatted_text
            else:
                current_chunk += formatted_text
        
        # 最后一块
        if current_chunk.strip():
            chunks.append(KnowledgeChunk(
                content=current_chunk,
                title=f"块{chunk_num}",
                source=file_path,
                metadata={"chunk_index": chunk_num}
            ))
        
        # 提取表格
        for table in doc.tables:
            table_text = self._table_to_markdown(table)
            chunks.append(KnowledgeChunk(
                content=table_text,
                title="表格",
                source=file_path,
                metadata={"type": "table"}
            ))
        
        return chunks
    
    def _table_to_markdown(self, table) -> str:
        """表格转 Markdown"""
        markdown = []
        
        for i, row in enumerate(table.rows):
            cells = [cell.text.strip() for cell in row.cells]
            markdown.append("| " + " | ".join(cells) + " |")
            
            if i == 0:
                markdown.append("| " + " | ".join(["---"] * len(cells)) + " |")
        
        return "\n".join(markdown)
```

#### AI 增强解析（高级功能）

```python
# src/utils/parsers/ai_enhanced_parser.py
class AIEnhancedParser:
    """AI 增强解析器 - 用 LLM 理解文档结构"""
    
    def __init__(self, llm: AIProvider):
        self.llm = llm
    
    async def parse_with_understanding(self, text: str) -> ParsedDocument:
        """用 AI 理解文档结构"""
        prompt = f"""分析以下文档内容，提取结构化信息：

【文档内容】
{text[:8000]}  # 限制长度

请返回 JSON 格式：
{{
    "title": "文档标题",
    "summary": "200 字摘要",
    "sections": [
        {{"heading": "章节标题", "content": "内容", "level": 1}}
    ],
    "key_points": ["关键点 1", "关键点 2"],
    "entities": ["实体 1", "实体 2"],
    "topics": ["主题 1", "主题 2"]
}}
"""
        response = await self.llm.generate(prompt, json_mode=True)
        return ParsedDocument(**json.loads(response))
```

---

### 11.3 向量数据库选型对比

#### 候选方案对比

| 方案 | 类型 | 优点 | 缺点 | 适用场景 | 推荐度 |
|------|------|------|------|----------|--------|
| **ChromaDB** | 嵌入式 | 轻量、无需服务器、API 简单 | 性能一般、不支持分布式 | 开发/小规模 (<100 万向量) | ⭐⭐⭐⭐ |
| **Qdrant** | 独立服务 | 性能强、支持过滤、开源 | 需要独立部署 | 生产环境 | ⭐⭐⭐⭐⭐ |
| **pgvector** | PG 扩展 | 与业务库一体、SQL 友好 | 性能中等、运维复杂 | 已有 PG 集群 | ⭐⭐⭐⭐ |
| **阿里云 DashScope** | 云服务 | 免运维、弹性扩容、阿里云集成 | 成本高、数据出域 | 阿里云部署 | ⭐⭐⭐⭐ |
| **Milvus** | 独立服务 | 超大规模、性能强 | 架构复杂、运维重 | 千万级向量 | ⭐⭐⭐ |
| **Weaviate** | 独立服务 | 内置分类、GraphQL | 学习成本高 | 特殊需求 | ⭐⭐⭐ |

#### 详细对比

##### 1. ChromaDB（开发首选）

```python
# 安装
pip install chromadb

# 使用示例
import chromadb
from chromadb.config import Settings

# 本地持久化
client = chromadb.PersistentClient(path="./chroma_data")

# 创建集合
collection = client.get_or_create_collection(
    name="knowledge",
    metadata={"hnsw:space": "cosine"}  # 余弦相似度
)

# 添加向量
collection.add(
    ids=["doc_1", "doc_2"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["内容 1", "内容 2"],
    metadatas=[{"source": "file.pdf"}, {"source": "web"}]
)

# 查询
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],
    n_results=5,
    where={"source": "file.pdf"}  # 过滤
)
```

**性能指标：**
- 查询延迟：P95 ~50ms (10 万向量)
- 内存占用：~1GB (100 万向量)
- 写入速度：~1000 向量/秒

---

##### 2. Qdrant（生产首选）

```python
# 安装
pip install qdrant-client

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue

# 连接（本地或云端）
client = QdrantClient(host="localhost", port=6333)
# 或 QdrantClient(url="https://xxx.qdrant.tech", api_key="xxx")

# 创建集合
client.create_collection(
    collection_name="knowledge",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# 添加向量（支持批量）
client.upsert(
    collection_name="knowledge",
    points=[
        {
            "id": 1,
            "vector": [0.1, 0.2, ...],
            "payload": {"source": "file.pdf", "page": 1}
        }
    ]
)

# 带过滤的查询
results = client.search(
    collection_name="knowledge",
    query_vector=[0.15, 0.25, ...],
    query_filter=Filter(
        must=[
            FieldCondition(key="source", match=MatchValue(value="file.pdf"))
        ]
    ),
    limit=5
)
```

**性能指标：**
- 查询延迟：P95 ~20ms (100 万向量)
- 内存占用：~500MB (100 万向量，HNSW 索引)
- 写入速度：~5000 向量/秒
- 支持：分布式、分片、复制

**Docker 部署：**
```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

---

##### 3. pgvector（PostgreSQL 扩展）

```python
# 安装扩展
# ALTER DATABASE agent SET search_path TO "$user", public, vector;
# CREATE EXTENSION IF NOT EXISTS vector;

from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    embedding = Column(Vector(1536))  # 向量列

# 创建索引（HNSW）
# CREATE INDEX ON knowledge_chunks USING hnsw (embedding vector_cosine_ops);

# 查询
from sqlalchemy import text
results = session.execute(
    text("""
        SELECT id, content, 
               embedding <=> :query_embedding AS similarity
        FROM knowledge_chunks
        ORDER BY similarity
        LIMIT 5
    """),
    {"query_embedding": [0.15, 0.25, ...]}
)
```

**性能指标：**
- 查询延迟：P95 ~30ms (100 万向量)
- 优势：与业务数据同一数据库，JOIN 查询方便
- 劣势：向量操作会占用 PG 资源

---

##### 4. 阿里云 DashScope（云服务）

```python
# 阿里云向量检索服务
from dashscope import VectorDB

# 创建实例
client = VectorDB(api_key="sk-xxx")

# 创建集合
client.create_collection(
    name="knowledge",
    dimension=1536,
    metric="cosine"
)

# 添加向量
client.add_documents(
    collection_name="knowledge",
    documents=[
        {"id": "1", "vector": [...], "metadata": {"source": "file.pdf"}}
    ]
)

# 查询
results = client.query(
    collection_name="knowledge",
    query_vector=[...],
    top_k=5
)
```

**成本估算（阿里云）：**
- 存储：¥0.0035/GB/小时
- 查询：¥0.001/千次
- 100 万向量 (~1GB)：约 ¥2.5/天

---

#### 最终选型建议

| 阶段 | 推荐方案 | 理由 |
|------|----------|------|
| **开发阶段** | ChromaDB (本地) | 零配置，快速启动 |
| **测试阶段** | Qdrant (Docker) | 接近生产环境 |
| **生产阶段** | Qdrant Cloud 或 阿里云 DashScope | 免运维，高可用 |
| **已有 PG** | pgvector | 减少组件，降低运维 |

#### 封装抽象层

```python
# src/core/vector_store.py - 统一接口
from abc import ABC, abstractmethod

class VectorStore(ABC):
    """向量存储抽象接口"""
    
    @abstractmethod
    async def add(self, ids: List[str], embeddings: List[List[float]], 
                  documents: List[str], metadatas: List[dict]):
        pass
    
    @abstractmethod
    async def query(self, query_embedding: List[float], k: int, 
                    filters: dict = None) -> List[QueryResult]:
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]):
        pass

class ChromaVectorStore(VectorStore):
    """ChromaDB 实现"""
    ...

class QdrantVectorStore(VectorStore):
    """Qdrant 实现"""
    ...

# 工厂模式
def create_vector_store(config: dict) -> VectorStore:
    if config["type"] == "chroma":
        return ChromaVectorStore(config["path"])
    elif config["type"] == "qdrant":
        return QdrantVectorStore(config["url"])
    elif config["type"] == "pgvector":
        return PGVectorStore(config["database_url"])
```

---

### 11.4 单机部署架构（零额外成本）

#### 现有资源

| 资源 | 配置 | 用途 |
|------|------|------|
| **阿里云 ECS** | 2 核 2G 40G 硬盘 | 应用 + 数据库 + 向量库 |
| **现有服务** | 函数计算 FC（包年包月） | 备用/异步任务 |
| **OSS** | 按量付费 | 文件存储（可选） |

**额外成本：¥0/月** （仅 OSS 按实际使用付费）

---

#### 架构图

```
┌─────────────────────────────────────────────┐
│          阿里云 ECS (2 核 2G 40G)             │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │   Docker Compose                       │  │
│  │                                        │  │
│  │  ┌─────────────┐  ┌─────────────────┐ │  │
│  │  │  FastAPI    │  │   SQLite        │ │  │
│  │  │  (应用服务)  │  │   (数据库)      │ │  │
│  │  │  8000 端口   │  │   本地文件       │ │  │
│  │  └─────────────┘  └─────────────────┘ │  │
│  │                                        │  │
│  │  ┌─────────────┐  ┌─────────────────┐ │  │
│  │  │  ChromaDB   │  │   本地文件系统   │ │  │
│  │  │  (向量库)   │  │   (知识/题库)    │ │  │
│  │  │  嵌入式     │  │   ./data/        │ │  │
│  │  └─────────────┘  └─────────────────┘ │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  外网访问：http://ECS 公网 IP:8000           │
└─────────────────────────────────────────────┘
```

---

#### 技术选型（轻量级）

| 组件 | 方案 | 理由 |
|------|------|------|
| **数据库** | SQLite | 零配置、单文件、无需独立服务 |
| **向量库** | ChromaDB (持久化模式) | 轻量、嵌入式、内存占用低 |
| **缓存** | 内存缓存 (functools.lru_cache) | 无需 Redis，够用 |
| **Web 服务器** | Uvicorn + Gunicorn | 轻量高效 |
| **进程管理** | Systemd 或 Supervisor | 系统级守护进程 |

---

#### 部署配置

##### 1. Docker Compose（推荐）

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    container_name: agent-platform
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data          # 数据持久化
      - ./logs:/app/logs          # 日志
      - ./config:/app/config      # 配置文件
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///app/data/agent.db
      - CHROMA_PERSIST_DIR=/app/data/chroma
      - QWEN_API_KEY=${QWEN_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LOG_LEVEL=INFO
    restart: unless-stopped
    networks:
      - app_network
    
    # 资源限制（2 核 2G 合理分配）
    deploy:
      resources:
        limits:
          cpus: '1.5'     # 最多 1.5 核
          memory: 1.5G    # 最多 1.5G 内存

  # 可选：定时任务（爬虫）
  crawler:
    build: .
    container_name: agent-crawler
    command: python -m src.tasks.crawler_scheduler
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///app/data/agent.db
      - CHROMA_PERSIST_DIR=/app/data/chroma
    restart: unless-stopped
    networks:
      - app_network
    # 只在需要时运行，不占用常驻资源
    profiles:
      - crawler

networks:
  app_network:
    driver: bridge

volumes:
  data:
  logs:
```

##### 2. Systemd 部署（无 Docker）

```ini
# /etc/systemd/system/agent-platform.service
[Unit]
Description=AI Agent Platform
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-agent-platform
Environment="PATH=/home/ubuntu/ai-agent-platform/venv/bin"
ExecStart=/home/ubuntu/ai-agent-platform/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# 资源限制
LimitNOFILE=65535
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable agent-platform
sudo systemctl start agent-platform
sudo systemctl status agent-platform
```

---

#### 数据库配置（SQLite）

```python
# config/database.yaml
database:
  url: sqlite+aiosqlite:///./data/agent.db
  
  # 优化配置（SQLite 性能）
  connect_args:
    timeout: 30
    check_same_thread: false
  
  # 连接池
  pool_size: 10          # SQLite 不需要大连接池
  max_overflow: 5
  pool_recycle: 3600
  
  # WAL 模式（提高并发）
  pragma:
    journal_mode: WAL
    synchronous: NORMAL
    cache_size: 10000
```

**SQLite 优化脚本：**
```python
# src/utils/db_optimize.py
async def optimize_sqlite(db_path: str):
    """优化 SQLite 性能"""
    async with aiosqlite.connect(db_path) as db:
        # 启用 WAL 模式
        await db.execute("PRAGMA journal_mode=WAL")
        # 提高缓存
        await db.execute("PRAGMA cache_size=10000")
        # 异步提交
        await db.execute("PRAGMA synchronous=NORMAL")
        # 定期清理
        await db.execute("VACUUM")
```

---

#### 向量库配置（ChromaDB）

```python
# config/vector_store.yaml
vector_store:
  type: chroma
  persist_directory: ./data/chroma
  
  # 性能优化
  settings:
    anonymized_telemetry: false
    chroma_db_impl: duckdb+parquet  # 高性能后端
  
  # 集合配置
  collection:
    name: knowledge
    metadata:
      hnsw:space: cosine
```

**内存优化：**
```python
# ChromaDB 内存占用优化
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="./data/chroma",
    settings=Settings(
        # 限制内存使用
        memory_limit_gb=0.5,  # 最多 500MB
        # 禁用遥测
        anonymized_telemetry=False
    )
)
```

---

#### 文件存储方案

**方案 1：本地文件系统（零成本）**
```python
# config/storage.yaml
storage:
  type: local
  base_path: ./data/files
  
  # 目录结构
  # ./data/files/
  #   ├── knowledge/    # 知识库文件
  #   ├── question_banks/  # 题库文件
  #   └── uploads/      # 用户上传
```

**方案 2：阿里云 OSS（按量付费，可选）**
```python
# 仅当需要外部分享或备份时使用
storage:
  type: oss
  endpoint: oss-cn-hangzhou.aliyuncs.com
  bucket: agent-data
  access_key: ${OSS_ACCESS_KEY}
  secret_key: ${OSS_SECRET_KEY}
  
  # 成本：¥0.12/GB/月，10GB = ¥1.2/月
```

---

#### 资源监控

**内存占用预估：**
| 组件 | 内存占用 |
|------|----------|
| FastAPI 应用 | ~200MB |
| SQLite | ~50MB |
| ChromaDB (10 万向量) | ~300MB |
| 系统预留 | ~500MB |
| **总计** | **~1.1GB** (2G 够用) |

**CPU 使用预估：**
- 空闲：~5-10%
- 正常请求：~20-40%
- 爬虫/AI 生成：~80-100%（短时）

**监控脚本：**
```bash
#!/bin/bash
# scripts/monitor.sh

echo "=== 系统资源 ==="
free -h
echo ""
echo "=== CPU 使用 ==="
top -bn1 | grep "Cpu(s)"
echo ""
echo "=== 磁盘使用 ==="
df -h /
echo ""
echo "=== Docker 容器 ==="
docker stats --no-stream
```

---

#### 备份策略

**本地备份：**
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
cp ./data/agent.db ${BACKUP_DIR}/agent_db_${DATE}.db

# 备份向量库
tar -czf ${BACKUP_DIR}/chroma_${DATE}.tar.gz ./data/chroma

# 备份配置文件
tar -czf ${BACKUP_DIR}/config_${DATE}.tar.gz ./config

# 保留最近 7 天备份
find ${BACKUP_DIR} -name "*.db" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete

echo "备份完成：${DATE}"
```

**定时备份（Cron）：**
```bash
# crontab -e
0 3 * * * /home/ubuntu/ai-agent-platform/scripts/backup.sh
```

**可选：备份到 OSS**
```bash
# 备份后上传到 OSS（低成本冷备份）
ossutil cp ${BACKUP_DIR}/agent_db_${DATE}.db oss://agent-data/backups/
```

---

#### 性能优化建议

1. **数据库优化**
   - 启用 WAL 模式
   - 定期 VACUUM
   - 为常用查询创建索引

2. **向量库优化**
   - 限制集合大小（>50 万向量考虑分库）
   - 定期清理无用数据
   - 使用 HNSW 索引

3. **应用优化**
   - 启用 Gzip 压缩
   - 静态资源缓存
   - 异步处理耗时任务（爬虫、AI 生成）

4. **系统优化**
   - 增加 Swap（防止 OOM）
   - 调整文件描述符限制
   - 使用 TCP BBR 加速网络

---

#### 升级路径

**当资源不足时：**

| 瓶颈 | 症状 | 升级方案 | 成本 |
|------|------|----------|------|
| **内存不足** | OOM、频繁 Swap | ECS 升级到 4G | +¥200/月 |
| **CPU 不足** | 响应慢、排队 | ECS 升级到 4 核 | +¥200/月 |
| **磁盘不足** | 空间告急 | 增加云盘 100G | +¥20/月 |
| **向量库性能** | 检索慢 | 迁移到 Qdrant Cloud | +¥300/月 |

**渐进式升级：**
```
阶段 1（现在）: 2 核 2G 单机 → 零额外成本
阶段 2（1000 用户）: ECS 4 核 4G → +¥400/月
阶段 3（1 万用户）: 分离数据库 + Redis → +¥800/月
阶段 4（10 万用户）: 负载均衡 + 多实例 → +¥2000/月
```

---

### 11.5 质量监控仪表盘实现

#### 架构设计

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  数据采集   │ ──▶ │  数据存储   │ ──▶ │  数据展示   │
│  (埋点)     │     │  (数据库)   │     │  (仪表盘)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
  - API 埋点          - PostgreSQL        - Web UI
  - 质量评分          - TimescaleDB       - Grafana (可选)
  - 用户反馈          - Redis (实时)       - 实时刷新
```

#### 数据模型

```python
# src/models/metrics.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class QualityMetrics(Base):
    """质量指标（按天聚合）"""
    __tablename__ = "quality_metrics"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)  # 日期
    metric_type = Column(String(50))     # 指标类型
    
    # 采集统计
    total_collected = Column(Integer, default=0)      # 采集总数
    auto_passed = Column(Integer, default=0)          # 自动通过
    optimized = Column(Integer, default=0)            # 优化后通过
    manual_reviewed = Column(Integer, default=0)      # 人工审核
    rejected = Column(Integer, default=0)             # 拒绝
    
    # 质量统计
    avg_score = Column(Float, default=0.0)            # 平均分数
    score_90_plus = Column(Integer, default=0)        # 90-100 分数量
    score_85_89 = Column(Integer, default=0)          # 85-89 分数量
    score_80_84 = Column(Integer, default=0)          # 80-84 分数量
    score_70_79 = Column(Integer, default=0)          # 70-79 分数量
    score_below_70 = Column(Integer, default=0)       # <70 分数量
    
    # 来源统计
    top_sources = Column(JSON)                        # 高质量来源 TOP10
    
    # 拒绝原因
    rejection_reasons = Column(JSON)                  # 拒绝原因分布
    
    created_at = Column(DateTime, default=datetime.utcnow)


class UserFeedback(Base):
    """用户反馈"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, index=True)            # 知识片段 ID
    user_id = Column(Integer)
    feedback_type = Column(String(10))                # thumbs_up / thumbs_down
    comment = Column(Text)                            # 可选评论
    created_at = Column(DateTime, default=datetime.utcnow)


class RealTimeMetrics(Base):
    """实时指标（Redis 存储，内存表）"""
    # 实际存储在 Redis，这里是逻辑模型
    
    # key: metrics:realtime:{date}
    # fields:
    #   - requests_today: 今日请求数
    #   - avg_response_time: 平均响应时间
    #   - error_rate: 错误率
    #   - active_users: 活跃用户数
```

#### 数据采集埋点

```python
# src/middleware/metrics_middleware.py
from fastapi import Request
from datetime import datetime

class MetricsMiddleware:
    """指标采集中间件"""
    
    def __init__(self, app, redis_client, db_session):
        self.app = app
        self.redis = redis_client
        self.db = db_session
    
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                status = message['status']
                elapsed = time.time() - start_time
                
                # 记录指标
                await self._record_metric(status, elapsed)
            
            return await send(message)
        
        return await self.app(scope, receive, send_wrapper)
    
    async def _record_metric(self, status: int, elapsed: float):
        """记录请求指标"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Redis 自增（实时统计）
        await self.redis.incr(f"metrics:requests:{today}")
        await self.redis.incr(f"metrics:status:{status}:{today}")
        
        # 响应时间（用列表存储，计算 P95）
        await self.redis.lpush(f"metrics:response_time:{today}", elapsed)
        await self.redis.ltrim(f"metrics:response_time:{today}", 0, 9999)  # 保留最近 1 万条
        
        # 错误请求单独记录
        if status >= 400:
            await self.redis.incr(f"metrics:errors:{today}")
```

#### 质量评分埋点

```python
# src/core/quality_scorer.py
class QualityScorer:
    async def score(self, chunk: KnowledgeChunk) -> QualityScore:
        score = await self._calculate_score(chunk)
        
        # 埋点：记录评分分布
        await self._record_score_metric(score)
        
        # 埋点：记录来源质量
        source = urlparse(chunk.source).netloc
        await self._record_source_metric(source, score)
        
        # 埋点：记录拒绝原因
        if score.total < 70:
            reason = self._determine_rejection_reason(score)
            await self._record_rejection_reason(reason)
        
        return score
    
    async def _record_score_metric(self, score: QualityScore):
        """记录分数分布"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if score.total >= 90:
            await self.redis.incr(f"metrics:score:90_plus:{today}")
        elif score.total >= 85:
            await self.redis.incr(f"metrics:score:85_89:{today}")
        elif score.total >= 80:
            await self.redis.incr(f"metrics:score:80_84:{today}")
        elif score.total >= 70:
            await self.redis.incr(f"metrics:score:70_79:{today}")
        else:
            await self.redis.incr(f"metrics:score:below_70:{today}")
```

#### 用户反馈埋点

```python
# src/api/routes/feedback.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/feedback")
async def submit_feedback(
    chunk_id: int,
    feedback_type: str,  # "thumbs_up" or "thumbs_down"
    comment: str = None,
    user_id: int = None
):
    """提交用户反馈"""
    feedback = UserFeedback(
        chunk_id=chunk_id,
        feedback_type=feedback_type,
        comment=comment,
        user_id=user_id
    )
    db.add(feedback)
    db.commit()
    
    # 埋点
    await redis.incr(f"metrics:feedback:{feedback_type}:{datetime.now().strftime('%Y-%m-%d')}")
    
    # 检查是否需要下架（5 次负面反馈）
    if feedback_type == "thumbs_down":
        negative_count = await count_negative_feedbacks(chunk_id)
        if negative_count >= 5:
            await auto_delist_chunk(chunk_id)
    
    return {"status": "ok"}
```

#### 仪表盘 API

```python
# src/api/routes/metrics.py
from fastapi import APIRouter
from sqlalchemy import func, extract

router = APIRouter()

@router.get("/metrics/overview")
async def get_overview_metrics(date: str = None):
    """概览指标"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # 从 Redis 获取实时数据
    requests_today = await redis.get(f"metrics:requests:{date}") or 0
    errors_today = await redis.get(f"metrics:errors:{date}") or 0
    
    # 计算平均响应时间
    response_times = await redis.lrange(f"metrics:response_time:{date}", 0, -1)
    avg_response_time = sum(map(float, response_times)) / len(response_times) if response_times else 0
    
    # 计算 P95 响应时间
    sorted_times = sorted(map(float, response_times))
    p95_index = int(len(sorted_times) * 0.95)
    p95_response_time = sorted_times[p95_index] if sorted_times else 0
    
    return {
        "date": date,
        "requests_today": int(requests_today),
        "errors_today": int(errors_today),
        "error_rate": errors_today / requests_today if requests_today else 0,
        "avg_response_time_ms": round(avg_response_time * 1000, 2),
        "p95_response_time_ms": round(p95_response_time * 1000, 2)
    }

@router.get("/metrics/quality")
async def get_quality_metrics(date: str = None):
    """质量指标"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # 从数据库获取聚合数据
    metrics = db.query(QualityMetrics).filter(
        extract('date', QualityMetrics.date) == date
    ).first()
    
    if not metrics:
        # 从 Redis 实时计算
        return await calculate_from_redis(date)
    
    return {
        "total_collected": metrics.total_collected,
        "pass_rate": (metrics.auto_passed + metrics.optimized) / metrics.total_collected if metrics.total_collected else 0,
        "avg_score": metrics.avg_score,
        "score_distribution": {
            "90-100": metrics.score_90_plus,
            "85-89": metrics.score_85_89,
            "80-84": metrics.score_80_84,
            "70-79": metrics.score_70_79,
            "<70": metrics.score_below_70
        },
        "rejection_reasons": metrics.rejection_reasons
    }

@router.get("/metrics/sources")
async def get_source_metrics(limit: int = 10):
    """来源质量排行"""
    # 查询高质量来源 TOP10
    sources = db.query(
        func.substring(KnowledgeChunk.source, 1, 100).label('domain'),
        func.avg(QualityScore.total).label('avg_score'),
        func.count().label('total')
    ).join(QualityScore).group_by('domain').order_by('avg_score DESC').limit(limit).all()
    
    return [
        {"domain": s.domain, "avg_score": round(s.avg_score, 2), "total": s.total}
        for s in sources
    ]

@router.get("/metrics/trend")
async def get_trend_metrics(days: int = 7):
    """趋势图数据"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    metrics = db.query(QualityMetrics).filter(
        QualityMetrics.date.between(start_date, end_date)
    ).order_by(QualityMetrics.date).all()
    
    return [
        {
            "date": m.date.strftime('%Y-%m-%d'),
            "total_collected": m.total_collected,
            "pass_rate": (m.auto_passed + m.optimized) / m.total_collected if m.total_collected else 0,
            "avg_score": m.avg_score
        }
        for m in metrics
    ]
```

#### Web UI 仪表盘

```vue
<!-- frontend/src/views/MetricsDashboard.vue -->
<template>
  <div class="metrics-dashboard">
    <!-- 概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="metric-card">
            <div class="label">今日请求</div>
            <div class="value">{{ metrics.requests_today }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="metric-card">
            <div class="label">平均响应时间</div>
            <div class="value">{{ metrics.avg_response_time_ms }} ms</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="metric-card">
            <div class="label">错误率</div>
            <div class="value">{{ (metrics.error_rate * 100).toFixed(2) }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="metric-card">
            <div class="label">采集通过率</div>
            <div class="value">{{ (metrics.pass_rate * 100).toFixed(2) }}%</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 质量分数分布 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>质量分数分布</template>
          <v-chart :option="scoreDistributionChart" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>拒绝原因分析</template>
          <v-chart :option="rejectionReasonsChart" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>7 天趋势</template>
          <v-chart :option="trendChart" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 来源排行 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>高质量来源 TOP10</template>
          <el-table :data="topSources">
            <el-table-column prop="domain" label="来源" />
            <el-table-column prop="avg_score" label="平均分" />
            <el-table-column prop="total" label="数量" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import VChart from 'vue-echarts'

const metrics = ref({})
const topSources = ref([])

// 定时刷新（每 30 秒）
onMounted(() => {
  fetchMetrics()
  setInterval(fetchMetrics, 30000)
})

async function fetchMetrics() {
  const [overview, quality, sources, trend] = await Promise.all([
    fetch('/api/metrics/overview').then(r => r.json()),
    fetch('/api/metrics/quality').then(r => r.json()),
    fetch('/api/metrics/sources').then(r => r.json()),
    fetch('/api/metrics/trend?days=7').then(r => r.json())
  ])
  
  metrics.value = { ...overview, ...quality }
  topSources.value = sources
  updateCharts(quality, trend)
}
</script>
```

#### Grafana 集成（可选）

```json
// grafana/dashboard.json
{
  "dashboard": {
    "title": "AI Agent Platform - 质量监控",
    "panels": [
      {
        "title": "今日请求量",
        "type": "stat",
        "targets": [{
          "query": "SELECT sum(value) FROM metrics_requests WHERE time > now() - 24h"
        }]
      },
      {
        "title": "质量分数趋势",
        "type": "graph",
        "targets": [{
          "query": "SELECT mean(avg_score) FROM quality_metrics WHERE time > now() - 7d GROUP BY time(1d)"
        }]
      }
    ]
  }
}
```

#### 告警规则

```yaml
# config/alerts.yaml
alerts:
  - name: 高错误率
    metric: error_rate
    threshold: 0.05  # 5%
    duration: 5m     # 持续 5 分钟
    action: send_notification
    
  - name: 响应时间过长
    metric: p95_response_time_ms
    threshold: 2000  # 2 秒
    duration: 10m
    action: send_notification
    
  - name: 采集质量下降
    metric: avg_score
    threshold: 75    # 低于 75 分
    duration: 1h
    action: send_notification
    
  - name: 负面反馈激增
    metric: feedback_thumbs_down_rate
    threshold: 0.1   # 10% 负面
    duration: 30m
    action: send_notification

notification:
  channels:
    - type: feishu
      webhook: ${FEISHU_WEBHOOK}
    - type: email
      recipients: [admin@example.com]
```

#### 知识库数据结构

```python
class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    name: str = Column(String(100))
    description: Text = Column(Text)
    type: str = Column(String(20))        # document/web/database
    
    created_at: datetime = Column(DateTime, default=datetime.utcnow)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    
    id: int = Column(Integer, primary_key=True)
    kb_id: int = Column(Integer, ForeignKey("knowledge_bases.id"))
    
    # 内容
    content: Text = Column(Text)          # 文本片段
    title: str = Column(String(200))      # 标题/章节名
    source: str = Column(String(500))     # 来源（文件路径/URL）
    page_number: int = Column(Integer)    # 页码（PDF）
    
    # 元数据
    metadata: JSON = Column(JSON)         # 额外元数据
    tags: List[str] = Column(JSON)
    
    # 向量嵌入
    embedding: Vector = Column(Vector(1536))
    
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
```

#### 知识库目录结构

```
data/
└── knowledge_bases/
    ├── bec_english/                     # BEC 英语知识库
    │   ├── textbooks/                   # 教材
    │   │   ├── bec_beginner.pdf
    │   │   └── bec_advanced.pdf
    │   ├── grammar/                     # 语法知识
    │   ├── vocabulary/                  # 词汇知识
    │   └── business_context/            # 商务背景知识
    ├── travel/                          # 旅游知识库
    │   ├── japan/
    │   └── europe/
    └── user_upload/                     # 用户上传
```

#### 文档解析流程

```python
# src/utils/document_parser.py
class DocumentParser:
    def __init__(self):
        self.parsers = {
            '.pdf': self._parse_pdf,
            '.docx': self._parse_docx,
            '.md': self._parse_markdown,
            '.txt': self._parse_text,
        }
    
    async def parse(self, file_path: str) -> List[KnowledgeChunk]:
        ext = Path(file_path).suffix.lower()
        parser = self.parsers.get(ext, self._parse_text)
        return await parser(file_path)
    
    async def _parse_pdf(self, file_path: str) -> List[KnowledgeChunk]:
        # 使用 PyMuPDF 或 pdfplumber 解析
        chunks = []
        doc = fitz.open(file_path)
        for page in doc:
            text = page.get_text()
            # 按段落分割
            paragraphs = self._split_into_paragraphs(text)
            for para in paragraphs:
                chunks.append(KnowledgeChunk(
                    content=para,
                    page_number=page.number,
                    source=file_path
                ))
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        # 智能分割：按段落、标题、列表等
        ...
```

---

### 11.3 RAG 实现方案

RAG（Retrieval-Augmented Generation）检索增强生成。

#### 架构设计

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户查询   │ ──▶ │  检索引擎   │ ──▶ │  相关文档   │
│  "BEC 考试   │     │  (向量检索)  │     │   片段      │
│   报名条件"  │     │             │     │  (Top 5)    │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   最终回答   │ ◀── │  AI 模型    │ ◀── │  增强提示   │
│  "BEC 报名   │     │  (生成回答)  │     │  (上下文 +  │
│   条件是..." │     │             │     │   查询)     │
└─────────────┘     └─────────────┘     └─────────────┘
```

#### 核心组件

```python
# src/core/rag_engine.py
class RAGEngine:
    def __init__(self, vector_store: VectorStore, llm: AIProvider):
        self.vector_store = vector_store
        self.llm = llm
        self.chunk_size = 500          # 分块大小
        self.chunk_overlap = 50        # 重叠大小
        self.top_k = 5                 # 检索数量
    
    async def query(self, question: str, kb_id: int = None) -> str:
        # 1. 生成查询嵌入
        query_embedding = await self._embed(question)
        
        # 2. 向量检索
        filters = {"kb_id": kb_id} if kb_id else {}
        chunks = await self.vector_store.similarity_search(
            query_embedding, 
            k=self.top_k,
            filters=filters
        )
        
        # 3. 重排序（可选，使用 Cross-Encoder）
        chunks = await self._rerank(question, chunks)
        
        # 4. 构建增强提示
        context = self._build_context(chunks)
        prompt = self._build_prompt(question, context)
        
        # 5. 生成回答
        response = await self.llm.generate(prompt)
        
        # 6. 添加引用来源
        response = self._add_citations(response, chunks)
        
        return response
    
    def _build_context(self, chunks: List[KnowledgeChunk]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[来源{i}] {chunk.source}\n{chunk.content}")
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        return f"""你是一个专业的助手。请根据以下资料回答问题。
如果资料中没有相关信息，请如实告知。

【参考资料】
{context}

【问题】
{question}

【回答】
"""
```

#### 向量存储方案

| 方案 | 描述 | 适用场景 | 优先级 |
|------|------|----------|--------|
| **ChromaDB** | 轻量级向量数据库，嵌入式 | 开发/小规模 | P0 |
| **Qdrant** | 专业向量数据库，支持过滤 | 生产环境 | P1 |
| **阿里云 DashScope** | 阿里云向量检索服务 | 阿里云部署 | P1 |
| **pgvector** | PostgreSQL 向量扩展 | 已有 PG 集群 | P2 |

#### 分块策略

```python
# src/utils/text_splitter.py
class TextSplitter:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str) -> List[str]:
        # 策略 1: 按段落分割（保持语义完整）
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 策略 2: 按标题分割（保持章节结构）
        # 策略 3: 固定大小分割（递归字符分割）
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size:
                chunks.append(current_chunk)
                # 保留重叠部分
                current_chunk = current_chunk[-self.chunk_overlap:] + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
```

#### 检索优化

```python
# 混合检索：向量 + 关键词
class HybridRetriever:
    def __init__(self, vector_store, bm25_index):
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.alpha = 0.7  # 向量检索权重
    
    async def search(self, query: str, k: int = 10) -> List[KnowledgeChunk]:
        # 向量检索
        vector_results = await self.vector_store.similarity_search(query, k=k*2)
        
        # 关键词检索 (BM25)
        bm25_results = self.bm25_index.search(query, k=k*2)
        
        # 融合排序 (RRF - Reciprocal Rank Fusion)
        fused = self._rrf_fusion(vector_results, bm25_results)
        
        return fused[:k]
```

#### RAG 评估指标

| 指标 | 描述 | 目标值 |
|------|------|--------|
| **检索准确率** | 检索到的文档相关性 | > 85% |
| **回答准确率** | 最终回答的正确性 | > 90% |
| **响应时间** | 端到端延迟 | P95 < 2s |
| **引用覆盖率** | 回答中有引用的比例 | > 80% |

---

### 11.4 知识质量保障机制

**核心问题：** 采集的知识如何确保质量？

#### 质量评分体系

参考 Prompt 评分经验，设计**三级质量分级**：

| 分数段 | 等级 | 处理方式 |
|--------|------|----------|
| **≥ 85 分** | 优秀 | 直接入库，标记为高质量 |
| **70-84 分** | 合格 | 需要优化后入库 |
| **< 70 分** | 不合格 | 直接丢弃 |

#### 质量评估维度

```python
# src/core/quality_scorer.py
class QualityScorer:
    """知识质量评分器"""
    
    def __init__(self, llm: AIProvider):
        self.llm = llm
        self.weights = {
            'relevance': 0.25,      # 相关性
            'accuracy': 0.25,       # 准确性
            'completeness': 0.20,   # 完整性
            'clarity': 0.15,        # 清晰度
            'timeliness': 0.15,     # 时效性
        }
    
    async def score(self, chunk: KnowledgeChunk) -> QualityScore:
        # 1. 自动规则检查（快速过滤）
        rule_score = self._rule_based_check(chunk)
        if rule_score < 60:
            return QualityScore(total=rule_score, auto_reject=True)
        
        # 2. AI 语义评分（详细评估）
        ai_score = await self._ai_semantic_score(chunk)
        
        # 3. 加权计算
        total = sum(ai_score[dim] * weight for dim, weight in self.weights.items())
        
        return QualityScore(
            total=total,
            dimensions=ai_score,
            auto_reject=False
        )
    
    def _rule_based_check(self, chunk: KnowledgeChunk) -> float:
        """基于规则的快速检查"""
        score = 100
        
        # 太短 → 信息不足
        if len(chunk.content) < 50:
            score -= 30
        
        # 太长 → 需要分割
        if len(chunk.content) > 2000:
            score -= 10
        
        # 包含乱码/特殊字符
        if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', chunk.content):
            score -= 20
        
        # 包含明显广告/导航文本
        if re.search(r'点击购买 | 立即注册 | 网站首页', chunk.content):
            score -= 25
        
        # 重复内容检测（简单哈希）
        if self._is_duplicate(chunk):
            score -= 40
        
        return max(0, score)
    
    async def _ai_semantic_score(self, chunk: KnowledgeChunk) -> dict:
        """AI 语义评分"""
        prompt = f"""请评估以下文本的质量，从 5 个维度打分（0-100）：

【文本】
{chunk.content}

【评分维度】
1. 相关性：与主题的相关程度
2. 准确性：信息是否准确可靠
3. 完整性：信息是否完整
4. 清晰度：表达是否清晰易懂
5. 时效性：信息是否过时

请以 JSON 格式返回：
{{
    "relevance": 分数,
    "accuracy": 分数,
    "completeness": 分数,
    "clarity": 分数,
    "timeliness": 分数,
    "reason": "评分理由"
}}
"""
        response = await self.llm.generate(prompt, json_mode=True)
        return json.loads(response)
```

#### 质量优化器

```python
# src/core/quality_optimizer.py
class QualityOptimizer:
    """知识质量优化器（针对 70-84 分的内容）"""
    
    def __init__(self, llm: AIProvider):
        self.llm = llm
        self.max_iterations = 3
    
    async def optimize(self, chunk: KnowledgeChunk) -> OptimizationResult:
        """优化知识片段，直到达到 85 分或达到最大迭代次数"""
        
        current_chunk = chunk
        history = []
        
        for i in range(self.max_iterations):
            # 1. 评分
            score = await self.scorer.score(current_chunk)
            
            if score.total >= 85:
                return OptimizationResult(
                    success=True,
                    chunk=current_chunk,
                    final_score=score.total,
                    iterations=i + 1
                )
            
            if score.total < 70:
                return OptimizationResult(
                    success=False,
                    reason="分数过低，无法优化",
                    final_score=score.total
                )
            
            # 2. 生成优化建议
            suggestions = await self._generate_suggestions(current_chunk, score)
            
            # 3. 执行优化
            optimized = await self._apply_optimization(current_chunk, suggestions)
            
            history.append({
                'iteration': i + 1,
                'score': score.total,
                'suggestions': suggestions
            })
            
            # 4. 检查是否有改进
            if optimized.content == current_chunk.content:
                break
            
            current_chunk = optimized
        
        # 最终评分
        final_score = await self.scorer.score(current_chunk)
        
        return OptimizationResult(
            success=final_score.total >= 80,
            chunk=current_chunk,
            final_score=final_score.total,
            iterations=len(history),
            history=history
        )
    
    async def _generate_suggestions(self, chunk: KnowledgeChunk, score: QualityScore) -> str:
        """生成优化建议"""
        weak_dims = [dim for dim, s in score.dimensions.items() if s < 80]
        
        prompt = f"""当前文本质量评分：{score.total} 分
薄弱维度：{', '.join(weak_dims)}

【原文本】
{chunk.content}

请提供具体的优化建议，帮助提升到 85 分以上。
聚焦于薄弱维度的改进。
"""
        return await self.llm.generate(prompt)
    
    async def _apply_optimization(self, chunk: KnowledgeChunk, suggestions: str) -> KnowledgeChunk:
        """应用优化建议"""
        prompt = f"""请根据以下建议优化文本：

【优化建议】
{suggestions}

【原文本】
{chunk.content}

【要求】
1. 保持核心信息不变
2. 提升表达清晰度
3. 补充缺失的关键信息
4. 去除冗余和无关内容
5. 确保信息准确

【优化后的文本】
"""
        optimized_content = await self.llm.generate(prompt)
        
        return KnowledgeChunk(
            content=optimized_content,
            title=chunk.title,
            source=chunk.source,
            metadata=chunk.metadata
        )
```

#### 去重机制

```python
# src/core/deduplication.py
class Deduplicator:
    """知识去重器"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.similarity_threshold = 0.95  # 相似度阈值
    
    async def is_duplicate(self, chunk: KnowledgeChunk) -> bool:
        """检查是否重复"""
        # 1. 精确去重（内容哈希）
        content_hash = hashlib.md5(chunk.content.encode()).hexdigest()
        if await self._exists_by_hash(content_hash):
            return True
        
        # 2. 语义去重（向量相似度）
        embedding = await self._embed(chunk.content)
        similar = await self.vector_store.similarity_search(
            embedding, 
            k=5,
            filters={"source": chunk.source}  # 同来源内去重
        )
        
        if similar and similar[0].similarity > self.similarity_threshold:
            return True
        
        return False
    
    async def _exists_by_hash(self, content_hash: str) -> bool:
        # 检查数据库中是否已存在相同哈希
        ...
```

#### 来源可信度评级

```python
# 网站可信度分级
SOURCE_CREDIBILITY = {
    # S 级 - 官方权威
    'S': {
        'domains': ['gov.cn', 'edu.cn', 'org.cn'],
        'base_score': 95,
        'auto_pass': True,
    },
    # A 级 - 知名平台
    'A': {
        'domains': ['zhihu.com', 'jianshu.com', 'csdn.net'],
        'base_score': 85,
        'auto_pass': False,
    },
    # B 级 - 一般网站
    'B': {
        'domains': ['*'],
        'base_score': 70,
        'auto_pass': False,
    },
    # C 级 - 低质量/黑名单
    'C': {
        'domains': ['content-farm.com', 'spam-site.net'],
        'base_score': 30,
        'auto_reject': True,
    },
}

def get_source_credibility(url: str) -> dict:
    """获取来源可信度评级"""
    domain = urlparse(url).netloc
    for level, config in SOURCE_CREDIBILITY.items():
        for pattern in config['domains']:
            if pattern == '*' or pattern in domain:
                return config
    return SOURCE_CREDIBILITY['B']
```

#### 人工审核流程

```python
# src/core/review_workflow.py
class ReviewWorkflow:
    """人工审核工作流"""
    
    def __init__(self):
        self.auto_pass_threshold = 85      # 自动通过
        self.auto_reject_threshold = 70    # 自动拒绝
        self.manual_review_threshold = 80  # 需要人工审核
    
    async def process(self, chunk: KnowledgeChunk) -> ReviewResult:
        # 1. 自动评分
        score = await self.scorer.score(chunk)
        
        # 2. 自动决策
        if score.total >= self.auto_pass_threshold:
            return ReviewResult(action='auto_pass', score=score)
        
        if score.total < self.auto_reject_threshold:
            return ReviewResult(action='auto_reject', score=score)
        
        # 3. 需要人工审核
        if score.total >= self.manual_review_threshold:
            # 创建审核任务
            review_task = await self._create_review_task(chunk, score)
            return ReviewResult(
                action='manual_review',
                score=score,
                task_id=review_task.id
            )
        
        # 4. 尝试优化后重新评分
        optimized = await self.optimizer.optimize(chunk)
        if optimized.success:
            return ReviewResult(action='auto_pass', score=optimized.final_score)
        else:
            return ReviewResult(action='auto_reject', score=optimized.final_score)
```

#### 质量监控仪表盘

```python
# 质量统计
class QualityMetrics:
    """质量监控指标"""
    
    async def get_daily_stats(self, date: str) -> dict:
        return {
            'total_collected': 1000,      # 采集总数
            'auto_passed': 650,           # 自动通过
            'optimized': 200,             # 优化后通过
            'manual_reviewed': 50,        # 人工审核
            'rejected': 100,              # 拒绝
            
            'avg_score': 82.5,            # 平均分数
            'score_distribution': {       # 分数分布
                '90-100': 150,
                '85-89': 300,
                '80-84': 200,
                '70-79': 250,
                '<70': 100
            },
            
            'top_sources': [              # 高质量来源
                {'domain': 'gov.cn', 'avg_score': 92},
                {'domain': 'zhihu.com', 'avg_score': 87},
            ],
            
            'rejection_reasons': {        # 拒绝原因分析
                'low_relevance': 40,
                'inaccurate': 30,
                'duplicate': 20,
                'other': 10
            }
        }
```

#### 持续优化闭环

```
采集 → 评分 → 优化 → 入库 → 用户反馈 → 重新评分 → 优化/下架
              ↑                                        │
              └────────────────────────────────────────┘
```

**用户反馈机制：**
- 👍 有用 → 加分，标记为高质量
- 👎 无用/错误 → 减分，触发重新审核
- 📝 纠错建议 → 记录并用于优化

**自动下架规则：**
- 连续收到 5 次负面反馈 → 自动下架
- 发现事实错误 → 立即下架并标记来源
- 信息过时（>2 年）→ 标记为"可能过时"

---

---

## 12. 实施步骤（优先级排序）

### 阶段 1：基础框架（1-2 周）

**目标：** 让系统能跑起来，支持基础对话

| 步骤 | 任务 | 产出 | 预计时间 |
|------|------|------|----------|
| 1.1 | 项目骨架搭建 | 目录结构、依赖配置、Docker 环境 | 1 天 |
| 1.2 | 数据库初始化 | 表结构、迁移脚本 | 1 天 |
| 1.3 | AI Provider 集成 | Qwen/DeepSeek 接入，能调用 API | 2 天 |
| 1.4 | 基础 Agent 引擎 | 简单对话循环（输入→AI→输出） | 2 天 |
| 1.5 | 短期记忆 | 会话上下文管理 | 1 天 |
| 1.6 | 基础 API | `/chat` 接口 | 1 天 |
| 1.7 | 简单 Web UI | 对话界面 | 2 天 |

**✅ MVP 验收：** 能打开网页，和 AI 进行多轮对话

---

### 阶段 2：知识库与 RAG（2-3 周）

**目标：** 实现知识采集、评分、检索

| 步骤 | 任务 | 产出 | 预计时间 |
|------|------|------|----------|
| 2.1 | 网页爬虫框架 | 支持指定网站采集 | 2 天 |
| 2.2 | 文档解析器 | PDF/Word/Markdown 解析 | 2 天 |
| 2.3 | 向量数据库集成 | ChromaDB 嵌入 | 1 天 |
| 2.4 | 文本分块策略 | 智能分割算法 | 1 天 |
| 2.5 | 质量评分器 | 规则检查 + AI 评分 | 2 天 |
| 2.6 | 质量优化器 | 自动优化 70-84 分内容 | 2 天 |
| 2.7 | RAG 检索引擎 | 向量检索 + 增强生成 | 3 天 |
| 2.8 | 去重机制 | 精确去重 + 语义去重 | 1 天 |

**✅ 验收：** 能采集网站内容，自动评分入库，RAG 检索回答

---

### 阶段 3：题库系统（1-2 周）

**目标：** 支持题库管理和测试功能

| 步骤 | 任务 | 产出 | 预计时间 |
|------|------|------|----------|
| 3.1 | 题库数据模型 | Question/QuestionBank 表 | 1 天 |
| 3.2 | 题库导入功能 | Excel/Markdown 批量导入 | 2 天 |
| 3.3 | AI 出题功能 | 基于知识自动生成题目 | 2 天 |
| 3.4 | 题库管理 UI | 查看/编辑/搜索题目 | 2 天 |
| 3.5 | 组卷功能 | 按难度/标签组卷 | 2 天 |

**✅ 验收：** 能导入题库，AI 自动出题，支持组卷

---

### 阶段 4：增强功能（2-3 周）

**目标：** 完善系统能力

| 步骤 | 任务 | 产出 | 预计时间 |
|------|------|------|----------|
| 4.1 | 长期记忆 | 持久化存储和检索 | 2 天 |
| 4.2 | 任务调度 | 定时任务、工作流 | 3 天 |
| 4.3 | 插件系统 | 插件加载机制 | 2 天 |
| 4.4 | 来源评级 | 网站可信度分级 | 1 天 |
| 4.5 | 人工审核流程 | 审核后台 | 2 天 |
| 4.6 | 质量监控仪表盘 | 统计数据可视化 | 2 天 |
| 4.7 | 用户反馈闭环 | 👍/👎反馈收集 | 1 天 |

**✅ 验收：** 完整的质量保障体系，可生产使用

---

### 阶段 5：生产优化（1-2 周）

**目标：** 性能、安全、部署

| 步骤 | 任务 | 产出 | 预计时间 |
|------|------|------|----------|
| 5.1 | 性能优化 | 缓存、索引、查询优化 | 2 天 |
| 5.2 | 安全加固 | 认证、授权、限流 | 2 天 |
| 5.3 | 日志监控 | 结构化日志、告警 | 2 天 |
| 5.4 | 阿里云部署 | ECS/RDS/Redis | 2 天 |
| 5.5 | API 文档 | OpenAPI/Swagger | 1 天 |

**✅ 验收：** 生产环境可用，99.5% 可用性

---

## 13. 立即开始（第一步）

**不要等完美设计，先跑起来！**

### 今日任务（Day 1）

```bash
# 1. 创建项目骨架
mkdir -p ai-agent-platform/{src/{core,providers,api,plugins,models,utils},tests,config,data}
cd ai-agent-platform

# 2. 初始化 Python 项目
python -m venv venv
source venv/bin/activate

# 3. 创建基础依赖
cat > requirements.txt <<EOF
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
aiosqlite==0.19.0
httpx==0.26.0
pydantic==2.5.3
pyyaml==6.0.1
loguru==0.7.2
python-dotenv==1.0.0
EOF

# 4. 创建 Docker Compose（开发环境）
cat > docker-compose.yml <<EOF
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///data/agent.db
      - QWEN_API_KEY=${QWEN_API_KEY}
EOF

# 5. 创建第一个文件：src/main.py
# FastAPI 入口，/health 接口

# 6. 运行测试
docker-compose up
curl http://localhost:8000/health
```

**目标：** 今天内让 `curl http://localhost:8000/health` 返回 `{"status": "ok"}`

---

## 14. 关键决策点

### 决策 1：先做题库还是先做知识库？

**建议：先做知识库（RAG）**

理由：
- 知识库更通用，可复用性强
- RAG 是核心能力，题库可以基于知识库生成
- 知识库采集 → 质量评分 → 入库 流程验证后，题库可以复用

### 决策 2：自己爬还是用 API？

**建议：混合策略**

| 场景 | 方案 |
|------|------|
| 有开放 API 的网站 | 优先用 API（稳定、合法） |
| 无 API 但允许爬虫 | 爬取（遵守 robots.txt） |
| 高质量付费内容 | 人工整理 + AI 辅助 |
| 冷启动 | AI 生成初始知识 |

### 决策 3：什么时候引入人工审核？

**建议：MVP 阶段全自动，第二阶段加入**

- 阶段 1：≥85 分自动入库，<85 分丢弃（快速迭代）
- 阶段 2：80-84 分进入人工审核队列（提高召回率）

---
