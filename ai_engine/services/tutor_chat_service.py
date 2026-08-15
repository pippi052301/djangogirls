# --- ai_engine/services/tutor_chat_service.py ---
import json
from .ai_config import get_client, types

def generate_tutor_chat_response(conversation_history, student_input, question_prompt, required_key_points):
    """
    Trợ lý AI đồng hành dạng chat gợi mở:
    - Đối chiếu bài làm/ý kiến của học sinh với các ý chính bắt buộc.
    - Tuyệt đối không đưa ra đáp án hoàn chỉnh hay viết hộ bài.
    - Gợi mở, đặt câu hỏi định hướng nếu chưa đủ ý.
    - Trả về JSON chứa phản hồi của AI và cờ (flag) cho biết đã đủ ý chính hay chưa để bật nút chấm điểm.
    """
    client = get_client()
    
    # Định nghĩa system instruction ép AI làm đúng vai trò sư phạm gợi mở và kiểm tra trạng thái
    system_instruction = f"""
    You are an intelligent, patient, and pedagogical AI tutor assisting a student with a long-form response or essay.
    
    [CONTEXT]
    - Question/Prompt: "{question_prompt}"
    - Mandatory Key Points Required: {json.dumps(required_key_points, ensure_ascii=False)}
    
    [RULES & CONSTRAINTS]
    1. DO NOT give away the final complete answer or write the essay for the student.
    2. Analyze the student's current input and conversation history against the Mandatory Key Points Required.
    3. If the student has NOT covered all or most of the essential key points, guide them with Socratic questioning, hints, and scaffolding questions to help them think deeper and cover the missing points.
    4. Evaluate whether the student has successfully addressed all the mandatory key points well enough to trigger the grading phase. Set "is_ready_for_grading" to true ONLY when they have explicitly or sufficiently touched upon the main required concepts. Otherwise, keep it false.
    5. WHEN "is_ready_for_grading" is true, compile everything the student has expressed across the ENTIRE conversation (all turns, including this one) into one single, coherent piece of writing in "compiled_final_answer" — use the student's own ideas and wording, do not improve, correct, or add content they didn't say. WHEN "is_ready_for_grading" is false, set "compiled_final_answer" to null.
    [MANDATORY OUTPUT FORMAT]
    Return your response strictly as a JSON object with the following structure:
    {{
        "ai_message": "Your conversational response, encouragement, and Socratic guidance goes here...",
        "is_ready_for_grading": false
                "compiled_final_answer": null

    }}
    """
    
    # Xây dựng nội dung gửi cho mô hình bao gồm lịch sử trò chuyện (nếu có)
    contents = []
    
    # Đưa lịch sử vào nội dung (nếu được truyền vào dưới dạng list các đoạn chat trước)
    if conversation_history:
        for message in conversation_history:
            role = "user" if message.get("role") == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=message.get("content", ""))]
            ))
            
    # Thêm câu hỏi/ý kiến hiện tại của người dùng
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=student_input)]
    ))
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error when calling Tutor Chat API: {e}")
        return {
            "ai_message": "Xin lỗi, hệ thống gia sư đang bận một chút. Bạn có thể chia sẻ lại ý tưởng của mình được không?",
            "is_ready_for_grading": False,
            "compiled_final_answer": None
        }