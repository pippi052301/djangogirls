# File: ai_engine/services/embedding_service.py
from .ai_config import get_client

def get_text_embedding(text):
    """
    Hàm gọi API Gemini để biến văn bản thành một mảng số (Vector).
    Sử dụng mô hình text-embedding-004 chuyên dụng.
    """
    try:
        result = get_client.models.embed_content(
            model="gemini-embedding-2",
            contents=text,
        )
        # Trả về mảng 768 con số
        return result.embeddings[0].values
    except Exception as e:
        print(f"Lỗi khi tạo Embedding: {e}")
        return None