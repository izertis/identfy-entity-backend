import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

import sentry_sdk
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "imbc)hfc1+6km)o%px&*xaw9s8_@xpy4=1t*pqn4mgzq(b+32y",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", 1))

BACKEND_DOMAIN = os.environ.get("BACKEND_DOMAIN", "http://localhost:8000")

DJANGO_ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "local")

ALLOWED_HOSTS: List[str] = os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,localhost:8080"
).split(",")

CSRF_TRUSTED_ORIGINS: List[str] = os.environ.get(
    "CSRF_TRUSTED_ORIGINS", "http://localhost,http://127.0.0.1"
).split(",")

# Base url to serve media files
MEDIA_URL = ".cache/"
# Path where media is stored
MEDIA_ROOT = os.path.join(BASE_DIR, ".cache/")

SERVER_NAME = os.environ.get("DJANGO_ENVIRONMENT", "localhost")

USE_PORT = True if SERVER_NAME == "localhost" else False

USE_HTTPS = int(os.environ.get("USE_HTTPS", False))

SERVER_PORT = os.environ.get("SERVER_PORT", "8000")
if USE_HTTPS:
    SERVER_PORT = "443"

# Application definition

INSTALLED_APPS = [
    "daphne",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_jsonform",
    "rest_framework",
    "drf_yasg",
    "rest_framework.authtoken",
    "corsheaders",
    "django_celery_results",
    "django_rest_passwordreset",
    "django_filters",
    "waffle",
    # owner izertis
    "feature_toggle_manager.apps.FeatureToggleManagerConfig",
    "tasks_protocol.apps.TasksProtocolConfig",
    "credentials",
    "openid",
    "project_commands",
]

MIDDLEWARE = [
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "waffle.middleware.WaffleMiddleware",
]


CORS_ORIGIN_ALLOW_ALL: bool = True
CORS_ALLOWED_ORIGINS: List[str] = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:3000"
).split(",")


ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "postgres"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "postgres"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

database_url = os.environ.get("DATABASE_URL", None)

if database_url:
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(database_url)


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = "static"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_DIRS = [
    BASE_DIR / "styles",
]

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN", ""),
        environment=DJANGO_ENVIRONMENT,
        traces_sample_rate=1.0,
        send_default_pii=True,
    )
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_REDIRECT_URL = ""

LOGIN_URL = "/"

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        },
        "basic": {"type": "basic"},
    },
}

JAZZMIN_SETTINGS: Dict[str, Any] = {
    "site_title": "Identfy Admin",
    "site_header": "Identfy",
    "site_brand": "Identfy",
    "login_logo": "images/logo/identfy_white_logo.svg",
    "login_logo_dark": "images/logo/identfy_white_logo.svg",
    "site_logo_classes": "img-circle",
    "site_icon": "images/icon/identfy_icon.png",
    "welcome_sign": _("Welcome to the Identfy Admin Site"),
    "copyright": _("Izertis"),
    "search_model": ["auth.User", "auth.Group"],
    "user_avatar": None,
    ############
    # Top Menu #
    ############
    "topmenu_links": [
        {
            "name": "Home",
            "url": "admin:index",
            "permissions": ["auth.view_user"],
        },
        {
            "name": "Support",
            "url": "https://github.com/farridav/django-jazzmin/issues",
            "new_window": True,
            "icon": "far fa-question-circle",
        },
        {"model": "auth.User"},
    ],
    #############
    # User Menu #
    #############
    "usermenu_links": [
        {
            "name": "Support",
            "url": "https://github.com/farridav/django-jazzmin/issues",
            "new_window": True,
            "icon": "far fa-question-circle",
        },
        {"model": "auth.user"},
    ],
    #############
    # Side Menu #
    #############
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "authtoken.tokenproxy": "fas fa-magic",
        "waffle.flag": "fas fa-flag",
        "waffle.sample": "fas fa-eye-dropper",
        "waffle.switch": "fas fa-check-circle",
        "django_celery_results.groupresult": "far fa-object-group",
        "django_celery_results.taskresult": "fas fa-tasks",
        "django_rest_passwordreset.resetpasswordtoken": "fas fa-exchange-alt",
        "openid.credentialissuermetadata": "fas fa-database",
        "openid.verifiermetadata": "fas fa-database",
        "openid.presentationdefinition": "fas fa-book",
        "openid.issuancecredentialoffer": "fab fa-openid",
        "openid.vcscopeaction": "fas fa-edit",
        "openid.vpscopeaction": "fas fa-envelope-open",
        "openid.noncemanager": "fas fa-random",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    #################
    # Related Modal #
    #################
    "related_modal_active": False,
    #############
    # UI Tweaks #
    #############
    "custom_css": "css/izertis.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    ###############
    # Change view #
    ###############
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "minty",
    "dark_mode_theme": "superhero",
}

ASGI_APPLICATION = "project.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}  # TODO USE REDIS ?

WSGI_APPLICATION = "project.wsgi.application"

INTERNAL_IPS = ["*"]


BACKEND_NOTIFICATIONS_SECRET = os.environ.get(
    "BACKEND_NOTIFICATIONS_SECRET", str(uuid4())
)


REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ]
}

APPEND_SLASH = os.environ.get("APPEND_SLASH", "False")

CREDENTIALS_URL = os.environ.get("CREDENTIALS_URL", "")

# OWN DATA
DID = os.environ.get("DID", "")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "")
PUBLIC_KEY = os.environ.get("PUBLIC_KEY", "")
EXTERNAL_URL = os.environ.get("EXTERNAL_URL", "")
EXTERNAL_API_KEY = os.environ.get("EXTERNAL_API_KEY", "")


# Local Settings
try:
    from .settings_local import *
except ImportError:
    pass
