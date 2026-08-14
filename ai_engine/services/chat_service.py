# --- services/chat_service.py ---
from .ai_config import get_client, types

def generate_chat_answer(question_text):
    """Function to call the Gemini AI to answer student questions"""
    client = get_client()
    
    prompt = f"Answer the student's following question concisely, clearly, and accurately:\n\nQuestion: {question_text}"
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=
    "You are a friendly, patient, and knowledgeable AI tutor. Explain complex concepts "
    "using simple words. Do not provide biased or unethical answers."
)
        )
        return response.text
    except Exception as e:
        print(f"Error when call API Chat: {e}")
        return None