# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Create async engine with optimized connection pooling for serverless
if not settings.ASYNC_DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in Environment Variables")

# On Vercel (Serverless), we should use NullPool to prevent connection leaks/errors
# and ensure each request gets a fresh connection that is closed immediately.
import os
pool_class = NullPool if os.getenv("VERCEL") else QueuePool

# Configure engine arguments dynamically based on pool class
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "pool_pre_ping": True,
    "poolclass": pool_class,
    "connect_args": {
        "command_timeout": 30,
        "server_settings": {
            "application_name": "RMS_Vercel"
        },
        # Fix for PGBouncer in Transaction Mode
        "prepare_threshold": 0,
        "statement_cache_size": 0  # Disable statement caching as required by PGBouncer
    }
}

# Only add pool sizing if using a pooling class that supports it (QueuePool)
if pool_class == QueuePool:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": 3600,
    })

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    **engine_kwargs
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """
    Initialize database with default data
    """
    from app.models.users import User
    from app.models.property import Property
    from app.models.tenant import Tenant
    from app.models.lease import Lease
    from app.models.payment import Payment
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")