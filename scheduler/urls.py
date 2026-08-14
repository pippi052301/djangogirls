from django.urls import path
from . import views

app_name = "scheduler"

urlpatterns = [
    path("create/", views.create_quiz_schedule, name="create"),
    path("edit/<int:pk>/", views.edit_quiz_schedule, name="edit"),
    path("delete/<int:pk>/", views.delete_quiz_schedule, name="delete"),
    path("toggle/<int:pk>/", views.toggle_quiz_schedule, name="toggle"),
    path("", views.schedule_list, name="schedule_list"),
]