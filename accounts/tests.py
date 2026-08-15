from django.test import TestCase

# Create your tests here.
class AccountsPageTest(TestCase):
    def test_accounts_page_opens(self):
        response = self.client.get("/accounts/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accounts Home")