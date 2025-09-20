"""
Configuration management for VeriChain application.
"""

import os
from typing import Optional, List, Union
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App Configuration
    app_name: str = "VeriChain"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    
    # Google Gemini Configuration
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None  # Alternative field name
    gemini_model: str = "gemini-1.5-flash"
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./verichain.db"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/verichain.log"
    
    # Agent Configuration
    max_retry_attempts: int = 3
    request_timeout: int = 30
    memory_size: int = 10
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Configuration - Handle as strings and convert to lists
    allowed_origins: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"
    allowed_methods: Union[str, List[str]] = "GET,POST,PUT,DELETE,OPTIONS"
    allowed_headers: Union[str, List[str]] = "*"
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @field_validator('allowed_methods', mode='before')
    @classmethod
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(',') if method.strip()]
        return v
    
    @field_validator('allowed_headers', mode='before')
    @classmethod
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [header.strip() for header in v.split(',') if header.strip()]
        return v
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    @property
    def effective_api_key(self) -> Optional[str]:
        """Get the effective API key (prioritize gemini_api_key over google_api_key)."""
        return self.gemini_api_key or self.google_api_key
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.is_development
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting."""
        if self.database_url.startswith("sqlite"):
            # Ensure logs directory exists for SQLite
            os.makedirs("logs", exist_ok=True)
        return self.database_url
    
    def validate_required_settings(self) -> List[str]:
        """Validate required settings and return missing ones."""
        missing = []
        
        if not self.effective_api_key:
            missing.append("GEMINI_API_KEY or GOOGLE_API_KEY")
        
        if not self.secret_key or self.secret_key == "your-secret-key-change-in-production":
            if self.is_production:
                missing.append("SECRET_KEY")
        
        return missing


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()