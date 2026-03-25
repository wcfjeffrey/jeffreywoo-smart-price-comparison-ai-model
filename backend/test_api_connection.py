import asyncio
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

async def test_api():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.chatanywhere.tech/v1")
    
    print(f"API Key: {'✓ Found' if api_key else '✗ Missing'}")
    print(f"Base URL: {base_url}")
    
    if not api_key:
        print("\n❌ ERROR: OPENAI_API_KEY not found in .env file!")
        print("Please add your API key to C:\\Projects\\SmartPriceComparison\\.env")
        return
    
    # Test the API connection
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-ca",
        "messages": [
            {"role": "user", "content": "Say 'API is working!'"}
        ],
        "max_tokens": 20
    }
    
    print("\nTesting API connection...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    message = result['choices'][0]['message']['content']
                    print(f"✓ API is working! Response: {message}")
                else:
                    text = await response.text()
                    print(f"✗ API Error: {response.status}")
                    print(f"Response: {text[:500]}")
                    
    except Exception as e:
        print(f"✗ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())