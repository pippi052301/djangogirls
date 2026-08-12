from django.shortcuts import render, redirect, get_object_or_404
from .models import Note, Folder, Tag, Attachment, NoteLink
from .forms import NoteForm, FolderForm, TagForm, NoteTagForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
# ================= NOTES VIEWS =================
@login_required
def note_list(request):
    notes_queryset = Note.objects.filter(owner=request.user).prefetch_related('tags', 'folder').order_by('-created_at')
    folders = Folder.objects.filter(owner=request.user)
    tags = Tag.objects.filter(owner=request.user)

    paginator = Paginator(notes_queryset, 10)
    page_number = request.GET.get('page', 1)
    notes = paginator.get_page(page_number)

    form = NoteForm(user=request.user)

    return render(
        request,
        "notes/note_list.html",
        {
            "notes": notes,
            "folders": folders,
            "tags": tags,
            "form": form,
        }
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
            form.save_m2m() 

            tag_ids = request.POST.getlist('tags')
            if tag_ids:
                valid_tags = Tag.objects.filter(id__in=tag_ids, owner=request.user)
                note.tags.set(valid_tags)

            return redirect("notes:note_list")

    return redirect("notes:note_list")

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
            note = form.save()
            tag_ids = request.POST.getlist('tags')
            if tag_ids:
                valid_tags = Tag.objects.filter(id__in=tag_ids, owner=request.user)
                note.tags.set(valid_tags)
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
        "notes/note_confirm_deletion.html",
        {"note": note, "object": note}
    )


# ================= FOLDERS VIEWS =================
@login_required
def folder_list(request):
    folders = Folder.objects.filter(owner=request.user).prefetch_related('notes')
    
    return render(
        request,
        "folders/folder_list.html", 
        {
            "folders": folders,
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

            return redirect("notes:folder_list")

    return redirect("notes:folder_list")

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

    notes = folder.notes.all()

    return render(
        request,
        "folders/folder_detail.html",
        {
            "folder": folder,
            "subfolders": subfolders,
            "notes": notes,
        }
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
            folder = form.save()
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
        "folders/folder_form.html",
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
        "folders/folder_confirm_delete.html",
        {
            "folder": folder,
            "object": folder
        }
    )


# ================= TAGS VIEWS =================
@login_required
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)

        if form.is_valid():
            tag = form.save(commit=False)
            tag.owner = request.user
            tag.save()

            # AJAX (JavaScript)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'id': tag.id, 'name': tag.name})

            return redirect("notes:tag_list")

    else:
        form = TagForm()

    return render(
        request,
        "notes/tags/tag_form.html",
        {"form": form}
    )

@login_required
@xframe_options_sameorigin
def tag_list(request):
    tags = Tag.objects.filter(owner=request.user)
    return render(
        request,
        "notes/tags/tag_list.html",
        {"tags": tags}
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
        "notes/tags/tag_detail.html",
        {
            "tag": tag,
            "notes": notes
        }
    )

@login_required
def tag_edit(request, pk):
    tag = get_object_or_404(
        Tag,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect("notes:tag_list")
    else:
        form = TagForm(instance=tag)

    return render(
        request,
        "notes/tags/tag_form.html",
        {
            "form": form,
            "tag": tag,
            "object": tag
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
        "notes/tags/tag_confirm_deletion.html",
        {
            "tag": tag,
            "object": tag
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