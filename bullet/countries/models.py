from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField
from web.fields import BranchField


class BranchCountry(models.Model):
    branch = BranchField()
    country = CountryField()
    languages = ArrayField(
        base_field=models.CharField(max_length=8, choices=settings.LANGUAGES)
    )

    class Meta:
        constraints = [
            UniqueConstraint("branch", "country", name="branch_country_unique"),
        ]
