from django.db import models
from django.contrib.auth.models import User


class QuizSchedule(models.Model):

    FREQUENCY_CHOICES = [
        ("daily", "Hàng ngày"),
        ("weekly", "Hàng tuần"),
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

    time = models.TimeField()

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