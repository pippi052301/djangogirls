from django.db import models
from django.contrib.auth.models import User


class QuizSchedule(models.Model):

    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("specific", "Specific Date"),
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

    weekly_days = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    specific_date = models.DateField(null=True, blank=True)

    time = models.TimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    priority = models.IntegerField(default=3)
    target_resource = models.CharField(max_length=100, blank=True, default="")

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

    @property
    def folder(self):
        if self.target_resource and self.target_resource.startswith("folder_"):
            try:
                from notes.models import Folder
                f_id = int(self.target_resource.replace("folder_", ""))
                return Folder.objects.filter(id=f_id, owner=self.user).first()
            except Exception:
                return None
        return None

    @property
    def note(self):
        if self.target_resource and self.target_resource.startswith("note_"):
            try:
                from notes.models import Note
                n_id = int(self.target_resource.replace("note_", ""))
                return Note.objects.filter(id=n_id, owner=self.user).first()
            except Exception:
                return None
        return None

    @property
    def ai_study_url(self):
        from django.urls import reverse
        from urllib.parse import quote
        if self.folder:
            return f"{reverse('ai_home')}?context_type=folder&context_name={quote(self.folder.name)}"
        elif self.note:
            return f"{reverse('ai_home')}?context_type=note&context_name={quote(self.note.title)}"
        elif self.topic:
            try:
                from notes.models import Folder, Note
                f_match = Folder.objects.filter(owner=self.user, name__iexact=self.topic).first()
                if f_match:
                    return f"{reverse('ai_home')}?context_type=folder&context_name={quote(f_match.name)}"
                n_match = Note.objects.filter(owner=self.user, title__iexact=self.topic).first()
                if n_match:
                    return f"{reverse('ai_home')}?context_type=note&context_name={quote(n_match.title)}"
            except Exception:
                pass
            return f"{reverse('ai_home')}?context_type=folder&context_name={quote(self.topic)}"
        return reverse('ai_home')

    @property
    def priority_color(self):
        colors = {
            1: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20",
            2: "bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20",
            3: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
            4: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
            5: "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20",
        }
        return colors.get(self.priority, colors[3])

    @property
    def card_style(self):
        styles = {
            1: "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900/50 text-red-900 dark:text-red-200 hover:border-red-500",
            2: "bg-orange-50 dark:bg-orange-950/30 border-orange-200 dark:border-orange-900/50 text-orange-900 dark:text-orange-200 hover:border-orange-500",
            3: "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/50 text-amber-900 dark:text-amber-200 hover:border-amber-500",
            4: "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/50 text-blue-900 dark:text-blue-200 hover:border-blue-500",
            5: "bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 hover:border-slate-400",
        }
        return styles.get(self.priority, styles[3])