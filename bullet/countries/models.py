from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField
from web.fields import BranchField, LanguageField


class BranchCountry(models.Model):
    branch = BranchField()
    country = CountryField()
    languages = ArrayField(base_field=LanguageField())

    class Meta:
        constraints = [
            UniqueConstraint("branch", "country", name="branch_country_unique"),
        ]
