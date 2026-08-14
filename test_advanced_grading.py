import json
from ai_engine.services.adaptive_service import advanced_grade_essay

# 1. DỮ LIỆU ĐẦU VÀO CỐ ĐỊNH (Không cần DB)
question_text = "Explain the discriminant D in a quadratic equation and describe how its value determines the number of real solutions."
standard_answer = """The discriminant of a quadratic equation is defined as D = b² - 4ac.

The value of D determines the number of real solutions of the quadratic equation.

If D > 0, the equation has two distinct real solutions.
If D = 0, the equation has one repeated real solution.
If D < 0, the equation has no real solutions."""

student_answer = """The discriminant is D = b² - 4ac, which is used to determine the number of real solutions of a quadratic equation ax² + bx + c = 0.

If D > 0, the equation has two distinct real solutions. If D = 0, the equation has one real solution (a repeated root). If D < 0, the equation has no real solutions.
  
"""

# 2. GIẢ LẬP DỮ LIỆU TỪ PGVECTOR (Bạn tự viết tay 2 bài mẫu)
fake_retrieved_samples = """
--- BÀI MẪU SỐ 1 (ĐIỂM: 100/100) ---
Bài làm: "Kiến trúc MVT của Django gồm 3 phần chính. Model chịu trách nhiệm định nghĩa cấu trúc dữ liệu và tương tác với Database. View đóng vai trò trung gian, tiếp nhận request, xử lý logic nghiệp vụ và trả về response. Template là lớp giao diện, kết xuất dữ liệu HTML để hiển thị cho người dùng."
Nhận xét của giáo viên: Lập luận chặt chẽ, dùng đúng từ chuyên ngành (request, response, kết xuất), cấu trúc rõ ràng.

--- BÀI MẪU SỐ 2 (ĐIỂM: 40/100) ---
Bài làm: "MVT có 3 cái là model view template. Model làm data, template làm html."
Nhận xét của giáo viên: Thiếu hẳn vai trò của View. Câu văn lủng củng, không có tính logic, từ vựng quá bình dân.
"""

# 3. CHẠY THỬ NGHIỆM
print("⏳ AI đang đọc bài mẫu và tiến hành chấm điểm...\n")
result = advanced_grade_essay(
    question=question_text,
    user_answer=student_answer,
    standard_key_points=standard_answer,
    sample_essays=fake_retrieved_samples # Truyền thẳng dữ liệu giả vào đây!
)

# 4. XEM KẾT QUẢ
if result:
    print("✅ HOÀN TẤT CHẤM ĐIỂM! BẢNG ĐIỂM ĐA CHIỀU:")
    print(json.dumps(result, indent=4, ensure_ascii=False))
else:
    print("❌ Lỗi gọi API.")