from django.urls import path
from . import views


app_name = "notes"


urlpatterns = [
    #note
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

    path(
        "bulk-delete/",
        views.note_bulk_delete,
        name="note_bulk_delete"
    ),
    # folder
    path(
        "folders/",
        views.folder_list,
        name="folder_list"
    ),

    path(
        "folders/create/",
        views.folder_create,
        name="folder_create"
    ),

    path(
        "folders/<int:pk>/",
        views.folder_detail,
        name="folder_detail"
    ),
    path(
        "folders/<int:pk>/edit/",
        views.folder_edit,
        name="folder_edit"
    ),

    path(
        "folders/<int:pk>/delete/",
        views.folder_delete,
        name="folder_delete"
    ),

    path(
        "folders/bulk-delete/",
        views.folder_bulk_delete,
        name="folder_bulk_delete"
    ),
    
    
    # TAG
    path(
        "tags/",
        views.tag_list,
        name="tag_list"
    ),

    path(
        "tags/create/",
        views.tag_create,
        name="tag_create"
    ),

    path(
        "tags/<int:pk>/",
        views.tag_detail,
        name="tag_detail"
    ),

    path(
        "tags/<int:pk>/edit/",
        views.tag_edit,
        name="tag_update"
    ),

    path(
        "tags/<int:pk>/delete/",
        views.tag_delete,
        name="tag_delete"
    ),
    path(
    "<int:pk>/tags/",
    views.note_tags,
    name="note_tags"
    ),
]
