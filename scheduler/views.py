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
<<<<<<< Updated upstream

    schedules = QuizSchedule.objects.filter(
        user=request.user
    )
=======
    import datetime
    import calendar
    from notes.models import Folder, Note

    schedules = QuizSchedule.objects.filter(user=request.user).order_by("-created_at")
    user_folders = Folder.objects.filter(owner=request.user)
    user_notes = Note.objects.filter(owner=request.user)
    
    today = datetime.date.today()
    
    # Weekly view dates (Mon to Sun)
    start_of_week = today - datetime.timedelta(days=today.weekday())
    week_days = [start_of_week + datetime.timedelta(days=i) for i in range(7)]
    
    # Monthly view dates
    year = today.year
    month = today.month
    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    month_weeks = cal.monthdatescalendar(year, month)
    month_name = calendar.month_name[month]
>>>>>>> Stashed changes

    return render(
        request,
        "scheduler/schedule_list.html",
        {
<<<<<<< Updated upstream
            "schedules": schedules
=======
            "schedules": schedules,
            "user_folders": user_folders,
            "user_notes": user_notes,
            "today": today,
            "week_days": week_days,
            "month_weeks": month_weeks,
            "month_name": month_name,
            "year": year,
            "current_month_num": month,
>>>>>>> Stashed changes
        }
    )