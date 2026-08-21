# --- ai_engine/services/tutor_chat_service.py ---

import json
from .ai_config import get_client, types


def generate_tutor_chat_response(
    conversation_history,
    student_input,
    question_prompt,
    required_key_points
):
    """
    Socratic AI Tutor:
    - Compare the student's response with required key points.
    - Do not provide the complete answer.
    - Guide the student using hints and questions.
    - Return whether the response is ready for grading.
    """

    client = get_client()

    system_instruction = f"""
    You are an intelligent, patient, and pedagogical AI tutor
    assisting a student with a long-form response or essay.

    [CONTEXT]
    - Question/Prompt: "{question_prompt}"
    - Mandatory Key Points Required:
      {json.dumps(required_key_points, ensure_ascii=False)}

    [RULES & CONSTRAINTS]

    1. DO NOT give away the final complete answer or write the essay
       for the student.

    2. Analyze the student's current input and conversation history
       against the Mandatory Key Points Required.

    3. If the student has NOT covered all or most of the essential
       key points, guide them with Socratic questioning, hints,
       and scaffolding questions.

    4. Set "is_ready_for_grading" to true ONLY when the student
       has sufficiently addressed the required key points.

    5. WHEN "is_ready_for_grading" is true, compile everything
       the student has expressed across the ENTIRE conversation,
       including the current turn, into one coherent piece of writing.

       Use only the student's own ideas and wording.
       Do not add new ideas or correct their content.

       WHEN "is_ready_for_grading" is false,
       set "compiled_final_answer" to null.

    [MANDATORY OUTPUT FORMAT]

    {{
        "ai_message": "Your conversational response and Socratic guidance.",
        "is_ready_for_grading": false,
        "compiled_final_answer": null
    }}
    """

    contents = []

    if conversation_history:
        for message in conversation_history:
            role = (
                "user"
                if message.get("role") == "user"
                else "model"
            )

            contents.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part.from_text(
                            text=message.get("content", "")
                        )
                    ]
                )
            )

    contents.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=student_input
                )
            ]
        )
    )

    models_to_try = [
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
        "gemini-2.5-flash-lite",
    ]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                ),
            )

            if response and response.text:
                return json.loads(response.text)

        except Exception as e:
            print(
                f"Error when calling Tutor Chat API "
                f"({model_name}): {e}"
            )
            continue

    # 全モデル失敗時は勝手に採点可能にしない
    return {
        "ai_message": (
            "The AI tutor is currently busy. "
            "Please try again in a moment."
        ),
        "is_ready_for_grading": False,
        "compiled_final_answer": None,
    }