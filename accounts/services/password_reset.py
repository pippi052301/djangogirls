from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone

from accounts.models import PasswordResetOTP


class InvalidPasswordResetOTP(ValueError):
    """Raised when a password reset OTP cannot be used."""


@transaction.atomic
def issue_password_reset_otp(*, user) -> str:
    """Issue a new OTP and invalidate the user's previous unused OTP."""
    return PasswordResetOTP.generate_otp(user)


@transaction.atomic
def reset_password_with_otp(
    *,
    user,
    otp_code: str,
    new_password: str,
):
    """Validate an OTP, update the password, and consume the OTP atomically."""
    normalized_code = otp_code.strip()

    if len(normalized_code) != 6 or not normalized_code.isdigit():
        raise InvalidPasswordResetOTP("The OTP is invalid or has expired.")

    otp = (
        PasswordResetOTP.objects
        .select_for_update()
        .filter(
            user=user,
            otp_code=normalized_code,
            used_at__isnull=True,
        )
        .first()
    )

    if otp is None or not otp.is_valid():
        raise InvalidPasswordResetOTP("The OTP is invalid or has expired.")

    validate_password(new_password, user=user)

    user.set_password(new_password)
    user.save(update_fields=["password"])

    otp.used_at = timezone.now()
    otp.save(update_fields=["used_at"])

    return user
