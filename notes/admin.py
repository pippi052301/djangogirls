from django.contrib import admin

from .models import (
    Folder,
    Note,
    Tag,
    NoteTag,
    Attachment,
    NoteLink,
)


admin.site.register(Folder)
admin.site.register(Note)
admin.site.register(Tag)
admin.site.register(NoteTag)
admin.site.register(Attachment)
admin.site.register(NoteLink)