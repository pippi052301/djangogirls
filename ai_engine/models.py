import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from pgvector.django import VectorField

EMBEDDING_DIMENSIONS = 3072

class SemanticAICache(models.Model):
    "Cache a structured AI response for semantically similar input text."

    feature_type = models.CharField(max_length=50, db_index=True)
    original_text = models.TextField()
    text_embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)
    ai_response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "semantic AI cache"
        verbose_name_plural = "semantic AI caches"

    def __str__(self):
        return f"{self.feature_type}: {self.original_text[:50]}"


class ReferenceSample(models.Model):
    "Store a teacher-graded answer used as a reference for AI grading."

    exercise_id = models.CharField(max_length=100, db_index=True)
    content = models.TextField()
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    feedback = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)

    class Meta:
        ordering = ["exercise_id", "id"]
        verbose_name = "reference sample"
        verbose_name_plural = "reference samples"

    def __str__(self):
        return f"Exercise {self.exercise_id}: {self.score:g}/100"


class TutorSession(models.Model):
    """
    Lưu lịch sử làm bài của 1 phiên chat gia sư (tutor chat) cho 1 học sinh:
    toàn bộ hội thoại, kết quả cuối cùng (compiled_final_answer), và điểm
    chấm essay (nếu đã được chấm qua submit_tutor_essay_for_grading_api).

    student trỏ thẳng tới settings.AUTH_USER_MODEL (project đã có sẵn
    django.contrib.auth + AuthenticationMiddleware, nên request.user luôn
    có sẵn ở mọi view, không cần client tự gửi student_id thủ công nữa).
    """

    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_sessions",
    )

    question_prompt = models.TextField()
    required_key_points = models.JSONField(default=list, blank=True)

    # Toàn bộ hội thoại: [{"role": "user"/"model", "content": "..."}]
    transcript = models.JSONField(default=list, blank=True)

    is_ready_for_grading = models.BooleanField(default=False)
    compiled_final_answer = models.TextField(blank=True, null=True)

    # Kết quả trả về từ advanced_grade_essay, null nếu chưa chấm
    grading_result = models.JSONField(blank=True, null=True)
    graded_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "tutor session"
        verbose_name_plural = "tutor sessions"

    def __str__(self):
        status = "graded" if self.grading_result else ("ready" if self.is_ready_for_grading else "in progress")
        return f"[{status}] {self.student} - {self.question_prompt[:50]}"
