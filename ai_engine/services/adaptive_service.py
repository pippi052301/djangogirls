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
    Bạn là chuyên gia giáo dục. Tạo {total_questions} câu hỏi luyện tập bằng tiếng Anh.
    PHÂN BỔ ĐỘ KHÓ:
    - {mc_count} câu trắc nghiệm (multiple_choice): RẤT DỄ.
    - {short_count} câu trả lời ngắn (short_answer): TRUNG BÌNH.
    - {long_count} câu trả lời dài (long_answer): KHÓ.
    BẮT BUỘC có trường "explanation" (tiếng Anh).
    
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


def grade_simple_answer(question_type, question, user_answer, correct_answer, explanation):
    """Hệ thống chấm điểm siêu tốc cho Trắc nghiệm và Câu trả lời ngắn."""
    if question_type == "multiple_choice":
        is_correct = str(user_answer).strip().upper() == str(correct_answer).strip().upper()
        return {
            "is_correct": is_correct,
            "score": 100 if is_correct else 0,
            "feedback": f"Đáp án của bạn là {'ĐÚNG' if is_correct else 'SAI'}. {explanation}"
        }

    prompt = f"""
    Hãy chấm điểm câu trả lời ngắn của học sinh một cách nhanh chóng.
    - Câu hỏi: "{question}"
    - Đáp án đúng / Từ khóa chuẩn: "{correct_answer}"
    - Bài làm của học sinh: "{user_answer}"
    - Lời giải thích chuẩn: "{explanation}"
    
    Yêu cầu: Học sinh có trả lời đúng ý nghĩa của đáp án chuẩn không? 
    TRẢ VỀ 100% JSON:
    {{
        "is_correct": true/false,
        "score": (0 đến 100),
        "feedback": "(Bắt buộc chèn lời giải thích chuẩn vào đây để học sinh hiểu)"
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Lỗi khi gọi API Grading Đơn giản: {e}")
        return None


def advanced_grade_essay(question, user_answer, standard_key_points, sample_essays=None):
    """Hệ thống chấm điểm AI đa chiều dựa trên cơ sở khoa học giáo dục."""
    few_shot_prompt = ""
    if sample_essays:
        few_shot_prompt = f"""
        ĐỂ ĐÁNH GIÁ CHUẨN XÁC HƠN, hãy tham khảo các bài làm mẫu đã được giáo viên chấm điểm dưới đây để hiểu được tiêu chuẩn chấm:
        {sample_essays}
        """

    prompt = f"""
    Bạn là một Chuyên gia Đánh giá Giáo dục cấp cao. Nhiệm vụ của bạn là chấm điểm bài làm của học sinh một cách tinh vi, khoa học và công tâm nhất.
    
    [DỮ LIỆU ĐẦU VÀO]
    - CÂU HỎI: "{question}"
    - ĐÁP ÁN CHUẨN: "{standard_key_points}"
    - BÀI LÀM CỦA HỌC SINH: "{user_answer}"
    {few_shot_prompt}
    
    [QUY TRÌNH ĐÁNH GIÁ BẮT BUỘC]
    Bước 1 (Decomposition): Phân tách bài làm của học sinh thành các ý chính.
    Bước 2 (Retrieval & Alignment): Đối chiếu từng ý với ĐÁP ÁN CHUẨN.
    Bước 3 (Scoring): Chấm điểm dựa trên Rubric 4 chiều.
    Bước 4 (Justification): Đưa ra lý do CỤ THỂ cho từng điểm số.
    
    [RUBRIC ĐA CHIỀU (Thang 100 điểm)]
    1. Độ chính xác nội dung (Content Accuracy) - Tối đa 40 điểm: Mức độ bao phủ các ý chuẩn.
    2. Tính logic của lập luận (Logical Argumentation) - Tối đa 30 điểm: Sự chặt chẽ, mạch lạc.
    3. Cấu trúc bài viết (Structure) - Tối đa 15 điểm: Mở bài, thân bài, kết luận rõ ràng.
    4. Từ vựng/Thuật ngữ (Vocabulary) - Tối đa 15 điểm: Sử dụng ngôn từ tinh tế, đúng chuyên ngành như một chuyên gia.
    
    [OUTPUT LANGUAGE] #en
    "decomposition", all "rationale", and "overall_feedback" must be written in English.
    Keep the JSON key names and score values unchanged.

    TRẢ VỀ 100% JSON THEO CẤU TRÚC:
    {{
        "decomposition": ["Ý 1...", "Ý 2..."],
        "rubric_scores": {{
            "content_accuracy": {{"score": 35, "max": 40, "rationale": "Lý do..."}},
            "logical_argumentation": {{"score": 25, "max": 30, "rationale": "Lý do..."}},
            "structure": {{"score": 12, "max": 15, "rationale": "Lý do..."}},
            "vocabulary": {{"score": 14, "max": 15, "rationale": "Lý do..."}}
        }},
        "total_score": 86,
        "overall_feedback": "Nhận xét tổng quan..."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2 
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Lỗi khi gọi API Grading Nâng cao: {e}")
        return None