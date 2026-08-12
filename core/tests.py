from django.test import TestCase

# Create your tests here.
class corePageTest(TestCase):
    def test_core_page_opens(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Support")