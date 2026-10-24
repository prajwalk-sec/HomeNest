"""
Django settings for HomeNest.

Production-ready configuration for:
- Django 5.2
- PostgreSQL
- Environment variables
- Gunicorn
- Static files
- Media files
- HTTPS deployment
"""

import os
from pathlib import Path
from urllib.parse import urlsplit

import cloudinary
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# ============================================================
# BASE CONFIGURATION
# ============================================================
# ============================================================
# BASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY or not SECRET_KEY.strip():
    raise ImproperlyConfigured(
        "SECRET_KEY is missing or empty. Set it in the deployment "
        "environment (Render: Dashboard > Environment) or in your local .env."
    )

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "").strip()
CLOUDINARY_CREDENTIAL_VARIABLES = (
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
)
cloudinary_credentials = {
    name: os.getenv(name, "").strip()
    for name in CLOUDINARY_CREDENTIAL_VARIABLES
}
configured_cloudinary_credentials = [
    name for name, value in cloudinary_credentials.items() if value
]

if CLOUDINARY_URL and configured_cloudinary_credentials:
    raise ImproperlyConfigured(
        "Configure Cloudinary using either CLOUDINARY_URL or all of "
        "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and "
        "CLOUDINARY_API_SECRET. Do not mix both configuration methods."
    )

if CLOUDINARY_URL:
    try:
        parsed_cloudinary_url = urlsplit(CLOUDINARY_URL)
        cloudinary_url_is_complete = (
            parsed_cloudinary_url.scheme.lower() == "cloudinary"
            and parsed_cloudinary_url.username
            and parsed_cloudinary_url.password
            and parsed_cloudinary_url.hostname
        )
    except ValueError:
        cloudinary_url_is_complete = False

    if not cloudinary_url_is_complete:
        raise ImproperlyConfigured(
            "CLOUDINARY_URL is incomplete or invalid. It must include "
            "the Cloudinary API key, API secret, and cloud name."
        )
elif configured_cloudinary_credentials:
    missing_cloudinary_credentials = [
        name
        for name, value in cloudinary_credentials.items()
        if not value
    ]
    if missing_cloudinary_credentials:
        raise ImproperlyConfigured(
            "Missing Cloudinary environment variable(s): "
            + ", ".join(missing_cloudinary_credentials)
        )
elif not DEBUG:
    raise ImproperlyConfigured(
        "Cloudinary credentials are required when DEBUG=False. Set "
        "CLOUDINARY_URL or all of CLOUDINARY_CLOUD_NAME, "
        "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
    )

if CLOUDINARY_URL or len(configured_cloudinary_credentials) == len(
    CLOUDINARY_CREDENTIAL_VARIABLES
):
    cloudinary.reset_config()
    cloudinary_config = cloudinary.config()
    missing_sdk_credentials = [
        name
        for name, value in (
            ("cloud name", cloudinary_config.cloud_name),
            ("API key", cloudinary_config.api_key),
            ("API secret", cloudinary_config.api_secret),
        )
        if not value
    ]
    if missing_sdk_credentials:
        credential_source = (
            "CLOUDINARY_URL"
            if CLOUDINARY_URL
            else ", ".join(CLOUDINARY_CREDENTIAL_VARIABLES)
        )
        raise ImproperlyConfigured(
            "Cloudinary configuration from "
            f"{credential_source} is missing: "
            + ", ".join(missing_sdk_credentials)
        )

CLOUDINARY_CONFIGURED = bool(
    CLOUDINARY_URL
    or len(configured_cloudinary_credentials)
    == len(CLOUDINARY_CREDENTIAL_VARIABLES)
)
# ============================================================
# SECURITY
# ============================================================

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
    "homenest-q4ji.onrender.com",
    "home-nest-mejd.vercel.app",
    ".vercel.app",
]

env_hosts = os.getenv("ALLOWED_HOSTS", "")

if env_hosts:
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in env_hosts.split(",")
        if host.strip()
    )

RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary_storage",
    "cloudinary",

    # HomeNest apps
    "apps.accounts",
    "apps.properties",
    "apps.tenants",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise for serving static files
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI
# ============================================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================
# DATABASE - POSTGRESQL
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    try:
        database_url_scheme = urlsplit(DATABASE_URL).scheme.lower()
        if database_url_scheme not in {"postgres", "postgresql"}:
            raise ValueError

        DATABASES = {
            "default": dj_database_url.parse(
                DATABASE_URL,
                engine="django.db.backends.postgresql",
                conn_max_age=600,
            ),
        }
    except (TypeError, ValueError):
        raise ImproperlyConfigured(
            "DATABASE_URL is invalid. Set it to the internal URL for the "
            "existing Render PostgreSQL database."
        ) from None

    if not DATABASES["default"].get("ENGINE"):
        raise ImproperlyConfigured(
            "DATABASE_URL did not resolve to a database engine. Set it to "
            "the internal URL for the existing Render PostgreSQL database."
        )

    if not DATABASES["default"]["ENGINE"].endswith("postgresql"):
        raise ImproperlyConfigured(
            "DATABASE_URL must point to the existing PostgreSQL database."
        )
elif not DEBUG:
    raise ImproperlyConfigured(
        "DATABASE_URL is required in production. Set it to the internal URL "
        "for the existing Render PostgreSQL database."
    )
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }
    }


# ============================================================
# CUSTOM USER MODEL
# ============================================================

AUTH_USER_MODEL = "accounts.User"


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# WhiteNoise compressed static files
STORAGES = {
    "default": {
        "BACKEND": (
            "config.storage.HomeNestMediaCloudinaryStorage"
            if CLOUDINARY_CONFIGURED
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# EMAIL
# ============================================================

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "")

EMAIL_PORT = int(
    os.getenv("EMAIL_PORT", "587")
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    ""
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    ""
)

EMAIL_USE_TLS = (
    os.getenv("EMAIL_USE_TLS", "True").lower()
    == "true"
)

EMAIL_USE_SSL = (
    os.getenv("EMAIL_USE_SSL", "False").lower()
    == "true"
)

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "HomeNest <no-reply@homenest.local>"
)


# ============================================================
# LOGIN / SESSION
# ============================================================

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"


# ============================================================
# HTTPS / SECURITY
# ============================================================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Browser should only communicate with the site over HTTPS
    SECURE_SSL_REDIRECT = (
        os.getenv("SECURE_SSL_REDIRECT", "True").lower()
        == "true"
    )

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HTTP Strict Transport Security
    SECURE_HSTS_SECONDS = int(
        os.getenv("SECURE_HSTS_SECONDS", "31536000")
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = False

    # Prevent browsers from guessing content types
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Referrer policy
    SECURE_REFERRER_POLICY = "same-origin"

    # Clickjacking protection
    X_FRAME_OPTIONS = "DENY"


# ============================================================
# CSRF TRUSTED ORIGINS
# ============================================================
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        ""
    ).split(",")
    if origin.strip()
]
render_origin = "https://homenest-q4ji.onrender.com"
if render_origin not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(render_origin)
if RENDER_EXTERNAL_HOSTNAME:
    render_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



# Temporary production error logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "apps.properties": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}
