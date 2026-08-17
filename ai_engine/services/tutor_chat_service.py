# --- ai_engine/services/tutor_chat_service.py ---
import json
from .ai_config import get_client, types

def generate_tutor_chat_response(conversation_history, student_input, question_prompt, required_key_points):
    """
    Socratic AI Tutor:
    - Compare the student's ideas with the required key points.
    - Do not provide the complete answer.
    - Guide the student using questions and hints.
    - Return readiness for grading and a compiled final answer.
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
    6. For math equations and formulas, write clean notation ($equation$ for inline, $$equation$$ for block) so formulas render beautifully and are 100% copy-pasteable.
    [MANDATORY OUTPUT FORMAT]
    Return your response strictly as a JSON object with the following structure:
    {{
        "ai_message": "Your conversational response, encouragement, and Socratic guidance goes here...",
        "is_ready_for_grading": false,
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

    models_to_try = ["genmini-flash-lite-latest",
                     "gemini-flash-latest",
                     "gemini-3-flsh-preview",
                     "gemini-2.5-flash-lite"
    ]

    for model_name in models_to_try:


        try:
            response = client.models.generate_content(
                model='model_name',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                ),
            )

            if response and respose.text:
                return json.loads(response.text)
        
        except Exception as e:
            print(f"Error when calling Tutor Chat API: {e}")

        continue

    #when all Ai models failed
    return {
        "ai_message": (
            "The AI tutor is currently busy. "
            "Please try again in a moment."
        ),
        "is_ready_for_grading": False,
        "compiled_final_answer": None,
    }
