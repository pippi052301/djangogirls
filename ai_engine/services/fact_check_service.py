import json
from .ai_config import get_client, types


def verify_note_accuracy(note_text, note_title=""):
    """
    Analyzes student study notes for factual inaccuracies, scientific errors,
    or common misconceptions.
    Returns a structured assessment including "Are you sure this information is correct?" alerts.
    """
    if not note_text or len(note_text.strip()) < 10:
        return {
            "is_accurate": True,
            "discrepancies": [],
            "summary": "Note content is too short to evaluate factual claims."
        }

    title_context = f"Note Title: {note_title}\n" if note_title else ""

    prompt = f"""
    You are a Senior Academic Fact-Checker and Pedagogical Reviewer.
    Your task is to analyze the following student study notes and verify whether the factual,
    scientific, historical, or conceptual statements are correct.

    [GOAL]
    Identify any statements that are:
    1. Factually incorrect (e.g., wrong scientific mechanism, incorrect historical dates/events, erroneous definitions).
    2. Common misconceptions (e.g., confusing correlation with causation, mistaking organelle functions).
    3. Misleading or contradictory claims.

    [CONSTRAINTS]
    - Do NOT flag stylistic choices, minor grammar mistakes, or subjective personal thoughts.
    - Focus strictly on OBJECTIVE academic, scientific, and factual accuracy.
    - If a note is entirely correct or non-factual, set "is_accurate": true and "discrepancies": [].
    - Always provide constructive, pedagogical feedback in the "reason" and "suggestion" fields.

    [MANDATORY JSON FORMAT]
    {{
        "is_accurate": true,
        "summary": "Brief summary of the factual evaluation.",
        "discrepancies": [
            {{
                "claim_text": "Exact sentence or clause from the note containing the error",
                "severity": "warning",
                "prompt_message": "Are you sure this information is correct?",
                "reason": "Clear, objective explanation of why this information is incorrect or misleading.",
                "suggestion": "The scientifically/factually accurate statement or recommended correction."
            }}
        ]
    }}

    {title_context}Note Content to Review:
    \"\"\"{note_text}\"\"\"
    """

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.6-flash",
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
        "gemini-2.5-flash-lite",
    ]

    try:
        client = get_client()
    except Exception as e:
        print(f"Error obtaining AI client: {e}")
        return {
            "is_accurate": True,
            "discrepancies": [],
            "summary": "AI fact-checking service is unavailable (API key not configured)."
        }

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction=(
                        "You are an impartial, highly rigorous academic fact-checker. "
                        "Evaluate notes with high precision against established academic and scientific truth. "
                        "Respond strictly in valid JSON matching the requested schema."
                    ),
                ),
            )

            if response and response.text:
                data = json.loads(response.text)
                # Ensure structure
                if "is_accurate" not in data:
                    data["is_accurate"] = len(data.get("discrepancies", [])) == 0
                return data

        except Exception as e:
            print(f"Fact-check model {model_name} failed: {e}")
            continue

    return {
        "is_accurate": True,
        "discrepancies": [],
        "summary": "AI fact-checking service is temporarily unavailable."
    }
