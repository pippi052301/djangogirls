from django.db import models
<<<<<<< Updated upstream
=======
try:
    from pgvector.django import VectorField
except (ImportError, Exception):
    class VectorField(models.JSONField):
        def __init__(self, *args, dimensions=None, **kwargs):
            super().__init__(*args, **kwargs)
>>>>>>> Stashed changes

# Create your models here.
