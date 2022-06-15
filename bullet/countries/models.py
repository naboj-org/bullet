from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField
from timezone_field import TimeZoneField
from web.fields import BranchField, ChoiceArrayField, LanguageField


class BranchCountry(models.Model):
    branch = BranchField()
    country = CountryField()
    languages = ChoiceArrayField(LanguageField())
    timezone = TimeZoneField()

    class Meta:
        constraints = [
            UniqueConstraint("branch", "country", name="branch_country_unique"),
        ]
