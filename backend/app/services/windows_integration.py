import os
import shutil
from datetime import datetime, timedelta
import asyncio
import subprocess
import logging

logger = logging.getLogger(__name__)


class WindowsIntegration:
    """Windows API integration for scheduling, messaging, and file organization"""

    async def send_desktop_notification(self, title: str, message: str):
        """Send Windows desktop notification"""
        try:
            # Using PowerShell to show toast notification
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
            $xml.LoadXml($template.GetXml())
            $textNodes = $xml.GetElementsByTagName("text")
            $textNodes.Item(0).AppendChild($xml.CreateTextNode("{title}")) | Out-Null
            $textNodes.Item(1).AppendChild($xml.CreateTextNode("{message}")) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("SmartPriceComparison").Show($toast)
            '''
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            logger.info(f"Desktop notification sent: {title}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    async def organize_files(self, file_paths: dict):
        """Organize files using Windows API"""
        base_dir = "reports"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        date_dir = os.path.join(base_dir, datetime.now().strftime("%Y-%m-%d"))
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)

        for file_type, file_path in file_paths.items():
            if os.path.exists(file_path):
                dest_path = os.path.join(date_dir, os.path.basename(file_path))
                shutil.move(file_path, dest_path)
                logger.info(f"Moved {file_path} to {dest_path}")

    async def schedule_task(self, task_name: str, schedule_time: datetime, command: str):
        """Schedule Windows task"""
        try:
            time_str = schedule_time.strftime("%H:%M")
            date_str = schedule_time.strftime("%Y/%m/%d")
            schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{command}" /sc once /st {time_str} /sd {date_str} /f'
            result = subprocess.run(schtasks_cmd, shell=True, capture_output=True)
            if result.returncode == 0:
                logger.info(f"Scheduled task '{task_name}' at {date_str} {time_str}")
            else:
                logger.error(f"Failed to schedule task: {result.stderr}")
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")