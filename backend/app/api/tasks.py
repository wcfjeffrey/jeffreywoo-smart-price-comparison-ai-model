from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.task import Task, TaskCreate, TaskUpdate
from app.services.task_scheduler import TaskScheduler
import logging

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


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Create a new scheduled task"""
    try:
        logger.info(f"Creating task for product: {task.product_name}")
        new_task = await scheduler.create_task(task)
        return new_task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
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