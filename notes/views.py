from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Note, Folder, Tag, Attachment, NoteLink
from .forms import NoteForm, FolderForm, TagForm, NoteTagForm, AttachmentForm, NoteLinkForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from django.views.decorators.clickjacking import xframe_options_sameorigin

from django.utils import timezone

# ================= CONTEXT PROCESSORS =================
def notes_processor(request):
    if request.user.is_authenticated:
        today_date = timezone.localtime(timezone.now()).date()
        today_notes = Note.objects.filter(owner=request.user, created_at__date=today_date).exclude(template_type='pdf').exclude(title__icontains='.pdf').order_by('-created_at')
        sidebar_notes = Note.objects.filter(owner=request.user).exclude(template_type='pdf').exclude(title__icontains='.pdf').order_by('-created_at')[:30]
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
    notes_queryset = (
        Note.objects
        .filter(owner=request.user)
        .exclude(template_type='pdf')
        .exclude(title__icontains='.pdf')
        .prefetch_related('tags')
        .select_related('folder')
    )

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

            folder_id = request.POST.get('folder') or request.GET.get('folder_id')
            if folder_id:
                folder_obj = Folder.objects.filter(id=folder_id, owner=request.user).first()
                if folder_obj:
                    note.folder = folder_obj

            note.save()
            form.save_m2m()


            form.save_m2m()


            tag_ids = request.POST.getlist('tags')

            if tag_ids:
                valid_tags = Tag.objects.filter(
                    id__in=tag_ids,
                    owner=request.user
                )
                note.tags.set(valid_tags)

            if note.folder:
                return redirect("notes:folder_detail", pk=note.folder.pk)

            return redirect("notes:note_list")

    return redirect("notes:note_list")


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

            parent_id = request.POST.get('parent') or request.GET.get('parent_id')
            if parent_id:
                parent_obj = Folder.objects.filter(id=parent_id, owner=request.user).first()
                if parent_obj:
                    folder.parent = parent_obj

            folder.save()

            # Create notes provided inside New Folder modal (supports multiple notes or single note)
            modal_notes_json = request.POST.get('modal_notes_json', '').strip()
            if modal_notes_json and modal_notes_json != '[]':
                try:
                    notes_arr = json.loads(modal_notes_json)
                    if isinstance(notes_arr, list):
                        for item in notes_arr:
                            n_title = (item.get('title') or 'Untitled Note').strip()
                            n_content = item.get('content', '')
                            n_template = item.get('template_type', 'blank')
                            
                            c_dict = {"body": n_content}
                            if isinstance(n_content, dict):
                                c_dict = n_content
                            elif isinstance(n_content, str) and n_content.startswith('{') and 'pdf_data' in n_content:
                                try:
                                    c_dict = json.loads(n_content)
                                    n_template = 'pdf'
                                except Exception:
                                    pass

                            Note.objects.create(
                                title=n_title,
                                content=c_dict,
                                template_type=n_template,
                                owner=request.user,
                                folder=folder
                            )
                except Exception as e:
                    print('Error parsing modal_notes_json:', e)
            else:
                note_title = request.POST.get('note_title', '').strip()
                note_content = request.POST.get('note_content', '').strip()
                if note_title:
                    template_type = request.POST.get('template_type', 'blank')
                    if not template_type or template_type == 'blank':
                        if '.pdf' in note_title.lower():
                            template_type = 'pdf'

                    content_dict = {"body": note_content}
                    if note_content.startswith('{') and 'pdf_data' in note_content:
                        try:
                            content_dict = json.loads(note_content)
                            template_type = 'pdf'
                        except Exception:
                            pass

                    new_note = Note.objects.create(
                        title=note_title,
                        content=content_dict,
                        template_type=template_type,
                        owner=request.user,
                        folder=folder
                    )
                    tag_ids = request.POST.getlist('note_tags')
                    if tag_ids:
                        tag_objs = Tag.objects.filter(id__in=tag_ids, owner=request.user)
                        new_note.tags.set(tag_objs)

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"id": folder.id, "name": folder.name})

            if folder.parent:
                return redirect("notes:folder_detail", pk=folder.parent.pk)

            return redirect("notes:folder_list")

    return redirect("notes:folder_list")

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
            note = form.save(commit=False)
            note.save()

            form.save_m2m()

            tag_ids = request.POST.getlist('tags')

            valid_tags = Tag.objects.filter(
                id__in=tag_ids,
                owner=request.user
            )

            note.tags.set(valid_tags)

            next_url = (
                request.POST.get("next")
                or request.GET.get("next")
            )

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

    for folder in folders:
        notes_data = []
        for n in folder.notes.all():
            notes_data.append({
                "id": n.id,
                "title": n.title,
                "content": n.content if isinstance(n.content, (dict, str)) else str(n.content),
                "template_type": n.template_type or ('pdf' if '.pdf' in n.title.lower() else 'blank')
            })
        folder.notes_json = json.dumps(notes_data)

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
                template_type = request.POST.get('template_type', 'blank')
                if not template_type or template_type == 'blank':
                    if '.pdf' in note_title.lower():
                        template_type = 'pdf'
                new_note = Note.objects.create(
                    title=note_title,
                    content={"body": note_content},
                    template_type=template_type,
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

    notes = folder.notes.filter(
        owner=request.user
    )

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

            # Batch process modal_notes_json if submitted from side drawer
            modal_notes_json = request.POST.get('modal_notes_json', '').strip()
            if modal_notes_json:
                try:
                    notes_arr = json.loads(modal_notes_json)
                    if isinstance(notes_arr, list):
                        submitted_ids = set()
                        for item in notes_arr:
                            n_id = item.get('id')
                            n_title = (item.get('title') or 'Untitled Note').strip()
                            n_content = item.get('content', '')
                            n_template = item.get('template_type', 'blank')

                            c_dict = {"body": n_content}
                            if isinstance(n_content, dict):
                                c_dict = n_content
                            elif isinstance(n_content, str) and n_content.startswith('{') and 'pdf_data' in n_content:
                                try:
                                    c_dict = json.loads(n_content)
                                    n_template = 'pdf'
                                except Exception:
                                    pass

                            if n_id and str(n_id).isdigit():
                                existing_note = Note.objects.filter(id=int(n_id), owner=request.user).first()
                                if existing_note:
                                    existing_note.title = n_title
                                    existing_note.content = c_dict
                                    existing_note.template_type = n_template
                                    existing_note.folder = folder
                                    existing_note.save()
                                    submitted_ids.add(existing_note.id)
                                    continue

                            new_note = Note.objects.create(
                                title=n_title,
                                content=c_dict,
                                template_type=n_template,
                                owner=request.user,
                                folder=folder
                            )
                            submitted_ids.add(new_note.id)

                        # Delete any notes previously in this folder that were removed from the modal list!
                        folder.notes.exclude(id__in=submitted_ids).delete()
                except Exception as e:
                    print('Error in folder_edit modal_notes_json:', e)

            return redirect("notes:folder_list")
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

    notes = Note.objects.filter(
        owner=request.user,
        tags=tag
    ).prefetch_related("tags")

    return render(
        request,
        "notes/tags/tag_detail.html",
        {
            "tag": tag,
            "notes": notes,
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
        from_note__owner=request.user,
        to_note__owner=request.user
    ).select_related(
        "from_note",
        "to_note"
    )

    nodes = [
        {
            "id": note.id,
            "label": note.title
        }
        for note in notes
    ]

    edges = [
        {
            "id": link.id,
            "from": link.from_note.id,
            "to": link.to_note.id
        }
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