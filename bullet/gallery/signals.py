from pathlib import Path

from django.conf import settings
from django.dispatch import receiver
from django_cleanup.signals import cleanup_pre_delete

from gallery.models import Photo
from gallery.thumbnails import delete_thumbnails


@receiver(cleanup_pre_delete, sender=Photo)
def on_photo_delete(file_name: str, **kwargs):
    file = Path(settings.MEDIA_ROOT) / file_name
    delete_thumbnails(file)
