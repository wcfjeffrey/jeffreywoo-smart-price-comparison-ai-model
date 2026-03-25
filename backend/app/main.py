from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.api import price_compare, anomaly_detection, reports, schedule, tasks, products, notifications
from app.core.config import settings
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.windows_integration import WindowsIntegration
from app.services.google_integration import GoogleIntegration
from app.core.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Initialize database
    try:
        await init_db()
        logger.info("✅ PostgreSQL database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    app.state.agent_orchestrator = orchestrator
    app.state.windows_integration = WindowsIntegration()
    app.state.google_integration = GoogleIntegration()

    # FORCE START THE SCHEDULER
    logger.info("=" * 60)
    logger.info("FORCE STARTING TASK SCHEDULER")
    logger.info("=" * 60)

    # Load tasks from database
    await orchestrator.task_scheduler._load_tasks_from_db()
    logger.info(f"Loaded {len(orchestrator.task_scheduler.tasks)} tasks")

    # Start the scheduler
    orchestrator.task_scheduler.start()

    logger.info(f"Scheduler running: {orchestrator.task_scheduler.scheduler.running}")

    jobs = orchestrator.task_scheduler.scheduler.get_jobs()
    logger.info(f"Jobs in scheduler: {len(jobs)}")
    for job in jobs:
        logger.info(f"  Job ID: {job.id}")

    logger.info("=" * 60)
    logger.info("Application started successfully")

    yield

    # Cleanup on shutdown
    orchestrator.task_scheduler.stop()
    logger.info("Application shutdown")


app = FastAPI(
    title="Smart Price Comparison System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(price_compare.router, prefix="/api/price", tags=["price"])
app.include_router(anomaly_detection.router, prefix="/api/anomaly", tags=["anomaly"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])


@app.get("/")
async def root():
    return {"message": "Smart Price Comparison System API"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }