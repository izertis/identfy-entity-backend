from django.apps import AppConfig


class OpenidConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "openid"

    def ready(self) -> None:
        import openid.signals
