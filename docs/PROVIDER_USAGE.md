# Provider 使用指南

## 支持的 Provider 类型

### 1. OpenAI 兼容代理

支持所有 OpenAI API 兼容的代理服务，例如：
- **NovaCode** (https://ai.novacode.top)
- 其他 OpenAI 兼容代理

### 2. 直连 API（待实现）

- 通义千问（DashScope）
- DeepSeek
- Kimi（月之暗面）

---

## 配置方式

### 方式 1：YAML 配置文件

```yaml
# config/providers/novacode.yaml
provider:
  type: openai_proxy
  name: NovaCode
  
  options:
    baseURL: "https://ai.novacode.top/v1"
    apiKey: "${NOVACODE_API_KEY}"
    timeout: 120
    max_retries: 3
  
  models:
    gpt-5.4:
      name: "GPT-5.4"
      limit:
        context: 1050000  # 105 万 tokens！
        output: 128000
      variants:
        low: {}
        medium: {}
        high: {}
        xhigh: {}
```

**使用：**
```python
from src.providers import load_provider

provider = load_provider("config/providers/novacode.yaml")

# 或者自动加载所有配置
from src.providers import load_providers
providers = load_providers("config/providers")
novacode = providers["novacode"]
```

### 方式 2：代码配置

```python
from src.providers import (
    ProviderFactory, ProviderConfig, ProviderOptions,
    ModelConfig, ModelLimit
)

# 创建配置
config = ProviderConfig(
    options=ProviderOptions(
        baseURL="https://ai.novacode.top/v1",
        apiKey="sk-xxxxxxxx",
        timeout=120
    ),
    models={
        "gpt-5.4": ModelConfig(
            name="GPT-5.4",
            limit=ModelLimit(context=1050000, output=128000),
            variants={
                "low": {},
                "medium": {},
                "high": {},
                "xhigh": {}
            }
        )
    }
)

# 创建 Provider
provider = ProviderFactory.create(config, "openai_proxy")
```

---

## 使用示例

### 1. 基础对话

```python
from src.providers import load_provider, ChatMessage

provider = load_provider("config/providers/novacode.yaml")

# 构建消息
messages = [
    ChatMessage(role="system", content="你是一个专业的助手"),
    ChatMessage(role="user", content="你好，请介绍一下自己")
]

# 发送请求
response = await provider.chat(
    model="gpt-5.4",
    messages=messages,
    temperature=0.7
)

print(response.content)
```

### 2. 使用模型变体

```python
from src.providers import ModelVariant

# 使用高质量变体
response = await provider.chat(
    model="gpt-5.4",
    variant=ModelVariant.HIGH,  # low/medium/high/xhigh
    messages=messages
)

# 使用超高质量（适合复杂任务）
response = await provider.chat(
    model="gpt-5.4",
    variant=ModelVariant.XHIGH,
    messages=messages
)
```

### 3. 流式响应

```python
async for chunk in provider.chat_stream(
    model="codex-mini-latest",
    variant=ModelVariant.MEDIUM,
    messages=messages
):
    print(chunk, end="", flush=True)
```

### 4. 长文档分析（利用大上下文）

```python
# 读取长文档
with open("long_document.txt", "r") as f:
    document = f.read()

messages = [
    ChatMessage(role="user", content=f"请分析这份文档：\n\n{document}")
]

# 使用 gpt-5.4（105 万上下文）
response = await provider.chat(
    model="gpt-5.4",
    variant=ModelVariant.XHIGH,
    messages=messages,
    max_tokens=50000  # 可以输出 5 万 tokens！
)
```

### 5. 代码生成

```python
# 使用 Codex Mini（快速、便宜）
messages = [
    ChatMessage(role="user", content="写一个 Python 快速排序函数")
]

response = await provider.chat(
    model="codex-mini-latest",
    variant=ModelVariant.MEDIUM,
    messages=messages
)

print(response.content)
```

---

## 模型选择指南

| 模型 | 上下文 | 输出 | 变体 | 适用场景 |
|------|--------|------|------|----------|
| **gpt-5.4** | 105 万 | 12.8 万 | 4 档 | 超长文档分析、复杂推理 |
| **gpt-5.2** | 40 万 | 12.8 万 | 4 档 | 大型项目分析 |
| **gpt-5.3-codex** | 40 万 | 12.8 万 | 4 档 | 代码生成、审查 |
| **codex-mini-latest** | 20 万 | 10 万 | 3 档 | 快速代码生成、日常任务 |
| **gpt-5.1-codex-mini** | 40 万 | 12.8 万 | 3 档 | 平衡速度与质量 |

### 变体选择

| 变体 | 速度 | 质量 | 成本 | 适用场景 |
|------|------|------|------|----------|
| **low** | ⚡⚡⚡ | ⭐⭐ | 💰 | 快速测试、简单任务 |
| **medium** | ⚡⚡ | ⭐⭐⭐ | 💰💰 | 日常使用、平衡 |
| **high** | ⚡ | ⭐⭐⭐⭐ | 💰💰💰 | 重要任务、高质量要求 |
| **xhigh** | 🐌 | ⭐⭐⭐⭐⭐ | 💰💰💰💰 | 关键任务、极致质量 |

---

## API 接口使用

### 通过 Web API

```bash
# 基础对话
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "provider": "novacode",
    "model": "gpt-5.4",
    "variant": "high"
  }'

# 流式对话
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "写一首诗",
    "provider": "novacode",
    "model": "gpt-5.2",
    "variant": "medium"
  }'
```

---

## 添加新的 Provider

### 1. 创建 Provider 类

```python
# src/providers/my_provider.py
from .base import AIProvider, ChatRequest, ChatResponse

class MyProvider(AIProvider):
    async def chat(self, request: ChatRequest) -> ChatResponse:
        # 实现对话逻辑
        pass
    
    async def chat_stream(self, request: ChatRequest):
        # 实现流式逻辑
        pass
```

### 2. 注册 Provider

```python
# 在工厂中注册
ProviderFactory.register("my_provider", MyProvider)
```

### 3. 创建配置文件

```yaml
# config/providers/my_provider.yaml
provider:
  type: my_provider
  name: MyProvider
  
  options:
    baseURL: "https://api.myprovider.com"
    apiKey: "${MY_PROVIDER_API_KEY}"
  
  models:
    model-1:
      name: "Model 1"
      limit:
        context: 4096
        output: 2048
```

---

## 最佳实践

### 1. 环境变量管理

```bash
# .env 文件
NOVACODE_API_KEY=sk-xxxxxxxx
DEEPSEEK_API_KEY=sk-yyyyyyyy
```

```python
# 代码中自动替换
apiKey: "${NOVACODE_API_KEY}"  # 自动从环境变量读取
```

### 2. 模型降级策略

```python
async def chat_with_fallback(messages):
    # 优先使用高质量模型
    try:
        return await provider.chat(
            model="gpt-5.4",
            variant=ModelVariant.XHIGH,
            messages=messages
        )
    except Exception:
        # 降级到中等模型
        return await provider.chat(
            model="gpt-5.2",
            variant=ModelVariant.MEDIUM,
            messages=messages
        )
```

### 3. Token 管理

```python
# 检查模型限制
model = provider.get_model("gpt-5.4")
if model:
    print(f"最大上下文：{model.limit.context}")
    print(f"最大输出：{model.limit.output}")

# 验证请求
if not provider.validate_model("gpt-5.4", max_tokens=50000):
    raise ValueError("超出模型限制")
```

### 4. 错误处理

```python
from httpx import HTTPError, TimeoutException

try:
    response = await provider.chat(...)
except TimeoutException:
    # 超时重试
    response = await provider.chat(...)
except HTTPError as e:
    if e.response.status_code == 429:
        # 限流，等待后重试
        await asyncio.sleep(60)
        response = await provider.chat(...)
    else:
        raise
```

---

## 故障排查

### 问题 1：API Key 无效

```bash
# 检查环境变量
echo $NOVACODE_API_KEY

# 测试 API
curl -H "Authorization: Bearer $NOVACODE_API_KEY" \
  https://ai.novacode.top/v1/models
```

### 问题 2：模型不存在

```python
# 列出可用模型
models = provider.list_models()
print(models)
```

### 问题 3：超时

```yaml
# 增加超时时间
options:
  timeout: 300  # 5 分钟
```

---

## 参考资料

- [NovaCode 文档](https://docs.novacode.top)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Provider 配置示例](../config/providers/)
