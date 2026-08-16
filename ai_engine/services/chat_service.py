# --- services/chat_service.py ---
import re
from .ai_config import get_client, types

def generate_chat_answer(question_text, context_type=None, context_name=None, context_text=None):
    """Function to call the Gemini AI to answer student questions with fallback support"""
    client = get_client()
    
    context_info = ""
    if context_type and context_name:
        context_info = f"[Active Context: {context_type} \"{context_name}\"]\n"
    if context_text:
        context_info += f"[Study Notes Content for {context_type} \"{context_name}\"]:\n\"\"\"\n{context_text}\n\"\"\"\n"

    prompt = f"{context_info}Student Question: {question_text}"
    
    models_to_try = ['gemini-flash-latest', 'gemini-3.7-flash', 'gemini-2.0-flash-exp']
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a friendly, patient, and knowledgeable AI study tutor. Answer questions clearly, accurately, and insightfully based on the user's study topics and notes provided. Avoid outputting raw unrendered LaTeX like ($\\text{Pi}$); write clean formulas or simple plain notation like (Pi)."
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Error when calling API Chat ({model_name}): {e}")
            continue

    topic_label = f"\"{context_name}\"" if context_name else "your study notes"
    if context_text and len(context_text) > 20:
        clean_snippets = [s.strip() for s in re.split(r'[\.\n\r]+', context_text) if len(s.strip()) > 15][:3]
        snippet_text = "\n- ".join(clean_snippets)
        return (
            f"I sure can! Here is what is inside your note on {topic_label}:\n\n"
            f"- {snippet_text}\n\n"
            f"How would you like to use this note today? We can break it down further, make up practice quiz questions, or connect it to a broader topic!"
        )

    return f"I'm ready to help you master {topic_label}! What specific concepts, practice problems, or questions would you like us to explore together?"