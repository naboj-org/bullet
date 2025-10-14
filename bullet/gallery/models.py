from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField
from pictures.models import PictureField


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
    image = PictureField(
        upload_to="photos", width_field="image_width", height_field="image_height"
    )
    taken_at = models.DateTimeField(blank=True, null=True)
