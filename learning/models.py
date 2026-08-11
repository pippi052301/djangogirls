from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
import random
from django.contrib.auth.models import User
from datetime import timedelta
class Note(models.Model):
    content = models.TextField()                     
    created_at = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return self.content[:30]  
            
