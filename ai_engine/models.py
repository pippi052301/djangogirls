from django.db import models
from pgvector.django import HalfVectorField, HnswIndex


class SemanticCache(models.Model):
    class Purpose(models.TextChoices):
        QUIZ = "quiz", "問題生成"
        ADAPTIVE_PRACTICE = "adaptive_practice", "適応型問題生成"
        GRADING = "grading", "AI採点"
        KNOWLEDGE_GRAPH = "knowledge_graph", "マップ生成"

    input_hash = models.CharField(
        max_length=64,
        help_text="完全一致確認用のSHA-256ハッシュ",
    )
    input_embedding = HalfVectorField(
        dimensions=3072,
        help_text="意味検索に使用する入力文のEmbedding",
    )
    response = models.JSONField(
        help_text="再利用するAIのJSON応答",
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
