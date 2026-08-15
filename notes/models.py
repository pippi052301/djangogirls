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
        default='blank',
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    
    )
    tags = models.ManyToManyField(
        'Tag',
        through='NoteTag',
        blank=True
    )
    

    @property
    def content_text(self):
        if isinstance(self.content, dict):
            return self.content.get("body", "")
        return str(self.content or "")

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

    @property
    def color_class(self):
        colors = [
            "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-800",
            "bg-purple-100 text-purple-700 border-purple-200 dark:bg-purple-900/40 dark:text-purple-300 dark:border-purple-800",
            "bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300 dark:border-emerald-800",
            "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:border-amber-800",
            "bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-900/40 dark:text-rose-300 dark:border-rose-800",
            "bg-indigo-100 text-indigo-700 border-indigo-200 dark:bg-indigo-900/40 dark:text-indigo-300 dark:border-indigo-800",
            "bg-pink-100 text-pink-700 border-pink-200 dark:bg-pink-900/40 dark:text-pink-300 dark:border-pink-800",
            "bg-teal-100 text-teal-700 border-teal-200 dark:bg-teal-900/40 dark:text-teal-300 dark:border-teal-800",
            "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/40 dark:text-orange-300 dark:border-orange-800",
            "bg-cyan-100 text-cyan-700 border-cyan-200 dark:bg-cyan-900/40 dark:text-cyan-300 dark:border-cyan-800",
        ]
        val = (self.id or 0) + sum(ord(c) for c in self.name)
        return colors[val % len(colors)]


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