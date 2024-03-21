import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from django.conf import settings


class Command(BaseCommand):
    help = "The functional/simpliest way to create a superuser"

    def handle(self, *args, **options):
        for path in settings.LOCALE_PATHS:
            if not os.path.exists(path):
                os.mkdir(path)

        os.system("python manage.py migrate")

        User = get_user_model()
        if not User.objects.filter(username="identfy").exists():
            User.objects.create_superuser(
                "identfy", "identfy@identfy.org", "identfy"  # USERNAME  # MAIL  # PASS
            )
