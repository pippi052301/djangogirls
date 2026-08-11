from django.urls import path
from . import views

urlpatterns = [
    # API 1: http://localhost:8000/ai/quiz/
    path('quiz/', views.create_quiz_api, name='api_create_quiz'),
    
    # API 2: http://localhost:8000/ai/graph/
    path('graph/', views.create_graph_api, name='api_create_graph'),
    
    # API 3: http://localhost:8000/ai/adaptive/
    path('adaptive/', views.create_adaptive_practice_api, name='api_create_adaptive'),
]