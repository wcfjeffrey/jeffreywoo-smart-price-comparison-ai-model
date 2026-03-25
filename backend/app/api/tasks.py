from fastapi import APIRouter, HTTPException, status
from app.models.task import Task, TaskCreate, TaskUpdate
from app.services.task_scheduler import TaskScheduler
import logging
from datetime import datetime, timedelta
import pytz
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

router = APIRouter()
scheduler = TaskScheduler()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_tasks():
    """Get all scheduled tasks"""
    try:
        tasks = scheduler.get_tasks()
        logger.info(f"Retrieved {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_scheduler_manually():
    """Manually start the scheduler"""
    try:
        logger.info("Manual scheduler start requested")
        await scheduler._load_tasks_from_db()
        scheduler.start()
        return {
            "status": "success",
            "running": scheduler.scheduler.running,
            "tasks_loaded": len(scheduler.tasks)
        }
    except Exception as e:
        logger.error(f"Manual start failed: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/stop")
async def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.stop()
        return {"status": "success", "message": "Scheduler stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/clear-jobs")
async def clear_all_jobs():
    """Clear all scheduled jobs"""
    try:
        # Get all jobs
        jobs = scheduler.scheduler.get_jobs()
        for job in jobs:
            scheduler.scheduler.remove_job(job.id)
        return {"status": "success", "message": f"Removed {len(jobs)} jobs"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/restart")
async def restart_scheduler():
    """Restart the scheduler cleanly"""
    try:
        # Stop if running
        if scheduler.scheduler.running:
            scheduler.stop()

        # Clear all jobs
        for job in scheduler.scheduler.get_jobs():
            scheduler.scheduler.remove_job(job.id)

        # Clear in-memory tasks
        scheduler.tasks.clear()

        # Load tasks from database
        await scheduler._load_tasks_from_db()

        # Start scheduler
        scheduler.start()

        return {
            "status": "success",
            "running": scheduler.scheduler.running,
            "tasks_loaded": len(scheduler.tasks),
            "jobs": len(scheduler.scheduler.get_jobs())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/status")
async def scheduler_status():
    """Check if scheduler is running"""
    try:
        is_running = scheduler.scheduler.running
        jobs = scheduler.scheduler.get_jobs()

        job_info = []
        for job in jobs:
            job_info.append({
                "id": job.id,
                "pending": True
            })

        return {
            "status": "running" if is_running else "stopped",
            "job_count": len(jobs),
            "jobs": job_info
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get a specific task"""
    try:
        task = scheduler.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_google_credentials():
    try:
        creds = Credentials(
            token=None,  # We'll refresh if needed
            refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            token_uri="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        return creds
    except Exception as e:
        logger.error(f"Failed to load Google credentials: {e}")
        return None

@router.post("/tasks/")
async def create_task(task: dict):
    """Create a new scheduled task with Google Calendar support"""
    try:
        logger.info(f"Creating task for product: {task.get('product_name')}")

        # 1. Save task to database
        new_task = await scheduler.create_task(task)

        # 2. Create Google Calendar event if requested
        if task.get("notification_method") in ["calendar", "both"]:
            try:
                user_timezone = task.get("timezone", "Asia/Hong_Kong")

                # Parse time
                time_str = task["time"]
                today = datetime.now(pytz.timezone(user_timezone)).date()

                local_tz = pytz.timezone(user_timezone)
                local_time = datetime.strptime(time_str, "%H:%M").time()
                local_dt = datetime.combine(today, local_time)
                aware_local_dt = local_tz.localize(local_dt)

                utc_dt = aware_local_dt.astimezone(pytz.UTC)

                event = {
                    'summary': f'Price Check: {task["product_name"]}',
                    'description': f'Scheduled price alert for {task["product_name"]}\nFrequency: {task["frequency"]}',
                    'start': {
                        'dateTime': utc_dt.isoformat(),
                        'timeZone': user_timezone,
                    },
                    'end': {
                        'dateTime': (utc_dt + timedelta(minutes=30)).isoformat(),
                        'timeZone': user_timezone,
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 10},
                            {'method': 'email', 'minutes': 30},
                        ],
                    },
                }

                # Build service using credentials from .env
                creds = get_google_credentials()
                if creds is None:
                    raise Exception("Google credentials not loaded")

                service = build('calendar', 'v3', credentials=creds)

                created_event = service.events().insert(
                    calendarId=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
                    body=event
                ).execute()

                logger.info(f"✅ Google Calendar event created successfully for {task['product_name']}")

            except Exception as calendar_err:
                logger.warning(f"Failed to create Google Calendar event: {calendar_err}")
                # Task is still created even if calendar fails

        return {
            "status": "success",
            "message": "Task created successfully",
            "task": new_task
        }

    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    try:
        logger.info(f"Updating task {task_id}")
        task = await scheduler.update_task(task_id, task_update)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Delete a task"""
    try:
        logger.info(f"Deleting task {task_id}")
        if not await scheduler.delete_task(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
