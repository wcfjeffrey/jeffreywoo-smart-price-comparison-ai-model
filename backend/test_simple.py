print("Testing imports...")

try:
    import aiohttp
    print(f"✓ aiohttp version: {aiohttp.__version__}")
except ImportError as e:
    print(f"✗ aiohttperror: {e}")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv found")
except ImportError as e:
    print(f"✗ dotenv error: {e}")