from ai_engine.services.embedding_service import get_text_embedding

# 1. Chuẩn bị một câu văn bất kỳ
sample_text = "MVT là kiến trúc cốt lõi của framework Django."

print(f"⏳ Đang gửi yêu cầu chuyển đổi câu văn sang Vector...")
print(f"Văn bản gốc: '{sample_text}'\n")

# 2. Gọi hàm của bạn
vector_result = get_text_embedding(sample_text)

# 3. Kiểm tra kết quả
if vector_result:
    print("✅ THÀNH CÔNG! AI đã dịch chữ thành mảng số (Vector).")
    print(f"👉 Kiểu dữ liệu trả về: {type(vector_result)}")
    print(f"👉 Tổng số chiều (độ dài mảng): {len(vector_result)} (Gemini chuẩn là 768 chiều)")
    
    # Chỉ in 5 con số đầu tiên ra cho đỡ rối mắt vì mảng rất dài
    print(f"👉 5 tọa độ đầu tiên của Vector: {vector_result[:5]} ...")
else:
    print("❌ THẤT BẠI! Hãy kiểm tra lại kết nối API hoặc file ai_config.py của bạn.")