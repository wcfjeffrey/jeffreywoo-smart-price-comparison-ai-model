# backend/app/core/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL - MUST include +asyncpg
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password@localhost:5432/price_comparison")

print(f"Database URL: {DATABASE_URL.replace('password', '***')}")

# Verify driver is asyncpg
if '+asyncpg' not in DATABASE_URL:
    print("⚠️ WARNING: DATABASE_URL does not specify asyncpg driver. Adding it.")
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
    print(f"Corrected URL: {DATABASE_URL.replace('password', '***')}")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True)
    product_name = Column(String(255), nullable=False)
    frequency = Column(String(20), nullable=False)
    time = Column(String(10), nullable=False)
    day_of_week = Column(Integer, nullable=True)
    day_of_month = Column(Integer, nullable=True)
    notification_method = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    calendar_event_id = Column(String(255), nullable=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PriceHistoryModel(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(255), nullable=False)
    supplier = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    delivery_time = Column(Integer)
    rating = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)


class UserPreferenceModel(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    email_enabled = Column(Boolean, default=False)
    calendar_enabled = Column(Boolean, default=False)
    email_address = Column(String(255))
    calendar_id = Column(String(255))
    alert_threshold = Column(Float, default=10.0)
    alert_on_anomaly = Column(Boolean, default=True)
    report_format = Column(String(20), default="html")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class RecommendationLogModel(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(255), nullable=False)
    recommendation = Column(Text)
    ai_confidence = Column(Float)
    ml_confidence = Column(Float)
    hybrid_action = Column(String(50))
    was_accepted = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.now)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")


async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        yield session