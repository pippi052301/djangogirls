from django.urls import path
from . import views


app_name = "scheduler"


urlpatterns = [

    path(
        "create/",
        views.create_quiz_schedule,
        name="create"
    ),

    path(
        "",
        views.schedule_list,
        name="schedule_list"
    ),

    path(
        "delete/<int:pk>/",
        views.delete_quiz_schedule,
        name="delete"
    ),

    path(
        "update/<int:pk>/",
        views.update_quiz_schedule,
        name="update"
    ),

]