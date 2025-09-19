import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application settings
    debug: bool = False
    log_level: str = "INFO"
    
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Celery settings
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Anthropic settings
    anthropic_api_key: Optional[str] = None
    
    # MCP settings
    mcp_enabled: bool = True
    mcp_media_server_url: Optional[str] = None
    mcp_image_server_url: Optional[str] = None
    mcp_tts_server_url: Optional[str] = None
    mcp_video_server_url: Optional[str] = None
    
    # LlamaIndex settings
    llama_index_enabled: bool = True
    llama_index_storage_dir: str = "./data/index_storage"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()