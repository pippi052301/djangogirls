import json
from .ai_config import get_client, types # Nhập Client dùng chung từ file cấu hình

def generate_quiz_from_text(text_content, num_questions=3):
    """Sinh câu hỏi trắc nghiệm thông thường."""
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
        response = get_client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Lỗi khi gọi API sinh Quiz: {e}")
        return None