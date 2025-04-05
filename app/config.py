"""Application configuration module."""
import os
from pydantic import BaseSettings

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
    
    # Storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"

settings = Settings() 