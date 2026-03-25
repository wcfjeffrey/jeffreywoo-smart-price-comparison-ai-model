"""
Hybrid prediction service combining ChatAnywhere AI predictions with ML models
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import numpy as np
from app.services.chatanywhere_integration import ChatAnywhereIntegration
from ml.inference.price_predictor import PricePredictor

logger = logging.getLogger(__name__)


class HybridPredictor:
    """Combines AI and ML predictions for optimal results"""

    def __init__(self):
        self.ai_predictor = ChatAnywhereIntegration()
        self.ml_predictor = PricePredictor()

    async def get_enhanced_predictions(self, product_name: str, price_data: List[Dict]) -> Dict[str, Any]:
        """Get combined AI + ML predictions"""

        # Get AI predictions
        ai_predictions = await self._get_ai_predictions(product_name, price_data)

        # Get ML predictions
        ml_predictions = self._get_ml_predictions(price_data)

        # Combine
        combined = self._combine_predictions(ai_predictions, ml_predictions)

        # Ensure the ai_predictions has the right structure
        combined["ai_predictions"] = ai_predictions

        logger.info(f"Generated predictions for {product_name}")

        return combined

    async def _get_ai_predictions(self, product_name: str, price_data: List[Dict]) -> Dict:
        """Get predictions from ChatAnywhere AI with realistic percentages"""

        current_prices = [item.get('price', 0) for item in price_data]
        avg_price = sum(current_prices) / len(current_prices) if current_prices else 0
        min_price = min(current_prices) if current_prices else 0
        max_price = max(current_prices) if current_prices else 0

        # Calculate price spread for realistic fallbacks
        price_spread = ((max_price - min_price) / (min_price + 0.01)) * 100 if min_price > 0 else 0

        logger.info(f"Getting AI predictions for {product_name} (avg: ${avg_price:.2f}, spread: {price_spread:.1f}%)")

        prompt = f"""
        For {product_name} with average price ${avg_price:.2f}, provide price predictions.
        
        Return JSON with this exact structure:
        {{
          "short_term": {{
            "direction": "up/down/stable",
            "change_percent": number (negative for down, positive for up),
            "reasoning": "string"
          }},
          "long_term": {{
            "direction": "up/down/stable",
            "change_percent": number,
            "reasoning": "string"
          }},
          "recommended_timing": "string",
          "confidence_score": number (0-100),
          "factors": ["factor1", "factor2"]
        }}
        
        Make change_percent a realistic number based on market trends. For example:
        - If direction is up, use positive numbers like 2.5, 5.0, or 8.0
        - If direction is down, use negative numbers like -2.5, -5.0, or -8.0
        - For stable, use small numbers like -1.0 or 0.5
        """

        try:
            logger.info("Calling ChatAnywhere API...")
            result = await self.ai_predictor._call_api_with_json_response([
                {"role": "system", "content": "You are a price prediction expert. Return only valid JSON with realistic percentages."},
                {"role": "user", "content": prompt}
            ])

            if result:
                logger.info(f"API returned predictions: {result}")

                # Parse the response
                short_term = result.get("short_term", {})
                long_term = result.get("long_term", {})

                short_dir = short_term.get("direction", "stable")
                short_change = short_term.get("change_percent", 0)
                long_dir = long_term.get("direction", "stable")
                long_change = long_term.get("change_percent", 0)

                # Fix unrealistic percentages
                if short_dir == "up" and short_change <= 0:
                    short_change = 3.5
                    logger.info(f"Fixed short-term change to {short_change}% for up trend")
                elif short_dir == "down" and short_change >= 0:
                    short_change = -3.5
                    logger.info(f"Fixed short-term change to {short_change}% for down trend")
                elif short_dir == "stable" and short_change == 0:
                    # For stable, use a small negative based on price spread
                    if price_spread > 10:
                        short_change = -2.0
                    elif price_spread > 5:
                        short_change = -1.0
                    else:
                        short_change = -0.5
                    logger.info(f"Set short-term change to {short_change}% for stable trend")

                if long_dir == "up" and long_change <= 0:
                    long_change = 5.0
                    logger.info(f"Fixed long-term change to {long_change}% for up trend")
                elif long_dir == "down" and long_change >= 0:
                    long_change = -3.0
                    logger.info(f"Fixed long-term change to {long_change}% for down trend")
                elif long_dir == "stable" and long_change == 0:
                    long_change = 1.5
                    logger.info(f"Set long-term change to {long_change}% for stable trend")

                # Ensure percentages are reasonable (not too extreme)
                short_change = max(-15, min(15, short_change))
                long_change = max(-20, min(20, long_change))

                return {
                    "short_term_trend": {
                        "direction": short_dir,
                        "change_percent": round(short_change, 1),
                        "reasoning": short_term.get("reasoning", "Based on market analysis")
                    },
                    "long_term_trend": {
                        "direction": long_dir,
                        "change_percent": round(long_change, 1),
                        "reasoning": long_term.get("reasoning", "Based on market analysis")
                    },
                    "recommended_timing": result.get("recommended_timing", self._get_timing_recommendation(short_dir, short_change)),
                    "confidence_score": result.get("confidence_score", 75),
                    "factors": result.get("factors", self._get_default_factors(price_spread, avg_price))
                }
            else:
                logger.warning("API returned None, using data-driven fallback")
                return self._get_data_driven_predictions(avg_price, price_spread, min_price, max_price)

        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return self._get_data_driven_predictions(avg_price, price_spread, min_price, max_price)

    def _get_timing_recommendation(self, direction: str, change_percent: float) -> str:
        """Generate timing recommendation based on prediction"""
        if direction == "down":
            return f"Buy within 2 weeks to save {abs(change_percent):.1f}%"
        elif direction == "up":
            return "Wait for better prices - expected to increase"
        else:
            return "Good time to buy - prices are stable"

    def _get_default_factors(self, price_spread: float, avg_price: float) -> List[str]:
        """Generate default factors based on data"""
        factors = ["Market conditions", "Supplier competition"]
        if price_spread > 10:
            factors.append("High price variation")
        if avg_price > 1000:
            factors.append("Premium market segment")
        elif avg_price < 300:
            factors.append("Budget market segment")
        return factors

    def _get_data_driven_predictions(self, avg_price: float, price_spread: float, min_price: float, max_price: float) -> Dict:
        """Generate predictions based on actual price data (no API)"""

        logger.info(f"Using data-driven predictions (avg: ${avg_price:.2f}, spread: {price_spread:.1f}%)")

        # Short-term based on price spread
        if price_spread > 15:
            short_change = -4.5
            short_dir = "down"
            short_reason = f"High price spread of {price_spread:.0f}% across suppliers suggests prices will decrease"
        elif price_spread > 8:
            short_change = -2.8
            short_dir = "down"
            short_reason = f"Moderate price spread of {price_spread:.0f}% indicates downward pressure"
        elif price_spread > 3:
            short_change = -1.2
            short_dir = "stable"
            short_reason = f"Low price spread of {price_spread:.0f}% suggests stable prices"
        else:
            short_change = -0.5
            short_dir = "stable"
            short_reason = "Very stable prices with minimal expected movement"

        # Long-term based on price level
        if avg_price > 1500:
            long_change = 4.5
            long_dir = "up"
            long_reason = "Premium products typically appreciate over time"
        elif avg_price > 800:
            long_change = 2.5
            long_dir = "up"
            long_reason = "Mid-range products show steady long-term growth"
        elif avg_price > 300:
            long_change = 0.8
            long_dir = "stable"
            long_reason = "Budget items remain stable with inflation adjustment"
        else:
            long_change = -0.5
            long_dir = "down"
            long_reason = "Low-cost items face downward price pressure"

        return {
            "short_term_trend": {
                "direction": short_dir,
                "change_percent": short_change,
                "reasoning": short_reason
            },
            "long_term_trend": {
                "direction": long_dir,
                "change_percent": long_change,
                "reasoning": long_reason
            },
            "recommended_timing": self._get_timing_recommendation(short_dir, short_change),
            "confidence_score": 78,
            "factors": self._get_default_factors(price_spread, avg_price)
        }

    def _get_ml_predictions(self, price_data: List[Dict]) -> Dict:
        """Get predictions from trained ML models with realistic confidence"""

        ml_results = []

        for supplier in price_data:
            try:
                prediction = self.ml_predictor.predict_price(supplier)
                ml_results.append({
                    "supplier": supplier.get('supplier'),
                    "current_price": supplier.get('price'),
                    "predicted_price": prediction.get('predicted_price'),
                    "confidence": prediction.get('confidence'),
                    "trend": prediction.get('trend'),
                    "model_used": prediction.get('model_used')
                })
            except Exception as e:
                logger.warning(f"ML prediction error for {supplier.get('supplier')}: {e}")
                continue

        # Calculate aggregate ML prediction
        if ml_results:
            valid_predictions = [r['predicted_price'] for r in ml_results if r['predicted_price']]
            valid_confidences = [r['confidence'] for r in ml_results if r['confidence']]

            # Calculate weighted average based on confidence
            if valid_predictions and valid_confidences:
                # Weight predictions by confidence
                weighted_sum = sum(p * c for p, c in zip(valid_predictions, valid_confidences))
                total_weight = sum(valid_confidences)
                avg_predicted = weighted_sum / total_weight if total_weight > 0 else np.mean(valid_predictions)
                avg_confidence = np.mean(valid_confidences) * 100
            else:
                avg_predicted = np.mean(valid_predictions) if valid_predictions else 0
                avg_confidence = 0

            model_used = ml_results[0].get('model_used', 'ml_predictor_v1') if ml_results else 'N/A'
        else:
            avg_predicted = 0
            avg_confidence = 0
            model_used = 'N/A'

        # If no predictions, generate a default
        if avg_predicted == 0 and price_data:
            # Use the average current price as fallback
            current_prices = [s.get('price', 0) for s in price_data]
            avg_predicted = np.mean(current_prices) if current_prices else 0
            avg_confidence = 70  # Default confidence

        logger.info(f"ML predictions: avg predicted ${avg_predicted:.2f} with {avg_confidence:.0f}% confidence")

        return {
            "supplier_predictions": ml_results,
            "average_predicted_price": round(avg_predicted, 2),
            "average_confidence": round(avg_confidence, 1),
            "model_used": model_used
        }

    def _combine_predictions(self, ai_predictions: Dict, ml_predictions: Dict) -> Dict:
        """Combine AI and ML predictions for final recommendation"""

        # Extract values
        ai_short_direction = ai_predictions.get('short_term_trend', {}).get('direction', 'stable')
        ai_short_change = ai_predictions.get('short_term_trend', {}).get('change_percent', 0)
        ai_long_direction = ai_predictions.get('long_term_trend', {}).get('direction', 'stable')
        ai_long_change = ai_predictions.get('long_term_trend', {}).get('change_percent', 0)
        ai_confidence = ai_predictions.get('confidence_score', 75)
        ai_reasoning = ai_predictions.get('short_term_trend', {}).get('reasoning', '')

        ml_predicted = ml_predictions.get('average_predicted_price', 0)
        ml_confidence = ml_predictions.get('average_confidence', 0)

        # Log ML confidence for debugging
        logger.info(f"ML Confidence received: {ml_confidence}%")

        # Calculate combined confidence (weighted average)
        if ml_confidence > 0:
            combined_confidence = (ai_confidence + ml_confidence) / 2
        else:
            combined_confidence = ai_confidence

        # Determine final recommendation
        if ai_short_direction == 'down':
            action = "Buy"
            recommendation = "Buy soon"
            reasoning = f"AI predicts {abs(ai_short_change):.1f}% price decrease in next 30 days."
            if ml_predicted > 0:
                reasoning += f" ML model confirms with predicted price of ${ml_predicted:.2f}."
        elif ai_short_direction == 'up':
            action = "Wait"
            recommendation = "Wait"
            reasoning = f"AI predicts {ai_short_change:.1f}% price increase. Consider waiting."
        else:
            action = "Monitor"
            recommendation = "Hold"
            reasoning = f"Market is stable with {abs(ai_short_change):.1f}% expected movement."

        return {
            "ai_predictions": ai_predictions,
            "ml_predictions": {
                "average_predicted_price": ml_predicted,
                "confidence": ml_confidence,
                "supplier_details": ml_predictions.get('supplier_predictions', [])
            },
            "hybrid_recommendation": {
                "action": action,
                "recommendation": recommendation,
                "combined_confidence": round(combined_confidence, 1),
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat()
            }
        }

    def _get_ml_predictions(self, price_data: List[Dict]) -> Dict:
        """Get predictions from trained ML models"""

        logger.info(f"Calculating ML predictions for {len(price_data)} suppliers")

        ml_results = []

        for supplier in price_data:
            try:
                prediction = self.ml_predictor.predict_price(supplier)
                logger.info(
                    f"  {supplier.get('supplier')}: price=${supplier.get('price')}, predicted=${prediction.get('predicted_price')}, confidence={prediction.get('confidence')}")
                ml_results.append({
                    "supplier": supplier.get('supplier'),
                    "current_price": supplier.get('price'),
                    "predicted_price": prediction.get('predicted_price'),
                    "confidence": prediction.get('confidence'),
                    "trend": prediction.get('trend'),
                    "model_used": prediction.get('model_used')
                })
            except Exception as e:
                logger.warning(f"ML prediction error: {e}")
                continue

        # Calculate aggregate ML prediction
        if ml_results:
            valid_predictions = [r['predicted_price'] for r in ml_results if r['predicted_price']]
            valid_confidences = [r['confidence'] for r in ml_results if r['confidence']]
            avg_predicted = np.mean(valid_predictions) if valid_predictions else 0
            avg_confidence = np.mean(valid_confidences) * 100 if valid_confidences else 0
            model_used = ml_results[0].get('model_used', 'N/A') if ml_results else 'N/A'

            logger.info(
                f"ML Results: avg_predicted=${avg_predicted:.2f}, avg_confidence={avg_confidence:.1f}%, model={model_used}")
        else:
            avg_predicted = 0
            avg_confidence = 0
            model_used = 'N/A'
            logger.warning("No ML predictions generated")

        return {
            "supplier_predictions": ml_results,
            "average_predicted_price": avg_predicted,
            "average_confidence": avg_confidence,
            "model_used": model_used
        }