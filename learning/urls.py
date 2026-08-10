from django.urls import path
from . import views


app_name = "learning"


urlpatterns = [
    path("", views.home, name="home"),
    path("notes/create/", views.create_note, name="create_note"),
    path("notes/", views.note_list, name="note_list"),
]