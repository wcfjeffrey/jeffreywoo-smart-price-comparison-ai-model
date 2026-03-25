from fastapi import APIRouter
from datetime import datetime
import logging
from app.services.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)
router = APIRouter()
orchestrator = AgentOrchestrator()


@router.get("/detected")
async def get_anomalies():
    """Get detected anomalies from real analysis"""
    try:
        logger.info("Fetching anomalies...")

        # Fetch and analyze data
        price_data = await orchestrator.agent_a.fetch_price_data()
        analysis = await orchestrator.agent_b.analyze_prices(price_data)

        anomalies = analysis.get('anomalies', [])

        # Add detected_at timestamp if not present
        for anomaly in anomalies:
            if 'detected_at' not in anomaly:
                anomaly['detected_at'] = datetime.now().isoformat()

        return {
            "status": "success",
            "data": anomalies,
            "analysis_summary": analysis.get('analysis', ''),
            "recommendations": analysis.get('recommendations', []),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "data": [
                {
                    "product": "Laptop X1",
                    "supplier": "Supplier C",
                    "anomaly_score": 0.85,
                    "reason": "Price 15% above market average",
                    "detected_at": datetime.now().isoformat()
                }
            ]
        }