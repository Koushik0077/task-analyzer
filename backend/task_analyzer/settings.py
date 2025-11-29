from pathlib import Path
import os

# ------------------------------------------------------------
# BASE PATH
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------
# SECURITY SETTINGS
# ------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-in-production"
)

# DEBUG defaults to False in production
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Allow all hosts unless overridden by env var
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")


# ------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",

    # Local apps
    "tasks",
]


# ------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Whitenoise for static files in production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # CORS
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ------------------------------------------------------------
# URL & WSGI
# ------------------------------------------------------------
ROOT_URLCONF = "task_analyzer.urls"
WSGI_APPLICATION = "task_analyzer.wsgi.application"


# ------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # You can add templates folder here if needed
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = []


# ------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------
# STATIC FILES (STATIC + WHITENOISE)
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Optional, but recommended for performance:
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ------------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# ------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ------------------------------------------------------------
# REST FRAMEWORK
# ------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer"
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser"
    ],
}


# ------------------------------------------------------------
# CORS (allows frontend → backend requests)
# ------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
