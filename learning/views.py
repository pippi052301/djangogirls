from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Note
from .forms import  NoteForm
# Create your views here. 

def home(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect("note_list")
        
    else:
        form = NoteForm()
    return render(
        request, 
        "learning/note_form.html",
        {
            "form": form
        }
    )