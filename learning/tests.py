from django.test import TestCase
from django.urls import reverse

class LearningPageTests(TestCase):
    def test_learning_home_opens(self):
        response = self.client.get(reverse("learning:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Study Support")