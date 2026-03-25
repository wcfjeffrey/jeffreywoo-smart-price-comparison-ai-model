import asyncio
import json
from app.services.product_analyzer import ProductAnalyzer


async def test():
    analyzer = ProductAnalyzer()
    result = await analyzer.analyze_product("iPhone 17 Pro")

    print("=" * 60)
    print("FULL RESPONSE:")
    print("=" * 60)

    predictions = result.get('predictions', {})
    print("\n📊 PREDICTIONS:")
    print(json.dumps(predictions, indent=2))

    print("\n📈 SHORT-TERM:")
    short = predictions.get('short_term_trend', {})
    print(f"   Direction: {short.get('direction')}")
    print(f"   Change: {short.get('change_percent')}%")
    print(f"   Reasoning: {short.get('reasoning')}")

    print("\n📉 LONG-TERM:")
    long = predictions.get('long_term_trend', {})
    print(f"   Direction: {long.get('direction')}")
    print(f"   Change: {long.get('change_percent')}%")
    print(f"   Reasoning: {long.get('reasoning')}")


if __name__ == "__main__":
    asyncio.run(test())