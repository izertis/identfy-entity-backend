from django.apps import AppConfig


class EbsiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ebsi'

    def ready(self) -> None:
        import ebsi.signals