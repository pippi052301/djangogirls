from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Note, Folder, Tag, Attachment, NoteLink
from .forms import NoteForm, FolderForm, TagForm, NoteTagForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin

from django.utils import timezone

# ================= CONTEXT PROCESSORS =================
def notes_processor(request):
    if request.user.is_authenticated:
        today_date = timezone.localtime(timezone.now()).date()
        today_notes = Note.objects.filter(owner=request.user, created_at__date=today_date).order_by('-created_at')
        sidebar_notes = Note.objects.filter(owner=request.user).order_by('-created_at')[:30]
        sidebar_folders = Folder.objects.filter(owner=request.user).order_by('-created_at')[:10]
        return {
            'today_notes': today_notes,
            'sidebar_notes': sidebar_notes,
            'sidebar_folders': sidebar_folders,
        }
    return {}


# ================= NOTES VIEWS =================
@login_required
def note_list(request):
    notes_queryset = Note.objects.filter(owner=request.user).prefetch_related('tags', 'folder')

    search_query = request.GET.get('q', '').strip()
    tag_id = request.GET.get('tag', '').strip()
    sort_by = request.GET.get('sort', 'recently').strip()

    if tag_id:
        notes_queryset = notes_queryset.filter(tags__id=tag_id)

    if search_query:
        notes_queryset = notes_queryset.filter(
            Q(title__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    if sort_by == 'az':
        notes_queryset = notes_queryset.order_by('title')
    elif sort_by == 'za':
        notes_queryset = notes_queryset.order_by('-title')
    else:
        notes_queryset = notes_queryset.order_by('-updated_at')

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
            "search_query": search_query,
            "selected_sort": sort_by,
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
            valid_tags = Tag.objects.filter(id__in=tag_ids, owner=request.user)
            note.tags.set(valid_tags)

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
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

@login_required
def note_bulk_delete(request):
    if request.method == "POST":
        note_ids = request.POST.getlist("note_ids")
        if note_ids:
            Note.objects.filter(id__in=note_ids, owner=request.user).delete()
    return redirect("notes:note_list")


# ================= FOLDERS VIEWS =================
@login_required
def folder_list(request):
    search_query = request.GET.get('q', '').strip()
    folders = Folder.objects.filter(owner=request.user).prefetch_related('notes')
    tags = Tag.objects.filter(owner=request.user)
    
    if search_query:
        folders = folders.filter(name__icontains=search_query)

    return render(
        request,
        "folders/folder_list.html", 
        {
            "folders": folders,
            "tags": tags,
            "search_query": search_query,
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

            # Create initial note if provided inside New Folder modal
            note_title = request.POST.get('note_title', '').strip()
            note_content = request.POST.get('note_content', '').strip()
            if note_title:
                new_note = Note.objects.create(
                    title=note_title,
                    content={"body": note_content},
                    owner=request.user,
                    folder=folder
                )
                tag_ids = request.POST.getlist('note_tags')
                if tag_ids:
                    tag_objs = Tag.objects.filter(id__in=tag_ids, owner=request.user)
                    new_note.tags.set(tag_objs)

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"id": folder.id, "name": folder.name})

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


@login_required
def folder_bulk_delete(request):
    if request.method == "POST":
        folder_ids = request.POST.getlist("folder_ids")
        if folder_ids:
            Folder.objects.filter(id__in=folder_ids, owner=request.user).delete()
    return redirect("notes:folder_list")


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
    return redirect(f"/notes/?q={tag.name}")

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