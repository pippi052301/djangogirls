import json
# Đảm bảo bạn trỏ đúng đường dẫn đến file ai.py hoặc ai_service.py của bạn
# Ví dụ: nếu file ai_service.py nằm ngang hàng với manage.py thì dùng import thẳng
# Nếu nằm trong thư mục learning thì dùng: from learning.ai_service import generate_quiz_from_text
from learning.services.ai_service import generate_quiz_from_text 

# 1. Chuẩn bị đầu vào (Văn bản mẫu)
sample_text = """
Bóng đá là môn thể thao đồng đội được chơi với một quả bóng hình cầu giữa hai đội. 
Ngày nay, để đáp ứng nhu cầu tập luyện và thi đấu phong trào, các trận đấu thường được tổ chức trên sân cỏ nhân tạo có hệ thống đèn chiếu sáng vào buổi tối. 
Điều này giúp người chơi linh hoạt hơn về thời gian sau những giờ học tập và làm việc căng thẳng.
"""

# 2. Chạy thử hàm AI
print("🤖 Đang gửi yêu cầu cho AI (Gemini 2.0)... Vui lòng chờ vài giây...\n")
result = generate_quiz_from_text(sample_text, num_questions=2)

# 3. Kiểm tra và hiển thị kết quả
if result:
    print("✅ THÀNH CÔNG! Dưới đây là dữ liệu JSON AI trả về:\n")
    # In ra dạng JSON có căn lề (indent=4) cho dễ nhìn
    json_string = json.dumps(result, indent=4, ensure_ascii=False)
    print(json_string)
else:
    print("❌ THẤT BẠI! Hãy kiểm tra lại API Key hoặc lỗi trong code.")