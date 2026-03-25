from typing import Dict, List, Any
from datetime import datetime
import numpy as np
from app.services.chatanywhere_integration import ChatAnywhereIntegration
from app.services.rerank_service import rerank_model
import logging

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Agent responsible for price analysis with rerank models"""

    def __init__(self):
        self.api = ChatAnywhereIntegration()

    async def analyze_prices(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price data with rerank model"""

        logger.info("📈 AnalysisAgent: Analyzing prices with rerank model...")

        try:
            # Use AI for deep analysis
            analysis = await self.api.analyze_prices_with_ai(price_data['data'])

            # Calculate supplier rankings using rerank model
            ranked_suppliers = self._rank_suppliers_with_rerank(price_data['data'])

            logger.info(f"✅ AnalysisAgent: Analysis complete with rerank scores")

            return {
                'predictions': analysis.get('predictions', []),
                'anomalies': analysis.get('anomalies', []),
                'ranked_suppliers': ranked_suppliers,
                'analysis': analysis.get('trend_analysis', 'Prices are stable'),
                'recommendations': analysis.get('recommendations', []),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ AnalysisAgent: Error: {e}")
            return self._get_fallback_analysis(price_data['data'])

    def _rank_suppliers_with_rerank(self, data: List[Dict]) -> List[Dict]:
        """Rank suppliers using cross-encoder rerank model"""

        # Prepare supplier data for rerank
        suppliers = []
        for item in data:
            supplier = {
                'supplier': item.get('supplier', 'Unknown'),
                'price': item.get('price', 0),
                'delivery_time': item.get('delivery_time', 5),
                'rating': item.get('rating', 3),
                'product_name': item.get('product_name', '')
            }
            suppliers.append(supplier)

        # Use rerank model to get intelligent rankings
        ranked_suppliers = rerank_model.rank_suppliers(suppliers)

        # Format for frontend display
        formatted = []
        for s in ranked_suppliers:
            formatted.append({
                'supplier': s['supplier'],
                'price': s['price'],
                'delivery_time': s['delivery_time'],
                'rating': s['rating'],
                'score': s['rerank_score'],
                'rationale': s['ranking_rationale'],
                'rank': s['rank']
            })

        return formatted

    def _get_fallback_analysis(self, data: List[Dict]) -> Dict[str, Any]:
        """Fallback analysis"""
        return {
            'predictions': [],
            'anomalies': [],
            'ranked_suppliers': self._rank_suppliers_with_rerank(data),
            'analysis': 'Prices are stable with minor fluctuations.',
            'recommendations': ['Consider bulk purchasing', 'Monitor price trends'],
            'timestamp': datetime.now().isoformat()
        }