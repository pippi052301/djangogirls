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

]