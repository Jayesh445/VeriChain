from pydantic_settings  import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./verichain.db"
    
    # AI/Agent Configuration
    gemini_api_key: str = ""
    agent_model: str = "gemini-pro"
    agent_temperature: float = 0.1
    
    # Business Rules
    reorder_threshold_percentage: float = 20.0
    anomaly_detection_threshold: float = 2.0
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Redis (optional)
    redis_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/verichain.log"
    
    class Config:
        env_file = ".env"


settings = Settings()