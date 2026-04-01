"""
Provider 工厂
支持动态加载不同类型的 Provider
"""
import yaml
import os
from typing import Dict, Optional
from loguru import logger

from .base import AIProvider, ProviderConfig, ProviderOptions, ModelConfig, ModelLimit
from .openai_proxy import OpenAIProxyProvider


class ProviderFactory:
    """Provider 工厂类"""
    
    _providers: Dict[str, type] = {
        "openai_proxy": OpenAIProxyProvider,
        # 未来扩展
        # "qwen": QwenProvider,
        # "deepseek": DeepSeekProvider,
        # "kimi": KimiProvider,
    }
    
    @classmethod
    def register(cls, name: str, provider_class: type):
        """注册新的 Provider 类型"""
        cls._providers[name] = provider_class
        logger.info(f"✅ 注册 Provider: {name}")
    
    @classmethod
    def create(cls, config: ProviderConfig, provider_type: str = "openai_proxy") -> AIProvider:
        """创建 Provider 实例"""
        if provider_type not in cls._providers:
            raise ValueError(f"不支持的 Provider 类型：{provider_type}")
        
        provider_class = cls._providers[provider_type]
        logger.info(f"🔌 创建 Provider: {provider_type}")
        
        return provider_class(config)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> AIProvider:
        """从 YAML 配置文件创建 Provider"""
        logger.info(f"📄 从 {config_path} 加载 Provider 配置")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 提取 provider 配置
        provider_data = data.get("provider", {})
        provider_type = provider_data.get("type", "openai_proxy")
        
        # 解析选项
        options_data = provider_data.get("options", {})
        
        # 替换环境变量
        api_key = options_data.get("apiKey", "")
        if api_key.startswith("${") and api_key.endswith("}"):
            env_var = api_key[2:-1]
            api_key = os.environ.get(env_var, "")
        
        options = ProviderOptions(
            baseURL=options_data.get("baseURL", ""),
            apiKey=api_key,
            timeout=options_data.get("timeout", 60),
            max_retries=options_data.get("max_retries", 3)
        )
        
        # 解析模型配置
        models_data = provider_data.get("models", {})
        models = {}
        
        for model_id, model_info in models_data.items():
            limit_data = model_info.get("limit", {})
            limit = ModelLimit(
                context=limit_data.get("context", 4096),
                output=limit_data.get("output", 2048)
            )
            
            model = ModelConfig(
                name=model_info.get("name", model_id),
                limit=limit,
                options=model_info.get("options", {}),
                variants=model_info.get("variants", {})
            )
            
            models[model_id] = model
            logger.debug(f"  - 加载模型：{model_id} ({model.name})")
        
        # 创建配置
        config = ProviderConfig(
            options=options,
            models=models
        )
        
        # 创建 Provider
        return cls.create(config, provider_type)
    
    @classmethod
    def create_multiple(cls, configs_dir: str) -> Dict[str, AIProvider]:
        """从配置目录加载多个 Provider"""
        providers = {}
        
        if not os.path.exists(configs_dir):
            logger.warning(f"配置目录不存在：{configs_dir}")
            return providers
        
        for filename in os.listdir(configs_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                config_path = os.path.join(configs_dir, filename)
                try:
                    provider = cls.from_yaml(config_path)
                    provider_name = filename.replace(".yaml", "").replace(".yml", "")
                    providers[provider_name] = provider
                    logger.info(f"✅ 加载 Provider: {provider_name}")
                except Exception as e:
                    logger.error(f"❌ 加载 Provider 失败 {filename}: {e}")
        
        return providers


# 便捷函数
def load_provider(config_path: str) -> AIProvider:
    """从配置文件加载 Provider"""
    return ProviderFactory.from_yaml(config_path)


def load_providers(configs_dir: str = "config/providers") -> Dict[str, AIProvider]:
    """从配置目录加载所有 Provider"""
    return ProviderFactory.create_multiple(configs_dir)
