from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Folder(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="folders",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subfolders",
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if self.parent_id:
            if self.parent.owner_id != self.owner_id:
                raise ValidationError(
                    "別のユーザーのフォルダには移動できません。"
                )

            ancestor = self.parent

            while ancestor is not None:
                if ancestor.pk == self.pk:
                    raise ValidationError(
                        "親子関係が循環するフォルダ構造にはできません。"
                    )

                ancestor = ancestor.parent

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Note(models.Model):
    class TemplateType(models.TextChoices):
        BLANK = "blank", "白紙"
        LECTURE = "lecture", "授業ノート"
        SUMMARY = "summary", "まとめ"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    folder = models.ForeignKey(
        Folder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notes",
    )
    title = models.CharField(max_length=255)
    subject = models.CharField(
        max_length=100,
        blank=True,
    )
    content = models.JSONField(
        default=dict,
        blank=True,
    )
    template_type = models.CharField(
        max_length=50,
        choices=TemplateType.choices,
        default=TemplateType.BLANK,
    )
    tags = models.ManyToManyField(
        "Tag",
        through="NoteTag",
        related_name="notes",
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def clean(self):
        super().clean()

        if self.folder_id and self.folder.owner_id != self.owner_id:
            raise ValidationError(
                "別のユーザーのフォルダには保存できません。"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tag(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_tag_name_per_owner",
            )
        ]

    def __str__(self):
        return self.name


class NoteTag(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="note_tags",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="note_tags",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["note", "tag"],
                name="unique_note_tag",
            )
        ]

    def clean(self):
        super().clean()

        if self.note_id and self.tag_id:
            if self.note.owner_id != self.tag.owner_id:
                raise ValidationError(
                    "別のユーザーのタグは追加できません。"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Attachment(models.Model):
    class AttachmentType(models.TextChoices):
        IMAGE = "image", "画像"
        FILE = "file", "ファイル"
        LINK = "link", "リンク"

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        upload_to="attachments/",
        blank=True,
        null=True,
    )
    url = models.URLField(blank=True)
    attachment_type = models.CharField(
        max_length=20,
        choices=AttachmentType.choices,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def clean(self):
        super().clean()

        if (
            self.attachment_type == self.AttachmentType.LINK
            and not self.url
        ):
            raise ValidationError(
                "リンク添付にはURLが必要です。"
            )

        if (
            self.attachment_type != self.AttachmentType.LINK
            and not self.file
        ):
            raise ValidationError(
                "画像・ファイル添付にはファイルが必要です。"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class NoteLink(models.Model):
    from_note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="links_from",
    )
    to_note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="links_to",
    )
    relation_label = models.CharField(
        max_length=100,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "from_note",
                    "to_note",
                    "relation_label",
                ],
                name="unique_note_link",
            )
        ]

    def clean(self):
        super().clean()

        if self.from_note_id and self.to_note_id:
            if self.from_note_id == self.to_note_id:
                raise ValidationError(
                    "同じノート同士はリンクできません。"
                )

            if self.from_note.owner_id != self.to_note.owner_id:
                raise ValidationError(
                    "別のユーザーのノートにはリンクできません。"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class MapNode(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="map_nodes",
    )
    key = models.CharField(
        max_length=100,
        help_text="AIのnodes[].idに対応するノート内の識別子",
    )
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["note", "key"],
                name="unique_map_node_key_per_note",
            )
        ]

    def __str__(self):
        return self.label


class MapEdge(models.Model):
    source = models.ForeignKey(
        MapNode,
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
    )
    target = models.ForeignKey(
        MapNode,
        on_delete=models.CASCADE,
        related_name="incoming_edges",
    )
    label = models.CharField(
        max_length=100,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "target", "label"],
                name="unique_map_edge",
            )
        ]

    def clean(self):
        super().clean()

        if self.source_id and self.target_id:
            if self.source_id == self.target_id:
                raise ValidationError(
                    "同じノード自身には接続できません。"
                )

            if self.source.note_id != self.target.note_id:
                raise ValidationError(
                    "異なるノートに属するノード同士は接続できません。"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} -> {self.target}"