from django.urls import path
from . import views

app_name = "learning"

urlpatterns = [
    path("", views.home, name="home"),
    path("notes/", views.note_list, name="note_list"),
    path("notes/new/", views.note_create, name="note_create"),
]