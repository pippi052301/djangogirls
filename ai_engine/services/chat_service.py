# --- services/chat_service.py ---
from .ai_config import get_client, types

def generate_chat_answer(question_text):
    """Function to call Gemini AI with automatic working model fallback list"""
    client = get_client()
    prompt = f"Answer the student's following question concisely, clearly, and accurately:\n\nQuestion: {question_text}"
    
    models_to_try = ['gemini-flash-lite-latest', 'gemini-3.5-flash', 'gemini-3.5-flash-lite', 'gemini-3.7-flash', 'gemma-4-31b-it']
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a friendly, patient, and knowledgeable AI tutor. Explain complex concepts "
                        "using simple words. Do not provide biased or unethical answers."
                    )
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue
            
    return None