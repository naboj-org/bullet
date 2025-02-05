import os
import secrets
from pathlib import Path

from django.core.files.storage import default_storage
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField

from gallery.constants import (
    BREAKPOINT_SM_PX,
    MAX_IMAGE_HEIGHT_REM,
    ORIGNAL_SIZE,
    THUMB_SIZES,
)


class Album(models.Model):
    id: int
    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256)
    competition = models.ForeignKey(
        "competitions.Competition",
        on_delete=models.CASCADE,
        related_name="albums",
    )
    competition_id: int
    country = CountryField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["country", "title"]
        constraints = [
            UniqueConstraint("slug", "competition", name="album__slug_competition")
        ]


def photo_upload_to(instance: "Photo", filename: str):
    _, dot_ext = os.path.splitext(filename)
    rand = secrets.token_hex(8)
    return f"albums/{instance.album_id}/{rand}{dot_ext}"


class Photo(models.Model):
    id: int
    album = models.ForeignKey(
        "gallery.Album",
        on_delete=models.CASCADE,
        related_name="photos",
    )
    album_id: int
    image_width = models.PositiveIntegerField()
    image_height = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to=photo_upload_to,
        width_field="image_width",
        height_field="image_height",
    )
    taken_at = models.DateTimeField(blank=True, null=True)

    @property
    def image_srcset(self):
        base_path = Path(self.image.name)
        base_name = base_path.with_suffix("").name
        srcset = []

        for width in THUMB_SIZES:
            name = base_path.with_name(f"{base_name}_{width}.webp")
            url = default_storage.url(str(name))
            srcset.append(f"{url} {width}w")

        srcset.append(f"{self.image.url} {ORIGNAL_SIZE}w")

        return ", ".join(srcset)

    @property
    def image_sizes(self):
        scaling = MAX_IMAGE_HEIGHT_REM / self.image_height
        width_rem = scaling * self.image_width

        return f"(max-width: {BREAKPOINT_SM_PX}px) 100vw, {width_rem:.2f}rem"
