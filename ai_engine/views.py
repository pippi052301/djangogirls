import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError 
from pgvector.django import CosineDistance

from .models import SemanticAICache, ReferenceSample 

from .services.quiz_service import generate_quiz_from_text
from .services.graph_service import generate_knowledge_graph
from .services.adaptive_service import generate_adaptive_practice, advanced_grade_essay, grade_simple_answer
from .services.embedding_service import get_text_embedding 

# --- HÀM TRỢ THỦ XỬ LÝ CACHING ---
SIMILARITY_THRESHOLD = 0.05 # Ngưỡng 95% giống nhau

def check_semantic_cache(text_content, feature_type):
    """Dịch văn bản thành Vector và quét CSDL tìm kết quả giống 95%"""
    input_vector = get_text_embedding(text_content)
    if not input_vector:
        return None, None
        
    matched_cache = SemanticAICache.objects.filter(
        feature_type=feature_type
    ).annotate(
        distance=CosineDistance('text_embedding', input_vector)
    ).filter(
        distance__lt=SIMILARITY_THRESHOLD
    ).order_by('distance').first()
    
    return matched_cache, input_vector

def save_to_cache(text_content, feature_type, input_vector, ai_response):
    """Lưu lại kết quả mới vào kho lưu trữ"""
    if input_vector:
        SemanticAICache.objects.create(
            feature_type=feature_type,
            original_text=text_content,
            text_embedding=input_vector,
            ai_response=ai_response
        )

# --- CÁC API CHÍNH ---

@csrf_exempt
def create_quiz_api(request):
    """API Tạo câu hỏi trắc nghiệm (Tích hợp Semantic Caching)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            num_questions = int(body.get('num_questions', 3))
            
            if not text_content:
                return JsonResponse({"error": "Thiếu nội dung văn bản"}, status=400)
            
            feature_key = f"quiz_n{num_questions}"

            matched_cache, input_vector = check_semantic_cache(text_content, feature_key)
            if matched_cache:
                return JsonResponse({"status": "success", "data": matched_cache.ai_response}, status=200)
            
            quiz_data = generate_quiz_from_text(text_content, num_questions)
            if quiz_data:
                save_to_cache(text_content, feature_key , input_vector, quiz_data)
                return JsonResponse({"status": "success", "data": quiz_data}, status=200)
            
            return JsonResponse({"error": "AI đang bận"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Chỉ chấp nhận phương thức POST"}, status=405)


@csrf_exempt
def create_graph_api(request):
    """API Bóc tách Sơ đồ tư duy (Tích hợp Semantic Caching)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            
            if not text_content:
                return JsonResponse({"error": "Thiếu nội dung văn bản"}, status=400)
            
            matched_cache, input_vector = check_semantic_cache(text_content, "graph")
            if matched_cache:
                return JsonResponse({"status": "success", "data": matched_cache.ai_response}, status=200)
            
            graph_data = generate_knowledge_graph(text_content)
            if graph_data:
                save_to_cache(text_content, "graph", input_vector, graph_data)
                return JsonResponse({"status": "success", "data": graph_data}, status=200)
            
            return JsonResponse({"error": "AI đang bận"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)


@csrf_exempt
def create_adaptive_practice_api(request):
    """API Sinh đề thi thích ứng (Tích hợp Semantic Caching)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            recent_score = int(body.get('recent_score', 50))
            
            if not text_content:
                return JsonResponse({"error": "Thiếu nội dung văn bản"}, status=400)
            
            # --- TẠO KHÓA PHÂN BIỆT THEO NHÓM NĂNG LỰC ---
            if recent_score < 40:
                level = "easy"
            elif recent_score < 75:
                level = "medium"
            else:
                level = "hard"

            feature_key = f"adaptive_{level}"
            
            matched_cache, input_vector = check_semantic_cache(text_content, feature_key)
            if matched_cache:
                return JsonResponse({"status": "success", "data": matched_cache.ai_response}, status=200)
            
            practice_data = generate_adaptive_practice(text_content, recent_score)
            if practice_data:
                save_to_cache(text_content, feature_key, input_vector, practice_data)
                return JsonResponse({"status": "success", "data": practice_data}, status=200)
            
            return JsonResponse({"error": "AI đang bận"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)


@csrf_exempt
def grade_essay_api(request):
    """API Chấm điểm tự luận đa chiều tích hợp Vector Search (RAG)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            question = body.get('question', '')
            user_answer = body.get('user_answer', '')
            standard_key_points = body.get('standard_key_points', '')
            exercise_id = body.get('exercise_id', None) 
            
            if not all([question, user_answer, standard_key_points]):
                return JsonResponse({"error": "Thiếu dữ liệu đầu vào."}, status=400)
            
            sample_essays_text = ""
            if 'sample_essays' in body:
                sample_essays_text = body.get('sample_essays')
            else:
                student_vector = get_text_embedding(user_answer)
                if student_vector:
                    query = ReferenceSample.objects.all()
                    if exercise_id:
                        query = query.filter(exercise_id=exercise_id)
                        
                    similar_samples = query.order_by(CosineDistance('embedding', student_vector))[:3]
                    for idx, sample in enumerate(similar_samples, 1):
                        sample_essays_text += f"\n--- BÀI MẪU SỐ {idx} (ĐIỂM: {sample.score}/100) ---\nBài làm: {sample.content}\nLời phê: {sample.feedback}\n"
            
            grading_result = advanced_grade_essay(question, user_answer, standard_key_points, sample_essays_text)
            if grading_result:
                return JsonResponse({"status": "success", "data": grading_result}, status=200)
            return JsonResponse({"error": "AI đang bận"}, status=503)
                
        except ValidationError as ve:
            return JsonResponse({"error": f"Lỗi dữ liệu Model: {str(ve)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)


@csrf_exempt
def grade_simple_api(request):
    """API Chấm điểm Nhanh (Cho Trắc nghiệm & Điền khuyết)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            question_type = body.get('question_type', '')
            question = body.get('question', '')
            user_answer = body.get('user_answer', '')
            correct_answer = body.get('correct_answer', '')
            explanation = body.get('explanation', 'Không có giải thích.')
            
            if not all([question_type, question, user_answer, correct_answer]):
                return JsonResponse({"error": "Thiếu dữ liệu đầu vào. Cần question_type, question, user_answer, correct_answer"}, status=400)
            
            result = grade_simple_answer(question_type, question, user_answer, correct_answer, explanation)
            
            if result:
                return JsonResponse({"status": "success", "data": result}, status=200)
            return JsonResponse({"error": "Lỗi xử lý"}, status=503)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)