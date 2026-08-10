from django.http import HttpResponse
from .models import Note  


def home(request):
    return HttpResponse("Hello, Django Girls!")
from django.shortcuts import render

def note_create(request):
    return render(request, 'learning/note_form.html')
def note_list(request):
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'learning/note_list.html', {'notes': notes})