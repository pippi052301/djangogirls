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

#Genaraate OTP for password_reset
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        
        return timezone.now() <= self.created_at + timedelta(minutes=5)

    @classmethod
    def generate_otp(cls, user):
        code = str(random.randint(100000, 999999))
        cls.objects.create(user=user, otp_code=code)
        return code               
