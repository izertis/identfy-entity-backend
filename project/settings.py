import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

import sentry_sdk
from django.utils.translation import gettext_lazy as _


def readEnvBool(envVarName: str, default: bool) -> bool:
    return (
        os.environ.get(envVarName) in [True, "true", "TRUE", "True", "1", "t", "T"]
    ) or default


def readEnvList(envVarName: str, default: str) -> str:
    return (
        os.environ.get(envVarName).split(",") if os.environ.get(envVarName) else default
    )


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-e&q@0vqsgl27&#h@8pa@dips7x+@jt+k+mrlwg=84mf31on7be",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", 1))


DJANGO_ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "local")


BACKEND_DOMAIN = os.environ.get("BACKEND_DOMAIN", "http://localhost:8000")

DOMAIN_WITHOUT_PROTOCOL = BACKEND_DOMAIN.replace("https://", "").replace("http://", "")

ALLOWED_HOSTS: List[str] = readEnvList(
    "ALLOWED_HOSTS", [DOMAIN_WITHOUT_PROTOCOL.split(":")[0]]
)

CSRF_TRUSTED_ORIGINS: List[str] = readEnvList("CSRF_TRUSTED_ORIGINS", [BACKEND_DOMAIN])

CORS_ORIGIN_ALLOW_ALL: bool = readEnvBool("CORS_ORIGIN_ALLOW_ALL", False)

CORS_ALLOWED_ORIGINS: List[str] = readEnvList("CORS_ALLOWED_ORIGINS", [BACKEND_DOMAIN])

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
    "django_json_widget",
    "django_jsonform",
    "rest_framework",
    "drf_yasg",
    "rest_framework.authtoken",
    "corsheaders",
    "django_celery_results",
    "django_rest_passwordreset",
    "django_filters",
    # owner izertis
    "organizations",
    "tasks_protocol",
    "credentials",
    "openid",
    "project_commands",
    "user",
    "ebsi",
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
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "project.wsgi.application"


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


EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")

# POSTMARK
POSTMARK_API_KEY = os.environ.get("POSTMARK_API_KEY", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")
POSTMARK = {
    "TOKEN": POSTMARK_API_KEY,
    "TEST_MODE": False,
    "VERBOSITY": 0,
}
if POSTMARK_API_KEY:
    EMAIL_BACKEND = "postmarker.django.EmailBackend"
    EMAIL_HOST = "smtp.postmarkapp.com"
    EMAIL_HOST_USER = POSTMARK_API_KEY
    EMAIL_HOST_PASSWORD = POSTMARK_API_KEY
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = False

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication,",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissions",
    ],
}

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN", ""),
        environment=DJANGO_ENVIRONMENT,
        traces_sample_rate=1.0,
        send_default_pii=True,
    )
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


SIMPLE_JWT = {
    "TOKEN_OBTAIN_SERIALIZER": "user.serializers.CustomTokenLoginSerializer",
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=os.environ.get("ACCESS_TOKEN_LIFETIME", 15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        hours=os.environ.get("REFRESH_TOKEN_LIFETIME", 1)
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
    "login_logo": "images/logo/identfy_white.svg",
    "login_logo_dark": "images/logo/identfy_white.svg",
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
        "django_celery_results.groupresult": "far fa-object-group",
        "django_celery_results.taskresult": "fas fa-tasks",
        "django_rest_passwordreset.resetpasswordtoken": "fas fa-exchange-alt",
        "organizations.organizationkeys": "fas fa-key",
        "openid.issuanceinformation": "fab fa-openid",
        "openid.verifiermetadata": "fas fa-database",
        "openid.presentationdefinition": "fas fa-book",
        "openid.issuanceflow": "fas fa-edit",
        "openid.verifyflow": "fas fa-envelope-open",
        "openid.noncemanager": "fas fa-random",
        "credentials.verifiablecredential": "fas fa-id-card-alt",
        "credentials.issuedverifiablecredential": "fas fa-folder",
        "ebsi.accreditationtoattest": "fas fa-address-card",
        "ebsi.accreditationtoaccredit": "fas fa-file-signature",
        "ebsi.accreditationtoonboard": "fas fa-user-plus",
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
        "organizations.organization": "vertical_tabs",
    },
    "language_chooser": False,
    "custom_links": {
        "credentials": [
            {
                "name": "Request VC",
                "url": "/admin/request-vc/",
                "icon": "fas fa-id-badge",
                "permissions": ["auth.request_vc"],
            },
        ]
    },
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


INTERNAL_IPS = ["*"]

BACKEND_NOTIFICATIONS_SECRET = os.environ.get(
    "BACKEND_NOTIFICATIONS_SECRET", str(uuid4())
)

REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ]
}

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", "")
AWS_BUCKET = os.environ.get("AWS_BUCKET", "")

CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True


##CONFIG ENVS
VC_SERVICE_URL = os.environ.get("VC_SERVICE_URL", "")
DID = os.environ.get("DID", "")
ENTITY_URL = os.environ.get("ENTITY_URL", "")
ENTITY_API_KEY = os.environ.get("ENTITY_API_KEY", "")
APPEND_SLASH = os.environ.get("APPEND_SLASH", "False")

EBSI_DIDR_URL = os.environ.get(
    "EBSI_DIDR_URL", "https://api-pilot.ebsi.eu/did-registry/v5/identifiers"
)
EBSI_TIR_URL = os.environ.get(
    "EBSI_TIR_URL",
    "https://api-pilot.ebsi.eu/trusted-issuers-registry/v5/issuers",
)

DEVELOPER_MOCKUP_ENTITIES = readEnvBool("DEVELOPER_MOCKUP_ENTITIES", False)

# Local Settings
try:
    from .settings_local import *
except ImportError:
    pass
