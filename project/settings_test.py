import os

import dj_database_url

from project.settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": "5432",
    }
}

database_url = os.environ.get("DATABASE_URL", None)
if database_url:
    DATABASES["default"] = dj_database_url.parse(database_url, conn_max_age=600)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEBUG = True

SECURE_SSL_REDIRECT = False
BACKEND_DOMAIN = "http://localhost:8000"
CORS_ALLOWED_ORIGINS = ["http://localhost:8000"]
ALLOWED_HOSTS = ["localhost:8000"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000"]
DEVELOPER_MOCKUP_ENTITIES = 1
DEVELOP_DATA = 1
