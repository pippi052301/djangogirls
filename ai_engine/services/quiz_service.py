import json
from .ai_config import get_client, types 

def generate_quiz_from_text(text_content, num_questions=3):
    """Generating simple multiplechoice."""
    prompt = f"""
    You are an education expert. Read the following text and create {num_questions} multiple-choice questions (4 options A, B, C, D) in Japanese.
    
    REQUIREMENTS:
    - Must have exactly 1 correct answer.
    - Provide a concise explanation of why the answer is correct.
    
    Required JSON structure:
    [
        {{
            "question": "Question content?",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Detailed explanation."
        }}
    ]

    Source text:
    \"\"\"{text_content}\"\"\"
    """
    
    try:
        response = get_client().models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error when calling API to generate Quiz: {e}")
        return None
