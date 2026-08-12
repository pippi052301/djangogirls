import json
from ai_engine.services.adaptive_service import advanced_grade_essay

# 1. DỮ LIỆU ĐẦU VÀO CỐ ĐỊNH (Không cần DB)
question_text = "二次方程式における判別式とは何か。また、判別式の値と実数解の個数との関係を説明しなさい。"
standard_answer = """判別式とは、二次方程式 ax² + bx + c = 0 において、
実数解の個数を判別するために用いられる D = b² - 4ac のことである。
D > 0 のとき異なる2つの実数解をもち、
D = 0 のとき1つの実数解（重解）をもち、
D < 0 のとき実数解をもたない。"""
student_answer = """判別式は D=b²+4ac で求められ、二次方程式の解そのものを計算するための公式である。
D>0なら実数解はなく、D=0なら異なる2つの実数解をもち、D<0なら1つの実数解をもつ。 
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