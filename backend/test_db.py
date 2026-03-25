"""
Test database connection
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_connection():
    print("Testing database connection...")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'not set')}")

    try:
        import asyncpg
        print("✓ asyncpg imported")

        # Parse URL
        import re
        url = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password@localhost:5432/price_comparison")

        # Extract connection details
        match = re.search(r'://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)',
                          url.replace('postgresql+asyncpg://', 'postgresql://'))

        if match:
            user, password, host, port, dbname = match.groups()
            print(f"Connecting to {host}:{port} as {user}")

            conn = await asyncpg.connect(
                user=user,
                password=password,
                database=dbname,
                host=host,
                port=int(port)
            )
            print("✅ Database connection successful!")

            # Test query
            result = await conn.fetchval("SELECT 1")
            print(f"Test query result: {result}")

            await conn.close()
            return True
        else:
            print("Could not parse database URL")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def test_engine():
    """Test SQLAlchemy async engine"""
    try:
        from app.core.database import engine, init_db

        print("Testing SQLAlchemy async engine...")
        await init_db()
        print("✅ SQLAlchemy engine works!")

        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ SQLAlchemy engine error: {e}")
        return False


async def main():
    print("=" * 50)
    print("Database Connection Test")
    print("=" * 50)

    result1 = await test_connection()
    print()

    if result1:
        result2 = await test_engine()

    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())