from django.shortcuts import render, redirect
from .models import Note
from .forms import NoteForm


def home(request):
    return render(request, "home.html")


def create_note(request):
    if request.method == "POST":
        form = NoteForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("learning:note_list")

    else:
        form = NoteForm()

    return render(
        request,
        "learning/note_form.html",
        {
            "form": form
        }
    )
    
def note_list(request):
    notes = Note.objects.all()

    return render(
        request,
        "learning/note_list.html",
        {
            "notes": notes
        }
    )