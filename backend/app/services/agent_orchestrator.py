import asyncio
from typing import Dict, List, Any
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.agent_a import DataFetcherAgent
from app.services.agent_b import AnalysisAgent
from app.services.agent_c import ReportAgent
from app.services.task_scheduler import TaskScheduler
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Multi-Agent workflow orchestrator"""

    def __init__(self):
        self.agent_a = DataFetcherAgent()
        self.agent_b = AnalysisAgent()
        self.agent_c = ReportAgent()
        self.task_scheduler = TaskScheduler()

    async def execute_price_comparison(self) -> Dict[str, Any]:
        """Execute complete price comparison workflow"""
        try:
            # Step 1: Fetch data
            fetched_data = await self.agent_a.fetch_price_data()

            # Step 2: Analyze
            analysis_result = await self.agent_b.analyze_prices(fetched_data)

            # Step 3: Generate report
            report = await self.agent_c.generate_report(analysis_result)

            # Step 4: Send notifications if anomalies detected
            if analysis_result.get('anomalies'):
                await self.send_anomaly_notifications(analysis_result['anomalies'])

            return {
                'status': 'success',
                'data': analysis_result,
                'report': report,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in execute_price_comparison: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def send_anomaly_notifications(self, anomalies: List[Dict]):
        """Send anomaly notifications"""
        for anomaly in anomalies:
            await self.agent_c.send_notification(anomaly)