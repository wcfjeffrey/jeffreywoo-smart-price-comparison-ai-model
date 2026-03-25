# backend/app/core/config.py
import os
from typing import Optional


# Simple config without pydantic-settings (if you're having issues)
class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.chatanywhere.tech/v1")

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/price_comparison")

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Google API Configuration
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    # Email Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER: Optional[str] = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")

    # MLflow Configuration
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

    # Spark Configuration
    SPARK_MASTER_URL: str = os.getenv("SPARK_MASTER_URL", "spark://localhost:7077")


settings = Settings()