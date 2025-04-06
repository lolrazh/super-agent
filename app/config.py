"""Application configuration module."""
import os
from typing import Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/superagent")
    
    # Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # LLM settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    LOCAL_MODEL_API_BASE: str = os.getenv("LOCAL_MODEL_API_BASE", "http://localhost:1234/v1")
    
    # Agent settings
    ASSISTANT_MODEL: str = os.getenv("ASSISTANT_MODEL", "gpt-4")  # Main assistant model
    PLANNER_MODEL: str = os.getenv("PLANNER_MODEL", "gpt-3.5-turbo")  # Task planning model
    EXECUTOR_MODEL: str = os.getenv("EXECUTOR_MODEL", "gpt-3.5-turbo")  # Task execution model
    CRITIC_MODEL: str = os.getenv("CRITIC_MODEL", "gpt-3.5-turbo")  # Review/critique model
    
    # Model configurations
    MODEL_CONFIGS: Dict = {
        "gpt-4": {"max_tokens": 8192, "temperature": 0.7},
        "gpt-3.5-turbo": {"max_tokens": 4096, "temperature": 0.7},
        "claude-2": {"max_tokens": 12000, "temperature": 0.7},
        "gemini-pro": {"max_tokens": 8192, "temperature": 0.7},
        "gpt-4o-mini": {"max_tokens": 8192, "temperature": 0.7}
    }
    
    # Storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    # Tool settings
    ENABLE_BROWSER_TOOLS: bool = os.getenv("ENABLE_BROWSER_TOOLS", "true").lower() == "true"
    ENABLE_CODE_EXECUTION: bool = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    ENABLE_FILE_OPERATIONS: bool = os.getenv("ENABLE_FILE_OPERATIONS", "true").lower() == "true"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"

settings = Settings() 