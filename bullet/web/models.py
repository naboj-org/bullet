from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from bullet.constants import Languages


class Translation(models.Model):
    reference = models.CharField(max_length=256)
    language = models.TextField(choices=Languages.choices)
    context = models.CharField(max_length=128, null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Translation of {self.reference} in {self.language} with context {self.context}'

    class Meta:
        unique_together = [
            ('reference', 'language', 'context')
        ]


@receiver(post_save, sender=Translation)
def save_profile(sender, instance, **kwargs):
    from web.dynamic_translations import translation_cache
    translation_cache.reload()
