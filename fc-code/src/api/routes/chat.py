"""
对话接口
支持多 Provider、多模型、模型变体
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from src.providers import (
    load_providers, ChatMessage, ModelVariant,
    ProviderFactory
)

router = APIRouter()

# 缓存 Provider 实例
_providers = {}


def get_providers():
    """获取所有 Provider（懒加载）"""
    global _providers
    if not _providers:
        _providers = load_providers("config/providers")
    return _providers


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户消息", min_length=1)
    provider: Optional[str] = Field("novacode", description="Provider 名称")
    model: str = Field(default="codex-mini-latest", description="模型 ID")
    variant: Optional[str] = Field(None, description="模型变体：low/medium/high/xhigh")
    stream: bool = Field(default=False, description="是否流式响应")
    conversation_id: Optional[str] = Field(None, description="会话 ID")
    temperature: float = Field(default=0.7, description="温度", ge=0, le=2)
    max_tokens: Optional[int] = Field(None, description="最大输出 tokens")
    options: Dict[str, Any] = Field(default_factory=dict, description="额外选项")


class ChatResponse(BaseModel):
    """对话响应"""
    id: str
    message: str
    provider: str
    model: str
    variant: Optional[str]
    conversation_id: str
    created_at: str
    usage: Optional[Dict[str, int]] = None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    发送对话消息
    
    - **message**: 用户消息
    - **provider**: Provider 名称（novacode 等）
    - **model**: 模型 ID（gpt-5.4, codex-mini-latest 等）
    - **variant**: 模型变体（low/medium/high/xhigh）
    - **stream**: 是否流式响应
    - **temperature**: 温度（0-2）
    - **max_tokens**: 最大输出 tokens
    """
    logger.info(f"💬 收到对话请求：{request.message[:50]}...")
    logger.info(f"   Provider: {request.provider}, Model: {request.model}, Variant: {request.variant}")
    
    try:
        # 获取 Provider
        providers = get_providers()
        if request.provider not in providers:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的 Provider: {request.provider}. 可用的：{list(providers.keys())}"
            )
        
        provider = providers[request.provider]
        
        # 验证模型
        model_config = provider.get_model(request.model)
        if not model_config:
            available_models = provider.list_models()
            raise HTTPException(
                status_code=400,
                detail=f"不支持的模型：{request.model}. 可用的：{available_models}"
            )
        
        # 验证变体
        variant = None
        if request.variant:
            try:
                variant = ModelVariant(request.variant.lower())
            except ValueError:
                valid_variants = [v.value for v in ModelVariant]
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的变体：{request.variant}. 有效的：{valid_variants}"
                )
        
        # 构建消息
        messages = [
            ChatMessage(role="user", content=request.message)
        ]
        
        # 发送请求
        if request.stream:
            # TODO: 实现流式响应
            raise HTTPException(status_code=501, detail="流式响应暂未实现")
        
        response = await provider.chat(
            model=request.model,
            variant=variant,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            options=request.options
        )
        
        return ChatResponse(
            id=response.id,
            message=response.content,
            provider=request.provider,
            model=request.model,
            variant=request.variant,
            conversation_id=request.conversation_id or f"conv_{datetime.now().timestamp()}",
            created_at=response.created_at,
            usage=response.usage
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"对话失败：{e}")
        raise HTTPException(status_code=500, detail=f"请求失败：{str(e)}")


@router.get("/providers")
async def list_providers():
    """获取所有可用的 Provider"""
    providers = get_providers()
    
    result = {}
    for name, provider in providers.items():
        result[name] = {
            "models": {},
            "base_url": provider.base_url
        }
        
        for model_id in provider.list_models():
            model = provider.get_model(model_id)
            if model:
                result[name]["models"][model_id] = {
                    "name": model.name,
                    "context_limit": model.limit.context,
                    "output_limit": model.limit.output,
                    "variants": list(model.variants.keys())
                }
    
    return {"providers": result}


@router.get("/providers/{provider_name}/models/{model_id}")
async def get_model_info(provider_name: str, model_id: str):
    """获取模型详情"""
    providers = get_providers()
    
    if provider_name not in providers:
        raise HTTPException(status_code=404, detail="Provider 不存在")
    
    provider = providers[provider_name]
    model = provider.get_model(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    return {
        "id": model_id,
        "name": model.name,
        "limit": {
            "context": model.limit.context,
            "output": model.limit.output
        },
        "variants": model.variants,
        "options": model.options
    }


@router.get("/conversations")
async def list_conversations():
    """获取会话列表"""
    # TODO: 实现
    return {"conversations": []}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取会话详情"""
    # TODO: 实现
    raise HTTPException(status_code=404, detail="会话不存在")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除会话"""
    # TODO: 实现
    return {"status": "ok"}
