"""
Task Scheduler with PostgreSQL persistence
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import uuid
import logging

from app.models.task import Task, Frequency, TaskCreate
from app.services.product_analyzer import ProductAnalyzer
from app.services.notification_service import NotificationService
from app.core.database import TaskModel, AsyncSessionLocal
from sqlalchemy import select, update, delete

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks with PostgreSQL persistence"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.tasks: Dict[str, Task] = {}
        self.product_analyzer = ProductAnalyzer()
        self.notification_service = NotificationService()

    async def _load_tasks_from_db(self):
        """Load tasks from PostgreSQL"""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(TaskModel))
                db_tasks = result.scalars().all()

                for db_task in db_tasks:
                    task = Task(
                        id=db_task.id,
                        product_name=db_task.product_name,
                        frequency=Frequency(db_task.frequency),
                        time=db_task.time,
                        day_of_week=db_task.day_of_week,
                        day_of_month=db_task.day_of_month,
                        notification_method=db_task.notification_method,
                        email=db_task.email,
                        active=db_task.active,
                        created_at=db_task.created_at,
                        updated_at=db_task.updated_at,
                        last_run=db_task.last_run,
                        next_run=db_task.next_run
                    )
                    self.tasks[task.id] = task

                logger.info(f"Loaded {len(self.tasks)} tasks from PostgreSQL")
        except Exception as e:
            logger.error(f"Error loading tasks from PostgreSQL: {e}")

    async def _save_task_to_db(self, task: Task):
        """Save task to PostgreSQL"""
        try:
            async with AsyncSessionLocal() as session:
                db_task = TaskModel(
                    id=task.id,
                    product_name=task.product_name,
                    frequency=task.frequency.value,
                    time=task.time,
                    day_of_week=task.day_of_week,
                    day_of_month=task.day_of_month,
                    notification_method=task.notification_method,
                    email=task.email,
                    active=task.active,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    last_run=task.last_run,
                    next_run=task.next_run
                )
                session.add(db_task)
                await session.commit()
                logger.info(f"Task {task.id} saved to PostgreSQL")
        except Exception as e:
            logger.error(f"Error saving task to PostgreSQL: {e}")

    async def _update_task_in_db(self, task: Task):
        """Update task in PostgreSQL"""
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(TaskModel)
                    .where(TaskModel.id == task.id)
                    .values(
                        product_name=task.product_name,
                        frequency=task.frequency.value,
                        time=task.time,
                        day_of_week=task.day_of_week,
                        day_of_month=task.day_of_month,
                        notification_method=task.notification_method,
                        email=task.email,
                        active=task.active,
                        updated_at=task.updated_at,
                        last_run=task.last_run,
                        next_run=task.next_run
                    )
                )
                await session.commit()
                logger.info(f"Task {task.id} updated in PostgreSQL")
        except Exception as e:
            logger.error(f"Error updating task in PostgreSQL: {e}")

    async def _delete_task_from_db(self, task_id: str):
        """Delete task from PostgreSQL"""
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    delete(TaskModel).where(TaskModel.id == task_id)
                )
                await session.commit()
                logger.info(f"Task {task_id} deleted from PostgreSQL")
        except Exception as e:
            logger.error(f"Error deleting task from PostgreSQL: {e}")

    async def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new scheduled task"""
        task_id = str(uuid.uuid4())
        now = datetime.now()

        next_run = self._calculate_next_run(task_data)

        task = Task(
            id=task_id,
            product_name=task_data.product_name,
            frequency=task_data.frequency,
            time=task_data.time,
            day_of_week=task_data.day_of_week,
            day_of_month=task_data.day_of_month,
            notification_method=task_data.notification_method,
            email=task_data.email,
            active=True,
            created_at=now,
            updated_at=now,
            next_run=next_run
        )

        self.tasks[task_id] = task

        # Save to PostgreSQL
        await self._save_task_to_db(task)

        # Schedule the task
        self._schedule_task(task)

        logger.info(f"Created task {task_id} for {task.product_name} - next run: {next_run}")
        return task

    def _calculate_next_run(self, task_data: TaskCreate) -> datetime:
        """Calculate the next run time for a task"""
        now = datetime.now()
        hour, minute = map(int, task_data.time.split(':'))

        if task_data.frequency == Frequency.DAILY:
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif task_data.frequency == Frequency.WEEKLY:
            day = task_data.day_of_week if task_data.day_of_week is not None else 0
            days_ahead = (day - now.weekday()) % 7
            if days_ahead == 0 and now.hour >= hour:
                days_ahead = 7
            next_run = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            return next_run

        elif task_data.frequency == Frequency.MONTHLY:
            day = task_data.day_of_month if task_data.day_of_month is not None else 1
            if day > now.day:
                next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                if now.month == 12:
                    next_run = now.replace(year=now.year + 1, month=1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month + 1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
            return next_run

        else:
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

    def _schedule_task(self, task: Task):
        """Schedule a task with APScheduler"""
        hour, minute = map(int, task.time.split(':'))

        if task.frequency == Frequency.DAILY:
            trigger = CronTrigger(hour=hour, minute=minute)
        elif task.frequency == Frequency.WEEKLY:
            trigger = CronTrigger(day_of_week=task.day_of_week, hour=hour, minute=minute)
        elif task.frequency == Frequency.MONTHLY:
            trigger = CronTrigger(day=task.day_of_month, hour=hour, minute=minute)
        else:
            run_date = task.next_run
            if run_date and run_date > datetime.now():
                self.scheduler.add_job(
                    self._execute_task,
                    'date',
                    run_date=run_date,
                    args=[task.id],
                    id=task.id
                )
                return

        self.scheduler.add_job(
            self._execute_task,
            trigger,
            args=[task.id],
            id=task.id
        )

    async def _execute_task(self, task_id: str):
        """Execute a scheduled task"""
        task = self.tasks.get(task_id)
        if not task or not task.active:
            return

        logger.info(f"Executing task {task_id} for product: {task.product_name}")

        try:
            # Analyze the product
            analysis = await self.product_analyzer.analyze_product(task.product_name)

            # Send notification
            await self.notification_service.send_price_report(
                task.email or "",
                task.product_name,
                analysis,
                task.notification_method
            )

            # Update last run
            task.last_run = datetime.now()
            # Update next run
            temp_task = TaskCreate(
                product_name=task.product_name,
                frequency=task.frequency,
                time=task.time,
                day_of_week=task.day_of_week,
                day_of_month=task.day_of_month,
                notification_method=task.notification_method,
                email=task.email
            )
            task.next_run = self._calculate_next_run(temp_task)
            task.updated_at = datetime.now()

            # Update in PostgreSQL
            await self._update_task_in_db(task)

            logger.info(f"Task {task_id} executed successfully, next run: {task.next_run}")

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")

    def get_tasks(self) -> List[Task]:
        """Get all tasks"""
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task"""
        return self.tasks.get(task_id)

    async def update_task(self, task_id: str, task_update) -> Optional[Task]:
        """Update a task"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for update")
            return None

        task = self.tasks[task_id]

        # Remove old scheduled job
        try:
            self.scheduler.remove_job(task_id)
        except Exception as e:
            logger.warning(f"Could not remove job {task_id}: {e}")

        # Update fields
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(task, field, value)

        task.updated_at = datetime.now()

        # Recalculate next run if frequency or time changed
        if 'frequency' in update_data or 'time' in update_data:
            temp_task = TaskCreate(
                product_name=task.product_name,
                frequency=task.frequency,
                time=task.time,
                day_of_week=task.day_of_week,
                day_of_month=task.day_of_month,
                notification_method=task.notification_method,
                email=task.email
            )
            task.next_run = self._calculate_next_run(temp_task)

        # Reschedule if active
        if task.active:
            self._schedule_task(task)

        # Update in PostgreSQL
        await self._update_task_in_db(task)

        logger.info(f"Updated task {task_id}")
        return task

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found for deletion")
            return False

        # Remove scheduled job
        try:
            self.scheduler.remove_job(task_id)
        except Exception as e:
            logger.warning(f"Could not remove job {task_id}: {e}")

        # Remove from tasks dict
        del self.tasks[task_id]

        # Delete from PostgreSQL
        await self._delete_task_from_db(task_id)

        logger.info(f"Deleted task {task_id}")
        return True

    def start(self):
        """Start the scheduler"""
        logger.info("=" * 50)
        logger.info("TaskScheduler.start() called")
        logger.info(f"Tasks in memory: {len(self.tasks)}")

        # Reschedule all active tasks on startup
        scheduled_count = 0
        for task in self.tasks.values():
            if task.active:
                logger.info(f"  Scheduling task: {task.product_name} at {task.time}")
                self._schedule_task(task)
                scheduled_count += 1

        logger.info(f"Scheduled {scheduled_count} tasks")

        # Start the APScheduler
        self.scheduler.start()
        logger.info("✅ APScheduler started")

        # Verify scheduler is running
        logger.info(f"Scheduler running: {self.scheduler.running}")

        jobs = self.scheduler.get_jobs()
        logger.info(f"Jobs in scheduler: {len(jobs)}")
        for job in jobs:
            logger.info(f"  Job ID: {job.id}")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Task scheduler stopped")