from django.urls import path
from . import views


app_name = "learning"


urlpatterns = [
    path("learning/notes_form", views.create_note, name="create_note"),
    path("", views.note_list, name="note_list"),
]