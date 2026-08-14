from django.db import models
from django.contrib.auth.models import User


class QuizSchedule(models.Model):

    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    ]

    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
        ("adaptive", "Adaptive"),
    ]

    PRIORITY_CHOICES = [
        (1, "P1 - Highest Priority"),
        (2, "P2 - High Priority"),
        (3, "P3 - Medium Priority"),
        (4, "P4 - Low Priority"),
        (5, "P5 - Lowest Priority"),
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

    weekly_days = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    time = models.TimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    question_count = models.IntegerField(
        default=10,
        null=True,
        blank=True
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="adaptive"
    )

    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1
    )

    is_active = models.BooleanField(
        default=True
    )

    last_generated = models.DateTimeField(
        null=True,
        blank=True
    )

    note = models.ForeignKey(
        'notes.Note',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='schedules'
    )

    folder = models.ForeignKey(
        'notes.Folder',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='schedules'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    @property
    def ai_study_url(self):
        import urllib.parse
        if self.note:
            encoded_title = urllib.parse.quote(self.note.title)
            return f"/ai/?context_type=note&context_name={encoded_title}&note_id={self.note.id}"
        elif self.folder:
            encoded_name = urllib.parse.quote(self.folder.name)
            return f"/ai/?context_type=folder&context_name={encoded_name}&folder_id={self.folder.id}"
        return "/ai/"

    @property
    def card_style(self):
        styles = {
            1: "bg-red-50/90 dark:bg-red-950/60 border-red-300 dark:border-red-800/80 text-red-900 dark:text-red-100 hover:bg-red-100 dark:hover:bg-red-900/60",
            2: "bg-orange-50/90 dark:bg-orange-950/60 border-orange-300 dark:border-orange-800/80 text-orange-900 dark:text-orange-100 hover:bg-orange-100 dark:hover:bg-orange-900/60",
            3: "bg-amber-50/90 dark:bg-amber-950/60 border-amber-300 dark:border-amber-800/80 text-amber-900 dark:text-amber-100 hover:bg-amber-100 dark:hover:bg-amber-900/60",
            4: "bg-blue-50/90 dark:bg-blue-950/60 border-blue-300 dark:border-blue-800/80 text-blue-900 dark:text-blue-100 hover:bg-blue-100 dark:hover:bg-blue-900/60",
            5: "bg-slate-100/90 dark:bg-slate-800/80 border-slate-300 dark:border-slate-700/80 text-slate-900 dark:text-slate-100 hover:bg-slate-200 dark:hover:bg-slate-700",
        }
        return styles.get(self.priority, styles[4])

    @property
    def priority_color(self):
        colors = {
            1: "bg-red-100 text-red-700 border-red-200 dark:bg-red-950/60 dark:text-red-300 dark:border-red-800",
            2: "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-950/60 dark:text-orange-300 dark:border-orange-800",
            3: "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800",
            4: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800",
            5: "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700",
        }
        return colors.get(self.priority, colors[1])

    def __str__(self):
        return f"{self.user.username} - {self.topic} (P{self.priority})"