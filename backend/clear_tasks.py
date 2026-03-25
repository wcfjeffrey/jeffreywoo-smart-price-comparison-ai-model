import asyncio
from app.core.database import AsyncSessionLocal
from app.core.database import TaskModel
from sqlalchemy import delete

async def clear_tasks():
    async with AsyncSessionLocal() as session:
        result = await session.execute(delete(TaskModel))
        await session.commit()
        print(f"Deleted {result.rowcount} tasks")

asyncio.run(clear_tasks())
print("Database cleared!")
