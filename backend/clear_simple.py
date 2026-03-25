import os
import sys

# Add the project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import and clear
try:
    from app.services.task_scheduler import TaskScheduler
    import asyncio
    
    async def clear():
        scheduler = TaskScheduler()
        # Clear in-memory tasks
        scheduler.tasks.clear()
        print(f"Cleared {len(scheduler.tasks)} in-memory tasks")
        
        # Try to clear database
        try:
            await scheduler._delete_task_from_db("all")
            print("Database tasks cleared")
        except:
            print("Could not clear database tasks")
    
    asyncio.run(clear())
    print("✅ Cleanup complete!")
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying alternative method...")
    
    # Alternative: Try to connect directly
    import psycopg2
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="price_comparison",
            user="admin",
            password="password"
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks;")
        conn.commit()
        print(f"Deleted {cur.rowcount} tasks from database")
        cur.close()
        conn.close()
    except Exception as e2:
        print(f"Database connection failed: {e2}")
        print("\nIf you're using SQLite, delete the SQLite file:")
        print("Remove-Item data/price_comparison.db -Force")
