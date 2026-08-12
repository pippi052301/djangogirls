from django.test import TestCase
from django.contrib.auth.models import User

class NotesPageTest(TestCase):
    def test_notes_page_opens(self):
        user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        
        response = self.client.get("/notes/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Note list")