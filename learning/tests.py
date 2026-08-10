from django.test import TestCase

# Create your tests here.
class HomeTest(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200) #status_code = 404, 200, etc