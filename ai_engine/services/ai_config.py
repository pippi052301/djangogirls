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
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # You could log a warning instead of letting the app crash right at import time.
            print("⚠️ WARNING: GEMINI_API_KEY is not configured in the .env file.")
        _client = genai.Client(api_key=api_key)
    return _client