# backend/app/config.py
from pydantic_settings import BaseSettings
from pydantic import ValidationError
from typing import Optional
import logging
import sys

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Rental Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "rental"
    DATABASE_URL: Optional[str] = None
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # JWT (REQUIRED)
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email (Mapped to .env)
    SMTP_PORT: Optional[int] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_FROM_NAME: Optional[str] = None
    
    # MPESA
    MPESA_SHORTCODE: Optional[str] = None
    MPESA_PASSKEY: Optional[str] = None
    MPESA_CONSUMER_KEY: Optional[str] = None
    MPESA_CONSUMER_SECRET: Optional[str] = None
    MPESA_CALLBACK_URL: Optional[str] = None
    MPESA_ENVIRONMENT: str = "sandbox"
    
    # DeepSeek AI
    DEEPSEEK_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **data):
        super().__init__(**data)
        self._validate_required_settings()
    
    def _validate_required_settings(self):
        """Validate that required settings are configured."""
        errors = []
        
        # SECRET_KEY is required for JWT
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-here":
            errors.append("SECRET_KEY must be set in .env (required for JWT)")
        
        # DATABASE_URL validation
        if not self.DATABASE_URL:
            # Construct from parts if not provided
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:5432/{self.POSTGRES_DB}"
        
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            raise ValueError("Missing or invalid required settings. Check .env file.")

try:
    settings = Settings()
except ValidationError as e:
    logger.error("Failed to load settings:", exc_info=True)
    sys.exit(1)