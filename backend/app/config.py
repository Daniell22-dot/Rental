# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

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
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email (Mapped to .env)
    SMTP_PORT: Optional[int] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
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

settings = Settings()