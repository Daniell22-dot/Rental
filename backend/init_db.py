import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Add the parent directory to sys.path to allow imports from 'app'
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Load environment variables from .env
dotenv_path = os.path.join(backend_dir, ".env")
if os.path.exists(dotenv_path):
    print(f"Loading environment from {dotenv_path}")
    load_dotenv(dotenv_path)

from app.core.database import Base
from app.config import settings

# Import all models to ensure they are registered with Base.metadata
from app.models.users import User
from app.models.property import Property
from app.models.unit import Unit
from app.models.tenant import Tenant
from app.models.lease import Lease
from app.models.payment import Payment
from app.models.maintenance import MaintenanceRequest
from app.models.notification import Notification
from app.models.interaction import Feedback, Review
from app.models.document import Document
from app.models.monitoring import SystemMetric, LogEntry
from app.models.cache import CacheItem

async def initialize_database():
    # Use a separate engine with a longer timeout for initialization
    # and disable pooling for a one-off script
    url = settings.ASYNC_DATABASE_URL
    print(f"Initializing database using: {url}")
    
    custom_engine = create_async_engine(
        url,
        connect_args={
            "timeout": 60,
            "command_timeout": 60,
        }
    )
    
    print("Connecting to Supabase (timeout: 60s)...")
    
    try:
        async with custom_engine.begin() as conn:
            print("Connection established. Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialization complete!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        traceback.print_exc()
    finally:
        await custom_engine.dispose()

if __name__ == "__main__":
    asyncio.run(initialize_database())
