import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError
from django.utils import timezone
from pgvector.django import CosineDistance

from .models import SemanticAICache, ReferenceSample
from learning.models import (
    Exercise,
    QuizAttempt,
    TutorSession,
    TutorMessage,
)

from .services.quiz_service import generate_quiz_from_text
from .services.graph_service import generate_knowledge_graph
from .services.adaptive_service import generate_adaptive_practice, advanced_grade_essay, grade_simple_answer
from .services.embedding_service import get_text_embedding 
from .services.chat_service import generate_chat_answer
from .services.tutor_chat_service import generate_tutor_chat_response
# --- CACHING HELPER FUNCTIONS ---
SIMILARITY_THRESHOLD = 0.035 

def check_semantic_cache(text_content, feature_type):
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
    """Save new to DB"""
    if input_vector:
        SemanticAICache.objects.create(
            feature_type=feature_type,
            original_text=text_content,
            text_embedding=input_vector,
            ai_response=ai_response
        )

# --- Main API ---

@csrf_exempt
def create_quiz_api(request):
    """Multiple-Choice Question Generation API (Integrated Semantic Caching)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            num_questions = int(body.get('num_questions', 3))
            
            if not text_content:
                return JsonResponse({"error": "Not enough content"}, status=400)
            
            # Call AI no cache
            quiz_data = generate_quiz_from_text(text_content, num_questions)
            
            if quiz_data:
                return JsonResponse({"status": "success", "data": quiz_data}, status=200) 
            return JsonResponse({"error": "AI busy"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Just accept POST"}, status=405)


@csrf_exempt
def create_graph_api(request):
    """Knowledge Graph Extraction API (Integrated Semantic Caching)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            
            if not text_content:
                return JsonResponse({"error": "Missing text content"}, status=400)
            
            matched_cache, input_vector = check_semantic_cache(text_content, "graph")
            if matched_cache:
                return JsonResponse({"status": "success", "data": matched_cache.ai_response}, status=200)
            
            graph_data = generate_knowledge_graph(text_content)
            if graph_data:
                save_to_cache(text_content, "graph", input_vector, graph_data)
                return JsonResponse({"status": "success", "data": graph_data}, status=200)
            
            return JsonResponse({"error": "AI busy"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def create_adaptive_practice_api(request):
    """Adaptive Exam Generation API (Semantic Caching Removed)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            recent_score = int(body.get('recent_score', 50))
            
            if not text_content:
                return JsonResponse({"error": "Not enough content"}, status=400)
            
            # --- Creates a differentiation key based on competency groups (Preserves legacy logic).
            if recent_score < 40:
                level = "easy"
            elif recent_score < 75:
                level = "medium"
            else:
                level = "hard"

            feature_key = f"adaptive_{level}"
            # -------------------------------------------------------------------
            
            # Call AI (no check_semantic_cache)
            practice_data = generate_adaptive_practice(text_content, recent_score)
            
            if practice_data:
                return JsonResponse({"status": "success", "data": practice_data}, status=200)
            
            return JsonResponse({"error": "AI busy"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
def grade_essay_api(request):
    """Multidimensional Essay Grading API with Vector Search (RAG) Integration"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            question = body.get('question', '')
            user_answer = body.get('user_answer', '')
            standard_key_points = body.get('standard_key_points', [])
            exercise_id = body.get('exercise_id', None) 
            
            if not all([question, user_answer, standard_key_points]):
                return JsonResponse({"error": "Not enough content."}, status=400)
            
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
                        sample_essays_text += f"\n--- Sample ID {idx} (SCORE: {sample.score}/100) ---\nAnswer: {sample.content}\nFeedback: {sample.feedback}\n"
            
            grading_result = advanced_grade_essay(question, user_answer, standard_key_points, sample_essays_text)
            if grading_result:
                return JsonResponse({"status": "success", "data": grading_result}, status=200)
            return JsonResponse({"error": "AI busy"}, status=503)
                
        except ValidationError as ve:
            return JsonResponse({"error": f"Error data Model: {str(ve)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid Method"}, status=405)

@csrf_exempt
def student_chat_api(request):
    """AI Chat API with Integrated Semantic Caching"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_question = body.get('question', '').strip()
            
            if not user_question:
                return JsonResponse({"error": "Please enter your question"}, status=400)
            
            # 1.CHECK CACHE FIRST WITH KEY 'chat_qa'
            feature_key = "chat_qa"
            matched_cache, input_vector = check_semantic_cache(user_question, feature_key)
            
            if matched_cache:
                # If the question has been asked before, return immediately
                return JsonResponse({
                    "status": "success", 
                    "data": matched_cache.ai_response,
                    "is_cached": True 
                }, status=200)
            
            # 2. CALL AI IF NOT FOUND IN CACHE
            ai_answer = generate_chat_answer(user_question)
            
            if ai_answer:
                # 3. SAVE TO CACHE FOR FUTURE REQUESTS
                save_to_cache(user_question, feature_key, input_vector, ai_answer)
                return JsonResponse({
                    "status": "success", 
                    "data": ai_answer,
                    "is_cached": False
                }, status=200)
            
            return JsonResponse({"error": "The AI tutor is busy, please try again later"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def grade_simple_api(request):
    """Rapid Grading API (For Multiple-Choice & Fill-in-the-Blank)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            question_type = body.get('question_type', '')
            question = body.get('question', '')
            user_answer = body.get('user_answer', '')
            correct_answer = body.get('correct_answer', '')
            explanation = body.get('explanation', 'No explan.')
            
            if not all([question_type, question, user_answer, correct_answer]):
                return JsonResponse({"error": "Not enough content. Need question_type, question, user_answer, correct_answer"}, status=400)
            
            result = grade_simple_answer(question_type, question, user_answer, correct_answer, explanation)
            
            if result:
                return JsonResponse({"status": "success", "data": result}, status=200)
            return JsonResponse({"error": "Error handle"}, status=503)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)


def tutor_chat_api(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Bạn cần đăng nhập để sử dụng gia sư AI."},
            status=401,
        )

    if request.method != "POST":
        return JsonResponse(
            {"error": "Chỉ chấp nhận phương thức POST."},
            status=405,
        )

    try:
        body = json.loads(request.body)

        student_input = body.get("student_input", "").strip()
        session_id = body.get("session_id")
        exercise_id = body.get("exercise_id")
        quiz_attempt_id = body.get("quiz_attempt_id")

        if not student_input:
            return JsonResponse(
                {"error": "Thiếu nội dung câu trả lời của học sinh."},
                status=400,
            )

        # =========================
        # 1. Session取得 / 作成
        # =========================

        if session_id:
            session = TutorSession.objects.filter(
                id=session_id,
                user=request.user,
            ).first()

            if not session:
                return JsonResponse(
                    {
                        "error":
                        "Không tìm thấy session, hoặc session không thuộc về bạn."
                    },
                    status=404,
                )

        else:
            if not exercise_id:
                return JsonResponse(
                    {"error": "Thiếu exercise_id cho lượt chat đầu tiên."},
                    status=400,
                )

            exercise = Exercise.objects.filter(
                id=exercise_id
            ).first()

            if not exercise:
                return JsonResponse(
                    {"error": "Không tìm thấy bài tập."},
                    status=404,
                )

            if (
                exercise.question_type
                != Exercise.QuestionType.LONG_ANSWER
            ):
                return JsonResponse(
                    {"error": "AI Tutor chỉ hỗ trợ câu hỏi tự luận."},
                    status=400,
                )

            quiz_attempt = None

            if quiz_attempt_id:
                quiz_attempt = QuizAttempt.objects.filter(
                    id=quiz_attempt_id,
                    user=request.user,
                ).first()

                if not quiz_attempt:
                    return JsonResponse(
                        {"error": "Không tìm thấy quiz attempt."},
                        status=404,
                    )

            session = TutorSession.objects.create(
                user=request.user,
                exercise=exercise,
                quiz_attempt=quiz_attempt,
            )

        # =========================
        # 2. DBから履歴取得
        # =========================

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in session.messages.all()
        ]

        # =========================
        # 3. AI Tutor呼び出し
        # =========================

        ai_result = generate_tutor_chat_response(
            conversation_history=conversation_history,
            student_input=student_input,
            question_prompt=session.exercise.question,
            required_key_points=session.exercise.key_points,
        )

        if not ai_result:
            return JsonResponse(
                {
                    "error":
                    "Hệ thống AI đang bận, vui lòng thử lại sau."
                },
                status=503,
            )

        # =========================
        # 4. 会話をDBへ保存
        # =========================

        TutorMessage.objects.create(
            session=session,
            role=TutorMessage.Role.USER,
            content=student_input,
        )

        TutorMessage.objects.create(
            session=session,
            role=TutorMessage.Role.MODEL,
            content=ai_result.get("ai_message", ""),
        )

        # =========================
        # 5. Session状態更新
        # =========================

        session.is_ready_for_grading = bool(
            ai_result.get("is_ready_for_grading", False)
        )

        if ai_result.get("compiled_final_answer"):
            session.compiled_final_answer = (
                ai_result["compiled_final_answer"]
            )

        session.save()

        return JsonResponse(
            {
                "status": "success",
                "session_id": session.id,
                "data": ai_result,
            },
            status=200,
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Dữ liệu gửi lên không phải định dạng JSON hợp lệ."},
            status=400,
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
        )

def build_grading_payload_from_tutor_result(tutor_result, question_prompt, required_key_points):
    """Cầu nối giữa tutor_chat_api và grade_essay_api."""
    return {
        "question": question_prompt,
        "user_answer": tutor_result["compiled_final_answer"],
        "standard_key_points": required_key_points,
    }


def submit_tutor_essay_for_grading_api(request):
    """
    Chấm điểm bài luận sau khi tutor chat báo is_ready_for_grading=True.
    Client chỉ cần gửi session_id; toàn bộ dữ liệu bài làm
    (question_prompt, required_key_points, compiled_final_answer) lấy thẳng
    từ TutorSession đã lưu, tránh trường hợp client tự gửi sai lệch dữ liệu.
    Kết quả chấm được lưu ngược lại vào chính session đó (session.grading_result).
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Bạn cần đăng nhập để sử dụng tính năng này."}, status=401)

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            session_id = body.get('session_id')

            if not session_id:
                return JsonResponse({"error": "Thiếu session_id"}, status=400)

            session = TutorSession.objects.filter(session_id=session_id, student=request.user).first()
            if not session:
                return JsonResponse({"error": "Không tìm thấy session"}, status=404)

            if not session.is_ready_for_grading or not session.compiled_final_answer:
                return JsonResponse({"error": "Session chưa sẵn sàng để chấm điểm (is_ready_for_grading=False)"}, status=400)

            payload = build_grading_payload_from_tutor_result(
                {"compiled_final_answer": session.compiled_final_answer},
                session.question_prompt,
                session.required_key_points
            )
            grading_result = advanced_grade_essay(**payload)  # unpack đúng khớp tên tham số

            if grading_result:
                session.grading_result = grading_result
                session.graded_at = timezone.now()
                session.save()
                return JsonResponse({"status": "success", "data": grading_result}, status=200)
            return JsonResponse({"error": "AI busy"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)


@require_GET
def tutor_history_api(request):
    """Xem lại lịch sử làm bài (các phiên tutor chat) của học sinh đang đăng nhập."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Bạn cần đăng nhập để xem lịch sử."}, status=401)

    sessions = TutorSession.objects.filter(student=request.user)[:50]
    data = [
        {
            "session_id": str(s.session_id),
            "question_prompt": s.question_prompt,
            "is_ready_for_grading": s.is_ready_for_grading,
            "score": (s.grading_result or {}).get("total_score"),
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]
    return JsonResponse({"status": "success", "data": data}, status=200)
