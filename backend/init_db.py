"""
Initialize PostgreSQL database
"""
import asyncio
from app.core.database import init_db, engine

async def main():
    print("Initializing database...")
    await init_db()
    print("✅ Database initialized successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())