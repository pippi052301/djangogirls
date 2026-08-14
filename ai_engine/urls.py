from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='ai_home'),
<<<<<<< Updated upstream
    
    # API 1: http://localhost:8000/ai/quiz/
=======

    # API 1: Multiplechoice
>>>>>>> Stashed changes
    path('quiz/', views.create_quiz_api, name='api_create_quiz'),
    
    # API 2: http://localhost:8000/ai/graph/
    path('graph/', views.create_graph_api, name='api_create_graph'),
    
    # API 3: http://localhost:8000/ai/adaptive/
    path('adaptive/', views.create_adaptive_practice_api, name='api_create_adaptive'),
<<<<<<< Updated upstream

    # API 4: http://localhost:8000/ai/chat/
    path('chat/', views.chat_api, name='api_chat'),

    # API 5: Record attempt
    path('record-attempt/', views.record_test_attempt_api, name='api_record_attempt'),

    # Quiz & Practice Views
=======
    
    # API 4: Scoring (Complicate + AI Rubric)
    path('grade_essay/', views.grade_essay_api, name='api_grade_essay'),
    
    # API 5: Scoring (Fast)
    path('grade_simple/', views.grade_simple_api, name='api_grade_simple'),

    # API 6: Chatbot
    path('chat/', views.student_chat_api, name='api_chat'),
    path('api/chat/', views.student_chat_api, name='student_chat_api'),

    # API 7: Record attempt
    path('record-attempt/', views.record_test_attempt_api, name='api_record_attempt'),
    path('clean-pdf-text/', views.clean_pdf_text_api, name='api_clean_pdf_text'),

    # Quiz & Summary views
>>>>>>> Stashed changes
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('quizzes/<int:quiz_id>/', views.quiz_session_view, name='quiz_session'),
    path('quizzes/attempt/<int:attempt_id>/result/', views.quiz_result_view, name='quiz_result'),
    path('summary/', views.periodic_summary_view, name='periodic_summary'),
]