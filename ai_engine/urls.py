from django.urls import path
from . import views

urlpatterns = [
    # API 1: Tạo trắc nghiệm
    path('quiz/', views.create_quiz_api, name='api_create_quiz'),
    
    # API 2: Vẽ sơ đồ tư duy
    path('graph/', views.create_graph_api, name='api_create_graph'),
    
    # API 3: Đề thi thích ứng
    path('adaptive/', views.create_adaptive_practice_api, name='api_create_adaptive'),
    
    # API 4: Chấm điểm tự luận (Phức tạp + AI Rubric)
    path('grade_essay/', views.grade_essay_api, name='api_grade_essay'),
    
    # API 5: Chấm điểm trắc nghiệm/điền khuyết (Siêu tốc)
    path('grade_simple/', views.grade_simple_api, name='api_grade_simple'),
]