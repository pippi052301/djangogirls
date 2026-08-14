# File: ai_engine/services/embedding_service.py
from .ai_config import get_client

def get_text_embedding(text):
    """
   Calls the Gemini API to convert text into a numeric array (Vector) 
    using the dedicated text-embedding-004 model.
    """
    try:
        result = get_client().models.embed_content(
            model="gemini-embedding-2",
            contents=text,
        )
        # Trả về mảng 768 con số
        return result.embeddings[0].values
    except Exception as e:
        print(f"Error when creating Embedding: {e}")
        return None