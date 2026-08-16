from django.test import TestCase
from .services.quiz_service import generate_quiz_from_text
from .services.graph_service import generate_knowledge_graph
from .services.adaptive_service import generate_adaptive_practice, grade_user_answer

class AIEngineIntegrationTests(TestCase):
    """
    Bộ kiểm thử tự động cho các tính năng AI.
    Lưu ý: Các test này sẽ gọi API thật tới Google Gemini nên cần có kết nối mạng.
    """

    def test_quiz_generation(self):
        """Kiểm tra tính năng sinh câu hỏi trắc nghiệm"""
        print("\n--- Testing Quiz Generation ---")
        sample_text = """
        Bóng đá là môn thể thao đồng đội được chơi với một quả bóng hình cầu giữa hai đội. 
        Ngày nay, để đáp ứng nhu cầu tập luyện và thi đấu phong trào, các trận đấu thường được tổ chức trên sân cỏ nhân tạo có hệ thống đèn chiếu sáng vào buổi tối. 
        Điều này giúp người chơi linh hoạt hơn về thời gian sau những giờ học tập và làm việc căng thẳng.
        """
        result = generate_quiz_from_text(sample_text, num_questions=2)
        
        # Khẳng định (Assert): AI phải trả về kết quả, không được bằng None
        self.assertIsNotNone(result, "Lỗi: API trả về None")
        # Khẳng định: Kết quả phải là một mảng (list)
        self.assertIsInstance(result, list)
        # Khẳng định: Bên trong kết quả phải có từ khóa 'question'
        if len(result) > 0:
            self.assertIn('question', result[0])
            print("OK: Test Quiz Success!")

    def test_knowledge_graph_generation(self):
        """Kiểm tra tính năng bóc tách Sơ đồ tư duy"""
        print("\n--- Testing Knowledge Graph Generation ---")
        sample_text = """
        Hệ sinh thái lập trình Web hiện đại thường chia làm hai phần chính: Frontend và Backend. 
        Frontend là phần giao diện người dùng, thường được xây dựng bằng HTML, CSS và JavaScript. 
        Trong khi đó, Backend là hệ thống máy chủ xử lý logic và cơ sở dữ liệu. 
        Python là ngôn ngữ phổ biến cho Backend, với các framework mạnh mẽ như Django.
        """
        graph_result = generate_knowledge_graph(sample_text)
        
        self.assertIsNotNone(graph_result, "Lỗi: API vẽ graph trả về None")
        self.assertIsInstance(graph_result, dict)
        # Khẳng định: Cấu trúc JSON phải chứa 'nodes' và 'edges'
        self.assertIn('nodes', graph_result)
        self.assertIn('edges', graph_result)
        print("OK: Test Graph Success!")

    def test_adaptive_practice_and_grading(self):
        """Kiểm tra luồng Đề thi thích ứng và Chấm điểm tự luận"""
        print("\n--- Testing Adaptive Practice & Grading ---")
        sample_text = """
        Django là một framework phát triển web bậc cao mã nguồn mở được viết bằng ngôn ngữ lập trình Python. 
        Nó tuân theo kiến trúc MVT (Model - View - Template). Trong đó, Model xử lý dữ liệu, View xử lý logic, và Template lo giao diện HTML.
        """
        
        # 1. Test sinh đề (Giả lập điểm 60)
        adaptive_quiz = generate_adaptive_practice(sample_text, recent_average_score=60, total_questions=3)
        self.assertIsNotNone(adaptive_quiz, "Lỗi: API Adaptive trả về None")
        self.assertIsInstance(adaptive_quiz, list)
        
        if len(adaptive_quiz) > 0:
            self.assertIn('explanation', adaptive_quiz[0])
        
        long_question = next((q for q in adaptive_quiz if q['type'] == 'long_answer'), None)
        
        if long_question:
            question_text = long_question['question']
            correct_criteria = long_question['key_points']
            student_answer = "Django tuân theo kiến trúc MVT."
            
            grading_result = grade_user_answer(question_text, student_answer, correct_criteria)
            
            self.assertIsNotNone(grading_result)
            self.assertTrue('score' in grading_result or 'total_score' in grading_result)
            score_val = grading_result.get('total_score', grading_result.get('score'))
            print(f"OK: Test Grading Success (AI Score: {score_val})!")
        else:
            print("OK: Test Adaptive Practice Success!")
