from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# ================= SECURITY =================

SECRET_KEY = 'django-insecure-=3#6$icdiknp$)b!1s#eov6the-x1@qhwl7-60^9rxks&8kaam'

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'pythonanywhere.com',
    "djangogirls-czhd.onrender.com",
    "127.0.0.1",
    "localhost",
]


# ================= APPLICATIONS =================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'learning',
    'accounts',
    'notes',
    'ai_engine',
    'scheduler',
]


# ================= MIDDLEWARE =================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ================= URL / WSGI =================

ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'


# ================= TEMPLATES =================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Notes sidebar/context
                'notes.views.notes_processor',
            ],
        },
    },
]


# ================= DATABASE =================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "djangogirls"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}


# ================= PASSWORD VALIDATION =================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ================= INTERNATIONALIZATION =================

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# ================= STATIC FILES =================

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'static'


# ================= MEDIA FILES =================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ================= AUTH =================

LOGIN_REDIRECT_URL = 'notes:note_list'

LOGIN_URL = 'accounts:login'

LOGOUT_REDIRECT_URL = 'learning:home'


# ================= DEFAULT PRIMARY KEY =================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================= EMAIL =================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ================= DATA UPLOAD LIMITS =================
# Allow large payloads (e.g. rich text study notes, batch files, folder creation) up to 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB