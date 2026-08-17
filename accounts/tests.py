from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import PasswordResetOTP


class AccountsPageTest(TestCase):
    def test_accounts_page_opens(self):
        response = self.client.get("/accounts/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accounts Home")


class PasswordResetOTPTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="OldPassword123!"
        )

    def test_generate_otp(self):
        code = PasswordResetOTP.generate_otp(self.user)
        self.assertEqual(len(code), 6)
        otp_obj = PasswordResetOTP.objects.filter(user=self.user, otp_code=code).first()
        self.assertIsNotNone(otp_obj)
        self.assertTrue(otp_obj.is_valid())

    def test_password_reset_flow(self):
        # Step 1: Send OTP
        response = self.client.post("/accounts/password-reset/", {
            "action": "send_otp",
            "email": "testuser@example.com"
        })
        self.assertEqual(response.status_code, 200)
        otp_obj = PasswordResetOTP.objects.filter(user=self.user).first()
        self.assertIsNotNone(otp_obj)

        # Step 2: Verify & Reset
        response = self.client.post("/accounts/password-reset/", {
            "action": "verify_and_reset",
            "email": "testuser@example.com",
            "otp_code": otp_obj.otp_code,
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))

        otp_obj.refresh_from_db()
        self.assertIsNotNone(otp_obj.used_at)
        self.assertFalse(otp_obj.is_valid())