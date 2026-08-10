from django.urls import path

from . import views

app_name = "learning"

urlpatterns = [
    path("", views.home, name="home"),
]
urlpatterns = [
    path('notes/new/', views.note_create, name='note_create'),
]