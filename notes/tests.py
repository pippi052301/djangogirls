from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Note, Folder, Tag

class NotesAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        self.folder = Folder.objects.create(name="Study Folder", owner=self.user)
        self.tag = Tag.objects.create(name="Python", owner=self.user)
        self.note = Note.objects.create(
            title="First Note",
            content={"body": "Hello Django"},
            owner=self.user,
            folder=self.folder
        )
        self.note.tags.add(self.tag)

    def test_notes_page_opens(self):
        response = self.client.get(reverse("notes:note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Notes")
        self.assertContains(response, "First Note")

    def test_note_create(self):
        response = self.client.post(reverse("notes:note_create"), {
            "title": "New Note",
            "content": "This is raw text content",
            "folder": self.folder.id,
            "tags": [self.tag.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title="New Note").exists())

    def test_note_detail_and_delete(self):
        detail_url = reverse("notes:note_detail", kwargs={"pk": self.note.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First Note")

        delete_url = reverse("notes:note_delete", kwargs={"pk": self.note.pk})
        get_del = self.client.get(delete_url)
        self.assertEqual(get_del.status_code, 200)

        post_del = self.client.post(delete_url)
        self.assertEqual(post_del.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_folder_list_and_delete(self):
        response = self.client.get(reverse("notes:folder_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Study Folder")

        detail_url = reverse("notes:folder_detail", kwargs={"pk": self.folder.pk})
        res_detail = self.client.get(detail_url)
        self.assertEqual(res_detail.status_code, 200)

        delete_url = reverse("notes:folder_delete", kwargs={"pk": self.folder.pk})
        get_del = self.client.get(delete_url)
        self.assertEqual(get_del.status_code, 200)

    def test_tag_views(self):
        list_url = reverse("notes:tag_list")
        res_list = self.client.get(list_url)
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "Python")

        detail_url = reverse("notes:tag_detail", kwargs={"pk": self.tag.pk})
        res_detail = self.client.get(detail_url)
        self.assertEqual(res_detail.status_code, 200)

        edit_url = reverse("notes:tag_update", kwargs={"pk": self.tag.pk})
        res_edit = self.client.get(edit_url)
        self.assertEqual(res_edit.status_code, 200)

        delete_url = reverse("notes:tag_delete", kwargs={"pk": self.tag.pk})
        res_del_get = self.client.get(delete_url)
        self.assertEqual(res_del_get.status_code, 200)