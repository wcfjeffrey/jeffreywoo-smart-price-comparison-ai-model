from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.services.product_analyzer import ProductAnalyzer

router = APIRouter()
analyzer = ProductAnalyzer()
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def analyze_product(product_name: str, background_tasks: BackgroundTasks = None):
    """Analyze a specific product"""
    try:
        result = await analyzer.analyze_product(product_name)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error analyzing product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{product_name}")
async def get_product_analysis(product_name: str):
    """Get analysis for a specific product"""
    try:
        result = await analyzer.analyze_product(product_name)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error analyzing product: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{product_name}")
async def compare_product_prices(product_name: str):
    """Compare prices for a specific product"""
    try:
        result = await analyzer.analyze_product(product_name)

        # Debug: Log what we received
        logger.info(f"Analyzer result type: {type(result)}")

        # Ensure result is a dictionary
        if isinstance(result, list):
            # If result is a list, wrap it in a dictionary
            logger.warning(f"Result is a list, wrapping in dictionary")
            analysis_data = {
                "data": result,
                "suppliers": result,
                "product_name": product_name,
                "best_supplier": {},
                "price_range": {"min": 0, "max": 0},
                "recommendations": [],
                "predictions": {},
                "ml_predictions": {},
                "hybrid_recommendation": {},
                "risk_analysis": {}
            }
        elif isinstance(result, dict):
            # Result is already a dictionary
            analysis_data = result
        else:
            # Unknown type, create empty dict
            logger.error(f"Unexpected result type: {type(result)}")
            analysis_data = {}

        # Format comparison data
        comparison = {
            "product_name": product_name,
            "suppliers": result.get('data', []),
            "best_price": result.get('best_supplier', {}),
            "price_range": result.get('price_range', {"min": 0, "max": 0}),
            "recommendations": result.get('recommendations', []),
            "predictions": analysis_data.get('predictions', {}),
            "ml_predictions": analysis_data.get("ml_predictions", {}),
            "hybrid_recommendation": analysis_data.get("hybrid_recommendation", {}),
            "risk_analysis": analysis_data.get("risk_analysis", {}),
        }

        # Debug: Log what we're returning
        logger.info(f"Returning comparison for {product_name}")
        logger.info(f"Predictions present: {bool(comparison.get('predictions'))}")
        logger.info(f"Short-term prediction: {comparison.get('predictions', {}).get('short_term_trend', {}).get('direction', 'N/A')}")
        logger.info(f"Short-term change: {comparison.get('predictions', {}).get('short_term_trend', {}).get('change_percent', 0)}%")

        return {
            "status": "success",
            "data": comparison
        }
    except Exception as e:
        logger.error(f"Error comparing prices for {product_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/ml-predict/{product_name}")
async def get_ml_predictions(product_name: str):
    """Get ML model-based price predictions"""
    try:
        # Get product data
        product_data = await analyzer.analyze_product(product_name)

        # Get ML predictions
        from ml.inference.price_predictor import PricePredictor
        predictor = PricePredictor()

        ml_predictions = []
        for supplier in product_data.get('suppliers', []):
            prediction = predictor.predict_price(supplier)
            ml_predictions.append({
                "supplier": supplier.get('supplier'),
                "current_price": supplier.get('price'),
                "ml_predicted_price": prediction.get('predicted_price'),
                "confidence": prediction.get('confidence'),
                "trend": prediction.get('trend'),
                "model_used": prediction.get('model_used')
            })

        return {
            "status": "success",
            "product": product_name,
            "ai_predictions": product_data.get('predictions', {}),
            "ml_predictions": ml_predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"ML prediction error: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/rl-optimize/{product_name}")
async def rl_optimize(product_name: str):
    """Get reinforcement learning optimization strategy"""
    try:
        # Import RL modules
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ml_path = os.path.join(project_root, '..', 'ml')
        sys.path.insert(0, ml_path)

        from reinforcement_learning.procurement_env import ProcurementEnvironment, procurement_agent

        # Create environment for this product
        env = ProcurementEnvironment()
        state, _ = env.reset()

        # Get optimal strategy
        strategy = procurement_agent.get_best_strategy(env, state)

        # Get product data for context
        product_data = await analyzer.analyze_product(product_name)

        # Generate insights
        insights = {
            "product": product_name,
            "recommended_action": strategy,
            "action_mapping": {
                "Buy Now": "Purchase immediately at current price - best for urgent needs or when prices are low",
                "Wait 1 Day": "Monitor prices for 1 day - good for short-term price watching",
                "Wait 3 Days": "Monitor for 3 days before purchasing - ideal for moderate price fluctuations",
                "Wait 1 Week": "Delay purchase by 1 week - best when expecting price drops",
                "Buy Bulk": "Purchase larger quantity for discount - optimal for high-volume needs"
            },
            "current_state": {
                "price": float(env.current_price),
                "inventory": int(env.inventory),
                "days_left": int(env.days_left)
            },
            "product_context": {
                "current_best_price": product_data.get('best_supplier', {}).get('price', 0),
                "supplier_count": len(product_data.get('suppliers', [])),
                "price_trend": product_data.get('predictions', {}).get('short_term_trend', {}).get('direction',
                                                                                                   'stable')
            },
            "learning_status": {
                "trained_episodes": len(procurement_agent.q_table),
                "exploration_rate": procurement_agent.epsilon,
                "q_table_size": len(procurement_agent.q_table),
                "model_status": "trained" if len(procurement_agent.q_table) > 0 else "untrained"
            },
            "recommendation": _generate_rl_recommendation(strategy, product_data)
        }

        return {
            "status": "success",
            "data": insights,
            "framework": "OpenAI Gym (Reinforcement Learning)",
            "algorithm": "Q-Learning"
        }

    except ImportError as e:
        logger.warning(f"RL modules not available: {e}")
        return {
            "status": "warning",
            "message": "Reinforcement Learning module not fully configured. Run training first: python ml/reinforcement_learning/train_agent.py",
            "setup_instructions": "1. Install gymnasium: pip install gymnasium\n2. Run training: python ml/reinforcement_learning/train_agent.py"
        }
    except Exception as e:
        logger.error(f"RL optimization error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "suggestion": "Make sure RL modules are installed and trained"
        }


def _generate_rl_recommendation(strategy: str, product_data: Dict) -> str:
    """Generate human-readable recommendation based on RL strategy"""
    best_price = product_data.get('best_supplier', {}).get('price', 0)
    price_trend = product_data.get('predictions', {}).get('short_term_trend', {}).get('direction', 'stable')

    if strategy == "Buy Now":
        if price_trend == 'down':
            return f"⚠️ RL recommends BUY NOW, but AI predicts prices may drop. Consider waiting for better prices."
        else:
            return f"✅ RL recommends BUY NOW at ${best_price:.2f}. Current prices are favorable."

    elif strategy == "Wait 1 Day":
        return f"⏰ RL recommends WAIT 1 DAY. Prices may improve slightly. Monitor closely."

    elif strategy == "Wait 3 Days":
        return f"📅 RL recommends WAIT 3 DAYS. Short-term price movements expected."

    elif strategy == "Wait 1 Week":
        if price_trend == 'down':
            return f"📉 RL recommends WAIT 1 WEEK. AI predicts price decrease, aligning with RL strategy."
        else:
            return f"📊 RL recommends WAIT 1 WEEK. Patience may yield better prices."

    elif strategy == "Buy Bulk":
        return f"📦 RL recommends BULK PURCHASE. Volume discount opportunity detected."

    return f"RL suggests: {strategy}. Monitor market conditions."

@router.post("/clear-cache/{product_name}")
async def clear_product_cache(product_name: str):
    """Clear cached analysis for a product"""
    try:
        analyzer.clear_cache(product_name)
        return {
            "status": "success",
            "message": f"Cache cleared for {product_name}"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-all-cache")
async def clear_all_cache():
    """Clear all cached analyses"""
    try:
        analyzer.clear_cache()
        return {
            "status": "success",
            "message": "All cache cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))