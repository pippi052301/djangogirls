from django.urls import path
from . import views


app_name = "learning"


urlpatterns = [
    path("", views.home, name="home"),
    path("learning/notes_form", views.create_note, name="create_note"),
    path("notes/", views.note_list, name="note_list"),
]