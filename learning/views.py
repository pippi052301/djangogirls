from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from notes.models import Note
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from accounts.models import PasswordResetOTP
from django.http import HttpResponse
from accounts.forms import RegisterForm 
def home(request):
    return HttpResponse("Hello, Django Girls!")

def note_create(request):
    return render(request, 'learning/note_form.html')

def note_list(request):
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'learning/note_list.html', {'notes': notes})
