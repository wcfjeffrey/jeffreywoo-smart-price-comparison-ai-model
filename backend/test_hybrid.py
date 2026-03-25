# Create test_hybrid.py
import asyncio
from app.services.hybrid_predictor import HybridPredictor


async def test():
    predictor = HybridPredictor()

    # Sample price data
    price_data = [
        {"supplier": "TechCorp", "price": 1299.99, "delivery_time": 3, "rating": 4.5},
        {"supplier": "MegaStore", "price": 1249.99, "delivery_time": 2, "rating": 4.8}
    ]

    result = await predictor.get_enhanced_predictions("iPhone 17 Pro", price_data)

    print("AI Predictions:", result.get('ai_predictions', {}))
    print("ML Predictions:", result.get('ml_predictions', {}))
    print("Hybrid Recommendation:", result.get('hybrid_recommendation', {}))


asyncio.run(test())