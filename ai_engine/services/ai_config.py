import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    """Lazy Initialization for Gemini Client."""
    global _client
    if _client is None:
        api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if not api_key:
            load_dotenv(override=True)
            api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if not api_key:
            print("⚠️ WARNING: GEMINI_API_KEY is not configured in the .env file.")
        _client = genai.Client(api_key=api_key)
    return _client