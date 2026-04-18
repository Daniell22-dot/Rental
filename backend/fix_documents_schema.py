import asyncio
from sqlalchemy import text
from app.core.database import engine

async def fix_schema():
    print("Connecting to database...")
    async with engine.begin() as conn:
        print("Checking if uploaded_by_id exists in documents...")
        # Check if column exists
        check_sql = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='documents' and column_name='uploaded_by_id';
        """)
        result = await conn.execute(check_sql)
        row = result.fetchone()
        
        if not row:
            print("Column 'uploaded_by_id' not found. Adding it...")
            alter_sql = text("ALTER TABLE documents ADD COLUMN uploaded_by_id INTEGER REFERENCES users(id);")
            await conn.execute(alter_sql)
            print("Column added successfully!")
        else:
            print("Column already exists!")

if __name__ == "__main__":
    asyncio.run(fix_schema())
