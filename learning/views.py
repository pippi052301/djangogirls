from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Note
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import PasswordResetOTP
from django.http import HttpResponse
from accounts.forms import RegisterForm 
def home(request):
    return render(request, 'learning/home.html')  # or return HttpResponse("Homepage")

def note_create(request):
    return render(request, 'learning/note_form.html')

def note_list(request):
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'learning/note_list.html', {'notes': notes})
def custom_password_reset(request):
    step = 1
    email = ""

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "send_otp":
            email = request.POST.get("email", "")
            # TODO: Logic tạo và gửi mã OTP qua Email ở đây
            step = 2
            messages.success(request, f"OTP code has been sent to {email}.")

        elif action == "verify_and_reset":
            otp_code = request.POST.get("otp_code")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match!")
                step = 2
            else:
                # TODO: Logic xác thực OTP và đổi mật khẩu cho user ở đây
                messages.success(request, "Password reset successfully. Please log in.")
                return redirect("accounts:login")

    return render(
        request,
        "accounts/password_reset.html",
        {"step": step, "email": email}
    )