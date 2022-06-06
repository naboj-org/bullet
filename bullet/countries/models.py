from competitions.models import BranchField
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField


class BranchCountry(models.Model):
    branch = BranchField()
    country = CountryField()
    languages = ArrayField(base_field=models.CharField(max_length=8))

    class Meta:
        constraints = [
            UniqueConstraint("branch", "country", name="branch_country_unique"),
        ]
