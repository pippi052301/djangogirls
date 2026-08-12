from django.shortcuts import render, redirect, get_object_or_404
from .models import Note, Folder, Tag, Attachment, NoteLink
from .forms import NoteForm, FolderForm, TagForm, NoteTagForm, AttachmentForm, NoteLinkForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
#notes settings
@login_required
def note_list(request):
    notes = Note.objects.filter(owner=request.user)

    return render(
        request,
        "notes/note_list.html",
        {"notes": notes}
    )

@login_required
def note_create(request):

    if request.method == "POST":

        form = NoteForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            note = form.save(commit=False)

            note.owner = request.user

            note.save()

            return redirect(
                "notes:note_detail",
                pk=note.pk
            )

    else:

        form = NoteForm(
            user=request.user
        )

    return render(
        request,
        "notes/note_form.html",
        {"form": form}
    )
    
@login_required
def note_detail(request, pk):
    note = get_object_or_404(
        Note,
        pk=pk,
        owner=request.user
    )

    return render(
        request,
        "notes/note_detail.html",
        {"note": note}
    )

@login_required
def note_edit(request, pk):

    note = get_object_or_404(
        Note,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        form = NoteForm(
            request.POST,
            instance=note,
            user=request.user
        )

        if form.is_valid():

            form.save()

            return redirect(
                "notes:note_detail",
                pk=note.pk
            )

    else:

        form = NoteForm(
            instance=note,
            user=request.user
        )

    return render(
        request,
        "notes/note_form.html",
        {
            "form": form,
            "note": note
        }
    )
    
@login_required
def note_delete(request, pk):
    note = get_object_or_404(
        Note,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":
        note.delete()

        return redirect("notes:note_list")

    return render(
        request,
        "notes/note_confirm_delete.html",
        {"note": note}
    )
    
#folder settings
@login_required
def folder_list(request):

    folders = Folder.objects.filter(
        owner=request.user,
        parent=None
    )

    return render(
        request,
        "notes/folder_list.html",
        {
            "folders": folders
        }
    )
    
@login_required
def folder_create(request):

    if request.method == "POST":

        form = FolderForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            folder = form.save(commit=False)

            folder.owner = request.user

            folder.save()

            return redirect(
                "notes:folder_detail",
                pk=folder.pk
            )

    else:

        form = FolderForm(
            user=request.user
        )

    return render(
        request,
        "notes/folder_form.html",
        {
            "form": form
        }
    )
    
@login_required
def folder_detail(request, pk):

    folder = get_object_or_404(
        Folder,
        pk=pk,
        owner=request.user
    )

    subfolders = Folder.objects.filter(
        parent=folder,
        owner=request.user
    )

    notes = Note.objects.filter(
        folder=folder,
        owner=request.user
    )

    return render(
        request,
        "notes/folder_detail.html",
        {
            "folder": folder,
            "subfolders": subfolders,
            "notes": notes,
        }
    )
    
@login_required
def folder_detail(request, pk):
    folder = get_object_or_404(Folder, pk=pk, owner=request.user)
    notes = folder.notes.all()  # Lấy danh sách ghi chú thuộc thư mục này
    return render(
        request,
        "notes/folder_detail.html",
        {"folder": folder, "notes": notes}
    )
@login_required
def folder_edit(request, pk):

    folder = get_object_or_404(
        Folder,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        form = FolderForm(
            request.POST,
            instance=folder,
            user=request.user
        )

        if form.is_valid():

            form.save()

            return redirect(
                "notes:folder_detail",
                pk=folder.pk
            )

    else:

        form = FolderForm(
            instance=folder,
            user=request.user
        )

    return render(
        request,
        "notes/folder_form.html",
        {
            "form": form,
            "folder": folder
        }
    )
    
@login_required
def folder_delete(request, pk):

    folder = get_object_or_404(
        Folder,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        folder.delete()

        return redirect(
            "notes:folder_list"
        )

    return render(
        request,
        "notes/folder_confirm_delete.html",
        {
            "folder": folder
        }
    )

@login_required
def tag_create(request):

    if request.method == "POST":

        form = TagForm(request.POST)

        if form.is_valid():

            tag = form.save(commit=False)

            tag.owner = request.user

            tag.save()

            return redirect(
                "notes:tag_list"
            )

    else:

        form = TagForm()

    return render(
        request,
        "notes/tag_form.html",
        {
            "form": form
        }
    )
    
@login_required
def tag_list(request):

    tags = Tag.objects.filter(
        owner=request.user
    )

    return render(
        request,
        "notes/tag_list.html",
        {
            "tags": tags
        }
    )
    
@login_required
def tag_detail(request, pk):

    tag = get_object_or_404(
        Tag,
        pk=pk,
        owner=request.user
    )

    notes = Note.objects.filter(
        owner=request.user,
        tags=tag
    )

    return render(
        request,
        "notes/tag_detail.html",
        {
            "tag": tag,
            "notes": notes
        }
    )
    
@login_required
def tag_delete(request, pk):

    tag = get_object_or_404(
        Tag,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        tag.delete()

        return redirect(
            "notes:tag_list"
        )

    return render(
        request,
        "notes/tag_confirm_delete.html",
        {
            "tag": tag
        }
    )

@login_required
def note_tags(request, pk):

    note = get_object_or_404(
        Note,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        form = NoteTagForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            tags = form.cleaned_data["tags"]

            note.tags.set(tags)

            return redirect(
                "notes:note_detail",
                pk=note.pk
            )

    else:

        form = NoteTagForm(
            user=request.user,
            initial={
                "tags": note.tags.all()
            }
        )

    return render(
        request,
        "notes/note_tags.html",
        {
            "note": note,
            "form": form
        }
    )
    
@login_required
def attachment_upload(request, pk):

    note = get_object_or_404(
        Note,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        form = AttachmentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            attachment = form.save(
                commit=False
            )

            attachment.note = note

            attachment.save()

            return redirect(
                "notes:note_detail",
                pk=note.pk
            )

    else:

        form = AttachmentForm()

    return render(
        request,
        "notes/attachment_form.html",
        {
            "form": form,
            "note": note
        }
    )
    
@login_required
def attachment_delete(request, pk):

    attachment = get_object_or_404(
        Attachment,
        pk=pk,
        note__owner=request.user
    )

    if request.method == "POST":
        note = attachment.note
        attachment.delete()

        return redirect(
            "notes:note_detail",
            pk=note.pk
        )

    return render(
        request,
        "notes/attachment_confirm_delete.html",
        {
            "attachment": attachment
        }
    )
    
@login_required
def note_link_create(request, pk):

    from_note = get_object_or_404(
        Note,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        form = NoteLinkForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            link = form.save(
                commit=False
            )

            link.from_note = from_note

            link.save()

            return redirect(
                "notes:note_detail",
                pk=from_note.pk
            )

    else:

        form = NoteLinkForm(
            user=request.user
        )

    return render(
        request,
        "notes/note_link_form.html",
        {
            "form": form,
            "note": from_note
        }
    )

@login_required
def note_link_delete(request, pk):

    link = get_object_or_404(
        NoteLink,
        pk=pk,
        from_note__owner=request.user
    )


    if request.method == "POST":
        note = link.from_note
        link.delete()

        return redirect(
            "notes:note_detail",
            pk=note.pk
        )

    return render(
        request,
        "notes/note_link_confirm_delete.html",
        {
            "link": link
        }
    )

@login_required
def map_view(request):

    return render(
        request,
        "notes/map.html"
    )
    
@login_required
def map_graph_data(request):

    notes = Note.objects.filter(
        owner=request.user
    )

    links = NoteLink.objects.filter(
        from_note__owner=request.user
    )

    nodes = [{"id": note.id, "label": note.title} for note in notes]

    edges = [
        {"id": link.id, "from": link.from_note.id, "to": link.to_note.id}
        for link in links
    ]

    return JsonResponse({
        "nodes": nodes,
        "edges": edges,
    })
@login_required
def template_picker(request):

    return render(
        request,
        "notes/template_picker.html"
    )
    
@login_required
def note_autosave(request, pk):

    if request.method != "PATCH":

        return JsonResponse(
            {
                "error": "PATCH required"
            },
            status=405
        )

    note = get_object_or_404(
        Note,
        pk=pk,
        owner=request.user
    )

    try:

        data = json.loads(
            request.body
        )

        note.content = data.get(
            "content",
            {}
        )

        note.save()

        return JsonResponse({
            "success": True
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON"
            },
            status=400
        )