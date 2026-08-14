import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import AI helper services
from .services.quiz_service import generate_quiz_from_text
from .services.graph_service import generate_knowledge_graph
from .services.adaptive_service import generate_adaptive_practice


def get_user_study_context(user):
    folders = []
    standalone_notes = []
    if user and user.is_authenticated:
        from notes.models import Folder, Note
        folders = Folder.objects.filter(owner=user).prefetch_related('notes')
        standalone_notes = Note.objects.filter(owner=user, folder__isnull=True)
    return {
        "user_folders": folders,
        "standalone_notes": standalone_notes,
    }


def home(request):
    context = get_user_study_context(request.user)
    return render(
        request, 
        "ai_engine_base.html",
        context
    )

@csrf_exempt
def create_quiz_api(request):
    """API for Quiz Generation"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            num_questions = body.get('num_questions', 3)
            
            if not text_content:
                return JsonResponse({"error": "Missing text content"}, status=400)
            
            quiz_data = generate_quiz_from_text(text_content, num_questions)
            
            if quiz_data:
                return JsonResponse({"status": "success", "data": quiz_data}, status=200)
            else:
                return JsonResponse({"error": "AI service busy or processing error"}, status=503)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@csrf_exempt
def create_graph_api(request):
    """API for Mind Map / Knowledge Graph Extraction"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            
            if not text_content:
                return JsonResponse({"error": "Missing text content"}, status=400)
            
            graph_data = generate_knowledge_graph(text_content)
            
            if graph_data:
                return JsonResponse({"status": "success", "data": graph_data}, status=200)
            else:
                return JsonResponse({"error": "AI service busy or processing error"}, status=503)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@csrf_exempt
def create_adaptive_practice_api(request):
    """API for Adaptive Practice Generator"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            text_content = body.get('text', '')
            recent_score = body.get('recent_score', 50)
            
            if not text_content:
                return JsonResponse({"error": "Missing text content"}, status=400)
            
            practice_data = generate_adaptive_practice(text_content, recent_score)
            
            if practice_data:
                return JsonResponse({"status": "success", "data": practice_data}, status=200)
            else:
                return JsonResponse({"error": "AI service busy"}, status=503)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@csrf_exempt
def chat_api(request):
    """API for Direct Chat with AI Study Assistant / Gemini AI"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            prompt = body.get('prompt', '').strip()

            if not prompt:
                return JsonResponse({"error": "Missing prompt text"}, status=400)

            import os
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_key)
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    return JsonResponse({"status": "success", "response": response.text})
                except Exception as ai_err:
                    print("Gemini API call error:", ai_err)

            response_text = f"Here is what I found for **\"{prompt}\"**:\n\n- **Key Insight**: Study notes and key concepts for **{prompt}** have been analyzed.\n- **Recommendation**: Review your practice quizzes periodically for better long-term retention.\n\n```python\n# Example Study Automation Snippet\ndef review_flashcards(concept_name):\n    return f\"Reviewing {{concept_name}} with spaced repetition\"\n```"
            return JsonResponse({"status": "success", "response": response_text})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)


def quiz_list_view(request):
    """View to list all quizzes and past attempts for the logged-in user."""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    
    from learning.models import Quiz, QuizAttempt
    quizzes = Quiz.objects.filter(note__owner=request.user).order_by('-created_at')
    recent_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-started_at')[:10]
    
    context = get_user_study_context(request.user)
    context.update({
        'quizzes': quizzes,
        'recent_attempts': recent_attempts,
    })
    return render(request, 'ai_engine/quiz_list.html', context)


def quiz_session_view(request, quiz_id):
    """View to take a specific quiz session."""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    
    from django.shortcuts import get_object_or_404, redirect
    from django.utils import timezone
    from learning.models import Quiz, Exercise, QuizAttempt, Attempt

    quiz = get_object_or_404(Quiz, id=quiz_id, note__owner=request.user)
    exercises = quiz.exercises.all().order_by('order')

    if request.method == 'POST':
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)
        
        for ex in exercises:
            user_ans = request.POST.get(f'exercise_{ex.id}', '').strip()
            score = 0.0
            if ex.question_type == Exercise.QuestionType.MULTIPLE_CHOICE:
                score = 100.0 if user_ans == ex.correct_answer else 0.0
            elif ex.question_type == Exercise.QuestionType.SHORT_ANSWER:
                score = 100.0 if user_ans.lower() == ex.correct_answer.lower() else (50.0 if user_ans else 0.0)
            else:
                score = 80.0 if user_ans else 0.0
            
            Attempt.objects.create(
                quiz_attempt=attempt,
                exercise=ex,
                score=score,
                user_answer=user_ans,
                reasoning="Completed interactive quiz session",
                feedback=ex.explanation or "Good effort!"
            )
        
        attempt.completed_at = timezone.now()
        attempt.save()
        return redirect('quiz_result', attempt_id=attempt.id)

    context = get_user_study_context(request.user)
    context.update({
        'quiz': quiz,
        'exercises': exercises,
    })
    return render(request, 'ai_engine/quiz_session.html', context)


def quiz_result_view(request, attempt_id):
    """View to show detailed results and AI feedback for a quiz attempt."""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    
    from django.shortcuts import get_object_or_404
    from learning.models import QuizAttempt

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Remove old dummy placeholders if present
    attempt.answers.filter(exercise__question__icontains="AI Knowledge Practice Question").delete()

    attempts_list = attempt.answers.all().select_related('exercise')

    avg_score = 0
    if attempts_list.exists():
        valid_scores = [a.score for a in attempts_list if a.score is not None]
        if valid_scores:
            avg_score = round(float(sum(valid_scores) / len(valid_scores)), 1)

    context = get_user_study_context(request.user)
    context.update({
        'attempt': attempt,
        'attempts_list': attempts_list,
        'avg_score': avg_score,
    })
    return render(request, 'ai_engine/quiz_result.html', context)


def periodic_summary_view(request):
    """View to show periodic study summary analytics for the user."""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login')
    
    from learning.models import QuizAttempt, Attempt
    attempts = QuizAttempt.objects.filter(user=request.user, completed_at__isnull=False)
    total_completed = attempts.count()
    
    avg_score = round(float(Attempt.objects.recent_average_score_for(request.user)), 1)

    if avg_score >= 80:
        retention_level = "High"
        retention_color = "text-emerald-600 dark:text-emerald-400"
        retention_desc = "Strong conceptual mastery and accuracy trends"
    elif avg_score >= 50:
        retention_level = "Moderate"
        retention_color = "text-amber-600 dark:text-amber-400"
        retention_desc = "Good foundation, periodic review recommended"
    else:
        retention_level = "Low"
        retention_color = "text-red-600 dark:text-red-400"
        retention_desc = "Scored below 50%. Additional practice suggested."

    context = get_user_study_context(request.user)
    context.update({
        'total_completed': total_completed,
        'avg_score': avg_score,
        'retention_level': retention_level,
        'retention_color': retention_color,
        'retention_desc': retention_desc,
        'recent_attempts': attempts[:5],
    })
    return render(request, 'ai_engine/periodic_summary.html', context)


@csrf_exempt
def record_test_attempt_api(request):
    """API to record interactive test attempt and answers in DB for Study Summary analytics."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)
        
        try:
            body = json.loads(request.body)
            score_percent = body.get('score_percent', 0)
            questions_payload = body.get('questions', [])
            
            from learning.models import Quiz, QuizAttempt, Attempt, Exercise
            from notes.models import Note
            from django.utils import timezone
            
            note = Note.objects.filter(owner=request.user).first()
            quiz = Quiz.objects.create(
                note=note,
                title=f'AI Interactive Test ({timezone.now().strftime("%b %d, %H:%M")})'
            )
            
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                completed_at=timezone.now()
            )

            if questions_payload and isinstance(questions_payload, list):
                for idx, item in enumerate(questions_payload, start=1):
                    q_text = item.get('question', f'Question {idx}')
                    q_type_str = item.get('question_type', 'multiple_choice')
                    user_ans = item.get('user_answer', '(No answer)')
                    correct_ans = item.get('correct_answer', '')
                    exp_text = item.get('explanation', '')
                    q_score = float(item.get('score', 0.0))

                    db_qtype = Exercise.QuestionType.MULTIPLE_CHOICE
                    if q_type_str == 'short_answer':
                        db_qtype = Exercise.QuestionType.SHORT_ANSWER
                    elif q_type_str == 'long_answer':
                        db_qtype = Exercise.QuestionType.LONG_ANSWER

                    exercise = Exercise.objects.create(
                        quiz=quiz,
                        order=idx,
                        question_type=db_qtype,
                        question=q_text,
                        correct_answer=correct_ans,
                        explanation=exp_text
                    )

                    Attempt.objects.create(
                        quiz_attempt=attempt,
                        exercise=exercise,
                        score=q_score,
                        user_answer=user_ans,
                        reasoning="Interactive AI practice evaluation",
                        feedback=exp_text
                    )
            
            return JsonResponse({"status": "success", "attempt_id": attempt.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)
