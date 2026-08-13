from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from accounts.forms import RegisterForm
from .models import UserProfile


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