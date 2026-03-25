from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ScheduleTask(BaseModel):
    task_type: str
    schedule_time: str
    parameters: dict

@router.post("/task")
async def create_scheduled_task(task: ScheduleTask):
    """Create scheduled task"""
    return {
        "status": "success",
        "message": f"Task {task.task_type} scheduled for {task.schedule_time}",
        "task_id": datetime.now().strftime("%Y%m%d_%H%M%S")
    }

@router.get("/tasks")
async def list_scheduled_tasks():
    """List scheduled tasks"""
    return {
        "status": "success",
        "data": [
            {"id": "price_comparison", "type": "price_comparison", "schedule": "every 6 hours", "next_run": "2024-01-15T15:00:00"},
            {"id": "daily_report", "type": "daily_report", "schedule": "daily at 9:00", "next_run": "2024-01-16T09:00:00"},
        ]
    }
