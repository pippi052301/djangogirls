import json
from .ai_config import get_client, types 

def generate_quiz_from_text(text_content, num_questions=3):
    """Generating simple multiplechoice."""
    prompt = f"""
    You are an education expert and academic examiner. Read the following text and create {num_questions} multiple-choice questions (4 options A, B, C, D) in Japanese.
    
    REQUIREMENTS:
    - Must have exactly 1 correct answer.
    - Provide a concise explanation of why the answer is correct.
    - TRUTH GROUNDING: The source text is student study notes and may contain mistakes. Always ground correct_answer in real scientific and academic facts. Never mark a factual error as correct!
    - If testing a concept where the student's note had a misconception, state the truth as correct_answer and clarify in the explanation: "注: ノートの記載と異なり、科学的には...が正解です。"
    
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
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction="You are an expert exam creator. Always ensure questions and answer keys strictly reflect objective factual truth."
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error when calling API to generate Quiz: {e}")
        return None
