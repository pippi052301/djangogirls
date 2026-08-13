from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


LOGIN_REDIRECT_URL = "/notes/"
LOGOUT_REDIRECT_URL = "/accounts/login/"


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    # Trang chính
    path(
        "",
        include("learning.urls")
    ),

    # Authentication
    path(
        "accounts/",
        include("accounts.urls")
    ),

    # Notes
    path(
        "notes/",
        include("notes.urls")
    ),

    # AI
    path(
        "ai/",
        include("ai_engine.urls")
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )