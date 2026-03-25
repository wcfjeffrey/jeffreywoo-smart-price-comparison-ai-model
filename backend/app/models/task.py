from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONCE = "once"

class NotificationMethod(str, Enum):
    EMAIL = "email"
    CALENDAR = "calendar"
    BOTH = "both"

class Task(BaseModel):
    id: str
    product_name: str
    frequency: Frequency
    time: str  # HH:MM format
    day_of_week: Optional[int] = None  # 0-6 for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly
    notification_method: NotificationMethod
    email: Optional[str] = None
    calendar_event_id: Optional[str] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    product_name: str
    frequency: Frequency
    time: str
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    notification_method: NotificationMethod
    email: Optional[str] = None

class TaskUpdate(BaseModel):
    product_name: Optional[str] = None
    frequency: Optional[Frequency] = None
    time: Optional[str] = None
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    notification_method: Optional[NotificationMethod] = None
    email: Optional[str] = None
    active: Optional[bool] = None

class NotificationPreferences(BaseModel):
    email_enabled: bool = False
    calendar_enabled: bool = False
    email_address: Optional[str] = None
    calendar_id: Optional[str] = None
    alert_threshold: float = 10.0  # Alert if price changes by >10%
    alert_on_anomaly: bool = True
    report_format: str = "json"  # json, csv, both