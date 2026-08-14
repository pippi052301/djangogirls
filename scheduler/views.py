from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import QuizScheduleForm
from .models import QuizSchedule


@login_required
def create_quiz_schedule(request):
    from notes.models import Folder, Note

    user_folders = Folder.objects.filter(owner=request.user)
    user_notes = Note.objects.filter(owner=request.user)

    if request.method == "POST":
        form = QuizScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            
            target_type_id = request.POST.get("target_resource", "")
            if target_type_id.startswith("folder_"):
                folder_id = target_type_id.replace("folder_", "")
                schedule.folder = user_folders.filter(id=folder_id).first()
            elif target_type_id.startswith("note_"):
                note_id = target_type_id.replace("note_", "")
                schedule.note = user_notes.filter(id=note_id).first()

            days_list = request.POST.getlist("weekly_days_list")
            if days_list:
                schedule.weekly_days = ",".join(days_list)

            if schedule.start_time:
                schedule.time = schedule.start_time

            schedule.save()
            return redirect("scheduler:schedule_list")
    else:
        form = QuizScheduleForm()

    return render(
        request,
        "scheduler/create_schedule.html",
        {
            "form": form,
            "user_folders": user_folders,
            "user_notes": user_notes,
        }
    )


@login_required
def edit_quiz_schedule(request, pk):
    from notes.models import Folder, Note

    schedule = get_object_or_404(QuizSchedule, pk=pk, user=request.user)
    user_folders = Folder.objects.filter(owner=request.user)
    user_notes = Note.objects.filter(owner=request.user)

    if request.method == "POST":
        form = QuizScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            schedule = form.save(commit=False)
            
            target_type_id = request.POST.get("target_resource", "")
            if target_type_id.startswith("folder_"):
                folder_id = target_type_id.replace("folder_", "")
                schedule.folder = user_folders.filter(id=folder_id).first()
                schedule.note = None
            elif target_type_id.startswith("note_"):
                note_id = target_type_id.replace("note_", "")
                schedule.note = user_notes.filter(id=note_id).first()
                schedule.folder = None
            else:
                schedule.folder = None
                schedule.note = None

            days_list = request.POST.getlist("weekly_days_list")
            if days_list:
                schedule.weekly_days = ",".join(days_list)

            if schedule.start_time:
                schedule.time = schedule.start_time

            schedule.save()
            return redirect("scheduler:schedule_list")
    else:
        form = QuizScheduleForm(instance=schedule)

    weekly_days_list = schedule.weekly_days.split(",") if schedule.weekly_days else []

    return render(
        request,
        "scheduler/create_schedule.html",
        {
            "form": form,
            "schedule": schedule,
            "is_edit": True,
            "user_folders": user_folders,
            "user_notes": user_notes,
            "weekly_days_list": weekly_days_list,
        }
    )


@login_required
def delete_quiz_schedule(request, pk):
    schedule = get_object_or_404(QuizSchedule, pk=pk, user=request.user)
    schedule.delete()
    return redirect("scheduler:schedule_list")


@login_required
def toggle_quiz_schedule(request, pk):
    schedule = get_object_or_404(QuizSchedule, pk=pk, user=request.user)
    schedule.is_active = not schedule.is_active
    schedule.save()
    return redirect("scheduler:schedule_list")


@login_required
def schedule_list(request):
    import datetime
    import calendar

    schedules = QuizSchedule.objects.filter(user=request.user).order_by("-created_at")
    
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
            "today": today,
            "week_days": week_days,
            "month_weeks": month_weeks,
            "month_name": month_name,
            "year": year,
            "current_month_num": month,
        }
    )