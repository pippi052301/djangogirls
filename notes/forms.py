from django.db import models
from django.contrib.auth.models import User


class Folder(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='folders'
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subfolders'
    )

    name = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Note(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes'
    )

    folder = models.ForeignKey(
        Folder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notes'
    )

    title = models.CharField(
        max_length=255
    )

    content = models.JSONField(
        default=dict,
        blank=True
    )

    template_type = models.CharField(
        max_length=50,
        default='blank'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


class Tag(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tags'
    )

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


class NoteTag(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE
    )

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['note', 'tag'],
                name='unique_note_tag'
            )
        ]


class Attachment(models.Model):
    ATTACHMENT_TYPES = [
        ('image', 'Image'),
        ('file', 'File'),
        ('link', 'Link'),
    ]

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    file = models.FileField(
        upload_to='attachments/',
        blank=True,
        null=True
    )

    url = models.URLField(
        blank=True
    )

    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class NoteLink(models.Model):
    from_note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='links_from'
    )

    to_note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='links_to'
    )

    relation_label = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )