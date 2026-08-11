from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.


class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.title}"


class Exercise(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "Easy"
        MEDIUM = "Medium"
        HARD = "Hard"
        
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="exercises")
    title = models.CharField(max_length=100)
    content = models.TextField()
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    question = models.TextField()
    correct_answer = models.TextField()
    hints = models.JSONField(default=list)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.difficulty} - {self.question[:100]}"


class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="attempts")
    user_answer = models.TextField()
    reasoning = models.TextField()
    is_correct = models.BooleanField(blank=True, null=True)
    used_hint_count = models.PositiveSmallIntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt by {self.user.username} on {self.exercise.title} - Correct: {self.is_correct}"


class MapNode(models.Model):
    """A topic displayed as a node on a note's learning map."""

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="map_nodes",
    )
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label


class MapEdge(models.Model):
    """A directed connection between two nodes on the same note map."""

    source = models.ForeignKey(
        MapNode,
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
    )
    target = models.ForeignKey(
        MapNode,
        on_delete=models.CASCADE,
        related_name="incoming_edges",
    )
    label = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if self.source_id and self.target_id:
            if self.source.note_id != self.target.note_id:
                raise ValidationError(
                    "異なるノートに属するノード同士は接続できません。"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} -> {self.target}"