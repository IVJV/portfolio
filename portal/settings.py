# portal/settings.py
"""
Django settings for portal project.
Deploy-ready for Railway + WhiteNoise + Cloudinary (optional) + Postgres (optional).
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------
# Helpers
# -----------------------------
def env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.environ.get(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


# -----------------------------
# Core security / env
# -----------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-secret-key")

# Production-safe default: DEBUG off unless explicitly enabled
DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")

# Needed behind proxies (Railway/Render) when DEBUG=False
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True


# -----------------------------
# Cloudinary toggle
# -----------------------------
# Cloudinary uses CLOUDINARY_URL like:
# cloudinary://<api_key>:<api_secret>@<cloud_name>
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL", "").strip()
USE_CLOUDINARY = bool(CLOUDINARY_URL)


# -----------------------------
# Applications
# -----------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Insert Cloudinary apps in a typical order (right after staticfiles)
if USE_CLOUDINARY:
    INSTALLED_APPS += [
        "cloudinary_storage",
        "cloudinary",
    ]

# Your apps
INSTALLED_APPS += [
    "core",
    "catalogo.apps.CatalogoConfig",
]

# Optional dev-only utilities (avoid breaking production if not installed)
if DEBUG and env_bool("DJANGO_EXTENSIONS", False):
    INSTALLED_APPS += ["django_extensions"]


# -----------------------------
# Middleware
# -----------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise: serve static files in production without extra services
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    # i18n must be enabled here
    "django.middleware.locale.LocaleMiddleware",

    # Force admin UI in English (your custom middleware)
    "portal.middleware.AdminEnglishMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Inject Areas into navbar dropdown globally
                "catalogo.context_processors.nav_areas",
            ],
        },
    },
]

WSGI_APPLICATION = "portal.wsgi.application"


# -----------------------------
# Database
# -----------------------------
# Default: SQLite for local dev
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Optional: use Postgres in production if DATABASE_URL is provided
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=not DEBUG,
    )


# -----------------------------
# Password validation
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# -----------------------------
# Internationalization (i18n)
# -----------------------------
USE_I18N = True
USE_TZ = True
TIME_ZONE = "UTC"

LANGUAGE_CODE = "es"

LANGUAGES = [
    ("es", "Español"),
    ("en", "English"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# -----------------------------
# Static files (WhiteNoise)
# -----------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise storage (hashed + compressed)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}


# -----------------------------
# Media
# -----------------------------
# Local dev fallback
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if USE_CLOUDINARY:
    # Professional default: treat default MEDIA as images.
    # PDFs/Docs should be RAW storage per-field in models (FileField(storage=RawMediaCloudinaryStorage())).
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }

# -----------------------------
# CSRF / Security (recommended for production)
# -----------------------------
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# -----------------------------
# Misc
# -----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
