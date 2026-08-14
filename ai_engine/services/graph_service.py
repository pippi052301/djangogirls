import json
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