import json
from .ai_config import get_client, types

def generate_adaptive_practice(text_content, recent_average_score=50, total_questions=5):
    """Generate difficulty-adaptive questions (with detailed solutions).."""
    # 1. Configure ratios based on student proficiency levels.
    if recent_average_score < 40:
        ratio_mc, ratio_short = 0.8, 0.2  # Below-average: 80% Easy, 20% Medium, 0% Hard
    elif recent_average_score < 75:
        ratio_mc, ratio_short = 0.4, 0.4  # Above-average: 40% Easy, 40% Medium, 20% Hard
    else:
        ratio_mc, ratio_short = 0.2, 0.4  # Advanced: 20% Easy, 20% Medium, 60% Hard

    # 2. Calculate actual quantities (Handling rounding errors thoroughly)
    mc_count = round(total_questions * ratio_mc)
    short_count = round(total_questions * ratio_short)
    long_count = total_questions - mc_count - short_count  
    prompt = f"""
    You are an education expert. Generate {total_questions} practice questions in English.
    DIFFICULTY DISTRIBUTION:
    - {mc_count} multiple choice questions (multiple_choice): VERY EASY.
    - {short_count} short answer questions (short_answer): MEDIUM.
    - {long_count} long answer questions (long_answer): HARD.
    MUST include the "explanation" field (in English).
    
    RETURN 100% A JSON ARRAY WITH THE FOLLOWING STRUCTURE:
    [
        {{
            "type": "multiple_choice",
            "question": "Content?",
            "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
            "correct_answer": "A",
            "explanation": "Explanation."
        }},
        {{
            "type": "short_answer",
            "question": "Content?",
            "sample_answer": "Sample answer",
            "explanation": "Explanation."
        }},
        {{
            "type": "long_answer",
            "question": "Content?",
            "key_points": ["Key point 1"],
            "explanation": "Explanation."
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
        print(f"Error when calling API Adaptive: {e}")
        return None


def grade_simple_answer(question_type, question, user_answer, correct_answer, explanation):
    """Lightning-fast automated grading system for Multiple Choice and Short Answer questions."""
    if question_type == "multiple_choice" or question_type == "short_answer"  :
        is_correct = str(user_answer).strip().upper() == str(correct_answer).strip().upper()
        return {
            "is_correct": is_correct,
            "score": 100 if is_correct else 0,
            "feedback": f"Your answer is {'Correct' if is_correct else 'Incorrect'}. {explanation}"
        }

    prompt = f"""
   - Question: "{question}"
    - Correct answer / Reference keywords: "{correct_answer}"
    - Student's response: "{user_answer}"
    - Reference explanation: "{explanation}"
    
    Requirement: Does the student's response correctly convey the meaning of the reference answer? 
    RETURN 100% JSON:
    {{
        "is_correct": true/false,
        "score": (0 to 100),
        "feedback": "(Must insert the reference explanation here so the student understands)"
    }}
    """
    try:
        response = get_client().models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json",
            system_instruction="You are an automated grading system. Grade objectively, strictly based on mathematical logic and semantic keyword matching. Results must be completely deterministic and identical across runs for identical inputs. Respond strictly with JSON."
        )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Simple Grading API: {e}")
        return None


def advanced_grade_essay(question, user_answer, standard_key_points, sample_essays=None):
    """Multidimensional AI grading system based on educational science principles."""
   # Chuẩn hóa: chấp nhận cả list (chuẩn mới, đồng bộ với tutor_chat) lẫn string (tương thích ngược)
    if isinstance(standard_key_points, (list, tuple)):
        key_points_text = "\n".join(f"- {point}" for point in standard_key_points)
    else:
        key_points_text = standard_key_points
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
        response = get_client().models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction="You are a Senior Educational Evaluation Expert. Your task is to grade student responses "
    "in the most sophisticated, scientific, and impartial manner possible. You must operate "
    "with absolute precision and consistency like a machine, allowing no emotion or randomness "
    "to alter the grading scale. Adhere to the rubric with extreme rigor."
)
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error when call API Grading: {e}")
        return None