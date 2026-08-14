from django.db import models
from django.contrib.auth.models import User


class QuizSchedule(models.Model):

    FREQUENCY_CHOICES = [
<<<<<<< Updated upstream
        ("daily", "Hàng ngày"),
        ("weekly", "Hàng tuần"),
=======
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("specific", "Specific Date"),
>>>>>>> Stashed changes
    ]

    DIFFICULTY_CHOICES = [
        ("easy", "Dễ"),
        ("medium", "Trung bình"),
        ("hard", "Khó"),
        ("adaptive", "Tự động"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    topic = models.CharField(
        max_length=255
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default="daily"
    )

<<<<<<< Updated upstream
    time = models.TimeField()
=======
    weekly_days = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    specific_date = models.DateField(null=True, blank=True)

    time = models.TimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
>>>>>>> Stashed changes

    question_count = models.IntegerField(
        default=10
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="adaptive"
    )

    is_active = models.BooleanField(
        default=True
    )

    last_generated = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.topic}"