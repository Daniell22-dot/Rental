# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Create async engine with optimized connection pooling
if not settings.ASYNC_DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in Environment Variables")

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
    echo_pool=False,  # Set to True for debugging connection pool issues
    connect_args={
        "timeout": 10,  # 10 second timeout for connection
        "command_timeout": 10,  # 10 second timeout for commands
    }
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