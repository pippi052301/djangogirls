import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Tải các biến môi trường
load_dotenv()

# Khởi tạo Client duy nhất để các file khác dùng chung
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))