from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import QuizScheduleForm
from .models import QuizSchedule


def _clean_schedule_post_data(request):
    post_data = request.POST.copy()
    
    if not post_data.get('topic'):
        post_data['topic'] = "Untitled Study Plan"

    weekly_days_list = post_data.getlist('weekly_days_list')
    if weekly_days_list:
        post_data['weekly_days'] = ",".join(weekly_days_list)
    elif post_data.get('frequency') == 'weekly' and not post_data.get('weekly_days'):
        post_data['weekly_days'] = "Mon,Tue,Wed,Thu,Fri"

    if not post_data.get('specific_date'):
        post_data['specific_date'] = None
    if not post_data.get('start_time'):
        post_data['start_time'] = None
    if not post_data.get('end_time'):
        post_data['end_time'] = None

    if not post_data.get('priority'):
        post_data['priority'] = 3

    return post_data


@login_required
def create_quiz_schedule(request):
    if request.method == "POST":
        post_data = _clean_schedule_post_data(request)
        form = QuizScheduleForm(post_data)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.save()
            return redirect("scheduler:schedule_list")
        else:
            print("Form errors:", form.errors)
            return redirect("scheduler:schedule_list")

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

    return render(
        request,
        "scheduler/schedule_list.html",
        {
            "schedules": schedules,
            "user_folders": user_folders,
            "user_notes": user_notes,
            "today": today,
            "week_days": week_days,
            "month_weeks": month_weeks,
            "month_name": month_name,
            "year": year,
            "current_month_num": month,
        }
    )


@login_required
def delete_quiz_schedule(request, pk):
    from django.shortcuts import get_object_or_404
    schedule = get_object_or_404(QuizSchedule, pk=pk, user=request.user)
    schedule.delete()
    return redirect("scheduler:schedule_list")


@login_required
def update_quiz_schedule(request, pk):
    from django.shortcuts import get_object_or_404
    schedule = get_object_or_404(QuizSchedule, pk=pk, user=request.user)
    if request.method == "POST":
        post_data = _clean_schedule_post_data(request)
        form = QuizScheduleForm(post_data, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect("scheduler:schedule_list")
        else:
            print("Update form errors:", form.errors)
    return redirect("scheduler:schedule_list")