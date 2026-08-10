from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("Hello, Django Girls!")
from django.shortcuts import render

def note_create(request):
    return render(request, 'learning/note_form.html')