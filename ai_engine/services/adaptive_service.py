import json
from .ai_config import get_client, types

def generate_adaptive_practice(text_content, recent_average_score=50, total_questions=5):
    """Generate difficulty-adaptive questions (with detailed solutions).."""
    # 1. Configure ratios based on student proficiency levels.
    if recent_average_score < 40:
        ratio_mc, ratio_short = 0.6, 0.2  # Below-average: 3 Easy (MC), 1 Medium (Short), 1 Hard (Oral)
    elif recent_average_score < 75:
        ratio_mc, ratio_short = 0.4, 0.4  # Standard: 2 Easy (MC), 2 Medium (Short), 1 Hard (Oral)
    else:
        ratio_mc, ratio_short = 0.2, 0.4  # Advanced: 1 Easy (MC), 2 Medium (Short), 2 Hard (Oral)

    # 2. Calculate actual quantities (Handling rounding errors thoroughly)
    mc_count = round(total_questions * ratio_mc)
    short_count = round(total_questions * ratio_short)
    oral_count = total_questions - mc_count - short_count  
    prompt = f"""
    You are an education expert. Generate {total_questions} practice questions in English.
    DIFFICULTY DISTRIBUTION:
    - {mc_count} multiple choice questions (multiple_choice): VERY EASY.
    - {short_count} short answer questions (short_answer): MEDIUM.
    - {oral_count} Socratic oral questioning / interactive tutor questions (socratic_tutor): HARD / ADVANCED.
    MUST include the "explanation" field (in English).
    
    CRITICAL MULTIPLE CHOICE RULE:
    - "correct_answer" MUST be ONLY the single uppercase letter key ("A", "B", "C", or "D") that corresponds to the correct option.
    - Double check that the letter in "correct_answer" EXACTLY matches the dictionary key of the correct option! Do NOT confuse mathematical symbols or variable names (such as Discriminant 'D') with option letter keys!
    
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
            "type": "socratic_tutor",
            "question": "Oral questioning prompt for interactive discussion...",
            "required_key_points": ["Key point 1", "Key point 2"],
            "explanation": "Reference answer & explanation."
        }}
    ]

    Source text:
    \"\"\"{text_content}\"\"\"
    """
    try:
        response = get_client().models.generate_content(
            model='gemini-flash-lite-latest', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        data = json.loads(response.text)
        if isinstance(data, dict):
            data = data.get("questions") or data.get("quiz") or data.get("data") or data.get("items") or [data]
        if not isinstance(data, list) or len(data) < 3:
            return None
        return verify_and_fix_quiz_answers(data)
    except Exception as e:
        print(f"Error when calling API Adaptive: {e}")
        return None


def verify_and_fix_quiz_answers(quiz_data):
    """Post-processing validation to ensure correct_answer key matches explanation and option text."""
    if not isinstance(quiz_data, list):
        return quiz_data

    for q in quiz_data:
        if not isinstance(q, dict):
            continue
        q_type = q.get("type")
        if q_type == "multiple_choice" and "options" in q and "correct_answer" in q:
            opts = q.get("options", {})
            corr_key = str(q.get("correct_answer", "")).strip().upper()
            expl = str(q.get("explanation", "")).lower()

            best_matching_key = corr_key

            for key, opt_text in opts.items():
                opt_clean = str(opt_text).lower().replace(" ", "").replace("^2", "²")
                expl_clean = expl.replace(" ", "").replace("^2", "²")
                
                # Check for formula substrings like b²-4ac
                if len(opt_clean) > 3 and opt_clean in expl_clean:
                    best_matching_key = key
                    break

            if best_matching_key != corr_key:
                print(f"Auto-corrected quiz key from {corr_key} to {best_matching_key}")
                q["correct_answer"] = best_matching_key

    return quiz_data


def grade_simple_answer(question_type, question, user_answer, correct_answer, explanation):
    """Grading for simple question types.
    - multiple_choice: instant exact-match grading (A/B/C/D).
    - short_answer: AI grading by meaning only, ignoring case/whitespace/punctuation/
      word-order/phrasing differences.
    """
    if question_type == "multiple_choice":
        is_correct = str(user_answer).strip().upper() == str(correct_answer).strip().upper()
        return {
            "is_correct": is_correct,
            "score": 100 if is_correct else 0,
            "feedback": f"Your answer is {'Correct' if is_correct else 'Incorrect'}. {explanation}"
        }

    # Short Answer smart mathematical equality check
    u_clean = str(user_answer).strip().lower()
    c_clean = str(correct_answer).strip().lower()

    # Number word equivalence maps
    num_map = {
        '0': ['0', 'zero',  'no', 'no real', 'negative'],
        '1': ['1', 'one', 'single', 'double root', 'one repeated'],
        '2': ['2', 'two', 'distinct', 'two distinct', 'two real']
    }

    is_correct = u_clean == c_clean
    if not is_correct:
        for key, synonyms in num_map.items():
            if any(s in u_clean for s in synonyms) and any(s in c_clean for s in synonyms):
                is_correct = True
                break

    if is_correct:
        return {
            "is_correct": True,
            "score": 100,
            "feedback": f"Your answer is Correct! {explanation}"
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
            model='gemini-flash-lite-latest', 
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
        key_points_text = "\n".join(
            f"- {point}"
            for point in standard_key_points
        )
    else:
        key_points_text = str(standard_key_points)
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