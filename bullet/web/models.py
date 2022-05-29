from competitions.models import BranchField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from bullet.constants import Languages


class Page(models.Model):
    url = models.CharField(max_length=128)
    language = models.TextField(choices=Languages.choices)
    branch = BranchField()
    title = models.CharField(max_length=128)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Translation(models.Model):
    reference = models.CharField(max_length=256)
    language = models.TextField(choices=Languages.choices)
    context = models.CharField(max_length=128, null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return (
            f"Translation of {self.reference} in {self.language} with context"
            f" {self.context}"
        )

    class Meta:
        unique_together = [("reference", "language", "context")]


@receiver(post_save, sender=Translation)
def save_profile(sender, instance, **kwargs):
    from web.dynamic_translations import translation_cache

    translation_cache.reload()


class Menu(models.Model):
    url = models.CharField(max_length=128)
    branch = BranchField()
    title = models.CharField(max_length=128)
    order = models.IntegerField(default=1)

    def __str__(self):
        return self.title


class Partner(models.Model):
    branch = BranchField()
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    image = models.FileField()


class Organizer(models.Model):
    branch = BranchField()
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    image = models.FileField()
