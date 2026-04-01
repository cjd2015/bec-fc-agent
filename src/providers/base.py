"""
AI Provider 抽象基类
支持多种 Provider 类型：直连 API、代理类 API、OpenAI 兼容代理
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncIterator
from pydantic import BaseModel, Field
from enum import Enum


class ModelVariant(str, Enum):
    """模型变体（推理速度/质量级别）"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"


class ModelLimit(BaseModel):
    """模型限制"""
    context: int = Field(..., description="上下文窗口大小（tokens）")
    output: int = Field(..., description="最大输出长度（tokens）")


class ModelConfig(BaseModel):
    """模型配置"""
    name: str = Field(..., description="模型显示名称")
    limit: ModelLimit = Field(..., description="模型限制")
    options: Dict = Field(default_factory=dict, description="模型选项")
    variants: Dict[str, Dict] = Field(default_factory=dict, description="变体配置")
    
    def get_variant(self, variant: ModelVariant) -> Dict:
        """获取变体配置"""
        return self.variants.get(variant.value, {})


class ProviderOptions(BaseModel):
    """Provider 配置"""
    baseURL: str = Field(..., description="API 基础 URL")
    apiKey: str = Field(..., description="API Key")
    timeout: int = Field(default=60, description="超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")


class ProviderConfig(BaseModel):
    """Provider 完整配置"""
    options: ProviderOptions = Field(..., description="连接选项")
    models: Dict[str, ModelConfig] = Field(..., description="支持的模型列表")


class ChatMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., description="角色：system/user/assistant")
    content: str = Field(..., description="消息内容")
    name: Optional[str] = Field(None, description="可选名称")


class ChatRequest(BaseModel):
    """对话请求"""
    messages: List[ChatMessage] = Field(..., description="消息列表")
    model: str = Field(..., description="模型 ID")
    variant: Optional[ModelVariant] = Field(None, description="模型变体")
    temperature: float = Field(default=0.7, description="温度")
    max_tokens: Optional[int] = Field(None, description="最大输出 tokens")
    stream: bool = Field(default=False, description="是否流式响应")
    options: Dict = Field(default_factory=dict, description="额外选项")


class ChatResponse(BaseModel):
    """对话响应"""
    id: str
    model: str
    content: str
    usage: Dict
    created_at: str


class AIProvider(ABC):
    """AI Provider 抽象基类"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.base_url = config.options.baseURL
        self.api_key = config.options.apiKey
        self.timeout = config.options.timeout
        self.max_retries = config.options.max_retries
        
        # 模型缓存
        self._models = config.models
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """对话（非流式）"""
        pass
    
    @abstractmethod
    async def chat_stream(self, request: ChatRequest) -> AsyncIterator[str]:
        """对话（流式）"""
        pass
    
    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        return self._models.get(model_id)
    
    def list_models(self) -> List[str]:
        """列出所有可用模型"""
        return list(self._models.keys())
    
    def validate_model(self, model_id: str, max_tokens: int) -> bool:
        """验证模型和 tokens 限制"""
        model = self.get_model(model_id)
        if not model:
            return False
        
        # 检查输出长度
        if max_tokens and max_tokens > model.limit.output:
            return False
        
        return True
    
    def _get_headers(self) -> Dict:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
