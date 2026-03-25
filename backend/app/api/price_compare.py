from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import asyncio
import logging
from app.services.agent_orchestrator import AgentOrchestrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Create a single instance of the orchestrator
orchestrator = AgentOrchestrator()


@router.get("/latest")
async def get_latest_prices():
    """Get latest price data from real API"""
    try:
        logger.info("Fetching latest prices from real API...")

        # Fetch real data from the agent
        result = await orchestrator.agent_a.fetch_price_data()

        # Log what we got
        logger.info(f"Fetched {len(result.get('data', []))} items from source: {result.get('source', 'unknown')}")

        # Transform data to match frontend expected format
        transformed_data = []
        for item in result.get('data', []):
            transformed_data.append({
                "product_name": item.get('product_name', 'Unknown Product'),
                "supplier": item.get('supplier', 'Unknown Supplier'),
                "price": float(item.get('price', 0)),
                "delivery_time": int(item.get('delivery_time', 3)),
                "rating": float(item.get('rating', 4.0)),
                "trend": item.get('trend', 'stable')  # Add trend if available
            })

        return {
            "status": "success",
            "data": transformed_data,
            "source": result.get('source', 'unknown'),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching latest prices: {e}", exc_info=True)
        # Fallback to sample data
        return {
            "status": "error",
            "message": str(e),
            "data": [
                {"product_name": "Laptop X1", "supplier": "Supplier A", "price": 999.99, "delivery_time": 3,
                 "rating": 4.5, "trend": "stable"},
                {"product_name": "Laptop X1", "supplier": "Supplier B", "price": 1049.99, "delivery_time": 2,
                 "rating": 4.8, "trend": "up"},
                {"product_name": "Monitor 27\"", "supplier": "Supplier A", "price": 299.99, "delivery_time": 5,
                 "rating": 4.2, "trend": "down"},
            ],
            "timestamp": datetime.now().isoformat()
        }


@router.get("/ranked")
async def get_ranked_suppliers():
    """Get ranked suppliers from real analysis"""
    try:
        logger.info("Fetching ranked suppliers...")

        # First fetch data
        price_data = await orchestrator.agent_a.fetch_price_data()
        logger.info(f"Fetched {len(price_data.get('data', []))} items for ranking")

        # Then analyze it
        analysis = await orchestrator.agent_b.analyze_prices(price_data)

        # Get ranked suppliers from analysis
        ranked_suppliers = analysis.get('ranked_suppliers', [])

        # Add rank numbers if not present
        for i, supplier in enumerate(ranked_suppliers):
            if 'rank' not in supplier:
                supplier['rank'] = i + 1

        return {
            "status": "success",
            "data": ranked_suppliers,
            "analysis": analysis.get('analysis', ''),
            "recommendations": analysis.get('recommendations', []),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching ranked suppliers: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "data": [
                {"rank": 1, "supplier": "Supplier B", "price": 1049.99, "delivery_time": 2, "rating": 4.8,
                 "score": 95.5},
                {"rank": 2, "supplier": "Supplier A", "price": 999.99, "delivery_time": 3, "rating": 4.5,
                 "score": 92.3},
                {"rank": 3, "supplier": "Supplier C", "price": 1099.99, "delivery_time": 4, "rating": 4.3,
                 "score": 85.2},
            ],
            "timestamp": datetime.now().isoformat()
        }


@router.get("/trends")
async def get_price_trends(product: str = None):
    """Get price trends from real analysis"""
    try:
        logger.info("Fetching price trends...")

        price_data = await orchestrator.agent_a.fetch_price_data()
        analysis = await orchestrator.agent_b.analyze_prices(price_data)

        return {
            "status": "success",
            "data": {
                "trend_analysis": analysis.get('analysis', ''),
                "recommendations": analysis.get('recommendations', []),
                "anomalies": analysis.get('anomalies', [])
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error fetching trends: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "data": {
                "trends": [
                    {"date": "2024-01-01", "avg_price": 1020.00},
                    {"date": "2024-01-08", "avg_price": 1015.00},
                    {"date": "2024-01-15", "avg_price": 1025.00},
                ]
            }
        }


@router.get("/test-real-data")
async def test_real_data():
    """Test endpoint to verify real API data is working"""
    try:
        logger.info("Testing real data endpoint...")

        result = await orchestrator.agent_a.fetch_price_data()
        data = result.get('data', [])

        return {
            "status": "success",
            "message": "Real API is working!",
            "data": data[:3],  # Show first 3 items
            "source": result.get('source', 'unknown'),
            "total_count": len(data),
            "sample": data[0] if data else None,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in test endpoint: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }


@router.get("/debug")
async def debug_info():
    """Debug endpoint to check what's happening"""
    try:
        # Check if agents are initialized
        agents_status = {
            "agent_a": hasattr(orchestrator, 'agent_a'),
            "agent_b": hasattr(orchestrator, 'agent_b'),
            "agent_c": hasattr(orchestrator, 'agent_c')
        }

        # Try to fetch data
        result = await orchestrator.agent_a.fetch_price_data()

        return {
            "status": "success",
            "agents": agents_status,
            "data_source": result.get('source', 'unknown'),
            "data_count": len(result.get('data', [])),
            "first_item": result.get('data', [])[0] if result.get('data') else None,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Debug error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }