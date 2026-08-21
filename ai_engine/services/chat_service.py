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
                        "You are a friendly, patient, and knowledgeable "
                        "AI study tutor. Answer questions clearly, "
                        "accurately, and insightfully based on the "
                        "user's study topics and notes provided. "
                        "Avoid outputting raw unrendered LaTeX; "
                        "write clean formulas or simple plain notation."
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