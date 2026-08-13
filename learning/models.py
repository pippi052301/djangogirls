from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone


class Quiz(models.Model):
    note = models.ForeignKey(
        "notes.Note",
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.title


class Exercise(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "選択問題"
        SHORT_ANSWER = "short_answer", "短答問題"
        LONG_ANSWER = "long_answer", "記述問題"

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="exercises",
    )
    order = models.PositiveSmallIntegerField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    difficulty = models.PositiveSmallIntegerField(
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="difficulty of this problem (0〜100)",
    )
    recent_average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="recent average score for this problem (0〜100)",
    )
    question = models.TextField()
    options = models.JSONField(
        default=dict,
        blank=True,
    )
    correct_answer = models.TextField(
        blank=True,
    )
    key_points = models.JSONField(
        default=list,
        blank=True,
    )
    hints = models.JSONField(
        default=list,
        blank=True,
    )
    explanation = models.TextField(
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "order"],
                name="unique_exercise_order_per_quiz",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    difficulty__gte=0,
                    difficulty__lte=100,
                ),
                name="exercise_difficulty_between_0_and_100",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    recent_average_score__gte=0,
                    recent_average_score__lte=100,
                ),
                name="exercise_recent_average_between_0_and_100",
            ),
        ]

    def clean(self):
        super().clean()

        if self.question_type == self.QuestionType.MULTIPLE_CHOICE:
            if (
                not isinstance(self.options, dict)
                or len(self.options) < 2
            ):
                raise ValidationError(
                    "Multiple choice questions require at least 2 options."
                )

            if not self.correct_answer:
                raise ValidationError(
                    "Multiple choice questions require a correct answer."
                )

        elif self.question_type == self.QuestionType.SHORT_ANSWER:
            if not self.correct_answer:
                raise ValidationError(
                    "Short answer questions require a correct answer."
                )

        elif self.question_type == self.QuestionType.LONG_ANSWER:
            if (
                not isinstance(self.key_points, list)
                or not self.key_points
            ):
                raise ValidationError(
                    "Long answer questions require key points for grading."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quiz.title} - 問題{self.order}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} - {self.quiz.title}"


class AttemptQuerySet(models.QuerySet):
    def recent_average_score_for(self, user, limit=5):
        """
        Returns the average score for the user's most recent 5 answered questions.

        Returns 50.00 if no answered questions are found.
        """

        average = (
            self.filter(
                quiz_attempt__user=user,
                score__isnull=False,
            )
            .order_by("-created_at")[:limit]
            .aggregate(
                value=models.Avg("score"),
            )["value"]
        )

        if average is None:
            return Decimal("50.00")

        return average


class Attempt(models.Model):
    quiz_attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    user_answer = models.TextField()
    reasoning = models.TextField(
        help_text="Logical steps taken by the user to solve the problem",
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    used_hint_count = models.PositiveSmallIntegerField(
        default=0,
    )
    feedback = models.TextField(
        blank=True,
    )
    rubric_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI-generated scores, justifications, and key points for each criterion",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    objects = AttemptQuerySet.as_manager()

    class Meta:
        ordering = ["exercise__order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["quiz_attempt", "exercise"],
                name="unique_answer_per_quiz_attempt",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(score__isnull=True)
                    | models.Q(
                        score__gte=0,
                        score__lte=100,
                    )
                ),
                name="attempt_score_between_0_and_100",
            ),
        ]

    def clean(self):
        super().clean()

        if not isinstance(self.rubric_details, dict):
            raise ValidationError(
                {"rubric_details": "Grading details must be saved as a JSON object."}
            )

        if self.quiz_attempt_id and self.exercise_id:
            if self.quiz_attempt.quiz_id != self.exercise.quiz_id:
                raise ValidationError(
                    "Answers can only be submitted for questions within the current quiz."
                )

            if self.used_hint_count > len(self.exercise.hints):
                raise ValidationError(
                    "The number of hints used exceeds the available hints for this question."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quiz_attempt.user} - {self.exercise}"

class MapNode(models.Model):
    note = models.ForeignKey(
        "notes.Note",
        on_delete=models.CASCADE,
        related_name="map_nodes",
    )
    key = models.CharField(
        max_length=100,
        help_text="Identifier within the note corresponding to the AI's nodes[].id",
    )
    label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["note", "key"],
                name="unique_map_node_key_per_note",
            )
        ]

    def __str__(self):
        return self.label


class MapEdge(models.Model):
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "target", "label"],
                name="unique_map_edge",
            )
        ]

    def clean(self):
        super().clean()

        if self.source_id and self.target_id:
            if self.source_id == self.target_id:
                raise ValidationError(
                    "A node cannot be connected to itself."
                )

            if self.source.note_id != self.target.note_id:
                raise ValidationError(
                    "Nodes from different notes cannot be connected."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} -> {self.target}"
    