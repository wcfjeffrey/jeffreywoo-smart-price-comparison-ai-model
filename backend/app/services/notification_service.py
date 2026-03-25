import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import json
from typing import Dict, Any, Optional
import logging

from app.models.task import NotificationMethod

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles email and calendar notifications"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")

        # Import Google integration
        try:
            from app.services.google_integration import GoogleIntegration
            self.google_integration = GoogleIntegration()
        except ImportError as e:
            logger.warning(f"Google integration not available: {e}")
            self.google_integration = None

    async def send_price_report(
            self,
            email: str,
            product_name: str,
            analysis: Dict[str, Any],
            method: NotificationMethod
    ):
        """Send price report via specified method"""

        if method in [NotificationMethod.EMAIL, NotificationMethod.BOTH]:
            await self._send_email_report(email, product_name, analysis)

        if method in [NotificationMethod.CALENDAR, NotificationMethod.BOTH]:
            await self._create_calendar_event(email, product_name, analysis)

    async def _send_email_report(
            self,
            email: str,
            product_name: str,
            analysis: Dict[str, Any]
    ):
        """Send email with price report"""

        subject = f"Price Analysis Report for {product_name}"

        # Create HTML report
        html_content = self._generate_html_report(product_name, analysis)

        # Create plain text version
        text_content = self._generate_text_report(product_name, analysis)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_user
        msg['To'] = email

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Send email
        try:
            if self.email_user and self.email_password:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email_user, self.email_password)
                    server.send_message(msg)
                logger.info(f"Email sent to {email}")
            else:
                logger.info(f"Email (would be sent): {subject} to {email}")
        except Exception as e:
            logger.error(f"Error sending email: {e}")

    async def _create_calendar_event(
            self,
            email: str,
            product_name: str,
            analysis: Dict[str, Any]
    ):
        """Create Google Calendar event"""

        if self.google_integration:
            # Create event for 1 hour from now as a reminder
            start_time = datetime.now() + timedelta(hours=1)
            await self.google_integration.create_calendar_event(
                summary=f"Price Analysis: {product_name}",
                description=f"Review price analysis for {product_name}. Best price: ${analysis.get('best_supplier', {}).get('price', 0):.2f}",
                start_time=start_time,
                duration_minutes=30
            )
        else:
            logger.info(f"Calendar Event (would be created) for {product_name}")

    async def send_alert(
            self,
            email: str,
            product_name: str,
            alert_type: str,
            message: str
    ):
        """Send an alert notification"""

        subject = f"[ALERT] {alert_type} - {product_name}"
        body = f"""
        Alert Type: {alert_type}
        Product: {product_name}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        {message}

        View full analysis at: http://localhost:3000/
        """

        try:
            if self.email_user and self.email_password:
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = self.email_user
                msg['To'] = email

                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email_user, self.email_password)
                    server.send_message(msg)
                logger.info(f"Alert sent to {email}")
            else:
                logger.info(f"Alert (would be sent): {subject}")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")

    def _generate_html_report(self, product_name: str, analysis: Dict) -> str:
        """Generate HTML email content"""

        best_price = analysis.get('best_supplier', {})
        recommendations = analysis.get('recommendations', [])

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #4CAF50; color: white; padding: 10px; }}
                .best-price {{ font-size: 24px; color: #2196F3; }}
                .recommendation {{ background: #e8f5e9; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Price Analysis Report: {product_name}</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <h2>Best Price</h2>
            <p class="best-price">${best_price.get('price', 0):.2f}</p>
            <p>from {best_price.get('supplier', 'N/A')}</p>

            <h2>Recommendations</h2>
            <div class="recommendation">
                <ul>
                    {''.join([f"<li>{rec}</li>" for rec in recommendations[:5]])}
                </ul>
            </div>
        </body>
        </html>
        """
        return html

    def _generate_text_report(self, product_name: str, analysis: Dict) -> str:
        """Generate plain text email content"""

        best_price = analysis.get('best_supplier', {})
        recommendations = analysis.get('recommendations', [])

        text = f"""
Price Analysis Report: {product_name}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

========================================
BEST PRICE
========================================
${best_price.get('price', 0):.2f} from {best_price.get('supplier', 'N/A')}

========================================
RECOMMENDATIONS
========================================
"""
        for rec in recommendations[:5]:
            text += f"- {rec}\n"

        return text