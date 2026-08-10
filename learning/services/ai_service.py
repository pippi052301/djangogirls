import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# 1. KHỞI TẠO CLIENT (Chuẩn mới)
# Tự động tìm GEMINI_API_KEY trong file .env
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_quiz_from_text(text_content, num_questions=3):
    """
    Hàm nhận vào văn bản, gọi AI sinh câu hỏi trắc nghiệm và trả về List chứa các Dictionary.
    """
    
    # 2. PROMPT
    prompt = f"""
    Bạn là một chuyên gia giáo dục. Hãy đọc đoạn văn bản sau và tạo ra {num_questions} câu hỏi trắc nghiệm (4 đáp án A, B, C, D) bằng tiếng Nhật.
    
    YÊU CẦU:
    - Có 1 đáp án đúng duy nhất.
    - Cung cấp lời giải thích ngắn gọn tại sao đáp án đó đúng.
    
    Cấu trúc JSON yêu cầu:
    [
        {{
            "question": "Nội dung câu hỏi?",
            "options": {{
                "A": "Lựa chọn A",
                "B": "Lựa chọn B",
                "C": "Lựa chọn C",
                "D": "Lựa chọn D"
            }},
            "correct_answer": "A",
            "explanation": "Giải thích chi tiết."
        }}
    ]

    Văn bản gốc:
    \"\"\"{text_content}\"\"\"
    """
    
    try:
        # 3. GỌI API BẰNG SDK MỚI
        response = client.models.generate_content(
            model='gemini-3.6-flash', # Sử dụng model thế hệ mới
            contents=prompt,
            config=types.GenerateContentConfig(
                # TÍNH NĂNG ĐỈNH CAO: Ép AI trả về chuẩn JSON, không bị lẫn chữ thừa
                response_mime_type="application/json",
            ),
        )
        
        # 4. XỬ LÝ KẾT QUẢ
        quiz_data = json.loads(response.text)
        return quiz_data
        
    except json.JSONDecodeError as e:
        print(f"Lỗi: Không thể phân tích cú pháp JSON. Chi tiết: {e}")
        return None
    except Exception as e:
        print(f"Lỗi khi gọi API Gemini: {e}")
        return None