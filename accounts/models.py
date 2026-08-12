import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_otps",
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def is_valid(self):
        expires_at = self.created_at + timedelta(minutes=5)

        return (
            self.used_at is None
            and timezone.now() <= expires_at
        )

    @classmethod
    def generate_otp(cls, user):
        code = f"{secrets.randbelow(1_000_000):06d}"

        cls.objects.create(
            user=user,
            otp_code=code,
        )

        return code

    def __str__(self):
        return f"Password reset OTP for {self.user}"