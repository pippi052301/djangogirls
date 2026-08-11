from django.test import TestCase

# Create your tests here.
class ai_enginePageTest(TestCase):
    def test_ai_engine_page_opens(self):
        response = self.client.get("/ai/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Engine Home")