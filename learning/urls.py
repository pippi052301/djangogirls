from django.urls import path
from . import views

app_name = "learning"

urlpatterns = [
    path("", views.home, name="home"),
    path("notes/", views.note_list, name="note_list"),
    path("notes/new/", views.note_create, name="note_create"),
    path("register/", views.register, name="register"),
    path("password-reset/", views.custom_password_reset, name="custom_password_reset"),
]