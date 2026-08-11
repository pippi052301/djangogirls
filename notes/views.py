from django.shortcuts import render, redirect, get_object_or_404
from .models import Note, Folder, Tag, Attachment, NoteLink
from .forms import NoteForm, FolderForm
from django.contrib.auth.decorators import login_required

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
    

    