import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

from django.core.files.storage import default_storage
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import Country, CountryField
from PIL import Image

from gallery.constants import (
    BREAKPOINT_SM_PX,
    EXIF_DATES,
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
    country: Country = CountryField()  # type:ignore

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

    def image_for_size(self, width):
        base_path = Path(self.image.name)
        base_name = base_path.with_suffix("").name
        name = base_path.with_name(f"{base_name}_{width}.webp")
        return default_storage.url(str(name))

    @property
    def image_smallest(self):
        return self.image_for_size(min(THUMB_SIZES))

    @property
    def image_srcset(self):
        srcset = []

        for width in THUMB_SIZES:
            url = self.image_for_size(width)
            srcset.append(f"{url} {width}w")

        srcset.append(f"{self.image.url} {ORIGNAL_SIZE}w")
        return ", ".join(srcset)

    @property
    def image_sizes(self):
        scaling = MAX_IMAGE_HEIGHT_REM / self.image_height
        width_rem = scaling * self.image_width

        return f"(max-width: {BREAKPOINT_SM_PX}px) 100vw, {width_rem:.2f}rem"

    def read_taken_at(self):
        im = Image.open(self.image)
        exif = im.getexif()

        for exif_id in EXIF_DATES:
            date = exif.get(exif_id)
            if not date:
                continue

            self.taken_at = datetime.strptime(date, "%Y:%m:%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )
            break
