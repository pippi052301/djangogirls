from django.test import TestCase

# Create your tests here.
class NotesPageTest(TestCase):
    def test_notes_page_opens(self):
        response = self.client.get("/notes/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notes Home")