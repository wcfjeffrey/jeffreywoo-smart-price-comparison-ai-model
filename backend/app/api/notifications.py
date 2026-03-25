from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.notification_service import NotificationService
from app.models.task import NotificationPreferences
import logging

router = APIRouter()
notification_service = NotificationService()
logger = logging.getLogger(__name__)


class TestNotificationRequest(BaseModel):
    email: str
    product_name: str
    message: str


@router.post("/preferences")
async def save_notification_preferences(prefs: NotificationPreferences):
    """Save user notification preferences"""
    return {
        "status": "success",
        "message": "Preferences saved",
        "preferences": prefs.dict()
    }


@router.post("/test")
async def send_test_notification(request: TestNotificationRequest):
    """Send a test notification"""
    try:
        await notification_service.send_alert(
            request.email,
            request.product_name,
            "TEST NOTIFICATION",
            request.message
        )
        return {"status": "success", "message": "Test notification sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-email")
async def test_email(email: str, product_name: str):
    """Test email notification"""
    try:
        await notification_service.send_alert(
            email,
            product_name,
            "TEST NOTIFICATION",
            f"This is a test email from JeffreyWoo Smart Price Comparison System.\n\n"
            f"Your scheduled price checks for {product_name} are working correctly!\n\n"
            f"The system will automatically send you price alerts when:\n"
            f"- Prices change significantly\n"
            f"- Anomalies are detected\n"
            f"- Scheduled price checks complete\n\n"
            f"Best regards,\nJeffreyWoo Team"
        )
        return {
            "status": "success",
            "message": f"Test email sent to {email}",
            "product": product_name
        }
    except Exception as e:
        logger.error(f"Test email error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/calendar/test")
async def test_calendar(product_name: str):
    """Test calendar event creation"""
    try:
        from datetime import datetime, timedelta
        start_time = datetime.now() + timedelta(hours=1)

        # Create a test calendar event
        await notification_service._create_calendar_event(
            "test@example.com",
            product_name,
            {
                "best_supplier": {"supplier": "Test Supplier", "price": 999.99},
                "recommendations": ["Test recommendation 1", "Test recommendation 2"]
            }
        )
        return {
            "status": "success",
            "message": f"Test calendar event created for {product_name}",
            "event_time": start_time.isoformat()
        }
    except Exception as e:
        logger.error(f"Test calendar error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/preferences/{user_id}")
async def get_notification_preferences(user_id: str):
    """Get user notification preferences"""
    return {
        "status": "success",
        "preferences": {
            "email_enabled": True,
            "calendar_enabled": True,
            "alert_threshold": 10.0,
            "alert_on_anomaly": True,
            "report_format": "html"
        }
    }