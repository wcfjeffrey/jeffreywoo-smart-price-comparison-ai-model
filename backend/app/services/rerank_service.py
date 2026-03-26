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
    Hybrid approach: combines deterministic scoring (price, delivery, rating) with semantic relevance.
    """

    def __init__(self):
        # Use a pre-trained cross-encoder model for relevance scoring
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.is_initialized = True
        # Weights for deterministic scoring (adjustable)
        self.price_weight = 0.5
        self.delivery_weight = 0.2
        self.rating_weight = 0.3
        # Hybrid blend factor (0 = only cross-encoder, 1 = only deterministic)
        self.alpha = 0.7
        logger.info("Rerank Model initialized successfully")

    def create_supplier_document(self, supplier: Dict, min_price: float, max_price: float,
                                 min_delivery: int, max_delivery: int,
                                 min_rating: float, max_rating: float) -> str:
        """
        Convert supplier data into a rich text document that includes comparative context.
        """
        price_desc = self._price_description(supplier.get('price'), min_price, max_price)
        delivery_desc = self._delivery_description(supplier.get('delivery_time'), min_delivery, max_delivery)
        rating_desc = self._rating_description(supplier.get('rating'), min_rating, max_rating)

        return (f"Supplier {supplier.get('supplier')}. {price_desc} {delivery_desc} {rating_desc} "
                f"Price: ${supplier.get('price')}, Delivery: {supplier.get('delivery_time')} days, "
                f"Rating: {supplier.get('rating')}/5 stars.")

    def create_query(self, user_preferences: Dict = None) -> str:
        """Create the ideal supplier query based on user preferences"""
        if user_preferences:
            return (f"Best supplier with priority on {user_preferences.get('priority', 'value')}. "
                    f"Budget: ${user_preferences.get('budget', 'flexible')}. "
                    f"Need fast delivery: {user_preferences.get('fast_delivery', False)}.")
        # Default query - balanced approach
        return "Best supplier that offers good price, fast delivery, and high rating."

    def _price_description(self, price: float, min_price: float, max_price: float) -> str:
        if price == min_price:
            return "Price is the lowest among all suppliers."
        elif price == max_price:
            return "Price is the highest among all suppliers."
        else:
            return f"Price is ${price}, which is in the mid range."

    def _delivery_description(self, days: int, min_delivery: int, max_delivery: int) -> str:
        if days == min_delivery:
            return "Delivery is the fastest available."
        elif days == max_delivery:
            return "Delivery is the slowest available."
        else:
            return f"Delivery takes {days} days, which is average."

    def _rating_description(self, rating: float, min_rating: float, max_rating: float) -> str:
        if rating == max_rating:
            return "Rating is the highest among all suppliers."
        elif rating == min_rating:
            return "Rating is the lowest among all suppliers."
        else:
            return f"Rating is {rating}/5, which is average."

    def _deterministic_score(self, supplier: Dict, min_price: float, max_price: float,
                             min_delivery: int, max_delivery: int,
                             min_rating: float, max_rating: float) -> float:
        """Compute normalized deterministic score (0-100) based on price, delivery, rating."""
        # Avoid division by zero
        price_range = max_price - min_price if max_price != min_price else 1
        delivery_range = max_delivery - min_delivery if max_delivery != min_delivery else 1
        rating_range = max_rating - min_rating if max_rating != min_rating else 1

        norm_price = (max_price - supplier['price']) / price_range
        norm_delivery = (max_delivery - supplier['delivery_time']) / delivery_range
        norm_rating = (supplier['rating'] - min_rating) / rating_range

        score = (self.price_weight * norm_price +
                 self.delivery_weight * norm_delivery +
                 self.rating_weight * norm_rating) * 100
        return score

    def rank_suppliers(self, suppliers: List[Dict], user_preferences: Dict = None) -> List[Dict]:
        """
        Rank suppliers using hybrid approach:
        1. Compute deterministic score based on price, delivery, rating.
        2. Enrich documents with comparative context.
        3. Get cross-encoder scores.
        4. Combine both scores (alpha * deterministic + (1-alpha) * normalized CE score).
        """
        if not suppliers:
            return []

        # Extract metrics for normalization
        prices = [s.get('price', 0) for s in suppliers]
        deliveries = [s.get('delivery_time', 0) for s in suppliers]
        ratings = [s.get('rating', 0) for s in suppliers]

        min_price, max_price = min(prices), max(prices)
        min_delivery, max_delivery = min(deliveries), max(deliveries)
        min_rating, max_rating = min(ratings), max(ratings)

        # Compute deterministic scores
        deterministic_scores = []
        documents = []
        for supplier in suppliers:
            det_score = self._deterministic_score(supplier, min_price, max_price,
                                                   min_delivery, max_delivery,
                                                   min_rating, max_rating)
            deterministic_scores.append(det_score)

            doc = self.create_supplier_document(supplier, min_price, max_price,
                                                 min_delivery, max_delivery,
                                                 min_rating, max_rating)
            documents.append(doc)

        # Get cross-encoder scores
        query = self.create_query(user_preferences)
        pairs = [(query, doc) for doc in documents]
        ce_scores = self.model.predict(pairs)

        # Normalize cross-encoder scores to 0-100
        ce_min = np.min(ce_scores)
        ce_max = np.max(ce_scores)
        if ce_max > ce_min:
            ce_norm = (ce_scores - ce_min) / (ce_max - ce_min) * 100
        else:
            ce_norm = np.ones_like(ce_scores) * 50

        # Hybrid final scores
        final_scores = self.alpha * np.array(deterministic_scores) + (1 - self.alpha) * ce_norm

        # Build ranked list
        ranked_suppliers = []
        for i, supplier in enumerate(suppliers):
            ranked_suppliers.append({
                **supplier,
                "rerank_score": float(final_scores[i]),
                "deterministic_score": deterministic_scores[i],
                "cross_encoder_score": float(ce_norm[i]),
                "raw_score": float(ce_scores[i]),
                "ranking_rationale": self._generate_rationale(supplier, final_scores[i])
            })

        # Sort by final score descending
        ranked_suppliers.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Add rank numbers
        for i, supplier in enumerate(ranked_suppliers):
            supplier["rank"] = i + 1

        return ranked_suppliers

    # --- rationale methods unchanged ---
    def _generate_rationale(self, supplier: Dict, score: float) -> str:
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
