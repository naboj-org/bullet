from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField
from pictures.models import PictureField


class Album(models.Model):
    title = models.CharField(max_length=256)
    competition = models.ForeignKey(
        "competitions.Competition",
        on_delete=models.CASCADE,
        related_name="albums",
    )
    country = CountryField()

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            UniqueConstraint(
                "title", "competition", "country", name="title_competition_country"
            )
        ]


class Photo(models.Model):
    album = models.ForeignKey(
        "gallery.Album",
        on_delete=models.CASCADE,
        related_name="photos",
    )
    image = PictureField(upload_to="photos")
