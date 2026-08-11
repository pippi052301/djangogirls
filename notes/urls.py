from django.urls import path
from . import views


app_name = "notes"


urlpatterns = [
    path(
        "",
        views.note_list,
        name="note_list"
    ),

    path(
        "create/",
        views.note_create,
        name="note_create"
    ),

    path(
        "<int:pk>/",
        views.note_detail,
        name="note_detail"
    ),

    path(
        "<int:pk>/edit/",
        views.note_edit,
        name="note_edit"
    ),

    path(
        "<int:pk>/delete/",
        views.note_delete,
        name="note_delete"
    ),
]