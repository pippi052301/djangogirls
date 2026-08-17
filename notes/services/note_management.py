from collections.abc import Iterable
from typing import Any

from django.core.exceptions import PermissionDenied
from django.db import transaction

from notes.models import Folder, Note, Tag


def _ensure_note_owner(*, note: Note, owner) -> None:
    if note.owner_id != owner.pk:
        raise PermissionDenied("You do not have permission to modify this note.")


def _ensure_folder_owner(*, folder: Folder | None, owner) -> None:
    if folder is not None and folder.owner_id != owner.pk:
        raise PermissionDenied("You do not have permission to use this folder.")


def _owned_tags(*, owner, tag_ids: Iterable[int | str]):
    normalized_ids = []

    for tag_id in tag_ids:
        try:
            normalized_ids.append(int(tag_id))
        except (TypeError, ValueError):
            continue

    return Tag.objects.filter(
        owner=owner,
        pk__in=normalized_ids,
    )


@transaction.atomic
def create_note(
    *,
    owner,
    title: str,
    content: Any = None,
    folder: Folder | None = None,
    template_type: str = "blank",
    tag_ids: Iterable[int | str] = (),
) -> Note:
    """Create a note and assign only tags and a folder owned by the user."""
    _ensure_folder_owner(folder=folder, owner=owner)

    note = Note(
        owner=owner,
        title=title,
        content={} if content is None else content,
        folder=folder,
        template_type=template_type,
    )
    note.full_clean()
    note.save()
    note.tags.set(_owned_tags(owner=owner, tag_ids=tag_ids))

    return note


@transaction.atomic
def update_note(
    *,
    note: Note,
    owner,
    title: str,
    content: Any,
    folder: Folder | None,
    template_type: str,
    tag_ids: Iterable[int | str] | None = None,
) -> Note:
    """Update a note and optionally replace its tags atomically."""
    _ensure_note_owner(note=note, owner=owner)
    _ensure_folder_owner(folder=folder, owner=owner)

    note.title = title
    note.content = content
    note.folder = folder
    note.template_type = template_type
    note.full_clean()
    note.save()

    if tag_ids is not None:
        note.tags.set(_owned_tags(owner=owner, tag_ids=tag_ids))

    return note


@transaction.atomic
def set_note_tags(
    *,
    note: Note,
    owner,
    tag_ids: Iterable[int | str],
) -> Note:
    """Replace a note's tags with tags owned by the same user."""
    _ensure_note_owner(note=note, owner=owner)
    note.tags.set(_owned_tags(owner=owner, tag_ids=tag_ids))

    return note


@transaction.atomic
def autosave_note_content(
    *,
    note: Note,
    owner,
    content: Any,
) -> Note:
    """Persist editor content while enforcing note ownership."""
    _ensure_note_owner(note=note, owner=owner)

    note.content = content
    note.full_clean()
    note.save(update_fields=["content", "updated_at"])

    return note