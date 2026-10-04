# --- services/chat_service.py ---

from .ai_config import get_client, types


def generate_chat_answer(
    question_text,
    context_type=None,
    context_name=None,
    context_text=None
):
    """Answer student questions with optional study context."""

    client = get_client()

    context_info = ""

    if context_type and context_name:
        context_info = (
            f'[Active Context: {context_type} "{context_name}"]\n'
        )

    if context_text:
        context_info += (
            f'[Study Notes Content for {context_type} "{context_name}"]:\n'
            f'"""\n{context_text}\n"""\n'
        )

    prompt = (
        f"{context_info}"
        f"Student Question: {question_text}"
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
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are a friendly, patient, pedagogical, and knowledgeable AI study tutor. "
                        "Answer questions clearly, accurately, and insightfully. "
                        "Use the provided study topics and notes as context for what the user is studying. "
                        "FACTUAL INTEGRITY RULE: Do NOT blindly treat user notes as infallible truth. "
                        "If the user's notes or question contain a factual error, scientific misconception, or inaccuracy, "
                        "do NOT agree with or reinforce the false claim. Instead, gently and politely clarify the "
                        "discrepancy (e.g., 'I noticed your study note mentions [X], but in scientific reality [Y] is the case because...'). "
                        "Lead them kindly to the truth. "
                        "Avoid outputting raw unrendered LaTeX; write clean formulas or simple plain notation."
                    )
                ),
            )

            if response and response.text:
                return response.text

        except Exception as e:
            print(
                f"Error when calling API Chat "
                f"({model_name}): {e}"
            )
            continue

    return (
        "The AI tutor is currently busy. "
        "Please try again in a moment."
    )