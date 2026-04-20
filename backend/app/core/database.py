# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.config import settings
import logging
from typing import AsyncGenerator

print("[RMS DEBUG] Loading database.py module...")
logger = logging.getLogger(__name__)

# Create async engine with optimized connection pooling for serverless
if not settings.ASYNC_DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in Environment Variables")

# On Vercel (Serverless), we should use NullPool to prevent connection leaks/errors
# and ensure each request gets a fresh connection that is closed immediately.
import os
pool_class = NullPool if os.getenv("VERCEL") else QueuePool

# Configure engine arguments dynamically based on pool class
# NOTE: connect_args are asyncpg-specific. 'prepare_threshold' is psycopg3-only
# and must NOT be used here. Use 'statement_cache_size=0' for asyncpg.
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "poolclass": pool_class,
    "connect_args": {
        "command_timeout": 30,
        "statement_cache_size": 0,  # Disables prepared statements - required for PgBouncer
        "server_settings": {
            "application_name": "RMS_Vercel"
        },
    }
}

# Only add pool sizing if using a pooling class that supports it (QueuePool)
if pool_class == QueuePool:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": 3600,
    })
else:
    # Explicitly ensure pool_size/max_overflow are NOT in kwargs for NullPool
    engine_kwargs.pop("pool_size", None)
    engine_kwargs.pop("max_overflow", None)
    print(f"[RMS DEBUG] Using NullPool. Arguments filtered: {list(engine_kwargs.keys())}")

print(f"[RMS DEBUG] Creating engine with class: {pool_class.__name__}")

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