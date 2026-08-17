from collections.abc import Iterable

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from notes.models import Folder, Note
from notes.services.note_management import create_note


def _ensure_folder_owner(*, folder: Folder, owner) -> None:
    if folder.owner_id != owner.pk:
        raise PermissionDenied("You do not have permission to modify this folder.")


def _validate_parent(
    *,
    parent: Folder | None,
    owner,
    folder: Folder | None = None,
) -> None:
    if parent is None:
        return

    _ensure_folder_owner(folder=parent, owner=owner)

    if folder is None:
        return

    current = parent
    visited_ids = set()

    while current is not None:
        if current.pk == folder.pk:
            raise ValidationError(
                {"parent": "A folder cannot be placed inside itself or its descendants."}
            )

        if current.pk in visited_ids:
            raise ValidationError(
                {"parent": "The selected folder hierarchy already contains a cycle."}
            )

        visited_ids.add(current.pk)
        current = current.parent


@transaction.atomic
def create_folder_with_initial_note(
    *,
    owner,
    name: str,
    parent: Folder | None = None,
    initial_note_title: str = "",
    initial_note_content=None,
    initial_note_template_type: str = "blank",
    initial_note_tag_ids: Iterable[int | str] = (),
) -> tuple[Folder, Note | None]:
    """Create a folder and its optional initial note atomically."""
    _validate_parent(parent=parent, owner=owner)

    folder = Folder(
        owner=owner,
        parent=parent,
        name=name,
    )
    folder.full_clean()
    folder.save()

    note = None
    if initial_note_title.strip():
        note = create_note(
            owner=owner,
            title=initial_note_title,
            content={} if initial_note_content is None else initial_note_content,
            folder=folder,
            template_type=initial_note_template_type,
            tag_ids=initial_note_tag_ids,
        )

    return folder, note


@transaction.atomic
def update_folder(
    *,
    folder: Folder,
    owner,
    name: str,
    parent: Folder | None,
) -> Folder:
    """Rename or move a folder while preventing ownership leaks and cycles."""
    _ensure_folder_owner(folder=folder, owner=owner)
    _validate_parent(parent=parent, owner=owner, folder=folder)

    folder.name = name
    folder.parent = parent
    folder.full_clean()
    folder.save()

    return folder
