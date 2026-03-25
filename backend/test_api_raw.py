import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()


async def test_raw_api():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.chatanywhere.tech/v1")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = """
    For iPhone 17 Pro, provide price predictions in JSON format with:
    short_term: {direction, change_percent, reasoning}
    long_term: {direction, change_percent, reasoning}
    recommended_timing, confidence_score, factors
    """

    payload = {
        "model": "gpt-4o-ca",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    print("Sending request...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            print(f"Status: {response.status}")
            result = await response.json()
            content = result['choices'][0]['message']['content']
            print("\n=== RAW API RESPONSE ===")
            print(content)
            print("\n=== END RAW RESPONSE ===")

            # Try to parse
            try:
                parsed = json.loads(content)
                print("\n✅ Successfully parsed JSON:")
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError as e:
                print(f"\n❌ Failed to parse JSON: {e}")


if __name__ == "__main__":
    asyncio.run(test_raw_api())