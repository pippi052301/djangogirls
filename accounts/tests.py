from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AccountsPageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_accounts_page_opens(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_logout_get_and_post(self):
        self.client.login(username="testuser", password="password123")
        get_res = self.client.get(reverse("accounts:logout"))
        self.assertEqual(get_res.status_code, 302)

        self.client.login(username="testuser", password="password123")
        post_res = self.client.post(reverse("accounts:logout"))
        self.assertEqual(post_res.status_code, 302)