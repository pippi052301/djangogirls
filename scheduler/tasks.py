from celery import shared_task

from django.utils import timezone

from .models import QuizSchedule


@shared_task
def check_quiz_schedules():

    now = timezone.localtime()

    current_time = now.time()

    schedules = QuizSchedule.objects.filter(
        is_active=True
    )

    for schedule in schedules:

        schedule_time = schedule.time

        if (
            schedule_time.hour == current_time.hour
            and schedule_time.minute == current_time.minute
        ):

            generate_scheduled_quiz.delay(
                schedule.id
            )