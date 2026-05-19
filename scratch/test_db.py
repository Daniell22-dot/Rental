import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys

# Add backend to path to import config if needed
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def test_connection():
    # Try to load from .env manually or use settings if available
    from app.config import settings
    url = settings.ASYNC_DATABASE_URL
    print(f"Testing connection to: {url}")
    
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Connection successful: {result.fetchone()}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
