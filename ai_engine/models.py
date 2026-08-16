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


from django.conf import settings

class ChatSession(models.Model):
    "Store user AI Assistant chat session history."
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default='New Chat')
    context_type = models.CharField(max_length=50, default='free_talk')
    context_name = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user} - {self.title}"


class ChatMessage(models.Model):
    "Store individual messages inside a ChatSession."
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"