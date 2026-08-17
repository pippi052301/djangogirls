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
            config=types.GenerateContentConfig(response_mime_type="application/json",
            system_instruction="You are an automated grading system. Grade objectively, strictly based on mathematical logic and semantic keyword matching. Results must be completely deterministic and identical across runs for identical inputs. Respond strictly with JSON."
        )
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
        FOR MORE ACCURATE EVALUATION, refer to the teacher-graded sample responses below to understand the grading standards:
         {sample_essays}
        """

    prompt = f"""
    You are a Senior Educational Evaluation Expert. Your task is to evaluate the student's response in a sophisticated, scientific, and impartial manner.
    
    [INPUT DATA]
    - QUESTION: "{question}"
    - REFERENCE ANSWER: "{key_points_text}"
    - STUDENT RESPONSE: "{user_answer}"
    {few_shot_prompt}
    
    [MANDATORY EVALUATION PROCESS]
    Step 1 (Decomposition): Break down the student's response into key points.
    Step 2 (Retrieval & Alignment): Match each point against the REFERENCE ANSWER.
    Step 3 (Scoring): Grade based on the 4-dimensional Rubric.
    Step 4 (Justification): Provide SPECIFIC justifications for each assigned score.
    
    [MULTIDIMENSIONAL RUBRIC (100-Point Scale)]
    1. Content Accuracy - 40 pts
    2. Logical Reasoning - 30 pts
    3. Essay Structure - 15 pts
    4. Vocabulary & Terminology - 15 pts

    RETURN 100% JSON WITH THE FOLLOWING STRUCTURE:
    {{
        "decomposition": ["Point 1...", "Point 2..."],
        "rubric_scores": {{
            "content_accuracy": {{"score": 35, "max": 40, "rationale": "Reason..."}},
            "logical_argumentation": {{"score": 25, "max": 30, "rationale": "Reason..."}},
            "structure": {{"score": 12, "max": 15, "rationale": "Reason..."}},
            "vocabulary": {{"score": 14, "max": 15, "rationale": "Reason..."}}
        }},
        "total_score": 86,
        "overall_feedback": "General overview..."
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