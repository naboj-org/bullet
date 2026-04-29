from django.apps import AppConfig


class BulletAdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bullet_admin"

    def ready(self):
        from pillow_heif import register_heif_opener

        register_heif_opener()
        from . import components  # noqa
