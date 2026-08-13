from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='accounts_home'),
    path('profile/', views.profile_view, name='profile'),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html", 
            redirect_authenticated_user=True
        ),
        name="login"
    ),
    path("register/", views.register, name="register"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html" 
        ),
        name="password_reset_form" 
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='learning:home'), name='logout'),
]