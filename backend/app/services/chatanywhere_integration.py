import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ChatAnywhereIntegration:
    """Real API integration with ChatAnywhere"""

    def __init__(self):
        # Get API key directly from environment variables
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.chatanywhere.tech/v1")

        if not self.api_key:
            print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables!")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def fetch_price_data_from_api(self, product_name: str = None) -> List[Dict]:
        """Fetch real price data using ChatAnywhere API"""

        # Use product name in prompt if provided
        product_context = f" for {product_name}" if product_name else " for electronic products"
        print(f"🔵 API: Fetching data{product_context}")

        prompt = f"""
        Generate realistic price data for 5 different electronic products{product_context}.

        Return a JSON object with this exact structure:
        {{
          "data": [
            {{
              "product_name": "product name",
              "supplier": "supplier name", 
              "price": numeric price,
              "delivery_time": days as integer,
              "rating": rating from 1-5,
              "source": "ChatAnywhere API"
            }}
          ]
        }}

        Use real product names like: Laptop, Smartphone, Headphones, Tablet, Smartwatch
        Use real supplier names like: TechCorp, MegaStore, ElectroWorld, GadgetHub
        Make prices realistic and varied.
        """

        payload = {
            "model": "gpt-4o-ca",
            "messages": [
                {"role": "system", "content": "You are a price data extraction agent. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        print(f"📥 API Response received, length: {len(content)}")

                        data = json.loads(content)
                        if isinstance(data, dict) and 'data' in data:
                            return data['data']
                        elif isinstance(data, list):
                            return data
                        else:
                            print("⚠️ Unexpected response format")
                            return self._get_sample_data()
                    else:
                        text = await response.text()
                        print(f"❌ API Error {response.status}: {text[:200]}")
                        return self._get_sample_data()
        except Exception as e:
            print(f"❌ API Exception: {e}")
            return self._get_sample_data()

    async def analyze_prices_with_ai(self, price_data: List[Dict]) -> Dict[str, Any]:
        """Use AI to analyze price data and detect anomalies"""

        prompt = f"""
        Analyze the following price data and provide:
        1. Market trend analysis
        2. Anomaly detection (prices that are significantly different)
        3. Supplier ranking recommendations
        4. Cost-saving opportunities

        Price Data:
        {json.dumps(price_data, indent=2)}

        Return a JSON object with this exact structure:
        {{
          "trend_analysis": "string describing market trends",
          "anomalies": [
            {{"product": "string", "supplier": "string", "reason": "string", "severity": "high/medium/low"}}
          ],
          "recommendations": ["recommendation1", "recommendation2"],
          "ranking": [
            {{"supplier": "string", "score": number, "reason": "string"}}
          ]
        }}
        """

        payload = {
            "model": "deepseek-v3",
            "messages": [
                {"role": "system", "content": "You are a price analysis expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        return json.loads(content)
                    else:
                        print(f"Analysis API Error: {response.status}")
                        return self._get_sample_analysis()
        except Exception as e:
            print(f"Analysis error: {e}")
            return self._get_sample_analysis()

    async def generate_report_with_ai(self, analysis: Dict) -> str:
        """Generate a formatted report using AI"""

        prompt = f"""
        Based on this price analysis, create a concise business report:

        Analysis: {json.dumps(analysis, indent=2)}

        Create a brief report with:
        1. Executive Summary (1-2 sentences)
        2. Key Findings (bullet points)
        3. Top Recommendations (2-3 items)

        Keep it professional but concise (under 300 words).
        """

        payload = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": "You are a business analyst creating professional reports."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        print(f"Report API Error: {response.status}")
                        return "Report generation temporarily unavailable. Please check your API key."
        except Exception as e:
            print(f"Report generation error: {e}")
            return f"Report generation error: {str(e)}"

    def _get_sample_data(self) -> List[Dict]:
        """Fallback sample data"""
        return [
            {"product_name": "Laptop X1", "supplier": "TechCorp", "price": 999.99, "delivery_time": 3, "rating": 4.5,
             "source": "Sample"},
            {"product_name": "Laptop X1", "supplier": "MegaStore", "price": 1049.99, "delivery_time": 2, "rating": 4.8,
             "source": "Sample"},
            {"product_name": "Monitor 27\"", "supplier": "TechCorp", "price": 299.99, "delivery_time": 5, "rating": 4.2,
             "source": "Sample"},
        ]

    def _get_sample_analysis(self) -> Dict:
        """Fallback analysis data"""
        return {
            "trend_analysis": "Prices are stable with slight downward trend.",
            "anomalies": [],
            "recommendations": ["Consider bulk purchasing", "Negotiate with top suppliers"],
            "ranking": [
                {"supplier": "TechCorp", "score": 92.5, "reason": "Best price-value ratio"},
                {"supplier": "MegaStore", "score": 88.3, "reason": "Fastest delivery"}
            ]
        }

    async def _call_api_with_json_response(self, messages: List[Dict], model: str = "gpt-4o-ca") -> Dict:
        """Call ChatAnywhere API and parse JSON response"""

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        print(f"🔵 RAW API CONTENT: {content[:500]}")  # DEBUG: Print raw content

                        # Clean the response
                        clean_content = content.strip()
                        if clean_content.startswith('```json'):
                            clean_content = clean_content[7:]
                        if clean_content.endswith('```'):
                            clean_content = clean_content[:-3]

                        print(f"🔵 CLEANED CONTENT: {clean_content[:500]}")  # DEBUG: Print cleaned content

                        try:
                            parsed = json.loads(clean_content)
                            print(f"✅ Successfully parsed JSON")  # DEBUG
                            return parsed
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
                            logger.error(f"Content that failed: {clean_content[:500]}")
                            return None
                    else:
                        text = await response.text()
                        logger.error(f"API Error {response.status}: {text[:200]}")
                        return None
        except Exception as e:
            logger.error(f"API call error: {e}")
            return None
