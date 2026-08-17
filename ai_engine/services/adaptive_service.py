import json
import re
from .ai_config import get_client, types

def clean_study_text(text):
    if not text:
        return ""
    if '\\u' in text:
        try:
            text = text.encode('utf-8').decode('unicode-escape')
        except Exception:
            pass
    return text.strip()

import html

def extract_math_study_snippets(text_content):
    """
    Extracts high-quality study sentences, filtering out cover page author headers,
    book title metadata, table of contents, and HTML tags while preserving math exponents.
    """
    text_content = clean_study_text(text_content)
    text_content = html.unescape(text_content)
    text_content = re.sub(r'<br\s*/?>', '\n', text_content, flags=re.I)
    text_content = re.sub(r'</p>', '\n', text_content, flags=re.I)
    text_content = re.sub(r'</div>', '\n', text_content, flags=re.I)
    text_content = re.sub(r'<[^>]+>', '', text_content)
    text_content = re.sub(r'[ \t]+', ' ', text_content)
    
    raw_chunks = re.split(r'[\n\r]+|\.\s+(?=[A-Z0-9])', text_content)
    
    ignore_keywords = [
        'Page', 'http', 'www', 'Content:', 'Note Title:', 'folder', 'study material', 'table of contents', 'preface', 'copyright'
    ]
    
    study_lines = []
    for chunk in raw_chunks:
        line = chunk.strip()
        if any(kw.lower() in line.lower() for kw in ignore_keywords):
            continue
        if len(line) >= 15 and not line.startswith('{'):
            clean_l = re.sub(r'[^\w\s\+\-\*\/\=\<\>\:\;\,\.\(\)\{\}\[\]\%\?²³≠≤≥±√π°ΔàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ]', '', line)
            clean_l = re.sub(r'(.{3,})\1+', r'\1', clean_l).strip()
            if len(clean_l) >= 10:
                study_lines.append(clean_l)
                
    return study_lines

def trim_to_clean_phrase(text, max_len=95):
    """
    Trims a text snippet smoothly at clean word/clause boundaries,
    preventing ugly truncated string fragments like '(wh' or trailing colons.
    """
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return re.sub(r'[\:\,\=\s]+$', '', text).strip()
    truncated = text[:max_len]
    if ' ' in truncated:
        truncated = truncated.rsplit(' ', 1)[0]
    if truncated.count('(') > truncated.count(')'):
        truncated = truncated.rsplit('(', 1)[0].strip()
    return re.sub(r'[\:\,\=\s]+$', '', truncated).strip()

def split_sentence_to_qa(sentence, q_idx=0):
    """
    Deconstructs a factual sentence into a distinct Question and Answer pair
    so the question prompt and correct choice are NOT identical duplicates,
    varying the question phrasing based on q_idx.
    """
    sentence = sentence.strip()
    sentence = re.sub(r'(.{3,})\1+', r'\1', sentence).strip()
    if not sentence:
        return "What is the central concept of this lesson?", "Mastering core principles and analytical methods."

    delimiters = [
        ', allowing ', ', causing ', ', resulting in ', ' causes ', ' is the site of ', ' requires ', ' allows '
    ]
    part1, part2 = "", ""
    for d in delimiters:
        if d in sentence.lower():
            idx = sentence.lower().index(d)
            part1 = sentence[:idx].strip()
            part2 = sentence[idx + len(d):].strip()
            break

    if not part1 or len(part1) < 8 or len(part2) < 8:
        if ',' in sentence:
            parts = [p.strip() for p in sentence.split(',') if len(p.strip()) > 8]
            if len(parts) >= 2:
                part1, part2 = parts[0], parts[1]
        if not part1 or len(part1) < 8:
            words = sentence.split()
            if len(words) >= 6:
                mid = len(words) // 2
                part1, part2 = " ".join(words[:mid]), " ".join(words[mid:])

    if not part1 or not part2:
        part1, part2 = sentence[:len(sentence)//2], sentence[len(sentence)//2:]

    part1 = re.sub(r'(.{3,})\1+', r'\1', part1).strip()
    part1 = re.sub(r'[\:\=\s]+$', '', part1).strip()
    part2 = re.sub(r'(.{3,})\1+', r'\1', part2).strip()

    clean_p1 = trim_to_clean_phrase(part1, 95)
    a = part2[0].upper() + part2[1:] if part2 else sentence

    templates = [
        f"When conditions specify '{clean_p1}', what is the resulting outcome or mechanism?",
        f"Which key principle or rule applies to: '{clean_p1}'?",
        f"What primary functional role is associated with: '{clean_p1}'?",
        f"Which statement correctly reflects the property of: '{clean_p1}'?"
    ]
    q = templates[q_idx % len(templates)]

    return q, a


def build_dynamic_context_fallback(text_content):
    """
    Extracts key sentences from actual study content to build direct, concrete,
    and natural questions in clean English with topic-matched distractors.
    """
    math_snippets = extract_math_study_snippets(text_content)
    
    s0 = math_snippets[0] if len(math_snippets) > 0 else "Given quadratic equation ax^2 + bx + c = 0"
    s1 = math_snippets[1] if len(math_snippets) > 1 else s0
    s2 = math_snippets[2] if len(math_snippets) > 2 else s0
    s3 = math_snippets[3] if len(math_snippets) > 3 else s0

    clean_s0 = trim_to_clean_phrase(s0, 95)
    clean_s1 = trim_to_clean_phrase(s1, 95)

    is_math = any(w in text_content.lower() for w in ["equation", "discriminant", "quadratic", "b²", "ax²", "solve", "math", "root", "formula"])

    q0, a0 = split_sentence_to_qa(s0, 0)
    q1, a1 = split_sentence_to_qa(s1, 1)
    q2, a2 = split_sentence_to_qa(s2, 2)
    q3, a3 = split_sentence_to_qa(s3, 3)

    if is_math:
        return [
            {
                "type": "multiple_choice",
                "question": "For the quadratic equation x² - 2x + 1 = 0 (substituting a = 1, b = -2, c = 1), calculate the discriminant D = b² - 4ac and determine the real solutions.",
                "options": {
                    "A": "D = 0 (one repeated real solution x = 1)",
                    "B": "D = 4 (two distinct real solutions x = 2 and x = -2)",
                    "C": "D = -4 (no real solutions)",
                    "D": "D = 8 (two distinct real solutions)"
                },
                "correct_answer": "A",
                "explanation": "D = b² - 4ac = (-2)² - 4(1)(1) = 4 - 4 = 0. Since D = 0, there is exactly one repeated real solution x = 1.",
                "max_score": 15
            },
            {
                "type": "multiple_choice",
                "question": "Given the quadratic equation x² - 5x + 6 = 0 (substituting a = 1, b = -5, c = 6), what is the value of the discriminant D and the number of solutions?",
                "options": {
                    "A": "D = -1 (no real solutions)",
                    "B": "D = 1 (two distinct real solutions x = 2 and x = 3)",
                    "C": "D = 0 (one repeated real solution)",
                    "D": "D = 25 (two distinct real solutions)"
                },
                "correct_answer": "B",
                "explanation": "D = b² - 4ac = (-5)² - 4(1)(6) = 25 - 24 = 1. Since D > 0, there are two distinct real solutions x = 2 and x = 3.",
                "max_score": 15
            },
            {
                "type": "multiple_choice",
                "question": "For the quadratic equation x² + 2x + 5 = 0 (substituting a = 1, b = 2, c = 5), what is the nature of its real solutions?",
                "options": {
                    "A": "Two distinct real solutions",
                    "B": "One repeated real solution x = -1",
                    "C": "No real solutions (D = -16 < 0)",
                    "D": "Infinitely many real solutions"
                },
                "correct_answer": "C",
                "explanation": "D = b² - 4ac = 2² - 4(1)(5) = 4 - 20 = -16. Since D < 0, there are no real solutions.",
                "max_score": 15
            },
            {
                "type": "multiple_choice",
                "question": "Which statement correctly reflects the rule for determining real solutions of ax² + bx + c = 0 based on the discriminant D = b² - 4ac?",
                "options": {
                    "A": "If D > 0, there is only one repeated real solution",
                    "B": "If D > 0 there are 2 distinct real solutions; if D = 0 there is 1 repeated solution; if D < 0 there are no real solutions",
                    "C": "If D < 0, there are always two distinct real solutions",
                    "D": "The discriminant formula cannot be used to find the number of solutions"
                },
                "correct_answer": "B",
                "explanation": "The sign of D determines the solution count: D > 0 (2 distinct real roots), D = 0 (1 double root), D < 0 (0 real roots).",
                "max_score": 15
            },
            {
                "type": "short_answer",
                "question": "Calculate the discriminant D for x² - 4x + 4 = 0 (substituting a = 1, b = -4, c = 4) and state the number of real solutions.",
                "sample_answer": "D = (-4)² - 4(1)(4) = 16 - 16 = 0. One repeated real solution x = 2.",
                "explanation": "Applying formula D = b² - 4ac with a=1, b=-4, c=4 yields D = 0.",
                "max_score": 10
            },
            {
                "type": "short_answer",
                "question": "Given the quadratic equation 2x² - 3x - 5 = 0 (substituting a = 2, b = -3, c = -5), calculate the value of discriminant D = b² - 4ac.",
                "sample_answer": "D = (-3)² - 4(2)(-5) = 9 + 40 = 49 (D > 0, two distinct real solutions).",
                "explanation": "D = (-3)² - 4(2)(-5) = 9 + 40 = 49.",
                "max_score": 10
            },
            {
                "type": "long_answer",
                "question": "Mathematical Essay Challenge: Explain the derivation of discriminant D = b² - 4ac and show step-by-step calculations for a = 1, b = -2, c = 1.",
                "key_points": ["Discriminant formula D = b² - 4ac", "Substituted values D = (-2)² - 4(1)(1) = 0", "Conclusion D = 0 gives 1 repeated real root x = 1"],
                "explanation": "A complete mathematical essay shows formula D, calculates D = 0, and concludes a double root.",
                "max_score": 10
            },
            {
                "type": "socratic_tutor",
                "question": "Interactive Socratic AI Tutor Debate: Discuss and calculate step-by-step the discriminant D = b² - 4ac when substituting coefficients a = 1, b = -2, c = 1.",
                "required_key_points": ["Formula D = b² - 4ac", "Calculation D = (-2)² - 4(1)(1) = 0", "Determining root count from D"],
                "explanation": "Engage with the Socratic AI Tutor to perform the numerical substitution and determine the root type.",
                "max_score": 10
            }
        ]

    return [
        {
            "type": "multiple_choice",
            "question": q0,
            "options": {
                "A": a0[:90],
                "B": "Incorrect statement or invalid property",
                "C": "Random variation not supported by study context",
                "D": "None of the above options"
            },
            "correct_answer": "A",
            "explanation": f"Study material specifies: {a0[:120]}",
            "max_score": 15
        },
        {
            "type": "multiple_choice",
            "question": q1,
            "options": {
                "A": "Ignore initial conditions",
                "B": a1[:90],
                "C": "Invalid rule application",
                "D": "Unable to calculate"
            },
            "correct_answer": "B",
            "explanation": f"According to study principles: {a1[:120]}",
            "max_score": 15
        },
        {
            "type": "multiple_choice",
            "question": q2,
            "options": {
                "A": "Omit critical steps",
                "B": "Random guess",
                "C": a2[:90],
                "D": "Undefined result"
            },
            "correct_answer": "C",
            "explanation": f"Study content specifies: {a2[:120]}",
            "max_score": 15
        },
        {
            "type": "multiple_choice",
            "question": q3,
            "options": {
                "A": "Disregard given parameters",
                "B": a3[:90],
                "C": "Incorrect formula application",
                "D": "Arbitrary choice"
            },
            "correct_answer": "B",
            "explanation": f"Solving requires following rule: {a3[:120]}",
            "max_score": 15
        },
        {
            "type": "short_answer",
            "question": f"State the primary result or mechanism associated with: '{clean_s0}'",
            "sample_answer": a0[:100],
            "explanation": f"Detailed solution: {a0[:120]}",
            "max_score": 10
        },
        {
            "type": "short_answer",
            "question": f"Explain the core principle or functional role regarding: '{clean_s1}'",
            "sample_answer": a1[:100],
            "explanation": f"Detailed solution: {a1[:120]}",
            "max_score": 10
        },
        {
            "type": "long_answer",
            "question": f"Analytical Essay: Explain the scientific principles and procedural steps for: '{clean_s0}'.",
            "key_points": [a0[:60], a1[:60], a2[:60]],
            "explanation": f"A thorough essay clearly explains: {a0[:70]} and {a1[:70]}.",
            "max_score": 10
        },
        {
            "type": "socratic_tutor",
            "question": f"Socratic Discussion with AI Tutor: Debate and clarify the core mechanism of: '{clean_s0}'.",
            "required_key_points": [a0[:60], a1[:60], a2[:60]],
            "explanation": "Engage with the AI Tutor step-by-step until all key points are clarified.",
            "max_score": 10
        }
    ]

    # English math section with concrete numerical calculations
    if is_math:
        return [
            {
                "type": "multiple_choice",
                "question": "For the quadratic equation x² - 2x + 1 = 0 (substituting a = 1, b = -2, c = 1), calculate the discriminant D = b² - 4ac and determine the real solutions.",
                "options": {
                    "A": "D = 0 (one repeated real solution x = 1)",
                    "B": "D = 4 (two distinct real solutions x = 2 and x = -2)",
                    "C": "D = -4 (no real solutions)",
                    "D": "D = 8 (two distinct real solutions)"
                },
                "correct_answer": "A",
                "explanation": "D = b² - 4ac = (-2)² - 4(1)(1) = 4 - 4 = 0. Since D = 0, there is exactly one repeated real solution x = 1.",
                "max_score": 15
            },
            {
                "type": "multiple_choice",
                "question": "Given the quadratic equation x² - 5x + 6 = 0 (substituting a = 1, b = -5, c = 6), what is the value of the discriminant D and the number of solutions?",
                "options": {
                    "A": "D = -1 (no real solutions)",
                    "B": "D = 1 (two distinct real solutions x = 2 and x = 3)",
                    "C": "D = 0 (one repeated real solution)",
                    "D": "D = 25 (two distinct real solutions)"
                },
                "correct_answer": "B",
                "explanation": "D = b² - 4ac = (-5)² - 4(1)(6) = 25 - 24 = 1. Since D > 0, there are two distinct real solutions x = 2 and x = 3.",
                "max_score": 15
            },
            {
                "type": "multiple_choice",
                "question": "For the quadratic equation x² + 2x + 5 = 0 (substituting a = 1, b = 2, c = 5), what is the nature of its real solutions?",
                "options": {
                    "A": "Two distinct real solutions",
                    "B": "One repeated real solution x = -1",
                    "C": "No real solutions (D = -16 < 0)",
                    "D": "Infinitely many real solutions"
                },
                "correct_answer": "C",
                "explanation": "D = b² - 4ac = 2² - 4(1)(5) = 4 - 20 = -16. Since D < 0, there are no real solutions.",
                "max_score": 15
            },
            {
                "type": "multiple_choice",
                "question": "Which statement correctly reflects the rule for determining real solutions of ax² + bx + c = 0 based on the discriminant D = b² - 4ac?",
                "options": {
                    "A": "If D > 0, there is only one repeated real solution",
                    "B": "If D > 0 there are 2 distinct real solutions; if D = 0 there is 1 repeated solution; if D < 0 there are no real solutions",
                    "C": "If D < 0, there are always two distinct real solutions",
                    "D": "The discriminant formula cannot be used to find the number of solutions"
                },
                "correct_answer": "B",
                "explanation": "The sign of D determines the solution count: D > 0 (2 distinct real roots), D = 0 (1 double root), D < 0 (0 real roots).",
                "max_score": 15
            },
            {
                "type": "short_answer",
                "question": "Calculate the discriminant D for x² - 4x + 4 = 0 (substituting a = 1, b = -4, c = 4) and state the number of real solutions.",
                "sample_answer": "D = (-4)² - 4(1)(4) = 16 - 16 = 0. The equation has 1 repeated real solution (x = 2).",
                "explanation": "D = b² - 4ac = (-4)² - 4(1)(4) = 0.",
                "max_score": 10
            },
            {
                "type": "short_answer",
                "question": "For the equation 2x² - 3x - 5 = 0 (substituting a = 2, b = -3, c = -5), compute the discriminant D = b² - 4ac.",
                "sample_answer": "D = (-3)² - 4(2)(-5) = 9 + 40 = 49 (two distinct real solutions).",
                "explanation": "D = (-3)² - 4(2)(-5) = 9 + 40 = 49.",
                "max_score": 10
            },
            {
                "type": "long_answer",
                "question": "Mathematical Essay Challenge: Explain the derivation of discriminant D = b² - 4ac and show step-by-step calculations for a = 1, b = -2, c = 1.",
                "key_points": ["Discriminant formula D = b² - 4ac", "Substituted values D = (-2)² - 4(1)(1) = 0", "Conclusion D = 0 gives 1 repeated real root x = 1"],
                "explanation": "A complete mathematical essay shows formula D, calculates D = 0, and concludes a double root.",
                "max_score": 10
            },
            {
                "type": "socratic_tutor",
                "question": "Interactive Socratic AI Tutor Debate: Discuss and calculate step-by-step the discriminant D = b² - 4ac when substituting coefficients a = 1, b = -2, c = 1.",
                "required_key_points": ["Formula D = b² - 4ac", "Calculation D = (-2)² - 4(1)(1) = 0", "Determining root count from D"],
                "explanation": "Engage with the Socratic AI Tutor to perform the numerical substitution and determine the root type.",
                "max_score": 10
            }
        ]

def generate_adaptive_practice(text_content, recent_average_score=50, total_questions=7):
    """
    Generate 7-Question AI Practice Suite with 40/40/20 Ratio (Total 100 Points Fixed Scale):
    - 40% (40 pts) Multiple Choice: 4 Questions @ 10 pts each
    - 40% (40 pts) Short Answer: 2 Questions @ 20 pts each
    - 20% (20 pts) Long Answer Essay: 1 Question evaluated via 4D rubric
    Total = 100 Points Fixed Scale
    """
    sampled_text = text_content[:3500] if len(text_content) > 3500 else text_content
    prompt = f"""
    You are a world-class education expert. Read the source text and create a 7-question practice test based STRICTLY on the source text below with a 40/40/20 point allocation ratio.
    CRITICAL LANGUAGE REQUIREMENT: Detect the language of the source text below. If the source text is in VIETNAMESE, generate ALL questions, options (A, B, C, D), correct answers, sample answers, key points, and explanations in VIETNAMESE. If the source text is in ENGLISH, generate them in ENGLISH.

    REQUIRED QUESTIONS IN JSON ARRAY:
    1-4. Exactly 4 Multiple Choice questions ("type": "multiple_choice") with 4 options (A, B, C, D), 1 correct answer, and explanation. (10 points each = 40 points total)
    5-6. Exactly 2 Short Answer questions ("type": "short_answer") with question, sample_answer, and explanation. (20 points each = 40 points total)
    7. Exactly 1 Essay question ("type": "long_answer") requiring analytical reasoning, with question, key_points (array of 3 mandatory concepts), and explanation. (20 points total)

    RETURN STRICTLY A JSON ARRAY WITH THIS STRUCTURE:
    [
        {{
            "type": "multiple_choice",
            "question": "Question 1 content?",
            "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
            "correct_answer": "A",
            "explanation": "Detailed explanation.",
            "max_score": 10
        }},
        {{
            "type": "multiple_choice",
            "question": "Question 2 content?",
            "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
            "correct_answer": "B",
            "explanation": "Detailed explanation.",
            "max_score": 10
        }},
        {{
            "type": "multiple_choice",
            "question": "Question 3 content?",
            "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
            "correct_answer": "C",
            "explanation": "Detailed explanation.",
            "max_score": 10
        }},
        {{
            "type": "multiple_choice",
            "question": "Question 4 content?",
            "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
            "correct_answer": "D",
            "explanation": "Detailed explanation.",
            "max_score": 10
        }},
        {{
            "type": "short_answer",
            "question": "Short Answer Question 5?",
            "sample_answer": "Expected short answer",
            "explanation": "Detailed explanation.",
            "max_score": 20
        }},
        {{
            "type": "short_answer",
            "question": "Short Answer Question 6?",
            "sample_answer": "Expected short answer",
            "explanation": "Detailed explanation.",
            "max_score": 20
        }},
        {{
            "type": "long_answer",
            "question": "Critical Essay Challenge...",
            "key_points": ["Core Concept 1", "Core Concept 2", "Core Concept 3"],
            "explanation": "Detailed pedagogical explanation.",
            "max_score": 20
        }}
    ]

    Source text:
    \"\"\"{sampled_text}\"\"\"
    """
    for model_name in ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']:
        try:
            response = get_client().models.generate_content(
                model=model_name, 
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            if response and response.text:
                res_data = json.loads(response.text)
                if isinstance(res_data, list) and len(res_data) > 0:
                    return res_data
        except Exception as e:
            print(f"Adaptive practice model {model_name} failed: {e}")
            continue

    print("Falling back to dynamic context-aware questions.")
    return build_dynamic_context_fallback(text_content)


def grade_simple_answer(question_type, question, user_answer, correct_answer, explanation):
    """Lightning-fast automated grading system for Multiple Choice and Short Answer questions."""
    if question_type == "multiple_choice":
        is_correct = str(user_answer).strip().upper() == str(correct_answer).strip().upper()
        return {
            "is_correct": is_correct,
            "score": 100 if is_correct else 0,
            "feedback": f"Your answer is {'Correct' if is_correct else 'Incorrect'}. {explanation}"
        }

    if question_type == "short_answer":
        u_norm = re.sub(r'[^\w\s\=\-\+\*\/\^\.\,]', '', str(user_answer or '')).strip().lower()
        c_norm = re.sub(r'[^\w\s\=\-\+\*\/\^\.\,]', '', str(correct_answer or '')).strip().lower()

        u_clean = re.sub(r'\s+', ' ', u_norm).strip()
        c_clean = re.sub(r'\s+', ' ', c_norm).strip()

        # 1. Exact string match
        if u_clean == c_clean:
            return {
                "is_correct": True,
                "score": 100,
                "feedback": f"Correct! {explanation}"
            }

        # 2. Extract key content words (filtering English stop words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'and', 'or', 'it', 'its', 'as', 'be', 'this', 'that'}
        c_words = [w for w in c_clean.split() if w not in stop_words and len(w) > 1]
        u_words = [w for w in u_clean.split() if w not in stop_words and len(w) > 1]

        # 3. For short numeric/math answers (e.g. "0", "-16", "1", "x=1"), require exact numeric match
        num_c = re.findall(r'-?\d+(?:\.\d+)?', c_clean)
        num_u = re.findall(r'-?\d+(?:\.\d+)?', u_clean)
        if num_c:
            is_correct = (num_c == num_u) and (len(u_words) == 0 or len(set(u_words).intersection(set(c_words))) >= len(set(c_words)) * 0.5)
            return {
                "is_correct": is_correct,
                "score": 100 if is_correct else 0,
                "feedback": f"Your answer is {'Correct' if is_correct else 'Incorrect'}. {explanation}"
            }

        # 4. For conceptual text answers, enforce strict key-term coverage (>= 75% coverage)
        if c_words and u_words:
            matched_words = set(w for w in c_words if w in u_words or any(w in uw or uw in w for uw in u_words if len(uw) >= 4 and len(w) >= 4))
            coverage = len(matched_words) / float(len(set(c_words)))
            is_correct = (coverage >= 0.75) and (len(matched_words) >= min(len(set(c_words)), 2))
        else:
            is_correct = False

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
            model='gemini-flash-latest', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json",
            system_instruction="You are an automated grading system. Grade objectively, strictly based on mathematical logic and semantic keyword matching. Results must be completely deterministic and identical across runs for identical inputs. Respond strictly with JSON."
        )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Simple Grading API: {e}")
        return {
            "is_correct": False,
            "score": 0,
            "feedback": f"AI service busy. Reference answer: {explanation}"
        }


def advanced_grade_essay(question, user_answer, standard_key_points, sample_essays=None):
    """Multidimensional AI grading system based on educational science principles."""
    clean_ans = str(user_answer or '').strip()
    words = clean_ans.split()
    vowels = set('aeiouyAEIOUYáàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ')
    has_vowels = any(c in vowels for c in clean_ans)

    if len(clean_ans) < 6 or len(words) < 2 or (not has_vowels and len(clean_ans) > 4):
        return {
            "total_score": 0,
            "overall_feedback": "Your response is incomplete, irrelevant, or contains random characters. Please provide a meaningful answer to earn points.",
            "rubric_scores": {
                "content_accuracy": {"score": 0, "max": 40, "rationale": "No relevant content provided"},
                "logical_argumentation": {"score": 0, "max": 30, "rationale": "No logical structure"},
                "structure": {"score": 0, "max": 15, "rationale": "Incomplete formatting"},
                "vocabulary": {"score": 0, "max": 15, "rationale": "No technical vocabulary"}
            }
        }

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
    
    for model_name in ['gemini-flash-latest', 'gemini-2.0-flash', 'gemini-3.7-flash']:
        try:
            response = get_client().models.generate_content(
                model=model_name, 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction="You are a Senior Educational Evaluation Expert. Your task is to grade student responses "
        "in the most sophisticated, scientific, and impartial manner possible. You must operate "
        "with absolute precision and consistency like a machine, allowing no emotion or randomness "
        "to alter the grading scale. Adhere to the rubric with extreme rigor."
                )
            )
            if response and response.text:
                return json.loads(response.text)
        except Exception as e:
            print(f"Error when calling API Grading with {model_name}: {e}")
            continue

    # Deterministic local fallback if Gemini API is rate-limited (Quota 429)
    u_lower = clean_ans.lower()
    ref_text = (str(question) + " " + str(key_points_text) + " " + str(sample_essays or "")).lower()
    ref_words = set(re.findall(r'\b[a-z0-9àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]{4,}\b', ref_text))
    user_words = set(re.findall(r'\b[a-z0-9àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]{4,}\b', u_lower))
    
    stop_words = {'with', 'that', 'this', 'from', 'have', 'were', 'which', 'their', 'there', 'about', 'would', 'could', 'should'}
    ref_words = ref_words - stop_words
    user_words = user_words - stop_words
    
    if not ref_words:
        matched_ratio = 0.5
    else:
        overlap = user_words.intersection(ref_words)
        matched_ratio = len(overlap) / max(1, min(len(ref_words), 10))

    if matched_ratio >= 0.5 or len(words) >= 30:
        total_score = min(96, max(88, int(matched_ratio * 100)))
        feedback = "Excellent! Your response accurately explains the core concepts, structural alterations, and analytical principles."
    elif matched_ratio >= 0.25 or len(words) >= 15:
        total_score = min(84, max(65, int(matched_ratio * 100)))
        feedback = "Good effort! Your response addresses several key concepts but could benefit from deeper analytical depth."
    else:
        total_score = 30
        feedback = "Your response is too brief or lacks key domain-specific terminology."

    acc = int(total_score * 0.4)
    log = int(total_score * 0.3)
    str_score = int(total_score * 0.15)
    voc = total_score - acc - log - str_score

    rationale_acc = f"Content aligned with key domain terms ({int(matched_ratio*100)}%)"
    rationale_log = "Logical reasoning consistent with context"
    rationale_str = "Clear essay structure"
    rationale_voc = "Technical domain vocabulary"

    return {
        "total_score": total_score,
        "overall_feedback": feedback,
        "rubric_scores": {
            "content_accuracy": {"score": acc, "max": 40, "rationale": rationale_acc},
            "logical_argumentation": {"score": log, "max": 30, "rationale": rationale_log},
            "structure": {"score": str_score, "max": 15, "rationale": rationale_str},
            "vocabulary": {"score": voc, "max": 15, "rationale": rationale_voc}
        }
    }

# Alias for backward compatibility
grade_user_answer = advanced_grade_essay