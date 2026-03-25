from typing import Dict, List, Any
from datetime import datetime
from app.services.chatanywhere_integration import ChatAnywhereIntegration


class DataFetcherAgent:
    """Agent responsible for fetching supplier data using real API"""

    def __init__(self):
        self.api = ChatAnywhereIntegration()

    async def fetch_price_data(self) -> Dict[str, Any]:
        """Fetch real price data using ChatAnywhere API"""

        print("=" * 50)
        print("📊 DataFetcherAgent: Fetching real price data...")
        print(f"API Key present: {bool(self.api.api_key)}")
        print(f"Base URL: {self.api.base_url}")
        print("=" * 50)

        try:
            # Fetch real data from API
            data = await self.api.fetch_price_data_from_api()

            if data and len(data) > 0:
                print(f"✅ DataFetcherAgent: Successfully fetched {len(data)} items")
                return {
                    'data': data,
                    'fetch_time': datetime.now().isoformat(),
                    'source': 'chatanywhere_api_live'
                }
            else:
                print("⚠️ DataFetcherAgent: API returned empty data, using fallback")
                return self._get_fallback_data()

        except Exception as e:
            print(f"❌ DataFetcherAgent: Error fetching data: {e}")
            return self._get_fallback_data()

    async def fetch_price_data_for_product(self, product_name: str) -> Dict[str, Any]:
        """Fetch price data for a specific product"""

        print(f"📊 Fetching price data for: {product_name}")

        try:
            data = await self.api.fetch_price_data_from_api(product_name)

            filtered_data = [item for item in data if product_name.lower() in item.get('product_name', '').lower()]

            if filtered_data:
                return {
                    'data': filtered_data,
                    'fetch_time': datetime.now().isoformat(),
                    'source': 'chatanywhere_api_live',
                    'product': product_name
                }
            else:
                return self._get_fallback_for_product(product_name)

        except Exception as e:
            print(f"Error fetching product data: {e}")
            return self._get_fallback_for_product(product_name)

    def _get_fallback_data(self) -> Dict[str, Any]:
        """Fallback sample data if API fails"""
        return {
            'data': [
                {'product_name': 'Laptop X1', 'supplier': 'TechCorp', 'price': 999.99,
                 'delivery_time': 3, 'rating': 4.5},
                {'product_name': 'Laptop X1', 'supplier': 'MegaStore', 'price': 1049.99,
                 'delivery_time': 2, 'rating': 4.8},
                {'product_name': 'Monitor 27"', 'supplier': 'TechCorp', 'price': 299.99,
                 'delivery_time': 5, 'rating': 4.2},
            ],
            'fetch_time': datetime.now().isoformat(),
            'source': 'fallback_data'
        }

    def _get_fallback_for_product(self, product_name: str) -> Dict[str, Any]:
        """Fallback data for a specific product"""
        return {
            'data': [
                {'product_name': product_name, 'supplier': 'TechCorp', 'price': 999.99,
                 'delivery_time': 3, 'rating': 4.5},
                {'product_name': product_name, 'supplier': 'MegaStore', 'price': 1049.99,
                 'delivery_time': 2, 'rating': 4.8},
            ],
            'fetch_time': datetime.now().isoformat(),
            'source': 'fallback_data',
            'product': product_name
        }