from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import RegisterForm


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("notes:note_list")

    else:

        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserProfile


def custom_logout(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_obj.name = request.POST.get("name", "").strip()
        profile_obj.avatar_url = request.POST.get("avatar_url", "").strip()
        profile_obj.bio = request.POST.get("bio", "").strip()
        profile_obj.pronouns = request.POST.get("pronouns", "").strip()
        profile_obj.company = request.POST.get("company", "").strip()
        profile_obj.location = request.POST.get("location", "").strip()
        profile_obj.website = request.POST.get("website", "").strip()
        profile_obj.social_1 = request.POST.get("social_1", "").strip()
        profile_obj.social_2 = request.POST.get("social_2", "").strip()
        profile_obj.social_3 = request.POST.get("social_3", "").strip()
        profile_obj.social_4 = request.POST.get("social_4", "").strip()
        profile_obj.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "success"})
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {"profile": profile_obj})