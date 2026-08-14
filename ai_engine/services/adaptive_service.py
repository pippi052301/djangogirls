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


def advanced_grade_essay(question, user_answer, standard_key_points, sample_essays=None):
    """
    Hệ thống chấm điểm AI đa chiều dựa trên cơ sở khoa học giáo dục.
    - standard_key_points: Đáp án chuẩn (RAG / Retrieval).
    - sample_essays: (Tùy chọn) Danh sách các bài làm mẫu đã được người chấm (Few-shot learning).
    """
    
    # 1. Xử lý phần "Học theo mẫu" (Few-shot Learning / Comparative Learning)
    few_shot_prompt = ""
    if sample_essays:
        few_shot_prompt = f"""
        ĐỂ ĐÁNH GIÁ CHUẨN XÁC HƠN, hãy tham khảo các bài làm mẫu đã được giáo viên chấm điểm dưới đây để hiểu được tiêu chuẩn chấm (không chấm gắt hơn hay lỏng hơn mẫu):
        {sample_essays}
        """

    # 2. Xây dựng Prompt "Kỹ sư AI" (Kết hợp Rubric + Decomposition + Justification)
    prompt = f"""
    Bạn là một Chuyên gia Đánh giá Giáo dục cấp cao. Nhiệm vụ của bạn là chấm điểm bài làm của học sinh một cách tinh vi, khoa học và công tâm nhất.
    
    [DỮ LIỆU ĐẦU VÀO]
    - CÂU HỎI: "{question}"
    - ĐÁP ÁN CHUẨN (TIÊU CHÍ BẮT BUỘC): "{standard_key_points}"
    - BÀI LÀM CỦA HỌC SINH: "{user_answer}"
    {few_shot_prompt}
    
    [QUY TRÌNH ĐÁNH GIÁ BẮT BUỘC]
    Bước 1 (Decomposition): Phân tách bài làm của học sinh thành các ý chính (Key points).
    Bước 2 (Retrieval & Alignment): Đối chiếu từng ý của học sinh với ĐÁP ÁN CHUẨN để xem có khớp về mặt ngữ nghĩa (Semantic) không.
    Bước 3 (Scoring): Chấm điểm dựa trên Rubric 4 chiều.
    Bước 4 (Justification): Đưa ra lý do TRỰC TIẾP và CỤ THỂ cho từng điểm số được cho/bị trừ.
    
    [RUBRIC ĐA CHIỀU (Thang 100 điểm)]
    1. Độ chính xác nội dung (Content Accuracy) - Tối đa 40 điểm: Mức độ bao phủ các ý chuẩn.
    2. Tính logic của lập luận (Logical Argumentation) - Tối đa 30 điểm: Sự chặt chẽ, mạch lạc.
    3. Cấu trúc bài viết (Structure) - Tối đa 15 điểm: Mở bài, thân bài, kết luận rõ ràng.
    4. Từ vựng/Thuật ngữ (Vocabulary) - Tối đa 15 điểm: Sử dụng ngôn từ tinh tế, đúng chuyên ngành như một chuyên gia.

    TRẢ VỀ 100% JSON THEO CẤU TRÚC SAU (Lưu ý: rationale phải giải thích chi tiết, không nói chung chung):
    {{
        "decomposition": ["Ý 1 học sinh viết...", "Ý 2 học sinh viết..."],
        "rubric_scores": {{
            "content_accuracy": {{"score": 35, "max": 40, "rationale": "Lý do cho điểm/trừ điểm..."}},
            "logical_argumentation": {{"score": 25, "max": 30, "rationale": "Lý do..."}},
            "structure": {{"score": 12, "max": 15, "rationale": "Lý do..."}},
            "vocabulary": {{"score": 14, "max": 15, "rationale": "Lý do..."}}
        }},
        "total_score": 86,
        "overall_feedback": "Nhận xét tổng quan và định hướng cải thiện bằng tiếng Việt..."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2 # Cố định temperature để AI đánh giá nhất quán
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Lỗi khi gọi API Grading Nâng cao: {e}")
        return None


def grade_user_answer(question, user_answer, correct_criteria):
    res = advanced_grade_essay(question, user_answer, correct_criteria)
    if res and "total_score" in res:
        return {"score": res["total_score"], "feedback": res.get("overall_feedback", "")}
    return res