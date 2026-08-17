
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
