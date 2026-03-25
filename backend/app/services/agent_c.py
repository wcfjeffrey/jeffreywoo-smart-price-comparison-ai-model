from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
from app.services.chatanywhere_integration import ChatAnywhereIntegration


class ReportAgent:
    """Agent responsible for report generation"""

    def __init__(self):
        self.api = ChatAnywhereIntegration()

    async def generate_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report"""

        print("📄 ReportAgent: Generating report...")

        try:
            # Generate AI-powered report
            report = await self.api.generate_report_with_ai(analysis_data)

            # Create CSV data
            csv_path = await self.create_csv_data(analysis_data)

            return {
                'summary': report[:500] if report else 'Report generated',
                'full_report': report,
                'csv_path': csv_path,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ ReportAgent: Error: {e}")
            return {
                'summary': 'Report generation in progress',
                'csv_path': None,
                'timestamp': datetime.now().isoformat()
            }

    async def create_csv_data(self, analysis_data: Dict) -> str:
        """Generate CSV data file"""
        import os

        filename = f"price_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"reports/{filename}"

        # Create reports directory if it doesn't exist
        os.makedirs('reports', exist_ok=True)

        df = pd.DataFrame(analysis_data.get('ranked_suppliers', []))
        df.to_csv(filepath, index=False)

        return filepath

    async def send_notification(self, anomaly_data: Dict[str, Any]):
        """Send anomaly notification with Windows integration"""

        # Send Windows desktop notification
        await self.windows_integration.send_desktop_notification(
            title="Price Anomaly Alert",
            message=f"Anomaly detected for {anomaly_data.get('product')}: {anomaly_data.get('reason')}"
        )

        # Schedule a follow-up task
        await self.windows_integration.schedule_task(
            task_name=f"Review {anomaly_data.get('product')} Price",
            schedule_time=datetime.now() + timedelta(hours=24),
            command="start http://localhost:3000"
        )

    async def send_email_report(self, report_data: Dict):
        """Send email report"""
        print(f"📧 Email report: {report_data.get('csv_path', 'No CSV')}")