import json
from .ai_config import client, types


def validate_quiz_data(data):
    """
    Kiểm tra dữ liệu Quiz do AI trả về có đúng cấu trúc không.
    """

    # Quiz phải là một list
    if not isinstance(data, list):
        return False

    # Kiểm tra từng câu hỏi
    for question in data:

        required_fields = [
            "question",
            "options",
            "correct_answer",
            "explanation",
        ]

        # Kiểm tra các field bắt buộc
        for field in required_fields:
            if field not in question:
                return False

        # options phải là dictionary
        if not isinstance(question["options"], dict):
            return False

        # Phải có đúng 4 đáp án A, B, C, D
        if set(question["options"].keys()) != {"A", "B", "C", "D"}:
            return False

        # correct_answer phải là A/B/C/D
        if question["correct_answer"] not in ["A", "B", "C", "D"]:
            return False

    return True


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
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        # Chuyển JSON text từ Gemini thành Python list
        result = json.loads(response.text)

        # Kiểm tra cấu trúc dữ liệu
        if not validate_quiz_data(result):
            print("AI trả về JSON không đúng format")
            return None

        return result

    except Exception as e:
        print(f"Lỗi khi gọi API sinh Quiz: {e}")
        return None