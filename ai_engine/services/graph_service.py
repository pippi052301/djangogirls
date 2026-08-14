import json
<<<<<<< Updated upstream
from .ai_config import client, types

def generate_knowledge_graph(text_content):
    """Bóc tách kiến thức thành Nút (Nodes) và Đường nối (Edges) cho Obsidian."""
    prompt = f"""
    Bạn là một chuyên gia phân tích dữ liệu và trích xuất tri thức (Knowledge Graph).
    Hãy đọc đoạn văn bản sau và trích xuất các từ khóa/khái niệm chính làm các "nodes" (nút), 
    đồng thời tìm ra mối quan hệ giữa chúng làm các "edges" (đường nối).
    
    YÊU CẦU BẮT BUỘC:
    1. Nodes (Nút): Là các danh từ, thuật ngữ, sự kiện hoặc tên riêng quan trọng.
       - 'id': Mã định danh duy nhất (viết liền không dấu).
       - 'label': Tên hiển thị ngắn gọn.
    2. Edges (Đường nối): Thể hiện mối quan hệ 1 chiều.
       - 'from': id của Node bắt đầu.
       - 'to': id của Node đích.
       - 'label': Cụm động từ ngắn gọn mô tả mối quan hệ.
    
    TRẢ VỀ 100% ĐỊNH DẠNG JSON THEO CẤU TRÚC SAU:
=======
from .ai_config import get_client, types 

def generate_knowledge_graph(text_content):
    """Function to generate Knowledge Graph with model fallback."""
    prompt = f"""
    You are a Knowledge Graph AI Expert. Read the source text below and extract key concepts (nodes) 
    and the relationships between them (edges).

    RETURN 100% JSON FORMAT WITH THE FOLLOWING STRUCTURE:
>>>>>>> Stashed changes
    {{
        "nodes": [
            {{"id": "node_1", "label": "Khái niệm A"}},
            {{"id": "node_2", "label": "Khái niệm B"}}
        ],
        "edges": [
            {{"from": "node_1", "to": "node_2", "label": "bao gồm"}}
        ]
    }}

    Văn bản gốc:
    \"\"\"{text_content}\"\"\"
    """
    
<<<<<<< Updated upstream
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Lỗi khi gọi API vẽ Graph: {e}")
        return None
=======
    models_to_try = ['gemini-flash-lite-latest', 'gemini-3.5-flash', 'gemini-3.5-flash-lite', 'gemini-3.7-flash']
    client = get_client()

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            if response and response.text:
                return json.loads(response.text)
        except Exception as e:
            print(f"Error when calling API draw Graph with {model_name}: {e}")
            continue
            
    return None
>>>>>>> Stashed changes
