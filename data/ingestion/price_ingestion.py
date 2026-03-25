"""
Data ingestion pipeline for price data
"""
import asyncio
import aiohttp
import json
import os
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any


class PriceDataIngestion:
    """Data ingestion pipeline for price data from various sources"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.chatanywhere.tech/v1")

    async def fetch_from_chatanywhere(self, product_name: str) -> List[Dict]:
        """Fetch price data from ChatAnywhere API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"Generate realistic price data for {product_name} from 3-5 suppliers. Return as JSON."

        payload = {
            "model": "gpt-4o-ca",
            "messages": [
                {"role": "system", "content": "You are a price data generator. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        data = json.loads(content)
                        if isinstance(data, dict) and 'data' in data:
                            return data['data']
                        return data if isinstance(data, list) else []
                    return []
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    async def ingest_product_data(self, products: List[str]) -> pd.DataFrame:
        """Ingest price data for multiple products"""
        all_data = []

        for product in products:
            data = await self.fetch_from_chatanywhere(product)
            for item in data:
                item['ingestion_timestamp'] = datetime.now().isoformat()
                all_data.append(item)

        # Convert to DataFrame
        df = pd.DataFrame(all_data)

        # Save raw data
        self._save_raw_data(df)

        return df

    def _save_raw_data(self, df: pd.DataFrame):
        """Save raw ingested data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/ingestion/raw_prices_{timestamp}.parquet"
        df.to_parquet(filename, index=False)
        print(f"Saved raw data to {filename}")

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform ingested data for warehouse"""
        # Add derived columns
        df['price_category'] = pd.cut(df['price'],
                                      bins=[0, 500, 1000, 1500, float('inf')],
                                      labels=['Budget', 'Mid', 'Premium', 'Luxury'])
        df['delivery_category'] = pd.cut(df['delivery_time'],
                                         bins=[0, 2, 5, float('inf')],
                                         labels=['Fast', 'Standard', 'Slow'])
        df['score'] = (1000 / df['price']) + (30 / df['delivery_time']) + (df['rating'] * 20)

        return df

    def load_to_warehouse(self, df: pd.DataFrame, table_name: str):
        """Load transformed data to warehouse"""
        filename = f"data/warehouse/{table_name}.parquet"
        df.to_parquet(filename, index=False)
        print(f"Loaded data to warehouse: {filename}")


# Example usage
if __name__ == "__main__":
    async def main():
        ingestor = PriceDataIngestion()
        df = await ingestor.ingest_product_data(["iPhone 17 Pro", "Samsung Galaxy S25", "MacBook Pro"])
        df_transformed = ingestor.transform_data(df)
        ingestor.load_to_warehouse(df_transformed, "price_comparison")


    asyncio.run(main())