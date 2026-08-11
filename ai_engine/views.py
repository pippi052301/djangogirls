import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import các hàm AI từ thư mục services của bạn
from .services.quiz_service import generate_quiz_from_text
from .services.graph_service import generate_knowledge_graph
from .services.adaptive_service import generate_adaptive_practice, grade_user_answer

@csrf_exempt # Tạm thời tắt kiểm tra CSRF để Frontend dễ test API
def create_quiz_api(request):
    """API Tạo câu hỏi trắc nghiệm thông thường"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            num_questions = body.get('num_questions', 3)
            
            if not text_content:
                return JsonResponse({"error": "Thiếu nội dung văn bản (text)"}, status=400)
            
            # Gọi hàm AI của bạn
            quiz_data = generate_quiz_from_text(text_content, num_questions)
            
            if quiz_data:
                return JsonResponse({"status": "success", "data": quiz_data}, status=200)
            else:
                return JsonResponse({"error": "AI đang bận hoặc lỗi xử lý"}, status=503)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Chỉ chấp nhận phương thức POST"}, status=405)


@csrf_exempt
def create_graph_api(request):
    """API Bóc tách Sơ đồ tư duy"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            
            if not text_content:
                return JsonResponse({"error": "Thiếu nội dung văn bản (text)"}, status=400)
            
            graph_data = generate_knowledge_graph(text_content)
            
            if graph_data:
                return JsonResponse({"status": "success", "data": graph_data}, status=200)
            else:
                return JsonResponse({"error": "AI đang bận hoặc lỗi xử lý"}, status=503)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)


@csrf_exempt
def create_adaptive_practice_api(request):
    """API Sinh đề thi thích ứng (có lời giải)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            recent_score = body.get('recent_score', 50)
            
            if not text_content:
                return JsonResponse({"error": "Thiếu nội dung văn bản"}, status=400)
            
            practice_data = generate_adaptive_practice(text_content, recent_score)
            
            if practice_data:
                return JsonResponse({"status": "success", "data": practice_data}, status=200)
            else:
                return JsonResponse({"error": "AI đang bận"}, status=503)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)