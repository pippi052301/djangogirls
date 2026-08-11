import json
from .ai_config import client, types

def generate_adaptive_practice(text_content, recent_average_score=50, total_questions=5):
    """Sinh câu hỏi thích ứng độ khó (Có kèm lời giải chi tiết)."""
    if recent_average_score < 40:
        mc_count, short_count, long_count = 4, 1, 0
    elif recent_average_score < 75:
        mc_count, short_count, long_count = 2, 2, 1
    else:
        mc_count, short_count, long_count = 1, 2, 2

    prompt = f"""
    Bạn là chuyên gia giáo dục. Tạo {total_questions} câu hỏi luyện tập bằng tiếng Nhật.
    PHÂN BỔ ĐỘ KHÓ:
    - {mc_count} câu trắc nghiệm (multiple_choice): RẤT DỄ.
    - {short_count} câu trả lời ngắn (short_answer): TRUNG BÌNH.
    - {long_count} câu trả lời dài (long_answer): KHÓ.
    BẮT BUỘC có trường "explanation" (tiếng Việt).
    
    TRẢ VỀ 100% JSON MẢNG VỚI CẤU TRÚC:
    [
        {{
            "type": "multiple_choice",
            "question": "Nội dung?",
            "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
            "correct_answer": "A",
            "explanation": "Giải thích."
        }},
        {{
            "type": "short_answer",
            "question": "Nội dung?",
            "sample_answer": "Đáp án mẫu",
            "explanation": "Giải thích."
        }},
        {{
            "type": "long_answer",
            "question": "Nội dung?",
            "key_points": ["Ý chính 1"],
            "explanation": "Giải thích."
        }}
    ]

    Văn bản gốc:
    \"\"\"{text_content}\"\"\"
    """
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Lỗi khi gọi API Adaptive: {e}")
        return None

def grade_user_answer(question, user_answer, key_points_or_sample):
    """Chấm điểm câu hỏi tự luận/ngắn."""
    prompt = f"""
    Giám khảo AI chấm thi.
    - Câu hỏi: "{question}"
    - Đáp án chuẩn/Ý chính cần có: "{key_points_or_sample}"
    - Bài làm của học sinh: "{user_answer}"
    
    TRẢ VỀ 100% JSON:
    {{
        "score": 85,
        "feedback": "Nhận xét chi tiết tiếng Việt..."
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Lỗi khi gọi API Grading: {e}")
        return None