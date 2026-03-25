"""
Debug script to test product predictions
"""
import asyncio
import json
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.product_analyzer import ProductAnalyzer


async def debug_predictions():
    print("=" * 60)
    print("DEBUG: Testing Product Predictions")
    print("=" * 60)

    analyzer = ProductAnalyzer()

    # Test with iPhone
    print("\n1. Testing iPhone 17 Pro...")
    result = await analyzer.analyze_product("iPhone 17 Pro")

    predictions = result.get('predictions', {})
    print("\n📊 Predictions:")
    print(json.dumps(predictions, indent=2))

    print("\n📈 Supplier Data:")
    for s in result.get('suppliers', [])[:3]:
        print(f"   {s.get('supplier')}: ${s.get('price')}")

    # Test with another product
    print("\n" + "=" * 60)
    print("2. Testing MacBook Pro...")
    result2 = await analyzer.analyze_product("MacBook Pro")

    predictions2 = result2.get('predictions', {})
    print("\n📊 Predictions:")
    print(json.dumps(predictions2, indent=2))

    print("\n📈 Supplier Data:")
    for s in result2.get('suppliers', [])[:3]:
        print(f"   {s.get('supplier')}: ${s.get('price')}")


if __name__ == "__main__":
    asyncio.run(debug_predictions())