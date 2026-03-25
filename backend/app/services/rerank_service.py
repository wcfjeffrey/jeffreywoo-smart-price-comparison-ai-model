"""
Rerank Model for Intelligent Supplier Ranking
Uses Cross-Encoder to rank suppliers based on relevance to ideal criteria
"""
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
from sentence_transformers import CrossEncoder
import torch

logger = logging.getLogger(__name__)


class RerankModel:
    """
    Cross-Encoder based reranking model for supplier evaluation
    Trained to understand trade-offs between price, delivery time, and rating
    """

    def __init__(self):
        # Use a pre-trained cross-encoder model for relevance scoring
        # This model understands the relationship between queries and documents
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.is_initialized = True
        logger.info("Rerank Model initialized successfully")

    def create_supplier_document(self, supplier: Dict) -> str:
        """Convert supplier data into a text document for ranking"""
        return f"Supplier {supplier.get('supplier')}. Price: ${supplier.get('price')}. Delivery: {supplier.get('delivery_time')} days. Rating: {supplier.get('rating')}/5 stars."

    def create_query(self, user_preferences: Dict = None) -> str:
        """Create the ideal supplier query based on user preferences"""
        if user_preferences:
            return f"Best supplier with priority on {user_preferences.get('priority', 'value')}. Budget: ${user_preferences.get('budget', 'flexible')}. Need fast delivery: {user_preferences.get('fast_delivery', False)}."
        # Default query - balanced approach
        return "Best supplier that offers good price, fast delivery, and high rating."

    def rank_suppliers(self, suppliers: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        """
        Rank suppliers using cross-encoder reranking
        Returns suppliers sorted by relevance score
        """
        if not suppliers:
            return []

        # Create query
        query = self.create_query(user_preferences)

        # Create documents for each supplier
        documents = [self.create_supplier_document(s) for s in suppliers]

        # Create pairs (query, document) for cross-encoder
        pairs = [(query, doc) for doc in documents]

        # Get relevance scores from cross-encoder
        scores = self.model.predict(pairs)

        # Normalize scores to 0-100 range
        min_score = np.min(scores)
        max_score = np.max(scores)
        if max_score > min_score:
            normalized_scores = (scores - min_score) / (max_score - min_score) * 100
        else:
            normalized_scores = np.ones_like(scores) * 50

        # Combine original supplier data with scores
        ranked_suppliers = []
        for i, supplier in enumerate(suppliers):
            ranked_suppliers.append({
                **supplier,
                "rerank_score": float(normalized_scores[i]),
                "raw_score": float(scores[i]),
                "ranking_rationale": self._generate_rationale(supplier, normalized_scores[i])
            })

        # Sort by rerank score (higher is better)
        ranked_suppliers.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Add rank numbers
        for i, supplier in enumerate(ranked_suppliers):
            supplier["rank"] = i + 1

        return ranked_suppliers

    def _generate_rationale(self, supplier: Dict, score: float) -> str:
        """Generate human-readable rationale for the ranking"""
        if score >= 80:
            return f"Excellent match! Good balance of price (${supplier.get('price')}), fast delivery ({supplier.get('delivery_time')} days), and high rating ({supplier.get('rating')}/5)."
        elif score >= 60:
            return f"Good option. {self._highlight_strength(supplier)}"
        elif score >= 40:
            return f"Average choice. Consider trade-offs: {self._highlight_tradeoff(supplier)}"
        else:
            return f"Not recommended. {self._highlight_weakness(supplier)}"

    def _highlight_strength(self, supplier: Dict) -> str:
        strengths = []
        if supplier.get('price', 1000) < 800:
            strengths.append("excellent price")
        if supplier.get('delivery_time', 5) <= 2:
            strengths.append("very fast delivery")
        if supplier.get('rating', 3) >= 4.5:
            strengths.append("top-rated supplier")
        return f"Key strengths: {', '.join(strengths)}." if strengths else "Balanced performance across all metrics."

    def _highlight_tradeoff(self, supplier: Dict) -> str:
        if supplier.get('price', 1000) > 1200:
            return f"Higher price (${supplier.get('price')}) but {supplier.get('delivery_time')}-day delivery"
        if supplier.get('delivery_time', 5) > 5:
            return f"Longer delivery ({supplier.get('delivery_time')} days) but good price"
        return "Moderate performance across metrics"

    def _highlight_weakness(self, supplier: Dict) -> str:
        weaknesses = []
        if supplier.get('price', 1000) > 1500:
            weaknesses.append("very expensive")
        if supplier.get('delivery_time', 5) > 7:
            weaknesses.append("very slow delivery")
        if supplier.get('rating', 3) < 3:
            weaknesses.append("poor rating")
        return f"Concerns: {', '.join(weaknesses)}." if weaknesses else "Generally weak performance"

    def compare_suppliers(self, supplier_a: Dict, supplier_b: Dict) -> Dict:
        """Compare two suppliers and determine which is better"""
        ranked = self.rank_suppliers([supplier_a, supplier_b])

        return {
            "winner": ranked[0],
            "loser": ranked[1],
            "winner_score": ranked[0]["rerank_score"],
            "loser_score": ranked[1]["rerank_score"],
            "recommendation": f"Choose {ranked[0]['supplier']} over {ranked[1]['supplier']} because {ranked[0]['ranking_rationale']}"
        }


# Singleton instance
rerank_model = RerankModel()