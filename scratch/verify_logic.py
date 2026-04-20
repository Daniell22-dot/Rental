import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock environment
os.environ["VERCEL"] = "1"
os.environ["DATABASE_URL"] = "postgres://user:pass@host:5432/db"
os.environ["SECRET_KEY"] = "test-secret-key"

try:
    from app.config import settings
    from app.core.database import engine, pool_class
    
    print(f"ASYNC_DATABASE_URL: {settings.ASYNC_DATABASE_URL}")
    print(f"Pool class: {pool_class.__name__}")
    print(f"Engine pool class: {engine.pool.__class__.__name__}")
    
    assert "postgresql+asyncpg" in settings.ASYNC_DATABASE_URL
    assert pool_class.__name__ == "NullPool"
    
    print("Verification successful!")
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
