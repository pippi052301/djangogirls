import json
import os
import re
import html
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError
from django.utils import timezone
from pgvector.django import CosineDistance

from .models import SemanticAICache, ReferenceSample
from learning.models import (
    Quiz,
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


import html

def extract_clean_note_text(note_obj):
    """Extract plain text or PDF text content without raw JSON/data URI or HTML noise."""
    if not note_obj:
        return ""
    c = note_obj.content
    text_out = ""
    if isinstance(c, dict):
        text_out = c.get('body') or c.get('text') or ""
    elif isinstance(c, str):
        if c.startswith('{') and ('pdf_data' in c or 'body' in c or 'text' in c):
            try:
                parsed = json.loads(c)
                text_out = parsed.get('body') or parsed.get('text') or ""
            except Exception:
                text_out = c
        else:
            text_out = c
    else:
        text_out = str(c or '')

    if text_out:
        text_out = html.unescape(text_out)
        text_out = re.sub(r'<br\s*/?>', '\n', text_out, flags=re.I)
        text_out = re.sub(r'</p>', '\n', text_out, flags=re.I)
        text_out = re.sub(r'</div>', '\n', text_out, flags=re.I)
        text_out = re.sub(r'<[^>]+>', '', text_out)
        text_out = re.sub(r'[ \t]+', ' ', text_out)

    if not text_out.strip():
        text_out = note_obj.title
    return text_out.strip()


def check_sufficient_content(text_content, context_name=""):
    """
    Validates study text:
    - Minimum requirement: 15 words AND 60 characters
    - Recommended target for optimal AI accuracy: 50+ words (300+ characters)
    """
    if not text_content:
        return False, f"This item '{context_name}' does not contain enough information for AI to generate a Knowledge Graph or Practice Test. (Minimum required: 15 words / 60 characters). Please add more study content to your note or select a different folder/note!", False

    clean_text = text_content.strip()
    words = [w for w in clean_text.split() if len(w) > 1 and w not in ('Note', 'Title', 'Content', 'Folder')]
    char_count = len(clean_text)

    # Minimum Required Threshold
    if len(words) < 15 or char_count < 60:
        return False, f"This item '{context_name or 'Study Material'}' does not contain enough information for AI to generate a Knowledge Graph or Practice Test. (Minimum required: 15 words / 60 characters). Please add more study content to your note or select a different folder/note!", False

    # Recommended Target for Maximum AI Precision
    is_recommended = (len(words) >= 50 or char_count >= 300)
    rec_tip = "" if is_recommended else "💡 Recommended: For maximum AI question precision and deep Knowledge Graphs, we recommend adding 50+ words (300+ characters) of detailed study content!"

    return True, rec_tip, is_recommended

@csrf_exempt
def create_graph_api(request):
    """Knowledge Graph API: Combines DB Folder/Notes tree with Gemini AI Concept Extraction"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            context_type = body.get('context_type', '')
            context_name = body.get('context_name', '')
            text_content = body.get('text', '')

            from notes.models import Note, Folder

            nodes_list = []
            edges_list = []
            full_text_to_analyze = ""
            raw_user_text = ""

            # 1. Gather DB Folder and Notes structure
            if request.user.is_authenticated and context_type == 'folder' and context_name:
                folder = Folder.objects.filter(owner=request.user, name=context_name).first()
                if folder:
                    folder_notes = folder.notes.all()
                    if not folder_notes.exists():
                        return JsonResponse({
                            "status": "warning",
                            "insufficient_content": True,
                            "message": f"This item '{folder.name}' does not contain enough information for AI to generate a Knowledge Graph or Practice Test. (Minimum required: 15 words / 60 characters). Please add more study content to your note or select a different folder/note!"
                        }, status=200)

                    folder_id = f"folder_{folder.id}"
                    nodes_list.append({"id": folder_id, "label": f"📁 {folder.name}"})
                    
                    full_text_to_analyze = f"Folder '{folder.name}' study material:\n"
                    for note_obj in folder_notes:
                        note_id = f"note_{note_obj.id}"
                        nodes_list.append({"id": note_id, "label": f"📄 {note_obj.title}"})
                        edges_list.append({"from": folder_id, "to": note_id, "label": "contains"})
                        
                        note_body = extract_clean_note_text(note_obj)
                        full_text_to_analyze += f"\nNote Title: {note_obj.title}\nContent: {note_body}\n"
                        raw_user_text += f" {note_obj.title} {note_body}"

            elif request.user.is_authenticated and context_type == 'note' and context_name:
                note = Note.objects.filter(owner=request.user, title=context_name).first()
                if note:
                    note_id = f"note_{note.id}"
                    nodes_list.append({"id": note_id, "label": f"📄 Note: {note.title}"})
                    note_body = extract_clean_note_text(note)
                    full_text_to_analyze = f"Note Title: {note.title}\nContent: {note_body}"
                    raw_user_text = f"{note.title} {note_body}"

            if not full_text_to_analyze:
                full_text_to_analyze = text_content
                raw_user_text = text_content

            # Check content sufficiency using raw user study text
            is_valid, rec_tip, is_recommended = check_sufficient_content(raw_user_text, context_name)
            if not is_valid:
                return JsonResponse({
                    "status": "warning",
                    "insufficient_content": True,
                    "message": rec_tip
                }, status=200)

            # 2. Extract Key Concepts & Relationships via Gemini AI
            ai_graph = generate_knowledge_graph(full_text_to_analyze)

            if ai_graph and isinstance(ai_graph, dict):
                ai_nodes = ai_graph.get('nodes', [])
                ai_edges = ai_graph.get('edges', [])

                # Add AI extracted concept nodes
                existing_ids = {n['id'] for n in nodes_list}
                for ai_n in ai_nodes:
                    node_id = str(ai_n.get('id', ''))
                    if node_id and node_id not in existing_ids:
                        nodes_list.append({
                            "id": node_id,
                            "label": f"💡 {ai_n.get('label', node_id)}"
                        })
                        existing_ids.add(node_id)
                        # Link root folder/note ONLY if no edges exist
                        if len(nodes_list) > 1 and not edges_list:
                            edges_list.append({
                                "from": nodes_list[0]['id'],
                                "to": node_id,
                                "label": "concept"
                            })

                for ai_e in ai_edges:
                    src = str(ai_e.get('from', ''))
                    tgt = str(ai_e.get('to', ''))
                    if src and tgt and src in existing_ids and tgt in existing_ids:
                        edges_list.append({
                            "from": src,
                            "to": tgt,
                            "label": ai_e.get('label', 'relates')
                        })

            # Return merged Knowledge Graph
            if nodes_list:
                return JsonResponse({
                    "status": "success",
                    "recommendation_tip": rec_tip,
                    "is_recommended": is_recommended,
                    "data": {
                        "nodes": nodes_list,
                        "edges": edges_list
                    }
                }, status=200)

            return JsonResponse({"error": "AI busy"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def create_adaptive_practice_api(request):
    """Adaptive Exam Generation API with Content Validation and Recommendation Tip"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            context_type = body.get('context_type', '')
            context_name = body.get('context_name', '')
            text_content = body.get('text', '')
            recent_score = int(body.get('recent_score', 50))
            
            from notes.models import Note, Folder
            full_text_to_analyze = text_content
            raw_user_text = text_content

            if request.user.is_authenticated:
                from learning.models import Attempt
                db_recent_avg = Attempt.objects.recent_average_score_for(request.user)
                if db_recent_avg is not None:
                    recent_score = float(db_recent_avg)
                
                
                print("DEBUG recent_score =", recent_score)
            

                if context_type == 'folder' and context_name:
                    folder = Folder.objects.filter(owner=request.user, name=context_name).first()
                    if folder:
                        folder_notes = folder.notes.all()
                        if not folder_notes.exists():
                            return JsonResponse({
                                "status": "warning",
                                "insufficient_content": True,
                                "message": f"This item '{folder.name}' does not contain enough information for AI to generate a Knowledge Graph or Practice Test. (Minimum required: 15 words / 60 characters). Please add more study content to your note or select a different folder/note!"
                            }, status=200)

                        full_text_to_analyze = f"Folder '{folder.name}' study material:\n"
                        raw_user_text = ""
                        for note_obj in folder_notes:
                            note_body = extract_clean_note_text(note_obj)
                            full_text_to_analyze += f"\nNote Title: {note_obj.title}\nContent: {note_body}\n"
                            raw_user_text += f" {note_obj.title} {note_body}"

                elif context_type == 'note' and context_name:
                    note = Note.objects.filter(owner=request.user, title=context_name).first()
                    if note:
                        note_body = extract_clean_note_text(note)
                        full_text_to_analyze = f"Note Title: {note.title}\nContent: {note_body}"
                        raw_user_text = f"{note.title} {note_body}"

            # Check content sufficiency using raw user study text
            is_valid, rec_tip, is_recommended = check_sufficient_content(raw_user_text, context_name)
            if not is_valid:
                return JsonResponse({
                    "status": "warning",
                    "insufficient_content": True,
                    "message": rec_tip
                }, status=200)
            
            practice_data = generate_adaptive_practice(full_text_to_analyze, recent_score)
            
            if practice_data:
                if request.user.is_authenticated and context_type == "note" and context_name:
                    note = Note.objects.filter(
                        owner=request.user,
                        title=context_name
                    ).first()

                    if note:
                        quiz = Quiz.objects.create(
                            note=note,
                            title="Adaptive Practice"
                        )

                        for index, item in enumerate(practice_data, start=1):
                            qtype = item.get("type", "multiple_choice")

                            exercise = Exercise.objects.create(
                                quiz=quiz,
                                order=index,
                                question_type=qtype,
                                recent_average_score=f"{recent_score:.2f}",
                                question=item.get("question", ""),
                                options=(
                                    item.get("options", {})
                                    if qtype == "multiple_choice"
                                    else {}
                                ),
                                correct_answer=(
                                    item.get("correct_answer", "")
                                    if qtype == "multiple_choice"
                                    else item.get("sample_answer", "")
                                    if qtype == "short_answer"
                                    else ""
                                ),
                                key_points=(
                                    item.get("key_points", [])
                                    if qtype == "long_answer"
                                    else []
                                ),
                                explanation=item.get("explanation", ""),
                            )

                            item["exercise_id"] = exercise.id

                return JsonResponse({
                    "status": "success",
                    "recommendation_tip": rec_tip,
                    "is_recommended": is_recommended,
                    "data": practice_data
                }, status=200)
            
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
                try:
                    student_vector = get_text_embedding(user_answer)
                    if student_vector:
                        query = ReferenceSample.objects.all()
                        if exercise_id:
                            query = query.filter(exercise_id=exercise_id)
                            
                        similar_samples = query.order_by(CosineDistance('embedding', student_vector))[:3]
                        for idx, sample in enumerate(similar_samples, 1):
                            sample_essays_text += f"\n--- Sample ID {idx} (SCORE: {sample.score}/100) ---\nAnswer: {sample.content}\nFeedback: {sample.feedback}\n"
                except Exception as e:
                    print(f"pgvector ReferenceSample search bypass: {e}")
            
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
    """AI Chat API with secure notes/folder context support."""
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        body = json.loads(request.body)
        user_question = (body.get('question') or body.get('prompt') or '').strip()
        context_type = body.get('context_type')
        context_name = body.get('context_name')

        if not user_question:
            return JsonResponse(
                {
                    "error": "Please enter your question",
                    "response": "Please enter your question.",
                },
                status=400,
            )

        context_text = ""

        # Only load private note/folder context for the authenticated owner.
        if request.user.is_authenticated and context_type and context_name:
            from notes.models import Note, Folder

            if context_type == 'folder':
                folder = Folder.objects.filter(
                    owner=request.user,
                    name=context_name,
                ).first()

                if folder:
                    notes = Note.objects.filter(folder=folder, owner=request.user)
                    if notes.exists():
                        context_text = "\n\n".join(
                            [
                                f"Note Title: {note.title}\n"
                                f"Content:\n{extract_clean_note_text(note)}"
                                for note in notes
                            ]
                        )

            elif context_type == 'note':
                note = Note.objects.filter(
                    owner=request.user,
                    title=context_name,
                ).first()

                if note:
                    context_text = (
                        f"Note Title: {note.title}\n"
                        f"Content:\n{extract_clean_note_text(note)}"
                    )

        # Chat responses are not semantically cached here because the answer
        # can depend on user-specific note context and should remain dynamic.
        ai_answer = generate_chat_answer(
            user_question,
            context_type,
            context_name,
            context_text,
        )

        if ai_answer:
            return JsonResponse(
                {
                    "status": "success",
                    "data": ai_answer,
                    "response": ai_answer,
                    "is_cached": False,
                },
                status=200,
            )

        return JsonResponse(
            {
                "error": "The AI tutor is busy, please try again later",
                "response": "The AI tutor is currently busy. Please try again in a moment.",
            },
            status=503,
        )

    except Exception as e:
        return JsonResponse(
            {
                "error": str(e),
                "response": f"Error: {str(e)}",
            },
            status=400,
        )
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

def build_grading_payload_from_tutor_result(
    tutor_result,
    question_prompt,
    required_key_points,
):
    """Bridge TutorSession output to the essay grading service."""
    return {
        "question": question_prompt,
        "user_answer": tutor_result["compiled_final_answer"],
        "standard_key_points": required_key_points,
    }


def submit_tutor_essay_for_grading_api(request):
    """
    Grade a TutorSession after the tutor marks it ready.
    The client only sends session_id; question/key points/final answer come from DB.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Bạn cần đăng nhập để sử dụng tính năng này."},
            status=401,
        )

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        body = json.loads(request.body)
        session_id = body.get("session_id")

        if not session_id:
            return JsonResponse({"error": "Thiếu session_id"}, status=400)

        session = TutorSession.objects.select_related("exercise").filter(
            id=session_id,
            user=request.user,
        ).first()

        if not session:
            return JsonResponse({"error": "Không tìm thấy session"}, status=404)

        if not session.is_ready_for_grading or not session.compiled_final_answer:
            return JsonResponse(
                {
                    "error":
                    "Session chưa sẵn sàng để chấm điểm "
                    "(is_ready_for_grading=False)"
                },
                status=400,
            )

        grading_result = advanced_grade_essay(
            question=session.exercise.question,
            user_answer=session.compiled_final_answer,
            standard_key_points=session.exercise.key_points,
        )

        if grading_result:
            return JsonResponse(
                {"status": "success", "data": grading_result},
                status=200,
            )

        return JsonResponse({"error": "AI busy"}, status=503)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
@login_required
def ai_home(request):
    prompt = request.GET.get('prompt', '')
    from notes.models import Note, Folder
    user_notes = Note.objects.filter(owner=request.user) if request.user.is_authenticated else []
    user_folders = Folder.objects.filter(owner=request.user) if request.user.is_authenticated else []
    standalone_notes = Note.objects.filter(owner=request.user, folder__isnull=True) if request.user.is_authenticated else []
    return render(request, 'ai_engine_base.html', {
        'initial_prompt': prompt,
        'user_notes': user_notes,
        'user_folders': user_folders,
        'standalone_notes': standalone_notes,
    })


@login_required
def quiz_list_view(request):
    from learning.models import Quiz, QuizAttempt, Attempt
    from notes.models import Note, Folder
    from django.db import models

    user_notes = Note.objects.filter(owner=request.user) if request.user.is_authenticated else []
    user_folders = Folder.objects.filter(owner=request.user) if request.user.is_authenticated else []
    standalone_notes = Note.objects.filter(owner=request.user, folder__isnull=True) if request.user.is_authenticated else []

    user_quizzes = Quiz.objects.filter(note__owner=request.user).order_by('-created_at') if request.user.is_authenticated else []
    user_attempts = QuizAttempt.objects.filter(user=request.user).select_related('quiz').order_by('-started_at') if request.user.is_authenticated else []

    quizzes_data = []
    for quiz in user_quizzes:
        latest_attempt = user_attempts.filter(quiz=quiz).first()
        attempts = Attempt.objects.filter(quiz_attempt__quiz=quiz, quiz_attempt__user=request.user) if request.user.is_authenticated else []
        avg_score = attempts.aggregate(avg=models.Avg('score'))['avg'] if attempts.exists() else None

        quizzes_data.append({
            'id': quiz.id,
            'title': quiz.title,
            'note_title': quiz.note.title if quiz.note else 'General Study Note',
            'question_count': quiz.exercises.count(),
            'created_at': quiz.created_at,
            'latest_attempt': latest_attempt,
            'avg_score': round(float(avg_score), 1) if avg_score is not None else None,
        })

    return render(request, 'ai_engine/quiz_list.html', {
        'user_notes': user_notes,
        'user_folders': user_folders,
        'standalone_notes': standalone_notes,
        'quizzes': quizzes_data,
        'total_quizzes_count': len(quizzes_data),
    })


@login_required
def periodic_summary_view(request):
    from learning.models import Attempt, QuizAttempt, Quiz
    from notes.models import Note, Folder
    from decimal import Decimal
    from django.db import models

    user_notes = Note.objects.filter(owner=request.user) if request.user.is_authenticated else []
    user_folders = Folder.objects.filter(owner=request.user) if request.user.is_authenticated else []
    standalone_notes = Note.objects.filter(owner=request.user, folder__isnull=True) if request.user.is_authenticated else []

    user_attempts = Attempt.objects.filter(quiz_attempt__user=request.user) if request.user.is_authenticated else Attempt.objects.none()
    
    total_attempts_count = user_attempts.count()
    completed_quizzes_count = QuizAttempt.objects.filter(user=request.user, completed_at__isnull=False).count() if request.user.is_authenticated else 0
    
    recent_avg_score = Attempt.objects.recent_average_score_for(request.user) if request.user.is_authenticated else Decimal("50.00")
    
    # Calculate average test score percentage across completed quiz attempts!
    completed_quiz_attempts = QuizAttempt.objects.filter(user=request.user, completed_at__isnull=False) if request.user.is_authenticated else []
    
    test_scores = []
    for qa in completed_quiz_attempts:
        s = Attempt.objects.filter(quiz_attempt=qa).aggregate(sum=models.Sum('score'))['sum']
        if s is not None:
            test_scores.append(float(s))

    if test_scores:
        avg_score_val = round(sum(test_scores) / len(test_scores), 1)
    else:
        avg_score_val = float(recent_avg_score)

    high_score_count = sum(1 for ts in test_scores if ts >= 80)
    medium_score_count = sum(1 for ts in test_scores if 50 <= ts < 80)
    low_score_count = sum(1 for ts in test_scores if ts < 50)

    mastery_percentage = min(100, max(0, int(avg_score_val)))

    # Fetch All Quizzes & Practice Suites (from notes or attempts)
    user_quizzes = Quiz.objects.filter(
        models.Q(note__owner=request.user) | models.Q(quiz_attempts__user=request.user)
    ).distinct().order_by('-created_at') if request.user.is_authenticated else []

    all_attempts = QuizAttempt.objects.filter(user=request.user).select_related('quiz').order_by('-started_at') if request.user.is_authenticated else []

    quizzes_data = []
    for quiz in user_quizzes:
        latest_attempt = all_attempts.filter(quiz=quiz).first()
        attempts = Attempt.objects.filter(quiz_attempt__quiz=quiz, quiz_attempt__user=request.user) if request.user.is_authenticated else []
        q_sum_score = attempts.aggregate(sum=models.Sum('score'))['sum'] if attempts.exists() else None

        exercises_list = []
        for ex in quiz.exercises.all():
            attempt_obj = Attempt.objects.filter(exercise=ex, quiz_attempt__user=request.user).first() if request.user.is_authenticated else None
            exercises_list.append({
                'order': ex.order,
                'question_type': ex.question_type,
                'question': ex.question,
                'options': ex.options,
                'correct_answer': ex.correct_answer,
                'user_answer': attempt_obj.user_answer if attempt_obj else None,
                'user_score': float(attempt_obj.score) if (attempt_obj and attempt_obj.score is not None) else None,
                'key_points': ex.key_points,
                'explanation': ex.explanation
            })

        display_note_title = quiz.note.title if quiz.note else 'General Study Note'
        if quiz.note and quiz.note.folder:
            display_note_title = f"Folder: {quiz.note.folder.name}"

        quiz_item = {
            'id': quiz.id,
            'title': quiz.title,
            'note_title': display_note_title,
            'question_count': quiz.exercises.count(),
            'created_at': quiz.created_at.strftime('%b %d, %Y') if quiz.created_at else '',
            'latest_attempt_at': latest_attempt.started_at.strftime('%b %d, %Y %H:%M') if (latest_attempt and latest_attempt.started_at) else None,
            'avg_score': round(float(q_sum_score), 1) if q_sum_score is not None else None,
            'exercises': exercises_list
        }
        quiz_item['quiz_json'] = json.dumps(quiz_item)
        quizzes_data.append(quiz_item)

    recent_quiz_attempts = QuizAttempt.objects.filter(user=request.user, completed_at__isnull=False).order_by('-completed_at')[:8] if request.user.is_authenticated else []
    recent_quiz_attempts = list(reversed(recent_quiz_attempts))
    chart_labels = [qa.completed_at.strftime('%m/%d %H:%M') for qa in recent_quiz_attempts]
    chart_scores = []
    for qa in recent_quiz_attempts:
        s = Attempt.objects.filter(quiz_attempt=qa).aggregate(sum=models.Sum('score'))['sum']
        chart_scores.append(round(float(s), 1) if s is not None else 0.0)

    if not chart_scores:
        chart_labels = ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5']
        chart_scores = [50, 65, 75, 80, 85]

    return render(request, 'ai_engine/periodic_summary.html', {
        'user_notes': user_notes,
        'user_folders': user_folders,
        'standalone_notes': standalone_notes,
        'total_attempts_count': total_attempts_count,
        'completed_quizzes_count': completed_quizzes_count,
        'avg_score': avg_score_val,
        'mastery_percentage': mastery_percentage,
        'high_score_count': high_score_count,
        'medium_score_count': medium_score_count,
        'low_score_count': low_score_count,
        'total_notes_count': len(user_notes),
        'total_folders_count': len(user_folders),
        'quizzes': quizzes_data,
        'total_quizzes_count': len(quizzes_data),
        'chart_labels': chart_labels,
        'chart_scores': chart_scores,
    })


@csrf_exempt
def record_attempt_api(request):
    """Persist completed quiz attempts, exercises, and scores into Database"""
    if request.method != 'POST':
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        score_percent = data.get('score_percent', 0)
        questions = data.get('questions', [])
        context_type = data.get('context_type', '')
        context_name = data.get('context_name', '')
        quiz_title = data.get('quiz_title', f"Practice Test ({timezone.now().strftime('%b %d, %H:%M')})")

        from learning.models import Quiz, Exercise, QuizAttempt, Attempt
        from notes.models import Note

        user = request.user if request.user.is_authenticated else None
        if not user:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        note_obj = None
        if context_type == 'folder' and context_name:
            from notes.models import Folder
            folder = Folder.objects.filter(owner=user, name=context_name).first()
            if folder and folder.notes.exists():
                note_obj = folder.notes.first()
        elif context_type == 'note' and context_name:
            note_obj = Note.objects.filter(owner=user, title=context_name).first()

        if not note_obj:
            note_obj = Note.objects.filter(owner=user).first()

        if not note_obj:
            note_obj = Note.objects.create(owner=user, title="AI Study Notes", content={"text": "Auto-created note for practice sessions"})

        quiz = Quiz.objects.create(
            note=note_obj,
            title=quiz_title
        )

        quiz_attempt = QuizAttempt.objects.create(
            user=user,
            quiz=quiz,
            completed_at=timezone.now()
        )

        for idx, q in enumerate(questions):
            q_type = q.get('question_type') or q.get('type') or 'multiple_choice'
            opts = q.get('options', {})
            corr_ans = q.get('correct_answer', '') or q.get('sample_answer', 'Reference Answer')
            k_points = q.get('key_points', [])

            if q_type == 'multiple_choice':
                ex_type = Exercise.QuestionType.MULTIPLE_CHOICE
                if not isinstance(opts, dict) or len(opts) < 2:
                    opts = {"A": "Option A", "B": "Option B"}
                if not corr_ans:
                    corr_ans = "A"
            elif q_type == 'short_answer':
                ex_type = Exercise.QuestionType.SHORT_ANSWER
                opts = {}
                if not corr_ans:
                    corr_ans = "Reference Answer"
            else:
                ex_type = Exercise.QuestionType.LONG_ANSWER
                opts = {}
                if not isinstance(k_points, list) or len(k_points) == 0:
                    k_points = ["Core concept 1", "Core concept 2"]

            ex = Exercise.objects.create(
                quiz=quiz,
                order=idx + 1,
                question_type=ex_type,
                question=q.get('question', f"Question {idx+1}"),
                options=opts,
                correct_answer=corr_ans,
                key_points=k_points,
                explanation=q.get('explanation', '')
            )

            Attempt.objects.create(
                quiz_attempt=quiz_attempt,
                exercise=ex,
                user_answer=str(q.get('user_answer', '(No answer provided)')),
                score=Decimal(str(q.get('score', score_percent)))
            )

        return JsonResponse({"status": "success", "quiz_id": quiz.id, "attempt_id": quiz_attempt.id})
    except Exception as e:
        print("Record attempt error:", e)
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def socratic_debate_api(request):
    """Coursera-Style Interactive Socratic Debate API"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            conversation_history = body.get('conversation_history') or body.get('history') or []
            student_input = body.get('student_input', '').strip()
            question_prompt = body.get('question_prompt', '')
            required_key_points = body.get('required_key_points', [])

            if not student_input:
                return JsonResponse({"error": "Please enter your response to continue the debate."}, status=400)

            debate_result = generate_tutor_chat_response(
                conversation_history=conversation_history,
                student_input=student_input,
                question_prompt=question_prompt,
                required_key_points=required_key_points
            )

            if debate_result:
                return JsonResponse(debate_result, status=200)
            return JsonResponse({"error": "Socratic AI busy"}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)


@require_GET
def tutor_history_api(request):
    """Return TutorSession history for the authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Bạn cần đăng nhập để xem lịch sử."},
            status=401,
        )

    sessions = (
        TutorSession.objects
        .filter(user=request.user)
        .select_related("exercise")[:50]
    )

    data = [
        {
            "session_id": session.id,
            "question": session.exercise.question,
            "is_ready_for_grading": session.is_ready_for_grading,
            "compiled_final_answer": session.compiled_final_answer,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        }
        for session in sessions
    ]

    return JsonResponse(
        {"status": "success", "data": data},
        status=200,
    )
# --- CHAT HISTORY PERSISTENCE APIS ---

@login_required
def get_chat_history_sessions_api(request):
    """Get all saved chat sessions for current user"""
    from .models import ChatSession
    sessions = ChatSession.objects.filter(user=request.user)
    data = []
    for s in sessions:
        data.append({
            'id': s.id,
            'title': s.title,
            'context_type': s.context_type,
            'context_name': s.context_name,
            'updated_at': s.updated_at.strftime('%b %d, %H:%M')
        })
    return JsonResponse({"status": "success", "sessions": data})


@login_required
def get_chat_session_detail_api(request, session_id):
    """Get detail and message history for a specific chat session"""
    from .models import ChatSession
    session = ChatSession.objects.filter(id=session_id, user=request.user).first()
    if not session:
        return JsonResponse({"error": "Session not found"}, status=404)
    
    messages = []
    for m in session.messages.all():
        messages.append({
            'role': m.role,
            'content': m.content,
            'created_at': m.created_at.strftime('%H:%M')
        })
    
    return JsonResponse({
        "status": "success",
        "session": {
            'id': session.id,
            'title': session.title,
            'context_type': session.context_type,
            'context_name': session.context_name,
            'messages': messages
        }
    })


@csrf_exempt
@login_required
def save_chat_message_api(request):
    """Save a chat message and associate/create a ChatSession"""
    if request.method == 'POST':
        try:
            from .models import ChatSession, ChatMessage
            body = json.loads(request.body)
            session_id = body.get('session_id')
            role = body.get('role', 'user')
            content = body.get('content', '').strip()
            context_type = body.get('context_type', 'free_talk')
            context_name = body.get('context_name', '')

            if not content:
                return JsonResponse({"error": "Content is required"}, status=400)

            session = None
            if session_id:
                session = ChatSession.objects.filter(id=session_id, user=request.user).first()

            if not session:
                # Generate smart title from content snippet
                title_clean = content.replace('\n', ' ').strip()
                if len(title_clean) > 25:
                    title_clean = title_clean[:25] + '...'
                
                session = ChatSession.objects.create(
                    user=request.user,
                    title=title_clean if title_clean else "New Chat",
                    context_type=context_type,
                    context_name=context_name
                )

            # Create message
            ChatMessage.objects.create(
                session=session,
                role=role,
                content=content
            )

            # Touch session updated_at
            session.save()

            return JsonResponse({
                "status": "success",
                "session_id": session.id,
                "session_title": session.title
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
@login_required
def delete_chat_session_api(request, session_id):
    """Delete a saved chat session"""
    if request.method == 'DELETE' or request.method == 'POST':
        from .models import ChatSession
        session = ChatSession.objects.filter(id=session_id, user=request.user).first()
        if session:
            session.delete()
            return JsonResponse({"status": "success"})
        return JsonResponse({"error": "Session not found"}, status=404)
    return JsonResponse({"error": "Invalid method"}, status=405)
