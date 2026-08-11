from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Note
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import PasswordResetOTP
from django.http import HttpResponse

def home(request):
    return render(request, 'learning/home.html')  # or return HttpResponse("Homepage")

def note_create(request):
    return render(request, 'learning/note_form.html')

def note_list(request):
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'learning/note_list.html', {'notes': notes})

def register(request):
    if request.method == 'POST':
        # Change UserCreationForm -> CustomUserCreationForm
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('learning:note_list')
    else:
        # Change UserCreationForm -> CustomUserCreationForm
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})




#Password_reset function
def custom_password_reset(request):
    step = 1
    email = request.POST.get('email', '')

    if request.method == 'POST':
        action = request.POST.get('action')

        # Step 1: Send OTP
        if action == 'send_otp':
            try:
                user = User.objects.get(email=email)
                otp_code = PasswordResetOTP.generate_otp(user)
                
                send_mail(
                    'Your Password Reset Code',
                    f'Your OTP code is: {otp_code}',
                    'noreply@studysupport.com',
                    [email],
                    fail_silently=False,
                )
                # Change notify
                messages.success(request, f'An OTP code has been sent to {email}. Check your terminal/email.')
                step = 2
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email address.')

        # Step 2: Comfirm OTP and new password
        elif action == 'verify_and_reset':
            step = 2
            otp_input = request.POST.get('otp_code')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                try:
                    user = User.objects.get(email=email)
                    otp_obj = PasswordResetOTP.objects.filter(user=user, otp_code=otp_input).last()

                    if otp_obj and otp_obj.is_valid():
                        user.set_password(new_password)
                        user.save()
                        # After success, send message then go login
                        messages.success(request, 'Password reset successfully! Please login.')
                        return redirect('login')
                    else:
                        messages.error(request, 'Invalid or expired OTP code.')
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')

    return render(request, 'registration/password_reset.html', {'step': step, 'email': email})
