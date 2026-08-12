from django.db import models
from pgvector.django import HalfVectorField, HnswIndex


class SemanticCache(models.Model):
    class Purpose(models.TextChoices):
        QUIZ = "quiz", "Question Generation"
        ADAPTIVE_PRACTICE = "adaptive_practice", "Adaptive Question Generation"
        GRADING = "grading", "AI Grading"
        KNOWLEDGE_GRAPH = "knowledge_graph", "Map Generation"

    input_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 hash for exact match verification",
    )
    input_embedding = HalfVectorField(
        dimensions=3072,
        help_text="Embedding for semantic search",
    )
    response = models.JSONField(
        help_text="JSON response from the AI model for reuse",
    )
    purpose = models.CharField(
        max_length=30,
        choices=Purpose.choices,
    )
    model_name = models.CharField(
        max_length=100,
    )
    prompt_version = models.CharField(
        max_length=30,
        default="1",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    last_used_at = models.DateTimeField(
        auto_now=True,
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-last_used_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "input_hash",
                    "purpose",
                    "model_name",
                    "prompt_version",
                ],
                name="unique_semantic_cache_input",
            )
        ]
        indexes = [
            HnswIndex(
                name="semantic_cache_embedding_hnsw",
                fields=["input_embedding"],
                m=16,
                ef_construction=64,
                opclasses=["halfvec_cosine_ops"],
            )
        ]

    def __str__(self):
        return f"{self.purpose} - {self.input_hash[:12]}"
