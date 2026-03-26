from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.services.agent_a import DataFetcherAgent
from app.services.agent_b import AnalysisAgent
from app.services.hybrid_predictor import HybridPredictor

# Simple in-memory cache
_analysis_cache = {}
_CACHE_DURATION = timedelta(minutes=5)  # Cache for 5 minutes


class ProductAnalyzer:
    """Specialized analyzer for specific products with hybrid predictions"""

    def __init__(self):
        self.data_fetcher = DataFetcherAgent()
        self.analysis_agent = AnalysisAgent()
        self.hybrid_predictor = HybridPredictor()

    async def analyze_product(self, product_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """Comprehensive analysis for a specific product with hybrid predictions"""

        # Check cache first
        if use_cache:
            cached = self._get_cached_analysis(product_name)
            if cached:
                logger.info(f"Returning cached analysis for {product_name}")
                return cached

        try:
            # Step 1: Fetch product-specific data
            product_data = await self.data_fetcher.fetch_price_data_for_product(product_name)
            suppliers_data = product_data.get('data', [])

            # Step 2: Analyze with AI
            analysis = await self.analysis_agent.analyze_prices(product_data)

            # Step 3: Get hybrid predictions (AI + ML)
            hybrid_predictions = await self.hybrid_predictor.get_enhanced_predictions(
                product_name, suppliers_data
            )

            # Get the AI predictions
            raw_ai_predictions = hybrid_predictions.get("ai_predictions", {})

            # Transform to match frontend expected format
            short_term = raw_ai_predictions.get("short_term_trend", raw_ai_predictions.get("short_term", {}))
            long_term = raw_ai_predictions.get("long_term_trend", raw_ai_predictions.get("long_term", {}))

            transformed_predictions = {
                "short_term_trend": {
                    "direction": short_term.get("direction", "stable"),
                    "change_percent": short_term.get("change_percent", 0),
                    "reasoning": short_term.get("reasoning", "Analysis in progress")
                },
                "long_term_trend": {
                    "direction": long_term.get("direction", "stable"),
                    "change_percent": long_term.get("change_percent", 0),
                    "reasoning": long_term.get("reasoning", "Analysis in progress")
                },
                "recommended_timing": raw_ai_predictions.get("recommended_timing", "Monitor market"),
                "confidence_score": raw_ai_predictions.get("confidence_score", 75),
                "factors": raw_ai_predictions.get("factors", ["Market conditions"])
            }

            # Step 4: Generate enhanced risk analysis (with predictions)
            risk_analysis = await self._analyze_risks_enhanced(product_data, analysis, transformed_predictions)

            logger.info(
                f"Risk analysis result: risk_score={risk_analysis.get('risk_score')}, risk_level={risk_analysis.get('risk_level')}, risks_count={len(risk_analysis.get('risks', []))}")

            # Step 5: Generate recommendations
            recommendations = await self._generate_recommendations(
                product_data, analysis, hybrid_predictions, risk_analysis
            )

            result = {
                "product_name": product_name,
                "timestamp": datetime.now().isoformat(),
                "data": suppliers_data,
                "suppliers": suppliers_data,
                "analysis": analysis,
                "predictions": transformed_predictions,
                "ml_predictions": hybrid_predictions.get("ml_predictions", {}),
                "hybrid_recommendation": hybrid_predictions.get("hybrid_recommendation", {}),
                "risk_analysis": risk_analysis,
                "recommendations": recommendations,
                "best_supplier": self._get_best_supplier(analysis.get('ranked_suppliers', [])),
                "price_range": {
                    "min": min([s.get('price', 0) for s in suppliers_data]) if suppliers_data else 0,
                    "max": max([s.get('price', 0) for s in suppliers_data]) if suppliers_data else 0
                }
            }

            # Cache the result
            self._cache_analysis(product_name, result)

            return result

        except Exception as e:
            return self._get_fallback_data(product_name)

    def _get_cached_analysis(self, product_name: str) -> Dict | None:
        """Get cached analysis if still valid"""
        if product_name in _analysis_cache:
            cached_data, cached_time = _analysis_cache[product_name]
            if datetime.now() - cached_time < _CACHE_DURATION:
                return cached_data
            else:
                # Remove expired cache
                del _analysis_cache[product_name]
        return None

    def _cache_analysis(self, product_name: str, data: Dict):
        """Cache analysis result"""
        _analysis_cache[product_name] = (data, datetime.now())

    def clear_cache(self, product_name: str = None):
        """Clear cache for specific product or all"""
        if product_name:
            _analysis_cache.pop(product_name, None)
        else:
            _analysis_cache.clear()

    async def _analyze_risks_enhanced(self, product_data: Dict, analysis: Dict, predictions: Dict) -> Dict:
        """Enhanced risk analysis based on actual data and predictions"""
        suppliers = product_data.get('data', [])
        anomalies = analysis.get('anomalies', [])

        risks = []
        risk_score = 0

        # 1. Check for price anomalies from AI analysis
        if anomalies:
            for anomaly in anomalies:
                risks.append({
                    "type": "price_anomaly",
                    "severity": "high",
                    "description": f"Price anomaly detected: {anomaly.get('reason', 'Unusual price pattern')}"
                })
                risk_score += 30

        # 2. Check for limited suppliers (supply chain risk)
        if len(suppliers) < 2:
            risks.append({
                "type": "limited_supply",
                "severity": "high",
                "description": f"Only {len(suppliers)} supplier available - high dependency risk"
            })
            risk_score += 35
        elif len(suppliers) < 3:
            risks.append({
                "type": "limited_supply",
                "severity": "medium",
                "description": f"Only {len(suppliers)} suppliers available - limited alternatives"
            })
            risk_score += 20

        # 3. Calculate price volatility (spread between suppliers)
        if len(suppliers) >= 2:
            prices = [s.get('price', 0) for s in suppliers]
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)

            if avg_price > 0:
                price_spread_percent = ((max_price - min_price) / avg_price) * 100

                if price_spread_percent > 20:
                    risks.append({
                        "type": "high_volatility",
                        "severity": "high",
                        "description": f"Extreme price variation of {price_spread_percent:.1f}% across suppliers"
                    })
                    risk_score += 25
                elif price_spread_percent > 10:
                    risks.append({
                        "type": "moderate_volatility",
                        "severity": "medium",
                        "description": f"Moderate price variation of {price_spread_percent:.1f}% across suppliers"
                    })
                    risk_score += 15
                elif price_spread_percent > 5:
                    risks.append({
                        "type": "low_volatility",
                        "severity": "low",
                        "description": f"Low price variation of {price_spread_percent:.1f}% across suppliers"
                    })
                    risk_score += 5

        # 4. Check for delivery time risks
        if suppliers:
            delivery_times = [s.get('delivery_time', 0) for s in suppliers]
            avg_delivery = sum(delivery_times) / len(delivery_times)

            if avg_delivery > 10:
                risks.append({
                    "type": "long_delivery",
                    "severity": "medium",
                    "description": f"Average delivery time of {avg_delivery:.0f} days - may affect urgent needs"
                })
                risk_score += 15
            elif avg_delivery > 7:
                risks.append({
                    "type": "moderate_delivery",
                    "severity": "low",
                    "description": f"Average delivery time of {avg_delivery:.0f} days - plan accordingly"
                })
                risk_score += 5

        # 5. Check for price trends (from predictions)
        short_term_trend = predictions.get('short_term_trend', {})
        short_dir = short_term_trend.get('direction', 'stable')
        short_change = short_term_trend.get('change_percent', 0)

        if short_dir == 'up' and short_change > 0:
            if short_change > 10:
                risks.append({
                    "type": "rapid_price_increase",
                    "severity": "high",
                    "description": f"Expected {short_change:.1f}% price increase in next 30 days - act soon"
                })
                risk_score += 20
            elif short_change > 5:
                risks.append({
                    "type": "price_increase",
                    "severity": "medium",
                    "description": f"Expected {short_change:.1f}% price increase in next 30 days"
                })
                risk_score += 10
            elif short_change > 0:
                risks.append({
                    "type": "price_increase",
                    "severity": "low",
                    "description": f"Expected {short_change:.1f}% price increase - monitor market"
                })
                risk_score += 5
        elif short_dir == 'down' and short_change < 0:
            change_abs = abs(short_change)
            if change_abs > 10:
                risks.append({
                    "type": "sharp_price_drop",
                    "severity": "medium",
                    "description": f"Expected {change_abs:.1f}% price drop - wait for better prices"
                })
                risk_score += 5

        # 6. Check for rating risks
        if suppliers:
            ratings = [s.get('rating', 0) for s in suppliers]
            avg_rating = sum(ratings) / len(ratings)

            if avg_rating < 3.0:
                risks.append({
                    "type": "low_rating",
                    "severity": "high",
                    "description": f"Average supplier rating of {avg_rating:.1f}/5 - quality concerns"
                })
                risk_score += 20
            elif avg_rating < 4.0:
                risks.append({
                    "type": "moderate_rating",
                    "severity": "low",
                    "description": f"Average supplier rating of {avg_rating:.1f}/5 - acceptable but not excellent"
                })
                risk_score += 5

        # Determine risk level
        if risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Generate recommendations based on risks
        risk_recommendations = []
        for risk in risks:
            if risk['type'] == 'limited_supply':
                risk_recommendations.append("Consider diversifying supplier base to reduce dependency risk")
            elif risk['type'] in ['high_volatility', 'moderate_volatility']:
                risk_recommendations.append("Monitor prices across multiple suppliers to catch the best deals")
            elif risk['type'] in ['long_delivery', 'moderate_delivery']:
                risk_recommendations.append("Order well in advance to accommodate delivery times")
            elif risk['type'] in ['price_increase', 'rapid_price_increase']:
                risk_recommendations.append("Consider purchasing soon before expected price increases")
            elif risk['type'] == 'sharp_price_drop':
                risk_recommendations.append("Wait for expected price drop to get better value")
            elif risk['type'] == 'low_rating':
                risk_recommendations.append("Verify quality with samples before bulk purchase")

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risks": risks,
            "recommendations": risk_recommendations
        }

    async def _generate_recommendations(self, product_data: Dict, analysis: Dict,
                                        hybrid_predictions: Dict, risk_analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Best supplier recommendation
        best_supplier = self._get_best_supplier(analysis.get('ranked_suppliers', []))
        if best_supplier:
            recommendations.append(
                f"Best value: Purchase from {best_supplier.get('supplier')} at ${best_supplier.get('price', 0):.2f}")

        # Hybrid recommendation
        hybrid_rec = hybrid_predictions.get('hybrid_recommendation', {})
        if hybrid_rec.get('recommendation'):
            recommendations.append(f"Strategy: {hybrid_rec.get('recommendation')}")

        # Timing recommendation from predictions
        predictions = hybrid_predictions.get('ai_predictions', {})
        timing = predictions.get('recommended_timing', '')
        if timing:
            recommendations.append(f"Optimal timing: {timing}")

        # Risk-based recommendations
        if risk_analysis.get('risk_level') == 'high':
            recommendations.append("⚠️ High risk detected - proceed with caution")

        # Add risk-specific recommendations
        risk_recommendations = risk_analysis.get('recommendations', [])
        recommendations.extend(risk_recommendations)

        # Trend-based recommendations
        short_term = predictions.get('short_term_trend', {})
        if short_term.get('direction') == 'down':
            recommendations.append(
                f"📉 Prices trending downward - consider waiting 1-2 weeks to save {abs(short_term.get('change_percent', 0)):.1f}%")
        elif short_term.get('direction') == 'up':
            recommendations.append("📈 Prices trending upward - consider buying soon")

        if not recommendations:
            recommendations.append("Prices are stable. Good time to purchase.")

        return recommendations

    def _get_best_supplier(self, ranked_suppliers: List[Dict]) -> Dict:
        """Get the best supplier recommendation"""
        if ranked_suppliers:
            return ranked_suppliers[0]
        return {}

    def _get_fallback_data(self, product_name: str) -> Dict:
        """Return fallback data"""
        return {
            "product_name": product_name,
            "timestamp": datetime.now().isoformat(),
            "data": [
                {"product_name": product_name, "supplier": "TechCorp", "price": 999.99, "delivery_time": 3,
                 "rating": 4.5},
                {"product_name": product_name, "supplier": "MegaStore", "price": 1049.99, "delivery_time": 2,
                 "rating": 4.8}
            ],
            "suppliers": [
                {"product_name": product_name, "supplier": "TechCorp", "price": 999.99, "delivery_time": 3,
                 "rating": 4.5},
                {"product_name": product_name, "supplier": "MegaStore", "price": 1049.99, "delivery_time": 2,
                 "rating": 4.8}
            ],
            "best_supplier": {"supplier": "MegaStore", "price": 1049.99},
            "price_range": {"min": 999.99, "max": 1049.99},
            "recommendations": ["Best price found at MegaStore", "Consider bulk purchasing"],
            "predictions": {
                "short_term_trend": {"direction": "stable", "change_percent": 0, "reasoning": "Analysis in progress"},
                "long_term_trend": {"direction": "stable", "change_percent": 0, "reasoning": "Analysis in progress"},
                "recommended_timing": "Monitor market",
                "confidence_score": 75
            },
            "ml_predictions": {"average_predicted_price": 0, "confidence": 0},
            "hybrid_recommendation": {
                "action": "Monitor",
                "recommendation": "Hold",
                "combined_confidence": 0,
                "reasoning": "Data unavailable"
            },
            "risk_analysis": {
                "risk_score": 0,
                "risk_level": "low",
                "risks": [],
                "recommendations": []
            }
        }
