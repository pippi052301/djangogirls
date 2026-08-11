import json
from learning.services.graph_service import generate_knowledge_graph # Nhớ trỏ đúng đường dẫn của bạn

# Văn bản đầu vào khá phức tạp để thử thách AI
sample_text = """
Hệ sinh thái lập trình Web hiện đại thường chia làm hai phần chính: Frontend và Backend. 
Frontend là phần giao diện người dùng, thường được xây dựng bằng HTML, CSS và JavaScript. 
Các framework nổi tiếng của Frontend bao gồm ReactJS và VueJS.
Trong khi đó, Backend là hệ thống máy chủ xử lý logic và cơ sở dữ liệu. 
Python là ngôn ngữ phổ biến cho Backend, với các framework mạnh mẽ như Django và FastAPI. 
Backend và Frontend giao tiếp với nhau thông qua API.
"""

print("🧠 Đang phân tích văn bản để vẽ bản đồ tri thức...\n")
graph_result = generate_knowledge_graph(sample_text)

if graph_result:
    print("✅ TRÍCH XUẤT THÀNH CÔNG! Dữ liệu đã sẵn sàng để vẽ sơ đồ Obsidian:\n")
    # In ra dạng JSON có indent=4 để kiểm tra mắt thường
    print(json.dumps(graph_result, indent=4, ensure_ascii=False))
else:
    print("❌ THẤT BẠI!")