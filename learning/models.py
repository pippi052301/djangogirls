from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

class Quiz(models.Model):
    class GenerationType(models.TextChoices):
        STANDARD = "standard", "標準"
        ADAPTIVE = "adaptive", "適応型"

    note = models.ForeignKey(
        "notes.Note",
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    title = models.CharField(max_length=100)
    generation_type = models.CharField(
        max_length=20,
        choices=GenerationType.choices,
        default=GenerationType.ADAPTIVE,
    )
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
    order = models.PositiveSmallIntegerField(default=1)
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
        help_text="この問題の難易度（0〜100）",
    )
    recent_average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="この問題を生成するときに使った直近5問の平均点",
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
                    "選択問題には2つ以上の選択肢が必要です。"
                )

            if not self.correct_answer:
                raise ValidationError(
                    "選択問題には正解が必要です。"
                )

        elif self.question_type == self.QuestionType.SHORT_ANSWER:
            if not self.correct_answer:
                raise ValidationError(
                    "短答問題には模範解答が必要です。"
                )

        elif self.question_type == self.QuestionType.LONG_ANSWER:
            if (
                not isinstance(self.key_points, list)
                or not self.key_points
            ):
                raise ValidationError(
                    "記述問題には採点用の要点が必要です。"
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
    started_at = models.DateTimeField(
        auto_now_add=True,
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(score__isnull=True)
                    | models.Q(
                        score__gte=0,
                        score__lte=100,
                    )
                ),
                name="quiz_attempt_score_between_0_and_100",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.quiz.title} ({self.score})"


class AttemptQuerySet(models.QuerySet):
    def recent_average_score_for(self, user, limit=5):
        """
        ユーザーの直近の採点済み5問から平均点を返す。

        採点済みの問題がなければ50.00を返す。
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
        null=True,        
        blank=True,
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    user_answer = models.TextField()
    reasoning = models.TextField(
        help_text="ユーザーが入力した、問題を解くための論理ステップ",
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
    is_correct = models.BooleanField(
        blank=True,
        null=True,
    )
    used_hint_count = models.PositiveSmallIntegerField(
        default=0,
    )
    feedback = models.TextField(
        blank=True,
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

        if self.quiz_attempt_id and self.exercise_id:
            if self.quiz_attempt.quiz_id != self.exercise.quiz_id:
                raise ValidationError(
                    "受験中のテストに含まれない問題には回答できません。"
                )

            if self.used_hint_count > len(self.exercise.hints):
                raise ValidationError(
                    "使用したヒント数が、問題のヒント数を超えています。"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quiz_attempt.user} - {self.exercise}"

class TutorSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_sessions",
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="tutor_sessions",
    )
    quiz_attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="tutor_sessions",
        null=True,
        blank=True,
    )
    is_ready_for_grading = models.BooleanField(
        default=False,
    )
    compiled_final_answer = models.TextField(
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def clean(self):
        super().clean()

        if (
            self.exercise_id
            and self.exercise.question_type
            != Exercise.QuestionType.LONG_ANSWER
        ):
            raise ValidationError(
                "Tutorセッションは記述問題にのみ作成できます。"
            )

        if self.quiz_attempt_id:
            if self.quiz_attempt.user_id != self.user_id:
                raise ValidationError(
                    "受験者とTutorセッションのユーザーが一致しません。"
                )

            if self.quiz_attempt.quiz_id != self.exercise.quiz_id:
                raise ValidationError(
                    "受験中のクイズに含まれない問題です。"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.exercise}"


class TutorMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "ユーザー"
        MODEL = "model", "AI Tutor"

    session = models.ForeignKey(
        TutorSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
    )
    content = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.session_id} - {self.role}"