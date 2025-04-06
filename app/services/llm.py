from typing import Dict, Any, Optional
from enum import Enum
import os
import logging

from app.config import settings
from camel.types import ModelType

logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    LOCAL = "local"

def get_llm_model(model_name: str) -> Any:
    """
    Get an LLM model instance based on the model name
    
    Args:
        model_name: Name of the model to use (format: provider/model)
        
    Returns:
        A configured LLM model instance
        
    Example:
        >>> model = get_llm_model("openai/gpt-4")
        >>> model = get_llm_model("anthropic/claude-2")
    """
    # Parse provider from model name
    if "/" in model_name:
        provider, model = model_name.split("/", 1)
    else:
        # Default to OpenAI if not specified
        provider = ModelProvider.OPENAI
        model = model_name
    
    try:
        # Create appropriate model based on provider
        if provider == ModelProvider.OPENAI:
            from camel.models import OpenAIModel
            
            # Get model config from settings
            model_config = settings.MODEL_CONFIGS.get(model, {})
            
            return OpenAIModel(
                model_type=ModelType.GPT_4 if "gpt-4" in model or "gpt-4o" in model else ModelType.GPT_35_TURBO,
                model_config_dict=model_config,
                api_key=os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
            )
        elif provider == ModelProvider.ANTHROPIC:
            from camel.models import AnthropicModel
            return AnthropicModel(
                model_name=model,
                api_key=os.getenv("ANTHROPIC_API_KEY", settings.ANTHROPIC_API_KEY)
            )
        elif provider == ModelProvider.GEMINI:
            from camel.models import GeminiModel
            return GeminiModel(
                model_name=model,
                api_key=os.getenv("GOOGLE_API_KEY", settings.GOOGLE_API_KEY)
            )
        elif provider == ModelProvider.LOCAL:
            # For local models via LMStudio or similar
            from camel.models import LocalModel
            return LocalModel(
                model_name=model,
                api_base=os.getenv("LOCAL_MODEL_API_BASE", settings.LOCAL_MODEL_API_BASE)
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")
            
    except Exception as e:
        logger.error(f"Failed to initialize LLM model {model_name}: {str(e)}")
        raise

def get_embedding_model(model_name: Optional[str] = None) -> Any:
    """
    Get an embedding model instance
    
    Args:
        model_name: Optional specific model to use, defaults to OpenAI's text-embedding-ada-002
        
    Returns:
        An embedding model instance
    """
    try:
        from camel.models import OpenAIEmbeddings
        
        # Default to OpenAI's embedding model if none specified
        if not model_name:
            model_name = "text-embedding-ada-002"
        
        return OpenAIEmbeddings(
            model_name=model_name,
            api_key=os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        )
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {str(e)}")
        raise 