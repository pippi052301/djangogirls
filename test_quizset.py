import json
from learning.services.adaptive_service import generate_adaptive_practice, grade_user_answer 

sample_text = """
Django là một framework phát triển web bậc cao mã nguồn mở được viết bằng ngôn ngữ lập trình Python. 
Mục tiêu cốt lõi của Django là giúp các nhà phát triển tạo ra các trang web phức tạp, hướng cơ sở dữ liệu một cách nhanh chóng và dễ dàng nhất.
Nó tuân theo kiến trúc MVT (Model - View - Template). Trong đó, Model xử lý dữ liệu và cơ sở dữ liệu, View xử lý logic nghiệp vụ, và Template lo phần giao diện người dùng hiển thị HTML.
"""

# Giả lập điểm trung bình của user này là 60 (Mức khá: sẽ trộn lẫn các dạng câu hỏi)
print("1️⃣ Đang tạo bộ câu hỏi luyện tập có kèm lời giải chi tiết (Lịch sử: 60 điểm)...")
adaptive_quiz = generate_adaptive_practice(sample_text, recent_average_score=60, total_questions=3)

if adaptive_quiz:
    print("✅ Đã tạo xong đề thi! (Lưu ý trường 'explanation' đã xuất hiện ở mọi câu):")
    print(json.dumps(adaptive_quiz, indent=4, ensure_ascii=False))
    
    # -----------------------------------------
    # TEST CHẤM ĐIỂM 
    # -----------------------------------------
    print("\n\n2️⃣ Đang mô phỏng học sinh nộp bài tự luận...")
    
    # Tìm câu tự luận trong bộ câu hỏi vừa sinh ra
    long_question_data = next((q for q in adaptive_quiz if q['type'] == 'long_answer'), None)
    
    if long_question_data:
        question_text = long_question_data['question']
        correct_criteria = long_question_data['key_points']
        
        # Câu trả lời mô phỏng của học sinh
        student_answer = "Django tuân theo kiến trúc MVT, trong đó Model lo giao diện còn Template lo dữ liệu."
        
        print(f"\n- CÂU HỎI: {question_text}")
        print(f"- ĐÁP ÁN CHUẨN (từ Database): {correct_criteria}")
        print(f"- HỌC SINH LÀM: {student_answer}")
        
        print("\n⏳ AI đang chấm bài...")
        grading_result = grade_user_answer(question_text, student_answer, correct_criteria)
        
        print("\n🏆 KẾT QUẢ CHẤM ĐIỂM:")
        print(f"Điểm số: {grading_result['score']}/100")
        print(f"Nhận xét: {grading_result['feedback']}")
    else:
        print("\nBộ câu hỏi này không có câu tự luận để test chấm điểm (Do random). Hãy chạy lại lệnh để thử!")
else:
    print("❌ Thất bại khi gọi API sinh đề thi.")

    # quizset,graph feature, 2 files test of that