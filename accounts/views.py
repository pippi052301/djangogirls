from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.forms import RegisterForm
from .models import UserProfile, PasswordResetOTP


def home(request):
    return HttpResponse("Accounts Home")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def password_reset_view(request):
    step = 1
    email = ""

    if request.method == "POST":
        action = request.POST.get("action")
        email = request.POST.get("email", "").strip()

        if action == "send_otp":
            if not email:
                messages.error(request, "Please enter your email address.")
            else:
                user = User.objects.filter(email__iexact=email).first()
                if user:
                    otp_code = PasswordResetOTP.generate_otp(user)
                    print(f"DEBUG: Generated OTP code for {user.email}: {otp_code}")
                    messages.success(
                        request,
                        f"An OTP code has been sent to {email}. Please check your inbox and enter the 6-digit OTP code below."
                    )
                    step = 2
                else:
                    messages.error(request, "No account found with this email address.")

        elif action == "verify_and_reset":
            step = 2
            otp_code = request.POST.get("otp_code", "").strip()
            new_password = request.POST.get("new_password", "").strip()
            confirm_password = request.POST.get("confirm_password", "").strip()

            if not email:
                messages.error(request, "Invalid request. Email is missing.")
                step = 1
            elif not otp_code or len(otp_code) != 6:
                messages.error(request, "Please enter a valid 6-digit OTP code.")
            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match. Please try again.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
            else:
                user = User.objects.filter(email__iexact=email).first()
                if not user:
                    messages.error(request, "User not found.")
                    step = 1
                else:
                    otp_obj = PasswordResetOTP.objects.filter(
                        user=user,
                        otp_code=otp_code,
                        used_at__isnull=True
                    ).first()

                    if otp_obj and otp_obj.is_valid():
                        otp_obj.used_at = timezone.now()
                        otp_obj.save()

                        user.set_password(new_password)
                        user.save()

                        messages.success(request, "Your password has been reset successfully! You can now log in.")
                        return redirect("accounts:login")
                    else:
                        messages.error(request, "Invalid or expired OTP code. Please click 'Resend OTP Code' below to get a new code.")

    return render(
        request,
        "accounts/password_reset_form.html",
        {
            "step": step,
            "email": email,
        }
    )


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.name = request.POST.get("name", "").strip()
        profile.avatar_url = request.POST.get("avatar_url", "").strip()
        profile.bio = request.POST.get("bio", "").strip()
        profile.pronouns = request.POST.get("pronouns", "Don't specify")
        profile.company = request.POST.get("company", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.website = request.POST.get("website", "").strip()
        profile.social_1 = request.POST.get("social_1", "").strip()
        profile.social_2 = request.POST.get("social_2", "").strip()
        profile.social_3 = request.POST.get("social_3", "").strip()
        profile.social_4 = request.POST.get("social_4", "").strip()
        profile.save()
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {"profile": profile})