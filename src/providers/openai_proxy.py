"""
OpenAI 兼容代理 Provider
支持 NovaCode、以及其他 OpenAI API 兼容的代理服务
"""
import httpx
import json
from typing import AsyncIterator, Dict, Any
from datetime import datetime
from loguru import logger

from .base import (
    AIProvider, ProviderConfig, ChatRequest, ChatResponse, 
    ChatMessage, ModelVariant
)


class OpenAIProxyProvider(AIProvider):
    """OpenAI 兼容代理 Provider"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, payload: Dict):
        """发送请求（非流式）"""
        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    "/chat/completions",
                    json=payload
                )
                response.raise_for_status()
                return response
            except httpx.HTTPError as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数退避
    
    async def chat(
        self,
        messages: list,
        model: str = None,
        variant: ModelVariant = None,
        temperature: float = 0.7,
        max_tokens: int = None,
        **options
    ) -> ChatResponse:
        """对话（非流式）"""
        # 验证模型
        if not self.validate_model(model, max_tokens or 4096):
            raise ValueError(f"无效的模型或超出限制：{model}")
        
        # 构建请求体
        payload = {
            "model": model,
            "messages": [
                {"role": msg.role if hasattr(msg, 'role') else msg['role'], 
                 "content": msg.content if hasattr(msg, 'content') else msg['content']}
                for msg in messages
            ],
            "temperature": temperature,
            "stream": False,
        }
        
        # 添加最大 tokens
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # 添加模型变体选项
        if variant:
            model_config = self.get_model(model)
            if model_config:
                variant_config = model_config.get_variant(variant)
                payload.update(variant_config)
        
        # 添加额外选项
        payload.update(options)
        
        logger.info(f"📤 发送请求到 {self.base_url}/chat/completions")
        logger.debug(f"请求模型：{model}, 消息数：{len(messages)}")
        
        # 发送请求
        response = await self._make_request(payload)
        data = response.json()
        
        # 解析响应
        choice = data["choices"][0]
        message = choice["message"]
        usage = data.get("usage", {})
        
        logger.info(f"✅ 响应成功，tokens: {usage.get('total_tokens', 'N/A')}")
        
        return ChatResponse(
            id=data.get("id", ""),
            model=model,
            content=message["content"],
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            },
            created_at=datetime.now().isoformat()
        )
    
    async def chat_stream(
        self,
        messages: list,
        model: str = None,
        variant: ModelVariant = None,
        temperature: float = 0.7,
        max_tokens: int = None,
        **options
    ) -> AsyncIterator[str]:
        """对话（流式）"""
        # 验证模型
        if not self.validate_model(model, max_tokens or 4096):
            raise ValueError(f"无效的模型或超出限制：{model}")
        
        # 构建请求体
        payload = {
            "model": model,
            "messages": [
                {"role": msg.role if hasattr(msg, 'role') else msg['role'], 
                 "content": msg.content if hasattr(msg, 'content') else msg['content']}
                for msg in messages
            ],
            "temperature": temperature,
            "stream": True,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # 添加模型变体选项
        if variant:
            model_config = self.get_model(model)
            if model_config:
                variant_config = model_config.get_variant(variant)
                payload.update(variant_config)
        
        payload.update(options)
        
        logger.info(f"📤 发送流式请求到 {self.base_url}/chat/completions")
        
        # 发送流式请求
        async with self.client.stream(
            "POST",
            "/chat/completions",
            json=payload
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    
                    if data.strip() == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(data)
                        choice = chunk["choices"][0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        logger.warning(f"解析 chunk 失败：{data}")
                        continue
    
    async def close(self):
        """关闭连接"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
