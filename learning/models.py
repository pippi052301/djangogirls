from django.db import models
from django.db import models
from django.utils import timezone

class Note(models.Model):
    content = models.TextField()                     
    created_at = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return self.content[:30]                 
# Create your models here.
