import asyncio
import sys
import os

# Add the parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.chatanywhere_integration import ChatAnywhereIntegration

async def test_real_data():
    print("=" * 50)
    print("Testing Real API Integration with ChatAnywhere")
    print("=" * 50)
    
    api = ChatAnywhereIntegration()
    
    print("\n1. Testing API Connection...")
    print(f"   API Key: {'✓ Present' if api.api_key else '✗ Missing'}")
    print(f"   Base URL: {api.base_url}")
    
    if not api.api_key:
        print("\n❌ ERROR: No API key found!")
        print("Please add your API key to C:\\Projects\\SmartPriceComparison\\.env")
        return
    
    print("\n2. Fetching Real Price Data...")
    data = await api.fetch_price_data_from_api()
    
    if data and len(data) > 0:
        print(f"\n✅ Successfully fetched {len(data)} items:")
        print("-" * 50)
        for i, item in enumerate(data[:5], 1):
            print(f"{i}. {item.get('product_name', 'Unknown')} - {item.get('supplier', 'Unknown')}")
            print(f"   Price: ${item.get('price', 0)}")
            print(f"   Delivery: {item.get('delivery_time', 'N/A')} days")
            print(f"   Rating: {item.get('rating', 'N/A')}/5")
            print()
    else:
        print("⚠️ No data returned from API")
    
    print("\n3. Testing AI Analysis...")
    if data:
        analysis = await api.analyze_prices_with_ai(data)
        print(f"   Trend Analysis: {analysis.get('trend_analysis', 'N/A')[:150]}...")
        print(f"   Anomalies Detected: {len(analysis.get('anomalies', []))}")
        print(f"   Recommendations: {len(analysis.get('recommendations', []))}")
    
    print("\n4. Testing Report Generation...")
    if data:
        report = await api.generate_report_with_ai(analysis)
        print(f"   Report Preview: {report[:200]}...")
    
    print("\n" + "=" * 50)
    print("✅ API Integration Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_real_data())