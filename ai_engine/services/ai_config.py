import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    """Khởi tạo lười biếng (Lazy Initialization) cho Gemini Client."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Bạn có thể log ra cảnh báo thay vì để app sập ngay lúc import
            print("⚠️ CẢNH BÁO: Chưa cấu hình GEMINI_API_KEY trong file .env")
        _client = genai.Client(api_key=api_key)
    return _client