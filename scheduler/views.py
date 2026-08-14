from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import QuizScheduleForm
from .models import QuizSchedule


@login_required
def create_quiz_schedule(request):

    if request.method == "POST":

        form = QuizScheduleForm(request.POST)

        if form.is_valid():

            schedule = form.save(
                commit=False
            )

            schedule.user = request.user

            schedule.save()

            return redirect(
                "scheduler:schedule_list"
            )

    else:

        form = QuizScheduleForm()

    return render(
        request,
        "scheduler/create_schedule.html",
        {
            "form": form
        }
    )


@login_required
def schedule_list(request):

    schedules = QuizSchedule.objects.filter(
        user=request.user
    )

    return render(
        request,
        "scheduler/schedule_list.html",
        {
            "schedules": schedules
        }
    )