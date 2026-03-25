from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import pytz

# Inside your task creation logic
user_timezone = task.get("timezone", "Asia/Hong_Kong")   # default to your region

# Parse the time string
time_str = task["time"]   # e.g. "18:40"
today = datetime.now().date()

# Create naive datetime
naive_dt = datetime.combine(today, datetime.strptime(time_str, "%H:%M").time())

# Make it timezone-aware
local_tz = pytz.timezone(user_timezone)
aware_dt = local_tz.localize(naive_dt)

# Convert to UTC for Google Calendar (Google expects UTC)
utc_dt = aware_dt.astimezone(pytz.UTC)

# Now use utc_dt when creating the Google Calendar event
event = {
    'summary': f'Price Check: {task["product_name"]}',
    'start': {
        'dateTime': utc_dt.isoformat(),
        'timeZone': user_timezone,
    },
    'end': {
        'dateTime': (utc_dt + timedelta(minutes=30)).isoformat(),  # 30 min duration
        'timeZone': user_timezone,
    },
    'reminders': {
        'useDefault': False,
        'overrides': [{'method': 'email', 'minutes': 30}],
    },
}

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
