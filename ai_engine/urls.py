from django.urls import path
from . import views

urlpatterns = [
    # API 1: Multiplechoice
    path('quiz/', views.create_quiz_api, name='api_create_quiz'),
    
    # API 2: Map
    path('graph/', views.create_graph_api, name='api_create_graph'),
    
    # API 3: Adaptive practice
    path('adaptive/', views.create_adaptive_practice_api, name='api_create_adaptive'),
    
    # API 4: Scoring  (Complicate + AI Rubric)
    path('grade_essay/', views.grade_essay_api, name='api_grade_essay'),
    
    # API 5: Scoring (Fast)
    path('grade_simple/', views.grade_simple_api, name='api_grade_simple'),

    # API 6: Chatbot
    path('api/chat/', views.student_chat_api, name='student_chat_api'),
    
    #API 7: Tutor chat
    path('tutor/chat/', views.tutor_chat_api, name='tutor_chat_api'),
    path('tutor/grade/', views.submit_tutor_essay_for_grading_api, name='api_tutor_grade'),
    path('tutor/history/', views.tutor_history_api, name='api_tutor_history'),
]
