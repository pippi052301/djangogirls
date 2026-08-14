import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY chưa được cấu hình")

client = genai.Client(
    api_key=GEMINI_API_KEY
)