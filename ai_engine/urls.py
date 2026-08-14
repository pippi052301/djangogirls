from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='ai_home'),
    
    # API 1: http://localhost:8000/ai/quiz/
    path('quiz/', views.create_quiz_api, name='api_create_quiz'),
    
    # API 2: http://localhost:8000/ai/graph/
    path('graph/', views.create_graph_api, name='api_create_graph'),
    
    # API 3: http://localhost:8000/ai/adaptive/
    path('adaptive/', views.create_adaptive_practice_api, name='api_create_adaptive'),

    # API 4: http://localhost:8000/ai/chat/
    path('chat/', views.chat_api, name='api_chat'),

    # API 5: Record attempt
    path('record-attempt/', views.record_test_attempt_api, name='api_record_attempt'),

    # Quiz & Practice Views
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('quizzes/<int:quiz_id>/', views.quiz_session_view, name='quiz_session'),
    path('quizzes/attempt/<int:attempt_id>/result/', views.quiz_result_view, name='quiz_result'),
    path('summary/', views.periodic_summary_view, name='periodic_summary'),
]