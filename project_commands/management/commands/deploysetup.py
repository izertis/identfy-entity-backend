import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


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
                "identfy",
                "identfy@identfy.org",
                "identfy",  # USERNAME  # MAIL  # PASS
            )
        os.system("python manage.py permissions")
        # Change password to a strong one
        if not User.objects.filter(username="service").exists():
            service_user = User.objects.create_user(
                username="service",
                email="",
                password="service",
            )

            service_user.groups.set([Group.objects.filter(name="SERVICE").first().id])
