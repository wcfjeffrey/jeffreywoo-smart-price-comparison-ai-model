from datetime import datetime, timedelta
import asyncio
from typing import Optional, List, Dict, Any
import logging
import os
import pickle

logger = logging.getLogger(__name__)


class GoogleIntegration:
    """Google Calendar and Gmail API integration"""
    
    def __init__(self):
        self.calendar_service = None
        self.gmail_service = None
        self._init_calendar()
    
    def _init_calendar(self):
        """Initialize Google Calendar service with OAuth2"""
        try:
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = None
            token_file = 'token.pickle'
            
            # Load existing token
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
                logger.info("✓ Loaded existing token")
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    logger.info("✓ Token refreshed")
                elif os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.info("✓ New token obtained")
                    with open(token_file, 'wb') as token:
                        pickle.dump(creds, token)
                    logger.info("✓ Token saved to token.pickle")
            
            if creds:
                self.calendar_service = build('calendar', 'v3', credentials=creds)
                logger.info("✅ Google Calendar service initialized")
                # Test connection
                calendar_list = self.calendar_service.calendarList().list().execute()
                calendars = calendar_list.get('items', [])
                if calendars:
                    logger.info(f"Connected to calendar: {calendars[0].get('summary')}")
            else:
                logger.warning("⚠️ No Google Calendar credentials found")
                
        except ImportError as e:
            logger.warning(f"Google API packages not installed: {e}")
        except Exception as e:
            logger.error(f"Google Calendar initialization error: {e}")
    
    async def create_calendar_event(self, summary: str, description: str, start_time: datetime, duration_minutes: int = 30):
        """Create Google Calendar event"""
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        if self.calendar_service:
            try:
                event = {
                    'summary': summary,
                    'description': description,
                    'start': {
                        'dateTime': start_time.isoformat(),
                        'timeZone': 'Asia/Hong_Kong',
                    },
                    'end': {
                        'dateTime': end_time.isoformat(),
                        'timeZone': 'Asia/Hong_Kong',
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 10},
                        ],
                    },
                }
                
                logger.info(f"Creating calendar event: {summary}")
                event_result = self.calendar_service.events().insert(
                    calendarId='primary', body=event
                ).execute()
                
                event_link = event_result.get('htmlLink', 'No link')
                logger.info(f"✅ Calendar event created: {event_link}")
                
                return {
                    "id": event_result.get('id'),
                    "link": event_link,
                    "summary": summary,
                    "start": start_time.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error creating calendar event: {e}")
                return {"error": str(e)}
        else:
            # Fallback to logging
            logger.warning(f"⚠️ Calendar service not available. Event would be created:")
            logger.warning(f"  Summary: {summary}")
            logger.warning(f"  Start: {start_time}")
            return {"id": "placeholder_event_id", "summary": summary, "warning": "Calendar service not available"}
    
    async def send_email(self, to: str, subject: str, body: str, attachments: Optional[list] = None):
        """Send email via Gmail API (placeholder for now)"""
        logger.info(f"Email (would be sent):")
        logger.info(f"  To: {to}")
        logger.info(f"  Subject: {subject}")
        return {"status": "success", "message": "Email would be sent"}
    
    async def get_calendar_events(self, time_min: datetime, time_max: datetime) -> List[Dict]:
        """Get calendar events within time range"""
        if self.calendar_service:
            try:
                events_result = self.calendar_service.events().list(
                    calendarId='primary',
                    timeMin=time_min.isoformat(),
                    timeMax=time_max.isoformat(),
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                return events_result.get('items', [])
            except Exception as e:
                logger.error(f"Error getting calendar events: {e}")
                return []
        return []
    
    async def add_calendar_reminder(self, task_id: str, task_name: str, scheduled_time: datetime):
        """Add a reminder for a scheduled task"""
        event_summary = f"Price Check: {task_name}"
        event_description = f"Scheduled price check for {task_name}. The system will analyze prices and send a report."
        
        return await self.create_calendar_event(
            summary=event_summary,
            description=event_description,
            start_time=scheduled_time,
            duration_minutes=15
        )
