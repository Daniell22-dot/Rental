import asyncio
from app.core.database import engine, init_db as _init_db

async def main():
    await _init_db()

if __name__ == "__main__":
    asyncio.run(main())
