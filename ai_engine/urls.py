from django.urls import path
from . import views


urlpatterns = [
    # AI Home / Assistant Page
    path('', views.ai_home, name='ai_home'),
    path('quizzes/', views.quiz_list_view, name='quiz_list'),
    path('summary/', views.periodic_summary_view, name='periodic_summary'),

    # API 1: Multiple Choice
    path('quiz/', views.create_quiz_api, name='api_create_quiz'),

    # API 2: Knowledge Graph
    path('graph/', views.create_graph_api, name='api_create_graph'),

    # API 3: Adaptive Practice
    path(
        'adaptive/',
        views.create_adaptive_practice_api,
        name='api_create_adaptive'
    ),

    # API 4: Essay Grading
    path(
        'grade_essay/',
        views.grade_essay_api,
        name='api_grade_essay'
    ),

    # API 5: Simple Grading
    path(
        'grade_simple/',
        views.grade_simple_api,
        name='api_grade_simple'
    ),

    # API 6: Normal AI Chat
    path(
        'api/chat/',
        views.student_chat_api,
        name='api_chat'
    ),
    path(
        'api/chat/student/',
        views.student_chat_api,
        name='student_chat_api'
    ),

    # API 7: Attempt Recording
    path(
        'api/attempt/',
        views.record_attempt_api,
        name='api_record_attempt'
    ),

    # API 8: Socratic Tutor
    path(
        'tutor/chat/',
        views.tutor_chat_api,
        name='tutor_chat_api'
    ),
    path(
        'tutor/grade/',
        views.submit_tutor_essay_for_grading_api,
        name='api_tutor_grade'
    ),
    path(
        'tutor/history/',
        views.tutor_history_api,
        name='api_tutor_history'
    ),

    # Separate Socratic Debate API
    path(
        'api/socratic-debate/',
        views.socratic_debate_api,
        name='api_socratic_debate'
    ),

    # API 9: Normal Chat History
    path(
        'api/history/sessions/',
        views.get_chat_history_sessions_api,
        name='api_history_sessions'
    ),
    path(
        'api/history/session/<int:session_id>/',
        views.get_chat_session_detail_api,
        name='api_history_session_detail'
    ),
    path(
        'api/history/session/save/',
        views.save_chat_message_api,
        name='api_history_save_message'
    ),
    path(
        'api/history/session/<int:session_id>/delete/',
        views.delete_chat_session_api,
        name='api_history_delete_session'
    ),
]