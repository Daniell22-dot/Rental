# backend/app/config.py
import os

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
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # JWT (REQUIRED)
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email (Mapped to .env)
    SMTP_PORT: Optional[int] = os.getenv("SMTP_PORT")
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    MAIL_FROM: Optional[str] = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME: Optional[str] = os.getenv("MAIL_FROM_NAME")
    
    # MPESA
    MPESA_SHORTCODE: Optional[str] = os.getenv("MPESA_SHORTCODE")
    MPESA_PASSKEY: Optional[str] = os.getenv("MPESA_PASSKEY")
    MPESA_CONSUMER_KEY: Optional[str] = os.getenv("MPESA_CONSUMER_KEY")
    MPESA_CONSUMER_SECRET: Optional[str] = os.getenv("MPESA_CONSUMER_SECRET")
    MPESA_CALLBACK_URL: Optional[str] = os.getenv("MPESA_CALLBACK_URL")
    MPESA_ENVIRONMENT: str = os.getenv("MPESA_ENVIRONMENT", "sandbox")
    
    # DeepSeek AI
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **data):
        super().__init__(**data)
        self._validate_required_settings()
    
    def _validate_required_settings(self):
        """Validate that required settings are configured."""
        errors = []
        
        # SECRET_KEY is required for JWT
        if not self.SECRET_KEY or self.SECRET_KEY == os.getenv("SECRET_KEY"):
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