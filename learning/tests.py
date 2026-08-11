from django.test import TestCase

# Create your tests here.
class NotesPageTest(TestCase): #need to be edited
    def test_learning_page_opens(self):
        response = self.client.get("/learning")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, Django Girls!")